/**
 * useLiveMTF — High-confidence MTF signal engine
 * Strategy: Only fire when 4H + 1H + 15M all agree + RSI + EMA confirmation
 * Target: High precision (fewer signals, better quality)
 */
import { useState, useEffect, useRef } from 'react';
import { fetchCandles } from '../services/marketApi';
import { fetchYahooCandles, isIndexSymbol } from '../services/yahooFinance';

// ── Indicators ────────────────────────────────────────────────────────────────

function calcEMA(closes, period) {
  if (closes.length < period) return null;
  const k = 2 / (period + 1);
  let ema = closes.slice(0, period).reduce((a, b) => a + b, 0) / period;
  for (let i = period; i < closes.length; i++) ema = closes[i] * k + ema * (1 - k);
  return ema;
}

function calcRSI(closes, period = 14) {
  if (closes.length < period + 1) return 50;
  let gains = 0, losses = 0;
  for (let i = 1; i <= period; i++) {
    const d = closes[i] - closes[i - 1];
    if (d > 0) gains += d; else losses -= d;
  }
  let ag = gains / period, al = losses / period;
  for (let i = period + 1; i < closes.length; i++) {
    const d = closes[i] - closes[i - 1];
    ag = (ag * (period - 1) + Math.max(d, 0)) / period;
    al = (al * (period - 1) + Math.max(-d, 0)) / period;
  }
  return al === 0 ? 100 : 100 - 100 / (1 + ag / al);
}

function calcATR(candles, period = 14) {
  if (candles.length < period + 1) return 0;
  const trs = candles.slice(1).map((c, i) => Math.max(
    c.high - c.low,
    Math.abs(c.high - candles[i].close),
    Math.abs(c.low  - candles[i].close)
  ));
  return trs.slice(-period).reduce((a, b) => a + b, 0) / period;
}

function calcMACD(closes) {
  const ema12 = calcEMA(closes, 12);
  const ema26 = calcEMA(closes, 26);
  if (!ema12 || !ema26) return { macd: 0, signal: 0, hist: 0 };
  const macd = ema12 - ema26;
  return { macd, hist: macd };
}

// ── Bias analysis per timeframe ───────────────────────────────────────────────

function analyzeBias(candles) {
  if (!candles || candles.length < 50) {
    return { bias: 'NEUTRAL', direction: 'neutral', strength: 0, score: 0 };
  }
  const closes = candles.map(c => c.close);
  const price  = closes[closes.length - 1];
  const prev   = closes[closes.length - 2];

  const ema20  = calcEMA(closes, 20);
  const ema50  = calcEMA(closes, 50);
  const ema200 = calcEMA(closes.slice(-200), Math.min(200, closes.length));
  const rsi    = calcRSI(closes, 14);
  const { hist } = calcMACD(closes);

  let score = 0;
  const reasons = [];

  // EMA stack
  if (ema20 && ema50 && ema20 > ema50)   { score += 2; reasons.push('EMA20>EMA50'); }
  if (ema20 && ema50 && ema20 < ema50)   { score -= 2; }
  if (ema50 && ema200 && ema50 > ema200) { score += 1; reasons.push('EMA50>EMA200'); }
  if (ema50 && ema200 && ema50 < ema200) { score -= 1; }

  // Price vs EMAs
  if (ema20 && price > ema20) { score += 1; reasons.push('Price>EMA20'); }
  if (ema20 && price < ema20) { score -= 1; }
  if (ema50 && price > ema50) { score += 1; }
  if (ema50 && price < ema50) { score -= 1; }

  // RSI
  if (rsi > 55 && rsi < 75) { score += 1; reasons.push(`RSI ${rsi.toFixed(0)}`); }
  if (rsi < 45 && rsi > 25) { score -= 1; }
  if (rsi >= 75) { score -= 1; } // overbought — avoid
  if (rsi <= 25) { score += 1; } // oversold — reversal

  // MACD
  if (hist > 0) { score += 1; reasons.push('MACD+'); }
  if (hist < 0) { score -= 1; }

  // Momentum
  if (price > prev) score += 0.5;
  if (price < prev) score -= 0.5;

  const maxScore = 8;
  const strength = Math.min(Math.abs(score) / maxScore * 100, 100);

  if (score >= 3)  return { bias: 'BULLISH', direction: 'up',      strength: Math.round(strength), score, reasons };
  if (score <= -3) return { bias: 'BEARISH', direction: 'down',    strength: Math.round(strength), score, reasons };
  return              { bias: 'NEUTRAL',  direction: 'neutral', strength: Math.round(strength), score, reasons: [] };
}

// ── High-confidence signal generator ─────────────────────────────────────────

