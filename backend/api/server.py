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
from advanced_llm_analyzer import AdvancedLLMAnalyzer, analyze_with_advanced_llm
from entry_analyzer import EntryPointAnalyzer, analyze_entry_point
from genesis_vocabulary import GenesisDriftVocabulary, generate_genesis_narrative
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
        "advanced_analysis": "/api/advanced-analysis?symbol={symbol}",
        "record_trade": "/api/record-trade",
        "backtest": "/api/backtest/{symbol}",
        "multi_timeframe": "/api/multi-timeframe/{symbol}",
        "batch": "/api/analyze/batch",
        "entry_zones": "/api/entry-zones?symbol={symbol}",
        "evaluate_entry": "/api/evaluate-entry",
        "sigma_bands": "/api/sigma-bands?symbol={symbol}",
        "genesis_state": "/api/genesis-state?symbol={symbol}",
        "websocket": "/ws/live/{symbol}"
    },
        "new_features": {
            "entry_analysis": "Optimal entry zones with risk/reward analysis",
            "genesis_vocabulary": "Philosophical market state narratives",
            "sigma_bands": "Price levels at sigma deviations",
            "user_entry_eval": "Evaluate your entry prices"
        }
    }


@app.get("/api/analyze")
async def analyze(
    symbol: str = Query(..., description="Trading pair"),
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
                "vwap": float(latest['Z_prime']),
                "deviation": float(latest['E']),
                "volume_ratio": float(latest['Volume_Ratio']),
                "signal": latest['Signal'],
                "phase": float(latest.get('Phase_Rad', 0)),
                "cycle_position": latest.get('Phase_Context', 'unknown'),
                "trend": latest.get('Trend_Consensus', 'unknown'),
                "regime": latest.get('Market_Regime', 'unknown'),
                "coherence": float(latest.get('Spectral_Power', 0)),
                "confidence": latest.get('Confidence', 'unknown')
            },
            "historical": {
                "bars": len(df),
                "buy_signals": int((df['Signal'] == 'BUY').sum()),
                "sell_signals": int((df['Signal'] == 'SELL').sum()),
                "hold_signals": int((df['Signal'] == 'HOLD').sum()),
                "series": [
                    {
                        "time": str(idx),
                        "price": float(row['close']),
                        "vwap": float(row['Z_prime']),
                        "deviation": float(row['E'])
                    }
                    for idx, row in df.tail(100).iterrows()
                ]
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
                        "deviation": float(latest['E']),
                        "signal": latest['Signal'],
                        "volume_ratio": float(latest['Volume_Ratio']),
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


@app.get("/api/backtest/{symbol:path}")
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


@app.get("/api/entry-zones")
async def entry_zones(
    symbol: str = Query(..., description="Trading pair"),
    timeframe: str = Query("1h", description="Timeframe"),
    days: int = Query(365, description="Historical days"),
    sigma_threshold: float = Query(2.0, description="Sigma threshold for signals")
):
    """
    Get optimal entry zones for a symbol
    
    Args:
        symbol: Trading pair (e.g., BTC/USD or BTC-USD)
        timeframe: Candle timeframe
        days: Historical data period
        sigma_threshold: Sigma threshold for coherent signals
        
    Returns:
        Optimal entry zones with risk/reward analysis
    """
    try:
        # Convert URL-safe format
        symbol = symbol.replace('-', '/')
        
        # Run core analysis
        df = analyze_symbol(symbol, timeframe=timeframe, days=days)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Get entry analysis
        entry_analysis = analyze_entry_point(df, sigma_threshold=sigma_threshold)
        
        if 'error' in entry_analysis:
            raise HTTPException(status_code=400, detail=entry_analysis['error'])
        
        return entry_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EntryEvaluationRequest(BaseModel):
    """Request model for user entry evaluation"""
    symbol: str
    user_entry_price: float
    timeframe: str = "1h"
    days: int = 365
    sigma_threshold: float = 2.0


@app.post("/api/evaluate-entry")
async def evaluate_entry(request: EntryEvaluationRequest):
    """
    Evaluate a user's entry price
    
    Args:
        request: Entry evaluation request with symbol and entry price
        
    Returns:
        Entry quality assessment with risk/reward analysis
    """
    try:
        # Convert URL-safe format
        symbol = request.symbol.replace('-', '/')
        
        # Run core analysis
        df = analyze_symbol(symbol, timeframe=request.timeframe, days=request.days)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Get entry analysis with user evaluation
        entry_analysis = analyze_entry_point(
            df,
            user_entry_price=request.user_entry_price,
            sigma_threshold=request.sigma_threshold
        )
        
        if 'error' in entry_analysis:
            raise HTTPException(status_code=400, detail=entry_analysis['error'])
        
        return entry_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sigma-bands")
async def sigma_bands(
    symbol: str = Query(..., description="Trading pair"),
    timeframe: str = Query("1h", description="Timeframe"),
    days: int = Query(365, description="Historical days"),
    num_bands: int = Query(3, description="Number of sigma bands")
):
    """
    Get sigma band price levels
    
    Args:
        symbol: Trading pair (e.g., BTC/USD or BTC-USD)
        timeframe: Candle timeframe
        days: Historical data period
        num_bands: Number of sigma bands above and below equilibrium
        
    Returns:
        Sigma band price levels
    """
    try:
        # Convert URL-safe format
        symbol = symbol.replace('-', '/')
        
        # Run core analysis
        df = analyze_symbol(symbol, timeframe=timeframe, days=days)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        latest = df.iloc[-1]
        Z_prime = float(latest['Z_prime'])
        sigma = float(latest['Sigma'])
        
        if pd.isna(Z_prime) or pd.isna(sigma) or sigma == 0:
            raise HTTPException(status_code=400, detail="Insufficient data for sigma bands calculation")
        
        # Calculate sigma bands
        bands = EntryPointAnalyzer.calculate_sigma_bands(Z_prime, sigma, num_bands)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": str(latest.name),
            "current_price": float(latest['close']),
            "equilibrium_Z_prime": Z_prime,
            "sigma": sigma,
            "bands": bands
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/genesis-state")
async def genesis_state(
    symbol: str = Query(..., description="Trading pair"),
    timeframe: str = Query("1h", description="Timeframe"),
    days: int = Query(365, description="Historical days"),
    sigma_threshold: float = Query(2.0, description="Sigma threshold")
):
    """
    Get Genesis Drift market state narrative
    
    Args:
        symbol: Trading pair (e.g., BTC/USD or BTC-USD)
        timeframe: Candle timeframe
        days: Historical data period
        sigma_threshold: Sigma threshold for coherent signals
        
    Returns:
        Genesis Drift philosophical market narrative
    """
    try:
        # Convert URL-safe format
        symbol = symbol.replace('-', '/')
        
        # Run core analysis
        df = analyze_symbol(symbol, timeframe=timeframe, days=days)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Generate Genesis Drift narrative
        narrative = generate_genesis_narrative(df, sigma_threshold)
        
        if 'error' in narrative:
            raise HTTPException(status_code=400, detail=narrative['error'])
        
        # Add symbol and timestamp
        narrative['symbol'] = symbol
        narrative['timeframe'] = timeframe
        narrative['timestamp'] = str(df.iloc[-1].name)
        
        return narrative
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/multi-timeframe/{symbol:path}")
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


@app.get("/api/advanced-analysis")
async def advanced_analysis(
    symbol: str = Query(..., description="Trading pair"),
    timeframe: str = Query("1h", description="Timeframe"),
    days: int = Query(30, description="Historical days"),
    budget: float = Query(100.0, description="Trading budget in USD")
):
    """
    Get advanced contextual trading analysis with actionable recommendations
    
    This endpoint provides:
    - Personalized action plans with specific quantities and prices
    - Position tracking and trade history
    - Staged entry recommendations (50%/25%/25%)
    - Stop loss and target calculations
    - "Why this is your entry" analysis
    - Position comparison with previous trades
    
    Args:
        symbol: Trading pair (e.g., BTC/USD or BTC-USD)
        timeframe: Candle timeframe
        days: Historical data period
        budget: Trading budget for position sizing
        
    Returns:
        Comprehensive contextual analysis with actionable trading plan
    """
    try:
        # Convert URL-safe format
        symbol = symbol.replace('-', '/')
        
        # Run core analysis
        df = analyze_symbol(symbol, timeframe=timeframe, days=days)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Generate advanced analysis
        analyzer = AdvancedLLMAnalyzer(use_local_llm=False)  # Use rule-based for speed
        analysis = analyzer.generate_actionable_analysis(df, symbol)
        
        if 'error' in analysis:
            raise HTTPException(status_code=400, detail=analysis['error'])
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TradeRecordRequest(BaseModel):
    """Request model for recording a trade"""
    symbol: str
    entry: float
    exit: Optional[float] = None
    quantity: float = 0
    profit_pct: Optional[float] = None


@app.post("/api/record-trade")
async def record_trade(request: TradeRecordRequest):
    """
    Record a trade in the user's history for contextual analysis
    
    Args:
        request: Trade record with entry, exit, quantity, profit
        
    Returns:
        Confirmation of trade recorded
    """
    try:
        from advanced_llm_analyzer import TradeHistory
        
        # Convert URL-safe format
        symbol = request.symbol.replace('-', '/')
        
        # Record trade
        history = TradeHistory()
        history.add_trade(
            symbol=symbol,
            entry=request.entry,
            exit=request.exit,
            quantity=request.quantity,
            profit_pct=request.profit_pct
        )
        
        return {
            "status": "success",
            "message": f"Trade recorded for {symbol}",
            "trade": {
                "symbol": symbol,
                "entry": request.entry,
                "exit": request.exit,
                "quantity": request.quantity,
                "profit_pct": request.profit_pct
            }
        }
        
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


@app.get("/api/advanced-analysis")
async def advanced_analysis_endpoint(
    symbol: str,
    timeframe: str = "1h",
    days: int = 30,
    budget: float = 100.0
):
    """
    Get advanced contextual analysis with AI narrative
    
    Args:
        symbol: Trading pair (e.g., BTC-USD or BTC/USD)
        timeframe: Candle interval (default: 1h)
        days: Historical data period (default: 30)
        budget: Trading budget in USD (default: 100.0)
    
    Returns:
        Comprehensive analysis with AI narrative, action plan, and position tracking
    """
    try:
        # Import advanced analyzer
        import sys
        sys.path.insert(0, '/home/ubuntu/Quant-oracle/backend')
        from advanced_llm_analyzer import AdvancedLLMAnalyzer
        
        # Normalize symbol format
        normalized_symbol = symbol.replace('-', '/')
        
        # Get market data
        df = analyze_symbol(normalized_symbol, timeframe=timeframe, days=days)
        
        if df is None or len(df) == 0:
            return {"error": f"No data available for {symbol}"}
        
        # Generate advanced analysis
        analyzer = AdvancedLLMAnalyzer(use_local_llm=False, use_openai=True)
        analysis = analyzer.generate_actionable_analysis(df, normalized_symbol, budget=budget)
        
        return analysis
        
    except Exception as e:
        print(f"Error in advanced analysis: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/api/record-trade")
async def record_trade_endpoint(trade_data: dict):
    """
    Record a trade for history tracking
    
    Args:
        trade_data: Dict with symbol, entry, exit, quantity, profit_pct
    
    Returns:
        Confirmation of trade recording
    """
    try:
        # Import advanced analyzer for trade history
        import sys
        sys.path.insert(0, '/home/ubuntu/Quant-oracle/backend')
        from advanced_llm_analyzer import TradeHistory
        
        history = TradeHistory()
        
        symbol = trade_data.get('symbol', '').replace('-', '/')
        entry = trade_data.get('entry')
        exit_price = trade_data.get('exit')
        quantity = trade_data.get('quantity')
        profit_pct = trade_data.get('profit_pct')
        
        if not symbol or entry is None:
            return {"error": "Missing required fields: symbol, entry"}
        
        history.record_trade(symbol, entry, exit_price, quantity, profit_pct)
        
        return {
            "status": "success",
            "message": f"Trade recorded for {symbol}",
            "trade": {
                "symbol": symbol,
                "entry": entry,
                "exit": exit_price,
                "quantity": quantity,
                "profit_pct": profit_pct
            }
        }
        
    except Exception as e:
        print(f"Error recording trade: {e}")
        return {"error": str(e)}


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
                    "vwap": float(latest['Z_prime']),
                    "deviation": float(latest['E']),
                    "signal": latest['Signal'],
                    "volume_ratio": float(latest['Volume_Ratio']),
                    "trend": latest.get('trend', 'unknown'),
                    "regime": latest.get('regime', 'unknown'),
                    "cycle_position": latest.get('cycle_position', 'unknown'),
                    "phase": float(latest.get('Phase', 0))
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
                        "vwap": float(latest['Z_prime']),
                        "deviation": float(latest['E']),
                        "signal": latest['Signal'],
                        "volume_ratio": float(latest['Volume_Ratio']),
                        "trend": latest.get('trend', 'unknown'),
                        "regime": latest.get('regime', 'unknown'),
                        "cycle_position": latest.get('cycle_position', 'unknown'),
                        "phase": float(latest.get('Phase', 0))
                    }
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, symbol)


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or default to 8000
    port = int(os.getenv('PORT', 8000))
    
    print("🚀 Starting Quant Oracle API Server...")
    print(f"📊 Endpoints available at http://0.0.0.0:{port}")
    print(f"📚 API docs at http://0.0.0.0:{port}/docs")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
