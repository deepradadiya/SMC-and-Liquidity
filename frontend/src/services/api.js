import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Market Data API
export const marketDataAPI = {
  getOHLCV: (symbol, timeframe = '1h', limit = 500) =>
    api.get(`/data/ohlcv?symbol=${symbol}&timeframe=${timeframe}&limit=${limit}`),
  
  getSymbols: () =>
    api.get('/data/symbols'),
  
  getTimeframes: () =>
    api.get('/data/timeframes'),
}

// Analysis API
export const analysisAPI = {
  analyzeSMC: (symbol, timeframe = '1h', limit = 500) =>
    api.post('/analysis/smc', { symbol, timeframe, limit }),
  
  getPatternSummary: (symbol, timeframe = '1h') =>
    api.get(`/analysis/patterns/${symbol}?timeframe=${timeframe}`),
}

// Signals API
export const signalsAPI = {
  generateSignals: (symbol, timeframe = '1h', minConfidence = 70.0) =>
    api.post('/signals/generate', { symbol, timeframe, min_confidence: minConfidence }),
  
  getActiveSignals: (symbol, timeframe = '1h', limit = 10) =>
    api.get(`/signals/active/${symbol}?timeframe=${timeframe}&limit=${limit}`),
  
  getSignalsSummary: () =>
    api.get('/signals/summary'),
}

// Backtest API
export const backtestAPI = {
  runBacktest: (symbol, timeframe = '1h', startDate = null, endDate = null, initialCapital = 10000) =>
    api.post('/backtest/run', {
      symbol,
      timeframe,
      start_date: startDate,
      end_date: endDate,
      initial_capital: initialCapital,
    }),
  
  quickBacktest: (symbol, timeframe = '1h', days = 30) =>
    api.get(`/backtest/quick/${symbol}?timeframe=${timeframe}&days=${days}`),
  
  getPerformanceMetrics: (symbol, timeframe = '1h') =>
    api.get(`/backtest/performance/${symbol}?timeframe=${timeframe}`),
}

// Health check
export const healthAPI = {
  check: () => api.get('/health', { baseURL: 'http://localhost:8000' }),
}

export default api