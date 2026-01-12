'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import SymbolSearch from '@/components/SymbolSearch'
import WatchlistPreview from '@/components/WatchlistPreview'

export default function Home() {
  const router = useRouter()
  const [selectedSymbol, setSelectedSymbol] = useState('')

  const handleAnalyze = () => {
    if (selectedSymbol) {
      router.push(`/analyze/${selectedSymbol.replace('/', '-')}`)
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-oracle-blue to-purple-500 bg-clip-text text-transparent">
            Quant Oracle
          </h1>
          <p className="text-xl text-gray-400">
            Professional Trading Analysis Powered by Quantitative Algorithms
          </p>
        </div>

        {/* Main Search */}
        <div className="metric-card max-w-2xl mx-auto mb-12">
          <h2 className="text-2xl font-semibold mb-4">Analyze Symbol</h2>
          <SymbolSearch 
            value={selectedSymbol}
            onChange={setSelectedSymbol}
            onSubmit={handleAnalyze}
          />
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="metric-card">
            <div className="text-3xl mb-2">📊</div>
            <h3 className="text-xl font-semibold mb-2">VWAP Analysis</h3>
            <p className="text-gray-400">
              Volume-weighted equilibrium detection with statistical deviation analysis
            </p>
          </div>

          <div className="metric-card">
            <div className="text-3xl mb-2">🔮</div>
            <h3 className="text-xl font-semibold mb-2">FFT Prediction</h3>
            <p className="text-gray-400">
              Cycle detection and phase analysis for timing predictions
            </p>
          </div>

          <div className="metric-card">
            <div className="text-3xl mb-2">🤖</div>
            <h3 className="text-xl font-semibold mb-2">AI Analysis</h3>
            <p className="text-gray-400">
              Professional insights powered by local LLM (Premium)
            </p>
          </div>

          <div className="metric-card">
            <div className="text-3xl mb-2">📈</div>
            <h3 className="text-xl font-semibold mb-2">Backtesting</h3>
            <p className="text-gray-400">
              Historical performance validation with 71.4% win rate
            </p>
          </div>

          <div className="metric-card">
            <div className="text-3xl mb-2">⏱️</div>
            <h3 className="text-xl font-semibold mb-2">Multi-Timeframe</h3>
            <p className="text-gray-400">
              Cross-timeframe confluence for higher confidence signals
            </p>
          </div>

          <div className="metric-card">
            <div className="text-3xl mb-2">🎯</div>
            <h3 className="text-xl font-semibold mb-2">Mean Reversion</h3>
            <p className="text-gray-400">
              Extreme deviation signals for high-probability setups
            </p>
          </div>
        </div>

        {/* Watchlist Preview */}
        <WatchlistPreview />

        {/* Quick Links */}
        <div className="flex justify-center gap-4 mt-12">
          <button 
            onClick={() => router.push('/backtest')}
            className="btn-secondary"
          >
            Run Backtest
          </button>
          <button 
            onClick={() => router.push('/watchlist')}
            className="btn-secondary"
          >
            View Watchlist
          </button>
        </div>
      </div>
    </main>
  )
}
