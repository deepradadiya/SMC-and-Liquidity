import React, { useState } from 'react';
import { Clock, TrendingUp, TrendingDown, Minus, BarChart3, Filter, RefreshCw } from 'lucide-react';
import { useMTFHistory } from '../hooks/useMTFHistory';

/**
 * MTF Confluence History Panel with time filters and historical analysis
 */
const MTFHistoryPanel = ({ symbol, htf = "4h", mtf = "1h", ltf = "5m" }) => {
  const [selectedDays, setSelectedDays] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  
  const {
    historyData,
    summary,
    loading,
    error,
    refetch,
    totalEntries,
    validSignals,
    averageScore,
    biasDistribution
  } = useMTFHistory(symbol, {
    days: selectedDays,
    htf,
    mtf,
    ltf,
    autoRefresh: true,
    refreshInterval: 30000 // 30 seconds
  });

  const timeFilters = [
    { label: '1 Day', value: 1, icon: '📅' },
    { label: '1 Week', value: 7, icon: '📊' },
    { label: '1 Month', value: 30, icon: '📈' },
    { label: '1 Year', value: 365, icon: '📋' }
  ];

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now - date) / 60000);
    
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--accent-green)';
    if (score >= 60) return 'var(--accent-yellow)';
    return 'var(--accent-red)';
  };

  const getBiasIcon = (bias) => {
    switch (bias) {
      case 'bullish': return <TrendingUp className="w-4 h-4" style={{ color: 'var(--accent-green)' }} />;
      case 'bearish': return <TrendingDown className="w-4 h-4" style={{ color: 'var(--accent-red)' }} />;
      default: return <Minus className="w-4 h-4" style={{ color: 'var(--text-secondary)' }} />;
    }
  };

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: 'var(--bg-secondary)' }}>
      
      {/* Header with filters */}
      <div className="p-3 border-b border-[var(--border)]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Clock className="w-4 h-4" />
            MTF History
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 rounded hover:bg-[var(--bg-hover)] transition-colors"
              title="Toggle Filters"
            >
              <Filter className="w-4 h-4" style={{ color: 'var(--text-secondary)' }} />
            </button>
            <button
              onClick={refetch}
              disabled={loading}
              className="p-2 rounded hover:bg-[var(--bg-hover)] transition-colors"
              title="Refresh History"
            >
              <RefreshCw 
                className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} 
                style={{ color: 'var(--text-secondary)' }} 
              />
            </button>
          </div>
        </div>

        {/* Time Filter Buttons */}
        <div className="flex gap-1">
          {timeFilters.map((filter) => (
            <button
              key={filter.value}
              onClick={() => setSelectedDays(filter.value)}
              className={`px-3 py-1.5 text-xs rounded transition-colors flex items-center gap-1 ${
                selectedDays === filter.value
                  ? 'text-white'
                  : 'hover:bg-[var(--bg-hover)]'
              }`}
              style={{
                backgroundColor: selectedDays === filter.value 
                  ? 'var(--accent-blue)' 
                  : 'transparent',
                color: selectedDays === filter.value 
                  ? 'white' 
                  : 'var(--text-secondary)'
              }}
            >
              <span>{filter.icon}</span>
              <span>{filter.label}</span>
            </button>
          ))}
        </div>

        {/* Advanced Filters (collapsible) */}
        {showFilters && (
          <div className="mt-3 p-3 rounded-lg" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
            <div className="text-xs font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
              TIMEFRAME FILTERS
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>HTF:</span>
                <span className="ml-1 font-medium" style={{ color: 'var(--text-primary)' }}>{htf}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>MTF:</span>
                <span className="ml-1 font-medium" style={{ color: 'var(--text-primary)' }}>{mtf}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>LTF:</span>
                <span className="ml-1 font-medium" style={{ color: 'var(--text-primary)' }}>{ltf}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="p-3 border-b border-[var(--border)]">
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-2 rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
              <div className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
                {summary.total_analyses}
              </div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                Total Analyses
              </div>
            </div>
            <div className="text-center p-2 rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
              <div className="text-lg font-bold" style={{ color: 'var(--accent-green)' }}>
                {summary.valid_signals}
              </div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                Valid Signals
              </div>
            </div>
            <div className="text-center p-2 rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
              <div className="text-lg font-bold" style={{ color: 'var(--accent-blue)' }}>
                {summary.average_confluence_score}
              </div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                Avg Score
              </div>
            </div>
            <div className="text-center p-2 rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
              <div className="text-lg font-bold" style={{ color: 'var(--accent-yellow)' }}>
                {summary.signal_rate}%
              </div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                Signal Rate
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-[var(--accent-blue)] border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Loading history...
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <div className="text-sm font-medium mb-1" style={{ color: 'var(--accent-red)' }}>
              Failed to load history
            </div>
            <div className="text-xs mb-3" style={{ color: 'var(--text-secondary)' }}>
              {error}
            </div>
            <button
              onClick={refetch}
              className="px-3 py-1 text-xs rounded transition-colors"
              style={{ backgroundColor: 'var(--accent-blue)', color: 'white' }}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* History List */}
      {!loading && !error && (
        <div className="flex-1 overflow-y-auto">
          {historyData.length === 0 ? (
            <div className="flex-1 flex items-center justify-center p-4">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-2" style={{ color: 'var(--text-secondary)' }} />
                <div className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  No History Available
                </div>
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  No MTF analyses found for the selected period
                </div>
              </div>
            </div>
          ) : (
            <div className="p-3 space-y-2">
              {historyData.map((entry) => (
                <div
                  key={entry.id}
                  className="p-3 rounded-lg border transition-colors hover:bg-[var(--bg-hover)]"
                  style={{ 
                    backgroundColor: 'var(--bg-tertiary)',
                    borderColor: entry.signal_valid ? 'var(--accent-green)' : 'var(--border)'
                  }}
                >
                  {/* Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getBiasIcon(entry.bias)}
                      <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                        {entry.bias.toUpperCase()}
                      </span>
                      {entry.signal_valid && (
                        <span className="px-2 py-0.5 text-xs rounded" style={{ 
                          backgroundColor: 'var(--accent-green)', 
                          color: 'white' 
                        }}>
                          VALID
                        </span>
                      )}
                    </div>
                    <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                      {formatTime(entry.timestamp)}
                    </div>
                  </div>

                  {/* Confluence Score */}
                  <div className="mb-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Confluence Score
                      </span>
                      <span className="text-xs font-bold" style={{ color: 'var(--text-primary)' }}>
                        {entry.confluence_score}/100
                      </span>
                    </div>
                    <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${entry.confluence_score}%`,
                          backgroundColor: getScoreColor(entry.confluence_score)
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* Trade Levels (if valid signal) */}
                  {entry.signal_valid && entry.entry_price && (
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div>
                        <span style={{ color: 'var(--text-secondary)' }}>Entry:</span>
                        <div className="font-mono font-semibold" style={{ color: 'var(--text-primary)' }}>
                          ${entry.entry_price.toFixed(2)}
                        </div>
                      </div>
                      <div>
                        <span style={{ color: 'var(--text-secondary)' }}>Stop:</span>
                        <div className="font-mono font-semibold" style={{ color: 'var(--accent-red)' }}>
                          ${(entry.stop_loss || 0).toFixed(2)}
                        </div>
                      </div>
                      <div>
                        <span style={{ color: 'var(--text-secondary)' }}>Target:</span>
                        <div className="font-mono font-semibold" style={{ color: 'var(--accent-green)' }}>
                          ${(entry.take_profit || 0).toFixed(2)}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Timeframes */}
                  <div className="mt-2 flex items-center gap-3 text-xs">
                    <span style={{ color: 'var(--text-secondary)' }}>
                      {entry.htf} / {entry.mtf} / {entry.ltf}
                    </span>
                    <span style={{ color: 'var(--text-secondary)' }}>
                      • {entry.reasons.length} factors
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MTFHistoryPanel;