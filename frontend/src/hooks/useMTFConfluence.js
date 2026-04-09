import { useState, useEffect, useCallback } from 'react';
import { analyzeMTFConfluence, getMTFStatus } from '../services/api';

/**
 * React hook for MTF Confluence analysis
 * Provides easy integration with Module 1 backend
 */
export const useMTFConfluence = (symbol, timeframes = {}) => {
  const [mtfData, setMTFData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Default timeframes
  const defaultTimeframes = {
    ltf: "5m",
    mtf: "1h", 
    htf: "4h",
    ...timeframes
  };

  const analyzeMTF = useCallback(async () => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await analyzeMTFConfluence(
        symbol,
        defaultTimeframes.ltf,
        defaultTimeframes.htf,
        defaultTimeframes.mtf
      );
      
      if (result) {
        // Transform backend data for UI components
        const transformedData = {
          ...result,
          // Add UI-specific properties
          signalType: result.bias === 'bullish' ? 'BUY' : 
                     result.bias === 'bearish' ? 'SELL' : 'NONE',
          riskReward: result.entry && result.stop_loss && result.take_profit ? 
                     Math.abs(result.take_profit - result.entry) / Math.abs(result.entry - result.stop_loss) : 0,
          // Professional status messaging
          statusMessage: result.confluence_score < 60 ? 
            `Analyzing market... Confidence score: ${result.confluence_score}/100. Next analysis in ${result.next_analysis_in || 5} minutes.` :
            `Signal ready with ${result.confluence_score}/100 confidence`,
          // MTF Bias data for UI
          mtfBias: [
            {
              timeframe: defaultTimeframes.htf.toUpperCase(),
              bias: result.htf_analysis?.bias?.toUpperCase() || 'NEUTRAL',
              strength: Math.min((result.confluence_score || 0) + 20, 100),
              direction: result.htf_analysis?.bias === 'bullish' ? 'up' : 
                        result.htf_analysis?.bias === 'bearish' ? 'down' : 'neutral'
            },
            {
              timeframe: defaultTimeframes.mtf.toUpperCase(),
              bias: result.mtf_analysis?.confirmed ? 'CONFIRMED' : 'NEUTRAL',
              strength: result.confluence_score || 0,
              direction: result.mtf_analysis?.confirmed ? 'up' : 'neutral'
            },
            {
              timeframe: defaultTimeframes.ltf.toUpperCase(),
              bias: result.entry ? 'ENTRY' : 'WAITING',
              strength: result.entry ? result.confluence_score : 30,
              direction: result.entry ? 'up' : 'neutral'
            }
          ]
        };
        
        setMTFData(transformedData);
        setLastUpdate(new Date());
      } else {
        setError('Failed to analyze MTF confluence');
      }
    } catch (err) {
      setError(err.message || 'MTF analysis failed');
      console.error('MTF Analysis Error:', err);
    } finally {
      setLoading(false);
    }
  }, [symbol, defaultTimeframes.ltf, defaultTimeframes.mtf, defaultTimeframes.htf]);

  // Auto-refresh with dynamic intervals based on confidence score
  useEffect(() => {
    analyzeMTF();
    
    // Dynamic refresh interval based on confidence score
    const getRefreshInterval = () => {
      if (!mtfData) return 30000; // Default 30 seconds
      const score = mtfData.confluence_score || 0;
      const nextAnalysisMinutes = mtfData.next_analysis_in || 5;
      return Math.max(nextAnalysisMinutes * 60 * 1000, 30000); // Convert to milliseconds, minimum 30s
    };
    
    const interval = setInterval(analyzeMTF, getRefreshInterval());
    return () => clearInterval(interval);
  }, [analyzeMTF, mtfData?.confluence_score, mtfData?.next_analysis_in]);

  // Quick status check (lighter weight)
  const getQuickStatus = useCallback(async () => {
    if (!symbol) return null;
    
    try {
      const status = await getMTFStatus(symbol, defaultTimeframes.htf);
      return status;
    } catch (err) {
      console.error('MTF Status Error:', err);
      return null;
    }
  }, [symbol, defaultTimeframes.htf]);

  return {
    mtfData,
    loading,
    error,
    lastUpdate,
    refetch: analyzeMTF,
    getQuickStatus,
    // Convenience getters
    confluenceScore: mtfData?.confluence_score || 0,
    bias: mtfData?.bias || 'neutral',
    signalValid: mtfData?.signal_valid || false,
    entry: mtfData?.entry,
    stopLoss: mtfData?.sl || mtfData?.stop_loss,
    takeProfit: mtfData?.tp || mtfData?.take_profit,
    reasons: mtfData?.reasons || [],
    mtfBias: mtfData?.mtfBias || [],
    statusMessage: mtfData?.statusMessage || '',
    nextAnalysisIn: mtfData?.next_analysis_in || 5,
    marketStatus: mtfData?.market_status || 'analyzing'
  };
};

export default useMTFConfluence;