# Asset Creation Guide for Quant Oracle

## Required Assets Checklist

### App Icons

#### 1. icon.png (1024x1024)
**Purpose:** Main app icon displayed on home screen

**Design Guidelines:**
- Simple, recognizable design
- Works at small sizes (48x48)
- Avoid text (hard to read when small)
- Use brand colors: #3b82f6 (blue), #0a0e27 (dark)

**Suggested Design:**
```
- Dark blue gradient background (#0a0e27 to #060918)
- White/light blue oracle symbol or "Q" letter
- Subtle glow effect
- Minimalist, modern style
```

**Tools:**
- Figma (free): https://figma.com
- Canva (free): https://canva.com
- Adobe Illustrator
- Inkscape (free)

#### 2. adaptive-icon.png (1024x1024)
**Purpose:** Android adaptive icon (foreground layer)

**Design Guidelines:**
- Transparent background
- Safe zone: 432x432 center (will always be visible)
- Outer areas may be cropped by different launchers
- Same design as main icon but with transparency

**Background Color:** #0a0e27 (set in app.json)

#### 3. favicon.png (48x48)
**Purpose:** Web version icon

**Design Guidelines:**
- Simplified version of main icon
- Clear at tiny size
- PNG format

### Store Graphics

#### 4. feature-graphic.png (1024x500)
**Purpose:** Featured in Play Store listing

**Design Guidelines:**
- Landscape orientation
- Showcase app features visually
- No text (Play Store adds title)
- High quality, professional look

**Suggested Content:**
```
Left side: App screenshot or mockup
Right side: Key features with icons
- 📊 VWAP Analysis
- 🔮 FFT Prediction
- 🤖 AI Insights
- 📈 Backtesting

Background: Dark gradient matching app theme
```

#### 5. Screenshots

**Phone Screenshots (1080x1920 or 1080x2340)**
Minimum 2, maximum 8 required

**Required Screenshots:**
1. **Dashboard/Home**
   - Show symbol search
   - Popular symbols
   - Feature cards
   - Clean, professional

2. **Analysis Detail**
   - Large signal indicator (BUY/SELL/HOLD)
   - Key metrics (price, VWAP, deviation)
   - Professional analysis text
   - Charts if available

3. **Watchlist** (optional but recommended)
   - Multiple symbols
   - Quick overview
   - Color-coded signals

4. **Backtest Results** (optional but recommended)
   - Performance metrics
   - Win rate
   - Charts

**Tablet Screenshots (1920x1200 or 2560x1600)**
Optional but recommended for better visibility

**Same content as phone, optimized for tablet layout**

## How to Create Screenshots

### Method 1: Android Emulator (Recommended)

```bash
# Start emulator
cd frontend/mobile
npx expo start --android

# In emulator:
# 1. Navigate to each screen
# 2. Press Ctrl+S (or Cmd+S on Mac) to save screenshot
# 3. Screenshots saved to ~/Pictures/Screenshots/
```

### Method 2: Physical Device

```bash
# Run on device
npx expo start

# Scan QR code with Expo Go app

# Take screenshots:
# Android: Power + Volume Down
# Screenshots in device gallery
```

### Method 3: Design Tool Mockups

Use Figma/Sketch to create mockups:
1. Import app design
2. Place in device frame
3. Export at required dimensions

**Free Device Mockups:**
- https://mockuphone.com
- https://smartmockups.com
- https://deviceframes.com

## Asset Specifications Summary

| Asset | Dimensions | Format | Required |
|-------|-----------|--------|----------|
| App Icon | 1024x1024 | PNG | Yes |
| Adaptive Icon | 1024x1024 | PNG | Yes |
| Favicon | 48x48 | PNG | Yes |
| Feature Graphic | 1024x500 | PNG/JPG | Yes |
| Phone Screenshots | 1080x1920 | PNG/JPG | 2-8 |
| Tablet Screenshots | 1920x1200 | PNG/JPG | 0-8 |

## Color Palette

Use these colors for consistency:

```
Primary Blue:    #3b82f6
Dark Background: #0a0e27
Darker BG:       #060918
Green (BUY):     #10b981
Red (SELL):      #ef4444
Yellow (HOLD):   #f59e0b
Gray Text:       #9ca3af
White Text:      #ffffff
```

