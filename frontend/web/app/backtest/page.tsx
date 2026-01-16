'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import api from '@/lib/api'

interface BacktestResult {
  symbol: string
  timeframe: string
  period_days: number
  total_bars: number
  signal_performance: {
    BUY?: {
      count: number
      win_rate_10: number
      mean_return_10: number
      median_return_10: number
    }
    SELL?: {
      count: number
      win_rate_10: number
      mean_return_10: number
      median_return_10: number
    }
    HOLD?: {
      count: number
      win_rate_10: number
      mean_return_10: number
      median_return_10: number
    }
  }
}

export default function BacktestPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const symbol = searchParams.get('symbol') || 'BTC/USD'
  
  const [timeframe, setTimeframe] = useState('1h')
  const [data, setData] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const timeframes = ['5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo', '3mo', '1y', '5y']

  useEffect(() => {
    const runBacktest = async () => {
      try {
        setLoading(true)
        setError(null)
        const result = await api.backtest(symbol, timeframe, 365, [5, 10, 20])
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to run backtest')
      } finally {
        setLoading(false)
      }
    }

    runBacktest()
  }, [symbol, timeframe])

  if (loading) {
    return (
      <main className="min-h-screen p-8 bg-gradient-to-br from-oracle-dark via-oracle-darker to-black">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-20">
            <div className="text-4xl mb-4">📊</div>
            <div className="text-xl text-gray-400">Running backtest for {symbol}...</div>
          </div>
        </div>
      </main>
    )
  }

  if (error || !data) {
    return (
      <main className="min-h-screen p-8 bg-gradient-to-br from-oracle-dark via-oracle-darker to-black">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-20">
            <div className="text-4xl mb-4">❌</div>
            <div className="text-xl text-red-400 mb-4">
              {error || 'Failed to run backtest'}
            </div>
            <button 
              onClick={() => router.back()} 
              className="px-6 py-2 bg-oracle-blue hover:bg-oracle-blue/80 text-white rounded-lg transition"
            >
              Go Back
            </button>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-oracle-dark via-oracle-darker to-black">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button 
            onClick={() => router.back()}
            className="text-oracle-blue hover:text-oracle-blue/80 mb-4 transition"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-oracle-blue mb-2">{symbol} Backtest</h1>
          <p className="text-gray-400">Historical performance analysis</p>
        </div>

        {/* Timeframe Selector */}
        <div className="mb-8 flex flex-wrap gap-2">
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-2 rounded-lg transition ${
                timeframe === tf
                  ? 'bg-oracle-blue text-white'
                  : 'bg-oracle-dark border border-oracle-blue/30 text-gray-300 hover:border-oracle-blue/60'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-oracle-dark/50 border border-oracle-blue/20 rounded-lg p-6">
            <div className="text-gray-400 text-sm mb-2">Total Bars</div>
            <div className="text-2xl font-bold text-oracle-blue">{data.total_bars}</div>
          </div>
          <div className="bg-oracle-dark/50 border border-oracle-blue/20 rounded-lg p-6">
            <div className="text-gray-400 text-sm mb-2">Timeframe</div>
            <div className="text-2xl font-bold text-oracle-blue">{data.timeframe}</div>
          </div>
          <div className="bg-oracle-dark/50 border border-oracle-blue/20 rounded-lg p-6">
            <div className="text-gray-400 text-sm mb-2">Period</div>
            <div className="text-2xl font-bold text-oracle-blue">{data.period_days} days</div>
          </div>
          <div className="bg-oracle-dark/50 border border-oracle-blue/20 rounded-lg p-6">
            <div className="text-gray-400 text-sm mb-2">Symbol</div>
            <div className="text-2xl font-bold text-oracle-blue">{data.symbol}</div>
          </div>
        </div>

        {/* Signal Performance */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(data.signal_performance).map(([signal, stats]) => {
            const signalColor = signal === 'BUY' ? 'text-oracle-green' : signal === 'SELL' ? 'text-oracle-red' : 'text-oracle-yellow'
            const signalBg = signal === 'BUY' ? 'bg-oracle-green/10' : signal === 'SELL' ? 'bg-oracle-red/10' : 'bg-oracle-yellow/10'
            
            return (
              <div key={signal} className={`${signalBg} border border-${signal === 'BUY' ? 'oracle-green' : signal === 'SELL' ? 'oracle-red' : 'oracle-yellow'}/30 rounded-lg p-6`}>
                <h3 className={`text-xl font-bold ${signalColor} mb-4`}>{signal} Signals</h3>
                <div className="space-y-3">
                  <div>
                    <div className="text-gray-400 text-sm">Count</div>
                    <div className="text-2xl font-bold text-white">{stats.count}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Win Rate (10 bars)</div>
                    <div className="text-2xl font-bold text-white">{stats.win_rate_10.toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Mean Return (10 bars)</div>
                    <div className={`text-2xl font-bold ${stats.mean_return_10 >= 0 ? 'text-oracle-green' : 'text-oracle-red'}`}>
                      {stats.mean_return_10.toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Median Return (10 bars)</div>
                    <div className={`text-2xl font-bold ${stats.median_return_10 >= 0 ? 'text-oracle-green' : 'text-oracle-red'}`}>
                      {stats.median_return_10.toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </main>
  )
}
