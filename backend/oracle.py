import ccxt
from ccxt.base import errors as ccxt_errors
import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
import sys
from config import (
    API_KEY, SECRET, SYMBOLS, TIMEFRAME, LIMIT, 
    VWAP_PERIOD, FFT_PERIOD, SIGMA_THRESHOLD, 
    REVERSAL_THRESHOLD_PERCENT, validate_config, DATA_SOURCE
)
from data_sources import fetch_ohlcv_data, initialize_data_source

# --- Phase 1: Coinbase API Integration and Data Fetching ---

def initialize_exchange():
    """Initializes the exchange object using ccxt.
    
    Falls back to Kraken for public data if Coinbase credentials are not provided.
    """
    try:
        if API_KEY != "YOUR_API_KEY_HERE" and SECRET != "YOUR_SECRET_HERE":
            print("Using Coinbase with provided credentials...")
            exchange = ccxt.coinbase({
                'apiKey': API_KEY,
                'secret': SECRET,
                'enableRateLimit': True,
            })
        else:
            print("WARNING: No Coinbase credentials provided.")
            print("Falling back to Kraken for public data access.")
            print("Note: Symbol format may differ (e.g., DOGE/USD on Kraken)")
            exchange = ccxt.kraken({
                'enableRateLimit': True,
            })
        
        return exchange
    except Exception as e:
        print(f"Error initializing exchange: {e}")
        return None

# --- Phase 2: Data Acquisition and Preprocessing ---
# Note: fetch_ohlcv_data is now imported from data_sources.py
# This provides unified interface for CoinGecko and exchange data

# --- Phase 3: Core Logic Implementation (VWAP & Deviation) ---

def calculate_vwap_and_deviation(df, period, sigma_threshold):
    """
    Calculates the Equilibrium State (Z') and Deviation Measurement (E).
    
    1. Equilibrium State (Z'): Z' = VWAP(price, volume)
    2. Deviation Measurement (E): E = (Z_current - Z') / σ
    
    Includes protection against division by zero and low volume periods.
    """
    
    df['TP'] = (df['high'] + df['low'] + df['close']) / 3
    df['TP_Vol'] = df['TP'] * df['volume']
    
    df['Cum_TP_Vol'] = df['TP_Vol'].rolling(window=period).sum()
    df['Cum_Volume'] = df['volume'].rolling(window=period).sum()
    
    # Protect against division by zero in low/no volume periods
    df["Z_prime"] = np.where(
        df['Cum_Volume'] > 0,
        df['Cum_TP_Vol'] / df['Cum_Volume'],
        df['close']  # Fallback to close price if no volume
    )
    
    df['Deviation'] = df['close'] - df['Z_prime']
    df['Sigma'] = df['Deviation'].rolling(window=period).std()
    
    # Protect against division by zero when sigma is zero (no price movement)
    # Use a small epsilon to avoid inf values
    epsilon = 1e-10
    df['E'] = np.where(
        df['Sigma'] > epsilon,
        df['Deviation'] / df['Sigma'],
        0.0  # No deviation if no volatility
    )
    
    df.drop(columns=['TP', 'TP_Vol', 'Cum_TP_Vol', 'Cum_Volume'], inplace=True)
    
    print(f"Calculated VWAP (Z') and Deviation (E) over a {period}-bar period.")
    return df

# --- Phase 4: FFT and Phase Position Implementation ---

