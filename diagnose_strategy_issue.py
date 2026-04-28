#!/usr/bin/env python3
"""
诊断策略失效问题
检查2024年6月30日前后策略计算的数据点数量
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_minute_data(symbol):
    """加载分钟级数据"""
    print(f"加载 {symbol} 数据...")
    df = pd.read_csv(f'{symbol}_minute_data_2023_2026.csv')
    df['timestamp'] = pd.to_datetime(df['Open Time'])
    df.set_index('timestamp', inplace=True)
    
    # 计算价格变化
    df['returns'] = df['Close'].pct_change()
    df = df.dropna()
    
    return df[['Close', 'returns']]

def calculate_fixed_breakout_strategy(df, lookback=1440, transaction_cost=0.001):
    """计算固定突破策略"""
    df = df.copy()
    
    # 计算1440分钟（1天）滚动最高/最低
    df['highest'] = df['Close'].rolling(window=lookback, min_periods=lookback//2).max()
    df['lowest'] = df['Close'].rolling(window=lookback, min_periods=lookback//2).min()
    
    # 生成交易信号
    signals = pd.Series(0, index=df.index)
    
    for i in range(1, len(df)):
        if pd.notna(df.iloc[i]['highest']) and pd.notna(df.iloc[i]['lowest']):
            if df.iloc[i]['Close'] > df.iloc[i-1]['highest']:
                signals.iloc[i] = 1
            elif df.iloc[i]['Close'] < df.iloc[i-1]['lowest']:
                signals.iloc[i] = -1
            else:
                signals.iloc[i] = signals.iloc[i-1]
        else:
            signals.iloc[i] = signals.iloc[i-1] if i > 0 else 0
    
    # 计算策略收益
    df['strategy_returns'] = signals.shift(1) * df['returns'] - signals.diff().abs() * transaction_cost
    
    return df, signals

def check_data_availability(strategy_df, check_date, lookback_days=90):
    """检查指定日期的数据可用性"""
    start_date = check_date - timedelta(days=lookback_days)
    
    print(f"\n检查日期: {check_date.strftime('%Y-%m-%d')}")
    print(f"回看起始: {start_date.strftime('%Y-%m-%d')}")
    
    # 筛选时间段
    recent_data = strategy_df[(strategy_df.index >= start_date) & (strategy_df.index <= check_date)]
    
    print(f"时间段内数据点: {len(recent_data)}")
    print(f"数据覆盖天数: {len(recent_data) / (24 * 60):.2f}")
    
    # 检查是否满足回测条件
    meets_min_points = len(recent_data) >= 1000
    days = len(recent_data) / (24 * 60)
    meets_min_days = days >= 10
    
    print(f"满足1000点要求: {meets_min_points}")
    print(f"满足10天要求: {meets_min_days}")
    
    if meets_min_points and meets_min_days:
        # 计算策略指标
        strategy_returns = recent_data['strategy_returns']
        total_return = (1 + strategy_returns).prod() - 1
        annualized_return = (1 + total_return) ** (365 / days) - 1
        volatility = strategy_returns.std() * np.sqrt(365 * 24 * 60)
        
        print(f"策略收益: {annualized_return:.1%}")
        print(f"策略波动: {volatility:.1%}")
        
        return True
    else:
        return False

def main():
    print("=== 策略失效问题诊断 ===\n")
    
    # 加载数据
    btc_data = load_minute_data('BTCUSDT')
    eth_data = load_minute_data('ETHUSDT')
    
    # 计算策略
    print("\n计算BTC固定突破策略...")
    btc_strategy, btc_signals = calculate_fixed_breakout_strategy(btc_data)
    
    print("计算ETH固定突破策略...")
    eth_strategy, eth_signals = calculate_fixed_breakout_strategy(eth_data)
    
    # 检查关键日期
    check_dates = [
        datetime(2024, 6, 28),
        datetime(2024, 6, 30), 
        datetime(2024, 7, 2),
        datetime(2024, 7, 7),
        datetime(2024, 7, 15),
        datetime(2024, 8, 1),
        datetime(2024, 9, 1),
    ]
    
    print("\n=== BTC策略诊断 ===")
    for date in check_dates:
        is_valid = check_data_availability(btc_strategy, date)
        print(f"策略有效性: {'✅' if is_valid else '❌'}")
        print("-" * 50)
    
    print("\n=== ETH策略诊断 ===")
    for date in check_dates:
        is_valid = check_data_availability(eth_strategy, date)
        print(f"策略有效性: {'✅' if is_valid else '❌'}")
        print("-" * 50)

if __name__ == "__main__":
    main()