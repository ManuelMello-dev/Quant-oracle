"""
FastAPI Server for Quant Oracle
Provides REST API and WebSocket endpoints
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_wrapper import analyze_symbol, run_backtest, analyze_multiple_timeframes
from llm_analyzer import analyze_with_llm, LLMAnalyzer
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="Quant Oracle API",
    description="Professional trading analysis powered by quantitative algorithms and LLM",
    version="1.0.0"
)

# CORS middleware for web/mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global LLM analyzer (lazy initialization)
llm_analyzer = None


class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    symbol: str
    timeframe: str = "1h"
    days: int = 365
    use_llm: bool = False


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    symbols: List[str]
    timeframe: str = "1h"
    days: int = 365


class BacktestRequest(BaseModel):
    """Request model for backtesting"""
    symbol: str
    timeframe: str = "1h"
    days: int = 365
    holding_periods: List[int] = [5, 10, 20]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Quant Oracle API",
        "version": "1.0.0",
        "endpoints": {
            "analysis": "/api/analyze/{symbol}",
            "backtest": "/api/backtest/{symbol}",
            "multi_timeframe": "/api/multi-timeframe/{symbol}",
            "batch": "/api/analyze/batch",
            "websocket": "/ws/live/{symbol}"
        }
    }


@app.get("/api/analyze/{symbol}")
async def analyze(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe (1h, 4h, 1d)"),
    days: int = Query(365, description="Historical days to fetch"),
    use_llm: bool = Query(False, description="Use LLM for professional analysis")
):
    """
    Analyze a trading symbol
    
    Args:
        symbol: Trading pair (e.g., BTC/USD, ETH/USD or BTC-USD, ETH-USD)
        timeframe: Candle timeframe
        days: Historical data period
        use_llm: Enable LLM-based analysis (Premium feature)
        
    Returns:
        Analysis results with signals and metrics
    """
    try:
        # Convert URL-safe format (BTC-USD) to standard format (BTC/USD)
        symbol = symbol.replace('-', '/')
        
        # Run core analysis
        df = analyze_symbol(symbol, timeframe=timeframe, days=days)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Extract latest metrics
        latest = df.iloc[-1]
        
        response = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": str(latest.name),
            "metrics": {
                "price": float(latest['close']),
                "vwap": float(latest['vwap']),
                "deviation": float(latest['deviation']),
                "volume_ratio": float(latest['volume_ratio']),
                "signal": latest['signal'],
                "phase": float(latest.get('phase', 0)),
                "cycle_position": latest.get('cycle_position', 'unknown'),
                "trend": latest.get('trend', 'unknown'),
                "regime": latest.get('regime', 'unknown')
            },
            "historical": {
                "bars": len(df),
                "buy_signals": int((df['signal'] == 'BUY').sum()),
                "sell_signals": int((df['signal'] == 'SELL').sum()),
                "hold_signals": int((df['signal'] == 'HOLD').sum())
            }
        }
        
        # Add LLM analysis if requested
        if use_llm:
            global llm_analyzer
            if llm_analyzer is None:
                llm_analyzer = LLMAnalyzer()
            
            if llm_analyzer.initialized:
                llm_result = llm_analyzer.analyze_market_data(df, symbol)
                response['professional_analysis'] = llm_result['analysis']
                response['analysis_method'] = llm_result['method']
            else:
                # Fallback to rule-based
                from llm_analyzer import analyze_with_llm
                llm_result = analyze_with_llm(df, symbol)
                response['professional_analysis'] = llm_result['analysis']
                response['analysis_method'] = 'rule-based'
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/batch")
async def batch_analyze(request: BatchAnalysisRequest):
    """
    Analyze multiple symbols in batch
    
    Args:
        request: Batch analysis request with symbols list
        
    Returns:
        List of analysis results
    """
    try:
        results = []
        
        for symbol in request.symbols:
            try:
                df = analyze_symbol(symbol, timeframe=request.timeframe, days=request.days)
                
                if df is not None and len(df) > 0:
                    latest = df.iloc[-1]
                    results.append({
                        "symbol": symbol,
                        "price": float(latest['close']),
                        "deviation": float(latest['deviation']),
                        "signal": latest['signal'],
                        "volume_ratio": float(latest['volume_ratio']),
                        "trend": latest.get('trend', 'unknown')
                    })
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/backtest/{symbol}")
async def backtest(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe"),
    days: int = Query(365, description="Historical days"),
    holding_periods: str = Query("5,10,20", description="Comma-separated holding periods")
):
    """
    Run backtest on historical data
    
    Args:
        symbol: Trading pair (BTC/USD or BTC-USD format)
        timeframe: Candle timeframe
        days: Historical period
        holding_periods: Holding periods to test
        
    Returns:
        Backtest results with performance metrics
    """
    try:
        # Convert URL-safe format
        symbol = symbol.replace('-', '/')
        
        # Parse holding periods
        periods = [int(p.strip()) for p in holding_periods.split(',')]
        
        # Run backtest
        results = run_backtest(symbol, timeframe=timeframe, days=days, holding_periods=periods)
        
        if results is None:
            raise HTTPException(status_code=404, detail=f"Backtest failed for {symbol}")
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/multi-timeframe/{symbol}")
async def multi_timeframe(
    symbol: str,
    timeframes: str = Query("1h,4h,1d", description="Comma-separated timeframes")
):
    """
    Analyze symbol across multiple timeframes
    
    Args:
        symbol: Trading pair (BTC/USD or BTC-USD format)
        timeframes: Timeframes to analyze
        
    Returns:
        Multi-timeframe analysis with confluence score
    """
    try:
        # Convert URL-safe format
        symbol = symbol.replace('-', '/')
        
        # Parse timeframes
        tf_list = [tf.strip() for tf in timeframes.split(',')]
        
        # Run multi-timeframe analysis
        results = analyze_multiple_timeframes(symbol, timeframes=tf_list)
        
        if results is None:
            raise HTTPException(status_code=404, detail=f"Multi-timeframe analysis failed for {symbol}")
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = []
        self.active_connections[symbol].append(websocket)
    
    def disconnect(self, websocket: WebSocket, symbol: str):
        if symbol in self.active_connections:
            self.active_connections[symbol].remove(websocket)
    
    async def broadcast(self, symbol: str, message: dict):
        if symbol in self.active_connections:
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


@app.websocket("/ws/live/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time updates
    
    Args:
        symbol: Trading pair to monitor
    """
    await manager.connect(websocket, symbol)
    
    try:
        # Send initial analysis
        df = analyze_symbol(symbol, timeframe="1h", days=30)
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            await websocket.send_json({
                "type": "initial",
                "symbol": symbol,
                "data": {
                    "price": float(latest['close']),
                    "deviation": float(latest['deviation']),
                    "signal": latest['signal'],
                    "volume_ratio": float(latest['volume_ratio'])
                }
            })
        
        # Keep connection alive and send updates every 60 seconds
        while True:
            await asyncio.sleep(60)
            
            # Fetch latest data
            df = analyze_symbol(symbol, timeframe="1h", days=30)
            if df is not None and len(df) > 0:
                latest = df.iloc[-1]
                await websocket.send_json({
                    "type": "update",
                    "symbol": symbol,
                    "timestamp": str(latest.name),
                    "data": {
                        "price": float(latest['close']),
                        "deviation": float(latest['deviation']),
                        "signal": latest['signal'],
                        "volume_ratio": float(latest['volume_ratio'])
                    }
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, symbol)


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Quant Oracle API Server...")
    print("📊 Endpoints available at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
