import React, { useEffect, useState } from 'react';
import './styles/globals.css';
import Header from './components/Header';
import Watchlist from './components/Watchlist';
import ChartPanel from './components/ChartPanel';
import SignalPanel from './components/SignalPanel';
import BottomPanel from './components/BottomPanel';
import useWebSocket from './hooks/useWebSocket';
import { useSignalStore, useRiskStore } from './stores';
import { Info } from 'lucide-react';

function App() {
  const [showDemoBanner, setShowDemoBanner] = useState(true);
  const { setActiveSignal } = useSignalStore();
  const { updatePnL } = useRiskStore();

  const handleWebSocketMessage = (data) => {
    console.log('WebSocket message:', data);
    
    if (data.type === 'price_update') {
      // Handle price updates
    } else if (data.type === 'new_signal') {
      setActiveSignal(data.signal);
      // Show toast notification
    } else if (data.type === 'circuit_breaker') {
      // Show circuit breaker alert
    }
  };

  const { connected, demoMode } = useWebSocket(handleWebSocketMessage);

  return (
    <div className="trading-terminal" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Demo Mode Banner */}
      {(demoMode || !connected) && showDemoBanner && (
        <div data-testid="demo-mode-banner" className="flex items-center justify-between px-4 py-2" style={{ backgroundColor: 'var(--accent-yellow)', color: '#000' }}>
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4" />
            <span className="text-sm font-medium">
              📋 DEMO MODE — Connect backend at localhost:8000 for live data
            </span>
          </div>
          <button
            data-testid="dismiss-demo-banner"
            onClick={() => setShowDemoBanner(false)}
            className="text-xs font-medium px-3 py-1 rounded hover:bg-black/10 transition-colors"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Header */}
      <Header />

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Watchlist */}
        <Watchlist />

        {/* Center: Chart + Signal Panel */}
        <div className="flex-1 flex overflow-hidden">
          <ChartPanel />
          <SignalPanel />
        </div>
      </div>

      {/* Bottom Panel */}
      <BottomPanel />
    </div>
  );
}

export default App;