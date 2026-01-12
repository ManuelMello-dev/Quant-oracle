# Quant Oracle Usage Guide

Complete guide to using the enhanced oracle system.

## Quick Start

### 1. Basic Analysis

```bash
python oracle.py
```

Shows current oracle state with key metrics.

### 2. Full Analysis

```bash
python oracle.py --backtest --trend --export
```

Includes:
- Historical signal performance
- Forward return analysis
- Market regime detection
- Trend context
- CSV export

### 3. Visual Analysis

```bash
python example_visual.py
```

Displays:
- ASCII dashboard
- Price chart
- Deviation heatmap
- Signal timeline
- Phase cycle diagram

### 4. Multi-Timeframe Analysis

```bash
python example_multi_timeframe.py
```

Analyzes confluence across 1h, 4h, and 1d timeframes.

## Command-Line Options

### `--backtest`

Analyzes historical signal performance:

```bash
python oracle.py --backtest
```

**Output:**
- Signal counts and percentages
- Forward returns at 1, 3, 5, 10, 24 bar horizons
- Win rates for BUY/SELL signals
- Phase prediction accuracy
- Market condition statistics

**Use when:**
- Evaluating oracle performance
- Understanding signal characteristics
- Validating strategy before use

### `--trend`

Adds trend and regime analysis:

```bash
python oracle.py --trend
```

**Output:**
- Trend direction (Uptrend/Downtrend)
- Market regime (Trending/Ranging/Volatile)
- Signal quality adjustment
- Cycle consistency scores

**Use when:**
- Need context for signals
- Want to filter signals by market condition
- Improving signal quality

### `--export`

Exports signals to CSV:

```bash
python oracle.py --export
```

**Output:**
- File: `oracle_signals_{SYMBOL}_{TIMEFRAME}.csv`
- Contains all OHLCV data, indicators, and signals

**Use when:**
- Need external analysis
- Building custom visualizations
- Archiving historical signals

## Configuration

Edit `config.py` or set environment variables:

```python
# Exchange credentials (optional for Kraken fallback)
export COINBASE_API_KEY='your_key'
export COINBASE_SECRET='your_secret'

# Oracle parameters
SYMBOL = 'DOGE/USD'          # Trading pair
TIMEFRAME = '1h'             # Candle interval
LIMIT = 500                  # Historical bars to fetch
VWAP_PERIOD = 100            # VWAP calculation window
FFT_PERIOD = 256             # FFT analysis window (power of 2)
SIGMA_THRESHOLD = 2.0        # Deviation threshold
REVERSAL_THRESHOLD_PERCENT = 0.10  # Phase timing threshold
```

### Recommended Settings by Trading Style

**Scalping (5m-15m):**
```python
TIMEFRAME = '5m'
LIMIT = 1000
VWAP_PERIOD = 50
FFT_PERIOD = 128
```

**Intraday (1h-4h):**
```python
TIMEFRAME = '1h'
LIMIT = 500
VWAP_PERIOD = 100
FFT_PERIOD = 256
```

**Swing (4h-1d):**
```python
TIMEFRAME = '4h'
LIMIT = 500
VWAP_PERIOD = 100
FFT_PERIOD = 256
```

**Position (1d-1w):**
```python
TIMEFRAME = '1d'
LIMIT = 365
VWAP_PERIOD = 50
FFT_PERIOD = 128
```

## Understanding Output

### Oracle State

```
Symbol: DOGE/USD
Current_Price: 0.152210
Equilibrium_Z_prime: 0.135557    # VWAP equilibrium price
Deviation_E: 2.223275            # Standardized deviation (σ units)
Final_Signal: HOLD/BUY/SELL
Direction: Long/Short/N/A
Confidence: High/Medium/Low
```

### Signal Interpretation

**BUY Signal:**
- Price is below equilibrium (undervalued)
- Deviation exceeds threshold (|E| > 2σ)
- Phase indicates approaching reversal
- Expecting price to rise back to equilibrium

**SELL Signal:**
- Price is above equilibrium (overvalued)
- Deviation exceeds threshold (|E| > 2σ)
- Phase indicates approaching reversal
- Expecting price to fall back to equilibrium

**HOLD Signal:**
- Either deviation or timing condition not met
- Price near equilibrium
- No clear reversal signal

### Confidence Levels

**High:**
- Volume confirms signal (above average)
- Signal quality is high (trend-aligned or ranging market)
- Cycle consistency > 70%

**Medium:**
- Moderate volume
- Mixed signal quality
- Moderate cycle consistency

**Low:**
- Below average volume
- Counter-trend signal or volatile market
- Low cycle consistency

## Advanced Usage

### Python API

```python
from oracle import initialize_exchange, run_oracle_analysis
from config import *

# Initialize
exchange = initialize_exchange()

# Run analysis
df, result, report = run_oracle_analysis(
    exchange=exchange,
    symbol='DOGE/USD',
    timeframe='1h',
    limit=500,
    vwap_period=100,
    fft_period=256,
    sigma_threshold=2.0,
    reversal_threshold_percent=0.10,
    enable_backtest=True,
    enable_trend_analysis=True,
    export_csv=True
)

# Access results
print(f"Signal: {result['Final_Signal']}")
print(f"Deviation: {result['Deviation_E']:.3f}")

# Access DataFrame
signals = df[df['Signal'] != 'HOLD']
print(f"Total signals: {len(signals)}")
```