## Quick Start with Figma

### 1. Create New File
- Go to https://figma.com
- Create account (free)
- New design file

### 2. Set Up Artboards
```
Frame 1: 1024x1024 (App Icon)
Frame 2: 1024x1024 (Adaptive Icon)
Frame 3: 1024x500 (Feature Graphic)
Frame 4: 1080x1920 (Phone Screenshot)
```

### 3. Design App Icon
```
1. Create circle or rounded square
2. Add gradient (dark blue to darker blue)
3. Add "Q" letter or oracle symbol
4. Add subtle glow/shadow
5. Export as PNG
```

### 4. Design Feature Graphic
```
1. Add dark gradient background
2. Place app screenshot mockup (left)
3. Add feature icons and text (right)
4. Keep it clean and professional
5. Export as PNG
```

### 5. Export Assets
```
File → Export
- Format: PNG
- Scale: 1x (original size)
- Export all frames
```

## Asset Placement

After creating assets, place them in:

```
frontend/mobile/assets/
├── icon.png              (1024x1024)
├── adaptive-icon.png     (1024x1024)
├── favicon.png           (48x48)
├── splash.png            (1284x2778, optional)
├── feature-graphic.png   (1024x500, for Play Store)
└── screenshots/
    ├── phone/
    │   ├── 1-dashboard.png
    │   ├── 2-analysis.png
    │   ├── 3-watchlist.png
    │   └── 4-backtest.png
    └── tablet/
        ├── 1-dashboard.png
        └── 2-analysis.png
```

## Testing Assets

### Test Icon Visibility

```bash
# Build preview APK
cd frontend/mobile
eas build --platform android --profile preview

# Install and check:
# - Icon appears correctly
# - Icon is clear at small size
# - Adaptive icon works with different launchers
```

### Test Screenshots

Before uploading to Play Store:
- View at actual size (100%)
- Check text is readable
- Verify colors are accurate
- Ensure no sensitive data visible
- Check for typos

## Common Mistakes to Avoid

❌ **Don't:**
- Use low resolution images
- Include text in app icon (hard to read)
- Use copyrighted images
- Show fake data or misleading features
- Include device frames in screenshots (Play Store adds them)
- Use screenshots from other apps

✅ **Do:**
- Use high quality, crisp images
- Keep designs simple and clean
- Use consistent branding
- Show real app features
- Test on multiple devices
- Follow Google's guidelines

## Resources

### Design Tools (Free)
- **Figma:** https://figma.com
- **Canva:** https://canva.com
- **GIMP:** https://gimp.org
- **Inkscape:** https://inkscape.org

### Icon Generators
- **App Icon Generator:** https://appicon.co
- **Adaptive Icon:** https://adapticon.tooo.io
- **Icon Kitchen:** https://icon.kitchen

### Mockup Tools
- **Mockuphone:** https://mockuphone.com
- **Smartmockups:** https://smartmockups.com
- **Previewed:** https://previewed.app

### Stock Images (if needed)
- **Unsplash:** https://unsplash.com
- **Pexels:** https://pexels.com
- **Pixabay:** https://pixabay.com

### Google Guidelines
- **Asset Guidelines:** https://support.google.com/googleplay/android-developer/answer/9866151
- **Design Guidelines:** https://developer.android.com/design

## Timeline

**Estimated time to create all assets:**
- App icons: 1-2 hours
- Feature graphic: 1-2 hours
- Screenshots: 1-2 hours
- **Total: 3-6 hours**

## Need Help?

If you're not a designer:
1. **Hire on Fiverr:** $20-50 for complete asset package
2. **Use templates:** Many free icon templates available
3. **AI tools:** Midjourney, DALL-E for icon concepts
4. **Ask community:** Reddit r/androiddev, r/ExpoJS

## Next Steps

1. [ ] Create app icon (1024x1024)
2. [ ] Create adaptive icon (1024x1024)
3. [ ] Create favicon (48x48)
4. [ ] Create feature graphic (1024x500)
5. [ ] Capture phone screenshots (2-8)
6. [ ] Capture tablet screenshots (optional)
7. [ ] Place all assets in correct folders
8. [ ] Test build with new assets
9. [ ] Upload to Play Console
10. [ ] Submit for review!
