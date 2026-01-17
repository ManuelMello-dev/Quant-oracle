"""
Data source abstraction layer for the Quant Oracle.

Supports multiple data sources (3-tier hybrid):
- CoinMarketCap (best OHLC, unlimited history, slower)
- CoinGecko (fast, reliable, 365 days max)
- CCXT exchanges (real-time, requires API keys)
- Auto-detection (smart selection based on use case)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def fetch_ohlcv_cmc(symbol, timeframe, limit):
    """
    Fetch OHLCV data from CoinMarketCap via cryptocmd scraper.
    
    Pros:
    - True OHLC data (not approximated)
    - Unlimited historical data (years)
    - No API keys needed
    
    Cons:
    - Slower (scraping-based, 10-30 seconds)
    - Only daily data available
    - Could break if CMC changes website
    
    Args:
        symbol: Trading pair (e.g., 'DOGE/USD')
        timeframe: Candle interval (note: CMC only provides daily)
        limit: Number of bars to fetch
    
    Returns:
        DataFrame with OHLCV data
    """
    from cryptocmd import CmcScraper
    from config import CMC_SYMBOL_MAP
    
    # Map symbol to CMC ticker
    ticker = CMC_SYMBOL_MAP.get(symbol)
    if not ticker:
        raise ValueError(f"Symbol {symbol} not supported by CMC. Add to CMC_SYMBOL_MAP in config.py")
    
    # Calculate date range
    end_date = datetime.now()
    
    # CMC provides daily data, so calculate days needed
    if timeframe in ['5m', '15m', '1h', '4h']:
        # For intraday timeframes, we'll get daily data and user will need to understand limitation
        days_needed = max(limit // 24, limit)  # Rough estimate
    elif timeframe == '1d':
        days_needed = limit
    elif timeframe == '1w':
        days_needed = limit * 7
    else:
        days_needed = limit
    
    start_date = end_date - timedelta(days=days_needed + 10)  # Add buffer
    
    # Format dates for CMC (DD-MM-YYYY)
    start_str = start_date.strftime("%d-%m-%Y")
    end_str = end_date.strftime("%d-%m-%Y")
    
    print(f"Fetching {symbol} from CoinMarketCap...")
    print(f"  Ticker: {ticker}")
    print(f"  Date range: {start_str} to {end_str}")
    print(f"  ⚠️  Note: CMC provides daily data only")
    
    try:
        # Scrape data from CMC
        scraper = CmcScraper(ticker, start_str, end_str)
        df = scraper.get_dataframe()
        
        # CMC columns: Date, Open, High, Low, Close, Volume, Market Cap
        df = df.rename(columns={
            'Date': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df = df.sort_index()  # Ensure chronological order
        
        # Select only OHLCV columns
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        # Handle timeframe resampling if needed
        if timeframe == '1w':
            # Resample daily to weekly
            df = df.resample('1W').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
        elif timeframe in ['5m', '15m', '1h', '4h']:
            # CMC only has daily data, can't provide intraday
            print(f"  ⚠️  CMC only provides daily data, cannot resample to {timeframe}")
            print(f"  ⚠️  Using daily data instead (consider using CoinGecko for intraday)")
        
        # Limit to requested number of bars
        df = df.tail(limit)
        
        print(f"✅ Successfully fetched {len(df)} bars from CoinMarketCap")
        
        if len(df) < limit:
            print(f"⚠️  Warning: Only got {len(df)} bars (requested {limit})")
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching data from CoinMarketCap: {e}")
        print(f"   This could be due to:")
        print(f"   - Network issues")
        print(f"   - CMC website changes")
        print(f"   - Invalid ticker symbol")
        return None


def fetch_ohlcv_coingecko(symbol, timeframe, limit):
    """
    Fetch OHLCV data from CoinGecko.
    
    Args:
        symbol: Trading pair (e.g., 'DOGE/USD')
        timeframe: Candle interval ('1h', '4h', '1d', '1w')
        limit: Number of bars to fetch
    
    Returns:
        DataFrame with OHLCV data
    """
    from pycoingecko import CoinGeckoAPI
    from config import COINGECKO_SYMBOL_MAP
    
    cg = CoinGeckoAPI()
    
    # Map symbol to CoinGecko ID
    coin_id = COINGECKO_SYMBOL_MAP.get(symbol)
    if not coin_id:
        raise ValueError(f"Symbol {symbol} not supported by CoinGecko. Add to COINGECKO_SYMBOL_MAP in config.py")
    
    # Calculate days needed based on timeframe
    timeframe_hours = {
        '5m': 5/60,
        '15m': 15/60,
        '1h': 1,
        '4h': 4,
        '1d': 24,
        '1w': 168
    }
    
    hours_per_bar = timeframe_hours.get(timeframe, 24)
    days_needed = int((limit * hours_per_bar) / 24) + 1
    
    # CoinGecko limits
    max_days = min(days_needed, 365)  # Free tier max
    
    print(f"Fetching {limit} bars of {symbol} at {timeframe} from CoinGecko...")
    print(f"  Requesting {max_days} days of data for coin: {coin_id}")
    
    try:
        # Fetch market chart data (includes prices, market cap, volume)
        chart = cg.get_coin_market_chart_by_id(
            id=coin_id,
            vs_currency='usd',
            days=max_days
        )
        
        # Extract prices and volumes
        prices = chart['prices']
        volumes = chart['total_volumes']
        
        # Convert to DataFrames
        price_df = pd.DataFrame(prices, columns=['timestamp', 'close'])
        volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
        
        # Merge on timestamp
        df = price_df.merge(volume_df, on='timestamp', how='left')
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # CoinGecko doesn't provide OHLC in free tier for market_chart
        # We'll approximate: open = previous close, high/low = close ± small range
        df['open'] = df['close'].shift(1).fillna(df['close'])
        
        # Estimate high/low based on typical crypto volatility
        # This is approximate but sufficient for VWAP calculations
        volatility = df['close'].pct_change().std()
        df['high'] = df['close'] * (1 + volatility)
        df['low'] = df['close'] * (1 - volatility)
        
        # Reorder columns
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        # Resample to requested timeframe if needed
        if timeframe != '1h':
            # CoinGecko gives ~5min data for 1 day, hourly for 2-90 days, daily for 91+ days
            # Resample to requested timeframe
            resample_map = {
                '5m': '5T',
                '15m': '15T',
                '1h': '1H',
                '4h': '4H',
                '1d': '1D',
                '1w': '1W'
            }
            
            freq = resample_map.get(timeframe, '1H')
            
            df = df.resample(freq).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
        
        # Limit to requested number of bars
        df = df.tail(limit)
        
        print(f"✅ Successfully fetched {len(df)} data points from CoinGecko")
        
        if len(df) < limit:
            print(f"⚠️  Warning: Only got {len(df)} bars (requested {limit})")
            print(f"   CoinGecko free tier may have data limitations for this timeframe")
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching data from CoinGecko: {e}")
        return None


def fetch_ohlcv_exchange(exchange, symbol, timeframe, limit):
    """
    Fetch OHLCV data from exchange via CCXT.
    
    Args:
        exchange: CCXT exchange object
        symbol: Trading pair (e.g., 'DOGE/USD')
        timeframe: Candle interval
        limit: Number of bars to fetch
    
    Returns:
        DataFrame with OHLCV data
    """
    import ccxt.base.errors as ccxt_errors
    
    print(f"Fetching {limit} bars of {symbol} at {timeframe} from exchange...")
    
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        print(f"✅ Successfully fetched {len(df)} data points from exchange")
        return df
        
    except ccxt_errors.ExchangeError as e:
        print(f"❌ Exchange Error: {e}")
        print("   Ensure the symbol is correct and the exchange supports the timeframe/limit")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def fetch_ohlcv_data(exchange, symbol, timeframe, limit, source='auto'):
    """
    Fetch OHLCV data from best available source (3-tier hybrid).
    
    Priority (auto mode):
    1. CMC - For large datasets (>365 days) or when OHLC accuracy critical
    2. CoinGecko - For real-time analysis (<365 days), fast and reliable
    3. Exchange - If user has API keys, most accurate real-time data
    
    Args:
        exchange: CCXT exchange object (can be None)
        symbol: Trading pair (e.g., 'DOGE/USD')
        timeframe: Candle interval
        limit: Number of bars to fetch
        source: 'auto', 'cmc', 'coingecko', or 'exchange'
    
    Returns:
        DataFrame with OHLCV data
    """
    
    if source == 'cmc':
        return fetch_ohlcv_cmc(symbol, timeframe, limit)
    
    elif source == 'coingecko':
        return fetch_ohlcv_coingecko(symbol, timeframe, limit)
    
    elif source == 'exchange':
        if exchange is None:
            raise ValueError("Exchange object required for 'exchange' source")
        return fetch_ohlcv_exchange(exchange, symbol, timeframe, limit)
    
    elif source == 'auto':
        # Smart selection based on use case
        
        # Strategy 1: Intraday timeframes -> Use CoinGecko (CMC only has daily)
        # Check this FIRST before dataset size to avoid CMC for intraday
        if timeframe in ['5m', '15m', '1h', '4h']:
            print(f"📊 Intraday timeframe ({timeframe}) - Using CoinGecko")
            df = fetch_ohlcv_coingecko(symbol, timeframe, limit)
            if df is not None and not df.empty:
                return df
            print("⚠️  CoinGecko fetch failed, trying CMC (daily data)...")
            df = fetch_ohlcv_cmc(symbol, timeframe, limit)
            if df is not None and not df.empty:
                return df
        
        # Strategy 2: Large historical dataset (>365 days) -> Use CMC
        elif limit > 365:
            print(f"📊 Large dataset ({limit} bars) - Using CoinMarketCap for best historical data")
            df = fetch_ohlcv_cmc(symbol, timeframe, limit)
            if df is not None and not df.empty:
                return df
            print("⚠️  CMC fetch failed, falling back to CoinGecko...")
        
        # Strategy 3: Default -> CoinGecko (fast, reliable, 365 days max)rst (faster)
        if timeframe in ['1d', '1w'] and limit <= 365:
            print(f"📊 Standard analysis ({limit} bars @ {timeframe}) - Using CoinGecko")
            df = fetch_ohlcv_coingecko(symbol, timeframe, limit)
            if df is not None and not df.empty:
                return df
            print("⚠️  CoinGecko fetch failed, trying CMC...")
            df = fetch_ohlcv_cmc(symbol, timeframe, limit)
            if df is not None and not df.empty:
                return df
        
        # Strategy 4: Exchange as last resort (if available)
        if exchange is not None:
            print("⚠️  Free sources failed, trying exchange...")
            df = fetch_ohlcv_exchange(exchange, symbol, timeframe, limit)
            if df is not None and not df.empty:
                return df
        
        # All sources failed
        print("❌ All data sources failed")
        return None
    
    else:
        raise ValueError(f"Unknown source: {source}. Use 'auto', 'cmc', 'coingecko', or 'exchange'")


def initialize_data_source():
    """
    Initialize data source based on configuration.
    
    Returns:
        Tuple of (exchange_object, source_type)
        - exchange_object: CCXT exchange or None
        - source_type: 'cmc', 'coingecko', 'exchange', or 'auto'
    """
    from config import DATA_SOURCE, API_KEY, SECRET
    
    if DATA_SOURCE == 'cmc':
        print("📊 Data Source: CoinMarketCap (scraper, no API keys needed)")
        print("   ✅ Best OHLC accuracy")
        print("   ✅ Unlimited historical data")
        print("   ⚠️  Slower (scraping-based)")
        return None, 'cmc'
    
    elif DATA_SOURCE == 'coingecko':
        print("📊 Data Source: CoinGecko (API, no keys needed)")
        print("   ✅ Fast and reliable")
        print("   ✅ Good for real-time analysis")
        print("   ⚠️  365 days max (free tier)")
        return None, 'coingecko'
    
    elif DATA_SOURCE == 'exchange':
        print("📊 Data Source: Exchange API")
        print("   ✅ Most accurate real-time data")
        print("   ⚠️  Requires API keys")
        from oracle import initialize_exchange
        exchange = initialize_exchange()
        if exchange is None:
            raise ValueError("Failed to initialize exchange. Check API keys.")
        return exchange, 'exchange'
    
    elif DATA_SOURCE == 'auto':
        # Smart 3-tier selection
        print("📊 Data Source: Auto (3-tier hybrid)")
        print("   Tier 1: CMC (for large datasets >365 days)")
        print("   Tier 2: CoinGecko (for real-time <365 days)")
        print("   Tier 3: Exchange (if API keys available)")
        
        # Check if exchange is available
        if API_KEY != "YOUR_API_KEY_HERE" and SECRET != "YOUR_SECRET_HERE":
            print("   ✅ Exchange API keys detected (available as fallback)")
            from oracle import initialize_exchange
            exchange = initialize_exchange()
            return exchange, 'auto'
        else:
            print("   ℹ️  No exchange API keys (CMC + CoinGecko only)")
            return None, 'auto'
    
    else:
        raise ValueError(f"Unknown DATA_SOURCE: {DATA_SOURCE}. Use 'auto', 'cmc', 'coingecko', or 'exchange'")