### Multi-Timeframe Confluence

```python
from multi_timeframe import (
    analyze_multiple_timeframes,
    calculate_timeframe_confluence,
    align_timeframes
)

# Analyze multiple timeframes
results = analyze_multiple_timeframes(
    exchange, 'DOGE/USD', ['1h', '4h', '1d'],
    500, 100, 256, 2.0, 0.10
)

# Calculate confluence
confluence = calculate_timeframe_confluence(results)
print(f"Dominant Signal: {confluence['dominant_signal']}")
print(f"Agreement: {confluence['agreement']}")

# Weighted alignment
alignment = align_timeframes(results)
print(f"Weighted Signal: {alignment['dominant_signal']}")
```

### Custom Backtesting

```python
from backtest import (
    calculate_forward_returns,
    analyze_signal_performance,
    analyze_phase_accuracy
)

# Add forward returns
df = calculate_forward_returns(df, periods=[1, 5, 10, 20])

# Analyze performance
perf = analyze_signal_performance(df)
print(f"BUY signals: {perf['signals']['BUY']['count']}")
print(f"Win rate: {perf['signals']['BUY']['forward_returns']['5']['win_rate']:.1f}%")

# Phase accuracy
phase_acc = analyze_phase_accuracy(df)
print(f"Phase accuracy: {phase_acc['accuracy_rate']:.1f}%")
```

### Trend Analysis

```python
from trend_analysis import (
    detect_trend,
    detect_market_regime,
    enhance_signal_with_context
)

# Detect trend
df = detect_trend(df, short_period=20, long_period=50)

# Detect regime
df = detect_market_regime(df, volatility_period=20)

# Enhance signals
df = enhance_signal_with_context(df)

# Filter by regime
ranging_signals = df[df['Market_Regime'] == 'Ranging']
print(f"Signals in ranging market: {len(ranging_signals)}")
```

## Best Practices

### 1. Always Check Multiple Timeframes

```bash
python example_multi_timeframe.py
```

Don't trade on a single timeframe signal. Look for confluence.

### 2. Use Trend Analysis

```bash
python oracle.py --trend
```

Context matters. Signals work differently in trending vs ranging markets.

### 3. Review Backtest Results

```bash
python oracle.py --backtest
```

Understand historical performance before using signals.

### 4. Monitor Cycle Consistency

Low consistency (<50%) = unreliable phase predictions.

### 5. Respect Market Regime

- **Ranging**: Mean reversion signals are reliable
- **Trending**: Only take trend-aligned signals
- **Volatile**: Reduce position size or avoid trading

### 6. Volume Confirmation

High confidence signals have above-average volume.

### 7. Export and Analyze

```bash
python oracle.py --export
```

Review signals in spreadsheet software for deeper insights.

## Troubleshooting

### "Insufficient data for signal generation"

**Cause:** Not enough bars for VWAP or FFT calculation.

**Solution:** Increase `LIMIT` in config.py to at least `max(VWAP_PERIOD, FFT_PERIOD)`.

### "Could not fetch data"

**Cause:** Exchange API error or invalid symbol.

**Solution:**
- Check symbol format (Kraken: DOGE/USD, Coinbase: DOGE-USD)
- Verify internet connection
- Try different exchange

### "No signals generated"

**Cause:** Thresholds too strict or market conditions don't meet criteria.

**Solution:**
- Lower `SIGMA_THRESHOLD` (e.g., 1.5 instead of 2.0)
- Increase `REVERSAL_THRESHOLD_PERCENT` (e.g., 0.15 instead of 0.10)
- Check if market is ranging (signals work best in ranging markets)

### "Phase predictions inaccurate"

**Cause:** Market is trending or cycle is inconsistent.

**Solution:**
- Use `--trend` flag to check market regime
- Only trust signals in ranging markets
- Check cycle consistency score

## Examples

### Example 1: Daily Analysis Routine

```bash
# Morning: Check current state
python oracle.py

# Review performance
python oracle.py --backtest

# Check multiple timeframes
python example_multi_timeframe.py

# Export for records
python oracle.py --export
```

### Example 2: Signal Validation

```bash
# Get signal with full context
python oracle.py --trend

# Check if signal is:
# 1. In ranging market (best for mean reversion)
# 2. High confidence (volume confirmed)
# 3. High cycle consistency (>70%)

# Verify with multi-timeframe
python example_multi_timeframe.py

# Only trade if:
# - Strong confluence (>75%)
# - Weighted alignment agrees
# - Market regime is favorable
```

### Example 3: Performance Analysis

```bash
# Run backtest
python oracle.py --backtest --export

# Open CSV in spreadsheet
# Filter signals by:
# - Confidence level
# - Market regime
# - Cycle consistency

# Calculate custom metrics:
# - Risk/reward ratios
# - Maximum drawdown
# - Sharpe ratio
```

## Limitations

1. **Oracle, Not Trading System**: Provides signals only, no execution
2. **Mean Reversion Focus**: Works best in ranging markets
3. **Phase Assumptions**: Assumes cyclical behavior (not always true)
4. **No Risk Management**: No position sizing or stop losses
5. **Historical Analysis**: Past performance doesn't guarantee future results

## Support

For issues or questions:
1. Check this guide
2. Review README.md
3. Examine example scripts
4. Inspect CSV exports for data quality

## License

This is an analysis tool for educational purposes.
Not financial advice. Use at your own risk.
