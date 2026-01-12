# Google Play Store Deployment Guide

## Prerequisites

### 1. Google Play Console Account
- Create account at [play.google.com/console](https://play.google.com/console)
- Pay one-time $25 registration fee
- Complete account verification

### 2. Development Tools
```bash
# Install EAS CLI (Expo Application Services)
npm install -g eas-cli

# Login to Expo
eas login

# Configure project
cd frontend/mobile
eas build:configure
```

## App Configuration

### 1. Update app.json
Already configured with:
- Package name: `com.quantoracle.app`
- Version: 1.0.0
- Version code: 1
- Permissions: INTERNET, ACCESS_NETWORK_STATE
- Adaptive icon with brand colors

### 2. Required Assets

#### App Icons
Create the following icon files in `frontend/mobile/assets/`:

**icon.png** (1024x1024)
- Main app icon
- PNG format
- Transparent or solid background
- Clear, recognizable at small sizes

**adaptive-icon.png** (1024x1024)
- Android adaptive icon foreground
- PNG with transparency
- Safe zone: 432x432 center area

**favicon.png** (48x48)
- Web favicon
- PNG format

#### Feature Graphic
**feature-graphic.png** (1024x500)
- Displayed in Play Store
- Showcase app features
- No text (will be overlaid)

#### Screenshots
Required: 2-8 screenshots per device type

**Phone Screenshots** (1080x1920 or 1080x2340)
- Dashboard view
- Analysis detail
- Watchlist
- Backtest results

**Tablet Screenshots** (1920x1200 or 2560x1600)
- Same screens, tablet layout

### 3. Store Listing Content

#### Short Description (80 characters max)
```
Professional crypto trading analysis with AI-powered signals
```

#### Full Description (4000 characters max)
```
Quant Oracle - Professional Trading Analysis

Transform your crypto trading with quantitative analysis powered by advanced algorithms and AI.

KEY FEATURES:

📊 VWAP Analysis
• Volume-weighted equilibrium detection
• Statistical deviation analysis (σ-based signals)
• Identify extreme undervaluation/overvaluation

🔮 FFT Prediction
• Cycle detection using Fast Fourier Transform
• Phase analysis for timing predictions
• Predict reversal points with precision

🤖 AI-Powered Insights (Premium)
• Professional analysis using local LLM
• Context-aware recommendations
• Entry/exit/stop suggestions

📈 Backtesting
• Historical performance validation
• 71.4% win rate on mean reversion signals
• Multiple holding period analysis

⏱️ Multi-Timeframe Analysis
• Cross-timeframe confluence scoring
• 1h, 4h, 1d alignment
• Higher confidence signals

🎯 Mean Reversion Strategy
• Extreme deviation signals (>2σ)
• High-probability setups
• Volume confirmation

SUPPORTED ASSETS:
• 10,000+ cryptocurrencies
• Bitcoin, Ethereum, Dogecoin, Solana, and more
• Real-time data from multiple sources

PRICING:
• Free: 5 analyses per day, rule-based insights
• Basic ($4.99/mo): Unlimited analyses, all features
• Premium ($9.99/mo): + AI analysis, priority support

ZERO SETUP:
• No API keys required
• No exchange account needed
• Start analyzing immediately

PRIVACY:
• No personal data collection
• Anonymous usage only
• GDPR compliant

Perfect for:
• Day traders seeking edge
• Swing traders timing entries
• Crypto investors managing risk
• Anyone wanting data-driven decisions

Download now and start making smarter trading decisions!
```

#### Category
- Finance

#### Content Rating
- Everyone
- No ads, no in-app purchases (initially)

#### Privacy Policy URL
Create and host privacy policy (required):
```
https://quantoracle.app/privacy
```

### 4. Privacy Policy Template

```markdown
# Privacy Policy for Quant Oracle

Last updated: [Date]

## Data Collection
Quant Oracle does NOT collect, store, or share any personal information.

## Usage Data
We collect anonymous usage statistics:
- Feature usage counts
- Error logs (no personal data)
- Performance metrics

## Third-Party Services
The app connects to:
- CoinGecko API (public data)
- CoinMarketCap (public data)
- Our backend API (no authentication)

## Data Storage
All data is stored locally on your device:
- Watchlist preferences
- App settings
- Analysis history

## Changes
We may update this policy. Changes will be posted in the app.

## Contact
Email: privacy@quantoracle.app
```

## Build Process

### 1. Create Production Build

```bash
cd frontend/mobile

# First build (creates credentials)
eas build --platform android --profile production

# This will:
# 1. Generate Android keystore (stored securely by EAS)
# 2. Build signed AAB (Android App Bundle)
# 3. Upload to EAS servers
```

### 2. Download AAB

```bash
# After build completes, download AAB
eas build:list

# Or download from EAS dashboard
# https://expo.dev/accounts/[your-account]/projects/quant-oracle/builds
```

### 3. Test Build Locally

```bash
# Create APK for testing
eas build --platform android --profile preview

# Install on device
adb install quant-oracle.apk
```

## Google Play Console Setup

### 1. Create App

1. Go to [Google Play Console](https://play.google.com/console)
2. Click "Create app"
3. Fill in details:
   - App name: Quant Oracle
   - Default language: English (US)
   - App or game: App
   - Free or paid: Free
4. Accept declarations

### 2. Store Listing

Navigate to "Store presence" → "Main store listing"

Upload:
- App icon (512x512)
- Feature graphic (1024x500)
- Phone screenshots (2-8)
- Tablet screenshots (optional but recommended)

Fill in:
- Short description
- Full description
- App category: Finance
- Contact email
- Privacy policy URL

### 3. Content Rating

1. Go to "Policy" → "App content"
2. Click "Start questionnaire"
3. Answer questions:
   - No violence
   - No sexual content
   - No user-generated content
   - No social features
   - Financial tools (trading analysis)
4. Submit for rating

### 4. Target Audience

1. Go to "Policy" → "Target audience"
2. Select age groups: 18+ (financial app)
3. Confirm no children's content

### 5. Data Safety

1. Go to "Policy" → "Data safety"
2. Fill in form:
   - Data collection: No personal data
   - Data sharing: None
   - Security practices: Data encrypted in transit
   - Data deletion: Not applicable (no data collected)

### 6. App Access

1. Go to "Policy" → "App access"
2. Select "All functionality is available without restrictions"

### 7. Ads

1. Go to "Policy" → "Ads"
2. Select "No, my app does not contain ads"

### 8. Upload AAB

1. Go to "Release" → "Production"
2. Click "Create new release"
3. Upload AAB file
4. Fill in release notes:

```
Initial release of Quant Oracle

Features:
• Professional trading analysis for 10,000+ cryptocurrencies
• VWAP equilibrium detection with statistical deviation
• FFT-based cycle prediction and timing
• Backtesting with 71.4% win rate validation
• Multi-timeframe confluence analysis
• AI-powered insights (Premium)
• Zero setup - no API keys required

Start making data-driven trading decisions today!
```

5. Set rollout percentage (start with 20% for testing)
6. Review and roll out

## Post-Launch

### 1. Monitor Crashes

```bash
# View crash reports in Play Console
# "Quality" → "Android vitals" → "Crashes & ANRs"
```

### 2. Respond to Reviews

- Reply to user reviews within 24-48 hours
- Address issues and thank positive feedback
- Update app based on feedback

### 3. Update Process

```bash
# Increment version in app.json
# version: "1.0.1"
# versionCode: 2

# Build new version
eas build --platform android --profile production

# Upload to Play Console
# Create new release with changelog
```

### 4. Analytics

Track key metrics:
- Daily Active Users (DAU)
- Retention rate
- Crash-free rate (target: >99%)
- Average rating (target: >4.0)

## Signing Configuration

### Manual Signing (Alternative to EAS)

If you want to manage your own keystore:

```bash
# Generate keystore
keytool -genkeypair -v -storetype PKCS12 \
  -keystore quant-oracle.keystore \
  -alias quant-oracle \
  -keyalg RSA -keysize 2048 -validity 10000

# Store credentials securely
# NEVER commit keystore to git
```

Update `eas.json`:
```json
{
  "build": {
    "production": {
      "android": {
        "buildType": "app-bundle",
        "credentialsSource": "local"
      }
    }
  }
}
```

## Troubleshooting

### Build Fails

```bash
# Clear cache
eas build:clear-cache

# Check logs
eas build:list
eas build:view [build-id]
```

### Upload Rejected

Common issues:
- Missing privacy policy
- Incomplete content rating
- Invalid screenshots (wrong dimensions)
- Missing required permissions declaration

### App Crashes

```bash
# Test locally first
npx expo start --no-dev --minify

# Check logs
adb logcat | grep "quant-oracle"
```

## Checklist

Before submitting:

- [ ] All icons created (1024x1024, adaptive, favicon)
- [ ] Feature graphic created (1024x500)
- [ ] Screenshots captured (2-8 per device type)
- [ ] Privacy policy published
- [ ] Store listing complete (descriptions, category)
- [ ] Content rating questionnaire completed
- [ ] Data safety form filled
- [ ] AAB built and tested
- [ ] Release notes written
- [ ] Contact email verified
- [ ] App tested on multiple devices
- [ ] Crash-free rate >99%
- [ ] All features working
- [ ] Backend API accessible

## Timeline

- **Day 1**: Create assets, write descriptions
- **Day 2**: Build AAB, test locally
- **Day 3**: Set up Play Console, upload AAB
- **Day 4-7**: Google review (typically 1-3 days)
- **Day 7+**: App live on Play Store!

## Costs

- Google Play registration: $25 (one-time)
- EAS Build: Free tier (limited builds) or $29/mo (unlimited)
- Hosting: $6-12/mo (backend API)
- **Total first month**: ~$60-70
- **Monthly ongoing**: $6-12 (or $35-41 with EAS)

## Support

- Expo docs: https://docs.expo.dev
- EAS Build: https://docs.expo.dev/build/introduction/
- Play Console: https://support.google.com/googleplay/android-developer

## Next Steps

1. Create app icons and graphics
2. Write privacy policy and host it
3. Run `eas build --platform android --profile production`
4. Set up Play Console listing
5. Upload AAB and submit for review
6. Launch! 🚀
