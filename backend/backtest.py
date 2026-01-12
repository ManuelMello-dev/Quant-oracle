"""
Backtesting module for the Quant Oracle.

Analyzes historical signal performance without executing trades.
Provides metrics on signal accuracy, timing, and market conditions.
"""

import pandas as pd
import numpy as np


def calculate_forward_returns(df, periods=[1, 3, 5, 10, 24]):
    """
    Calculates forward returns for multiple time horizons.
    
    Args:
        df: DataFrame with OHLCV data
        periods: List of forward-looking periods (in bars)
    
    Returns:
        DataFrame with forward return columns added
    """
    for period in periods:
        df[f'Forward_Return_{period}'] = (
            df['close'].shift(-period) / df['close'] - 1
        ) * 100
    
    return df


def analyze_signal_performance(df, signal_col='Signal'):
    """
    Analyzes the performance of generated signals.
    
    Calculates metrics for BUY and SELL signals separately.
    """
    
    results = {
        'total_bars': len(df),
        'valid_bars': df[signal_col].notna().sum(),
        'signals': {}
    }
    
    for signal_type in ['BUY', 'SELL']:
        signal_mask = df[signal_col] == signal_type
        signal_count = signal_mask.sum()
        
        if signal_count == 0:
            results['signals'][signal_type] = {
                'count': 0,
                'percentage': 0.0
            }
            continue
        
        signal_data = df[signal_mask].copy()
        
        metrics = {
            'count': signal_count,
            'percentage': (signal_count / len(df)) * 100,
            'avg_deviation_e': signal_data['E'].mean(),
            'avg_volume_ratio': signal_data['Volume_Ratio'].mean(),
            'high_confidence_pct': (signal_data['Confidence'] == 'High').sum() / signal_count * 100,
            'forward_returns': {}
        }
        
        # Calculate forward return statistics
        for col in df.columns:
            if col.startswith('Forward_Return_'):
                period = col.split('_')[-1]
                returns = signal_data[col].dropna()
                
                if len(returns) > 0:
                    # For BUY signals, positive returns are good
                    # For SELL signals, negative returns are good (price went down)
                    if signal_type == 'SELL':
                        returns = -returns  # Invert for SELL signals
                    
                    metrics['forward_returns'][period] = {
                        'mean': returns.mean(),
                        'median': returns.median(),
                        'std': returns.std(),
                        'win_rate': (returns > 0).sum() / len(returns) * 100,
                        'best': returns.max(),
                        'worst': returns.min()
                    }
        
        results['signals'][signal_type] = metrics
    
    return results


def analyze_phase_accuracy(df):
    """
    Analyzes the accuracy of phase-based reversal predictions.
    
    Checks if price actually reversed within the predicted timeframe.
    """
    
    results = {
        'total_predictions': 0,
        'accurate_predictions': 0,
        'false_predictions': 0,
        'avg_error_bars': 0.0
    }
    
    # Only analyze bars with valid phase data and signals
    valid_mask = (
        df['T_reversal'].notna() & 
        df['Timing_Signal'] == True
    )
    
    valid_data = df[valid_mask].copy()
    
    if len(valid_data) == 0:
        return results
    
    results['total_predictions'] = len(valid_data)
    
    errors = []
    
    for idx, row in valid_data.iterrows():
        t_reversal = int(row['T_reversal'])
        signal_type = row['Signal']
        
        # Get the position in the dataframe
        pos = df.index.get_loc(idx)
        
        # Look ahead up to t_reversal + buffer
        lookback = min(t_reversal + 5, len(df) - pos - 1)
        
        if lookback <= 0:
            continue
        
        future_prices = df.iloc[pos+1:pos+1+lookback]['close'].values
        current_price = row['close']
        
        if len(future_prices) == 0:
            continue
        
        # Check for reversal based on signal type
        if signal_type == 'BUY':
            # Expecting price to go up (was undervalued)
            reversal_occurred = np.any(future_prices > current_price * 1.01)  # 1% threshold
            if reversal_occurred:
                reversal_bar = np.argmax(future_prices > current_price * 1.01)
                errors.append(abs(reversal_bar - t_reversal))
                results['accurate_predictions'] += 1
            else:
                results['false_predictions'] += 1
                
        elif signal_type == 'SELL':
            # Expecting price to go down (was overvalued)
            reversal_occurred = np.any(future_prices < current_price * 0.99)  # 1% threshold
            if reversal_occurred:
                reversal_bar = np.argmax(future_prices < current_price * 0.99)
                errors.append(abs(reversal_bar - t_reversal))
                results['accurate_predictions'] += 1
            else:
                results['false_predictions'] += 1
    
    if errors:
        results['avg_error_bars'] = np.mean(errors)
        results['median_error_bars'] = np.median(errors)
    
    if results['total_predictions'] > 0:
        results['accuracy_rate'] = (
            results['accurate_predictions'] / results['total_predictions'] * 100
        )
    
    return results


