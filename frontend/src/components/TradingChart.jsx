import React, { useEffect, useRef, useState } from 'react'
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts'
import { useChartStore } from '../stores/chartStore'
import { useSignalStore } from '../stores/signalStore'

const TradingChart = () => {
  const chartContainerRef = useRef()
  const chartRef = useRef()
  const candlestickSeriesRef = useRef()
  
  const { 
    symbol, 
    timeframe, 
    darkMode, 
    chartData, 
    smcLevels,
    showOrderBlocks,
    showFVGs,
    showLiquidityZones,
    showBosChoch,
    showSessionBoxes,
    showHTFLevels
  } = useChartStore()
  
  const { activeSignal } = useSignalStore()
  
  const [isLoading, setIsLoading] = useState(true)

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: darkMode ? '#0a0a0a' : '#ffffff' },
        textColor: darkMode ? '#e5e5e5' : '#333333',
      },
      grid: {
        vertLines: { color: darkMode ? '#2a2a2a' : '#e0e0e0' },
        horzLines: { color: darkMode ? '#2a2a2a' : '#e0e0e0' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: darkMode ? '#64748b' : '#94a3b8',
          width: 1,
          style: 2,
        },
        horzLine: {
          color: darkMode ? '#64748b' : '#94a3b8',
          width: 1,
          style: 2,
        },
      },
      rightPriceScale: {
        borderColor: darkMode ? '#2a2a2a' : '#e0e0e0',
        textColor: darkMode ? '#e5e5e5' : '#333333',
      },
      timeScale: {
        borderColor: darkMode ? '#2a2a2a' : '#e0e0e0',
        textColor: darkMode ? '#e5e5e5' : '#333333',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    })

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#00d4aa',
      downColor: '#ff6b6b',
      borderDownColor: '#ff6b6b',
      borderUpColor: '#00d4aa',
      wickDownColor: '#ff6b6b',
      wickUpColor: '#00d4aa',
    })

    chartRef.current = chart
    candlestickSeriesRef.current = candlestickSeries

    // Generate sample data for demo
    const generateSampleData = () => {
      const data = []
      let price = 45000
      const now = new Date()
      
      for (let i = 100; i >= 0; i--) {
        const time = Math.floor((now.getTime() - i * 60 * 60 * 1000) / 1000)
        const change = (Math.random() - 0.5) * 1000
        price += change
        
        const open = price
        const high = price + Math.random() * 500
        const low = price - Math.random() * 500
        const close = low + Math.random() * (high - low)
        
        data.push({
          time,
          open,
          high,
          low,
          close,
        })
        
        price = close
      }
      
      return data
    }

    const sampleData = generateSampleData()
    candlestickSeries.setData(sampleData)
    setIsLoading(false)

    // Handle resize
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth })
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [darkMode])

  // Update chart data
  useEffect(() => {
    if (!candlestickSeriesRef.current || !chartData.length) return

    try {
      candlestickSeriesRef.current.setData(chartData)
      setIsLoading(false)
    } catch (error) {
      console.error('Error setting chart data:', error)
    }
  }, [chartData])

  // Draw SMC levels
  useEffect(() => {
    if (!chartRef.current) return

    // Clear existing overlays (in a real implementation, you'd track these)
    // For now, we'll just add new ones

    // Order Blocks
    if (showOrderBlocks && smcLevels.orderBlocks) {
      smcLevels.orderBlocks.forEach(ob => {
        try {
          const rectangle = {
            time1: ob.start_time,
            time2: ob.end_time,
            price1: ob.high,
            price2: ob.low,
          }

          // Note: This is a simplified implementation
          // In a real app, you'd use the chart's drawing API properly
          console.log('Drawing Order Block:', rectangle)
        } catch (error) {
          console.error('Error drawing order block:', error)
        }
      })
    }

    // Fair Value Gaps
    if (showFVGs && smcLevels.fvgs) {
      smcLevels.fvgs.forEach(fvg => {
        try {
          console.log('Drawing FVG:', fvg)
        } catch (error) {
          console.error('Error drawing FVG:', error)
        }
      })
    }

    // Liquidity Zones
    if (showLiquidityZones && smcLevels.liquidityZones) {
      smcLevels.liquidityZones.forEach(lz => {
        try {
          console.log('Drawing Liquidity Zone:', lz)
        } catch (error) {
          console.error('Error drawing liquidity zone:', error)
        }
      })
    }

  }, [smcLevels, showOrderBlocks, showFVGs, showLiquidityZones, showBosChoch, showSessionBoxes, showHTFLevels])

  // Draw active signal levels
  useEffect(() => {
    if (!chartRef.current || !activeSignal) return

    try {
      // Draw entry, SL, TP lines
      console.log('Drawing signal levels:', activeSignal)
      
      // In a real implementation, you'd create price lines:
      // const entryLine = candlestickSeriesRef.current.createPriceLine({
      //   price: activeSignal.entry_price,
      //   color: '#3b82f6',
      //   lineWidth: 2,
      //   lineStyle: 0,
      //   axisLabelVisible: true,
      //   title: 'Entry',
      // })
      
    } catch (error) {
      console.error('Error drawing signal levels:', error)
    }
  }, [activeSignal])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full bg-dark-surface">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-bull mx-auto mb-2"></div>
          <p className="text-dark-muted text-sm">Loading chart data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-full">
      {/* Chart container */}
      <div 
        ref={chartContainerRef} 
        className="w-full h-full"
        style={{ minHeight: '400px' }}
      />
      
      {/* Chart overlays */}
      <div className="absolute top-4 left-4 z-10">
        <div className="bg-dark-surface/90 backdrop-blur-sm rounded-lg p-3 border border-dark-border">
          <div className="flex items-center space-x-4">
            <div className="text-dark-text font-mono font-semibold">
              {symbol}
            </div>
            <div className="text-dark-muted text-sm">
              {timeframe.toUpperCase()}
            </div>
            {activeSignal && (
              <div className={`px-2 py-1 rounded text-xs font-medium ${
                activeSignal.direction === 'BUY' 
                  ? 'bg-bull/20 text-bull' 
                  : 'bg-bear/20 text-bear'
              }`}>
                {activeSignal.direction} SIGNAL
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chart controls */}
      <div className="absolute top-4 right-4 z-10">
        <div className="bg-dark-surface/90 backdrop-blur-sm rounded-lg p-2 border border-dark-border">
          <div className="flex space-x-2">
            <button
              onClick={() => useChartStore.getState().toggleOrderBlocks()}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                showOrderBlocks 
                  ? 'bg-bull/20 text-bull' 
                  : 'text-dark-muted hover:text-dark-text'
              }`}
            >
              OB
            </button>
            <button
              onClick={() => useChartStore.getState().toggleFVGs()}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                showFVGs 
                  ? 'bg-bull/20 text-bull' 
                  : 'text-dark-muted hover:text-dark-text'
              }`}
            >
              FVG
            </button>
            <button
              onClick={() => useChartStore.getState().toggleLiquidityZones()}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                showLiquidityZones 
                  ? 'bg-bull/20 text-bull' 
                  : 'text-dark-muted hover:text-dark-text'
              }`}
            >
              LZ
            </button>
            <button
              onClick={() => useChartStore.getState().toggleBosChoch()}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                showBosChoch 
                  ? 'bg-bull/20 text-bull' 
                  : 'text-dark-muted hover:text-dark-text'
              }`}
            >
              BOS
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TradingChart