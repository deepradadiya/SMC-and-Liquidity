#!/usr/bin/env python3
"""
Demo: Chart with Historical Data
Shows how to use the historical data API to create charts
"""

import asyncio
import aiohttp
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

async def fetch_and_chart_data():
    """Fetch historical data and create charts"""
    
    base_url = "http://localhost:8000/api/historical"
    symbol = "BTCUSDT"
    
    async with aiohttp.ClientSession() as session:
        
        print(f"📊 Fetching historical data for {symbol}...")
        
        # Fetch multiple timeframes
        timeframes = "1h,4h,1d"
        async with session.get(f"{base_url}/fetch/{symbol}?timeframes={timeframes}") as response:
            if response.status == 200:
                data = await response.json()
                
                print(f"✅ Fetched {data['total_datasets']} datasets")
                
                # Create subplots for different timeframes
                fig, axes = plt.subplots(3, 1, figsize=(15, 12))
                fig.suptitle(f'{symbol} Historical Data - Multiple Timeframes', fontsize=16)
                
                for i, (tf, tf_data) in enumerate(data['timeframes'].items()):
                    if tf_data['total_candles'] > 0 and tf_data['data']:
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(tf_data['data'])
                        df['datetime'] = pd.to_datetime(df['datetime'])
                        
                        # Use last 1000 candles for better visualization
                        df_plot = df.tail(1000).copy()
                        
                        ax = axes[i]
                        
                        # Plot candlestick-style chart
                        for idx, row in df_plot.iterrows():
                            color = 'green' if row['close'] >= row['open'] else 'red'
                            
                            # Body
                            body_height = abs(row['close'] - row['open'])
                            body_bottom = min(row['open'], row['close'])
                            
                            ax.bar(row['datetime'], body_height, bottom=body_bottom, 
                                  width=pd.Timedelta(hours=1 if tf == '1h' else 4 if tf == '4h' else 24),
                                  color=color, alpha=0.7, edgecolor=color)
                            
                            # Wicks
                            ax.plot([row['datetime'], row['datetime']], 
                                   [row['low'], row['high']], 
                                   color='black', linewidth=0.5)
                        
                        # Formatting
                        ax.set_title(f'{tf} - {len(df_plot)} candles (Latest: ${df_plot.iloc[-1]["close"]:.2f})')
                        ax.set_ylabel('Price ($)')
                        ax.grid(True, alpha=0.3)
                        
                        # Format x-axis
                        if tf == '1h':
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
                            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
                        elif tf == '4h':
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
                        else:  # 1d
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                        
                        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
                        
                        print(f"   📈 {tf}: {tf_data['total_candles']} total candles, showing last {len(df_plot)}")
                
                plt.tight_layout()
                plt.savefig(f'{symbol}_historical_chart.png', dpi=300, bbox_inches='tight')
                print(f"💾 Chart saved as {symbol}_historical_chart.png")
                
                # Show some statistics
                print(f"\n📊 Data Statistics for {symbol}:")
                for tf, tf_data in data['timeframes'].items():
                    if tf_data['total_candles'] > 0:
                        df = pd.DataFrame(tf_data['data'])
                        latest_price = float(df.iloc[-1]['close'])
                        earliest_price = float(df.iloc[0]['close'])
                        total_return = ((latest_price - earliest_price) / earliest_price) * 100
                        
                        print(f"   {tf}: {tf_data['total_candles']} candles")
                        print(f"      📅 {tf_data['earliest_date']} to {tf_data['latest_date']}")
                        print(f"      💰 ${earliest_price:.2f} → ${latest_price:.2f} ({total_return:+.1f}%)")
                        print(f"      📈 High: ${df['high'].astype(float).max():.2f}")
                        print(f"      📉 Low: ${df['low'].astype(float).min():.2f}")
                        print()
                
            else:
                print(f"❌ Error fetching data: {response.status}")

async def create_volume_analysis():
    """Create volume analysis chart"""
    
    base_url = "http://localhost:8000/api/historical"
    symbol = "BTCUSDT"
    
    async with aiohttp.ClientSession() as session:
        
        print(f"📊 Creating volume analysis for {symbol}...")
        
        # Fetch 1h data for volume analysis
        async with session.get(f"{base_url}/fetch/{symbol}/1h") as response:
            if response.status == 200:
                data = await response.json()
                
                if data['total_candles'] > 0:
                    df = pd.DataFrame(data['data'])
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df['volume'] = df['volume'].astype(float)
                    df['close'] = df['close'].astype(float)
                    
                    # Use last 500 candles
                    df_plot = df.tail(500).copy()
                    
                    # Create volume analysis
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), 
                                                  gridspec_kw={'height_ratios': [3, 1]})
                    
                    # Price chart
                    ax1.plot(df_plot['datetime'], df_plot['close'], linewidth=1, color='blue')
                    ax1.set_title(f'{symbol} Price and Volume Analysis (1h)')
                    ax1.set_ylabel('Price ($)')
                    ax1.grid(True, alpha=0.3)
                    
                    # Volume chart
                    colors = ['green' if close >= open_price else 'red' 
                             for close, open_price in zip(df_plot['close'], df_plot['open'])]
                    
                    ax2.bar(df_plot['datetime'], df_plot['volume'], 
                           color=colors, alpha=0.7, width=pd.Timedelta(hours=0.8))
                    ax2.set_ylabel('Volume')
                    ax2.set_xlabel('Date')
                    ax2.grid(True, alpha=0.3)
                    
                    # Format x-axis
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=7))
                    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
                    
                    plt.tight_layout()
                    plt.savefig(f'{symbol}_volume_analysis.png', dpi=300, bbox_inches='tight')
                    print(f"💾 Volume analysis saved as {symbol}_volume_analysis.png")
                    
                    # Volume statistics
                    avg_volume = df_plot['volume'].mean()
                    max_volume = df_plot['volume'].max()
                    print(f"📊 Volume Stats: Avg: {avg_volume:,.0f}, Max: {max_volume:,.0f}")

def main():
    """Main demo function"""
    print("🎯 Historical Data Chart Demo")
    print("=" * 40)
    
    try:
        # Create charts
        asyncio.run(fetch_and_chart_data())
        asyncio.run(create_volume_analysis())
        
        print("\n✅ Demo completed!")
        print("📁 Check the generated PNG files:")
        print("   - BTCUSDT_historical_chart.png")
        print("   - BTCUSDT_volume_analysis.png")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()