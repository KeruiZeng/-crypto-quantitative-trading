#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 阶段1系统快速修复
===================
基于测试结果的针对性修复
"""

import pandas as pd
import numpy as np

# 先验证calculate_strategy_metrics函数的问题
def test_calculate_strategy_metrics_debug():
    """专门调试calculate_strategy_metrics函数"""
    
    print("🔍 调试calculate_strategy_metrics函数")
    print("=" * 50)
    
    # 模拟加载数据
    try:
        btc_data = pd.read_csv('BTCUSDT_minute_data_2023_2026.csv')
        btc_data['Date'] = pd.to_datetime(btc_data['Open Time'])
        print(f"✅ 数据加载成功: {len(btc_data)} 行")
        
        # 模拟策略配置
        strategy_config = {
            'BTCUSDT_FixedBreakout': {
                'lookback_period': 20,
                'breakout_threshold': 1.8,
                'stop_loss': 0.03,
                'take_profit': 0.06
            }
        }
        
        # 测试特定日期的metrics计算
        current_date = '2023-02-12'
        symbol = 'BTCUSDT_FixedBreakout'
        lookback_days = 14
        
        print(f"\n🎯 测试参数:")
        print(f"   策略: {symbol}")
        print(f"   当前日期: {current_date}")
        print(f"   回看天数: {lookback_days}")
        
        # 步骤1：找到当前日期索引
        current_date_pd = pd.to_datetime(current_date)
        valid_dates = btc_data[btc_data['Date'] <= current_date_pd]
        current_idx = len(valid_dates) - 1
        print(f"\n📍 当前索引: {current_idx}")
        
        # 步骤2：计算历史数据范围
        start_idx = max(0, current_idx - lookback_days + 1)
        historical_data = btc_data.iloc[start_idx:current_idx+1]
        print(f"📊 历史数据范围: {start_idx} - {current_idx} ({len(historical_data)} 行)")
        print(f"📅 时间范围: {historical_data['Date'].min()} 至 {historical_data['Date'].max()}")
        
        # 步骤3：使用固定的简单信号生成（避免复杂函数）
        config = strategy_config[symbol]
        
        # 计算技术指标
        df = historical_data.copy()
        df['SMA'] = df['Close'].rolling(window=config['lookback_period']).mean()
        df['Price_Change'] = df['Close'].pct_change()
        df['Volatility'] = df['Price_Change'].rolling(window=config['lookback_period']).std()
        
        # 生成信号
        signals = []
        for i in range(len(df)):
            if i < config['lookback_period']:
                signals.append(0)
                continue
            
            current_price = df.iloc[i]['Close']
            sma = df.iloc[i]['SMA']
            volatility = df.iloc[i]['Volatility']
            
            # 突破策略信号
            if pd.isna(sma) or pd.isna(volatility):
                signals.append(0)
            elif current_price > sma * (1 + config['breakout_threshold'] * volatility):
                signals.append(1)  # 买入
            elif current_price < sma * (1 - config['breakout_threshold'] * volatility):
                signals.append(-1)  # 卖出
            else:
                signals.append(0)  # 持有
        
        signals = np.array(signals)
        
        print(f"\n🎯 信号生成结果:")
        print(f"   信号数量: {len(signals)}")
        print(f"   买入: {len(signals[signals == 1])}")
        print(f"   卖出: {len(signals[signals == -1])}")
        print(f"   持有: {len(signals[signals == 0])}")
        
        # 步骤4：计算收益
        if len(signals) < 5:
            print(f"❌ 信号数量不足: {len(signals)}")
            return 0.0, 0.1, 0.0
        
        prices = df['Close'].values
        returns = []
        
        for i in range(1, len(signals)):
            if signals[i-1] != 0:
                price_change = (prices[i] - prices[i-1]) / prices[i-1]
                strategy_return = signals[i-1] * price_change
                returns.append(strategy_return)
                
                # 调试前几个收益计算
                if len(returns) <= 5:
                    print(f"   收益 {len(returns)}: 信号={signals[i-1]}, 价格变化={price_change:.6f}, 策略收益={strategy_return:.6f}")
        
        print(f"\n📊 收益计算结果:")
        print(f"   有效交易数: {len(returns)}")
        
        if len(returns) == 0:
            print(f"❌ 无有效交易")
            return 0.0, 0.1, 0.0
        
        total_return = np.sum(returns)
        volatility = np.std(returns) if len(returns) > 1 else 0.1
        volatility = max(volatility, 0.01)
        sharpe = total_return / volatility if volatility > 0 else 0.0
        
        print(f"   总收益: {total_return:.6f} ({total_return*100:.4f}%)")
        print(f"   波动率: {volatility:.6f} ({volatility*100:.4f}%)")
        print(f"   夏普比率: {sharpe:.6f}")
        
        print(f"\n✅ 函数应该返回: ({total_return:.6f}, {volatility:.6f}, {sharpe:.6f})")
        
        return total_return, volatility, sharpe
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_calculate_strategy_metrics_debug()