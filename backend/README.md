# Quant Oracle Trading System

A quantitative trading oracle that combines VWAP (Volume Weighted Average Price), statistical deviation analysis, FFT (Fast Fourier Transform) phase detection, trend analysis, and market regime detection to generate trading signals.

## Features

### Core Analysis
- **Equilibrium Detection**: Uses VWAP to establish price equilibrium (Z')
- **Deviation Measurement**: Calculates standardized deviation (E) from equilibrium with zero-division protection
- **Phase Analysis**: FFT-based cycle detection to identify reversal timing
- **Rolling Signal Generation**: Generates signals for all historical bars, not just the latest

### Advanced Features
- **Backtesting Framework**: Analyzes historical signal performance with forward returns
- **Multiple Timeframe Analysis**: Confluence detection across different timeframes
- **Trend Detection**: Multi-method trend identification (MA, Linear Regression, Directional Movement)
- **Market Regime Detection**: Classifies markets as Trending, Ranging, or Volatile
- **Phase Context Interpretation**: Adjusts signal quality based on market conditions
- **Cycle Consistency Analysis**: Measures reliability of phase predictions
- **ASCII Visualizations**: Terminal-based charts and dashboards

### Data Sources
- **CoinGecko**: Free, 10,000+ coins, no API keys needed (default)
- **Coinbase**: With API credentials (optional)
- **Kraken**: Public data fallback (optional)
- **Auto-detect**: Uses best available source

## Installation

```bash
pip install -r requirements.txt
```

**That's it!** The oracle works immediately with CoinGecko (no API keys needed).

## Configuration

### **Data Source (Choose One)**

```python
# config.py

# Option 1: CoinGecko (recommended - no API keys needed)
DATA_SOURCE = 'coingecko'

# Option 2: Exchange (requires API keys)
DATA_SOURCE = 'exchange'

# Option 3: Auto-detect (uses exchange if keys available, else CoinGecko)
DATA_SOURCE = 'auto'
```

### **Exchange API Keys (Optional)**

Only needed if using `DATA_SOURCE = 'exchange'`:

```bash
export COINBASE_API_KEY='your_key'
export COINBASE_SECRET='your_secret'
```

### Parameters

- `SYMBOL`: Trading pair (e.g., 'DOGE/USD', 'BTC/USD')
- `TIMEFRAME`: Candle interval ('1h', '4h', '1d')
- `LIMIT`: Number of historical bars to fetch (500)
- `VWAP_PERIOD`: Rolling window for VWAP calculation (100)
- `FFT_PERIOD`: Window for FFT analysis, should be power of 2 (256)
- `SIGMA_THRESHOLD`: Deviation threshold for signal generation (2.0)
- `REVERSAL_THRESHOLD_PERCENT`: Phase proximity threshold (0.10)

## Usage

### Basic Usage

```bash
python oracle.py
```

### With Backtesting

```bash
python oracle.py --backtest
```

Analyzes historical signal performance including:
- Forward returns at multiple horizons (1, 3, 5, 10, 24 bars)
- Win rates for BUY and SELL signals
- Phase prediction accuracy
- Market condition analysis

### With Trend Analysis

```bash
python oracle.py --trend
```

Adds market regime detection and trend context:
- Trend direction (Uptrend/Downtrend)
- Market regime (Trending/Ranging/Volatile)
- Signal quality adjustment based on context
- Cycle consistency scoring

### Export Signals to CSV

```bash
python oracle.py --export
```

Exports all signals and indicators to CSV for external analysis.

### Combined Analysis

```bash
python oracle.py --backtest --trend --export
```

### Multiple Timeframe Analysis

```python
from multi_timeframe import analyze_multiple_timeframes, calculate_timeframe_confluence, print_multi_timeframe_summary
from oracle import initialize_exchange
from config import *

exchange = initialize_exchange()
timeframes = ['1h', '4h', '1d']

results = analyze_multiple_timeframes(
    exchange, SYMBOL, timeframes, LIMIT,
    VWAP_PERIOD, FFT_PERIOD, SIGMA_THRESHOLD, REVERSAL_THRESHOLD_PERCENT
)

confluence = calculate_timeframe_confluence(results)
print_multi_timeframe_summary(SYMBOL, results, confluence)
```

## Signal Logic

The oracle generates signals based on multiple conditions:

### Primary Conditions

1. **Deviation Signal**: `|E| > SIGMA_THRESHOLD`
   - E < 0: Price below equilibrium (undervalued) → BUY signal
   - E > 0: Price above equilibrium (overvalued) → SELL signal

2. **Timing Signal**: `T_reversal < Dominant_Period × REVERSAL_THRESHOLD_PERCENT`
   - Indicates approaching cycle reversal

### Context Enhancement (with --trend)

3. **Market Regime**:
   - **Ranging**: Mean reversion signals are more reliable
   - **Trending**: Signals aligned with trend are preferred
   - **Volatile**: All signals receive lower confidence

4. **Cycle Consistency**:
   - High consistency (>70%) upgrades signal confidence
   - Low consistency indicates unreliable phase predictions

## Output

### Basic Output

```
Symbol: DOGE/USD
Timestamp: 2024-01-04 18:00:00
Current_Price: 0.152210
Equilibrium_Z_prime: 0.135557
Deviation_E: 2.223275
Dominant_Period: 256.00 bars
Phase_Deg: 27.35°
T_reversal: 236.55 bars
Final_Signal: HOLD/BUY/SELL
Direction: Long/Short/N/A
Confidence: High/Medium/Low
```

### Backtest Output

```
SIGNAL PERFORMANCE SUMMARY
Total Bars Analyzed: 500
Valid Signal Bars: 244

BUY SIGNALS:
  Count: 15 (3.00%)
  Avg Deviation (E): -2.456
  Forward Returns:
    1 bars: Mean=+0.45%, Median=+0.32%, WinRate=60.0%
    5 bars: Mean=+1.23%, Median=+0.98%, WinRate=66.7%

PHASE PREDICTION ACCURACY
Total Predictions: 15
Accurate: 10 (66.7%)
Avg Timing Error: 3.2 bars
```

### Visual Dashboard

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         QUANT ORACLE DASHBOARD                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Symbol: DOGE/USD          Timeframe: 1h        Signal: 🟢 BUY               ║
║ Price: $0.152210          Direction: Long                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
...
```

## Architecture

### Core Modules

- **oracle.py**: Main analysis engine with VWAP, FFT, and signal generation
- **config.py**: Configuration and validation
- **backtest.py**: Performance analysis and metrics
- **multi_timeframe.py**: Cross-timeframe confluence detection
- **trend_analysis.py**: Trend detection and market regime classification
- **visualize.py**: ASCII charts and dashboards

### Analysis Pipeline

1. **Data Acquisition**: Fetch OHLCV via CCXT
2. **Indicator Calculation**: VWAP, deviation, FFT phase (rolling)
3. **Signal Generation**: Apply thresholds to all bars
4. **Context Enhancement**: Add trend and regime analysis (optional)
5. **Backtesting**: Analyze historical performance (optional)
6. **Visualization**: Generate charts and dashboards

## Key Improvements

### Robustness
- ✅ Division by zero protection in VWAP and deviation calculations
- ✅ NaN handling throughout the pipeline
- ✅ Configuration validation before execution
- ✅ Graceful fallback to public exchange data

### Analysis Depth
- ✅ Rolling signal generation for all historical bars
- ✅ Forward return analysis at multiple horizons
- ✅ Phase prediction accuracy measurement
- ✅ Market regime classification
- ✅ Trend-aware signal quality adjustment

### Usability
- ✅ Command-line flags for optional features
- ✅ CSV export for external analysis
- ✅ ASCII visualizations for terminal use
- ✅ Comprehensive backtest reports
- ✅ Multi-timeframe confluence detection

## Limitations

- Oracle provides signals only; does not execute trades
- Requires sufficient historical data (LIMIT ≥ max(VWAP_PERIOD, FFT_PERIOD))
- FFT assumes cyclical price behavior (works best in ranging markets)
- Phase interpretation is probabilistic, not deterministic
- No position sizing or risk management included
- Backtesting uses forward returns, not simulated trades

## Best Practices

1. **Use Multiple Timeframes**: Check confluence across 3+ timeframes
2. **Enable Trend Analysis**: Context improves signal quality
3. **Review Backtest Results**: Understand historical performance before use
4. **Check Market Regime**: Signals work differently in trending vs ranging markets
5. **Monitor Cycle Consistency**: Low consistency = unreliable phase predictions
6. **Validate with Volume**: High volume confirmation increases reliability

## Example Workflow

```bash
# 1. Basic analysis
python oracle.py

# 2. Full analysis with all features
python oracle.py --backtest --trend --export

# 3. Review exported CSV
# oracle_signals_DOGE_USD_1h.csv

# 4. Multi-timeframe analysis (in Python)
python -c "
from multi_timeframe import *
from oracle import initialize_exchange
from config import *

exchange = initialize_exchange()
results = analyze_multiple_timeframes(
    exchange, SYMBOL, ['1h', '4h', '1d'], LIMIT,
    VWAP_PERIOD, FFT_PERIOD, SIGMA_THRESHOLD, REVERSAL_THRESHOLD_PERCENT
)
confluence = calculate_timeframe_confluence(results)
print_multi_timeframe_summary(SYMBOL, results, confluence)
"
```

## Contributing

This is an oracle system for analysis purposes. It does not execute trades.
All enhancements should focus on improving signal quality and analysis depth.
