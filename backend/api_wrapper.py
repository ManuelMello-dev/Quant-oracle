"""
API Wrapper - Simplified interface for backend modules
Provides consistent API for web/mobile frontends
"""

import pandas as pd
from typing import Optional, List, Dict
import sys
import os

# Import backend modules
from oracle import run_oracle_analysis
from data_sources import fetch_ohlcv_data
from config import (
    VWAP_PERIOD, FFT_PERIOD, SIGMA_THRESHOLD, 
    REVERSAL_THRESHOLD_PERCENT
)
VOLUME_THRESHOLD_PERCENT = 100  # Default if not in config


def analyze_symbol(symbol: str, timeframe: str = '1h', days: int = 365) -> Optional[pd.DataFrame]:
    """
    Analyze a trading symbol with all indicators
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USD')
        timeframe: Candle timeframe ('1h', '4h', '1d')
        days: Historical days to fetch
        
    Returns:
        DataFrame with OHLCV + indicators, or None if failed
    """
    try:
        # Calculate limit based on timeframe and days
        if timeframe == '1h':
            limit = days * 24
        elif timeframe == '4h':
            limit = days * 6
        elif timeframe == '1d':
            limit = days
        else:
            limit = days * 24  # Default to 1h
        
        # Initialize exchange (required by run_oracle_analysis)
        import ccxt
        exchange = ccxt.binance()
        
        # Run analysis (it fetches data internally and returns tuple)
        result = run_oracle_analysis(
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
            vwap_period=VWAP_PERIOD,
            fft_period=FFT_PERIOD,
            sigma_threshold=SIGMA_THRESHOLD,
            reversal_threshold_percent=REVERSAL_THRESHOLD_PERCENT,
            enable_backtest=False,
            enable_trend_analysis=True,
            export_csv=False,
            data_source='auto'
        )
        
        # Extract DataFrame from tuple (df, stats, backtest_results)
        if isinstance(result, tuple):
            df = result[0]
        else:
            df = result
        
        return df
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_backtest(
    symbol: str,
    timeframe: str = '1h',
    days: int = 365,
    holding_periods: List[int] = [5, 10, 20]
) -> Optional[Dict]:
    """
    Run backtest on historical data
    
    Args:
        symbol: Trading pair
        timeframe: Candle timeframe
        days: Historical period
        holding_periods: Holding periods to test
        
    Returns:
        Dict with backtest results
    """
    try:
        # Get analysis
        df = analyze_symbol(symbol, timeframe, days)
        if df is None or len(df) == 0:
            return None
        
        # Calculate forward returns
        for period in holding_periods:
            df[f'forward_return_{period}'] = (
                df['close'].shift(-period) / df['close'] - 1
            ) * 100
        
        # Analyze signal performance
        results = {
            'symbol': symbol,
            'timeframe': timeframe,
            'period_days': days,
            'total_bars': len(df),
            'signal_performance': {}
        }
        
        for signal in ['BUY', 'SELL', 'HOLD']:
            signal_df = df[df['Signal'] == signal].copy()
            if len(signal_df) > 0:
                results['signal_performance'][signal] = {
                    'count': len(signal_df),
                    'win_rate_10': float((signal_df['forward_return_10'] > 0).mean() * 100) if 'forward_return_10' in signal_df else 0,
                    'mean_return_10': float(signal_df['forward_return_10'].mean()) if 'forward_return_10' in signal_df else 0,
                    'median_return_10': float(signal_df['forward_return_10'].median()) if 'forward_return_10' in signal_df else 0
                }
        
        return results
        
    except Exception as e:
        print(f"Error backtesting {symbol}: {e}")
        return None


def analyze_multiple_timeframes(
    symbol: str,
    timeframes: List[str] = ['1h', '4h', '1d']
) -> Optional[Dict]:
    """
    Analyze symbol across multiple timeframes
    
    Args:
        symbol: Trading pair
        timeframes: List of timeframes to analyze
        
    Returns:
        Dict with multi-timeframe results
    """
    try:
        results = {
            'symbol': symbol,
            'timeframes': {}
        }
        
        signals = []
        deviations = []
        
        for tf in timeframes:
            df = analyze_symbol(symbol, tf, days=90)
            if df is not None and len(df) > 0:
                latest = df.iloc[-1]
                results['timeframes'][tf] = {
                    'signal': latest['Signal'],
                    'deviation': float(latest['E']),
                    'volume_ratio': float(latest['Volume_Ratio']),
                    'trend': latest.get('trend', 'unknown')
                }
                signals.append(latest['Signal'])
                deviations.append(float(latest['E']))
        
        # Calculate confluence
        if signals:
            buy_count = signals.count('BUY')
            sell_count = signals.count('SELL')
            total = len(signals)
            
            if buy_count > sell_count:
                recommendation = 'BUY'
                score = (buy_count / total) * 100
            elif sell_count > buy_count:
                recommendation = 'SELL'
                score = (sell_count / total) * 100
            else:
                recommendation = 'HOLD'
                score = 50.0
            
            results['confluence'] = {
                'score': score,
                'recommendation': recommendation
            }
        
        return results
        
    except Exception as e:
        print(f"Error in multi-timeframe analysis for {symbol}: {e}")
        return None


# Export functions
__all__ = [
    'analyze_symbol',
    'run_backtest',
    'analyze_multiple_timeframes'
]
