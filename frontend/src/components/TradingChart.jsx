import React, { useEffect, useRef, useState } from 'react'
import { createChart, ColorType } from 'lightweight-charts'

const TradingChart = ({ data, smcAnalysis, className = '' }) => {
  const chartContainerRef = useRef()
  const chartRef = useRef()
  const candlestickSeriesRef = useRef()
  
  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'white' },
        textColor: '#333',
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#cccccc',
      },
      timeScale: {
        borderColor: '#cccccc',
        timeVisible: true,
        secondsVisible: false,
      },
    })

    chartRef.current = chart

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    candlestickSeriesRef.current = candlestickSeries

    // Handle resize
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth })
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  useEffect(() => {
    if (!candlestickSeriesRef.current || !data) return

    // Convert data to lightweight-charts format
    const chartData = data.map(candle => ({
      time: new Date(candle.timestamp).getTime() / 1000,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
    }))

    candlestickSeriesRef.current.setData(chartData)
  }, [data])

  useEffect(() => {
    if (!chartRef.current || !smcAnalysis) return

    // Add SMC overlays
    addSMCOverlays(chartRef.current, smcAnalysis)
  }, [smcAnalysis])

  const addSMCOverlays = (chart, analysis) => {
    // Add liquidity zones as horizontal lines
    analysis.liquidity_zones?.forEach(zone => {
      const line = chart.addLineSeries({
        color: zone.zone_type === 'support' ? '#26a69a' : '#ef5350',
        lineWidth: 2,
        lineStyle: 1, // Dashed
        title: `${zone.zone_type} - ${zone.level}`,
      })
      
      line.setData([
        { time: new Date(zone.timestamp).getTime() / 1000, value: zone.level }
      ])
    })

    // Add order blocks as rectangles (simplified as lines for now)
    analysis.order_blocks?.forEach(block => {
      const highLine = chart.addLineSeries({
        color: block.block_type === 'bullish' ? '#26a69a80' : '#ef535080',
        lineWidth: 1,
        title: `${block.block_type} OB High`,
      })
      
      const lowLine = chart.addLineSeries({
        color: block.block_type === 'bullish' ? '#26a69a80' : '#ef535080',
        lineWidth: 1,
        title: `${block.block_type} OB Low`,
      })
      
      const timestamp = new Date(block.timestamp).getTime() / 1000
      highLine.setData([{ time: timestamp, value: block.high }])
      lowLine.setData([{ time: timestamp, value: block.low }])
    })

    // Add Fair Value Gaps
    analysis.fair_value_gaps?.forEach(fvg => {
      const topLine = chart.addLineSeries({
        color: fvg.gap_type === 'bullish' ? '#2196f380' : '#ff980080',
        lineWidth: 2,
        title: `${fvg.gap_type} FVG`,
      })
      
      const bottomLine = chart.addLineSeries({
        color: fvg.gap_type === 'bullish' ? '#2196f380' : '#ff980080',
        lineWidth: 2,
        title: `${fvg.gap_type} FVG`,
      })
      
      const timestamp = new Date(fvg.timestamp).getTime() / 1000
      topLine.setData([{ time: timestamp, value: fvg.top }])
      bottomLine.setData([{ time: timestamp, value: fvg.bottom }])
    })
  }

  return (
    <div className={`relative ${className}`}>
      <div ref={chartContainerRef} className="w-full h-96" />
      
      {/* Legend */}
      <div className="absolute top-2 left-2 bg-white bg-opacity-90 p-2 rounded text-xs">
        <div className="flex flex-col space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-green-500"></div>
            <span>Support/Bullish</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-red-500"></div>
            <span>Resistance/Bearish</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-blue-400"></div>
            <span>Fair Value Gap</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TradingChart