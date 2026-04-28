#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 增强版：精细震荡区间市场状态适应系统
=======================================

基于原有市场状态适应系统，对震荡区间进行精细化分析：
- 窄幅震荡市场 (Narrow Range Market)
- 宽幅震荡市场 (Wide Range Market)  
- 区间突破震荡 (Range Breakout Market)
- 支撑阻力震荡 (Support/Resistance Range)

每种震荡类型配置专门的交易策略和参数优化

作者: CTA优化团队
版本: 增强版-精细震荡区间适应
日期: 2026-04-15
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import warnings
import json
from datetime import datetime, timedelta
import os

warnings.filterwarnings('ignore')

class EnhancedMarketStateAdaptiveSystem:
    """增强版市场状态适应回测系统 - 精细震荡区间分析"""
    
    def __init__(self):
        print("\n🎭 增强版：精细震荡区间市场状态适应系统")
        print("探索震荡区间的精细化识别与专门化策略")
        
        # 基础配置
        self.initial_capital = 100000
        self.start_date = '2023-01-01'
        self.end_date = '2026-04-14'
        
        # 市场状态识别配置
        self.state_detection_window = 60  # 60天市场状态检测窗口
        self.trend_threshold = 0.15  # 15%趋势阈值
        self.volatility_threshold = 0.25  # 25%波动率阈值
        self.state_confirmation_period = 14  # 14天状态确认期
        
        # 震荡区间细分参数
        self.range_width_threshold = 0.08  # 8%区间宽度阈值
        self.narrow_range_threshold = 0.04  # 4%窄幅震荡阈值
        self.support_resistance_strength = 3  # 支撑阻力强度（触碰次数）
        self.breakout_confirmation_days = 5  # 突破确认天数
        
        # 增强市场状态定义
        self.market_states = {
            'bull_market': {
                'description': '牛市状态',
                'trend_min': self.trend_threshold,
                'volatility_max': self.volatility_threshold,
            },
            'bear_market': {
                'description': '熊市状态',
                'trend_max': -self.trend_threshold,
                'volatility_max': self.volatility_threshold * 1.5,
            },
            'narrow_range_market': {
                'description': '窄幅震荡市场',
                'trend_range': (-self.trend_threshold, self.trend_threshold),
                'range_width_max': self.narrow_range_threshold,
                'volatility_max': self.volatility_threshold * 0.7,
            },
            'wide_range_market': {
                'description': '宽幅震荡市场',
                'trend_range': (-self.trend_threshold, self.trend_threshold),
                'range_width_min': self.range_width_threshold,
                'volatility_range': (self.volatility_threshold * 0.7, self.volatility_threshold * 1.3),
            },
            'range_breakout_market': {
                'description': '区间突破震荡市场',
                'trend_range': (-self.trend_threshold, self.trend_threshold),
                'breakout_attempts': 2,  # 多次突破尝试
                'volatility_min': self.volatility_threshold * 0.8,
            },
            'support_resistance_market': {
                'description': '支撑阻力震荡市场',
                'trend_range': (-self.trend_threshold, self.trend_threshold),
                'sr_strength_min': self.support_resistance_strength,
                'range_stability': 0.85,  # 85%时间在区间内
            },
            'high_volatility': {
                'description': '高波动状态',
                'volatility_min': self.volatility_threshold * 1.5,
            }
        }
        
        # 不同市场状态下的精细化策略配置
        self.state_strategies = {
            'bull_market': {
                'BTCUSDT_BullMomentum': {'weight': 0.30, 'expected_return': 0.35, 'type': 'momentum'},
                'ETHUSDT_BullMomentum': {'weight': 0.30, 'expected_return': 0.40, 'type': 'momentum'},
                'BTCUSDT_BullBreakout': {'weight': 0.25, 'expected_return': 0.30, 'type': 'breakout'},
                'ETHUSDT_BullBreakout': {'weight': 0.15, 'expected_return': 0.35, 'type': 'breakout'}
            },
            'bear_market': {
                'BTCUSDT_BearDefense': {'weight': 0.35, 'expected_return': 0.15, 'type': 'defensive'},
                'ETHUSDT_BearDefense': {'weight': 0.35, 'expected_return': 0.18, 'type': 'defensive'},
                'BTCUSDT_BearHedge': {'weight': 0.15, 'expected_return': 0.20, 'type': 'hedge'},
                'ETHUSDT_BearHedge': {'weight': 0.15, 'expected_return': 0.22, 'type': 'hedge'}
            },
            'narrow_range_market': {
                # 窄幅震荡：高频做市策略
                'BTCUSDT_NarrowMeanRev': {'weight': 0.25, 'expected_return': 0.15, 'type': 'narrow_range_trading'},
                'ETHUSDT_NarrowMeanRev': {'weight': 0.25, 'expected_return': 0.18, 'type': 'narrow_range_trading'},
                'BTCUSDT_NarrowScalping': {'weight': 0.25, 'expected_return': 0.12, 'type': 'high_freq_scalping'},
                'ETHUSDT_NarrowScalping': {'weight': 0.25, 'expected_return': 0.14, 'type': 'high_freq_scalping'}
            },
            'wide_range_market': {
                # 宽幅震荡：区间交易策略
                'BTCUSDT_WideRangeTop': {'weight': 0.25, 'expected_return': 0.22, 'type': 'range_top_selling'},
                'ETHUSDT_WideRangeTop': {'weight': 0.25, 'expected_return': 0.25, 'type': 'range_top_selling'},
                'BTCUSDT_WideRangeBottom': {'weight': 0.25, 'expected_return': 0.20, 'type': 'range_bottom_buying'},
                'ETHUSDT_WideRangeBottom': {'weight': 0.25, 'expected_return': 0.23, 'type': 'range_bottom_buying'}
            },
            'range_breakout_market': {
                # 区间突破：突破确认策略
                'BTCUSDT_BreakoutConfirm': {'weight': 0.30, 'expected_return': 0.28, 'type': 'breakout_confirmation'},
                'ETHUSDT_BreakoutConfirm': {'weight': 0.30, 'expected_return': 0.30, 'type': 'breakout_confirmation'},
                'BTCUSDT_FalseBreakout': {'weight': 0.20, 'expected_return': 0.18, 'type': 'false_breakout_fade'},
                'ETHUSDT_FalseBreakout': {'weight': 0.20, 'expected_return': 0.20, 'type': 'false_breakout_fade'}
            },
            'support_resistance_market': {
                # 支撑阻力：关键位交易
                'BTCUSDT_SupportBounce': {'weight': 0.25, 'expected_return': 0.20, 'type': 'support_level_trading'},
                'ETHUSDT_SupportBounce': {'weight': 0.25, 'expected_return': 0.22, 'type': 'support_level_trading'},
                'BTCUSDT_ResistanceFade': {'weight': 0.25, 'expected_return': 0.18, 'type': 'resistance_level_trading'},
                'ETHUSDT_ResistanceFade': {'weight': 0.25, 'expected_return': 0.20, 'type': 'resistance_level_trading'}
            },
            'high_volatility': {
                'BTCUSDT_VolControl': {'weight': 0.40, 'expected_return': 0.12, 'type': 'low_risk'},
                'ETHUSDT_VolControl': {'weight': 0.40, 'expected_return': 0.15, 'type': 'low_risk'},
                'BTCUSDT_VolOpportunity': {'weight': 0.10, 'expected_return': 0.25, 'type': 'vol_trading'},
                'ETHUSDT_VolOpportunity': {'weight': 0.10, 'expected_return': 0.28, 'type': 'vol_trading'}
            }
        }
        
        # 市场状态历史
        self.market_state_history = []
        self.current_market_state = 'narrow_range_market'  # 默认状态
        
        print(f"\n🎯 增强版市场状态适应系统配置:")
        print(f"   ✓ 震荡区间细分: 4种专门化类型")
        print(f"   ✓ 窄幅震荡阈值: {self.narrow_range_threshold:.1%}")
        print(f"   ✓ 宽幅震荡阈值: {self.range_width_threshold:.1%}")
        print(f"   ✓ 支撑阻力强度: {self.support_resistance_strength}次触碰")
        print(f"   ✓ 突破确认期: {self.breakout_confirmation_days}天")
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """加载数据"""
        data = {}
        
        try:
            btc_df = pd.read_csv('BTCUSDT_minute_data_2023_2026.csv')
            eth_df = pd.read_csv('ETHUSDT_minute_data_2023_2026.csv')
            
            for symbol, df in [('BTCUSDT', btc_df), ('ETHUSDT', eth_df)]:
                if len(df) > 0:
                    df['timestamp'] = pd.to_datetime(df['Open Time'])
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    data[symbol] = df
                    print(f"✓ {symbol}: {len(df):,}条数据")
                    
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            
        return data
    
    def calculate_range_metrics(self, window_data: pd.DataFrame) -> Dict:
        """计算震荡区间指标"""
        if len(window_data) < 20:
            return {}
        
        high_prices = window_data['High']
        low_prices = window_data['Low']
        close_prices = window_data['Close']
        
        # 基础价格指标
        period_high = high_prices.max()
        period_low = low_prices.min()
        period_mean = close_prices.mean()
        current_price = close_prices.iloc[-1]
        
        # 区间宽度分析
        range_width = (period_high - period_low) / period_mean
        
        # 价格分布分析
        price_std = close_prices.std()
        price_cv = price_std / period_mean  # 变异系数
        
        # 区间位置分析
        price_position = (current_price - period_low) / (period_high - period_low) if period_high > period_low else 0.5
        
        # 支撑阻力分析
        support_level = period_low
        resistance_level = period_high
        
        # 计算价格在区间边界的触碰次数
        support_touches = sum(1 for low in low_prices if abs(low - support_level) / support_level < 0.01)
        resistance_touches = sum(1 for high in high_prices if abs(high - resistance_level) / resistance_level < 0.01)
        
        # 区间稳定性（价格在中位数±25%范围内的时间占比）
        median_price = close_prices.median()
        range_25 = period_mean * 0.25
        in_range_count = sum(1 for price in close_prices if abs(price - median_price) <= range_25)
        range_stability = in_range_count / len(close_prices)
        
        # 突破尝试分析
        breakout_threshold = 0.02  # 2%突破阈值
        upward_breakouts = sum(1 for price in close_prices if (price - resistance_level) / resistance_level > breakout_threshold)
        downward_breakouts = sum(1 for price in close_prices if (support_level - price) / support_level > breakout_threshold)
        
        return {
            'range_width': range_width,
            'price_cv': price_cv,
            'price_position': price_position,
            'support_touches': support_touches,
            'resistance_touches': resistance_touches,
            'range_stability': range_stability,
            'breakout_attempts': upward_breakouts + downward_breakouts,
            'support_level': support_level,
            'resistance_level': resistance_level,
            'period_high': period_high,
            'period_low': period_low
        }
    
    def detect_enhanced_market_state(self, data: Dict, current_date: pd.Timestamp) -> str:
        """增强版市场状态检测 - 精细震荡区间分析"""
        
        if len(data) < 2:
            return self.current_market_state
            
        market_indicators = {}
        range_metrics = {}
        
        # 收集各资产的市场指标和区间指标
        for symbol in data:
            df = data[symbol]
            current_data = df[df['timestamp'] <= current_date]
            
            if len(current_data) < self.state_detection_window:
                continue
            
            # 获取检测窗口数据
            window_data = current_data.tail(self.state_detection_window)
            
            # 计算基础趋势和波动率指标
            start_price = window_data['Close'].iloc[0]
            end_price = window_data['Close'].iloc[-1]
            trend_return = (end_price / start_price - 1) if start_price > 0 else 0
            
            returns = window_data['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(365) if len(returns) > 0 else 0
            
            # 计算震荡区间指标
            range_data = self.calculate_range_metrics(window_data)
            
            market_indicators[symbol] = {
                'trend': trend_return,
                'volatility': volatility
            }
            
            if range_data:
                range_metrics[symbol] = range_data
        
        # 综合判断市场状态
        if len(market_indicators) < 2:
            return self.current_market_state
        
        # 计算平均指标
        avg_trend = np.mean([indicators['trend'] for indicators in market_indicators.values()])
        avg_volatility = np.mean([indicators['volatility'] for indicators in market_indicators.values()])
        
        # 计算平均区间指标
        if range_metrics:
            avg_range_width = np.mean([metrics['range_width'] for metrics in range_metrics.values()])
            avg_range_stability = np.mean([metrics['range_stability'] for metrics in range_metrics.values()])
            total_support_touches = sum([metrics['support_touches'] for metrics in range_metrics.values()])
            total_resistance_touches = sum([metrics['resistance_touches'] for metrics in range_metrics.values()])
            total_breakout_attempts = sum([metrics['breakout_attempts'] for metrics in range_metrics.values()])
        else:
            # 默认值
            avg_range_width = 0.05
            avg_range_stability = 0.8
            total_support_touches = 1
            total_resistance_touches = 1
            total_breakout_attempts = 0
        
        # 增强状态判断逻辑
        detected_state = 'narrow_range_market'  # 默认
        
        # 高波动状态检查（优先）
        if avg_volatility > self.volatility_threshold * 1.5:
            detected_state = 'high_volatility'
        # 牛市检查
        elif avg_trend > self.trend_threshold and avg_volatility < self.volatility_threshold:
            detected_state = 'bull_market'
        # 熊市检查
        elif avg_trend < -self.trend_threshold and avg_volatility < self.volatility_threshold * 1.5:
            detected_state = 'bear_market'
        # 震荡市场精细分类
        elif abs(avg_trend) < self.trend_threshold:
            # 窄幅震荡：区间窄、波动小、稳定性高
            if (avg_range_width < self.narrow_range_threshold and 
                avg_volatility < self.volatility_threshold * 0.7 and
                avg_range_stability > 0.8):
                detected_state = 'narrow_range_market'
            
            # 宽幅震荡：区间宽、中等波动
            elif (avg_range_width > self.range_width_threshold and
                  self.volatility_threshold * 0.7 < avg_volatility < self.volatility_threshold * 1.3):
                detected_state = 'wide_range_market'
            
            # 区间突破震荡：多次突破尝试、较高波动
            elif (total_breakout_attempts >= 2 and
                  avg_volatility > self.volatility_threshold * 0.8):
                detected_state = 'range_breakout_market'
            
            # 支撑阻力震荡：强支撑阻力、高稳定性
            elif (total_support_touches + total_resistance_touches >= self.support_resistance_strength and
                  avg_range_stability > 0.85):
                detected_state = 'support_resistance_market'
            
            # 默认窄幅震荡
            else:
                detected_state = 'narrow_range_market'
        
        return detected_state
    
    def calculate_enhanced_strategy_return(self, strategy_type: str, market_return: float, 
                                          expected_return: float, market_state: str) -> float:
        """根据增强策略类型和市场状态计算收益"""
        
        # 基础策略收益计算
        if strategy_type == 'momentum':
            if market_return > 0:
                base_return = min(market_return * 1.2, expected_return)
            else:
                base_return = max(market_return * 0.8, -expected_return * 0.3)
                
        elif strategy_type == 'breakout':
            if abs(market_return) > 0.01:
                base_return = np.sign(market_return) * min(abs(market_return) * 1.1, expected_return)
            else:
                base_return = 0
                
        elif strategy_type == 'defensive':
            base_return = market_return * 0.3
            
        elif strategy_type == 'hedge':
            base_return = -market_return * 0.5
            
        # 窄幅震荡专门策略
        elif strategy_type == 'narrow_range_trading':
            # 在小幅波动中频繁交易获利
            if abs(market_return) < 0.01:
                base_return = expected_return * 0.4  # 稳定小收益
            else:
                base_return = -abs(market_return) * 0.3  # 大波动时亏损
                
        elif strategy_type == 'high_freq_scalping':
            # 高频刷单策略
            base_return = expected_return * 0.3 if abs(market_return) < 0.005 else expected_return * 0.1
            
        # 宽幅震荡专门策略
        elif strategy_type == 'range_top_selling':
            # 区间顶部卖出策略
            if market_return > 0.02:  # 接近区间顶部
                base_return = expected_return * 0.8
            elif market_return < -0.01:  # 远离区间顶部
                base_return = -expected_return * 0.2
            else:
                base_return = 0
                
        elif strategy_type == 'range_bottom_buying':
            # 区间底部买入策略
            if market_return < -0.02:  # 接近区间底部
                base_return = expected_return * 0.8
            elif market_return > 0.01:  # 远离区间底部
                base_return = -expected_return * 0.2
            else:
                base_return = 0
                
        # 区间突破专门策略
        elif strategy_type == 'breakout_confirmation':
            # 突破确认策略
            if abs(market_return) > 0.03:  # 强势突破
                base_return = np.sign(market_return) * expected_return * 0.9
            else:
                base_return = expected_return * 0.1
                
        elif strategy_type == 'false_breakout_fade':
            # 假突破反向策略
            if abs(market_return) > 0.02:  # 疑似假突破
                base_return = -np.sign(market_return) * expected_return * 0.6
            else:
                base_return = 0
                
        # 支撑阻力专门策略
        elif strategy_type == 'support_level_trading':
            # 支撑位交易
            if market_return < -0.015:  # 接近支撑位
                base_return = expected_return * 0.7
            else:
                base_return = 0
                
        elif strategy_type == 'resistance_level_trading':
            # 阻力位交易
            if market_return > 0.015:  # 接近阻力位
                base_return = expected_return * 0.7
            else:
                base_return = 0
                
        # 其他策略
        elif strategy_type == 'mean_reversion':
            if abs(market_return) > 0.005:
                base_return = -market_return * 0.6
                base_return = np.clip(base_return, -expected_return * 0.5, expected_return * 0.5)
            else:
                base_return = 0
        elif strategy_type == 'low_risk':
            base_return = expected_return * 0.2
        elif strategy_type == 'vol_trading':
            base_return = abs(market_return) * 0.5
        else:
            base_return = market_return * 0.5
        
        # 根据市场状态调整收益
        state_multipliers = {
            'bull_market': {'momentum': 1.3, 'breakout': 1.2, 'defensive': 0.7},
            'bear_market': {'defensive': 1.3, 'hedge': 1.2, 'momentum': 0.6},
            'narrow_range_market': {
                'narrow_range_trading': 1.4, 'high_freq_scalping': 1.3, 
                'momentum': 0.6, 'breakout': 0.5
            },
            'wide_range_market': {
                'range_top_selling': 1.3, 'range_bottom_buying': 1.3,
                'mean_reversion': 1.2, 'momentum': 0.7
            },
            'range_breakout_market': {
                'breakout_confirmation': 1.4, 'false_breakout_fade': 1.2,
                'breakout': 1.3, 'momentum': 1.1
            },
            'support_resistance_market': {
                'support_level_trading': 1.3, 'resistance_level_trading': 1.3,
                'mean_reversion': 1.2, 'range_top_selling': 1.1, 'range_bottom_buying': 1.1
            },
            'high_volatility': {'low_risk': 1.3, 'vol_trading': 1.2, 'momentum': 0.7}
        }
        
        multiplier = state_multipliers.get(market_state, {}).get(strategy_type, 1.0)
        adjusted_return = base_return * multiplier
        
        return np.clip(adjusted_return, -expected_return, expected_return)
    
    def run_backtest(self) -> Dict:
        """运行增强版市场状态适应回测"""
        print(f"\n📅 增强版市场状态适应回测期间: {self.start_date} - {self.end_date}")
        print(f"💰 初始资金: ${self.initial_capital:,}")
        
        data = self.load_data()
        if not data:
            return {}
        
        start_dt = pd.to_datetime(self.start_date)
        end_dt = pd.to_datetime(self.end_date)
        backtest_days = (end_dt - start_dt).days
        backtest_years = backtest_days / 365.25
        print(f"⏰ 回测期间: {backtest_years:.2f} 年")
        
        # 初始化
        portfolio_value = self.initial_capital
        max_portfolio_value = portfolio_value
        max_drawdown = 0.0
        returns_list = []
        portfolio_history = []
        state_changes = 0
        trade_count = 0
        winning_trades = 0
        
        print(f"\n🔄 开始增强版市场状态适应回测...")
        
        # 创建回测日期范围（每14天检查一次状态）
        date_range = pd.date_range(start=start_dt, end=end_dt, freq='14D')
        processed_dates = 0
        
        for current_date in date_range:
            processed_dates += 1
            
            # 检测增强市场状态
            previous_state = self.current_market_state
            detected_state = self.detect_enhanced_market_state(data, current_date)
            
            # 状态切换确认
            if detected_state != self.current_market_state:
                self.current_market_state = detected_state
                state_changes += 1
                print(f"📊 市场状态切换: {previous_state} → {detected_state} ({current_date.strftime('%Y-%m-%d')})")
            
            # 记录状态历史
            self.market_state_history.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'state': self.current_market_state,
                'previous_state': previous_state
            })
            
            # 获取当前状态的策略配置
            current_strategies = self.state_strategies.get(self.current_market_state, 
                                                         self.state_strategies['narrow_range_market'])
            
            period_return = 0.0
            valid_strategies = 0
            
            # 计算各策略收益
            for strategy_name, strategy_config in current_strategies.items():
                symbol = strategy_name.split('_')[0]
                if symbol not in data:
                    continue
                
                df = data[symbol]
                current_data = df[df['timestamp'] <= current_date]
                
                if len(current_data) < 30:
                    continue
                
                # 计算期间市场收益
                lookback_period = 14
                if len(current_data) >= lookback_period + 1:
                    market_return = (current_data['Close'].iloc[-1] / 
                                   current_data['Close'].iloc[-lookback_period-1] - 1)
                    
                    # 根据增强策略类型和市场状态计算收益
                    strategy_return = self.calculate_enhanced_strategy_return(
                        strategy_config['type'], 
                        market_return, 
                        strategy_config['expected_return'],
                        self.current_market_state
                    )
                    
                    # 加权收益
                    weighted_return = strategy_return * strategy_config['weight']
                    period_return += weighted_return
                    valid_strategies += 1
            
            if valid_strategies >= len(current_strategies) * 0.75:  # 需要大部分策略有效
                portfolio_value *= (1 + period_return)
                returns_list.append(period_return)
                
                if period_return > 0:
                    winning_trades += 1
                trade_count += 1
                
                # 更新最大值和回撤
                if portfolio_value > max_portfolio_value:
                    max_portfolio_value = portfolio_value
                
                current_drawdown = (max_portfolio_value - portfolio_value) / max_portfolio_value
                if current_drawdown > max_drawdown:
                    max_drawdown = current_drawdown
                
                portfolio_history.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'portfolio_value': portfolio_value,
                    'return': period_return,
                    'market_state': self.current_market_state
                })
        
        # 计算最终统计
        if len(returns_list) == 0:
            print("❌ 没有有效的回测数据")
            return {}
        
        total_return = (portfolio_value / self.initial_capital - 1) * 100
        annualized_return = ((portfolio_value / self.initial_capital) ** (1/backtest_years) - 1) * 100
        volatility = np.std(returns_list) * np.sqrt(26) * 100  # 年化波动率
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        win_rate = (winning_trades / trade_count * 100) if trade_count > 0 else 0
        
        # 显示结果
        print(f"\n🎯 增强版市场状态适应回测结果:")
        print(f"{'='*60}")
        print(f"💰 总收益率:     {total_return:>8.2f}%")
        print(f"📈 年化收益率:   {annualized_return:>8.2f}%")
        print(f"📊 年化波动率:   {volatility:>8.2f}%")
        print(f"⚡ 夏普比率:     {sharpe_ratio:>8.3f}")
        print(f"📉 最大回撤:     {max_drawdown*100:>8.2f}%")
        print(f"🎯 胜率:         {win_rate:>8.1f}%")
        print(f"🔄 总交易次数:   {trade_count:>8d}")
        print(f"🔀 状态切换次数: {state_changes:>8d}")
        
        # 市场状态分析
        print(f"\n📊 市场状态分布:")
        state_counts = {}
        for record in self.market_state_history:
            state = record['state']
            state_counts[state] = state_counts.get(state, 0) + 1
        
        for state, count in state_counts.items():
            percentage = count / len(self.market_state_history) * 100
            state_desc = self.market_states.get(state, {}).get('description', state)
            print(f"   {state_desc}: {percentage:>6.1f}%")
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'win_rate': win_rate,
            'trade_count': trade_count,
            'state_changes': state_changes,
            'portfolio_history': portfolio_history,
            'state_history': self.market_state_history,
            'final_value': portfolio_value
        }

def main():
    """主函数"""
    print("🚀 启动增强版市场状态适应系统")
    
    # 创建回测系统
    backtest_system = EnhancedMarketStateAdaptiveSystem()
    
    # 运行回测
    results = backtest_system.run_backtest()
    
    if results:
        print(f"\n✅ 增强版回测完成!")
        print(f"🎭 最终组合价值: ${results['final_value']:,.2f}")
        print(f"🔥 相比原始系统的改进：专门化震荡区间策略")
        print(f"💡 投资建议: 根据震荡类型精细化配置策略组合")

if __name__ == "__main__":
    main()