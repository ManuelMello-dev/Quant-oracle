'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'

interface WatchlistItem {
  symbol: string
  price: number
  deviation: number
  signal: string
  volume_ratio: number
  trend: string
  error?: string
}

export default function WatchlistPreview() {
  const router = useRouter()
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWatchlist()
  }, [])

  const loadWatchlist = async () => {
    try {
      // Load from localStorage
      const saved = localStorage.getItem('watchlist')
      const symbols = saved ? JSON.parse(saved) : ['BTC/USD', 'ETH/USD', 'DOGE/USD']

      // Fetch data for all symbols
      const response = await api.batchAnalyze(symbols)
      setWatchlist(response.results)
    } catch (error) {
      console.error('Failed to load watchlist:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-oracle-green'
      case 'SELL': return 'text-oracle-red'
      default: return 'text-oracle-yellow'
    }
  }

  const getDeviationColor = (deviation: number) => {
    if (deviation < -2) return 'text-oracle-green'
    if (deviation > 2) return 'text-oracle-red'
    return 'text-gray-400'
  }

  if (loading) {
    return (
      <div className="metric-card">
        <h2 className="text-2xl font-semibold mb-4">Watchlist</h2>
        <div className="text-center py-8 text-gray-400">Loading...</div>
      </div>
    )
  }

  return (
    <div className="metric-card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">Watchlist</h2>
        <button
          onClick={() => router.push('/watchlist')}
          className="text-oracle-blue hover:underline"
        >
          View All
        </button>
      </div>

      <div className="space-y-3">
        {watchlist.map((item) => (
          <div
            key={item.symbol}
            onClick={() => router.push(`/analyze/${item.symbol.replace('/', '-')}`)}
            className="bg-oracle-dark rounded-lg p-4 cursor-pointer hover:bg-opacity-80 transition-all"
          >
            {item.error ? (
              <div className="text-red-400">
                {item.symbol}: {item.error}
              </div>
            ) : (
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-semibold text-lg">{item.symbol}</div>
                  <div className="text-sm text-gray-400">
                    ${item.price.toFixed(4)} • {item.trend}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${getSignalColor(item.signal)}`}>
                    {item.signal}
                  </div>
                  <div className={`text-sm ${getDeviationColor(item.deviation)}`}>
                    {item.deviation > 0 ? '+' : ''}{item.deviation.toFixed(2)}σ
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {watchlist.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          No symbols in watchlist. Add some to get started!
        </div>
      )}
    </div>
  )
}
