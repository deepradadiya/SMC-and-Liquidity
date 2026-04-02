import React from 'react'
import { Copy, TrendingUp, TrendingDown, Clock, Target, Shield, Brain, Globe } from 'lucide-react'
import { useSignalStore } from '../stores/signalStore'
import { useRiskStore } from '../stores/riskStore'
import toast from 'react-hot-toast'

const SignalPanel = () => {
  const { activeSignal, getSignalAge } = useSignalStore()
  const { calculateRiskReward } = useRiskStore()

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text)
    toast.success(`${label} copied to clipboard`)
  }

  const CircularProgress = ({ value, max = 100, size = 60, strokeWidth = 6 }) => {
    const radius = (size - strokeWidth) / 2
    const circumference = radius * 2 * Math.PI
    const offset = circumference - (value / max) * circumference

    return (
      <div className="relative inline-flex items-center justify-center">
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            className="text-dark-border"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={`transition-all duration-300 ${
              value >= 80 ? 'text-bull' : value >= 60 ? 'text-warning-500' : 'text-bear'
            }`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-bold text-dark-text">{value}</span>
        </div>
      </div>
    )
  }

  const RiskRewardBar = ({ ratio }) => {
    const maxRatio = 5
    const percentage = Math.min((ratio / maxRatio) * 100, 100)
    
    return (
      <div className="w-full">
        <div className="flex justify-between text-xs text-dark-muted mb-1">
          <span>Risk</span>
          <span>Reward</span>
        </div>
        <div className="w-full bg-dark-border rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-300 ${
              ratio >= 2 ? 'bg-bull' : ratio >= 1.5 ? 'bg-warning-500' : 'bg-bear'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="text-center text-xs text-dark-muted mt-1">
          1:{ratio.toFixed(1)}
        </div>
      </div>
    )
  }

  const SessionIcon = ({ session }) => {
    const icons = {
      asia: '🌏',
      london: '🇬🇧',
      new_york: '🇺🇸'
    }
    return <span className="text-lg">{icons[session] || '🌍'}</span>
  }

  if (!activeSignal) {
    return (
      <div className="h-full bg-dark-surface border border-dark-border rounded-lg p-4">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="w-16 h-16 bg-dark-border rounded-full flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="w-8 h-8 text-dark-muted" />
            </div>
            <h3 className="text-dark-text font-medium mb-2">No Active Signal</h3>
            <p className="text-dark-muted text-sm">
              Waiting for confluence conditions to be met
            </p>
          </div>
        </div>
      </div>
    )
  }

  const riskReward = calculateRiskReward(
    activeSignal.entry_price,
    activeSignal.stop_loss,
    activeSignal.take_profit
  )

  return (
    <div className="h-full bg-dark-surface border border-dark-border rounded-lg p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-dark-text font-semibold">Active Signal</h3>
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-dark-muted" />
          <span className="text-xs text-dark-muted">
            {getSignalAge(activeSignal)}
          </span>
        </div>
      </div>

      {/* Direction Badge */}
      <div className="flex items-center justify-center">
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-semibold ${
          activeSignal.direction === 'BUY' 
            ? 'bg-bull/20 text-bull' 
            : 'bg-bear/20 text-bear'
        }`}>
          {activeSignal.direction === 'BUY' ? (
            <TrendingUp className="w-5 h-5" />
          ) : (
            <TrendingDown className="w-5 h-5" />
          )}
          <span>{activeSignal.direction}</span>
        </div>
      </div>

      {/* Confluence Score */}
      <div className="text-center">
        <div className="flex justify-center mb-2">
          <CircularProgress value={activeSignal.confluence_score || 0} />
        </div>
        <p className="text-xs text-dark-muted">Confluence Score</p>
      </div>

      {/* Price Levels */}
      <div className="space-y-3">
        <div className="flex items-center justify-between p-2 bg-dark-bg rounded border border-dark-border">
          <div className="flex items-center space-x-2">
            <Target className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-dark-muted">Entry</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-mono text-dark-text">
              ${activeSignal.entry_price?.toFixed(2)}
            </span>
            <button
              onClick={() => copyToClipboard(activeSignal.entry_price?.toString(), 'Entry price')}
              className="text-dark-muted hover:text-dark-text transition-colors"
            >
              <Copy className="w-3 h-3" />
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between p-2 bg-dark-bg rounded border border-dark-border">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-bear" />
            <span className="text-sm text-dark-muted">Stop Loss</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-mono text-dark-text">
              ${activeSignal.stop_loss?.toFixed(2)}
            </span>
            <button
              onClick={() => copyToClipboard(activeSignal.stop_loss?.toString(), 'Stop loss')}
              className="text-dark-muted hover:text-dark-text transition-colors"
            >
              <Copy className="w-3 h-3" />
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between p-2 bg-dark-bg rounded border border-dark-border">
          <div className="flex items-center space-x-2">
            <Target className="w-4 h-4 text-bull" />
            <span className="text-sm text-dark-muted">Take Profit</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-mono text-dark-text">
              ${activeSignal.take_profit?.toFixed(2)}
            </span>
            <button
              onClick={() => copyToClipboard(activeSignal.take_profit?.toString(), 'Take profit')}
              className="text-dark-muted hover:text-dark-text transition-colors"
            >
              <Copy className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Risk:Reward Ratio */}
      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-dark-muted">Risk:Reward</span>
        </div>
        <RiskRewardBar ratio={riskReward} />
      </div>

      {/* ML Approval */}
      {activeSignal.ml_probability && (
        <div className="flex items-center justify-between p-2 bg-dark-bg rounded border border-dark-border">
          <div className="flex items-center space-x-2">
            <Brain className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-dark-muted">ML Approval</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-medium ${
              activeSignal.ml_probability >= 0.7 ? 'text-bull' : 'text-warning-500'
            }`}>
              ✅ {(activeSignal.ml_probability * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      )}

      {/* Session Indicator */}
      {activeSignal.session && (
        <div className="flex items-center justify-between p-2 bg-dark-bg rounded border border-dark-border">
          <div className="flex items-center space-x-2">
            <Globe className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-dark-muted">Session</span>
          </div>
          <div className="flex items-center space-x-2">
            <SessionIcon session={activeSignal.session} />
            <span className="text-sm text-dark-text capitalize">
              {activeSignal.session.replace('_', ' ')}
            </span>
          </div>
        </div>
      )}

      {/* Timeframe Stack */}
      {activeSignal.timeframes && (
        <div className="space-y-2">
          <span className="text-sm text-dark-muted">Timeframe Analysis</span>
          <div className="flex items-center justify-center space-x-2">
            {activeSignal.timeframes.map((tf, index) => (
              <React.Fragment key={tf}>
                <div className="px-2 py-1 bg-dark-border rounded text-xs font-mono text-dark-text">
                  {tf.toUpperCase()}
                </div>
                {index < activeSignal.timeframes.length - 1 && (
                  <span className="text-dark-muted">→</span>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SignalPanel