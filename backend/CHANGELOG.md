# Changelog

## Version 2.0 - Multi-Symbol Support (2026-01-04)

### 🎯 Major Features

#### Multi-Symbol Analysis
- **Analyze up to 3 symbols simultaneously**
- Configure default symbols in `config.py`
- Override via command line with `--symbols`
- Automatic comparison table for multiple symbols
- Signal summary across all analyzed symbols

### 📝 Changes

#### Configuration (`config.py`)
- **Changed**: `SYMBOL` → `SYMBOLS` (now accepts list)
- **Added**: Support for list of up to 3 symbols
- **Backward compatible**: Single symbol still works
- **Default**: `['DOGE/USD', 'BTC/USD', 'ETH/USD']`

#### Oracle (`oracle.py`)
- **Added**: `--symbols` command line flag
- **Added**: Multi-symbol comparison table
- **Added**: Signal summary across symbols
- **Enhanced**: `generate_signal()` now accepts symbol parameter
- **Enhanced**: Main execution loop processes multiple symbols
- **Enhanced**: Results aggregation and comparison

#### Documentation
- **Added**: `MULTI_SYMBOL_GUIDE.md` - Complete multi-symbol usage guide
- **Added**: `CHANGELOG.md` - This file
- **Updated**: Usage examples for multi-symbol scenarios

### 🚀 Usage

#### Default (3 symbols from config)
```bash
python oracle.py
```

#### Custom symbols via command line
```bash
python oracle.py --symbols "BTC/USD,ETH/USD"
```

#### Single symbol with backtest
```bash
python oracle.py --symbols "DOGE/USD" --backtest
```

#### Multiple symbols with trend analysis
```bash
python oracle.py --symbols "BTC/USD,ETH/USD,SOL/USD" --trend
```

### 📊 Output Format

#### Multi-Symbol Comparison Table
```
Symbol       Signal Price        Deviation  Confidence  
------------------------------------------------------------
DOGE/USD     ⚪ HOLD   $0.150054       +1.771σ Low         
BTC/USD      ⚪ HOLD   $91220.000000    +1.880σ Low         
ETH/USD      ⚪ HOLD   $3135.880000    +1.643σ Low         
```

#### Signal Summary
```
Signal Summary: 0 BUY, 0 SELL, 3 HOLD
✅ All symbols on HOLD - no active signals.
```

### ⚡ Performance

| Symbols | Basic | --backtest | --trend | --backtest --trend |
|---------|-------|------------|---------|-------------------|
| 1       | ~2s   | ~3s        | ~4s     | ~5s               |
| 2       | ~4s   | ~6s        | ~8s     | ~10s              |
| 3       | ~6s   | ~9s        | ~12s    | ~15s              |

### 🔧 Technical Details

#### Symbol Processing
- Sequential processing (not parallel)
- Each symbol gets full analysis pipeline
- Independent signal generation per symbol
- Aggregated results for comparison

#### Memory Usage
- ~150KB per symbol with all indicators
- 3 symbols = ~450KB total
- Negligible for modern systems

#### Limitations
- Maximum 3 symbols (enforced)
- Same timeframe for all symbols
- Same parameters (VWAP_PERIOD, FFT_PERIOD, etc.)
- Sequential processing (no parallelization)

### 🐛 Bug Fixes
- None (new feature release)

### 📚 Documentation Updates
- Added multi-symbol usage examples
- Created dedicated multi-symbol guide
- Updated README with new features
- Added performance benchmarks

### 🔮 Future Enhancements

Potential additions for future versions:
- Parallel processing for faster analysis
- Symbol-specific parameter tuning
- Cross-symbol correlation analysis
- Portfolio-level signals
- Automated watchlist management
- Real-time multi-symbol monitoring

---

## Version 1.0 - Enhanced Oracle (2026-01-04)

### Initial Release Features

#### Core Enhancements
- Division by zero protection
- Rolling signal generation (all historical bars)
- Backtesting framework with forward returns
- Multiple timeframe analysis
- Trend detection and market regime classification
- Enhanced phase interpretation
- ASCII visualizations

#### Modules
- `oracle.py` - Main oracle engine
- `backtest.py` - Performance analysis
- `multi_timeframe.py` - Cross-timeframe analysis
- `trend_analysis.py` - Trend and regime detection
- `visualize.py` - ASCII charts and dashboards
- `config.py` - Configuration with validation

#### Documentation
- `README.md` - Overview and features
- `USAGE.md` - Complete usage guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details

#### Command-Line Flags
- `--backtest` - Historical performance analysis
- `--trend` - Market regime detection
- `--export` - CSV export

#### Performance Metrics
- Forward returns at multiple horizons
- Win rate analysis
- Phase prediction accuracy
- Market condition analysis

---

## Migration Guide

### From Version 1.0 to 2.0

#### Configuration Changes

**Old (v1.0):**
```python
SYMBOL = 'DOGE/USD'
```

**New (v2.0):**
```python
SYMBOLS = ['DOGE/USD', 'BTC/USD', 'ETH/USD']
```

**Backward Compatibility:**
```python
# This still works
SYMBOLS = 'DOGE/USD'

# Or single-item list
SYMBOLS = ['DOGE/USD']
```

#### Command-Line Changes

**Old (v1.0):**
```bash
# Edit config.py to change symbol
python oracle.py
```

**New (v2.0):**
```bash
# Override via command line
python oracle.py --symbols "BTC/USD"

# Multiple symbols
python oracle.py --symbols "BTC/USD,ETH/USD"
```

#### Code Changes

If you have custom scripts using the oracle:

**Old:**
```python
from config import SYMBOL
oracle_result = generate_signal(df, SIGMA_THRESHOLD, REVERSAL_THRESHOLD_PERCENT)
```

**New:**
```python
from config import SYMBOLS
symbol = SYMBOLS[0] if isinstance(SYMBOLS, list) else SYMBOLS
oracle_result = generate_signal(df, SIGMA_THRESHOLD, REVERSAL_THRESHOLD_PERCENT, symbol)
```

### Breaking Changes

None - fully backward compatible.

### Deprecations

None - `SYMBOL` is still supported via automatic conversion.

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 2.0 | 2026-01-04 | Multi-symbol support |
| 1.0 | 2026-01-04 | Enhanced oracle with backtesting |
| 0.1 | 2026-01-04 | Original basic oracle |
