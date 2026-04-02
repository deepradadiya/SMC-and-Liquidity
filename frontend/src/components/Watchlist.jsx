import React, { useState, useEffect } from 'react'
import { Plus, X, TrendingUp, TrendingDown, ChevronLeft, ChevronRight } from 'lucide-react'
import { useChartStore } from '../stores/chartStore'

const Watchlist = ({ isCollapsed, onToggleCollapse }) => {
  const { symbol, setSymbol } = useChartStore()
  const [watchedSymbols, setWatchedSymbols] = useState([
    'BTCUSDT',
    'ETHUSDT',
    'ADAUSDT',
    'SOLUSDT',
    'DOTUSDT',
    'LINKUSDT'
  ])
  const [newSymbol, setNewSymbol] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [priceData, setPriceData] = useState({})

  // Mock price data - in real app, this would come from WebSocket
  useEffect(() => {
    const generateMockPrices = () => {
      const mockData = {}
      watchedSymbols.forEach(sym => {
        const basePrice = {
          'BTCUSDT': 45000,
          'ETHUSDT': 2800,
          'ADAUSDT': 0.45,
          'SOLUSDT': 95,
          'DOTUSDT': 7.2,
          'LINKUSDT': 15.8
        }[sym] || 100

        const change = (Math.random() - 0.5) * 10 // -5% to +5%
        const price = basePrice * (1 + change / 100)
        
        mockData[sym] = {
          price: price,
          change: change,
          volume: Math.random() * 1000000,
          sparkline: Array.from({ length: 7 }, () => 
            basePrice * (1 + (Math.random() - 0.5) * 0.1)
          )
        }
      })
      setPriceData(mockData)
    }

    generateMockPrices()
    const interval = setInterval(generateMockPrices, 5000) // Update every 5 seconds

    return () => clearInterval(interval)
  }, [watchedSymbols])

  const addSymbol = () => {
    if (newSymbol && !watchedSymbols.includes(newSymbol.toUpperCase())) {
      setWatchedSymbols([...watchedSymbols, newSymbol.toUpperCase()])
      setNewSymbol('')
      setShowAddForm(false)
    }
  }

  const removeSymbol = (symbolToRemove) => {
    setWatchedSymbols(watchedSymbols.filter(s => s !== symbolToRemove))
  }

  const selectSymbol = (selectedSymbol) => {
    setSymbol(selectedSymbol)
  }

  const formatPrice = (price, symbol) => {
    if (!price) return '0.00'
    
    // Different decimal places for different assets
    const decimals = symbol.includes('USDT') ? 
      (price < 1 ? 4 : price < 100 ? 2 : 0) : 2
    
    return price.toFixed(decimals)
  }

  const formatVolume = (volume) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`
    }
    return volume.toFixed(0)
  }

  const MiniSparkline = ({ data, isPositive }) => {
    if (!data || data.length === 0) return null

    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * 40
      const y = range === 0 ? 10 : 20 - ((value - min) / range) * 20
      return `${x},${y}`
    }).join(' ')

    return (
      <svg width="40" height="20" className="overflow-visible">
        <polyline
          points={points}
          fill="none"
          stroke={isPositive ? '#00d4aa' : '#ff6b6b'}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    )
  }

  if (isCollapsed) {
    return (
      <div className="w-12 bg-dark-surface border-r border-dark-border flex flex-col">
        <div className="p-3 border-b border-dark-border">
          <button
            onClick={onToggleCollapse}
            className="w-full flex items-center justify-center text-dark-muted hover:text-dark-text transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <div className="space-y-2 p-2">
            {watchedSymbols.map((sym) => {
              const data = priceData[sym]
              const isActive = sym === symbol
              const isPositive = data?.change >= 0
              
              return (
                <button
                  key={sym}
                  onClick={() => selectSymbol(sym)}
                  className={`w-full p-2 rounded text-xs transition-colors ${
                    isActive
                      ? 'bg-bull/20 text-bull border border-bull/30'
                      : 'text-dark-muted hover:text-dark-text hover:bg-dark-bg'
                  }`}
                >
                  <div className="font-mono">
                    {sym.replace('USDT', '')}
                  </div>
                  {data && (
                    <div className={`text-xs mt-1 ${
                      isPositive ? 'text-bull' : 'text-bear'
                    }`}>
                      {isPositive ? '+' : ''}{data.change.toFixed(1)}%
                    </div>
                  )}
                </button>
              )
            })}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-64 bg-dark-surface border-r border-dark-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-dark-border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-dark-text font-semibold">Watchlist</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="text-dark-muted hover:text-dark-text transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
            <button
              onClick={onToggleCollapse}
              className="text-dark-muted hover:text-dark-text transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Add Symbol Form */}
        {showAddForm && (
          <div className="space-y-2">
            <input
              type="text"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              placeholder="Enter symbol (e.g., BTCUSDT)"
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded text-dark-text text-sm focus:outline-none focus:border-bull"
              onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
            />
            <div className="flex space-x-2">
              <button
                onClick={addSymbol}
                className="flex-1 px-3 py-1 bg-bull/20 text-bull rounded text-xs hover:bg-bull/30 transition-colors"
              >
                Add
              </button>
              <button
                onClick={() => {
                  setShowAddForm(false)
                  setNewSymbol('')
                }}
                className="flex-1 px-3 py-1 bg-dark-border text-dark-muted rounded text-xs hover:bg-dark-border/80 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Symbol List */}
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-1 p-2">
          {watchedSymbols.map((sym) => {
            const data = priceData[sym]
            const isActive = sym === symbol
            const isPositive = data?.change >= 0
            
            return (
              <div
                key={sym}
                className={`relative group rounded-lg border transition-all ${
                  isActive
                    ? 'bg-bull/10 border-bull/30'
                    : 'bg-dark-bg border-dark-border hover:border-dark-border/60'
                }`}
              >
                <button
                  onClick={() => selectSymbol(sym)}
                  className="w-full p-3 text-left"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-mono font-semibold text-dark-text">
                      {sym}
                    </div>
                    <div className="flex items-center space-x-1">
                      {data?.change !== undefined && (
                        <>
                          {isPositive ? (
                            <TrendingUp className="w-3 h-3 text-bull" />
                          ) : (
                            <TrendingDown className="w-3 h-3 text-bear" />
                          )}
                        </>
                      )}
                    </div>
                  </div>

                  {data && (
                    <>
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-dark-text font-medium">
                          ${formatPrice(data.price, sym)}
                        </div>
                        <div className={`text-sm ${
                          isPositive ? 'text-bull' : 'text-bear'
                        }`}>
                          {isPositive ? '+' : ''}{data.change.toFixed(2)}%
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="text-xs text-dark-muted">
                          Vol: {formatVolume(data.volume)}
                        </div>
                        <div className="flex items-center">
                          <MiniSparkline data={data.sparkline} isPositive={isPositive} />
                        </div>
                      </div>
                    </>
                  )}
                </button>

                {/* Remove button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    removeSymbol(sym)
                  }}
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-dark-muted hover:text-bear transition-all"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            )
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-dark-border">
        <div className="flex items-center justify-between text-xs text-dark-muted">
          <span>{watchedSymbols.length} symbols</span>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-bull rounded-full animate-pulse"></div>
            <span>Live</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Watchlist