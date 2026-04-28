#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 CTA策略系统综合回测 2023-2026
=====================================
针对激进型、保守型、平衡型三个CTA系统进行历史数据回测
时间跨度：2023年1月1日 - 2026年4月14日
"""

import pandas as pd
import numpy as np
import json
import glob
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class CTABacktester:
    def __init__(self):
        self.data_cache = {}
        self.results = {}
        
        # 可用的交易对数据
        self.available_pairs = [
            'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'DOTUSDT',
            'XRPUSDT', 'LINKUSDT', 'SOLUSDT', 'MATICUSDT', 'AVAXUSDT',
            'LTCUSDT', 'BCHUSDT', 'ATOMUSDT', 'DOGEUSDT', 'UNIUSDT'
        ]
        
        print("🚀 CTA策略系统综合回测器初始化完成")
        print(f"📊 可用交易对数量: {len(self.available_pairs)}")
        
    def load_crypto_data(self, symbol):
        """加载加密货币数据"""
        if symbol in self.data_cache:
            return self.data_cache[symbol]
            
        file_path = f"{symbol}_minute_data_2023_2026.csv"
        try:
            df = pd.read_csv(file_path)
            
            # 处理列名，统一为小写
            df.columns = df.columns.str.replace(' ', '_').str.lower()
            
            # 设置时间索引
            if 'open_time' in df.columns:
                df['date'] = pd.to_datetime(df['open_time'])
            elif 'timestamp' in df.columns:
                df['date'] = pd.to_datetime(df['timestamp'])
            else:
                print(f"❌ {symbol} 无法找到时间列")
                return None
            
            # 标准化OHLCV列名
            column_mapping = {
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col not in df.columns:
                    print(f"❌ {symbol} 缺少 {old_col} 列")
                    return None
            
            df = df.set_index('date').sort_index()
            
            # 计算收益率和技术指标
            df['returns'] = df['close'].pct_change()
            df['ma_fast'] = df['close'].rolling(10).mean()
            df['ma_slow'] = df['close'].rolling(30).mean()
            df['rsi'] = self.calculate_rsi(df['close'])
            df['bb_upper'], df['bb_lower'] = self.calculate_bollinger_bands(df['close'])
            
            self.data_cache[symbol] = df
            print(f"✅ {symbol} 数据加载成功: {len(df)} 条记录")
            return df
            
        except FileNotFoundError:
            print(f"❌ {symbol} 数据文件未找到")
            return None
        except Exception as e:
            print(f"❌ {symbol} 数据加载失败: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """计算布林带"""
        ma = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        return upper, lower
    
    def generate_strategy_signals(self, data, strategy_type, params):
        """生成策略信号"""
        signals = pd.Series(0, index=data.index)
        
        try:
            if strategy_type == "Momentum":
                # 动量策略
                fast_period = params.get('fast_period', 10)
                slow_period = params.get('slow_period', 30)
                ma_fast = data['close'].rolling(fast_period).mean()
                ma_slow = data['close'].rolling(slow_period).mean()
                
                signals[ma_fast > ma_slow] = 1
                signals[ma_fast <= ma_slow] = -1
                
            elif strategy_type == "SuperMomentum":
                # 增强动量策略
                fast_period = params.get('fast', 5)
                slow_period = params.get('slow', 20)
                threshold = params.get('threshold', 0.5)
                
                fast_ma = data['close'].rolling(fast_period).mean()
                slow_ma = data['close'].rolling(slow_period).mean()
                momentum = (fast_ma / slow_ma - 1) * 100
                
                signals[momentum > threshold] = 1
                signals[momentum < -threshold] = -1
                
            elif strategy_type == "Breakout":
                # 突破策略
                period = params.get('period', 20)
                multiplier = params.get('multiplier', 1.02)
                
                high_ma = data['high'].rolling(period).max()
                low_ma = data['low'].rolling(period).min()
                
                signals[data['close'] > (high_ma * multiplier)] = 1
                signals[data['close'] < (low_ma / multiplier)] = -1
                
            elif strategy_type == "AdvancedRSI":
                # RSI策略
                rsi_period = params.get('period', 14)
                overbought = params.get('overbought', 70)
                oversold = params.get('oversold', 30)
                
                rsi = self.calculate_rsi(data['close'], rsi_period)
                
                signals[rsi < oversold] = 1
                signals[rsi > overbought] = -1
                
            elif strategy_type == "MeanReversion":
                # 均值回归策略
                period = params.get('period', 20)
                threshold = params.get('threshold', 2.0)
                
                ma = data['close'].rolling(period).mean()
                std = data['close'].rolling(period).std()
                
                z_score = (data['close'] - ma) / std
                signals[z_score < -threshold] = 1
                signals[z_score > threshold] = -1
            
            # 清除NaN值
            signals = signals.fillna(0)
            
        except Exception as e:
            print(f"❌ 信号生成失败 ({strategy_type}): {e}")
            
        return signals
    
    def backtest_strategy(self, symbol, strategy_name, strategy_type, params, weight, start_date, end_date):
        """单个策略回测"""
        try:
            data = self.load_crypto_data(symbol)
            if data is None:
                print(f"❌ {symbol} 数据加载失败")
                return None
            
            # 筛选时间范围
            data_period = data[start_date:end_date].copy()
            if len(data_period) == 0:
                print(f"❌ {symbol} 在指定时间段内无数据")
                return None
            
            # 生成信号
            signals = self.generate_strategy_signals(data_period, strategy_type, params)
            if signals.sum() == 0:
                print(f"⚠️ {symbol} {strategy_name} 未生成有效信号")
                return None
            
            # 计算收益
            data_period['signal'] = signals.shift(1).fillna(0)  # 避免前瞻偏差
            data_period['strategy_returns'] = data_period['signal'] * data_period['returns']
            data_period['cumulative_returns'] = (1 + data_period['strategy_returns']).cumprod()
            
            # 计算绩效指标
            total_return = data_period['cumulative_returns'].iloc[-1] - 1
            
            # 年化收益率 (3年多的数据)
            years = len(data_period) / (365 * 24 * 60)  # 分钟数据转换为年数
            if years > 0:
                annualized_return = (1 + total_return) ** (1 / years) - 1
            else:
                annualized_return = 0
                
            volatility = data_period['strategy_returns'].std() * np.sqrt(365 * 24 * 60)
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            
            # 计算最大回撤
            cummax = data_period['cumulative_returns'].expanding().max()
            drawdown = (data_period['cumulative_returns'] - cummax) / cummax
            max_drawdown = drawdown.min()
            
            # 计算胜率
            winning_trades = (data_period['strategy_returns'] > 0).sum()
            total_trades = (data_period['strategy_returns'] != 0).sum()
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            print(f"✅ {symbol} {strategy_name[:20]}... - 年化收益: {annualized_return:.2%}, 信号数: {(signals != 0).sum()}")
            
            return {
                'symbol': symbol,
                'strategy_name': strategy_name,
                'weight': weight,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'returns_series': data_period['strategy_returns'],
                'cumulative_series': data_period['cumulative_returns']
            }
            
        except Exception as e:
            print(f"❌ {symbol} {strategy_name} 回测失败: {e}")
            return None
    
    def backtest_portfolio(self, portfolio_config, start_date='2023-01-01', end_date='2026-04-14'):
        """组合回测"""
        print(f"\n🔍 开始回测 {portfolio_config['name']} 系统")
        print(f"📅 回测期间: {start_date} - {end_date}")
        print(f"🎯 策略总数: {len(portfolio_config['strategies'])}")
        
        strategy_results = []
        portfolio_returns = None
        
        for i, strategy in enumerate(portfolio_config['strategies'], 1):
            symbol = strategy['symbol']
            strategy_name = strategy['name']
            strategy_type = strategy['type']
            params = strategy['params']
            weight = strategy['weight']
            
            print(f"🔄 [{i}/{len(portfolio_config['strategies'])}] 回测 {symbol} {strategy_type}")
            
            # 单策略回测
            result = self.backtest_strategy(symbol, strategy_name, strategy_type, 
                                          params, weight, start_date, end_date)
            
            if result:
                strategy_results.append(result)
                
                # 加权组合收益
                weighted_returns = result['returns_series'] * weight
                if portfolio_returns is None:
                    portfolio_returns = weighted_returns.copy()
                else:
                    # 简化的索引对齐
                    portfolio_returns = portfolio_returns.add(weighted_returns, fill_value=0)
            else:
                print(f"⚠️ {symbol} {strategy_name} 跳过")
        
        if portfolio_returns is None or len(strategy_results) == 0:
            print(f"❌ {portfolio_config['name']} 回测失败：无有效策略结果")
            return None
        
        print(f"✅ {portfolio_config['name']} 有效策略数量: {len(strategy_results)}")
        
        # 计算组合绩效
        portfolio_cumulative = (1 + portfolio_returns).cumprod()
        total_return = portfolio_cumulative.iloc[-1] - 1
        
        # 年化收益率
        years = len(portfolio_returns) / (365 * 24 * 60)  # 分钟数据
        if years > 0:
            annualized_return = (1 + total_return) ** (1 / years) - 1
        else:
            annualized_return = 0
            
        volatility = portfolio_returns.std() * np.sqrt(365 * 24 * 60)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cummax = portfolio_cumulative.expanding().max()
        drawdown = (portfolio_cumulative - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 胜率
        winning_periods = (portfolio_returns > 0).sum()
        total_periods = len(portfolio_returns)
        win_rate = winning_periods / total_periods
        
        return {
            'portfolio_name': portfolio_config['name'],
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'strategy_count': len(strategy_results),
            'strategy_results': strategy_results,
            'portfolio_returns': portfolio_returns,
            'cumulative_returns': portfolio_cumulative
        }
    
    def create_aggressive_config(self):
        """创建激进型配置"""
        return {
            'name': '激进型CTA策略',
            'target_return': 0.45,
            'risk_level': '高',
            'strategies': [
                {
                    'symbol': 'ADAUSDT',
                    'name': 'Breakout_Fast_Breakout',
                    'type': 'Breakout',
                    'params': {'period': 10, 'multiplier': 1.015},
                    'weight': 0.146
                },
                {
                    'symbol': 'ADAUSDT', 
                    'name': 'Momentum_Medium_Momentum',
                    'type': 'Momentum',
                    'params': {'fast_period': 5, 'slow_period': 15},
                    'weight': 0.138
                },
                {
                    'symbol': 'ETHUSDT',
                    'name': 'Breakout_Fast_Breakout',
                    'type': 'Breakout',
                    'params': {'period': 10, 'multiplier': 1.015},
                    'weight': 0.138
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'Momentum_Slow_Momentum',
                    'type': 'Momentum',
                    'params': {'fast_period': 10, 'slow_period': 30},
                    'weight': 0.124
                },
                {
                    'symbol': 'ETHUSDT',
                    'name': 'Momentum_Medium_Momentum',
                    'type': 'Momentum',
                    'params': {'fast_period': 5, 'slow_period': 15},
                    'weight': 0.110
                },
                {
                    'symbol': 'BTCUSDT',
                    'name': 'Breakout_Fast_Breakout',
                    'type': 'Breakout',
                    'params': {'period': 10, 'multiplier': 1.015},
                    'weight': 0.086
                },
                {
                    'symbol': 'BTCUSDT',
                    'name': 'Momentum_Medium_Momentum',
                    'type': 'Momentum',
                    'params': {'fast_period': 5, 'slow_period': 15},
                    'weight': 0.072
                },
                {
                    'symbol': 'BTCUSDT',
                    'name': 'Momentum_Slow_Momentum',
                    'type': 'Momentum',
                    'params': {'fast_period': 10, 'slow_period': 30},
                    'weight': 0.064
                }
            ]
        }
    
    def create_conservative_config(self):
        """创建保守型配置"""
        return {
            'name': '保守型CTA策略',
            'target_return': 0.25,
            'risk_level': '中等',
            'strategies': [
                {
                    'symbol': 'BTCUSDT',
                    'name': 'SuperMomentum_Fast',
                    'type': 'SuperMomentum',
                    'params': {'fast': 3, 'slow': 12, 'threshold': 0.008},
                    'weight': 0.078
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'AdvancedRSI_7_80_20',
                    'type': 'AdvancedRSI',
                    'params': {'period': 7, 'overbought': 80, 'oversold': 20},
                    'weight': 0.099
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'AdvancedRSI_21_70_30',
                    'type': 'AdvancedRSI',
                    'params': {'period': 21, 'overbought': 70, 'oversold': 30},
                    'weight': 0.080
                },
                {
                    'symbol': 'DOTUSDT',
                    'name': 'MeanReversion_15_1.8',
                    'type': 'MeanReversion',
                    'params': {'period': 15, 'threshold': 1.8},
                    'weight': 0.083
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'AdvancedRSI_14_75_25',
                    'type': 'AdvancedRSI',
                    'params': {'period': 14, 'overbought': 75, 'oversold': 25},
                    'weight': 0.080
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'MeanReversion_35_2.5',
                    'type': 'MeanReversion',
                    'params': {'period': 35, 'threshold': 2.5},
                    'weight': 0.087
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'SuperMomentum_Medium',
                    'type': 'SuperMomentum',
                    'params': {'fast': 3, 'slow': 12, 'threshold': 0.008},
                    'weight': 0.060
                },
                {
                    'symbol': 'BTCUSDT',
                    'name': 'SuperMomentum_Slow',
                    'type': 'SuperMomentum',
                    'params': {'fast': 5, 'slow': 20, 'threshold': 0.005},
                    'weight': 0.060
                },
                {
                    'symbol': 'BTCUSDT',
                    'name': 'SuperMomentum_Ultra',
                    'type': 'SuperMomentum',
                    'params': {'fast': 8, 'slow': 30, 'threshold': 0.003},
                    'weight': 0.056
                },
                {
                    'symbol': 'BNBUSDT',
                    'name': 'Breakout_20_1.02',
                    'type': 'Breakout',
                    'params': {'period': 20, 'multiplier': 1.02},
                    'weight': 0.050
                },
                {
                    'symbol': 'DOTUSDT',
                    'name': 'SuperMomentum_Fast',
                    'type': 'SuperMomentum',
                    'params': {'fast': 3, 'slow': 12, 'threshold': 0.008},
                    'weight': 0.045
                },
                {
                    'symbol': 'BNBUSDT',
                    'name': 'MeanReversion_25_2.0',
                    'type': 'MeanReversion',
                    'params': {'period': 25, 'threshold': 2.0},
                    'weight': 0.048
                },
                {
                    'symbol': 'BNBUSDT',
                    'name': 'SuperMomentum_Medium',
                    'type': 'SuperMomentum',
                    'params': {'fast': 5, 'slow': 20, 'threshold': 0.005},
                    'weight': 0.048
                },
                {
                    'symbol': 'ETHUSDT',
                    'name': 'AdvancedRSI_14_70_30',
                    'type': 'AdvancedRSI',
                    'params': {'period': 14, 'overbought': 70, 'oversold': 30},
                    'weight': 0.053
                },
                {
                    'symbol': 'BTCUSDT',
                    'name': 'MeanReversion_30_2.2',
                    'type': 'MeanReversion',
                    'params': {'period': 30, 'threshold': 2.2},
                    'weight': 0.040
                }
            ]
        }
    
    def create_balanced_config(self):
        """创建平衡型配置"""
        return {
            'name': '平衡型CTA策略',
            'target_return': 0.35,
            'risk_level': '中高',
            'strategies': [
                # 成长导向组件
                {
                    'symbol': 'ADAUSDT',
                    'name': 'Breakout_Fast_Breakout',
                    'type': 'Breakout',
                    'params': {'period': 10, 'multiplier': 1.015},
                    'weight': 0.135
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'Momentum_Medium_Momentum',
                    'type': 'Momentum',
                    'params': {'fast_period': 5, 'slow_period': 15},
                    'weight': 0.128
                },
                {
                    'symbol': 'ETHUSDT',
                    'name': 'Breakout_Fast_Breakout',
                    'type': 'Breakout',
                    'params': {'period': 10, 'multiplier': 1.015},
                    'weight': 0.127
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'Momentum_Slow_Momentum',
                    'type': 'Momentum',
                    'params': {'fast_period': 10, 'slow_period': 30},
                    'weight': 0.115
                },
                {
                    'symbol': 'ETHUSDT',
                    'name': 'Momentum_Medium_Momentum',
                    'type': 'Momentum',
                    'params': {'fast_period': 5, 'slow_period': 15},
                    'weight': 0.102
                },
                # 稳健导向组件
                {
                    'symbol': 'BTCUSDT',
                    'name': 'SuperMomentum_Conservative',
                    'type': 'SuperMomentum',
                    'params': {'fast': 3, 'slow': 12, 'threshold': 0.008},
                    'weight': 0.048
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'AdvancedRSI_Balanced',
                    'type': 'AdvancedRSI',
                    'params': {'period': 7, 'overbought': 80, 'oversold': 20},
                    'weight': 0.061
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'AdvancedRSI_Conservative',
                    'type': 'AdvancedRSI',
                    'params': {'period': 21, 'overbought': 70, 'oversold': 30},
                    'weight': 0.050
                },
                {
                    'symbol': 'DOTUSDT',
                    'name': 'MeanReversion_Stable',
                    'type': 'MeanReversion',
                    'params': {'period': 15, 'threshold': 1.8},
                    'weight': 0.051
                },
                {
                    'symbol': 'ADAUSDT',
                    'name': 'AdvancedRSI_Moderate',
                    'type': 'AdvancedRSI',
                    'params': {'period': 14, 'overbought': 75, 'oversold': 25},
                    'weight': 0.049
                }
            ]
        }
    
    def print_backtest_results(self, result):
        """打印回测结果"""
        if not result:
            print("❌ 回测结果为空")
            return
        
        print(f"\n📊 {result['portfolio_name']} 回测报告")
        print("=" * 50)
        
        print(f"💰 总收益率: {result['total_return']:.2%}")
        print(f"📈 年化收益率: {result['annualized_return']:.2%}")
        print(f"📊 年化波动率: {result['volatility']:.2%}")
        print(f"⚡ 夏普比率: {result['sharpe_ratio']:.3f}")
        print(f"📉 最大回撤: {result['max_drawdown']:.2%}")
        print(f"🎯 胜率: {result['win_rate']:.2%}")
        print(f"🔢 策略数量: {result['strategy_count']}")
        
        print(f"\n🔝 表现最佳策略 (前5名):")
        print("-" * 40)
        strategy_performance = [(s['strategy_name'], s['annualized_return']) 
                              for s in result['strategy_results']]
        strategy_performance.sort(key=lambda x: x[1], reverse=True)
        
        for i, (name, ret) in enumerate(strategy_performance[:5], 1):
            print(f"{i}. {name}: {ret:.2%}")
    
    def run_comprehensive_backtest(self):
        """运行综合回测"""
        print("🚀 开始CTA策略系统综合回测 (2023-2026)")
        print("=" * 60)
        
        # 创建三个系统配置
        configs = [
            self.create_aggressive_config(),
            self.create_conservative_config(),
            self.create_balanced_config()
        ]
        
        # 回测每个系统
        all_results = []
        for config in configs:
            result = self.backtest_portfolio(config)
            if result:
                all_results.append(result)
                self.print_backtest_results(result)
                
        # 生成对比报告
        if len(all_results) > 1:
            self.print_comparison_report(all_results)
            
        # 保存结果
        self.save_results(all_results)
        
        return all_results
    
    def print_comparison_report(self, results):
        """打印对比报告"""
        print("\n🏆 三系统对比分析")
        print("=" * 60)
        
        print(f"{'策略系统':<15} {'年化收益':<10} {'最大回撤':<10} {'夏普比率':<10} {'胜率':<8}")
        print("-" * 60)
        
        for result in results:
            name = result['portfolio_name'].replace('CTA策略', '')
            annual_ret = f"{result['annualized_return']:.1%}"
            max_dd = f"{result['max_drawdown']:.1%}"
            sharpe = f"{result['sharpe_ratio']:.2f}"
            win_rate = f"{result['win_rate']:.1%}"
            
            print(f"{name:<15} {annual_ret:<10} {max_dd:<10} {sharpe:<10} {win_rate:<8}")
        
        # 找出最佳系统
        best_return = max(results, key=lambda x: x['annualized_return'])
        best_sharpe = max(results, key=lambda x: x['sharpe_ratio'])
        best_drawdown = min(results, key=lambda x: abs(x['max_drawdown']))
        
        print("\n🎖️ 各项最佳表现:")
        print(f"📈 最高收益: {best_return['portfolio_name']} ({best_return['annualized_return']:.2%})")
        print(f"⚡ 最佳风险收益比: {best_sharpe['portfolio_name']} (夏普比率 {best_sharpe['sharpe_ratio']:.3f})")
        print(f"🛡️ 最小回撤: {best_drawdown['portfolio_name']} ({best_drawdown['max_drawdown']:.2%})")
    
    def save_results(self, results):
        """保存回测结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cta_backtest_results_{timestamp}.json"
        
        # 准备保存的数据（移除无法序列化的pandas对象）
        save_data = []
        for result in results:
            clean_result = {
                'portfolio_name': result['portfolio_name'],
                'total_return': result['total_return'],
                'annualized_return': result['annualized_return'],
                'volatility': result['volatility'],
                'sharpe_ratio': result['sharpe_ratio'],
                'max_drawdown': result['max_drawdown'],
                'win_rate': result['win_rate'],
                'strategy_count': result['strategy_count']
            }
            save_data.append(clean_result)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 回测结果已保存: {filename}")

def main():
    """主函数"""
    print("🎯 CTA策略系统综合回测启动")
    print("📅 回测时间跨度: 2023-2026")
    
    backtester = CTABacktester()
    results = backtester.run_comprehensive_backtest()
    
    print("\n✅ 综合回测完成!")
    print("🎉 三个CTA系统历史回测结果已生成")

if __name__ == "__main__":
    main()