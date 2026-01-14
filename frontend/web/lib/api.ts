import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface AnalysisMetrics {
  price: number
  vwap: number
  deviation: number
  volume_ratio: number
  signal: 'BUY' | 'SELL' | 'HOLD'
  phase: number
  cycle_position: string
  trend: string
  regime: string
}

export interface AnalysisResponse {
  symbol: string
  timeframe: string
  timestamp: string
  metrics: AnalysisMetrics
  historical: {
    bars: number
    buy_signals: number
    sell_signals: number
    hold_signals: number
    series: Array<{
      time: string
      price: number
      vwap: number
      deviation: number
    }>
  }
  professional_analysis?: string
  analysis_method?: string
}

export interface BacktestResponse {
  symbol: string
  timeframe: string
  period_days: number
  total_bars: number
  signal_performance: {
    [key: string]: {
      count: number
      win_rate_10: number
      mean_return_10: number
      median_return_10: number
    }
  }
  phase_accuracy: {
    total_predictions: number
    correct_predictions: number
    accuracy: number
  }
}

export interface MultiTimeframeResponse {
  symbol: string
  timeframes: {
    [key: string]: {
      signal: string
      deviation: number
      volume_ratio: number
      trend: string
    }
  }
  confluence: {
    score: number
    recommendation: string
  }
}

export const api = {
  async analyze(
    symbol: string,
    timeframe: string = '1h',
    days: number = 365,
    useLLM: boolean = false
  ): Promise<AnalysisResponse> {
    const response = await axios.get(`${API_URL}/api/analyze`, {
      params: { symbol, timeframe, days, use_llm: useLLM }
    })
    return response.data
  },

  async backtest(
    symbol: string,
    timeframe: string = '1h',
    days: number = 365,
    holdingPeriods: number[] = [5, 10, 20]
  ): Promise<BacktestResponse> {
    const response = await axios.get(`${API_URL}/api/backtest/${symbol}`, {
      params: { 
        timeframe, 
        days, 
        holding_periods: holdingPeriods.join(',') 
      }
    })
    return response.data
  },

  async multiTimeframe(
    symbol: string,
    timeframes: string[] = ['1h', '4h', '1d']
  ): Promise<MultiTimeframeResponse> {
    const response = await axios.get(`${API_URL}/api/multi-timeframe/${symbol}`, {
      params: { timeframes: timeframes.join(',') }
    })
    return response.data
  },

  async batchAnalyze(
    symbols: string[],
    timeframe: string = '1h',
    days: number = 365
  ): Promise<any> {
    const response = await axios.post(`${API_URL}/api/analyze/batch`, {
      symbols,
      timeframe,
      days
    })
    return response.data
  },

  connectWebSocket(symbol: string, onMessage: (data: any) => void): WebSocket {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    const ws = new WebSocket(`${WS_URL}/ws/live/${symbol}`)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage(data)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    return ws
  }
}

export default api
