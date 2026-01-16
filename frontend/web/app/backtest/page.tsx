'use client'

import { Suspense } from 'react'
import BacktestContent from './content'

export default function BacktestPage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen p-8 bg-gradient-to-br from-oracle-dark via-oracle-darker to-black">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-20">
            <div className="text-4xl mb-4">📊</div>
            <div className="text-xl text-gray-400">Loading backtest...</div>
          </div>
        </div>
      </main>
    }>
      <BacktestContent />
    </Suspense>
  )
}
