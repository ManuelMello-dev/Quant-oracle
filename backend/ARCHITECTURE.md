# Quant Oracle - Application Architecture

## Overview
Production-ready trading oracle with web and mobile interfaces, powered by local LLM for professional analysis.

## Architecture Layers

### 1. Backend (Python)
**Location:** `/backend/`

**Components:**
- `api/server.py` - FastAPI REST API server
- `api/websocket.py` - Real-time data streaming
- Core Python modules (oracle.py, data_sources.py, etc.)
- LLM analyzer (llm_analyzer.py)

**Endpoints:**
```
GET  /api/analyze/{symbol}          - Get current analysis
GET  /api/backtest/{symbol}         - Run backtest
GET  /api/multi-timeframe/{symbol}  - Multi-timeframe analysis
POST /api/analyze/batch             - Batch analysis (multiple symbols)
WS   /ws/live/{symbol}              - Real-time updates
```

### 2. Frontend - Web (React + Next.js)
**Location:** `/frontend/web/`

**Tech Stack:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- TailwindCSS
- Recharts (visualizations)
- SWR (data fetching)

**Pages:**
```
/                    - Dashboard (overview)
/analyze/[symbol]    - Detailed analysis
/backtest            - Backtesting interface
/watchlist           - Multi-symbol monitoring
/settings            - Configuration
```

### 3. Frontend - Mobile (React Native)
**Location:** `/frontend/mobile/`

**Tech Stack:**
- React Native 0.73+
- Expo (for easier deployment)
- TypeScript
- NativeWind (TailwindCSS for RN)
- React Navigation
- Victory Native (charts)

**Screens:**
```
Dashboard            - Overview with key metrics
Analysis             - Detailed symbol analysis
Watchlist            - Multi-symbol tracking
Alerts               - Push notifications
Settings             - Configuration
```

### 4. Shared Code
**Location:** `/frontend/shared/`

**Modules:**
- `types.ts` - TypeScript interfaces
- `api.ts` - API client
- `utils.ts` - Common utilities
- `constants.ts` - Shared constants

## Data Flow

```
┌─────────────────┐
│  Data Sources   │
│ CMC/CoinGecko   │
│   /Exchange     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python Core    │
│  Oracle Engine  │
│  + LLM Analyzer │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   REST + WS     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│  Web   │ │ Mobile │
│ Next.js│ │React RN│
└────────┘ └────────┘
```

## UI/UX Design Principles

### Visual Design
- **Dark Mode First:** Trading apps work best in dark mode
- **Color Coding:**
  - Green: BUY signals, positive returns
  - Red: SELL signals, negative returns
  - Yellow: HOLD signals, warnings
  - Blue: Information, neutral
- **Typography:** Monospace for numbers, Sans-serif for text
- **Spacing:** Generous padding for mobile touch targets

### Key Screens

#### 1. Dashboard
```
┌─────────────────────────────────────┐
│  Quant Oracle          [Settings]   │
├─────────────────────────────────────┤
│                                     │
│  BTC/USD                    $42,150 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Deviation: -2.3σ           🟢 BUY  │
│  Volume: 145%                       │
│  Confidence: 87%                    │
│                                     │
│  [View Details] [Add to Watchlist]  │
│                                     │
├─────────────────────────────────────┤
│  Watchlist                          │
│  • ETH/USD    +1.2σ    🟡 HOLD     │
│  • DOGE/USD   -3.2σ    🟢 BUY      │
│  • SOL/USD    +2.8σ    🔴 SELL     │
│                                     │
│  [+ Add Symbol]                     │
└─────────────────────────────────────┘
```

#### 2. Analysis Detail
```
┌─────────────────────────────────────┐
│  ← BTC/USD Analysis                 │
├─────────────────────────────────────┤
│  Price Chart (24h)                  │
│  ┌───────────────────────────────┐  │
│  │     /\      /\                │  │
│  │    /  \    /  \     /\        │  │
│  │   /    \  /    \   /  \       │  │
│  │  /      \/      \ /    \      │  │
│  └───────────────────────────────┘  │
│                                     │
│  Metrics                            │
│  • Price:        $42,150            │
│  • VWAP:         $43,200            │
│  • Deviation:    -2.3σ              │
│  • Volume:       145%               │
│  • Signal:       🟢 BUY             │
│                                     │
│  Professional Analysis              │
│  ┌───────────────────────────────┐  │
│  │ Price is 2.3σ below equilibrium│  │
│  │ indicating strong undervaluation│  │
│  │ Mean reversion likely...       │  │
│  │                                │  │
│  │ ✅ ENTRY: $42,150              │  │
│  │ 🎯 TARGET: $43,200             │  │
│  │ 🛑 STOP: $41,000               │  │
│  └───────────────────────────────┘  │
│                                     │
│  [Run Backtest] [Multi-Timeframe]  │
└─────────────────────────────────────┘
```

