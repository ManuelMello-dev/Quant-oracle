import axios from 'axios'

// Use environment variable or default to localhost
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000'

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
  }
  professional_analysis?: string
  analysis_method?: string
}

export const api = {
  async analyze(
    symbol: string,
    timeframe: string = '1h',
    days: number = 365,
    useLLM: boolean = false
  ): Promise<AnalysisResponse> {
    const response = await axios.get(`${API_URL}/api/analyze/${symbol}`, {
      params: { timeframe, days, use_llm: useLLM }
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

  async backtest(
    symbol: string,
    timeframe: string = '1h',
    days: number = 365,
    holdingPeriods: number[] = [5, 10, 20]
  ): Promise<any> {
    const response = await axios.get(`${API_URL}/api/backtest/${symbol}`, {
      params: { 
        timeframe, 
        days, 
        holding_periods: holdingPeriods.join(',') 
      }
    })
    return response.data
  },
}

export default api
