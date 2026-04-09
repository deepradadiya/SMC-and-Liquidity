import React, { useEffect } from 'react';
import { useChartStore, useSignalStore } from '../stores';
import { useMTFConfluence } from '../hooks/useMTFConfluence';
import { Copy, CheckCircle, X, TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';

/**
 * Enhanced SignalPanel that uses real MTF Confluence data from Module 1
 */
const MTFSignalPanel = () => {
  const { symbol, timeframe, htf } = useChartStore();
  const { setActiveSignal } = useSignalStore();
  
  // Use real MTF confluence data
  const {
    mtfData,
    loading,
    error,
    lastUpdate,
    refetch,
    confluenceScore,
    bias,
    signalValid,
    entry,
    stopLoss,
    takeProfit,
    reasons,
    mtfBias
  } = useMTFConfluence(symbol, {
    ltf: timeframe,
    htf: htf,
    mtf: "1h"
  });

  // Update signal store when MTF data changes
  useEffect(() => {
    if (mtfData && signalValid) {
      const realSignal = {
        id: `mtf_${Date.now()}`,
        symbol: symbol,
        direction: bias === 'bullish' ? 'BUY' : bias === 'bearish' ? 'SELL' : 'NONE',
        entry_price: entry,
        stop_loss: stopLoss,
        take_profit: takeProfit,
        confluence_score: confluenceScore,
        ml_probability: 0.75, // MTF confidence
        session: 'live_analysis',
        timeframes: [htf, '1h', timeframe],
        timestamp: new Date().toISOString(),
        type: 'MTF Confluence',
        reasons: reasons
      };
      
      setActiveSignal(realSignal);
    }
  }, [mtfData, signalValid, symbol, bias, entry, stopLoss, takeProfit, confluenceScore, reasons, setActiveSignal, htf, timeframe]);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Just now';
    const minutes = Math.floor((Date.now() - new Date(timestamp).getTime()) / 60000);
    return minutes < 60 ? `${minutes} min ago` : `${Math.floor(minutes / 60)} hr ago`;
  };

  // Create signal object for display
  const signal = mtfData ? {
    type: bias === 'bullish' ? 'BUY' : bias === 'bearish' ? 'SELL' : 'NONE',
    symbol: symbol,
    timeframe: timeframe.toUpperCase(),
    session: 'Live Analysis',
    timestamp: lastUpdate?.getTime() || Date.now(),
    confluence_score: confluenceScore,
    entry: entry || 0,
    stop_loss: stopLoss || 0,
    take_profit: takeProfit || 0,
    risk_reward: entry && stopLoss && takeProfit ? 
      Math.abs(takeProfit - entry) / Math.abs(entry - stopLoss) : 0,
    ml_confidence: 71, // Mock ML data
    risk_amount: 215,
    risk_percent: 1,
    position_size: 0.005,
    reasons: reasons
  } : null;

  return (
    <div className="w-70 border-l border-[var(--border)] flex flex-col overflow-y-auto" style={{ backgroundColor: 'var(--bg-secondary)' }}>
      
      {/* Header with refresh */}
      <div className="p-3 border-b border-[var(--border)] flex items-center justify-between">
        <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
          MTF Confluence Analysis
        </h3>
        <button 
          onClick={refetch}
          disabled={loading}
          className="p-2 rounded hover:bg-[var(--bg-hover)] transition-colors"
          title="Refresh Analysis"
        >
          <RefreshCw 
            className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} 
            style={{ color: 'var(--text-secondary)' }} 
          />
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="m-3 p-8 text-center rounded-lg" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
          <div className="w-16 h-16 border-4 border-[var(--accent-blue)] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
            ANALYZING MTF CONFLUENCE...
          </div>
          <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            {symbol} • {timeframe} / {htf}
          </div>
        </div>
      )}

      {/* Professional Status Message - Show when not loading and confidence < 60 */}
      {!loading && mtfData && confluenceScore < 60 && (
        <div className="m-3 p-6 text-center rounded-lg border" style={{ 
          backgroundColor: 'var(--bg-tertiary)', 
          borderColor: 'var(--accent-yellow)' 
        }}>
          <div className="w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ 
            backgroundColor: 'var(--accent-yellow)', 
            color: 'white' 
          }}>
            📊
          </div>
          <div className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
            ANALYZING MARKET CONDITIONS
          </div>
          <div className="text-xs mb-3" style={{ color: 'var(--text-secondary)' }}>
            {mtfData.statusMessage || `Confidence score: ${confluenceScore}/100`}
          </div>
          <div className="text-xs px-3 py-1 rounded-full inline-block" style={{ 
            backgroundColor: 'var(--bg-secondary)', 
            color: 'var(--text-secondary)' 
          }}>
            Next analysis in {mtfData.next_analysis_in || 5} minutes
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="m-3 p-4 rounded-lg border border-[var(--accent-red)]" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
          <div className="text-sm font-medium mb-1" style={{ color: 'var(--accent-red)' }}>
            Analysis Error
          </div>
          <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            {error}
          </div>
          <button 
            onClick={refetch}
            className="mt-2 px-3 py-1 text-xs rounded transition-colors"
            style={{ backgroundColor: 'var(--accent-red)', color: 'white' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Active Signal Card */}
      {signal && !loading && (
        <div className="m-3 rounded-lg overflow-hidden" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
          {/* Header */}
          <div className="p-3 flex items-center justify-between" style={{ 
            backgroundColor: signal.type === 'BUY' ? 'var(--accent-green)' : 
                           signal.type === 'SELL' ? 'var(--accent-red)' : 'var(--text-secondary)' 
          }}>
            <div className="flex items-center gap-2">
              {signal.type === 'BUY' && <TrendingUp className="w-5 h-5 text-white" />}
              {signal.type === 'SELL' && <TrendingDown className="w-5 h-5 text-white" />}
              {signal.type === 'NONE' && <Minus className="w-5 h-5 text-white" />}
              <span className="font-semibold text-white">
                {signal.type === 'NONE' ? 'NO SIGNAL' : `${signal.type} SIGNAL`}
              </span>
            </div>
            <div className="text-xs text-white opacity-90">
              LIVE
            </div>
          </div>

          <div className="p-3">
            <div className="flex items-center justify-between mb-3">
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {signal.symbol} • {signal.timeframe}
              </span>
              <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                {formatTime(signal.timestamp)}
              </span>
            </div>

            {/* Confluence Score */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
                  Confluence Score
                </span>
                <span className="text-xs font-bold" style={{ color: 'var(--text-primary)' }}>
                  {signal.confluence_score}/100
                </span>
              </div>
              <div className="w-full h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${signal.confluence_score}%`,
                    backgroundColor: signal.confluence_score >= 80 ? 'var(--accent-green)' : 
                                   signal.confluence_score >= 60 ? 'var(--accent-yellow)' : 'var(--accent-red)'
                  }}
                ></div>
              </div>
            </div>

            {/* Trade Levels - Only show if signal is valid */}
            {signalValid && (
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span style={{ color: 'var(--text-secondary)' }}>Entry</span>
                  <div className="flex items-center gap-2">
                    <span className="monospace font-semibold" style={{ color: 'var(--text-primary)' }}>
                      ${(signal.entry || 0).toFixed(2)}
                    </span>
                    <button onClick={() => copyToClipboard((signal.entry || 0).toString())} 
                            className="p-1 rounded hover:bg-[var(--bg-hover)] transition-colors">
                      <Copy className="w-3 h-3" style={{ color: 'var(--text-secondary)' }} />
                    </button>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span style={{ color: 'var(--text-secondary)' }}>Stop</span>
                  <div className="flex items-center gap-2">
                    <span className="monospace font-semibold" style={{ color: 'var(--accent-red)' }}>
                      ${(signal.stop_loss || 0).toFixed(2)}
                    </span>
                    <button onClick={() => copyToClipboard((signal.stop_loss || 0).toString())} 
                            className="p-1 rounded hover:bg-[var(--bg-hover)] transition-colors">
                      <Copy className="w-3 h-3" style={{ color: 'var(--text-secondary)' }} />
                    </button>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span style={{ color: 'var(--text-secondary)' }}>Target</span>
                  <div className="flex items-center gap-2">
                    <span className="monospace font-semibold" style={{ color: 'var(--accent-green)' }}>
                      ${(signal.take_profit || 0).toFixed(2)}
                    </span>
                    <button onClick={() => copyToClipboard((signal.take_profit || 0).toString())} 
                            className="p-1 rounded hover:bg-[var(--bg-hover)] transition-colors">
                      <Copy className="w-3 h-3" style={{ color: 'var(--text-secondary)' }} />
                    </button>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span style={{ color: 'var(--text-secondary)' }}>R:R</span>
                  <span className="monospace font-semibold" style={{ color: 'var(--text-primary)' }}>
                    1 : {(signal.risk_reward || 0).toFixed(1)}
                  </span>
                </div>
              </div>
            )}

            {/* Confluence Reasons */}
            <div className="mb-4">
              <div className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
                CONFLUENCE FACTORS:
              </div>
              <div className="space-y-1">
                {(signal.reasons || []).map((reason, index) => (
                  <div key={index} className="flex items-start gap-2 text-xs">
                    <CheckCircle className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: 'var(--accent-green)' }} />
                    <span style={{ color: 'var(--text-primary)' }}>{reason}</span>
                  </div>
                ))}
                {(!signal.reasons || signal.reasons.length === 0) && (
                  <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                    No confluence factors detected
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons - Only show if signal is valid */}
            {signalValid && (
              <div className="flex items-center gap-2">
                <button className="flex-1 py-2 text-sm font-medium rounded transition-colors" 
                        style={{ backgroundColor: 'var(--accent-green)', color: 'white' }}>
                  ✓ TAKE TRADE
                </button>
                <button className="flex-1 py-2 text-sm font-medium rounded transition-colors flex items-center justify-center gap-1" 
                        style={{ backgroundColor: 'var(--bg-hover)', color: 'var(--text-primary)' }}>
                  <X className="w-4 h-4" /> SKIP
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MTF Bias - Real Data with Professional Status */}
      {mtfBias && mtfBias.length > 0 && (
        <div className="mx-3 mb-3 p-3 rounded-lg" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
          <div className="text-xs font-semibold mb-3" style={{ color: 'var(--text-secondary)' }}>
            MTF BIAS (LIVE)
          </div>
          <div className="space-y-2">
            {mtfBias.map((bias) => (
              <div key={bias.timeframe}>
                <div className="flex items-center justify-between mb-1 text-xs">
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                    {bias.timeframe}
                  </span>
                  <div className="flex items-center gap-1">
                    {/* Show loading state for individual timeframes when confidence is low */}
                    {confluenceScore < 60 && bias.bias === 'WAITING' ? (
                      <span className="text-xs px-2 py-1 rounded" style={{ 
                        backgroundColor: 'var(--bg-secondary)', 
                        color: 'var(--text-secondary)' 
                      }}>
                        ANALYZING...
                      </span>
                    ) : (
                      <>
                        <span className="font-semibold" style={{ 
                          color: bias.direction === 'up' ? 'var(--accent-green)' : 
                                 bias.direction === 'down' ? 'var(--accent-red)' : 'var(--text-secondary)' 
                        }}>
                          {bias.bias}
                        </span>
                        {bias.direction === 'up' && <TrendingUp className="w-3 h-3" style={{ color: 'var(--accent-green)' }} />}
                        {bias.direction === 'down' && <TrendingDown className="w-3 h-3" style={{ color: 'var(--accent-red)' }} />}
                        {bias.direction === 'neutral' && <Minus className="w-3 h-3" style={{ color: 'var(--text-secondary)' }} />}
                      </>
                    )}
                  </div>
                </div>
                <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${bias.strength}%`,
                      backgroundColor: bias.direction === 'up' ? 'var(--accent-green)' : 
                                     bias.direction === 'down' ? 'var(--accent-red)' : 'var(--text-secondary)'
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Status */}
      <div className="mx-3 mb-3 p-3 rounded-lg text-center" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
        <div className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
          MODULE 1 STATUS
        </div>
        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-full" style={{ backgroundColor: 'var(--bg-secondary)' }}>
          <span>🎯</span>
          <span className="text-sm font-semibold" style={{ 
            color: mtfData ? 'var(--accent-green)' : 'var(--accent-yellow)' 
          }}>
            {mtfData ? 'ACTIVE' : 'LOADING'}
          </span>
        </div>
        {lastUpdate && (
          <div className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
            Last update: {formatTime(lastUpdate)}
          </div>
        )}
      </div>
    </div>
  );
};

export default MTFSignalPanel;