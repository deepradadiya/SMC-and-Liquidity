import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const fetchData = async (symbol, timeframe) => {
  try {
    const response = await api.get('/data', {
      params: { symbol, timeframe }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch data:', error);
    return null;
  }
};

export const analyzeMarket = async (symbol, timeframe) => {
  try {
    const response = await api.post('/analyze', {
      symbol,
      timeframe
    });
    return response.data;
  } catch (error) {
    console.error('Failed to analyze market:', error);
    return null;
  }
};

export const runBacktest = async (config) => {
  try {
    const response = await api.post('/backtest/run', config);
    return response.data;
  } catch (error) {
    console.error('Failed to run backtest:', error);
    return null;
  }
};

export const fetchSignals = async () => {
  try {
    const response = await api.get('/signals');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch signals:', error);
    return null;
  }
};

export const fetchRiskStatus = async () => {
  try {
    const response = await api.get('/risk/status');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch risk status:', error);
    return null;
  }
};

export default api;