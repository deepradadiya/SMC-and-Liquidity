import { create } from 'zustand';
import { mockActiveSignal, mockHistoricalTrades } from '../data/mockData';

export const useSignalStore = create((set) => ({
  activeSignal: mockActiveSignal,
  historicalSignals: mockHistoricalTrades,
  scanning: false,
  lastAnalyzed: Date.now() - 120000,
  
  setActiveSignal: (signal) => set({ activeSignal: signal }),
  clearActiveSignal: () => set({ activeSignal: null }),
  addHistoricalSignal: (signal) => set((state) => ({
    historicalSignals: [signal, ...state.historicalSignals]
  })),
  setScanning: (scanning) => set({ scanning }),
  updateLastAnalyzed: () => set({ lastAnalyzed: Date.now() })
}));

export const useChartStore = create((set) => ({
  symbol: 'BTCUSDT',
  timeframe: '15m',
  htf: '4h',
  overlays: {
    orderBlocks: true,
    fvgs: true,
    liquidity: true,
    structure: true,
    sessions: false,
    levels: true,
    htf: false
  },
  
  setSymbol: (symbol) => set({ symbol }),
  setTimeframe: (timeframe) => set({ timeframe }),
  setHTF: (htf) => set({ htf }),
  toggleOverlay: (overlay) => set((state) => ({
    overlays: {
      ...state.overlays,
      [overlay]: !state.overlays[overlay]
    }
  }))
}));

export const useRiskStore = create((set) => ({
  balance: 12450.30,
  todayPnL: 234.50,
  todayPnLPercent: 1.9,
  riskPerTrade: 1,
  maxDailyLoss: 5,
  minRR: 1.5,
  maxConcurrentTrades: 3,
  circuitBreaker: true,
  mlFilter: true,
  mlThreshold: 60,
  currentRisk: 35,
  
  updateBalance: (balance) => set({ balance }),
  updatePnL: (pnl, percent) => set({ todayPnL: pnl, todayPnLPercent: percent }),
  updateRiskSettings: (settings) => set(settings)
}));

export const useAlertStore = create((set) => ({
  alerts: [],
  unreadCount: 2,
  notifications: {
    telegram: false,
    email: false,
    browser: true,
    sound: true
  },
  
  addAlert: (alert) => set((state) => ({
    alerts: [{ ...alert, id: Date.now() }, ...state.alerts],
    unreadCount: state.unreadCount + 1
  })),
  clearAlerts: () => set({ alerts: [], unreadCount: 0 }),
  markAsRead: () => set({ unreadCount: 0 }),
  updateNotifications: (notifications) => set({ notifications })
}));