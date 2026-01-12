# CoinGecko Integration Guide

The oracle now supports **CoinGecko** as a data source, providing free, reliable market data without requiring exchange API keys!

---

## 🎯 Why CoinGecko?

### **Benefits:**
- ✅ **No API keys needed** - Works immediately after install
- ✅ **Free tier** - 10,000 calls/month, 50 calls/minute
- ✅ **10,000+ coins** - More symbols than any single exchange
- ✅ **Aggregated data** - Prices from multiple exchanges
- ✅ **Reliable** - 99.9% uptime, well-maintained API
- ✅ **Global** - No geo-restrictions

### **Perfect For:**
- Quick testing and development
- Users without exchange accounts
- Multi-coin analysis
- Mobile/desktop apps
- Commercial products (with Pro tier)

---

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
pip install pycoingecko
```

### **2. Configure Data Source**

Edit `config.py`:

```python
# Set data source (default: 'coingecko')
DATA_SOURCE = 'coingecko'  # or 'exchange' or 'auto'
```

### **3. Run Oracle**

```bash
python oracle.py --symbols "DOGE/USD"
```

**That's it!** No API keys, no exchange setup needed.

---

## ⚙️ Configuration Options

### **Data Source Modes**

```python
# config.py

# Option 1: CoinGecko only (recommended for most users)
DATA_SOURCE = 'coingecko'

# Option 2: Exchange only (requires API keys)
DATA_SOURCE = 'exchange'

# Option 3: Auto-detect (uses exchange if keys available, else CoinGecko)
DATA_SOURCE = 'auto'
```

### **Supported Symbols**

Add symbols to `COINGECKO_SYMBOL_MAP` in `config.py`:

```python
COINGECKO_SYMBOL_MAP = {
    'DOGE/USD': 'dogecoin',
    'BTC/USD': 'bitcoin',
    'ETH/USD': 'ethereum',
    'PEPE/USD': 'pepe',
    'SOL/USD': 'solana',
    # Add more...
}
```

**Find CoinGecko IDs:** https://www.coingecko.com/en/coins/all

---

## 📊 Data Quality

### **What CoinGecko Provides:**

| Data | Quality | Notes |
|------|---------|-------|
| **Price** | ✅ Excellent | Aggregated from multiple exchanges |
| **Volume** | ✅ Excellent | Total volume across exchanges |
| **OHLC** | ⚠️ Approximated | Free tier doesn't provide true OHLC |
| **Timeframes** | ✅ Good | 1h, 4h, 1d, 1w supported |
| **History** | ✅ Good | Up to 365 days on free tier |

### **OHLC Approximation:**

CoinGecko free tier provides price points, not true OHLC candles. The oracle approximates:
- **Open**: Previous close
- **High/Low**: Close ± estimated volatility
- **Close**: Actual price from CoinGecko
- **Volume**: Actual volume from CoinGecko

**Impact:** Minimal for VWAP-based strategies. VWAP uses close price and volume, which are accurate.

---

## 🎪 Usage Examples

### **Basic Analysis**

```bash
# Single symbol
python oracle.py --symbols "DOGE/USD"

# Multiple symbols
python oracle.py --symbols "BTC/USD,ETH/USD,DOGE/USD"
```

### **With Backtest**

```bash
python oracle.py --symbols "DOGE/USD" --backtest
```

### **Full Analysis**

```bash
python oracle.py --symbols "DOGE/USD" --backtest --trend --export
```

### **Programmatic Usage**

```python
from data_sources import fetch_ohlcv_data

# Fetch DOGE data from CoinGecko
df = fetch_ohlcv_data(
    exchange=None,  # Not needed for CoinGecko
    symbol='DOGE/USD',
    timeframe='1h',
    limit=1000,
    source='coingecko'
)

