import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Loader2, Download, RefreshCw, TrendingUp, Calendar, BarChart3 } from 'lucide-react';

const HistoricalDataPanel = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
  const [selectedTimeframes, setSelectedTimeframes] = useState(['1m', '5m', '15m', '1h', '4h', '1d']);
  const [supportedTimeframes, setSupportedTimeframes] = useState({});
  const [historicalData, setHistoricalData] = useState({});
  const [loading, setLoading] = useState(false);
  const [dataSummary, setDataSummary] = useState(null);
  const [error, setError] = useState(null);

  const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT', 'DOTUSDT', 'LINKUSDT'];

  // Fetch supported timeframes on component mount
  useEffect(() => {
    fetchSupportedTimeframes();
    fetchDataSummary();
  }, []);

  const fetchSupportedTimeframes = async () => {
    try {
      const response = await fetch('/api/historical/timeframes');
      if (response.ok) {
        const data = await response.json();
        setSupportedTimeframes(data);
      }
    } catch (error) {
      console.error('Error fetching timeframes:', error);
    }
  };

  const fetchDataSummary = async () => {
    try {
      const response = await fetch('/api/historical/summary');
      if (response.ok) {
        const data = await response.json();
        setDataSummary(data);
      }
    } catch (error) {
      console.error('Error fetching data summary:', error);
    }
  };

  const fetchHistoricalData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const timeframesParam = selectedTimeframes.join(',');
      const response = await fetch(`/api/historical/fetch/${selectedSymbol}?timeframes=${timeframesParam}`);
      
      if (response.ok) {
        const data = await response.json();
        setHistoricalData(data);
        
        // Refresh data summary
        await fetchDataSummary();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch historical data');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getTimeframeBadgeColor = (tf) => {
    const colors = {
      '1m': 'bg-red-100 text-red-800',
      '5m': 'bg-orange-100 text-orange-800',
      '15m': 'bg-yellow-100 text-yellow-800',
      '1h': 'bg-green-100 text-green-800',
      '4h': 'bg-blue-100 text-blue-800',
      '1d': 'bg-purple-100 text-purple-800',
      '1w': 'bg-indigo-100 text-indigo-800',
      '1M': 'bg-pink-100 text-pink-800'
    };
    return colors[tf] || 'bg-gray-100 text-gray-800';
  };

  const toggleTimeframe = (tf) => {
    setSelectedTimeframes(prev => 
      prev.includes(tf) 
        ? prev.filter(t => t !== tf)
        : [...prev, tf]
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Historical Data Manager
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Symbol Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">Symbol</label>
              <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {symbols.map(symbol => (
                    <SelectItem key={symbol} value={symbol}>
                      {symbol}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Fetch Button */}
            <div className="flex items-end">
              <Button 
                onClick={fetchHistoricalData} 
                disabled={loading || selectedTimeframes.length === 0}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Fetching...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    Fetch Data
                  </>
                )}
              </Button>
            </div>

            {/* Refresh Summary */}
            <div className="flex items-end">
              <Button 
                variant="outline" 
                onClick={fetchDataSummary}
                className="w-full"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Summary
              </Button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Timeframe Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Select Timeframes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
            {Object.entries(supportedTimeframes).map(([tf, config]) => (
              <div
                key={tf}
                className={`p-3 border rounded-lg cursor-pointer transition-all ${
                  selectedTimeframes.includes(tf)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => toggleTimeframe(tf)}
              >
                <div className="text-center">
                  <div className="font-medium">{tf}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {config.description}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    Max: {Math.floor(config.max_historical_days / 365)}y
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setSelectedTimeframes(Object.keys(supportedTimeframes))}
            >
              Select All
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setSelectedTimeframes([])}
            >
              Clear All
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setSelectedTimeframes(['1m', '5m', '15m', '1h', '4h', '1d'])}
            >
              Select Common
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Data Summary */}
      {dataSummary && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Cached Data Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {dataSummary.total_datasets}
                </div>
                <div className="text-sm text-blue-800">Total Datasets</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {Object.keys(supportedTimeframes).length}
                </div>
                <div className="text-sm text-green-800">Supported Timeframes</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {new Set(dataSummary.datasets.map(d => d.symbol)).size}
                </div>
                <div className="text-sm text-purple-800">Unique Symbols</div>
              </div>
            </div>

            {dataSummary.datasets.length > 0 && (
              <div className="max-h-64 overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left p-2">Symbol</th>
                      <th className="text-left p-2">Timeframe</th>
                      <th className="text-right p-2">Candles</th>
                      <th className="text-left p-2">Date Range</th>
                      <th className="text-left p-2">Updated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dataSummary.datasets.slice(0, 20).map((dataset, index) => (
                      <tr key={index} className="border-t">
                        <td className="p-2 font-medium">{dataset.symbol}</td>
                        <td className="p-2">
                          <Badge className={getTimeframeBadgeColor(dataset.timeframe)}>
                            {dataset.timeframe}
                          </Badge>
                        </td>
                        <td className="p-2 text-right">{formatNumber(dataset.total_candles)}</td>
                        <td className="p-2 text-xs">
                          {formatDate(dataset.earliest_date)} - {formatDate(dataset.latest_date)}
                        </td>
                        <td className="p-2 text-xs text-gray-500">
                          {formatDate(dataset.last_updated)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {dataSummary.datasets.length > 20 && (
                  <div className="text-center p-2 text-sm text-gray-500">
                    ... and {dataSummary.datasets.length - 20} more datasets
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Fetched Data Results */}
      {historicalData.timeframes && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Fetched Data: {historicalData.symbol}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <p className="text-green-800 text-sm">
                ✅ Successfully fetched {historicalData.total_datasets} datasets in {historicalData.fetch_duration_seconds?.toFixed(2)}s
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(historicalData.timeframes).map(([tf, data]) => (
                <div key={tf} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <Badge className={getTimeframeBadgeColor(tf)}>
                      {tf}
                    </Badge>
                    <span className="text-sm font-medium">
                      {formatNumber(data.total_candles)} candles
                    </span>
                  </div>
                  
                  {data.total_candles > 0 ? (
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-gray-500">Range:</span>
                        <div className="text-xs">
                          {formatDate(data.earliest_date)} - {formatDate(data.latest_date)}
                        </div>
                      </div>
                      {data.data && data.data.length > 0 && (
                        <div>
                          <span className="text-gray-500">Latest Price:</span>
                          <div className="font-medium">
                            ${parseFloat(data.data[data.data.length - 1].close).toLocaleString()}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500">No data available</div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default HistoricalDataPanel;