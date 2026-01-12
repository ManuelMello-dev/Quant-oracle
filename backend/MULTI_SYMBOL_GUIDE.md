# Multi-Symbol Oracle Guide

The oracle now supports analyzing up to 3 symbols simultaneously.

## Configuration

### Method 1: Edit config.py (Default)

```python
# config.py
SYMBOLS = ['DOGE/USD', 'BTC/USD', 'ETH/USD']
```

The oracle will analyze all symbols in the list (max 3).

### Method 2: Command Line (Override)

```bash
# Analyze specific symbols
python oracle.py --symbols "BTC/USD,ETH/USD"

# Single symbol
python oracle.py --symbols "DOGE/USD"

# Three symbols
python oracle.py --symbols "BTC/USD,ETH/USD,SOL/USD"
```

## Usage Examples

### Basic Multi-Symbol Analysis

```bash
python oracle.py
```

Analyzes all symbols configured in `config.py` (default: DOGE, BTC, ETH).

**Output:**
- Individual analysis for each symbol
- Multi-symbol comparison table
- Signal summary

### With Backtest (Single Symbol)

```bash
python oracle.py --symbols "BTC/USD" --backtest
```

Runs full backtest on BTC/USD only.

**Note**: Backtest is run per symbol, so analyzing 3 symbols with `--backtest` will take 3x longer.

### With Trend Analysis

```bash
python oracle.py --symbols "ETH/USD,BTC/USD" --trend
```

Adds market regime detection for each symbol.

### Export Multiple Symbols

```bash
python oracle.py --export
```

Creates separate CSV files:
- `oracle_signals_DOGE_USD_1h.csv`
- `oracle_signals_BTC_USD_1h.csv`
- `oracle_signals_ETH_USD_1h.csv`

### Full Analysis on Multiple Symbols

```bash
python oracle.py --symbols "BTC/USD,ETH/USD" --backtest --trend --export
```

⚠️ **Warning**: This will take significant time (2-3 minutes per symbol).

## Output Format

### Individual Symbol Analysis

Each symbol gets:
- VWAP and deviation calculation
- FFT phase analysis
- Signal generation
- Current oracle state

### Multi-Symbol Comparison Table

```
Symbol       Signal Price        Deviation  Confidence  
------------------------------------------------------------
DOGE/USD     ⚪ HOLD   $0.150054       +1.771σ Low         
BTC/USD      🟢 BUY    $91220.000000   -2.345σ High        
ETH/USD      ⚪ HOLD   $3135.880000    +1.643σ Low         
```

### Signal Summary

```
Signal Summary: 1 BUY, 0 SELL, 2 HOLD

⚠️  Active signals detected! Review individual analysis above.
```

## Symbol Format

**Kraken (default fallback):**
- `DOGE/USD`
- `BTC/USD`
- `ETH/USD`
- `SOL/USD`
- `XRP/USD`

**Coinbase (with credentials):**
- `DOGE-USD`
- `BTC-USD`
- `ETH-USD`

## Limitations

1. **Maximum 3 symbols** - More than 3 will be truncated
2. **Same timeframe** - All symbols use the same TIMEFRAME from config
3. **Same parameters** - All symbols use same VWAP_PERIOD, FFT_PERIOD, etc.
4. **Sequential processing** - Symbols are analyzed one at a time (not parallel)

## Performance Considerations

### Analysis Time (per symbol)

| Mode | Time per Symbol | 3 Symbols Total |
|------|----------------|-----------------|
| Basic | ~2 seconds | ~6 seconds |
| --backtest | ~3 seconds | ~9 seconds |
| --trend | ~4 seconds | ~12 seconds |
| --backtest --trend | ~5 seconds | ~15 seconds |

### Memory Usage

- ~150KB per symbol (with all indicators)
- 3 symbols = ~450KB total
- Negligible for modern systems

## Use Cases

### Portfolio Monitoring

```bash
# Monitor your crypto portfolio
python oracle.py --symbols "BTC/USD,ETH/USD,SOL/USD"
```

Check all holdings at once for signals.

### Correlation Analysis

```bash
# Compare major cryptos
python oracle.py --symbols "BTC/USD,ETH/USD,DOGE/USD" --trend
```

See if signals align across correlated assets.

### Diversification

```bash
# Different asset classes
python oracle.py --symbols "BTC/USD,ETH/USD,XRP/USD"
```

Look for uncorrelated opportunities.

### Quick Scan

```bash
# Rapid check of top 3 holdings
python oracle.py
```

Uses default config symbols for fast analysis.

## Advanced: Programmatic Access

```python
from oracle import initialize_exchange, run_oracle_analysis
from config import *

exchange = initialize_exchange()
symbols = ['BTC/USD', 'ETH/USD', 'DOGE/USD']

results = []
for symbol in symbols:
    df, result, report = run_oracle_analysis(
        exchange, symbol, TIMEFRAME, LIMIT,
        VWAP_PERIOD, FFT_PERIOD, SIGMA_THRESHOLD,
        REVERSAL_THRESHOLD_PERCENT
    )
    results.append(result)

# Find active signals
active = [r for r in results if r['Final_Signal'] != 'HOLD']
print(f"Active signals: {len(active)}")
```

## Tips

1. **Start with 1 symbol** when using `--backtest` to save time
2. **Use config.py** for your regular watchlist
3. **Use --symbols** for ad-hoc analysis
4. **Check correlation** - if BTC signals, check ETH too
5. **Export regularly** to track signal history across symbols

## Troubleshooting

### "Could not fetch data for SYMBOL"

- Check symbol format (Kraken uses `/`, Coinbase uses `-`)
- Verify symbol exists on the exchange
- Try a different symbol

### "Analysis taking too long"

- Reduce LIMIT in config.py (e.g., 500 instead of 1000)
- Analyze fewer symbols
- Remove `--backtest` flag

### "Different results for same symbol"

- Market data updates every hour
- Prices change between runs
- This is expected behavior

## Examples

### Example 1: Morning Routine

```bash
# Quick check of portfolio
python oracle.py

# If signals detected, investigate
python oracle.py --symbols "BTC/USD" --backtest --trend
```

### Example 2: Deep Dive

```bash
# Analyze one symbol thoroughly
python oracle.py --symbols "ETH/USD" --backtest --trend --export

# Review CSV for historical patterns
# Check backtest performance
# Verify market regime
```

### Example 3: Comparison

```bash
# Compare BTC vs ETH
python oracle.py --symbols "BTC/USD,ETH/USD"

# Look for:
# - Which is more overvalued/undervalued?
# - Which has better phase timing?
# - Which has higher confidence?
```

## Best Practices

1. **Regular monitoring**: Run daily with default symbols
2. **Signal confirmation**: If one symbol signals, check correlated assets
3. **Volume matters**: Prefer signals with high confidence (volume confirmed)
4. **Phase timing**: Both deviation AND timing must align
5. **Backtest first**: Before trading a new symbol, run `--backtest` to understand performance

## Future Enhancements

Potential additions:
- Parallel processing for faster multi-symbol analysis
- Cross-symbol correlation analysis
- Portfolio-level signals (e.g., "2 of 3 symbols signal SELL")
- Symbol-specific parameter tuning
- Automated watchlist management
