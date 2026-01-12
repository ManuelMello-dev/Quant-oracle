# ✅ Quant Oracle - Servers Running!

## 🌐 Access Your Application

### Web Application (Frontend)
**Click here to open:** [https://3000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev](https://3000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev)

**What you'll see:**
- Dashboard with symbol search
- Popular symbols (BTC/USD, ETH/USD, DOGE/USD, etc.)
- Feature cards
- Watchlist preview

### Backend API
**API Endpoint:** [https://8000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev](https://8000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev)

**API Documentation:** [https://8000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev/docs](https://8000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev/docs)

---

## 🧪 Test the Application

### 1. Open the Web App
Click the web application link above

### 2. Analyze a Symbol
1. Type "BTC/USD" in the search box
2. Click "Analyze" button
3. Wait 5-10 seconds for data to load
4. View the analysis results:
   - Signal (BUY/SELL/HOLD)
   - Price and VWAP
   - Deviation (σ)
   - Volume ratio
   - Trend and regime

### 3. Try Other Symbols
- ETH/USD
- DOGE/USD
- SOL/USD
- ADA/USD
- XRP/USD

### 4. Check Watchlist
- Click "View Watchlist" button
- See multiple symbols at once

---

## 📊 Server Status

### Backend API
- **Status:** ✅ Running
- **Port:** 8000
- **Process ID:** Check with `ps aux | grep "python api/server"`
- **Logs:** `/tmp/backend.log`

### Web Application
- **Status:** ✅ Running
- **Port:** 3000
- **Process ID:** Check with `ps aux | grep "next dev"`
- **Logs:** `/tmp/web.log`

---

## 🔄 Restart Servers

If you need to restart the servers:

```bash
./START_SERVERS.sh
```

Or manually:

```bash
# Stop servers
pkill -f "python api/server.py"
pkill -f "next dev"

# Start backend
cd /workspaces/workspaces/backend
python api/server.py > /tmp/backend.log 2>&1 &

# Start web
cd /workspaces/workspaces/frontend/web
npm run dev > /tmp/web.log 2>&1 &
```

---

## 📝 View Logs

### Backend Logs
```bash
tail -f /tmp/backend.log
```

### Web Logs
```bash
tail -f /tmp/web.log
```

---

## 🐛 Troubleshooting

### Web App Shows "Environment Not Found"
- Servers may have stopped
- Run `./START_SERVERS.sh` to restart
- Wait 30 seconds for servers to be ready

### Analysis Takes Long Time
- First request fetches data from CoinGecko
- Subsequent requests are faster
- CoinGecko has rate limit (50 calls/min)

### "No Data Available" Error
- Symbol might not be supported
- Try popular symbols first (BTC/USD, ETH/USD)
- Check backend logs for errors

### CORS Errors
- Backend CORS is configured for all origins
- Should not occur, but if it does, check backend logs

---

## 🎯 What to Try

### Basic Features
1. **Symbol Search** - Enter any crypto pair
2. **Analysis** - Get full metrics and signals
3. **Watchlist** - Monitor multiple symbols
4. **Backtest** - Run historical performance tests

### Advanced Features
1. **Multi-Timeframe** - Compare 1h, 4h, 1d signals
2. **AI Analysis** - Enable LLM toggle (Premium)
3. **Real-Time Updates** - WebSocket connection
4. **Export Data** - Download CSV files

---

## 📚 Documentation

- **QUICK_START.md** - Setup guide
- **USAGE.md** - Feature documentation
- **ARCHITECTURE.md** - System design
- **WEB_FIX_SUMMARY.md** - Recent fixes
- **PROJECT_COMPLETE.md** - Full project summary

---

## 🎉 You're All Set!

Both servers are running and ready to use. Open the web application link above and start analyzing crypto markets!

**Web App:** [https://3000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev](https://3000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev)

**API Docs:** [https://8000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev/docs](https://8000--019b8a1e-0ff9-7575-87e2-841a33eea170.us-east-1-01.gitpod.dev/docs)

---

**Happy Trading!** 📈🚀
