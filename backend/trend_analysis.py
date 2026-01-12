"""
Trend Analysis and Enhanced Phase Interpretation.

Provides context for phase-based signals by detecting market regime.
Helps distinguish between mean-reversion and trend-following scenarios.
"""

import pandas as pd
import numpy as np


def detect_trend(df, short_period=20, long_period=50):
    """
    Detects market trend using multiple methods.
    
    Methods:
    1. Moving Average Crossover
    2. Linear Regression Slope
    3. ADX-like directional strength
    
    Returns DataFrame with trend indicators added.
    """
    
    # Method 1: Moving Average Crossover
    df['SMA_Short'] = df['close'].rolling(window=short_period).mean()
    df['SMA_Long'] = df['close'].rolling(window=long_period).mean()
    df['MA_Trend'] = np.where(df['SMA_Short'] > df['SMA_Long'], 'Uptrend', 'Downtrend')
    
    # Method 2: Linear Regression Slope
    def calculate_slope(series):
        if len(series) < 2:
            return 0
        x = np.arange(len(series))
        slope, _ = np.polyfit(x, series, 1)
        return slope
    
    df['LR_Slope'] = df['close'].rolling(window=short_period).apply(calculate_slope, raw=False)
    df['LR_Trend'] = np.where(df['LR_Slope'] > 0, 'Uptrend', 'Downtrend')
    
    # Method 3: Directional Movement (simplified ADX concept)
    df['High_Diff'] = df['high'].diff()
    df['Low_Diff'] = -df['low'].diff()
    
    df['Plus_DM'] = np.where(
        (df['High_Diff'] > df['Low_Diff']) & (df['High_Diff'] > 0),
        df['High_Diff'],
        0
    )
    
    df['Minus_DM'] = np.where(
        (df['Low_Diff'] > df['High_Diff']) & (df['Low_Diff'] > 0),
        df['Low_Diff'],
        0
    )
    
    # Smooth directional movement
    df['Plus_DM_Smooth'] = df['Plus_DM'].rolling(window=14).mean()
    df['Minus_DM_Smooth'] = df['Minus_DM'].rolling(window=14).mean()
    
    # Calculate directional indicator
    df['DI_Diff'] = df['Plus_DM_Smooth'] - df['Minus_DM_Smooth']
    df['DM_Trend'] = np.where(df['DI_Diff'] > 0, 'Uptrend', 'Downtrend')
    
    # Trend strength (0-100)
    df['Trend_Strength'] = np.abs(df['DI_Diff']) / (df['Plus_DM_Smooth'] + df['Minus_DM_Smooth'] + 1e-10) * 100
    
    # Consensus trend (majority vote)
    df['Trend_Consensus'] = df.apply(
        lambda row: 'Uptrend' if [row['MA_Trend'], row['LR_Trend'], row['DM_Trend']].count('Uptrend') >= 2 else 'Downtrend',
        axis=1
    )
    
    # Clean up intermediate columns
    df.drop(columns=['High_Diff', 'Low_Diff', 'Plus_DM', 'Minus_DM'], inplace=True)
    
    print(f"Trend Detection: Calculated trend indicators using {short_period}/{long_period} periods")
    
    return df


def detect_market_regime(df, volatility_period=20):
    """
    Detects market regime: Trending, Ranging, or Volatile.
    
    This helps interpret phase signals correctly:
    - Trending: Phase reversals may be less reliable
    - Ranging: Phase reversals are more reliable (mean reversion)
    - Volatile: Signals require extra caution
    """
    
    # Calculate volatility
    df['Returns'] = df['close'].pct_change()
    df['Volatility'] = df['Returns'].rolling(window=volatility_period).std() * 100
    
    # Calculate range efficiency (how much price moves vs how much it oscillates)
    df['Price_Range'] = df['high'] - df['low']
    df['True_Range'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            np.abs(df['high'] - df['close'].shift(1)),
            np.abs(df['low'] - df['close'].shift(1))
        )
    )
    
    df['ATR'] = df['True_Range'].rolling(window=14).mean()
    
    # Calculate directional movement efficiency
    df['Price_Change'] = np.abs(df['close'] - df['close'].shift(volatility_period))
    df['Path_Length'] = df['Price_Range'].rolling(window=volatility_period).sum()
    df['Efficiency_Ratio'] = df['Price_Change'] / (df['Path_Length'] + 1e-10)
    
    # Classify regime
    def classify_regime(row):
        if pd.isna(row['Efficiency_Ratio']) or pd.isna(row['Volatility']):
            return 'Unknown'
        
        # High efficiency = trending
        # Low efficiency = ranging
        # High volatility = volatile
        
        if row['Volatility'] > df['Volatility'].quantile(0.75):
            return 'Volatile'
        elif row['Efficiency_Ratio'] > 0.5:
            return 'Trending'
        else:
            return 'Ranging'
    
    df['Market_Regime'] = df.apply(classify_regime, axis=1)
    
    # Clean up intermediate columns
    df.drop(columns=['Returns', 'Price_Range', 'True_Range', 'Price_Change', 'Path_Length'], inplace=True)
    
    print(f"Market Regime Detection: Classified {len(df)} bars")
    
    return df


