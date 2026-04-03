import React, { useState } from 'react';
import { useChartStore, useRiskStore, useAlertStore } from '../stores';
import { Bell, Settings, Moon, Sun, Zap } from 'lucide-react';
import SymbolSearchModal from './modals/SymbolSearchModal';
import SettingsModal from './modals/SettingsModal';

const timeframes = ['1m', '5m', '15m', '1h', '4h', '1D'];
const htfOptions = ['1h', '4h', '1D'];

const Header = () => {
  const { symbol, timeframe, htf, setTimeframe, setHTF } = useChartStore();
  const { balance, todayPnL, todayPnLPercent } = useRiskStore();
  const { unreadCount } = useAlertStore();
  const [darkMode, setDarkMode] = useState(true);
  const [liveMode, setLiveMode] = useState(false);
  const [showSymbolSearch, setShowSymbolSearch] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [session, setSession] = useState('London Open');

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  return (
    <>
      <header className="h-12 bg-[var(--bg-secondary)] border-b border-[var(--border)] flex items-center justify-between px-4 gap-4">
        {/* Left Side */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5" style={{ color: 'var(--accent-blue)' }} />
            <span className="text-white font-semibold text-sm">SMC Terminal</span>
            <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: 'var(--accent-purple)', color: 'white' }}>
              v2.0 PRO
            </span>
          </div>
        </div>

        {/* Center */}
        <div className="flex items-center gap-3 flex-1 justify-center">
          {/* Symbol Selector */}
          <button
            data-testid="symbol-selector-button"
            onClick={() => setShowSymbolSearch(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium transition-colors"
            style={{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-primary)' }}
          >
            <span className="monospace font-semibold">{symbol}</span>
            <span style={{ color: 'var(--accent-green)' }}>$43,250.00</span>
            <span className="text-xs" style={{ color: 'var(--accent-green)' }}>▲ 2.3%</span>
          </button>

          {/* Timeframe Selector */}
          <div className="flex items-center gap-1" data-testid="timeframe-selector">
            {timeframes.map((tf) => (
              <button
                key={tf}
                data-testid={`timeframe-${tf}`}
                onClick={() => setTimeframe(tf)}
                className="px-3 py-1.5 text-xs font-medium rounded transition-colors"
                style={{
                  backgroundColor: timeframe === tf ? 'var(--accent-blue)' : 'var(--bg-tertiary)',
                  color: timeframe === tf ? 'white' : 'var(--text-secondary)'
                }}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* HTF Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>HTF:</span>
            <select
              data-testid="htf-selector"
              value={htf}
              onChange={(e) => setHTF(e.target.value)}
              className="px-2 py-1.5 text-xs rounded border-0 outline-none"
              style={{ backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-primary)' }}
            >
              {htfOptions.map((tf) => (
                <option key={tf} value={tf}>{tf}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-4">
          {/* Balance */}
          <div className="flex items-center gap-1 text-sm">
            <span style={{ color: 'var(--text-secondary)' }}>💰</span>
            <span className="monospace font-semibold" style={{ color: todayPnL >= 0 ? 'var(--accent-green)' : 'var(--text-primary)' }}>
              {formatCurrency(balance)}
            </span>
          </div>

          {/* Today's P&L */}
          <div className="flex items-center gap-1 text-sm" data-testid="today-pnl">
            <span>{todayPnL >= 0 ? '📈' : '📉'}</span>
            <span className="monospace font-semibold" style={{ color: todayPnL >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
              {todayPnL >= 0 ? '+' : ''}{formatCurrency(todayPnL)}
            </span>
            <span className="text-xs" style={{ color: todayPnL >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
              ({todayPnL >= 0 ? '+' : ''}{todayPnLPercent.toFixed(2)}%)
            </span>
          </div>

          {/* Session Badge */}
          <div data-testid="session-badge" className="flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
            <span className="w-2 h-2 rounded-full pulse" style={{ backgroundColor: 'var(--accent-green)' }}></span>
            <span style={{ color: 'var(--text-primary)' }}>{session}</span>
          </div>

          {/* Live/Paper Toggle */}
          <div className="flex items-center gap-1 px-1 py-1 rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
            <button
              data-testid="paper-mode-button"
              onClick={() => setLiveMode(false)}
              className="px-2 py-1 text-xs font-medium rounded transition-colors"
              style={{
                backgroundColor: !liveMode ? 'var(--accent-blue)' : 'transparent',
                color: !liveMode ? 'white' : 'var(--text-secondary)'
              }}
            >
              PAPER
            </button>
            <button
              data-testid="live-mode-button"
              onClick={() => setLiveMode(true)}
              className="px-2 py-1 text-xs font-medium rounded transition-colors flex items-center gap-1"
              style={{
                backgroundColor: liveMode ? 'var(--accent-red)' : 'transparent',
                color: liveMode ? 'white' : 'var(--text-secondary)'
              }}
            >
              {liveMode && <span className="w-1.5 h-1.5 rounded-full pulse" style={{ backgroundColor: 'white' }}></span>}
              LIVE
            </button>
          </div>

          {/* Alerts */}
          <button data-testid="alerts-button" className="relative" style={{ color: 'var(--text-secondary)' }}>
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full text-xs flex items-center justify-center" style={{ backgroundColor: 'var(--accent-red)', color: 'white' }}>
                {unreadCount}
              </span>
            )}
          </button>

          {/* Settings */}
          <button data-testid="settings-button" onClick={() => setShowSettings(true)} style={{ color: 'var(--text-secondary)' }}>
            <Settings className="w-5 h-5" />
          </button>

          {/* Theme Toggle */}
          <button data-testid="theme-toggle" onClick={() => setDarkMode(!darkMode)} style={{ color: 'var(--text-secondary)' }}>
            {darkMode ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {showSymbolSearch && <SymbolSearchModal onClose={() => setShowSymbolSearch(false)} />}
      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </>
  );
};

export default Header;