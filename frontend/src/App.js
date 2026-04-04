import React, { useEffect, useState } from 'react';
import './styles/globals.css';
import Header from './components/Header';
import Watchlist from './components/Watchlist';
import ChartPanel from './components/ChartPanel';
import SignalPanel from './components/SignalPanel';
import BottomPanel from './components/BottomPanel';
import useWebSocket from './hooks/useWebSocket';
import { useSignalStore, useRiskStore, useAlertStore, useChartStore } from './stores';
import { checkHealth, fetchRiskStatus, fetchSignals } from './services/api';
import { Info, AlertTriangle } from 'lucide-react';

function App() {
  const [showDemoBanner, setShowDemoBanner] = useState(true);
  const [backendStatus, setBackendStatus] = useState('checking');
  const { setActiveSignal, addHistoricalSignal } = useSignalStore();
  const { updatePnL, updateRiskMetrics } = useRiskStore();
  const { addAlert } = useAlertStore();
  const { updateSMCData, updateMTFData } = useChartStore();

  // Check backend health on startup
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const health = await checkHealth();
        if (health && health.status === 'healthy') {
          setBackendStatus('connected');
          // Load initial data
          loadInitialData();
        } else {
          setBackendStatus('disconnected');
        }
      } catch (error) {
        console.error('Backend health check failed:', error);
        setBackendStatus('disconnected');
      }
    };

    checkBackendHealth();
    
    // Check health every 30 seconds
    const healthInterval = setInterval(checkBackendHealth, 30000);
    
    return () => clearInterval(healthInterval);
  }, []);

  const loadInitialData = async () => {
    try {
      // Load risk status
      const riskStatus = await fetchRiskStatus();
      if (riskStatus) {
        updateRiskMetrics(riskStatus);
      }

      // Load recent signals
      const signals = await fetchSignals(null, 10);
      if (signals && signals.length > 0) {
        // Set most recent as active if it's still active
        const activeSignal = signals.find(s => s.status === 'ACTIVE');
        if (activeSignal) {
          setActiveSignal(activeSignal);
        }
      }
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };

  const handleWebSocketMessage = (data) => {
    console.log('WebSocket message:', data);
    
    switch (data.type) {
      case 'price_update':
        // Handle real-time price updates
        break;
        
      case 'new_signal':
        setActiveSignal(data.signal);
        addAlert({
          type: 'signal',
          title: 'New Trading Signal',
          message: `${data.signal.signal_type} signal for ${data.signal.symbol}`,
          severity: 'info'
        });
        break;
        
      case 'signal_filled':
        addHistoricalSignal(data.signal);
        addAlert({
          type: 'trade',
          title: 'Signal Filled',
          message: `${data.signal.signal_type} signal filled at ${data.signal.entry_price}`,
          severity: 'success'
        });
        break;
        
      case 'circuit_breaker':
        addAlert({
          type: 'risk',
          title: 'Circuit Breaker Activated',
          message: 'Daily loss limit reached. Trading halted.',
          severity: 'error'
        });
        break;
        
      case 'risk_update':
        updateRiskMetrics(data.metrics);
        break;
        
      case 'smc_update':
        updateSMCData(data.smc_data);
        break;
        
      case 'mtf_update':
        updateMTFData(data.mtf_data);
        break;
        
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const { connected, demoMode } = useWebSocket(handleWebSocketMessage);

  const getBannerConfig = () => {
    if (backendStatus === 'checking') {
      return {
        color: 'var(--accent-blue)',
        icon: Info,
        message: '🔄 Checking backend connection...'
      };
    } else if (backendStatus === 'disconnected' || !connected) {
      return {
        color: 'var(--accent-red)',
        icon: AlertTriangle,
        message: '⚠️ DEMO MODE — Backend disconnected. Connect backend at localhost:8000 for live data'
      };
    } else if (demoMode) {
      return {
        color: 'var(--accent-yellow)',
        icon: Info,
        message: '📋 DEMO MODE — Limited functionality. Full features available with live backend'
      };
    }
    return null;
  };

  const bannerConfig = getBannerConfig();

  return (
    <div className="trading-terminal" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Status Banner */}
      {bannerConfig && showDemoBanner && (
        <div 
          data-testid="status-banner" 
          className="flex items-center justify-between px-4 py-2" 
          style={{ backgroundColor: bannerConfig.color, color: '#000' }}
        >
          <div className="flex items-center gap-2">
            <bannerConfig.icon className="w-4 h-4" />
            <span className="text-sm font-medium">
              {bannerConfig.message}
            </span>
          </div>
          <button
            data-testid="dismiss-banner"
            onClick={() => setShowDemoBanner(false)}
            className="text-xs font-medium px-3 py-1 rounded hover:bg-black/10 transition-colors"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Header */}
      <Header backendStatus={backendStatus} />

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