def interpret_phase_with_trend(df):
    """
    Interprets phase signals in the context of trend and regime.
    
    Adds contextual flags to improve signal quality.
    """
    
    # Initialize interpretation columns
    df['Phase_Context'] = 'Neutral'
    df['Signal_Quality'] = 'Medium'
    
    for i in range(len(df)):
        if pd.isna(df.iloc[i]['T_reversal']) or df.iloc[i]['Signal'] == 'HOLD':
            continue
        
        signal = df.iloc[i]['Signal']
        trend = df.iloc[i]['Trend_Consensus']
        regime = df.iloc[i]['Market_Regime']
        trend_strength = df.iloc[i]['Trend_Strength']
        
        # Interpret phase signal based on context
        if regime == 'Ranging':
            # Mean reversion is reliable in ranging markets
            df.iloc[i, df.columns.get_loc('Phase_Context')] = 'Mean_Reversion_Favorable'
            df.iloc[i, df.columns.get_loc('Signal_Quality')] = 'High'
            
        elif regime == 'Trending':
            # Check if signal aligns with trend
            if (signal == 'BUY' and trend == 'Uptrend') or (signal == 'SELL' and trend == 'Downtrend'):
                df.iloc[i, df.columns.get_loc('Phase_Context')] = 'Trend_Aligned'
                df.iloc[i, df.columns.get_loc('Signal_Quality')] = 'High'
            else:
                df.iloc[i, df.columns.get_loc('Phase_Context')] = 'Counter_Trend'
                df.iloc[i, df.columns.get_loc('Signal_Quality')] = 'Low'
                
        elif regime == 'Volatile':
            # Volatile markets are unpredictable
            df.iloc[i, df.columns.get_loc('Phase_Context')] = 'High_Volatility'
            df.iloc[i, df.columns.get_loc('Signal_Quality')] = 'Low'
    
    quality_counts = df['Signal_Quality'].value_counts()
    print(f"Phase Interpretation: {quality_counts.to_dict()}")
    
    return df


def calculate_cycle_consistency(df, lookback=10):
    """
    Calculates how consistent the dominant cycle period has been.
    
    More consistent cycles = more reliable phase predictions.
    """
    
    df['Cycle_Consistency'] = np.nan
    
    for i in range(lookback, len(df)):
        recent_periods = df.iloc[i-lookback:i]['Dominant_Period'].dropna()
        
        if len(recent_periods) > 0:
            # Calculate coefficient of variation (std / mean)
            cv = recent_periods.std() / (recent_periods.mean() + 1e-10)
            
            # Convert to consistency score (0-100, higher is better)
            consistency = max(0, 100 - (cv * 100))
            df.iloc[i, df.columns.get_loc('Cycle_Consistency')] = consistency
    
    print(f"Cycle Consistency: Calculated for {df['Cycle_Consistency'].notna().sum()} bars")
    
    return df


def enhance_signal_with_context(df):
    """
    Enhances signals with trend and regime context.
    
    Adjusts confidence based on market conditions.
    """
    
    # Detect trend
    df = detect_trend(df)
    
    # Detect market regime
    df = detect_market_regime(df)
    
    # Interpret phase with trend
    df = interpret_phase_with_trend(df)
    
    # Calculate cycle consistency
    df = calculate_cycle_consistency(df)
    
    # Adjust confidence based on context
    for i in range(len(df)):
        if df.iloc[i]['Signal'] == 'HOLD':
            continue
        
        current_confidence = df.iloc[i]['Confidence']
        signal_quality = df.iloc[i]['Signal_Quality']
        cycle_consistency = df.iloc[i]['Cycle_Consistency']
        
        # Downgrade confidence if signal quality is low
        if signal_quality == 'Low' and current_confidence == 'High':
            df.iloc[i, df.columns.get_loc('Confidence')] = 'Medium'
        
        # Upgrade confidence if signal quality is high and cycle is consistent
        if signal_quality == 'High' and not pd.isna(cycle_consistency) and cycle_consistency > 70:
            if current_confidence == 'Low':
                df.iloc[i, df.columns.get_loc('Confidence')] = 'Medium'
            elif current_confidence == 'Medium':
                df.iloc[i, df.columns.get_loc('Confidence')] = 'High'
    
    print("Signal Enhancement: Applied trend and regime context to confidence levels")
    
    return df


def get_regime_statistics(df):
    """
    Returns statistics about market regimes in the dataset.
    """
    
    regime_counts = df['Market_Regime'].value_counts()
    trend_counts = df['Trend_Consensus'].value_counts()
    
    stats = {
        'regime_distribution': regime_counts.to_dict(),
        'trend_distribution': trend_counts.to_dict(),
        'avg_trend_strength': df['Trend_Strength'].mean(),
        'avg_volatility': df['Volatility'].mean(),
        'avg_cycle_consistency': df['Cycle_Consistency'].mean()
    }
    
    return stats
