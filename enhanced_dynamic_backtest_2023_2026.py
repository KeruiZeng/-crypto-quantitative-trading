#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 增强版动态CTA投资组合管理系统 2023-2026
==========================================
Version 2.0 - 集成多策略扩展 + 智能风险管理
新增功能：8种策略 + 7维风险监控 + 自适应权重优化
目标：收益提升30%，风险降低35%
"""

import pandas as pd 
import numpy as np
import json
from datetime import datetime, timedelta
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# 导入优化模块
try:
    from advanced_strategy_engine import AdvancedStrategyEngine
    from intelligent_risk_manager import IntelligentRiskManager
    OPTIMIZATION_MODULES_AVAILABLE = True
    print("✅ 优化模块加载成功")
except ImportError as e:
    print(f"⚠️ 优化模块加载失败: {e}")
    print("📝 将使用基础版本运行")
    OPTIMIZATION_MODULES_AVAILABLE = False

class EnhancedDynamicBacktest:
    """增强版动态CTA回测系统"""
    
    def __init__(self):
        print("🚀 增强版动态CTA投资组合管理系统 2023-2026")
        print("="*70)
        print("v2.0: 多策略 + 智能风险管理")
        
        # 扩展策略配置 (8种策略)
        if OPTIMIZATION_MODULES_AVAILABLE:
            self.strategies_config = {
                # 原有策略
                'BTCUSDT_FixedBreakout': {'symbol': 'BTCUSDT', 'weight': 0.20, 'type': 'breakout'},
                'ETHUSDT_FixedBreakout': {'symbol': 'ETHUSDT', 'weight': 0.20, 'type': 'breakout'},
                # 新增策略 
                'BTCUSDT_MeanReversion': {'symbol': 'BTCUSDT', 'weight': 0.15, 'type': 'mean_reversion'},
                'ETHUSDT_MeanReversion': {'symbol': 'ETHUSDT', 'weight': 0.15, 'type': 'mean_reversion'},
                'BTCUSDT_Momentum': {'symbol': 'BTCUSDT', 'weight': 0.10, 'type': 'momentum'},
                'ETHUSDT_Momentum': {'symbol': 'ETHUSDT', 'weight': 0.10, 'type': 'momentum'},
                'BTCUSDT_GridTrading': {'symbol': 'BTCUSDT', 'weight': 0.05, 'type': 'grid'},
                'ETHUSDT_GridTrading': {'symbol': 'ETHUSDT', 'weight': 0.05, 'type': 'grid'}
            }
            print("📊 已配置8种多样化策略")
        else:
            # 降级到基础配置
            self.strategies_config = {
                'BTCUSDT_FixedBreakout': {'symbol': 'BTCUSDT', 'weight': 0.4, 'type': 'breakout'},
                'ETHUSDT_FixedBreakout': {'symbol': 'ETHUSDT', 'weight': 0.6, 'type': 'breakout'}
            }
            print("📊 使用基础2策略配置")
        
        # 增强管理参数
        self.rebalance_threshold = 0.05  # 5%
        self.optimization_frequency = 7   # 7天（每周）
        self.stress_test_frequency = 30   # 30天
        self.transaction_cost = 0.0005    # 0.05%
        self.min_data_days = 5           # 每周优化最小数据要求
        
        # 风险管理参数 (增强)
        self.risk_thresholds = {
            'var_95': -0.03,          # VaR阈值从-5%调至-3%
            'drawdown': -0.025,       # 回撤预警-2.5%
            'correlation': 0.6,       # 相关性预警60%
            'concentration': 0.3,     # 集中度预警30%
            'volatility': 1.8         # 波动率预警倍数
        }
        
        # 回测参数
        self.start_date = '2023-01-01'
        self.end_date = '2026-04-14'
        self.initial_capital = 100000
        
        # 初始化增强模块
        if OPTIMIZATION_MODULES_AVAILABLE:
            self.advanced_engine = AdvancedStrategyEngine()
            self.risk_manager = IntelligentRiskManager()
            print("🛡️ 智能风险管理器已激活")
        
        # 预加载所有数据
        self.preload_all_data()
        
        # 记录历史 (增强)
        self.portfolio_history = []
        self.rebalance_history = []
        self.optimization_history = []
        self.stress_test_history = []
        self.risk_analysis_history = []  # 新增
        self.strategy_performance_history = []  # 新增
        
        print(f"📊 回测期间: {self.start_date} - {self.end_date}")
        print(f"💰 初始资金: ${self.initial_capital:,}")
        print(f"⚖️ 再平衡阈值: ±{self.rebalance_threshold:.0%}")
        print(f"🎯 风险管理等级: {'高级' if OPTIMIZATION_MODULES_AVAILABLE else '标准'}")
    
    def preload_all_data(self):
        """增强版数据预加载"""
        print(f"\n📂 预加载策略数据...")
        
        self.strategy_data = {}
        self.raw_symbol_data = {}  # 保存原始数据
        
        # 获取唯一符号列表
        symbols = list(set([config['symbol'] for config in self.strategies_config.values()]))
        
        for symbol in symbols:
            try:
                datafile = f"{symbol}_minute_data_2023_2026.csv"
                print(f"   📈 加载 {datafile}")
                
                df = pd.read_csv(datafile)
                
                # 标准化处理
                df.columns = df.columns.str.replace(' ', '_').str.lower()
                df['datetime'] = pd.to_datetime(df['open_time'])
                df = df.set_index('datetime').sort_index()
                
                # 计算收益率
                df['returns'] = df['close'].pct_change().fillna(0)
                
                # 技术指标
                df['sma_21'] = df['close'].rolling(21).mean()
                df['bb_std'] = df['close'].rolling(21).std()
                df['bb_upper'] = df['sma_21'] + 2 * df['bb_std']
                df['bb_lower'] = df['sma_21'] - 2 * df['bb_std']
                df['volume_sma'] = df['volume'].rolling(21).mean()
                df['volume_ratio'] = df['volume'] / df['volume_sma']
                
                # 前向填充
                df = df.fillna(method='bfill').fillna(0)
                
                # 保存原始数据
                self.raw_symbol_data[symbol] = df[self.start_date:self.end_date].copy()
                
                print(f"      ✅ {symbol}: {len(df):,} 条记录")
                
            except Exception as e:
                print(f"      ❌ {symbol} 加载失败: {e}")
        
        # 为每个策略生成数据
        self.generate_all_strategies()
        
        print(f"✅ 数据预加载完成，共 {len(self.strategy_data)} 个策略")
    
    def generate_all_strategies(self):
        """生成所有策略数据"""
        
        for strategy_name, config in self.strategies_config.items():
            symbol = config['symbol']
            strategy_type = config.get('type', 'breakout')
            
            if symbol not in self.raw_symbol_data:
                continue
            
            df = self.raw_symbol_data[symbol].copy()
            
            try:
                if strategy_type == 'breakout':
                    # 原有突破策略
                    df = self.generate_breakout_strategy(df)
                elif OPTIMIZATION_MODULES_AVAILABLE:
                    # 新增策略（如果模块可用）
                    if strategy_type == 'mean_reversion':
                        df = self.advanced_engine.mean_reversion_strategy(df)
                    elif strategy_type == 'momentum':
                        df = self.advanced_engine.momentum_strategy(df)
                    elif strategy_type == 'grid':
                        df = self.advanced_engine.grid_trading_strategy(df)
                    elif strategy_type == 'volatility':
                        df = self.advanced_engine.volatility_strategy(df)
                    else:
                        # 默认为突破策略
                        df = self.generate_breakout_strategy(df)
                else:
                    # 如果优化模块不可用，都使用突破策略
                    df = self.generate_breakout_strategy(df)
                
                self.strategy_data[strategy_name] = df
                print(f"      🎯 {strategy_name}: {strategy_type} 策略已生成")
                
            except Exception as e:
                print(f"      ⚠️ {strategy_name} 生成失败: {e}")
                # 使用基础突破策略作为后备
                df = self.generate_breakout_strategy(df)
                self.strategy_data[strategy_name] = df
    
    def generate_breakout_strategy(self, df):
        """生成突破策略 (原有逻辑)"""
        df = df.copy()
        
        try:
            # 布林带突破信号
            bb_breakout_up = (df['close'] > df['bb_upper']) & (df['volume_ratio'] > 1.5)
            bb_breakout_down = (df['close'] < df['bb_lower']) & (df['volume_ratio'] > 1.5)
            
            # 生成信号
            signals = pd.Series(0, index=df.index)
            signals[bb_breakout_up] = 1
            signals[bb_breakout_down] = -1
            
            # 强制持仓4小时
            signals = self.enforce_holding_period(signals, 240)
        
        except Exception as e:
            print(f"         ⚠️ 策略生成失败: {e}")
            signals = pd.Series(0, index=df.index)
        
        # 计算策略收益
        df['position'] = signals
        df['strategy_returns'] = signals.shift(1) * df['returns'] - signals.diff().abs() * self.transaction_cost
        
        return df
    
    def enforce_holding_period(self, signals, min_periods):
        """强制持仓期"""
        fixed_signals = signals.copy()
        position = 0
        hold_count = 0
        
        for i in range(len(signals)):
            current_signal = signals.iloc[i]
            if current_signal != 0 and hold_count == 0:
                position = current_signal
                hold_count = min_periods
            elif hold_count > 0:
                hold_count -= 1
                if hold_count == 0:
                    position = 0
            fixed_signals.iloc[i] = position
        
        return fixed_signals
    
    def enhanced_portfolio_optimization(self, current_date):
        """增强版投资组合优化"""
        print(f"   🚀 执行增强权重优化 ({current_date.strftime('%Y-%m-%d')})")
        
        strategy_names = list(self.strategies_config.keys())
        expected_returns = []
        volatilities = []
        valid_strategies = []
        
        # 计算各策略指标
        for strategy_name in strategy_names:
            metrics = self.calculate_strategy_metrics(strategy_name, current_date, 7)
            if metrics:
                expected_returns.append(metrics['annualized_return'])
                volatilities.append(metrics['volatility'])
                valid_strategies.append(strategy_name)
                
                print(f"      📊 {strategy_name[-15:]}: 收益{metrics['annualized_return']:.1%}, 波动{metrics['volatility']:.1%}")
        
        if len(valid_strategies) < 2:
            print(f"      ⚠️ 有效策略不足 ({len(valid_strategies)}个)，保持现有权重")
            return None
        
        # 增强优化算法
        if OPTIMIZATION_MODULES_AVAILABLE and len(valid_strategies) >= 3:
            # 使用风险平价模型
            weights = self.risk_parity_optimization(expected_returns, volatilities, valid_strategies)
        else:
            # 基于夏普比率的简化优化
            weights = self.sharpe_based_optimization(expected_returns, volatilities, valid_strategies)
        
        # 构建权重字典
        weight_dict = {}
        for i, strategy_name in enumerate(valid_strategies):
            weight_dict[strategy_name] = weights[i]
        
        # 补充缺失策略权重为0
        for strategy_name in strategy_names:
            if strategy_name not in weight_dict:
                weight_dict[strategy_name] = 0.0
        
        # 计算组合指标
        weights_array = np.array(weights)
        expected_returns_array = np.array(expected_returns)
        volatilities_array = np.array(volatilities)
        
        portfolio_return = np.sum(weights_array * expected_returns_array)
        portfolio_vol = np.sqrt(np.sum((weights_array * volatilities_array) ** 2))
        sharpe = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
        
        print(f"      ✅ 优化完成: 预期收益{portfolio_return:.1%}, 夏普{sharpe:.2f}")
        
        return weight_dict
    
    def risk_parity_optimization(self, expected_returns, volatilities, valid_strategies):
        """风险平价优化算法"""
        
        n = len(expected_returns)
        
        # 构建简化的协方差矩阵
        vol_array = np.array(volatilities)
        
        # 假设相关性矩阵 (可以基于历史数据计算)
        correlation_matrix = np.eye(n)
        for i in range(n):
            for j in range(i+1, n):
                # 基于策略类型设置相关性
                strategy1 = valid_strategies[i]
                strategy2 = valid_strategies[j]
                
                # 同币种不同策略相关性较高
                if strategy1.split('_')[0] == strategy2.split('_')[0]:
                    correlation_matrix[i, j] = correlation_matrix[j, i] = 0.6
                else:
                    correlation_matrix[i, j] = correlation_matrix[j, i] = 0.3
        
        # 协方差矩阵
        cov_matrix = np.outer(vol_array, vol_array) * correlation_matrix
        
        # 风险平价权重
        def risk_parity_objective(w):
            portfolio_vol = np.sqrt(np.dot(w, np.dot(cov_matrix, w)))
            marginal_contrib = np.dot(cov_matrix, w) / portfolio_vol
            contrib = w * marginal_contrib
            return np.sum((contrib - contrib.mean()) ** 2)
        
        # 约束条件
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = tuple((0, 0.4) for _ in range(n))  # 单策略最大40%
        
        # 初始权重
        w0 = np.ones(n) / n
        
        try:
            result = minimize(risk_parity_objective, w0, method='SLSQP', 
                            bounds=bounds, constraints=constraints)
            
            if result.success:
                return result.x
            else:
                print(f"      ⚠️ 风险平价优化失败，使用等权重")
                return np.ones(n) / n
        except:
            print(f"      ⚠️ 优化异常，使用等权重")
            return np.ones(n) / n
    
    def sharpe_based_optimization(self, expected_returns, volatilities, valid_strategies):
        """夏普比率优化 (原逻辑的增强版)"""
        
        expected_returns = np.array(expected_returns)
        volatilities = np.array(volatilities)
        
        # 计算夏普比率
        sharpe_ratios = expected_returns / volatilities
        sharpe_ratios[sharpe_ratios < 0] = 0  # 负夏普设为0
        
        if np.sum(sharpe_ratios) == 0:
            # 等权重分配
            weights = np.ones(len(valid_strategies)) / len(valid_strategies)
        else:
            # 基于夏普比率但增加多样性约束
            weights = sharpe_ratios / np.sum(sharpe_ratios)
            
            # 多样性调整：限制单策略最大权重
            max_weight = 0.5 if len(valid_strategies) <= 3 else 0.4
            
            while np.max(weights) > max_weight:
                # 找到超重的策略
                over_weight_idx = np.argmax(weights)
                excess = weights[over_weight_idx] - max_weight
                
                # 将超重部分分配给其他策略
                weights[over_weight_idx] = max_weight
                other_indices = np.arange(len(weights)) != over_weight_idx
                
                if np.sum(other_indices) > 0:
                    weights[other_indices] += excess / np.sum(other_indices)
        
        return weights
    
    def calculate_strategy_metrics(self, strategy_name, end_date, lookback_days=7):
        """计算策略指标 (与原版一致)"""
        if strategy_name not in self.strategy_data:
            return None
            
        df = self.strategy_data[strategy_name]
        start_date = end_date - timedelta(days=lookback_days)
        
        # 筛选时间段
        recent_data = df[(df.index >= start_date) & (df.index <= end_date)]
        
        if len(recent_data) < 1000:  # 至少1000个数据点
            return None
            
        strategy_returns = recent_data['strategy_returns']
        
        # 计算指标
        total_return = (1 + strategy_returns).prod() - 1
        days = len(recent_data) / (24 * 60)
        
        if days < self.min_data_days:  # 至少5天数据
            return None
            
        annualized_return = (1 + total_return) ** (365 / days) - 1
        volatility = strategy_returns.std() * np.sqrt(365 * 24 * 60)
        
        return {
            'annualized_return': annualized_return,
            'volatility': max(volatility, 0.001),  # 避免零波动
            'total_return': total_return
        }
    
    def enhanced_risk_analysis(self, current_date, portfolio_data, current_weights):
        """增强风险分析"""
        
        if not OPTIMIZATION_MODULES_AVAILABLE:
            return {'risk_level': 'UNKNOWN', 'alerts': [], 'recommendations': []}
        
        # 构建策略收益数据
        strategy_returns = {}
        end_date = current_date
        start_date = end_date - timedelta(days=30)  # 用30天数据分析
        
        for strategy_name in self.strategy_data:
            if strategy_name in current_weights and current_weights[strategy_name] > 0:
                df = self.strategy_data[strategy_name]
                period_data = df[(df.index >= start_date) & (df.index <= end_date)]
                
                if len(period_data) > 100:  # 至少100个数据点
                    strategy_returns[strategy_name] = period_data['strategy_returns']
        
        if len(strategy_returns) < 2:
            return {'risk_level': 'LOW', 'alerts': [], 'recommendations': []}
        
        # 执行风险分析
        try:
            risk_report = self.risk_manager.comprehensive_risk_analysis(
                portfolio_data, current_weights, strategy_returns
            )
            
            # 生成预警和建议
            risk_report['alerts'] = self.risk_manager.generate_risk_alerts(risk_report)
            risk_report['recommendations'] = self.risk_manager.generate_risk_recommendations(risk_report)
            
            return risk_report
            
        except Exception as e:
            print(f"      ⚠️ 风险分析失败: {e}")
            return {'risk_level': 'UNKNOWN', 'alerts': [], 'recommendations': []}
    
    def run_enhanced_backtest(self):
        """运行增强版回测"""
        
        print(f"\n🚀 开始增强版回测...")
        print("="*50)
        
        # 初始化
        current_weights = {name: config['weight'] for name, config in self.strategies_config.items()}
        portfolio_value = self.initial_capital
        last_optimization_date = None
        last_stress_test_date = None
        
        # 生成交易日期
        all_dates = sorted(set().union(*[df.index.date for df in self.strategy_data.values()]))
        trading_dates = [d for d in all_dates if pd.Timestamp(d) >= pd.Timestamp(self.start_date)]
        
        total_days = len(trading_dates)
        print(f"📅 交易天数: {total_days} 天")
        
        # 初始化性能跟踪
        optimization_count = 0
        rebalance_count = 0
        risk_alerts_count = 0
        
        for i, current_date in enumerate(trading_dates):
            current_datetime = pd.Timestamp(current_date)
            
            # 进度显示
            if i % 30 == 0 or i == len(trading_dates) - 1:
                progress = (i + 1) / total_days * 100
                print(f"📊 回测进度: {progress:.1f}% ({current_date})")
            
            # 1. 定期优化 
            if (last_optimization_date is None or 
                (current_datetime - last_optimization_date).days >= self.optimization_frequency):
                
                optimized_weights = self.enhanced_portfolio_optimization(current_datetime)
                if optimized_weights:
                    
                    # 检查再平衡需求
                    need_rebalance, max_deviation = self.check_rebalance_needed(current_weights, optimized_weights)
                    
                    if need_rebalance:
                        # 执行再平衡
                        trades, cost = self.execute_rebalance(current_weights, optimized_weights, portfolio_value)
                        
                        current_weights = optimized_weights.copy()
                        portfolio_value -= cost
                        rebalance_count += 1
                        
                        # 记录再平衡
                        self.rebalance_history.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'trades': trades,
                            'cost': cost,
                            'max_deviation': max_deviation
                        })
                        
                        print(f"   🔄 再平衡: 最大偏差{max_deviation:.1%}, 成本${cost:.2f}")
                    
                    # 记录优化
                    self.optimization_history.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'old_weights': {k: v for k, v in current_weights.items()},
                        'new_weights': optimized_weights
                    })
                    
                    last_optimization_date = current_datetime
                    optimization_count += 1
            
            # 2. 计算当日收益
            daily_return = self.calculate_daily_portfolio_return(current_datetime, current_weights)
            portfolio_value *= (1 + daily_return)
            
            # 3. 增强风险监控 (每周)
            if OPTIMIZATION_MODULES_AVAILABLE and i % 7 == 0:  # 每周风险检查
                
                # 构建投资组合数据
                portfolio_df = pd.DataFrame({
                    'portfolio_value': [portfolio_value] * 10  # 简化数据
                })
                
                risk_report = self.enhanced_risk_analysis(current_datetime, portfolio_df, current_weights)
                
                # 处理风险预警
                if risk_report.get('alerts'):
                    risk_alerts_count += len(risk_report['alerts'])
                    print(f"   ⚠️ 风险预警 ({len(risk_report['alerts'])}项): {risk_report['risk_level']}")
                    
                    # 应急风险控制
                    if risk_report['risk_level'] == 'HIGH':
                        self.apply_emergency_risk_control(current_weights, portfolio_value)
                        print(f"   🚨 应急风险控制已激活")
                
                # 记录风险分析
                self.risk_analysis_history.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'risk_score': risk_report.get('overall_risk_score', 0),
                    'risk_level': risk_report.get('risk_level', 'UNKNOWN'),
                    'alerts_count': len(risk_report.get('alerts', []))
                })
            
            # 4. 压力测试 (每月)
            if (last_stress_test_date is None or 
                (current_datetime - last_stress_test_date).days >= self.stress_test_frequency):
                
                stress_result = self.monte_carlo_stress_test(current_datetime, current_weights)
                self.stress_test_history.append(stress_result)
                last_stress_test_date = current_datetime
            
            # 5. 记录每周组合状态
            if i % 7 == 0:  # 每周记录
                week_return = daily_return * 7  # 简化计算
                
                self.portfolio_history.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'portfolio_value': portfolio_value,
                    'week_return': week_return,
                    'weights': current_weights.copy()
                })
        
        # 计算最终结果
        final_results = self.calculate_enhanced_results(portfolio_value, optimization_count, rebalance_count, risk_alerts_count)
        
        return final_results
    
    def apply_emergency_risk_control(self, current_weights, portfolio_value):
        """应急风险控制"""
        # 降低仓位至70%
        for strategy in current_weights:
            current_weights[strategy] *= 0.7
    
    def calculate_daily_portfolio_return(self, date, weights):
        """计算日投资组合收益 (与原版一致)"""
        portfolio_return = 0
        
        for strategy_name, weight in weights.items():
            if weight > 0 and strategy_name in self.strategy_data:
                df = self.strategy_data[strategy_name]
                
                # 获取当日数据
                daily_data = df[df.index.date == date.date()]
                
                if not daily_data.empty:
                    daily_strategy_return = daily_data['strategy_returns'].sum()
                    portfolio_return += weight * daily_strategy_return
        
        return portfolio_return
    
    def check_rebalance_needed(self, current_weights, target_weights):
        """检查再平衡需求 (与原版一致)"""
        max_deviation = 0
        
        for strategy in target_weights:
            current = current_weights.get(strategy, 0)
            target = target_weights[strategy]
            
            if target > 0:
                deviation_pct = abs(current - target) / target
                max_deviation = max(max_deviation, deviation_pct)
            elif current > 0.01:
                max_deviation = max(max_deviation, current)
        
        return max_deviation > self.rebalance_threshold, max_deviation
    
    def execute_rebalance(self, current_weights, target_weights, portfolio_value):
        """执行再平衡 (与原版一致)"""
        trades = []
        total_cost = 0
        
        for strategy, target_weight in target_weights.items():
            current_weight = current_weights.get(strategy, 0)
            
            if abs(target_weight - current_weight) > 0.001:
                weight_change = target_weight - current_weight
                trade_amount = weight_change * portfolio_value
                cost = abs(trade_amount) * self.transaction_cost
                
                trades.append({
                    'strategy': strategy,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'trade_amount': trade_amount,
                    'cost': cost
                })
                
                total_cost += cost
        
        return trades, total_cost
    
    def monte_carlo_stress_test(self, current_date, current_weights):
        """蒙特卡罗压力测试 (简化版)"""
        
        # 获取最近30天的投资组合收益
        portfolio_returns = []
        start_date = current_date - timedelta(days=30)
        
        for date in pd.date_range(start_date, current_date, freq='D'):
            daily_return = self.calculate_daily_portfolio_return(date, current_weights)
            portfolio_returns.append(daily_return)
        
        portfolio_returns = np.array(portfolio_returns)
        
        if len(portfolio_returns) < 10:
            return {
                'date': current_date.strftime('%Y-%m-%d'),
                'var_95': 0,
                'prob_loss': 0,
                'risk_level': '🟢 低风险'
            }
        
        # 计算VaR
        var_95 = np.percentile(portfolio_returns, 5)
        prob_loss = (portfolio_returns < 0).mean()
        
        # 风险等级
        if var_95 < -0.03 or prob_loss > 0.6:
            risk_level = '🔴 高风险'
        elif var_95 < -0.015 or prob_loss > 0.4:
            risk_level = '🟡 中等风险'
        else:
            risk_level = '🟢 低风险'
        
        return {
            'date': current_date.strftime('%Y-%m-%d'),
            'var_95': var_95,
            'prob_loss': prob_loss,
            'risk_level': risk_level
        }
    
    def calculate_enhanced_results(self, final_value, optimization_count, rebalance_count, risk_alerts_count):
        """计算增强版回测结果"""
        
        # 基础指标
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 计算收益序列
        portfolio_values = [record['portfolio_value'] for record in self.portfolio_history]
        returns_series = pd.Series(portfolio_values).pct_change().dropna()
        
        # 性能指标
        annualized_return = (final_value / self.initial_capital) ** (365 / len(self.portfolio_history) * 7) - 1
        volatility = returns_series.std() * np.sqrt(52)  # 周收益标准差年化
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = pd.Series(portfolio_values)
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # 胜率
        positive_returns = returns_series[returns_series > 0]
        win_rate = len(positive_returns) / len(returns_series) if len(returns_series) > 0 else 0
        
        # 增强指标
        strategy_count = len([w for w in self.portfolio_history[-1]['weights'].values() if w > 0.01]) if self.portfolio_history else 0
        avg_correlation = self.calculate_average_correlation()
        
        results = {
            'backtest_info': {
                'system': f'增强版动态CTA投资组合管理系统 v2.0',
                'period': f'{self.start_date} - {self.end_date}',
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'optimization_enabled': OPTIMIZATION_MODULES_AVAILABLE
            },
            'parameters': {
                'initial_capital': self.initial_capital,
                'rebalance_threshold': self.rebalance_threshold,
                'optimization_frequency': self.optimization_frequency,
                'stress_test_frequency': self.stress_test_frequency,
                'strategy_count': len(self.strategies_config),
                'active_strategy_count': strategy_count
            },
            'performance': {
                'final_value': final_value,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate
            },
            'activities': {
                'optimizations': optimization_count,
                'rebalances': rebalance_count,
                'stress_tests': len(self.stress_test_history),
                'risk_alerts': risk_alerts_count
            },
            'risk_metrics': {
                'average_correlation': avg_correlation,
                'max_single_weight': max([max(record['weights'].values()) for record in self.portfolio_history]) if self.portfolio_history else 0,
                'risk_analysis_count': len(self.risk_analysis_history)
            },
            'history': {
                'portfolio': self.portfolio_history[-50:],  # 最近50个记录
                'optimizations': self.optimization_history,
                'rebalances': self.rebalance_history[-20:],  # 最近20次再平衡
                'stress_tests': self.stress_test_history
            }
        }
        
        return results
    
    def calculate_average_correlation(self):
        """计算平均相关性"""
        if len(self.strategy_data) < 2:
            return 0
        
        # 获取最近30天的策略收益
        strategy_returns = {}
        
        for name, df in self.strategy_data.items():
            recent_returns = df['strategy_returns'].tail(30*24*60//15)  # 最近30天（假设15分钟数据）
            if len(recent_returns) > 100:
                strategy_returns[name] = recent_returns
        
        if len(strategy_returns) < 2:
            return 0
        
        # 计算相关性矩阵
        df_returns = pd.DataFrame(strategy_returns).dropna()
        if len(df_returns) < 10:
            return 0
        
        corr_matrix = df_returns.corr()
        
        # 计算平均相关性 (排除对角线)
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if not pd.isna(corr_val):
                    correlations.append(abs(corr_val))
        
        return np.mean(correlations) if correlations else 0

def main():
    """运行增强版回测"""
    
    print("🚀 增强版CTA策略系统启动")
    print("=" * 60)
    
    # 创建增强版回测实例
    backtest = EnhancedDynamicBacktest()
    
    try:
        # 运行回测
        results = backtest.run_enhanced_backtest()
        
        # 显示结果摘要
        print(f"\n📊 增强版回测完成!")
        print("=" * 50)
        print(f"💰 最终价值: ${results['performance']['final_value']:,.2f}")
        print(f"📈 总收益率: {results['performance']['total_return']:.2%}")
        print(f"📊 年化收益: {results['performance']['annualized_return']:.2%}")
        print(f"⚡ 夏普比率: {results['performance']['sharpe_ratio']:.3f}")
        print(f"📉 最大回撤: {results['performance']['max_drawdown']:.2%}")
        print(f"🎯 胜率: {results['performance']['win_rate']:.1%}")
        print(f"🔄 优化次数: {results['activities']['optimizations']}")
        print(f"⚖️ 再平衡次数: {results['activities']['rebalances']}")
        print(f"🛡️ 风险预警: {results['activities']['risk_alerts']}次")
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f"enhanced_dynamic_backtest_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 详细结果已保存至: {result_file}")
        
        # 性能对比
        if OPTIMIZATION_MODULES_AVAILABLE:
            improvement_msg = "✅ 多策略 + 智能风险管理已激活"
        else:
            improvement_msg = "⚠️ 基础模式运行（优化模块未加载）"
        
        print(f"🎯 系统状态: {improvement_msg}")
        
        return results
        
    except Exception as e:
        print(f"❌ 回测执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()