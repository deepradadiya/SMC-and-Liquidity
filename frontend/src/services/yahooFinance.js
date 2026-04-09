/**
 * Indian Index candles via local ML API (yfinance backend)
 * Falls back to Stooq daily data if ML API is offline
 */

const ML_API = process.env.REACT_APP_ML_API_URL || 'https://signovax.onrender.com';
const PROXY  = 'https://api.allorigins.win/get?url=';

const STOOQ_TICKERS = { NIFTY50: '^nf', SENSEX: '^bs' };

export function isIndexSymbol(symbol) {
  return symbol === 'NIFTY50' || symbol === 'SENSEX';
}

// ── Primary: ML API (yfinance) ────────────────────────────────────────────────
async function fetchFromMLApi(symbol, interval, limit) {
  const url = `${ML_API}/index-candles?symbol=${symbol}&interval=${interval}&limit=${limit}`;
  const res  = await fetch(url, { signal: AbortSignal.timeout(10000) });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.candles;
}

// ── Fallback: Stooq daily ─────────────────────────────────────────────────────
async function fetchStooqDaily(symbol, limit) {
  const ticker = STOOQ_TICKERS[symbol];
  const url    = `https://stooq.com/q/d/l/?s=${ticker}&i=d`;
  const res    = await fetch(`${PROXY}${encodeURIComponent(url)}`, { signal: AbortSignal.timeout(8000) });
  const json   = await res.json();
  const csv    = json.contents;
  if (!csv || csv.includes('No data')) return null;

  const lines = csv.trim().split('\n').slice(1);
  const candles = lines.map(line => {
    const [date, open, high, low, close, volume] = line.split(',');
    if (!close || isNaN(parseFloat(close))) return null;
    return {
      time:   Math.floor(new Date(date).getTime() / 1000),
      open:   parseFloat(open),
      high:   parseFloat(high),
      low:    parseFloat(low),
      close:  parseFloat(close),
      volume: parseFloat(volume) || 0,
    };
  }).filter(Boolean);

  candles.sort((a, b) => a.time - b.time);
  return candles.slice(-limit);
}

// ── Main export ───────────────────────────────────────────────────────────────
export async function fetchYahooCandles(symbol, interval = '15m', limit = 300) {
  // Try ML API first (fast, accurate, real intraday)
  try {
    const candles = await fetchFromMLApi(symbol, interval, limit);
    if (candles && candles.length > 0) return candles;
  } catch { /* fall through to Stooq */ }

  // Fallback: Stooq daily (slower, daily only)
  try {
    return await fetchStooqDaily(symbol, limit);
  } catch {
    return null;
  }
}
