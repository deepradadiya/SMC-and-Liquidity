import React, { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Activity, DollarSign, Target, AlertTriangle } from 'lucide-react'
import { signalsAPI, backtestAPI, marketDataAPI } from '../services/api'

const Dashboard = () => {
  const [signalsSummary, setSignalsSummary] = useState(null)
  const [performanceData, setPerformanceData] = useState({})
  const [marketOverview, setMarketOverview] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load signals summary
      const signalsResponse = await signalsAPI.getSignalsSummary()
      setSignalsSummary(signalsResponse.data)

      // Load performance data for key symbols
      const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
      const performancePromises = symbols.map(symbol => 
        backtestAPI.getPerformanceMetrics(symbol, '1h')
      )
      
      const performanceResults = await Promise.allSettled(performancePromises)
      const performanceMap = {}
      
      performanceResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          performanceMap[symbols[index]] = result.value.data
        }
      })
      
      setPerformanceData(performanceMap)

      // Create market overview
      const overview = symbols.map(symbol => ({
        symbol,
        signals: signalsResponse.data.signals_by_symbol[symbol] || {},
        performance: performanceMap[symbol] || {}
      }))
      
      setMarketOverview(overview)
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, change, icon: Icon, color = 'blue' }) => {
    const colorClasses = {
      blue: 'text-blue-600 bg-blue-50',
      green: 'text-green-600 bg-green-50',
      red: 'text-red-600 bg-red-50',
      yellow: 'text-yellow-600 bg-yellow-50'
    }

    return (
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {change !== undefined && (
              <p className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {change >= 0 ? '+' : ''}{change}%
              </p>
            )}
          </div>
          <div className={`p-3 rounded-full ${colorClasses[color]}`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const totalSignals = signalsSummary ? 
    Object.values(signalsSummary.signals_by_symbol).reduce((total, symbolData) => {
      return total + Object.values(symbolData).reduce((sum, tf) => sum + (tf.count || 0), 0)
    }, 0) : 0

  const avgWinRate = Object.values(performanceData).length > 0 ?
    Object.values(performanceData).reduce((sum, perf) => sum + (perf.win_rate || 0), 0) / Object.values(performanceData).length : 0

  const totalReturn = Object.values(performanceData).length > 0 ?
    Object.values(performanceData).reduce((sum, perf) => sum + (perf.total_return_percent || 0), 0) : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Trading Dashboard</h1>
        <p className="text-gray-600">Smart Money Concepts trading system overview</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Signals"
          value={totalSignals}
          icon={Activity}
          color="blue"
        />
        <StatCard
          title="Avg Win Rate"
          value={`${avgWinRate.toFixed(1)}%`}
          change={avgWinRate > 50 ? 5.2 : -2.1}
          icon={Target}
          color="green"
        />
        <StatCard
          title="Total Return"
          value={`${totalReturn.toFixed(1)}%`}
          change={totalReturn}
          icon={DollarSign}
          color={totalReturn >= 0 ? 'green' : 'red'}
        />
        <StatCard
          title="Risk Level"
          value="Medium"
          icon={AlertTriangle}
          color="yellow"
        />
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Signals Overview */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Signals by Symbol</h3>
          <div className="space-y-4">
            {marketOverview.map(item => (
              <div key={item.symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{item.symbol}</h4>
                  <div className="flex space-x-4 text-sm text-gray-600">
                    <span>1H: {item.signals['1h']?.count || 0} signals</span>
                    <span>4H: {item.signals['4h']?.count || 0} signals</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex space-x-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {item.signals['1h']?.buy_signals || 0} BUY
                    </span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      {item.signals['1h']?.sell_signals || 0} SELL
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Overview */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Overview</h3>
          <div className="space-y-4">
            {marketOverview.map(item => (
              <div key={item.symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{item.symbol}</h4>
                  <div className="text-sm text-gray-600">
                    Win Rate: {item.performance.win_rate?.toFixed(1) || 0}%
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-semibold ${
                    (item.performance.total_return_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {(item.performance.total_return_percent || 0) >= 0 ? '+' : ''}
                    {item.performance.total_return_percent?.toFixed(1) || 0}%
                  </div>
                  <div className="text-sm text-gray-500">
                    {item.performance.total_trades || 0} trades
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Market Data: Connected</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">SMC Engine: Active</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Signal Generator: Running</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard