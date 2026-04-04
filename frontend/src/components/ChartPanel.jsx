import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, LineSeries } from 'lightweight-charts';
import { useChartStore, useSignalStore } from '../stores';
import { generateMockCandles, mockOrderBlocks, mockFVGs, mockLiquidityZones } from '../data/mockData';
import { Camera, RotateCcw, TrendingUp } from 'lucide-react';

const ChartPanel = () => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const { overlays, toggleOverlay } = useChartStore();
  const { scanning, updateLastAnalyzed } = useSignalStore();
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      layout: {
        background: { color: '#0a0e17' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#1a2235' },
        horzLines: { color: '#1a2235' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: '#3b82f6',
          width: 1,
          style: 0,
        },
        horzLine: {
          color: '#3b82f6',
          width: 1,
          style: 0,
        },
      },
      rightPriceScale: {
        borderColor: '#1e293b',
      },
      timeScale: {
        borderColor: '#1e293b',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10b981',
      downColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    const candles = generateMockCandles(500, 43000);
    candleSeries.setData(candles);

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;

    if (overlays.orderBlocks) {
      mockOrderBlocks.forEach((ob) => {
        const lineSeries = chartRef.current.addSeries(LineSeries, {
          color: 'transparent',
          lineWidth: 0,
          priceLineVisible: false,
          lastValueVisible: false,
        });

        const obData = [
          { time: ob.time_start, value: ob.price_high },
          { time: ob.time_end, value: ob.price_high },
        ];
        lineSeries.setData(obData);

        lineSeries.createPriceLine({
          price: ob.price_high,
          color: ob.type === 'bullish' ? '#10b981' : '#ef4444',
          lineWidth: 1,
          lineStyle: 2,
          axisLabelVisible: true,
        });

        lineSeries.createPriceLine({
          price: ob.price_low,
          color: ob.type === 'bullish' ? '#10b981' : '#ef4444',
          lineWidth: 1,
          lineStyle: 2,
          axisLabelVisible: true,
        });
      });
    }

    if (overlays.liquidity) {
      mockLiquidityZones.forEach((liq) => {
        const lineSeries = chartRef.current.addSeries(LineSeries, {
          color: '#8b5cf6',
          lineWidth: 1,
          lineStyle: 2,
          priceLineVisible: false,
        });

        const currentTime = Date.now() / 1000;
        lineSeries.setData([
          { time: liq.time, value: liq.price },
          { time: currentTime, value: liq.price },
        ]);
      });
    }
  }, [overlays]);

  const handleAnalyze = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      updateLastAnalyzed();
    }, 2000);
  };

  const handleScreenshot = () => {
    console.log('Taking screenshot...');
  };

  const handleResetZoom = () => {
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  };

  return (
    <div className="flex-1 flex flex-col" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Chart Container */}
      <div ref={chartContainerRef} data-testid="trading-chart" className="flex-1 relative">
        {analyzing && (
          <div className="absolute inset-0 flex items-center justify-center z-10" style={{ backgroundColor: 'rgba(10, 14, 23, 0.9)' }}>
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-[var(--accent-blue)] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <div className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Analyzing Market...</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Detecting Order Blocks...</div>
            </div>
          </div>
        )}
      </div>

      {/* Chart Toolbar */}
      <div className="h-10 border-t border-[var(--border)] flex items-center justify-between px-4" style={{ backgroundColor: 'var(--bg-secondary)' }}>
        <div className="flex items-center gap-2">
          {[
            { key: 'orderBlocks', label: 'OB' },
            { key: 'fvgs', label: 'FVG' },
            { key: 'liquidity', label: 'LIQ' },
            { key: 'structure', label: 'BOS' },
            { key: 'sessions', label: 'SESSION' },
            { key: 'levels', label: 'ENTRY' },
            { key: 'htf', label: 'HTF' },
          ].map((overlay) => (
            <button
              key={overlay.key}
              data-testid={`overlay-${overlay.key}`}
              onClick={() => toggleOverlay(overlay.key)}
              className="px-3 py-1 text-xs font-medium rounded transition-colors"
              style={{
                backgroundColor: overlays[overlay.key] ? 'var(--accent-blue)' : 'var(--bg-tertiary)',
                color: overlays[overlay.key] ? 'white' : 'var(--text-secondary)'
              }}
            >
              {overlay.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <button
            data-testid="screenshot-button"
            onClick={handleScreenshot}
            className="p-1.5 rounded hover:bg-[var(--bg-hover)] transition-colors"
            style={{ color: 'var(--text-secondary)' }}
          >
            <Camera className="w-4 h-4" />
          </button>
          <button
            data-testid="reset-zoom-button"
            onClick={handleResetZoom}
            className="p-1.5 rounded hover:bg-[var(--bg-hover)] transition-colors"
            style={{ color: 'var(--text-secondary)' }}
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            data-testid="analyze-button"
            onClick={handleAnalyze}
            disabled={analyzing}
            className="px-4 py-1.5 text-xs font-medium rounded transition-colors flex items-center gap-2"
            style={{
              backgroundColor: 'var(--accent-blue)',
              color: 'white',
              opacity: analyzing ? 0.6 : 1
            }}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            {analyzing ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChartPanel;