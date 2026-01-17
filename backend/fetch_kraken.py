"""
Kraken exchange data fetcher for intraday timeframes (5m, 15m)

Uses CCXT to fetch real-time OHLCV data from Kraken exchange.
No API keys required for public data.
"""

import ccxt
import pandas as pd
from datetime import datetime


def fetch_ohlcv_kraken(symbol, timeframe, limit):
    """
    Fetch OHLCV data from Kraken via CCXT
    
    Pros:
    - Real-time intraday data (5m, 15m, 1h, etc.)
    - No API keys needed for public data
    - Reliable and fast
    - No geo-restrictions
    
    Args:
        symbol: Trading pair (e.g., 'ETH/USD', 'BTC/USD')
        timeframe: Candle interval ('5m', '15m', '1h', '4h', '1d')
        limit: Number of bars to fetch (max 720)
        
    Returns:
        DataFrame with OHLCV data
    """
    try:
        # Initialize Kraken exchange
        exchange = ccxt.kraken()
        
        # Fetch OHLCV data
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        if not ohlcv:
            raise ValueError(f"No data returned from Kraken for {symbol}")
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        print(f"✅ Successfully fetched {len(df)} bars of {timeframe} data from Kraken")
        
        return df
        
    except Exception as e:
        print(f"❌ Kraken fetch failed for {symbol}: {e}")
        return None


if __name__ == "__main__":
    # Test the function
    df = fetch_ohlcv_kraken('ETH/USD', '5m', 100)
    if df is not None:
        print(f"\nLatest data:")
        print(df.tail())
        print(f"\nPrice: ${df['close'].iloc[-1]:.2f}")
