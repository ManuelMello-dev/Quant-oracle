# Quant Oracle - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

## 1. Backend Setup (2 minutes)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start API server
cd backend
python api/server.py
```

Server runs at: [http://localhost:8000](http://localhost:8000)

API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

## 2. Web App Setup (2 minutes)

```bash
# Install dependencies
cd frontend/web
npm install

# Start development server
npm run dev
```

Web app runs at: [http://localhost:3000](http://localhost:3000)

## 3. Mobile App Setup (Optional, 3 minutes)

```bash
# Install dependencies
cd frontend/mobile
npm install

# Start Expo
npx expo start

# Scan QR code with Expo Go app
```

## Test It Out

### Test Backend API

```bash
# Test analysis endpoint
curl "http://localhost:8000/api/analyze/BTC-USD"

# Test backtest endpoint
curl "http://localhost:8000/api/backtest/BTC-USD"
```

### Test Web App

1. Open [http://localhost:3000](http://localhost:3000)
2. Enter "BTC/USD" in search
3. Click "Analyze"
4. View results!

### Test Mobile App

1. Install Expo Go on your phone
2. Scan QR code from terminal
3. App loads on your device
4. Test analysis features

## Common Issues

### Backend: "Module not found"
```bash
pip install -r requirements.txt --force-reinstall
```

### Web: "Cannot find module"
```bash
cd frontend/web
rm -rf node_modules .next
npm install
```

### Mobile: "Metro bundler error"
```bash
cd frontend/mobile
npx expo start --clear
```

### Data Source: "No data available"
- CoinGecko rate limit (50 calls/min)
- Try different symbol
- Wait 1 minute and retry

## Features to Try

### 1. Basic Analysis
- Symbol: BTC/USD
- View: Price, VWAP, Deviation, Signal
- Check: Volume confirmation

### 2. Backtest
- Run historical performance test
- View: Win rate, returns, signal distribution
- Timeframe: 1h, 4h, or 1d

### 3. Multi-Timeframe
- Compare: 1h, 4h, 1d signals
- Check: Confluence score
- Higher score = stronger signal

### 4. LLM Analysis (Premium)
- Enable AI toggle
- Get: Professional analysis
- Includes: Entry/exit/stop recommendations

## Configuration

### Backend (`backend/config.py`)
```python
SIGMA_THRESHOLD = 2.0        # Deviation threshold
VWAP_PERIOD = 100            # VWAP calculation period
FFT_PERIOD = 256             # FFT window size
DATA_SOURCE = 'auto'         # 'auto', 'cmc', 'coingecko', 'exchange'
```

### Web (`frontend/web/next.config.js`)
```javascript
env: {
  NEXT_PUBLIC_API_URL: 'http://localhost:8000',
  NEXT_PUBLIC_WS_URL: 'ws://localhost:8000',
}
```

### Mobile (`frontend/mobile/app.json`)
```json
"extra": {
  "EXPO_PUBLIC_API_URL": "http://localhost:8000"
}
```

## Next Steps

### For Development
1. Read `ARCHITECTURE.md` for system design
2. Check `USAGE.md` for detailed features
3. Review code comments for implementation details

### For Deployment
1. Read `DEPLOYMENT_SUMMARY.md` for overview
2. Follow `GOOGLE_PLAY_DEPLOYMENT.md` for mobile
3. Deploy backend to Railway/Render
4. Deploy web to Vercel

### For Customization
1. Modify `config.py` for different parameters
2. Update `tailwind.config.js` for styling
3. Add new indicators in `oracle.py`
4. Create custom visualizations in `visualize.py`

## Example Usage

### Python API
```python
from backend.api_wrapper import analyze_symbol

# Analyze symbol
df = analyze_symbol('BTC/USD', timeframe='1h', days=30)

# Get latest signal
latest = df.iloc[-1]
print(f"Signal: {latest['signal']}")
print(f"Deviation: {latest['deviation']:.2f}σ")
print(f"Price: ${latest['close']:.2f}")
```

### REST API
```bash
# Analyze
curl http://localhost:8000/api/analyze/BTC-USD

# Backtest
curl http://localhost:8000/api/backtest/BTC-USD?days=90

# Multi-timeframe
curl http://localhost:8000/api/multi-timeframe/BTC-USD

# Batch analyze
curl -X POST http://localhost:8000/api/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC/USD", "ETH/USD", "DOGE/USD"]}'
```

### JavaScript/TypeScript
```typescript
import api from './lib/api'

// Analyze
const data = await api.analyze('BTC/USD', '1h', 365, false)
console.log(data.metrics.signal)

// Backtest
const results = await api.backtest('BTC/USD', '1h', 365)
console.log(results.signal_performance)

// Multi-timeframe
const mtf = await api.multiTimeframe('BTC/USD', ['1h', '4h', '1d'])
console.log(mtf.confluence.score)
```

## Performance Tips

### Backend
- Use smaller `days` parameter for faster responses
- Enable caching for frequently accessed symbols
- Use `source='coingecko'` for fastest data fetch

### Web
- Enable SWR caching (already configured)
- Use `refreshInterval` for auto-updates
- Lazy load heavy components

### Mobile
- Implement pagination for watchlist
- Cache analysis results locally
- Use React.memo for expensive components

## Troubleshooting

### "Connection refused"
- Backend not running
- Check port 8000 is free
- Start backend: `python backend/api/server.py`

### "CORS error"
- Backend CORS not configured
- Check `allow_origins` in `server.py`
- Should be `["*"]` for development

### "Rate limit exceeded"
- CoinGecko: 50 calls/min
- Wait 1 minute
- Or use `source='cmc'` in config

### "No data available"
- Symbol not found
- Check symbol format: "BTC/USD" not "BTCUSD"
- Try popular symbols first

## Support

- **Documentation:** All `.md` files in repository
- **Issues:** GitHub Issues
- **Email:** support@quantoracle.app

## You're All Set! 🎉

The system is running and ready to use. Try analyzing some symbols and exploring the features!

**Recommended First Steps:**
1. Analyze BTC/USD
2. Run a backtest
3. Check multi-timeframe analysis
4. Add symbols to watchlist
5. Explore the code

Happy trading! 📈
