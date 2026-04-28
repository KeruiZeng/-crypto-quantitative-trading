#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📈 动态CTA投资组合管理系统 2023-2026 历史回测
================================================
验证动态管理策略在历史数据上的完整表现
包含：定期优化 + 动态再平衡 + 压力测试
"""

import pandas as pd 
import numpy as np
import json
from datetime import datetime, timedelta
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class DynamicPortfolioBacktest:
    def __init__(self):
        print("📈 动态CTA投资组合管理系统 2023-2026 历史回测")
        print("="*70)
        
        # 策略配置
        self.strategies_config = {
            'BTCUSDT_FixedMomentum': {
                'symbol': 'BTCUSDT',
                'strategy_type': 'FixedMomentum',
                'initial_weight': 0.0,
                'datafile': 'BTCUSDT_minute_data_2023_2026.csv'
            },
            'ETHUSDT_FixedMomentum': {
                'symbol': 'ETHUSDT', 
                'strategy_type': 'FixedMomentum',
                'initial_weight': 0.0,
                'datafile': 'ETHUSDT_minute_data_2023_2026.csv'
            },
            'ADAUSDT_FixedMomentum': {
                'symbol': 'ADAUSDT',
                'strategy_type': 'FixedMomentum', 
                'initial_weight': 0.0,
                'datafile': 'ADAUSDT_minute_data_2023_2026.csv'
            },
            'BTCUSDT_FixedBreakout': {
                'symbol': 'BTCUSDT',
                'strategy_type': 'FixedBreakout',
                'initial_weight': 0.2,
                'datafile': 'BTCUSDT_minute_data_2023_2026.csv'
            },
            'ETHUSDT_FixedBreakout': {
                'symbol': 'ETHUSDT',
                'strategy_type': 'FixedBreakout', 
                'initial_weight': 0.8,
                'datafile': 'ETHUSDT_minute_data_2023_2026.csv'
            }
        }
        
        # 管理参数
        self.rebalance_threshold = 0.05  # 5%
        self.optimization_frequency = 7   # 7天（每周）
        self.stress_test_frequency = 30   # 30天
        self.transaction_cost = 0.0005    # 0.05%
        
        # 回测参数
        self.start_date = '2023-01-01'
        self.end_date = '2026-04-14'  # 完整时间段
        self.initial_capital = 100000
        
        # 回测记录
        self.portfolio_history = []
        self.rebalance_history = []
        self.optimization_history = []
        self.stress_test_history = []
        self.daily_returns = []
        
        # 策略数据缓存
        self.strategy_data_cache = {}
        
        print(f"📊 回测期间: {self.start_date} - {self.end_date}")
        print(f"💰 初始资金: ${self.initial_capital:,}")
        print(f"⚖️ 再平衡阈值: ±{self.rebalance_threshold:.0%}")
        print(f"🔄 优化频率: {self.optimization_frequency}天")
    
    def load_strategy_data(self, symbol, strategy_type, start_date=None, end_date=None):
        """加载策略数据"""
        try:
            strategy_name = f"{symbol}_{strategy_type}"
            
            if strategy_name in self.strategy_data_cache:
                df = self.strategy_data_cache[strategy_name].copy()
            else:
                datafile = self.strategies_config[strategy_name]['datafile']
                print(f"   📂 加载 {datafile}...")
                
                df = pd.read_csv(datafile, nrows=500000)
                
                # 标准化列名
                df.columns = df.columns.str.replace(' ', '_').str.lower()
                required_cols = ['open_time', 'close', 'volume', 'high', 'low']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    print(f"      ❌ 缺少必要列: {missing_cols}")
                    return None
                
                # 时间处理
                df['datetime'] = pd.to_datetime(df['open_time'])
                df = df.set_index('datetime').sort_index()
                
                # 计算技术指标
                df = self.calculate_technical_indicators(df)
                
                # 生成策略信号和收益
                if strategy_type == 'FixedMomentum':
                    df = self.generate_momentum_strategy(df)
                elif strategy_type == 'FixedBreakout':
                    df = self.generate_breakout_strategy(df)
                
                self.strategy_data_cache[strategy_name] = df.copy()
            
            # 筛选时间段
            if start_date and end_date:
                df = df[start_date:end_date].copy()
            
            return df
            
        except Exception as e:
            print(f"      ❌ 加载失败: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """计算技术指标"""
        df['returns'] = df['close'].pct_change().fillna(0)
        
        # 移动平均线
        for period in [10, 21, 50]:
            df[f'sma_{period}'] = df['close'].rolling(period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        
        # 布林带
        df['bb_mid'] = df['sma_21']
        df['bb_std'] = df['close'].rolling(21).std()
        df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std'] 
        df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
        
        # RSI
        df['rsi'] = self.calculate_rsi(df['close'], 14)
        
        # 价格和成交量比率
        df['price_sma_ratio'] = df['close'] / df['sma_21']
        df['volume_sma'] = df['volume'].rolling(21).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        return df.fillna(method='bfill').fillna(0)
    
    def calculate_rsi(self, prices, period=14):
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def generate_momentum_strategy(self, df):
        """生成动量策略"""
        signals = pd.Series(0, index=df.index)
        
        # 每小时重采样决策
        hourly_data = df.resample('1H').last().fillna(method='ffill')
        trend_up = hourly_data['ema_10'] > hourly_data['ema_21']
        price_strength = abs(hourly_data['price_sma_ratio'] - 1) > 0.02
        volume_confirm = hourly_data['volume_ratio'] > 1.0
        
        hourly_signals = pd.Series(0, index=hourly_data.index)
        hourly_signals[trend_up & price_strength & volume_confirm] = 1
        hourly_signals[~trend_up & price_strength & volume_confirm] = -1
        
        # 分钟级别信号插值
        signals = hourly_signals.reindex(df.index, method='ffill').fillna(0)
        
        # 强制持仓1小时
        signals = self.enforce_holding_period(signals, 60)
        
        # 计算策略收益
        df['position'] = signals
        df['strategy_returns'] = signals.shift(1) * df['returns'] - signals.diff().abs() * self.transaction_cost
        
        return df
    
    def generate_breakout_strategy(self, df):
        """生成突破策略"""
        signals = pd.Series(0, index=df.index)
        
        # 每4小时重采样决策
        data_4h = df.resample('4H').last().fillna(method='ffill')
        
        breakout_up = (data_4h['close'] > data_4h['bb_upper']) & (data_4h['volume_ratio'] > 1.2)
        breakout_down = (data_4h['close'] < data_4h['bb_lower']) & (data_4h['volume_ratio'] > 1.2)
        
        signals_4h = pd.Series(0, index=data_4h.index)
        signals_4h[breakout_up] = 1
        signals_4h[breakout_down] = -1
        
        # 分钟级别信号插值
        signals = signals_4h.reindex(df.index, method='ffill').fillna(0)
        
        # 强制持仓4小时
        signals = self.enforce_holding_period(signals, 240)
        
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
    
    def calculate_portfolio_metrics(self, strategy_data, lookback_days=7):
        """计算投资组合指标"""
        if strategy_data is None or len(strategy_data) == 0:
            return None
            
        end_date = strategy_data.index[-1]
        start_date = end_date - timedelta(days=lookback_days)
        
        recent_data = strategy_data[start_date:end_date].copy()
        
        if len(recent_data) < 100:
            return None
        
        strategy_returns = recent_data['strategy_returns']
        
        # 基础指标
        total_return = (1 + strategy_returns).prod() - 1
        days = len(recent_data) / (24 * 60) 
        annualized_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
        
        volatility = strategy_returns.std() * np.sqrt(365 * 24 * 60)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cum_returns = (1 + strategy_returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdown = (cum_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_return': total_return
        }
    
    def optimize_portfolio_weights(self, current_date, lookback_days=7):
        """优化投资组合权重"""
        print(f"\n🔄 执行权重优化 ({current_date.strftime('%Y-%m-%d')})")
        print("="*60)
        
        strategy_names = list(self.strategies_config.keys())
        expected_returns = []
        volatilities = []
        valid_strategies = []
        
        # 计算各策略指标
        for strategy_name in strategy_names:
            symbol = self.strategies_config[strategy_name]['symbol']
            strategy_type = self.strategies_config[strategy_name]['strategy_type']
            
            end_date = current_date
            start_date = end_date - timedelta(days=lookback_days)
            
            strategy_data = self.load_strategy_data(symbol, strategy_type, start_date, end_date)
            
            if strategy_data is not None:
                metrics = self.calculate_portfolio_metrics(strategy_data, lookback_days)
                if metrics:
                    expected_returns.append(metrics['annualized_return'])
                    volatilities.append(metrics['volatility'])
                    valid_strategies.append(strategy_name)
                    
                    print(f"   📊 {strategy_name}: 收益{metrics['annualized_return']:.1%}, 波动{metrics['volatility']:.1%}")
        
        if len(valid_strategies) < 2:
            print("   ⚠️ 有效策略数量不足，使用现有权重")
            return None
        
        # 构建协方差矩阵
        returns_matrix = []
        for strategy_name in valid_strategies:
            symbol = self.strategies_config[strategy_name]['symbol'] 
            strategy_type = self.strategies_config[strategy_name]['strategy_type']
            
            end_date = current_date
            start_date = end_date - timedelta(days=lookback_days)
            
            strategy_data = self.load_strategy_data(symbol, strategy_type, start_date, end_date)
            daily_returns = strategy_data['strategy_returns'].resample('D').sum()
            returns_matrix.append(daily_returns)
        
        returns_df = pd.DataFrame(returns_matrix).T.fillna(0)
        cov_matrix = returns_df.cov().values
        expected_returns = np.array(expected_returns)
        
        # 马科维茨优化
        n = len(expected_returns)
        
        def objective(weights):
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            return -(portfolio_return - 0.5 * 0.5 * portfolio_variance)  # 风险厌恶系数0.5
        
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = [(0.0, 0.8) for _ in range(n)]
        x0 = np.array([1/n] * n)
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_weights = result.x
            portfolio_return = np.sum(optimal_weights * expected_returns)
            portfolio_vol = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
            sharpe = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
            
            print(f"\n   ✅ 优化成功:")
            print(f"      预期收益: {portfolio_return:.2%}")
            print(f"      预期波动: {portfolio_vol:.2%}")  
            print(f"      预期夏普: {sharpe:.3f}")
            print(f"\n   📊 新权重配置:")
            
            weight_dict = {}
            for i, strategy_name in enumerate(valid_strategies):
                weight = optimal_weights[i]
                weight_dict[strategy_name] = weight
                if weight > 0.01:  # 只显示>1%的权重
                    print(f"      {strategy_name}: {weight:.1%}")
            
            # 补充缺失策略权重为0
            for strategy_name in strategy_names:
                if strategy_name not in weight_dict:
                    weight_dict[strategy_name] = 0.0
            
            return weight_dict
        else:
            print(f"   ❌ 优化失败: {result.message}")
            return None
    
    def check_rebalance_needed(self, current_weights, target_weights):
        """检查再平衡需求"""
        max_deviation = 0
        rebalance_needed = False
        
        for strategy in target_weights:
            current = current_weights.get(strategy, 0)
            target = target_weights[strategy]
            
            deviation = abs(current - target)
            if target > 0:
                deviation_pct = deviation / target
                if deviation_pct > self.rebalance_threshold:
                    rebalance_needed = True
                max_deviation = max(max_deviation, deviation_pct)
            elif current > 0.01:  # 目标为0但当前不为0
                rebalance_needed = True
                max_deviation = max(max_deviation, current)
        
        return rebalance_needed, max_deviation
    
    def execute_rebalance(self, current_weights, target_weights, portfolio_value):
        """执行再平衡"""
        trades = []
        total_transaction_cost = 0
        
        for strategy in target_weights:
            current_weight = current_weights.get(strategy, 0)
            target_weight = target_weights[strategy]
            
            current_value = current_weight * portfolio_value
            target_value = target_weight * portfolio_value
            trade_amount = target_value - current_value
            
            if abs(trade_amount) > portfolio_value * 0.001:  # 最小交易金额
                transaction_cost = abs(trade_amount) * self.transaction_cost
                total_transaction_cost += transaction_cost
                
                trades.append({
                    'strategy': strategy,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'trade_amount': trade_amount,
                    'transaction_cost': transaction_cost
                })
        
        new_portfolio_value = portfolio_value - total_transaction_cost
        
        return trades, total_transaction_cost, new_portfolio_value
    
    def run_historical_backtest(self):
        """运行历史回测"""
        print(f"\n🚀 开始历史回测 ({self.start_date} - {self.end_date})")
        print("="*70)
        
        # 初始化
        current_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        portfolio_value = self.initial_capital
        
        # 初始权重
        current_weights = {name: config['initial_weight'] 
                         for name, config in self.strategies_config.items()}
        target_weights = current_weights.copy()
        
        last_optimization_date = current_date
        last_stress_test_date = current_date
        
        daily_dates = pd.date_range(start=current_date, end=end_date, freq='D')
        
        print(f"📅 回测时间点: {len(daily_dates)} 天")
        
        for i, date in enumerate(daily_dates):
            if i % 30 == 0:  # 每30天打印进度
                progress = f"📈 回测进度: {i}/{len(daily_dates)} ({date.strftime('%Y-%m-%d')})"
                print(progress)
            
            # 1. 定期优化检查 (7天，每周)
            if (date - last_optimization_date).days >= self.optimization_frequency:
                print(f"🔄 执行权重优化 ({date.strftime('%Y-%m-%d')})")
                new_target_weights = self.optimize_portfolio_weights(date, lookback_days=7)
                if new_target_weights:
                    old_weights = target_weights.copy()
                    target_weights = new_target_weights
                    
                    self.optimization_history.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'old_weights': old_weights,
                        'new_weights': target_weights
                    })
                    
                    last_optimization_date = date
                    print(f"✅ 权重优化完成，下次优化日期: {(date + timedelta(days=self.optimization_frequency)).strftime('%Y-%m-%d')}")
                else:
                    # 即使优化失败也更新时间，避免每天重试
                    last_optimization_date = date
            
            # 2. 再平衡检查
            needs_rebalance, max_deviation = self.check_rebalance_needed(current_weights, target_weights)
            
            if needs_rebalance:
                trades, transaction_cost, new_portfolio_value = self.execute_rebalance(
                    current_weights, target_weights, portfolio_value)
                
                if trades:
                    self.rebalance_history.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'trades': trades,
                        'transaction_cost': transaction_cost,
                        'max_deviation': max_deviation,
                        'portfolio_value_before': portfolio_value,
                        'portfolio_value_after': new_portfolio_value
                    })
                    
                    current_weights = target_weights.copy()
                    portfolio_value = new_portfolio_value
            
            # 3. 计算当日投资组合收益
            daily_portfolio_return = self.calculate_daily_portfolio_return(date, current_weights)
            if daily_portfolio_return is not None:
                portfolio_value *= (1 + daily_portfolio_return)
                
                self.portfolio_history.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'portfolio_value': portfolio_value,
                    'daily_return': daily_portfolio_return,
                    'weights': current_weights.copy()
                })
            
            # 4. 定期压力测试 (30天)
            if (date - last_stress_test_date).days >= self.stress_test_frequency:
                print(f"\n🎲 执行定期压力测试 ({date.strftime('%Y-%m-%d')})")
                stress_result = self.run_stress_test(date, current_weights)
                if stress_result:
                    self.stress_test_history.append(stress_result)
                    print(f"✅ 压力测试完成，风险等级: {self.assess_risk_level(stress_result)}")
                last_stress_test_date = date
        
        print(f"\n✅ 回测完成！")
        self.calculate_backtest_performance()
        
    def calculate_daily_portfolio_return(self, date, weights):
        """计算日投资组合收益"""
        try:
            portfolio_return = 0
            
            for strategy_name, weight in weights.items():
                if weight > 0:
                    symbol = self.strategies_config[strategy_name]['symbol']
                    strategy_type = self.strategies_config[strategy_name]['strategy_type']
                    
                    # 获取策略当日数据
                    strategy_data = self.load_strategy_data(symbol, strategy_type)
                    if strategy_data is not None and len(strategy_data) > 0:
                        daily_data = strategy_data[strategy_data.index.date == date.date()]
                        
                        if not daily_data.empty and 'strategy_returns' in daily_data.columns:
                            daily_strategy_return = daily_data['strategy_returns'].sum()
                            portfolio_return += weight * daily_strategy_return
            
            return portfolio_return
            
        except Exception as e:
            # 返回0收益而不是None，避免后续计算中断
            return 0.0
    
    def run_stress_test(self, current_date, current_weights):
        """运行压力测试"""
        try:
            strategy_names = list(current_weights.keys())
            weights_array = np.array([current_weights[s] for s in strategy_names])
            
            # 简化的压力测试
            expected_returns = []
            volatilities = []
            
            for strategy_name in strategy_names:
                symbol = self.strategies_config[strategy_name]['symbol']
                strategy_type = self.strategies_config[strategy_name]['strategy_type'] 
                
                lookback_start = current_date - timedelta(days=60)
                strategy_data = self.load_strategy_data(symbol, strategy_type, lookback_start, current_date)
                
                if strategy_data is not None and len(strategy_data) > 0:
                    metrics = self.calculate_portfolio_metrics(strategy_data, 60)
                    if metrics:
                        expected_returns.append(metrics['annualized_return'])
                        volatilities.append(metrics['volatility'])
                    else:
                        expected_returns.append(0)
                        volatilities.append(0.1)
                else:
                    expected_returns.append(0)
                    volatilities.append(0.1)
            
            expected_returns = np.array(expected_returns)
            volatilities = np.array(volatilities)
            
            # 投资组合级别指标
            portfolio_return = np.sum(weights_array * expected_returns)
            portfolio_vol = np.sqrt(np.sum((weights_array * volatilities) ** 2))  # 简化计算
            
            # 蒙特卡罗模拟 (简化版) 
            time_horizon = 7  # 每周优化时间窗口
            num_simulations = 1000
            
            daily_return = portfolio_return / 365
            daily_vol = max(portfolio_vol / np.sqrt(365), 0.001)  # 防止零波动
            
            simulations = []
            for _ in range(num_simulations):
                random_returns = np.random.normal(daily_return, daily_vol, time_horizon)
                cumulative_return = np.prod(1 + random_returns) - 1
                simulations.append(cumulative_return)
            
            simulations = np.array(simulations)
            
            return {
                'date': current_date.strftime('%Y-%m-%d'),
                'portfolio_weights': current_weights,
                'expected_return': float(portfolio_return),
                'expected_volatility': float(portfolio_vol),
                'var_95': float(np.percentile(simulations, 5)),
                'var_99': float(np.percentile(simulations, 1)),
                'max_loss': float(np.min(simulations)),
                'prob_loss': float(np.mean(simulations < 0)),
                'mean_simulation': float(np.mean(simulations)),
                'std_simulation': float(np.std(simulations))
            }
        
        except Exception as e:
            print(f"      ⚠️ 压力测试失败: {e}")
            return None
    
    def assess_risk_level(self, stress_result):
        """评估风险等级"""
        if not stress_result:
            return "未知"
            
        var_95 = stress_result.get('var_95', 0)
        prob_loss = stress_result.get('prob_loss', 0)
        
        risk_score = 0
        
        # VaR评分
        if var_95 > -0.05:
            risk_score += 1  # 低风险
        elif var_95 > -0.15:
            risk_score += 2  # 中等风险
        else:
            risk_score += 3  # 高风险
            
        # 亏损概率评分
        if prob_loss < 0.1:
            risk_score += 1
        elif prob_loss < 0.3:
            risk_score += 2
        else:
            risk_score += 3
        
        if risk_score <= 3:
            return "🟢 低风险"
        elif risk_score <= 5:
            return "🟡 中等风险"
        else:
            return "🔴 高风险"
    
    def calculate_backtest_performance(self):
        """计算回测表现"""
        print(f"\n📊 回测表现分析")
        print("="*50)
        
        if not self.portfolio_history:
            print("❌ 无投资组合历史数据")
            return
        
        # 转换为DataFrame
        df = pd.DataFrame(self.portfolio_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # 基本统计
        initial_value = self.initial_capital
        final_value = df['portfolio_value'].iloc[-1]
        total_return = (final_value / initial_value - 1)
        
        days = len(df)
        years = days / 365
        annualized_return = (final_value / initial_value) ** (1/years) - 1
        
        daily_returns = pd.Series(df['daily_return'], index=df.index)
        volatility = daily_returns.std() * np.sqrt(365)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        portfolio_values = df['portfolio_value']
        running_max = portfolio_values.expanding().max()
        drawdowns = (portfolio_values - running_max) / running_max
        max_drawdown = drawdowns.min()
        
        # 胜率
        win_rate = (daily_returns > 0).mean()
        
        # 打印结果
        print(f"💰 初始资金: ${initial_value:,.2f}")
        print(f"💰 最终价值: ${final_value:,.2f}")
        print(f"📈 总收益: {total_return:.2%}")
        print(f"📈 年化收益: {annualized_return:.2%}")
        print(f"📊 年化波动: {volatility:.2%}")
        print(f"⚡ 夏普比率: {sharpe_ratio:.3f}")
        print(f"📉 最大回撤: {max_drawdown:.2%}")
        print(f"🎯 胜率: {win_rate:.1%}")
        print(f"🔄 再平衡次数: {len(self.rebalance_history)}")
        print(f"⚙️ 优化次数: {len(self.optimization_history)}")
        print(f"🎲 压力测试次数: {len(self.stress_test_history)}")
        
        # 月度统计
        monthly_returns = daily_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        positive_months = (monthly_returns > 0).sum()
        total_months = len(monthly_returns)
        
        print(f"\n📅 月度表现:")
        print(f"   正收益月份: {positive_months}/{total_months} ({positive_months/total_months:.1%})")
        print(f"   最佳月份: {monthly_returns.max():.2%}")
        print(f"   最差月份: {monthly_returns.min():.2%}")
        
        # 保存详细数据
        self.detailed_df = df
        
    def save_backtest_results(self):
        """保存回测结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dynamic_portfolio_backtest_2023_2026_{timestamp}.json"
        
        # 计算汇总统计
        if hasattr(self, 'detailed_df'):
            df = self.detailed_df
            initial_value = self.initial_capital
            final_value = df['portfolio_value'].iloc[-1]
            total_return = (final_value / initial_value - 1)
            
            days = len(df)
            years = days / 365
            annualized_return = (final_value / initial_value) ** (1/years) - 1
            
            daily_returns = pd.Series(df['daily_return'], index=df.index)
            volatility = daily_returns.std() * np.sqrt(365)
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            
            portfolio_values = df['portfolio_value']
            running_max = portfolio_values.expanding().max()
            drawdowns = (portfolio_values - running_max) / running_max
            max_drawdown = drawdowns.min()
            
            win_rate = (daily_returns > 0).mean()
        else:
            final_value = self.initial_capital
            total_return = 0
            annualized_return = 0
            volatility = 0
            sharpe_ratio = 0
            max_drawdown = 0
            win_rate = 0
        
        results = {
            'backtest_info': {
                'system': '动态CTA投资组合管理系统',
                'version': '2.0',
                'backtest_period': f"{self.start_date} - {self.end_date}",
                'timestamp': timestamp
            },
            'parameters': {
                'initial_capital': self.initial_capital,
                'rebalance_threshold': self.rebalance_threshold,
                'optimization_frequency': self.optimization_frequency,
                'stress_test_frequency': self.stress_test_frequency,
                'transaction_cost': self.transaction_cost
            },
            'performance_summary': {
                'initial_value': self.initial_capital,
                'final_value': float(final_value),
                'total_return': float(total_return),
                'annualized_return': float(annualized_return),
                'volatility': float(volatility),
                'sharpe_ratio': float(sharpe_ratio),
                'max_drawdown': float(max_drawdown),
                'win_rate': float(win_rate)
            },
            'management_activities': {
                'rebalances': len(self.rebalance_history),
                'optimizations': len(self.optimization_history),
                'stress_tests': len(self.stress_test_history)
            },
            'detailed_history': {
                'portfolio_history': self.portfolio_history[-100:],  # 最近100天
                'rebalance_history': self.rebalance_history,
                'optimization_history': self.optimization_history,
                'stress_test_history': self.stress_test_history[-10:]  # 最近10次
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 回测结果已保存: {filename}")
        return filename

def main():
    """主函数"""
    backtest = DynamicPortfolioBacktest()
    
    print(f"\n📋 策略配置:")
    for name, config in backtest.strategies_config.items():
        print(f"   📊 {name}: {config['initial_weight']:.0%}")
    
    print(f"\n🚀 开始执行2023-2026历史回测...")
    print("   这可能需要几分钟时间...")
    
    try:
        backtest.run_historical_backtest()
        filename = backtest.save_backtest_results()
        
        print(f"\n🎉 历史回测完成！")
        print(f"📄 详细结果文件: {filename}")
        print(f"\n💡 建议查看:")
        print(f"   1. 投资组合价值变化曲线")
        print(f"   2. 再平衡活动效果分析")
        print(f"   3. 压力测试风险评估")
        
    except Exception as e:
        print(f"❌ 回测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()