function generateHighConfidenceSignal(candles4h, candles1h, candles15m, symbol) {
  if (!candles4h || !candles1h || !candles15m) return null;

  const bias4h  = analyzeBias(candles4h);
  const bias1h  = analyzeBias(candles1h);
  const bias15m = analyzeBias(candles15m);

  // RULE 1: All 3 timeframes must agree
  const allBull = bias4h.direction === 'up'   && bias1h.direction === 'up'   && bias15m.direction === 'up';
  const allBear = bias4h.direction === 'down' && bias1h.direction === 'down' && bias15m.direction === 'down';

  if (!allBull && !allBear) return null;

  const type = allBull ? 'BUY' : 'SELL';

  // RULE 2: RSI must not be extreme in signal direction
  const closes15m = candles15m.map(c => c.close);
  const rsi15m    = calcRSI(closes15m, 14);
  if (type === 'BUY'  && rsi15m > 75) return null; // overbought — skip
  if (type === 'SELL' && rsi15m < 25) return null; // oversold — skip

  // RULE 3: Price must be on correct side of EMA20 on 15m
  const ema20_15m = calcEMA(closes15m, 20);
  const price     = closes15m[closes15m.length - 1];
  if (type === 'BUY'  && ema20_15m && price < ema20_15m * 0.998) return null;
  if (type === 'SELL' && ema20_15m && price > ema20_15m * 1.002) return null;

  // RULE 4: 4H must have strong score
  if (Math.abs(bias4h.score) < 4) return null;

  // Calculate ATR-based levels
  const atr = calcATR(candles15m, 14);
  const sl  = type === 'BUY'  ? price - atr * 1.5 : price + atr * 1.5;
  const tp  = type === 'BUY'  ? price + atr * 3.0 : price - atr * 3.0;

  // Confidence based on agreement strength
  const totalScore = Math.abs(bias4h.score) + Math.abs(bias1h.score) + Math.abs(bias15m.score);
  const confidence = Math.min(Math.round(totalScore / 24 * 100), 92);

  const reasons = [
    `4H: ${bias4h.bias} (score ${bias4h.score > 0 ? '+' : ''}${bias4h.score.toFixed(1)})`,
    `1H: ${bias1h.bias} (score ${bias1h.score > 0 ? '+' : ''}${bias1h.score.toFixed(1)})`,
    `15M: ${bias15m.bias} (score ${bias15m.score > 0 ? '+' : ''}${bias15m.score.toFixed(1)})`,
    `RSI 15M: ${rsi15m.toFixed(1)}`,
    ...bias4h.reasons.slice(0, 2),
  ];

  return {
    id:              `hc_${Date.now()}`,
    type,
    symbol,
    timeframe:       '15M',
    session:         'Live Analysis',
    timestamp:       Date.now(),
    confluence_score: confidence,
    entry:           +price.toFixed(4),
    stop_loss:       +sl.toFixed(4),
    take_profit:     +tp.toFixed(4),
    risk_reward:     2,
    ml_confidence:   confidence,
    risk_amount:     215,
    risk_percent:    1,
    position_size:   0.005,
    reasons,
  };
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useLiveMTF(symbol, timeframe) {
  const [mtfBias, setMtfBias] = useState([]);
  const [signal,  setSignal]  = useState(null);
  const [loading, setLoading] = useState(true);
  const timerRef = useRef(null);

  const analyze = async () => {
    if (!symbol) return;
    setLoading(true);
    try {
      const fetchFn = isIndexSymbol(symbol)
        ? (interval) => fetchYahooCandles(symbol, interval, 200)
        : (interval) => fetchCandles(symbol, interval, 200);

      // Fetch all timeframes in parallel
      const [r4h, r1h, r15m, r5m] = await Promise.allSettled([
        fetchFn('4h'), fetchFn('1h'), fetchFn('15m'), fetchFn('5m'),
      ]);

      const c4h  = r4h.status  === 'fulfilled' ? r4h.value  : null;
      const c1h  = r1h.status  === 'fulfilled' ? r1h.value  : null;
      const c15m = r15m.status === 'fulfilled' ? r15m.value : null;
      const c5m  = r5m.status  === 'fulfilled' ? r5m.value  : null;

      // Calculate bias for each timeframe
      const b4h  = analyzeBias(c4h);
      const b1h  = analyzeBias(c1h);
      const b15m = analyzeBias(c15m);
      const b5m  = analyzeBias(c5m);

      setMtfBias([
        { timeframe: '4H',  ...b4h  },
        { timeframe: '1H',  ...b1h  },
        { timeframe: '15M', ...b15m },
        { timeframe: '5M',  ...b5m  },
      ]);

      // Generate high-confidence signal
      const sig = generateHighConfidenceSignal(c4h, c1h, c15m, symbol);
      setSignal(sig);

    } catch {
      // keep previous state
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    analyze();
    timerRef.current = setInterval(analyze, 60000);
    return () => clearInterval(timerRef.current);
  }, [symbol, timeframe]); // eslint-disable-line

  return { mtfBias, signal, loading };
}
