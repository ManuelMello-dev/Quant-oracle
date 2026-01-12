'use client'

import { useState } from 'react'

interface SymbolSearchProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
}

const POPULAR_SYMBOLS = [
  'BTC/USD', 'ETH/USD', 'DOGE/USD', 'SOL/USD', 
  'ADA/USD', 'XRP/USD', 'MATIC/USD', 'AVAX/USD'
]

export default function SymbolSearch({ value, onChange, onSubmit }: SymbolSearchProps) {
  const [showSuggestions, setShowSuggestions] = useState(false)

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSubmit()
      setShowSuggestions(false)
    }
  }

  const handleSelectSymbol = (symbol: string) => {
    onChange(symbol)
    setShowSuggestions(false)
  }

  return (
    <div className="relative">
      <div className="flex gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value.toUpperCase())}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          onKeyPress={handleKeyPress}
          placeholder="Enter symbol (e.g., BTC/USD)"
          className="flex-1 bg-oracle-dark border border-gray-700 rounded-lg px-4 py-3 text-lg focus:outline-none focus:border-oracle-blue transition-colors"
        />
        <button
          onClick={onSubmit}
          className="btn-primary px-8"
        >
          Analyze
        </button>
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-oracle-darker border border-gray-800 rounded-lg overflow-hidden z-10">
          <div className="p-2 text-sm text-gray-400 border-b border-gray-800">
            Popular Symbols
          </div>
          {POPULAR_SYMBOLS.map((symbol) => (
            <button
              key={symbol}
              onClick={() => handleSelectSymbol(symbol)}
              className="w-full text-left px-4 py-2 hover:bg-oracle-dark transition-colors"
            >
              {symbol}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