#### 3. Backtest Results
```
┌─────────────────────────────────────┐
│  ← Backtest: BTC/USD (365 days)     │
├─────────────────────────────────────┤
│  Performance                        │
│  • Win Rate:      71.4%             │
│  • Avg Return:    +3.2%             │
│  • Max Drawdown:  -8.5%             │
│  • Sharpe Ratio:  1.85              │
│                                     │
│  Equity Curve                       │
│  ┌───────────────────────────────┐  │
│  │                          /    │  │
│  │                     /---/     │  │
│  │              /-----/          │  │
│  │        /----/                 │  │
│  │  -----/                       │  │
│  └───────────────────────────────┘  │
│                                     │
│  Signal Distribution                │
│  • BUY:   12 signals (3.3%)         │
│  • SELL:  15 signals (4.1%)         │
│  • HOLD:  338 signals (92.6%)       │
│                                     │
│  [Export CSV] [Share]               │
└─────────────────────────────────────┘
```

## Mobile-Specific Features

### Push Notifications
- Signal alerts (BUY/SELL triggers)
- Price alerts (custom thresholds)
- Volume spikes
- Extreme deviations (>3σ)

### Offline Support
- Cache last analysis
- Queue requests when offline
- Sync when connection restored

### Gestures
- Swipe left/right: Navigate symbols
- Pull to refresh: Update data
- Long press: Add to watchlist
- Pinch to zoom: Chart interaction

## Google Play Store Requirements

### App Metadata
- **Package Name:** `com.quantoracle.app`
- **Version:** 1.0.0 (Build 1)
- **Min SDK:** 24 (Android 7.0)
- **Target SDK:** 34 (Android 14)

### Required Assets
- App icon (512x512, 192x192, 96x96, 72x72, 48x48)
- Feature graphic (1024x500)
- Screenshots (phone + tablet, 2-8 images)
- Privacy policy URL
- Content rating questionnaire

### Permissions
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

### Security
- ProGuard/R8 obfuscation
- SSL certificate pinning
- No hardcoded API keys
- Secure storage for user preferences

## Web Deployment

### Hosting Options
1. **Vercel** (Recommended for Next.js)
   - Zero-config deployment
   - Edge functions
   - Automatic HTTPS
   
2. **Netlify**
   - Similar to Vercel
   - Good for static sites
   
3. **Self-hosted**
   - Docker container
   - Nginx reverse proxy
   - Let's Encrypt SSL

### Domain Setup
- Primary: `quantoracle.app`
- API: `api.quantoracle.app`
- WebSocket: `ws.quantoracle.app`

## Backend Deployment

### Options
1. **Railway** (Recommended)
   - Python support
   - WebSocket support
   - Auto-scaling
   - $5/month starter
   
2. **Render**
   - Free tier available
   - Good Python support
   
3. **DigitalOcean App Platform**
   - $5/month
   - Full control

### Requirements
- Python 3.11+
- 512MB RAM minimum (1GB recommended)
- 1 CPU core
- 10GB storage

## Cost Analysis

### Infrastructure (Monthly)
- Backend hosting: $5-10 (Railway/Render)
- Web hosting: $0 (Vercel free tier)
- Domain: $1-2/month
- **Total: $6-12/month**

### Per-User Costs
- API calls: $0 (self-hosted)
- LLM inference: $0 (local model)
- Data sources: $0 (free APIs)
- **Total: $0/user**

### Profit Margins
- Free tier: 100% margin (rule-based)
- Basic ($4.99): 100% margin
- Premium ($9.99): 98.7% margin (LLM costs ~$0.13/user)

## Development Workflow

### Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api/server.py

# Web
cd frontend/web
npm install
npm run dev

# Mobile
cd frontend/mobile
npm install
npx expo start
```

### Testing
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
npm test

# E2E tests
npm run test:e2e
```

### Deployment
```bash
# Backend
git push railway main

# Web
git push vercel main

# Mobile
eas build --platform android
eas submit --platform android
```

## Security Considerations

### API Security
- Rate limiting (100 req/min per IP)
- CORS configuration
- Input validation
- SQL injection prevention (use ORMs)

### Data Privacy
- No user data collection (GDPR compliant)
- Anonymous usage analytics only
- No third-party trackers
- Clear privacy policy

### Mobile Security
- Certificate pinning
- Encrypted local storage
- Biometric authentication (optional)
- Secure API key storage

## Performance Targets

### Backend
- API response: <200ms (p95)
- WebSocket latency: <50ms
- Concurrent users: 1000+

### Web
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Lighthouse score: >90

### Mobile
- App launch: <2s
- Screen transitions: <300ms
- Memory usage: <100MB
- Battery impact: Minimal

## Monitoring & Analytics

### Backend Monitoring
- Uptime monitoring (UptimeRobot)
- Error tracking (Sentry)
- Performance metrics (custom)

### Frontend Analytics
- Page views (privacy-friendly)
- User flows
- Error tracking
- Performance metrics

### Business Metrics
- Daily/Monthly Active Users
- Conversion rate (free → paid)
- Churn rate
- Feature usage

## Next Steps

1. ✅ Design architecture
2. ⏳ Implement FastAPI backend
3. ⏳ Create Next.js web app
4. ⏳ Build React Native mobile app
5. ⏳ Integrate LLM analyzer
6. ⏳ Add Google Play Store assets
7. ⏳ Deploy and test
8. ⏳ Launch!
