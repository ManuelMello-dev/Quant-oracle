#!/usr/bin/env python3
"""
Example: Visual Analysis

Demonstrates ASCII visualization capabilities of the oracle.
"""

from oracle import (
    initialize_exchange,
    run_oracle_analysis
)
from visualize import print_visual_analysis
from config import (
    SYMBOL, TIMEFRAME, LIMIT, VWAP_PERIOD, FFT_PERIOD,
    SIGMA_THRESHOLD, REVERSAL_THRESHOLD_PERCENT,
    validate_config
)


def main():
    """Run oracle with visual output."""
    
    print("="*60)
    print("VISUAL ORACLE ANALYSIS")
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
    
    # Run analysis
    data_df, oracle_result, _ = run_oracle_analysis(
        exchange=exchange,
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        limit=LIMIT,
        vwap_period=VWAP_PERIOD,
        fft_period=FFT_PERIOD,
        sigma_threshold=SIGMA_THRESHOLD,
        reversal_threshold_percent=REVERSAL_THRESHOLD_PERCENT,
        enable_backtest=False,
        enable_trend_analysis=False,
        export_csv=False
    )
    
    if oracle_result is None:
        print("❌ Analysis failed")
        return
    
    # Print visual analysis
    print_visual_analysis(oracle_result, data_df)


if __name__ == '__main__':
    main()