def analyze_market_conditions(df):
    """
    Analyzes market conditions during signal generation.
    
    Categorizes market as trending, ranging, or volatile.
    """
    
    results = {
        'overall': {},
        'by_signal': {}
    }
    
    # Calculate trend strength (using linear regression slope)
    df['Trend_Strength'] = df['close'].rolling(window=50).apply(
        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == 50 else np.nan
    )
    
    # Calculate volatility (rolling std)
    df['Volatility'] = df['close'].pct_change().rolling(window=20).std() * 100
    
    # Overall statistics
    results['overall'] = {
        'avg_trend_strength': df['Trend_Strength'].mean(),
        'avg_volatility': df['Volatility'].mean(),
        'trend_direction': 'Uptrend' if df['Trend_Strength'].mean() > 0 else 'Downtrend'
    }
    
    # Statistics by signal type
    for signal_type in ['BUY', 'SELL', 'HOLD']:
        signal_mask = df['Signal'] == signal_type
        signal_data = df[signal_mask]
        
        if len(signal_data) > 0:
            results['by_signal'][signal_type] = {
                'count': len(signal_data),
                'avg_trend_strength': signal_data['Trend_Strength'].mean(),
                'avg_volatility': signal_data['Volatility'].mean()
            }
    
    return results


def generate_backtest_report(df, symbol, timeframe):
    """
    Generates a comprehensive backtest report.
    
    Returns a dictionary with all analysis results.
    """
    
    print("\n" + "="*60)
    print(f"BACKTEST REPORT: {symbol} @ {timeframe}")
    print("="*60)
    
    # Calculate forward returns
    df = calculate_forward_returns(df)
    
    # Analyze signal performance
    print("\n[1/3] Analyzing signal performance...")
    signal_perf = analyze_signal_performance(df)
    
    # Analyze phase accuracy
    print("[2/3] Analyzing phase prediction accuracy...")
    phase_acc = analyze_phase_accuracy(df)
    
    # Analyze market conditions
    print("[3/3] Analyzing market conditions...")
    market_cond = analyze_market_conditions(df)
    
    report = {
        'symbol': symbol,
        'timeframe': timeframe,
        'period': {
            'start': df.index[0],
            'end': df.index[-1],
            'total_bars': len(df)
        },
        'signal_performance': signal_perf,
        'phase_accuracy': phase_acc,
        'market_conditions': market_cond
    }
    
    return report


def print_backtest_report(report):
    """
    Prints a formatted backtest report to console.
    """
    
    print("\n" + "="*60)
    print("SIGNAL PERFORMANCE SUMMARY")
    print("="*60)
    
    sp = report['signal_performance']
    print(f"\nTotal Bars Analyzed: {sp['total_bars']}")
    print(f"Valid Signal Bars: {sp['valid_bars']}")
    
    for signal_type in ['BUY', 'SELL']:
        if signal_type not in sp['signals']:
            continue
            
        metrics = sp['signals'][signal_type]
        print(f"\n{signal_type} SIGNALS:")
        print(f"  Count: {metrics['count']} ({metrics['percentage']:.2f}%)")
        
        if metrics['count'] == 0:
            continue
            
        print(f"  Avg Deviation (E): {metrics['avg_deviation_e']:.3f}")
        print(f"  Avg Volume Ratio: {metrics['avg_volume_ratio']:.3f}")
        print(f"  High Confidence: {metrics['high_confidence_pct']:.1f}%")
        
        if metrics['forward_returns']:
            print(f"\n  Forward Returns:")
            for period, stats in sorted(metrics['forward_returns'].items(), key=lambda x: int(x[0])):
                print(f"    {period} bars: Mean={stats['mean']:+.2f}%, "
                      f"Median={stats['median']:+.2f}%, "
                      f"WinRate={stats['win_rate']:.1f}%")
    
    print("\n" + "="*60)
    print("PHASE PREDICTION ACCURACY")
    print("="*60)
    
    pa = report['phase_accuracy']
    if pa['total_predictions'] > 0:
        print(f"\nTotal Predictions: {pa['total_predictions']}")
        print(f"Accurate: {pa['accurate_predictions']} ({pa.get('accuracy_rate', 0):.1f}%)")
        print(f"False: {pa['false_predictions']}")
        if 'avg_error_bars' in pa and pa['avg_error_bars'] > 0:
            print(f"Avg Timing Error: {pa['avg_error_bars']:.1f} bars")
            print(f"Median Timing Error: {pa.get('median_error_bars', 0):.1f} bars")
    else:
        print("\nNo phase predictions to analyze")
    
    print("\n" + "="*60)
    print("MARKET CONDITIONS")
    print("="*60)
    
    mc = report['market_conditions']
    overall = mc['overall']
    print(f"\nOverall Trend: {overall['trend_direction']}")
    print(f"Avg Trend Strength: {overall['avg_trend_strength']:.6f}")
    print(f"Avg Volatility: {overall['avg_volatility']:.3f}%")
    
    if mc['by_signal']:
        print("\nConditions by Signal Type:")
        for signal_type, stats in mc['by_signal'].items():
            print(f"  {signal_type}: Count={stats['count']}, "
                  f"Trend={stats['avg_trend_strength']:.6f}, "
                  f"Vol={stats['avg_volatility']:.3f}%")
    
    print("\n" + "="*60)


def export_signals_to_csv(df, filename='oracle_signals.csv'):
    """
    Exports signal data to CSV for external analysis.
    """
    
    export_cols = [
        'open', 'high', 'low', 'close', 'volume',
        'Z_prime', 'Deviation', 'Sigma', 'E',
        'Dominant_Period', 'Phase_Rad', 'T_reversal',
        'Deviation_Signal', 'Timing_Signal',
        'Signal', 'Direction', 'Confidence', 'Volume_Ratio'
    ]
    
    # Only export columns that exist
    export_cols = [col for col in export_cols if col in df.columns]
    
    df[export_cols].to_csv(filename)
    print(f"\n✅ Exported signal data to {filename}")
    
    return filename
