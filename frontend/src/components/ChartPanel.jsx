import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, CandlestickSeries, LineSeries } from 'lightweight-charts';
import { useChartStore } from '../stores/chartStore';
import { useSignalStore } from '../stores';
import { usePriceStore } from '../stores/priceStore';
import { fetchCandles, fetchLiveSignal } from '../services/marketApi';
import { fetchYahooCandles, isIndexSymbol } from '../services/yahooFinance';
import { generateMockCandles } from '../data/mockData';
import { Camera, RotateCcw, TrendingUp, Wifi, WifiOff } from 'lucide-react';

const TF_MAP = { '1m':'1m', '5m':'5m', '15m':'15m', '1h':'1h', '4h':'4h', '1D':'1d' };

const ChartPanel = () => {
  const chartContainerRef = useRef(null);
  const chartRef          = useRef(null);
  const candleSeriesRef   = useRef(null);
  const overlaySeriesRef  = useRef([]);
  const candleBufferRef   = useRef([]);
  const klineWsRef        = useRef(null);

  const {
    symbol, timeframe,
    showOrderBlocks, showFVGs, showLiquidityZones,
    showBosChoch, showSessionBoxes, showHTFLevels,
    toggleOrderBlocks, toggleFVGs, toggleLiquidityZones,
    toggleBosChoch, toggleSessionBoxes, toggleHTFLevels,
  } = useChartStore();

  const { updateLastAnalyzed } = useSignalStore();
  const { prices } = usePriceStore();

  const [loading,   setLoading]   = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [signalData, setSignalData] = useState(null);
  const [wsLive,    setWsLive]    = useState(false);

  const binanceInterval = TF_MAP[timeframe] || '15m';
  const isIndex = isIndexSymbol(symbol);

  // ── 1. Init chart once ───────────────────────────────────────────────────
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width:  chartContainerRef.current.clientWidth || 800,
      height: chartContainerRef.current.clientHeight || 500,
      layout: { background: { color: '#0a0e17' }, textColor: '#94a3b8' },
      grid:   { vertLines: { color: '#1a2235' }, horzLines: { color: '#1a2235' } },
      crosshair: {
        mode: 1,
        vertLine: { color: '#3b82f6', width: 1, style: 0 },
        horzLine: { color: '#3b82f6', width: 1, style: 0 },
      },
      rightPriceScale: { borderColor: '#1e293b' },
      timeScale: { borderColor: '#1e293b', timeVisible: true, secondsVisible: false },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: '#10b981', downColor: '#ef4444',
      wickUpColor: '#10b981', wickDownColor: '#ef4444',
    });

    chartRef.current        = chart;
    candleSeriesRef.current = series;

    const ro = new ResizeObserver(() => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width:  chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    });
    ro.observe(chartContainerRef.current);

    return () => {
      ro.disconnect();
      chartRef.current?.remove();
      chartRef.current        = null;
      candleSeriesRef.current = null;
    };
  }, []);

  // ── 2. Load candles on symbol/timeframe change ───────────────────────────
  const loadHistory = useCallback(async () => {
    setLoading(true);
    setSignalData(null);
    if (candleSeriesRef.current) {
      try { candleSeriesRef.current.setData([]); } catch (_) {}
    }
    candleBufferRef.current = [];

    try {
      const candles = isIndex
        ? await fetchYahooCandles(symbol, binanceInterval, 500)
        : await fetchCandles(symbol, binanceInterval, 500);

      if (!candles || candles.length === 0) throw new Error('No data');
      candles.sort((a, b) => a.time - b.time);
      candleBufferRef.current = candles;
      if (candleSeriesRef.current) {
        candleSeriesRef.current.setData(candles);
        chartRef.current?.timeScale().fitContent();
      }
    } catch {
      const fallback = isIndex
        ? (symbol === 'NIFTY50' ? 23775 : 76632)
        : (prices[symbol]?.price || 67000);
      const mock = generateMockCandles(300, fallback);
      candleBufferRef.current = mock;
      if (candleSeriesRef.current) {
        candleSeriesRef.current.setData(mock);
        chartRef.current?.timeScale().fitContent();
      }
    } finally {
      setLoading(false);
    }
  }, [symbol, binanceInterval, isIndex]); // eslint-disable-line

  useEffect(() => {
    const t = setTimeout(loadHistory, 50);
    return () => clearTimeout(t);
  }, [loadHistory]);

  // ── 3. Kline WebSocket (crypto only) ────────────────────────────────────
  useEffect(() => {
    if (klineWsRef.current) {
      klineWsRef.current.onclose = null;
      klineWsRef.current.close();
      klineWsRef.current = null;
    }
    setWsLive(false);
    if (isIndex) return;

    const url = `wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@kline_${binanceInterval}`;
    let alive = true;
    let reconnectTimer = null;

    const connect = () => {
      if (!alive) return;
      const ws = new WebSocket(url);
      klineWsRef.current = ws;
      ws.onopen  = () => { if (alive) setWsLive(true); };
      ws.onerror = () => {};
      ws.onclose = () => {
        if (!alive) return;
        setWsLive(false);
        reconnectTimer = setTimeout(connect, 3000);
      };
      ws.onmessage = (evt) => {
        if (!alive || !candleSeriesRef.current) return;
        try {
          const k = JSON.parse(evt.data).k;
          if (!k) return;
          const candle = {
            time:  Math.floor(k.t / 1000),
            open:  parseFloat(k.o), high: parseFloat(k.h),
            low:   parseFloat(k.l), close: parseFloat(k.c),
          };
          const buf = candleBufferRef.current;
          if (!buf.length) return;
          const last = buf[buf.length - 1];
          if (candle.time === last.time) {
            const u = { ...candle, open: last.open, high: Math.max(last.high, candle.high), low: Math.min(last.low, candle.low) };
            buf[buf.length - 1] = u;
            candleSeriesRef.current.update(u);
          } else if (candle.time > last.time) {
            buf.push(candle);
            if (buf.length > 1000) buf.shift();
            candleSeriesRef.current.update(candle);
          }
        } catch { /* ignore */ }
      };
    };

    connect();
    return () => {
      alive = false;
      clearTimeout(reconnectTimer);
      if (klineWsRef.current) { klineWsRef.current.onclose = null; klineWsRef.current.close(); }
    };
  }, [symbol, binanceInterval, isIndex]);

  // ── 4. Overlays ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!chartRef.current) return;
    overlaySeriesRef.current.forEach(s => { try { chartRef.current.removeSeries(s); } catch (_) {} });
    overlaySeriesRef.current = [];

    if (signalData && signalData.signal !== 'HOLD') {
      const now = Math.floor(Date.now() / 1000);
      const past = now - 3600;
      [
        { price: signalData.currentPrice, color: signalData.signal === 'BUY' ? '#10b981' : '#ef4444', title: `${signalData.signal}` },
        { price: signalData.stopLoss,     color: '#ef4444', title: 'SL' },
        { price: signalData.takeProfit,   color: '#10b981', title: 'TP' },
      ].filter(l => l.price).forEach(level => {
        try {
          const s = chartRef.current.addSeries(LineSeries, { color: 'transparent', lineWidth: 0, priceLineVisible: false, lastValueVisible: false });
          s.setData([{ time: past, value: level.price }, { time: now, value: level.price }]);
          s.createPriceLine({ price: level.price, color: level.color, lineWidth: 2, lineStyle: 0, axisLabelVisible: true, title: level.title });
          overlaySeriesRef.current.push(s);
        } catch (_) {}
      });
    }
  }, [signalData, showOrderBlocks, showFVGs, showLiquidityZones, showBosChoch, showSessionBoxes, showHTFLevels]);

  // ── 5. Analyze ───────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const result = await fetchLiveSignal(symbol, binanceInterval);
      setSignalData(result);
      updateLastAnalyzed();
    } catch { /* ignore */ } finally {
      setAnalyzing(false);
    }
  };

  const livePrice = prices[symbol]?.price;

  return (
    <div className="flex-1 flex flex-col" style={{ backgroundColor: 'var(--bg-primary)' }}>

      {/* Signal banner */}
      {signalData && (
        <div style={{
          display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 10, padding: '5px 14px',
          backgroundColor: signalData.signal === 'BUY' ? '#052e16' : signalData.signal === 'SELL' ? '#450a0a' : '#1c1917',
          borderBottom: `2px solid ${signalData.signal === 'BUY' ? '#10b981' : signalData.signal === 'SELL' ? '#ef4444' : '#78716c'}`,
        }}>
          <span style={{
            fontWeight: 800, fontSize: 12, letterSpacing: 1, padding: '2px 10px', borderRadius: 4,
            backgroundColor: signalData.signal === 'BUY' ? '#10b981' : signalData.signal === 'SELL' ? '#ef4444' : '#78716c',
            color: '#fff',
          }}>
            {signalData.signal === 'BUY' ? '▲ BUY' : signalData.signal === 'SELL' ? '▼ SELL' : '◆ HOLD'}
          </span>
          {[
            ['Conf', `${signalData.confidence}%`],
            ...(signalData.signal !== 'HOLD' ? [
              ['SL', `${Number(signalData.stopLoss || 0).toLocaleString()}`],
              ['TP', `${Number(signalData.takeProfit || 0).toLocaleString()}`],
              ['R:R', '1:2'],
            ] : []),
          ].map(([label, val]) => (
            <span key={label} style={{ fontSize: 11, color: '#94a3b8' }}>
              {label}: <b style={{ color: '#f1f5f9' }}>{val}</b>
            </span>
          ))}
          <button onClick={() => setSignalData(null)}
            style={{ marginLeft: 'auto', color: '#64748b', background: 'none', border: 'none', cursor: 'pointer', fontSize: 15 }}>
            ✕
          </button>
        </div>
      )}

      {/* Chart */}
      <div ref={chartContainerRef} className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center z-10"
            style={{ backgroundColor: 'rgba(10,14,23,0.85)' }}>
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <div style={{ color: '#f1f5f9', fontSize: 12 }}>Loading {symbol} {timeframe}...</div>
              {isIndex && <div style={{ color: '#64748b', fontSize: 10, marginTop: 4 }}>Fetching from yfinance backend...</div>}
            </div>
          </div>
        )}

        {!isIndex && !loading && livePrice && (
          <div className="absolute top-3 left-3 z-10 px-3 py-1 rounded text-xs font-bold"
            style={{ backgroundColor: '#0f172a', border: `1px solid ${wsLive ? '#10b981' : '#f59e0b'}`, color: wsLive ? '#10b981' : '#f59e0b' }}>
            {wsLive ? '⚡ LIVE' : '○ REST'} ${Number(livePrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        )}

        {!isIndex && !loading && (
          <div className="absolute top-3 right-3 z-10 flex items-center gap-1.5 px-2 py-1 rounded text-xs"
            style={{ backgroundColor: '#0f172a', border: `1px solid ${wsLive ? '#10b981' : '#3b82f6'}` }}>
            {wsLive
              ? <><Wifi className="w-3 h-3" style={{ color: '#10b981' }} /><span style={{ color: '#10b981' }}>WebSocket Live</span></>
              : <><WifiOff className="w-3 h-3" style={{ color: '#3b82f6' }} /><span style={{ color: '#3b82f6' }}>Connecting...</span></>
            }
          </div>
        )}

        {isIndex && !loading && (
          <div className="absolute top-3 left-3 z-10 px-3 py-1 rounded text-xs font-bold"
            style={{ backgroundColor: '#0f172a', border: '1px solid #f59e0b', color: '#f59e0b' }}>
            🇮🇳 {symbol === 'NIFTY50' ? 'NIFTY 50' : 'SENSEX'} · Daily Data
          </div>
        )}
      </div>

      {/* Toolbar */}
      <div className="h-10 border-t border-[var(--border)] flex items-center justify-between px-4"
        style={{ backgroundColor: 'var(--bg-secondary)' }}>
        <div className="flex items-center gap-2">
          {[
            { key: 'ob',  label: 'OB',      active: showOrderBlocks,    toggle: toggleOrderBlocks },
            { key: 'fvg', label: 'FVG',     active: showFVGs,           toggle: toggleFVGs },
            { key: 'liq', label: 'LIQ',     active: showLiquidityZones, toggle: toggleLiquidityZones },
            { key: 'bos', label: 'BOS',     active: showBosChoch,       toggle: toggleBosChoch },
            { key: 'ses', label: 'SESSION', active: showSessionBoxes,   toggle: toggleSessionBoxes },
            { key: 'htf', label: 'HTF',     active: showHTFLevels,      toggle: toggleHTFLevels },
          ].map(o => (
            <button key={o.key} onClick={o.toggle}
              className="px-3 py-1 text-xs font-medium rounded transition-colors"
              style={{ backgroundColor: o.active ? 'var(--accent-blue)' : 'var(--bg-tertiary)', color: o.active ? 'white' : 'var(--text-secondary)' }}>
              {o.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => { const c = chartContainerRef.current?.querySelector('canvas'); if (!c) return; const a = document.createElement('a'); a.download = `${symbol}.png`; a.href = c.toDataURL(); a.click(); }}
            className="p-1.5 rounded hover:bg-[var(--bg-hover)]" style={{ color: 'var(--text-secondary)' }}>
            <Camera className="w-4 h-4" />
          </button>
          <button onClick={() => chartRef.current?.timeScale().fitContent()}
            className="p-1.5 rounded hover:bg-[var(--bg-hover)]" style={{ color: 'var(--text-secondary)' }}>
            <RotateCcw className="w-4 h-4" />
          </button>
          <button onClick={handleAnalyze} disabled={analyzing}
            className="px-4 py-1.5 text-xs font-medium rounded flex items-center gap-2"
            style={{ backgroundColor: 'var(--accent-blue)', color: 'white', opacity: analyzing ? 0.6 : 1 }}>
            <TrendingUp className="w-3.5 h-3.5" />
            {analyzing ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChartPanel;
