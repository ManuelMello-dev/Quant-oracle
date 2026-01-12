#!/usr/bin/env python3
"""
Example: Multi-Timeframe Analysis

Demonstrates how to use the oracle across multiple timeframes
to detect signal confluence.
"""

from multi_timeframe import (
    analyze_multiple_timeframes,
    calculate_timeframe_confluence,
    print_multi_timeframe_summary,
    align_timeframes
)
from oracle import initialize_exchange
from config import (
    SYMBOL, LIMIT, VWAP_PERIOD, FFT_PERIOD,
    SIGMA_THRESHOLD, REVERSAL_THRESHOLD_PERCENT,
    validate_config
)


def main():
    """Run multi-timeframe analysis."""
    
    print("="*60)
    print("MULTI-TIMEFRAME ORACLE ANALYSIS")
    print("="*60)
    
    # Validate configuration
    try:
        validate_config()
        print("✅ Configuration validated\n")
    except ValueError as e:
        print(f"❌ Configuration Error:\n{e}")
        return
    
    # Initialize exchange
    exchange = initialize_exchange()
    if not exchange:
        print("❌ Failed to initialize exchange")
        return
    
    # Define timeframes to analyze
    # Choose based on your trading style:
    # - Scalping: ['5m', '15m', '1h']
    # - Intraday: ['15m', '1h', '4h']
    # - Swing: ['1h', '4h', '1d']
    # - Position: ['4h', '1d', '1w']
    
    timeframes = ['1h', '4h', '1d']
    
    print(f"Analyzing {SYMBOL} across timeframes: {timeframes}\n")
    
    # Perform analysis
    results = analyze_multiple_timeframes(
        exchange=exchange,
        symbol=SYMBOL,
        timeframes=timeframes,
        limit=LIMIT,
        vwap_period=VWAP_PERIOD,
        fft_period=FFT_PERIOD,
        sigma_threshold=SIGMA_THRESHOLD,
        reversal_threshold_percent=REVERSAL_THRESHOLD_PERCENT
    )
    
    if not results:
        print("❌ No results obtained")
        return
    
    # Calculate confluence
    confluence = calculate_timeframe_confluence(results)
    
    # Calculate weighted alignment
    alignment = align_timeframes(results)
    
    # Print summary
    print_multi_timeframe_summary(SYMBOL, results, confluence)
    
    # Print weighted alignment
    print("\n" + "="*60)
    print("WEIGHTED TIMEFRAME ALIGNMENT")
    print("="*60)
    print(f"\nWeighted Scores:")
    for signal, score in alignment['weighted_scores'].items():
        print(f"  {signal}: {score:.1f}%")
    print(f"\nDominant Signal (Weighted): {alignment['dominant_signal']}")
    print(f"Confidence: {alignment['dominant_score']:.1f}%")
    print("="*60)
    
    # Trading recommendation
    print("\n" + "="*60)
    print("TRADING RECOMMENDATION")
    print("="*60)
    
    if confluence['agreement'] == 'STRONG' and alignment['dominant_score'] > 60:
        print(f"\n✅ STRONG SIGNAL: {alignment['dominant_signal']}")
        print("   Multiple timeframes agree with high confidence")
        print("   Consider this signal for trading")
    elif confluence['agreement'] == 'MODERATE':
        print(f"\n⚠️  MODERATE SIGNAL: {alignment['dominant_signal']}")
        print("   Some timeframe disagreement exists")
        print("   Wait for stronger confluence or use smaller position size")
    else:
        print(f"\n❌ WEAK SIGNAL: Mixed signals across timeframes")
        print("   Do not trade - wait for clearer setup")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