def calculate_fft_phase(df, period):
    """
    Calculates the Phase Position (φ) and Time to Reversal (T_reversal) for all valid bars.
    
    φ = arctan(FFT(price)) -> T_reversal = (1 - φ/2π) * Period
    
    Performs rolling FFT analysis to generate phase data for each bar.
    """
    
    price_series = df['close'].values
    
    if len(price_series) < period:
        print(f"WARNING: Price series length ({len(price_series)}) is less than FFT_PERIOD ({period}). Skipping FFT.")
        df['Dominant_Period'] = np.nan
        df['Phase_Rad'] = np.nan
        df['T_reversal'] = np.nan
        df['Dominant_Freq'] = np.nan
        df['Spectral_Power'] = np.nan
        return df
    
    # Initialize columns
    df['Dominant_Period'] = np.nan
    df['Phase_Rad'] = np.nan
    df['T_reversal'] = np.nan
    df['Dominant_Freq'] = np.nan
    df['Spectral_Power'] = np.nan
    
    # Perform rolling FFT analysis
    for i in range(period, len(df) + 1):
        series = price_series[i-period:i]
        N = len(series)
        T = 1.0
        
        series_detrended = series - np.mean(series)
        
        yf = fft(series_detrended)
        xf = fftfreq(N, T)[:N//2]
        
        magnitudes = 2.0/N * np.abs(yf[0:N//2])
        
        if len(magnitudes[1:]) == 0:
            continue
            
        dominant_idx = np.argmax(magnitudes[1:]) + 1
        
        if dominant_idx == 0 or xf[dominant_idx] == 0:
            continue
            
        dominant_period = 1.0 / xf[dominant_idx]
        dominant_freq = xf[dominant_idx]
        spectral_power = magnitudes[dominant_idx]
        
        phase_rad = np.arctan2(yf.imag[dominant_idx], yf.real[dominant_idx])
        phase_norm = (phase_rad + 2 * np.pi) % (2 * np.pi)
        T_reversal = (1 - phase_norm / (2 * np.pi)) * dominant_period
        
        df.iloc[i-1, df.columns.get_loc('Dominant_Period')] = dominant_period
        df.iloc[i-1, df.columns.get_loc('Phase_Rad')] = phase_norm
        df.iloc[i-1, df.columns.get_loc('T_reversal')] = T_reversal
        df.iloc[i-1, df.columns.get_loc('Dominant_Freq')] = dominant_freq
        df.iloc[i-1, df.columns.get_loc('Spectral_Power')] = spectral_power
    
    valid_count = df['Dominant_Period'].notna().sum()
    print(f"FFT Analysis: Generated phase data for {valid_count} bars (rolling window: {period})")
    
    return df

# --- Phase 5: Decision Logic and Signal Generation ---

def generate_signals_rolling(df, sigma_threshold, reversal_threshold_percent, vwap_period):
    """
    Generates trade signals for all valid bars in the DataFrame.
    
    If |E| > sigma_threshold AND φ indicates approaching reversal -> TRADE SIGNAL
    Direction: E < 0 = BUY (undervalued), E > 0 = SELL (overvalued)
    
    Returns DataFrame with signal columns added.
    """
    
    # Initialize signal columns
    df['Deviation_Signal'] = False
    df['Timing_Signal'] = False
    df['Reversal_Threshold_Bars'] = np.nan
    df['Signal'] = 'HOLD'
    df['Direction'] = 'N/A'
    df['Volume_Ratio'] = np.nan
    df['Confidence'] = 'N/A'
    
    # Calculate volume ratio for all bars
    avg_volume = df['volume'].rolling(window=vwap_period).mean()
    df['Volume_Ratio'] = df['volume'] / avg_volume
    
    # Generate signals for each bar
    for i in range(len(df)):
        E = df.iloc[i]['E']
        T_reversal = df.iloc[i]['T_reversal']
        Dominant_Period = df.iloc[i]['Dominant_Period']
        
        if pd.isna(E) or pd.isna(T_reversal) or pd.isna(Dominant_Period):
            continue
        
        # Check deviation threshold
        deviation_signal = abs(E) > sigma_threshold
        df.iloc[i, df.columns.get_loc('Deviation_Signal')] = deviation_signal
        
        # Check timing threshold
        reversal_threshold_bars = Dominant_Period * reversal_threshold_percent
        timing_signal = T_reversal < reversal_threshold_bars
        df.iloc[i, df.columns.get_loc('Timing_Signal')] = timing_signal
        df.iloc[i, df.columns.get_loc('Reversal_Threshold_Bars')] = reversal_threshold_bars
        
        # Generate signal
        if deviation_signal and timing_signal:
            if E < 0:
                df.iloc[i, df.columns.get_loc('Signal')] = 'BUY'
                df.iloc[i, df.columns.get_loc('Direction')] = 'Long'
            elif E > 0:
                df.iloc[i, df.columns.get_loc('Signal')] = 'SELL'
                df.iloc[i, df.columns.get_loc('Direction')] = 'Short'
        
        # Confidence based on volume
        vol_ratio = df.iloc[i]['Volume_Ratio']
        if not pd.isna(vol_ratio):
            if vol_ratio > 1.0:
                df.iloc[i, df.columns.get_loc('Confidence')] = 'High'
            else:
                df.iloc[i, df.columns.get_loc('Confidence')] = 'Low'
    
    signal_counts = df['Signal'].value_counts()
    print(f"Signal Generation: {signal_counts.to_dict()}")
    
    return df


def generate_signal(df, sigma_threshold, reversal_threshold_percent, symbol=None):
    """
    Generates a trade signal for the most recent bar.
    
    Returns a dictionary with the current oracle state.
    """
    
    last_row = df.iloc[-1]
    
    E = last_row['E']
    T_reversal = last_row['T_reversal']
    Dominant_Period = last_row['Dominant_Period']
    
    if pd.isna(E) or pd.isna(T_reversal) or pd.isna(Dominant_Period):
        print("WARNING: Insufficient data for signal generation (NaN values detected).")
        return {
            "Symbol": symbol or "UNKNOWN",
            "Timeframe": TIMEFRAME,
            "Current_Price": last_row['close'],
            "Final_Signal": "INSUFFICIENT_DATA",
            "Direction": "N/A",
            "Confidence": "N/A"
        }
    
    oracle_output = {
        "Symbol": symbol or "UNKNOWN",
        "Timeframe": TIMEFRAME,
        "Timestamp": last_row.name,
        "Current_Price": last_row['close'],
        "Equilibrium_Z_prime": last_row['Z_prime'],
        "Deviation": last_row['Deviation'],
        "Sigma": last_row['Sigma'],
        "Deviation_E": E,
        "Sigma_Threshold": sigma_threshold,
        "Deviation_Signal": last_row['Deviation_Signal'],
        "Dominant_Period": Dominant_Period,
        "Dominant_Freq": last_row['Dominant_Freq'],
        "Spectral_Power": last_row['Spectral_Power'],
        "Phase_Rad": last_row['Phase_Rad'],
        "Phase_Deg": np.degrees(last_row['Phase_Rad']),
        "T_reversal": T_reversal,
        "Reversal_Threshold_Bars": last_row['Reversal_Threshold_Bars'],
        "Timing_Signal": last_row['Timing_Signal'],
        "Volume_Ratio": last_row['Volume_Ratio'],
        "Final_Signal": last_row['Signal'],
        "Direction": last_row['Direction'],
        "Confidence": last_row['Confidence']
    }
    
    return oracle_output

# --- Main Execution Block ---

def run_oracle_analysis(
    exchange,
    symbol,
    timeframe,
    limit,
    vwap_period,
    fft_period,
    sigma_threshold=None,  # Now optional, will use timeframe-aware default
    reversal_threshold_percent=0.25,
    enable_backtest=False,
    enable_trend_analysis=False,
    export_csv=False,
    data_source='auto'
):
    """
    Runs complete oracle analysis with optional enhancements.
    
    Args:
        exchange: CCXT exchange object (can be None if using CoinGecko)
        symbol: Trading pair
        timeframe: Candle interval
        limit: Number of bars to fetch
        vwap_period: VWAP calculation period
        fft_period: FFT analysis period
        sigma_threshold: Deviation threshold (None = use timeframe-aware default)
        reversal_threshold_percent: Phase timing threshold
        enable_backtest: Run backtest analysis
        enable_trend_analysis: Add trend and regime detection
        export_csv: Export signals to CSV
        data_source: 'auto', 'coingecko', or 'exchange'
    
    Returns:
        Tuple of (dataframe, oracle_result, backtest_report)
    """
    
    # Use timeframe-aware threshold if not specified
    if sigma_threshold is None:
        from config import get_sigma_threshold
        sigma_threshold = get_sigma_threshold(timeframe)
        print(f"📊 Using timeframe-aware threshold: {sigma_threshold}σ for {timeframe}")
    
    # Fetch data from configured source
    data_df = fetch_ohlcv_data(exchange, symbol, timeframe, limit, source=data_source)
    
    if data_df is None or data_df.empty:
        print("❌ Could not fetch data. Please check configuration and network connection.")
        return None, None, None
    
    # Calculate indicators
    data_df = calculate_vwap_and_deviation(data_df, vwap_period, sigma_threshold)
    data_df = calculate_fft_phase(data_df, fft_period)
    data_df = generate_signals_rolling(data_df, sigma_threshold, reversal_threshold_percent, vwap_period)
    
    # Optional: Add trend analysis
    if enable_trend_analysis:
        print("\n" + "="*60)
        print("TREND & REGIME ANALYSIS")
        print("="*60)
        from trend_analysis import enhance_signal_with_context, get_regime_statistics
        data_df = enhance_signal_with_context(data_df)
        regime_stats = get_regime_statistics(data_df)
        print(f"\nRegime Distribution: {regime_stats['regime_distribution']}")
        print(f"Trend Distribution: {regime_stats['trend_distribution']}")
    
    # Generate current signal
    oracle_result = generate_signal(data_df, sigma_threshold, reversal_threshold_percent, symbol)
    
    # Optional: Run backtest
    backtest_report = None
    if enable_backtest:
        from backtest import generate_backtest_report, print_backtest_report
        backtest_report = generate_backtest_report(data_df, symbol, timeframe)
        print_backtest_report(backtest_report)
    
    # Optional: Export to CSV
    if export_csv:
        from backtest import export_signals_to_csv
        filename = f"oracle_signals_{symbol.replace('/', '_')}_{timeframe}.csv"
        export_signals_to_csv(data_df, filename)
    
    return data_df, oracle_result, backtest_report


if __name__ == '__main__':
    # Parse command line arguments
    enable_backtest = '--backtest' in sys.argv
    enable_trend = '--trend' in sys.argv
    export_csv = '--export' in sys.argv
    
    # Parse symbols from command line or use config
    symbols_to_analyze = []
    
    # Check for --symbols flag
    if '--symbols' in sys.argv:
        idx = sys.argv.index('--symbols')
        if idx + 1 < len(sys.argv):
            # Get comma-separated symbols
            symbols_arg = sys.argv[idx + 1]
            symbols_to_analyze = [s.strip() for s in symbols_arg.split(',')]
    
    # If no command line symbols, use config
    if not symbols_to_analyze:
        if isinstance(SYMBOLS, list):
            symbols_to_analyze = SYMBOLS  # Analyze all configured symbols
        else:
            symbols_to_analyze = [SYMBOLS]
    
    # No artificial limit - analyze all requested symbols
    
    try:
        validate_config()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration Error:\n{e}")
        exit(1)
    
    # Initialize data source (exchange or CoinGecko)
    exchange, source_type = initialize_data_source()
    
    print(f"\n📊 Analyzing {len(symbols_to_analyze)} symbol(s): {', '.join(symbols_to_analyze)}\n")
    
    # Analyze each symbol
    all_results = []
    
    for symbol in symbols_to_analyze:
        print("\n" + "="*60)
        print(f"ANALYZING: {symbol}")
        print("="*60)
        
        # Run analysis with configured data source
        data_df, oracle_result, backtest_report = run_oracle_analysis(
            exchange=exchange,
            symbol=symbol,
            timeframe=TIMEFRAME,
            limit=LIMIT,
            vwap_period=VWAP_PERIOD,
            fft_period=FFT_PERIOD,
            sigma_threshold=SIGMA_THRESHOLD,
            reversal_threshold_percent=REVERSAL_THRESHOLD_PERCENT,
            enable_backtest=enable_backtest,
            enable_trend_analysis=enable_trend,
            export_csv=export_csv,
            data_source=source_type
        )
        
        if oracle_result:
            all_results.append(oracle_result)
            
            print("\n" + "="*60)
            print(f"CURRENT ORACLE STATE: {symbol}")
            print("="*60)
            for key, value in oracle_result.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.6f}")
                elif isinstance(value, bool):
                    print(f"{key}: {value}")
                else:
                    print(f"{key}: {value}")
            print("="*60)
        else:
            print(f"❌ Oracle analysis failed for {symbol}.")
    
    # Summary comparison if multiple symbols
    if len(all_results) > 1:
        print("\n" + "="*60)
        print("MULTI-SYMBOL COMPARISON")
        print("="*60)
        
        print(f"\n{'Symbol':<12} {'Signal':<6} {'Price':<12} {'Deviation':<10} {'Confidence':<12}")
        print("-" * 60)
        
        for result in all_results:
            signal_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '⚪'}.get(result['Final_Signal'], '⚪')
            print(f"{result['Symbol']:<12} {signal_emoji} {result['Final_Signal']:<6} "
                  f"${result['Current_Price']:<11.6f} {result['Deviation_E']:>+9.3f}σ "
                  f"{result['Confidence']:<12}")
        
        print("="*60)
        
        # Count signals
        buy_count = sum(1 for r in all_results if r['Final_Signal'] == 'BUY')
        sell_count = sum(1 for r in all_results if r['Final_Signal'] == 'SELL')
        hold_count = sum(1 for r in all_results if r['Final_Signal'] == 'HOLD')
        
        print(f"\nSignal Summary: {buy_count} BUY, {sell_count} SELL, {hold_count} HOLD")
        
        if buy_count > 0 or sell_count > 0:
            print("\n⚠️  Active signals detected! Review individual analysis above.")
        else:
            print("\n✅ All symbols on HOLD - no active signals.")
    
    # Print usage hint
    if not enable_backtest and not enable_trend and len(symbols_to_analyze) == 1:
        print("\n💡 Tip: Run with --backtest for performance analysis")
        print("💡 Tip: Run with --trend for market regime detection")
        print("💡 Tip: Run with --export to save signals to CSV")
        print("💡 Tip: Run with --symbols BTC/USD,ETH/USD,DOGE/USD to analyze multiple symbols")
    
    if len(all_results) == 0:
        print("❌ All oracle analyses failed.")
        exit(1)
