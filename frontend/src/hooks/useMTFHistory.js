import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for fetching MTF confluence historical data
 */
export const useMTFHistory = (symbol, options = {}) => {
  const [historyData, setHistoryData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const {
    days = 1,
    htf = null,
    mtf = null,
    ltf = null,
    autoRefresh = false,
    refreshInterval = 60000 // 1 minute
  } = options;

  const fetchHistory = useCallback(async () => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Build query parameters
      const params = new URLSearchParams({ days: days.toString() });
      if (htf) params.append('htf', htf);
      if (mtf) params.append('mtf', mtf);
      if (ltf) params.append('ltf', ltf);
      
      // Fetch history data
      const historyResponse = await fetch(
        `http://localhost:8000/api/mtf/mtf-history/${symbol}?${params}`
      );
      
      if (!historyResponse.ok) {
        throw new Error(`HTTP error! status: ${historyResponse.status}`);
      }
      
      const historyResult = await historyResponse.json();
      setHistoryData(historyResult.history || []);
      
      // Fetch summary data
      const summaryResponse = await fetch(
        `http://localhost:8000/api/mtf/mtf-history-summary/${symbol}?days=${days}`
      );
      
      if (summaryResponse.ok) {
        const summaryResult = await summaryResponse.json();
        setSummary(summaryResult);
      }
      
    } catch (err) {
      console.error('Error fetching MTF history:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [symbol, days, htf, mtf, ltf]);

  // Initial fetch
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(fetchHistory, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchHistory]);

  // Helper functions
  const getHistoryByTimeRange = useCallback((hours) => {
    const cutoffTime = new Date(Date.now() - hours * 60 * 60 * 1000);
    return historyData.filter(entry => 
      new Date(entry.timestamp) >= cutoffTime
    );
  }, [historyData]);

  const getValidSignalsCount = useCallback(() => {
    return historyData.filter(entry => entry.signal_valid).length;
  }, [historyData]);

  const getAverageConfluenceScore = useCallback(() => {
    if (historyData.length === 0) return 0;
    const total = historyData.reduce((sum, entry) => sum + entry.confluence_score, 0);
    return Math.round(total / historyData.length);
  }, [historyData]);

  const getBiasDistribution = useCallback(() => {
    const distribution = { bullish: 0, bearish: 0, neutral: 0 };
    historyData.forEach(entry => {
      distribution[entry.bias] = (distribution[entry.bias] || 0) + 1;
    });
    return distribution;
  }, [historyData]);

  const getLatestEntry = useCallback(() => {
    return historyData.length > 0 ? historyData[0] : null;
  }, [historyData]);

  const getEntriesForTimeframe = useCallback((timeframe) => {
    return historyData.filter(entry => 
      entry.htf === timeframe || entry.mtf === timeframe || entry.ltf === timeframe
    );
  }, [historyData]);

  return {
    // Data
    historyData,
    summary,
    
    // State
    loading,
    error,
    
    // Actions
    refetch: fetchHistory,
    
    // Helper functions
    getHistoryByTimeRange,
    getValidSignalsCount,
    getAverageConfluenceScore,
    getBiasDistribution,
    getLatestEntry,
    getEntriesForTimeframe,
    
    // Computed values
    totalEntries: historyData.length,
    validSignals: getValidSignalsCount(),
    averageScore: getAverageConfluenceScore(),
    biasDistribution: getBiasDistribution(),
    latestEntry: getLatestEntry()
  };
};

export default useMTFHistory;