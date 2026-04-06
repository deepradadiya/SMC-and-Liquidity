import React from 'react';
import { X, TrendingUp, CheckCircle, Copy } from 'lucide-react';
import { mockMarketRegime } from '../data/mockData';

const RightPanel = ({ isOpen, panelType, selectedData, onClose }) => {
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${months[date.getMonth()]} ${date.getDate()}, ${hours}:${minutes}`;
  };

  return (
    <div 
      className={`w-80 border-l border-[var(--border)] flex flex-col slide-in-right flex-shrink-0 transition-all duration-300 ${
        isOpen ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0 w-0 border-0'
      }`}
      style={{ backgroundColor: 'var(--bg-tertiary)' }}
    >
      {/* Panel Header */}
      <div className={`flex items-center justify-between p-4 border-b border-[var(--border)] ${isOpen ? 'block' : 'hidden'}`}>
        <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
          {panelType === 'signal' && 'SIGNAL DETAILS'}
          {panelType === 'market-regime' && 'MARKET REGIME'}
          {panelType === 'buy-signal' && 'BUY SIGNAL ANALYSIS'}
        </h3>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-[var(--bg-hover)] transition-colors"
          style={{ color: 'var(--text-secondary)' }}
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Panel Content */}
      <div className={`flex-1 overflow-y-auto p-4 ${isOpen ? 'block' : 'hidden'}`}>
        {panelType === 'signal' && selectedData && (
          <div className="space-y-4">
            {/* Signal Header */}
            <div className="p-3 rounded-lg" style={{ backgroundColor: selectedData.type === 'BUY' ? 'var(--accent-green)' : 'var(--accent-red)' }}>
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 text-white" />
                <span className="text-lg font-bold text-white">{selectedData.type} SIGNAL</span>
              </div>
              <div className="text-white opacity-90 text-sm">
                {selectedData.symbol} • {selectedData.timeframe}
              </div>
              <div className="text-white opacity-75 text-xs">
                {formatTime(selectedData.time)}
              </div>
            </div>

            {/* Trade Levels */}
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 rounded text-sm" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Entry</span>
                <div className="flex items-center gap-2">
                  <span className="monospace font-semibold" style={{ color: 'var(--text-primary)' }}>
                    ${selectedData.entry.toLocaleString()}
                  </span>
                  <button onClick={() => copyToClipboard(selectedData.entry.toString())} className="p-1 rounded hover:bg-[var(--bg-hover)]">
                    <Copy className="w-3 h-3" style={{ color: 'var(--text-secondary)' }} />
                  </button>
                </div>
              </div>
              <div className="flex items-center justify-between p-2 rounded text-sm" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Stop Loss</span>
                <div className="flex items-center gap-2">
                  <span className="monospace font-semibold" style={{ color: 'var(--accent-red)' }}>
                    ${selectedData.sl.toLocaleString()}
                  </span>
                  <button onClick={() => copyToClipboard(selectedData.sl.toString())} className="p-1 rounded hover:bg-[var(--bg-hover)]">
                    <Copy className="w-3 h-3" style={{ color: 'var(--text-secondary)' }} />
                  </button>
                </div>
              </div>
              <div className="flex items-center justify-between p-2 rounded text-sm" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Take Profit</span>
                <div className="flex items-center gap-2">
                  <span className="monospace font-semibold" style={{ color: 'var(--accent-green)' }}>
                    ${selectedData.tp.toLocaleString()}
                  </span>
                  <button onClick={() => copyToClipboard(selectedData.tp.toString())} className="p-1 rounded hover:bg-[var(--bg-hover)]">
                    <Copy className="w-3 h-3" style={{ color: 'var(--text-secondary)' }} />
                  </button>
                </div>
              </div>
            </div>

            {/* Signal Stats */}
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 rounded text-center" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <div className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{selectedData.score}</div>
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Confluence</div>
              </div>
              <div className="p-2 rounded text-center" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <div className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{selectedData.rr.toFixed(1)}</div>
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Risk:Reward</div>
              </div>
              <div className="p-2 rounded text-center" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <div className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{selectedData.ml}%</div>
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>ML Filter</div>
              </div>
              <div className="p-2 rounded text-center" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <div className="text-sm font-bold" style={{ color: selectedData.pnl >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                  {selectedData.pnl >= 0 ? '+' : ''}${selectedData.pnl}
                </div>
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>P&L</div>
              </div>
            </div>

            {/* Status */}
            <div className="p-4 rounded-lg text-center" style={{ backgroundColor: 'var(--bg-secondary)' }}>
              <div className="text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>STATUS</div>
              <span
                className="px-4 py-2 rounded-full text-sm font-bold"
                style={{
                  backgroundColor: selectedData.status === 'TP HIT' ? 'rgba(16, 185, 129, 0.2)' : selectedData.status === 'SL HIT' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                  color: selectedData.status === 'TP HIT' ? 'var(--accent-green)' : selectedData.status === 'SL HIT' ? 'var(--accent-red)' : 'var(--accent-blue)'
                }}
              >
                {selectedData.status}
              </span>
            </div>
          </div>
        )}

        {panelType === 'market-regime' && (
          <div className="space-y-4">
            {/* Market Regime Display */}
            <div className="text-center p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-secondary)' }}>
              <div className="text-4xl mb-3">{mockMarketRegime.icon}</div>
              <div className="text-xl font-bold mb-1" style={{ color: `var(--accent-${mockMarketRegime.color})` }}>
                {mockMarketRegime.status}
              </div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                Current market trend analysis
              </div>
            </div>

            {/* Market Analysis */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>ANALYSIS</h4>
              <div className="space-y-2">
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-3 h-3 mt-1 flex-shrink-0" style={{ color: 'var(--accent-green)' }} />
                  <span className="text-xs" style={{ color: 'var(--text-primary)' }}>Strong bullish momentum detected</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-3 h-3 mt-1 flex-shrink-0" style={{ color: 'var(--accent-green)' }} />
                  <span className="text-xs" style={{ color: 'var(--text-primary)' }}>Higher highs and higher lows pattern</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-3 h-3 mt-1 flex-shrink-0" style={{ color: 'var(--accent-green)' }} />
                  <span className="text-xs" style={{ color: 'var(--text-primary)' }}>Volume supporting the trend</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-3 h-3 mt-1 flex-shrink-0" style={{ color: 'var(--accent-green)' }} />
                  <span className="text-xs" style={{ color: 'var(--text-primary)' }}>Key support levels holding strong</span>
                </div>
              </div>
            </div>

            {/* Confidence Meter */}
            <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--bg-secondary)' }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>Confidence</span>
                <span className="text-xs font-bold" style={{ color: 'var(--text-primary)' }}>85%</span>
              </div>
              <div className="w-full h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: '85%', backgroundColor: 'var(--accent-green)' }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {panelType === 'buy-signal' && (
          <div className="space-y-6">
            {/* Buy Signal Header */}
            <div className="text-center p-6 rounded-lg" style={{ backgroundColor: 'var(--accent-green)' }}>
              <div className="text-6xl mb-4">📈</div>
              <div className="text-2xl font-bold mb-2 text-white">BUY SIGNAL</div>
              <div className="text-sm text-white opacity-90">
                Strong bullish confluence detected
              </div>
            </div>

            {/* Signal Analysis */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>SIGNAL ANALYSIS</h4>
              <div className="space-y-2">
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 mt-0.5" style={{ color: 'var(--accent-green)' }} />
                  <span className="text-sm" style={{ color: 'var(--text-primary)' }}>Order block mitigation confirmed</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 mt-0.5" style={{ color: 'var(--accent-green)' }} />
                  <span className="text-sm" style={{ color: 'var(--text-primary)' }}>Fair value gap filled</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 mt-0.5" style={{ color: 'var(--accent-green)' }} />
                  <span className="text-sm" style={{ color: 'var(--text-primary)' }}>Liquidity sweep completed</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 mt-0.5" style={{ color: 'var(--accent-green)' }} />
                  <span className="text-sm" style={{ color: 'var(--text-primary)' }}>Change of character detected</span>
                </div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-secondary)' }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Risk Level</span>
                <span className="text-sm font-bold" style={{ color: 'var(--accent-green)' }}>LOW</span>
              </div>
              <div className="w-full h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: '25%', backgroundColor: 'var(--accent-green)' }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RightPanel;