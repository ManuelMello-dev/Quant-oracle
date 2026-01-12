"""
Multiple Timeframe Analysis for the Quant Oracle.

Analyzes signals across different timeframes to improve confidence.
Implements timeframe alignment and confluence detection.
"""

import pandas as pd
import numpy as np
from oracle import (
    fetch_ohlcv_data,
    calculate_vwap_and_deviation,
    calculate_fft_phase,
    generate_signals_rolling
)


def fetch_multiple_timeframes(exchange, symbol, timeframes, limit):
    """
    Fetches OHLCV data for multiple timeframes.
    
    Args:
        exchange: CCXT exchange object
        symbol: Trading pair symbol
        timeframes: List of timeframe strings (e.g., ['1h', '4h', '1d'])
        limit: Number of bars to fetch per timeframe
    
    Returns:
        Dictionary mapping timeframe to DataFrame
    """
    
    data = {}
    
    for tf in timeframes:
        print(f"\nFetching {symbol} @ {tf}...")
        df = fetch_ohlcv_data(exchange, symbol, tf, limit)
        
        if df is not None and not df.empty:
            data[tf] = df
        else:
            print(f"⚠️  Failed to fetch data for {tf}")
    
    return data


def analyze_multiple_timeframes(
    exchange, 
    symbol, 
    timeframes, 
    limit,
    vwap_period,
    fft_period,
    sigma_threshold,
    reversal_threshold_percent
):
    """
    Performs oracle analysis across multiple timeframes.
    
    Returns a dictionary with analysis results for each timeframe.
    """
    
    results = {}
    
    # Fetch data for all timeframes
    data = fetch_multiple_timeframes(exchange, symbol, timeframes, limit)
    
    # Analyze each timeframe
    for tf, df in data.items():
        print(f"\n{'='*60}")
        print(f"Analyzing {symbol} @ {tf}")
        print(f"{'='*60}")
        
        # Calculate indicators
        df = calculate_vwap_and_deviation(df, vwap_period, sigma_threshold)
        df = calculate_fft_phase(df, fft_period)
        df = generate_signals_rolling(df, sigma_threshold, reversal_threshold_percent, vwap_period)
        
        # Get current signal
        last_row = df.iloc[-1]
        
        results[tf] = {
            'dataframe': df,
            'current_signal': last_row['Signal'],
            'current_direction': last_row['Direction'],
            'current_confidence': last_row['Confidence'],
            'deviation_e': last_row['E'],
            'phase_deg': np.degrees(last_row['Phase_Rad']) if not pd.isna(last_row['Phase_Rad']) else np.nan,
            't_reversal': last_row['T_reversal'],
            'volume_ratio': last_row['Volume_Ratio']
        }
    
    return results


def calculate_timeframe_confluence(results):
    """
    Calculates signal confluence across timeframes.
    
    Higher confluence = more timeframes agree on the signal.
    """
    
    if not results:
        return {
            'confluence_score': 0,
            'agreement': 'NONE',
            'details': {}
        }
    
    signals = [r['current_signal'] for r in results.values()]
    directions = [r['current_direction'] for r in results.values()]
    
    # Count signal types
    buy_count = signals.count('BUY')
    sell_count = signals.count('SELL')
    hold_count = signals.count('HOLD')
    
    total = len(signals)
    
    # Determine confluence
    if buy_count > sell_count and buy_count > hold_count:
        dominant_signal = 'BUY'
        confluence_score = buy_count / total * 100
    elif sell_count > buy_count and sell_count > hold_count:
        dominant_signal = 'SELL'
        confluence_score = sell_count / total * 100
    else:
        dominant_signal = 'HOLD'
        confluence_score = hold_count / total * 100
    
    # Determine agreement level
    if confluence_score >= 75:
        agreement = 'STRONG'
    elif confluence_score >= 50:
        agreement = 'MODERATE'
    else:
        agreement = 'WEAK'
    
    confluence = {
        'confluence_score': confluence_score,
        'dominant_signal': dominant_signal,
        'agreement': agreement,
        'details': {
            'BUY': buy_count,
            'SELL': sell_count,
            'HOLD': hold_count,
            'total_timeframes': total
        }
    }
    
    return confluence


def print_multi_timeframe_summary(symbol, results, confluence):
    """
    Prints a formatted summary of multi-timeframe analysis.
    """
    
    print("\n" + "="*60)
    print(f"MULTI-TIMEFRAME ANALYSIS: {symbol}")
    print("="*60)
    
    print("\nIndividual Timeframe Signals:")
    print("-" * 60)
    
    for tf, data in results.items():
        signal = data['current_signal']
        direction = data['current_direction']
        confidence = data['current_confidence']
        deviation_e = data['deviation_e']
        
        signal_emoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '⚪'
        }.get(signal, '⚪')
        
        print(f"{signal_emoji} {tf:>4s}: {signal:>4s} {direction:>5s} | "
              f"Confidence: {confidence:>4s} | E: {deviation_e:+.3f}")
    
    print("\n" + "="*60)
    print("CONFLUENCE ANALYSIS")
    print("="*60)
    
    print(f"\nDominant Signal: {confluence['dominant_signal']}")
    print(f"Confluence Score: {confluence['confluence_score']:.1f}%")
    print(f"Agreement Level: {confluence['agreement']}")
    
    print(f"\nSignal Distribution:")
    for signal_type, count in confluence['details'].items():
        if signal_type != 'total_timeframes':
            pct = count / confluence['details']['total_timeframes'] * 100
            print(f"  {signal_type}: {count} ({pct:.1f}%)")
    
    print("\n" + "="*60)
    
    # Recommendation
    if confluence['agreement'] == 'STRONG':
        print(f"\n✅ STRONG CONFLUENCE: {confluence['dominant_signal']} signal across multiple timeframes")
    elif confluence['agreement'] == 'MODERATE':
        print(f"\n⚠️  MODERATE CONFLUENCE: {confluence['dominant_signal']} signal with some disagreement")
    else:
        print(f"\n❌ WEAK CONFLUENCE: Mixed signals across timeframes - exercise caution")
    
    print("="*60 + "\n")


def get_timeframe_hierarchy():
    """
    Returns standard timeframe hierarchies for analysis.
    """
    
    hierarchies = {
        'intraday': ['15m', '1h', '4h'],
        'swing': ['1h', '4h', '1d'],
        'position': ['4h', '1d', '1w'],
        'scalp': ['5m', '15m', '1h']
    }
    
    return hierarchies


def align_timeframes(results):
    """
    Aligns signals from different timeframes based on their hierarchy.
    
    Higher timeframes (e.g., 1d) carry more weight than lower timeframes (e.g., 1h).
    """
    
    # Timeframe weights (higher = more important)
    weights = {
        '1m': 1,
        '5m': 2,
        '15m': 3,
        '30m': 4,
        '1h': 5,
        '2h': 6,
        '4h': 7,
        '6h': 8,
        '12h': 9,
        '1d': 10,
        '3d': 11,
        '1w': 12,
        '1M': 13
    }
    
    weighted_scores = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    total_weight = 0
    
    for tf, data in results.items():
        signal = data['current_signal']
        weight = weights.get(tf, 5)  # Default weight if timeframe not in dict
        
        weighted_scores[signal] += weight
        total_weight += weight
    
    # Normalize scores
    for signal in weighted_scores:
        weighted_scores[signal] = (weighted_scores[signal] / total_weight) * 100
    
    # Determine weighted dominant signal
    dominant_signal = max(weighted_scores, key=weighted_scores.get)
    
    alignment = {
        'weighted_scores': weighted_scores,
        'dominant_signal': dominant_signal,
        'dominant_score': weighted_scores[dominant_signal]
    }
    
    return alignment
