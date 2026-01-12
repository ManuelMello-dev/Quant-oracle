"""
Simple Working API Server for Quant Oracle
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ccxt
from oracle import run_oracle_analysis

app = FastAPI(title="Quant Oracle API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Quant Oracle API",
        "version": "1.0.0"
    }

@app.get("/api/analyze/{symbol}")
def analyze(symbol: str, days: int = 7):
    """Analyze a symbol - simple and working"""
    try:
        # Convert URL format
        symbol = symbol.replace('-', '/')
        
        # Calculate limit
        limit = days * 24  # Assuming 1h timeframe
        
        # Run analysis
        exchange = ccxt.binance()
        result = run_oracle_analysis(
            exchange=exchange,
            symbol=symbol,
            timeframe='1h',
            limit=limit,
            vwap_period=100,
            fft_period=256,
            sigma_threshold=2.0,
            reversal_threshold_percent=0.10,
            enable_backtest=False,
            enable_trend_analysis=False,
            export_csv=False,
            data_source='coingecko'
        )
        
        # Extract DataFrame
        df = result[0] if isinstance(result, tuple) else result
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Get latest data
        latest = df.iloc[-1]
        
        # Build response
        response = {
            "symbol": symbol,
            "timeframe": "1h",
            "timestamp": str(latest.name),
            "metrics": {
                "price": float(latest['close']),
                "vwap": float(latest['Z_prime']),
                "deviation": float(latest['E']),
                "volume_ratio": float(latest['Volume_Ratio']) * 100,
                "signal": str(latest['Signal']),
                "phase": float(latest['Phase_Rad']) if latest['Phase_Rad'] == latest['Phase_Rad'] else 0,
                "cycle_position": "unknown",
                "trend": "unknown",
                "regime": "unknown"
            },
            "historical": {
                "bars": len(df),
                "buy_signals": int((df['Signal'] == 'BUY').sum()),
                "sell_signals": int((df['Signal'] == 'SELL').sum()),
                "hold_signals": int((df['Signal'] == 'HOLD').sum())
            }
        }
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Quant Oracle API...")
    print("📊 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
