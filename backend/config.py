import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Data Source Configuration ---
# Options: 'cmc', 'coingecko', 'exchange', 'auto'
# - 'cmc': CoinMarketCap scraper (best OHLC, unlimited history, slower)
# - 'coingecko': CoinGecko API (fast, reliable, 365 days max)
# - 'exchange': Exchange API (requires keys, real-time)
# - 'auto': Smart selection (CMC for backtesting, CoinGecko for real-time)
DATA_SOURCE = os.environ.get("DATA_SOURCE", "auto")

# --- Exchange API Configuration (Optional) ---
# Only needed if DATA_SOURCE is 'exchange' or 'auto' with keys
# NOTE: For security, it is highly recommended to set these as environment variables.
# e.g., export COINBASE_API_KEY='YOUR_KEY'
#       export COINBASE_SECRET='YOUR_SECRET'

API_KEY = os.environ.get("COINBASE_API_KEY", "YOUR_API_KEY_HERE")
SECRET = os.environ.get("COINBASE_SECRET", "YOUR_SECRET_HERE")

# --- Oracle Parameters ---
# The trading pairs to analyze (up to 3)
# Universal format: 'DOGE/USD', 'BTC/USD', 'ETH/USD'
# Works with both CoinGecko and exchanges
SYMBOLS = ['DOGE/USD', 'BTC/USD', 'ETH/USD']

# Symbol mapping for CoinGecko (symbol -> coin_id)
COINGECKO_SYMBOL_MAP = {
    'DOGE/USD': 'dogecoin',
    'BTC/USD': 'bitcoin',
    'ETH/USD': 'ethereum',
    'PEPE/USD': 'pepe',
    'SOL/USD': 'solana',
    'XRP/USD': 'ripple',
    'ADA/USD': 'cardano',
    'AVAX/USD': 'avalanche-2',
    'DOT/USD': 'polkadot',
    'MATIC/USD': 'matic-network',
    'LINK/USD': 'chainlink',
    'UNI/USD': 'uniswap',
    'SHIB/USD': 'shiba-inu',
    'LTC/USD': 'litecoin',
    'BCH/USD': 'bitcoin-cash',
}

# Symbol mapping for CoinMarketCap (symbol -> ticker)
CMC_SYMBOL_MAP = {
    'DOGE/USD': 'DOGE',
    'BTC/USD': 'BTC',
    'ETH/USD': 'ETH',
    'PEPE/USD': 'PEPE',
    'SOL/USD': 'SOL',
    'XRP/USD': 'XRP',
    'ADA/USD': 'ADA',
    'AVAX/USD': 'AVAX',
    'DOT/USD': 'DOT',
    'MATIC/USD': 'MATIC',
    'LINK/USD': 'LINK',
    'UNI/USD': 'UNI',
    'SHIB/USD': 'SHIB',
    'LTC/USD': 'LTC',
    'BCH/USD': 'BCH',
}

# Legacy support - if SYMBOL is used, it will be converted to SYMBOLS
SYMBOL = SYMBOLS[0] if isinstance(SYMBOLS, list) else SYMBOLS

# The timeframe for the OHLCV data (e.g., '1h', '4h', '1d')
TIMEFRAME = '1h'

# Number of historical data points to fetch for analysis (e.g., 500)
LIMIT = 1500

# Standard deviation threshold for the deviation signal E
# User specified |E| > 2*sigma
SIGMA_THRESHOLD = 2.0

# The period (in number of bars) for the VWAP calculation.
# A longer period smooths the equilibrium.
VWAP_PERIOD = 100

# The period (in number of bars) for the FFT analysis.
# This should be a power of 2 for optimal FFT performance.
FFT_PERIOD = 256

# Reversal timing threshold (as a fraction of the dominant period)
# If T_reversal < Dominant_Period * REVERSAL_THRESHOLD_PERCENT, it's considered 'approaching reversal'
REVERSAL_THRESHOLD_PERCENT = 0.10

# --- Validation ---
def validate_config():
    """Validates configuration parameters."""
    errors = []
    
    if LIMIT < max(VWAP_PERIOD, FFT_PERIOD):
        errors.append(f"LIMIT ({LIMIT}) must be >= max(VWAP_PERIOD, FFT_PERIOD) = {max(VWAP_PERIOD, FFT_PERIOD)}")
    
    if SIGMA_THRESHOLD <= 0:
        errors.append(f"SIGMA_THRESHOLD must be positive, got {SIGMA_THRESHOLD}")
    
    if not (0 < REVERSAL_THRESHOLD_PERCENT < 1):
        errors.append(f"REVERSAL_THRESHOLD_PERCENT must be between 0 and 1, got {REVERSAL_THRESHOLD_PERCENT}")
    
    if FFT_PERIOD & (FFT_PERIOD - 1) != 0:
        errors.append(f"FFT_PERIOD should be a power of 2 for optimal performance, got {FFT_PERIOD}")
    
    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True