print(df.head())
```

---

## 💰 Cost Analysis

### **Free Tier (Sufficient for Most Users)**

**Limits:**
- 10,000 API calls/month
- 50 calls/minute
- 365 days historical data

**Usage Calculation:**
```
1 oracle run = 2 API calls (prices + volumes)
10 runs/day × 30 days = 600 calls/month

Free tier supports: 5,000 runs/month
Perfect for personal use!
```

### **Pro Tier (For Commercial Apps)**

| Plan | Price | Calls/Month | Rate Limit |
|------|-------|-------------|------------|
| **Analyst** | $129/mo | 500,000 | 500/min |
| **Lite** | $499/mo | 3,000,000 | 1000/min |

**For 1,000 users × 10 runs/day:**
- Calls needed: 600,000/month
- **Analyst plan sufficient**
- Cost per user: $0.13/mo
- **99% profit margin** on $9.99/mo subscription

---

## 🔄 Comparison: CoinGecko vs Exchange

| Feature | CoinGecko | Exchange (Kraken) |
|---------|-----------|-------------------|
| **Setup** | None | API keys required |
| **Cost** | Free (10k calls/mo) | Free (public data) |
| **Symbols** | 10,000+ coins | Exchange-specific |
| **Data Quality** | Aggregated | Exchange-specific |
| **Rate Limits** | 50/min | Varies by exchange |
| **Reliability** | 99.9% uptime | Exchange dependent |
| **Geo-restrictions** | None | Some exchanges blocked |
| **OHLC Accuracy** | Approximated | Exact |
| **Best For** | Multi-coin, easy setup | Single exchange, exact data |

---

## 🎯 Recommended Setup

### **For Development/Testing:**
```python
DATA_SOURCE = 'coingecko'  # Fast, easy, no setup
```

### **For Production (Personal Use):**
```python
DATA_SOURCE = 'coingecko'  # Free tier sufficient
```

### **For Production (Commercial):**
```python
DATA_SOURCE = 'auto'  # Use exchange if user has keys, else CoinGecko
```

### **For High-Frequency Trading:**
```python
DATA_SOURCE = 'exchange'  # Need exact OHLC data
```

---

## 🐛 Troubleshooting

### **"Symbol not supported by CoinGecko"**

**Solution:** Add symbol to `COINGECKO_SYMBOL_MAP` in `config.py`

```python
COINGECKO_SYMBOL_MAP = {
    'YOUR/SYMBOL': 'coingecko-coin-id',
}
```

Find coin ID at: https://www.coingecko.com/en/coins/all

---

### **"Only got X bars (requested Y)"**

**Cause:** CoinGecko free tier has data limitations

**Solutions:**
1. Reduce `LIMIT` in config (e.g., 500 instead of 1000)
2. Use longer timeframe (e.g., '1d' instead of '1h')
3. Upgrade to CoinGecko Pro for more data

---

### **"Rate limit exceeded"**

**Cause:** Too many API calls (>50/min)

**Solutions:**
1. Add delays between oracle runs
2. Cache data locally
3. Upgrade to CoinGecko Pro (500/min)

---

### **Data seems delayed**

**Cause:** CoinGecko updates every few minutes

**Solution:** This is normal. CoinGecko is not real-time. For real-time data, use `DATA_SOURCE = 'exchange'`

---

## 📚 Additional Resources

**CoinGecko API Documentation:**
- https://www.coingecko.com/en/api/documentation

**pycoingecko Library:**
- https://github.com/man-c/pycoingecko

**Coin List (find IDs):**
- https://www.coingecko.com/en/coins/all

**API Status:**
- https://status.coingecko.com/

---

## 🎉 Summary

**CoinGecko integration provides:**
- ✅ Zero-setup data source
- ✅ Free tier for personal use
- ✅ 10,000+ supported coins
- ✅ Reliable, aggregated data
- ✅ Perfect for oracle-based strategies
- ✅ Commercial-ready with Pro tier

**Your oracle now works out-of-the-box with no API keys needed!** 🚀
