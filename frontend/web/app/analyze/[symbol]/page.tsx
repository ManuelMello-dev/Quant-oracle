'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import useSWR from 'swr'
import api, { AnalysisResponse } from '@/lib/api'

export default function AnalyzePage() {
  const params = useParams()
  const router = useRouter()
  const symbol = (params.symbol as string).replace('-', '/')
  const [useLLM, setUseLLM] = useState(false)
  const [timeframe, setTimeframe] = useState('1h')

  const { data, error, isLoading, mutate } = useSWR<AnalysisResponse>(
    ['analyze', symbol, timeframe, useLLM],
    () => api.analyze(symbol, timeframe, 365, useLLM),
    { refreshInterval: 60000 } // Refresh every minute
  )

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-oracle-green'
      case 'SELL': return 'text-oracle-red'
      default: return 'text-oracle-yellow'
    }
  }

  const getSignalEmoji = (signal: string) => {
    switch (signal) {
      case 'BUY': return '🟢'
      case 'SELL': return '🔴'
      default: return '🟡'
    }
  }

  if (isLoading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-20">
            <div className="text-4xl mb-4">📊</div>
            <div className="text-xl text-gray-400">Analyzing {symbol}...</div>
          </div>
        </div>
      </main>
    )
  }

  if (error || !data) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-20">
            <div className="text-4xl mb-4">❌</div>
            <div className="text-xl text-red-400 mb-4">
              Failed to analyze {symbol}
            </div>
            <button onClick={() => router.push('/')} className="btn-primary">
              Go Back
            </button>
          </div>
        </div>
      </main>
    )
  }

  const { metrics, historical } = data

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <button
              onClick={() => router.push('/')}
              className="text-oracle-blue hover:underline mb-2"
            >
              ← Back to Dashboard
            </button>
            <h1 className="text-4xl font-bold">{symbol}</h1>
            <p className="text-gray-400">{timeframe} • Last updated: {new Date(data.timestamp).toLocaleString()}</p>
          </div>
          <div className="flex gap-2">
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="bg-oracle-dark border border-gray-700 rounded-lg px-4 py-2"
            >
              <option value="1h">1 Hour</option>
              <option value="4h">4 Hours</option>
              <option value="1d">1 Day</option>
            </select>
            <button
              onClick={() => setUseLLM(!useLLM)}
              className={useLLM ? 'btn-primary' : 'btn-secondary'}
            >
              {useLLM ? '🤖 AI On' : '🤖 AI Off'}
            </button>
          </div>
        </div>

        {/* Main Signal */}
        <div className="metric-card mb-8 text-center">
          <div className="text-6xl mb-4">{getSignalEmoji(metrics.signal)}</div>
          <div className={`text-5xl font-bold mb-2 ${getSignalColor(metrics.signal)}`}>
            {metrics.signal}
          </div>
          <div className="text-xl text-gray-400">
            {metrics.deviation < -2 && 'Strong undervaluation - Mean reversion likely'}
            {metrics.deviation > 2 && 'Strong overvaluation - Correction likely'}
            {Math.abs(metrics.deviation) <= 2 && 'Near equilibrium - Range-bound trading'}
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="metric-card">
            <div className="text-sm text-gray-400 mb-1">Price</div>
            <div className="text-2xl font-bold font-mono">
              ${metrics.price.toFixed(4)}
            </div>
          </div>

          <div className="metric-card">
            <div className="text-sm text-gray-400 mb-1">VWAP (Equilibrium)</div>
            <div className="text-2xl font-bold font-mono">
              ${metrics.vwap.toFixed(4)}
            </div>
          </div>

          <div className="metric-card">
            <div className="text-sm text-gray-400 mb-1">Deviation</div>
            <div className={`text-2xl font-bold font-mono ${
              metrics.deviation < -2 ? 'text-oracle-green' :
              metrics.deviation > 2 ? 'text-oracle-red' :
              'text-gray-400'
            }`}>
              {metrics.deviation > 0 ? '+' : ''}{metrics.deviation.toFixed(2)}σ
            </div>
          </div>

          <div className="metric-card">
            <div className="text-sm text-gray-400 mb-1">Volume</div>
            <div className={`text-2xl font-bold font-mono ${
              metrics.volume_ratio > 100 ? 'text-oracle-green' : 'text-gray-400'
            }`}>
              {metrics.volume_ratio.toFixed(0)}%
            </div>
          </div>

          <div className="metric-card">
            <div className="text-sm text-gray-400 mb-1">Trend</div>
            <div className="text-xl font-semibold capitalize">
              {metrics.trend}
            </div>
          </div>

          <div className="metric-card">
            <div className="text-sm text-gray-400 mb-1">Market Regime</div>
            <div className="text-xl font-semibold capitalize">
              {metrics.regime}
            </div>
          </div>

          <div className="metric-card">
            <div className="text-sm text-gray-400 mb-1">Cycle Position</div>
            <div className="text-xl font-semibold capitalize">
              {metrics.cycle_position}
            </div>
          </div>

          <div className="metric-card">
            <div className="text-sm text-gray-400 mb-1">Phase</div>
            <div className="text-xl font-bold font-mono">
              {metrics.phase.toFixed(2)}°
            </div>
          </div>
        </div>

        {/* Professional Analysis */}
        {data.professional_analysis && (
          <div className="metric-card mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              Professional Analysis
              <span className="text-sm text-gray-400 ml-2">
                ({data.analysis_method})
              </span>
            </h2>
            <div className="prose prose-invert max-w-none">
              <pre className="whitespace-pre-wrap text-gray-300 leading-relaxed">
                {data.professional_analysis}
              </pre>
            </div>
          </div>
        )}

        {/* Historical Stats */}
        <div className="metric-card mb-8">
          <h2 className="text-2xl font-semibold mb-4">Historical Statistics</h2>
          <div className="grid md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-400">Total Bars</div>
              <div className="text-2xl font-bold">{historical.bars}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">BUY Signals</div>
              <div className="text-2xl font-bold text-oracle-green">
                {historical.buy_signals} ({((historical.buy_signals / historical.bars) * 100).toFixed(1)}%)
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">SELL Signals</div>
              <div className="text-2xl font-bold text-oracle-red">
                {historical.sell_signals} ({((historical.sell_signals / historical.bars) * 100).toFixed(1)}%)
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">HOLD Signals</div>
              <div className="text-2xl font-bold text-oracle-yellow">
                {historical.hold_signals} ({((historical.hold_signals / historical.bars) * 100).toFixed(1)}%)
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={() => router.push(`/backtest?symbol=${symbol}`)}
            className="btn-primary flex-1"
          >
            Run Backtest
          </button>
          <button
            onClick={() => mutate()}
            className="btn-secondary"
          >
            Refresh
          </button>
        </div>
      </div>
    </main>
  )
}
