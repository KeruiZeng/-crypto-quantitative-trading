#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 动态CTA投资组合管理系统
=====================================
集成定期重新优化、动态再平衡、压力测试功能
基于现代投资组合理论的自动化管理系统
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from scipy.optimize import minimize
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class DynamicPortfolioManager:
    def __init__(self):
        # 当前策略配置
        self.strategies_data = {
            'BTCUSDT_FixedMomentum': {
                'return': 0.2984, 'sharpe': 4.737, 'volatility': 0.063, 
                'max_drawdown': -0.0309, 'win_rate': 0.551, 'current_weight': 0.0
            },
            'ETHUSDT_FixedMomentum': {
                'return': 0.1446, 'sharpe': 4.637, 'volatility': 0.031, 
                'max_drawdown': -0.0027, 'win_rate': 0.484, 'current_weight': 0.0
            }, 
            'ADAUSDT_FixedMomentum': {
                'return': 0.1914, 'sharpe': 3.635, 'volatility': 0.053, 
                'max_drawdown': -0.0100, 'win_rate': 0.564, 'current_weight': 0.0
            },
            'BTCUSDT_FixedBreakout': {
                'return': 1.3928, 'sharpe': 10.699, 'volatility': 0.130, 
                'max_drawdown': -0.0232, 'win_rate': 0.517, 'current_weight': 0.20
            },
            'ETHUSDT_FixedBreakout': {
                'return': 2.0986, 'sharpe': 14.008, 'volatility': 0.150, 
                'max_drawdown': -0.0276, 'win_rate': 0.511, 'current_weight': 0.80
            },
        }
        
        # 动态管理参数
        self.rebalance_threshold = 0.05  # 5%权重偏离阈值
        self.optimization_frequency = 7   # 7天重新优化（每周）
        self.stress_test_frequency = 30   # 30天压力测试
        
        # 历史记录
        self.performance_history = []
        self.rebalance_history = []
        self.optimization_history = []
        self.stress_test_history = []
        
        # 当前组合状态
        self.last_optimization_date = None
        self.last_stress_test_date = None
        self.portfolio_value = 100000  # 初始100k
        
        print("🤖 动态CTA投资组合管理系统")
        print("📊 集成功能: 定期优化 + 动态再平衡 + 压力测试")
        print(f"⚖️ 再平衡阈值: ±{self.rebalance_threshold:.0%}")
        print(f"🔄 优化频率: {self.optimization_frequency}天")
        print(f"🎲 压力测试频率: {self.stress_test_frequency}天")
        
    def load_strategy_data(self, symbol, strategy_type, start_date, end_date):
        """加载指定时间段的策略数据"""
        try:
            file_path = f"{symbol}_minute_data_2023_2026.csv"
            df = pd.read_csv(file_path, nrows=150000)
            
            df.columns = df.columns.str.replace(' ', '_').str.lower()
            df['date'] = pd.to_datetime(df['open_time'])
            df = df.set_index('date').sort_index()
            
            # 筛选时间段
            df = df[start_date:end_date].copy()
            
            # 基础指标
            df['returns'] = df['close'].pct_change().fillna(0)
            
            # 技术指标
            for period in [10, 21, 50]:
                df[f'sma_{period}'] = df['close'].rolling(period).mean()
                df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
                df[f'rsi_{period}'] = self.calculate_rsi(df['close'], period)
            
            df['price_sma_ratio'] = df['close'] / df['sma_21']
            df['volume_sma'] = df['volume'].rolling(21).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # 模拟策略收益
            if strategy_type == "FixedMomentum":
                df['strategy_returns'] = self.simulate_momentum_returns(df)
            elif strategy_type == "FixedBreakout":
                df['strategy_returns'] = self.simulate_breakout_returns(df)
            
            return df
            
        except Exception as e:
            print(f"❌ {symbol}_{strategy_type} 数据加载失败: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def simulate_momentum_returns(self, df):
        """模拟动量策略收益"""
        signals = pd.Series(0, index=df.index)
        
        # 每小时信号
        hourly_data = df.resample('1H').last().fillna(method='ffill')
        trend_up = hourly_data['ema_10'] > hourly_data['ema_21']
        price_strength = abs(hourly_data['price_sma_ratio'] - 1) > 0.02
        volume_confirm = hourly_data['volume_ratio'] > 1.0
        
        hourly_signals = pd.Series(0, index=hourly_data.index)
        hourly_signals[trend_up & price_strength & volume_confirm] = 1
        hourly_signals[~trend_up & price_strength & volume_confirm] = -1
        
        signals = hourly_signals.reindex(df.index, method='ffill').fillna(0)
        
        # 强制持仓1小时
        signals = self.hold_position(signals, 60)
        strategy_returns = signals.shift(1) * df['returns'] - signals.diff().abs() * 0.0005
        return strategy_returns.fillna(0)
    
    def simulate_breakout_returns(self, df):
        """模拟突破策略收益"""
        signals = pd.Series(0, index=df.index)
        
        # 每4小时信号
        data_4h = df.resample('4H').last().fillna(method='ffill')
        
        bb_mid = data_4h['sma_21']
        bb_std = data_4h['close'].rolling(21).std()
        bb_upper = bb_mid + 2 * bb_std
        bb_lower = bb_mid - 2 * bb_std
        
        breakout_up = (data_4h['close'] > bb_upper) & (data_4h['volume_ratio'] > 1.2)
        breakout_down = (data_4h['close'] < bb_lower) & (data_4h['volume_ratio'] > 1.2)
        
        signals_4h = pd.Series(0, index=data_4h.index)
        signals_4h[breakout_up] = 1
        signals_4h[breakout_down] = -1
        
        signals = signals_4h.reindex(df.index, method='ffill').fillna(0)
        
        # 强制持仓4小时
        signals = self.hold_position(signals, 240)
        strategy_returns = signals.shift(1) * df['returns'] - signals.diff().abs() * 0.0005
        return strategy_returns.fillna(0)
    
    def hold_position(self, signals, min_hold_periods):
        """强制持仓管理"""
        fixed_signals = signals.copy()
        position = 0
        hold_count = 0
        
        for i in range(len(signals)):
            current_signal = signals.iloc[i]
            if current_signal != 0 and hold_count == 0:
                position = current_signal
                hold_count = min_hold_periods
            elif hold_count > 0:
                hold_count -= 1
                if hold_count == 0:
                    position = 0
            fixed_signals.iloc[i] = position
        return fixed_signals
    
    def calculate_rolling_covariance(self, lookback_days=90):
        """计算滚动协方差矩阵"""
        print(f"\n📊 计算{lookback_days}天滚动协方差矩阵")
        print("="*50)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        strategy_names = list(self.strategies_data.keys())
        returns_data = {}
        
        for strategy_name in strategy_names:
            symbol, strategy_type = strategy_name.split('_', 1)
            df = self.load_strategy_data(symbol, strategy_type, start_date, end_date)
            
            if df is not None and len(df) > 0:
                # 计算日收益
                daily_returns = df['strategy_returns'].resample('D').sum()
                returns_data[strategy_name] = daily_returns
        
        if len(returns_data) < 2:
            print("   ⚠️ 数据不足，使用历史协方差矩阵")
            return self.get_historical_covariance_matrix()
        
        # 构建收益矩阵
        returns_df = pd.DataFrame(returns_data).fillna(0)
        
        if len(returns_df) < 30:
            print("   ⚠️ 时间序列太短，使用历史协方差矩阵")
            return self.get_historical_covariance_matrix()
        
        # 计算协方差矩阵
        cov_matrix = returns_df.cov().values
        
        print(f"   ✅ 成功计算协方差矩阵 ({len(returns_df)}天数据)")
        print("   📈 策略相关性:")
        corr_matrix = returns_df.corr()
        for i in range(len(strategy_names)):
            for j in range(i+1, len(strategy_names)):
                corr = corr_matrix.iloc[i, j]
                print(f"      {strategy_names[i]} vs {strategy_names[j]}: {corr:.3f}")
        
        return cov_matrix
    
    def get_historical_covariance_matrix(self):
        """获取历史协方差矩阵"""
        strategy_names = list(self.strategies_data.keys())
        n = len(strategy_names)
        
        # 基于历史相关性构建协方差矩阵
        asset_correlations = {
            ('BTCUSDT', 'ETHUSDT'): 0.75,
            ('BTCUSDT', 'ADAUSDT'): 0.65, 
            ('ETHUSDT', 'ADAUSDT'): 0.70,
        }
        
        corr_matrix = np.eye(n)
        for i, strategy1 in enumerate(strategy_names):
            for j, strategy2 in enumerate(strategy_names):
                if i != j:
                    asset1 = strategy1.split('_')[0]
                    asset2 = strategy2.split('_')[0]
                    
                    if asset1 == asset2:
                        corr_matrix[i, j] = 0.85  # 相同资产高相关
                    elif (asset1, asset2) in asset_correlations:
                        corr_matrix[i, j] = asset_correlations[(asset1, asset2)]
                    elif (asset2, asset1) in asset_correlations:
                        corr_matrix[i, j] = asset_correlations[(asset2, asset1)]
                    else:
                        corr_matrix[i, j] = 0.50
        
        volatilities = np.array([self.strategies_data[s]['volatility'] for s in strategy_names])
        cov_matrix = np.outer(volatilities, volatilities) * corr_matrix
        
        return cov_matrix
    
    def quarterly_optimization(self, force_update=False):
        """季度重新优化"""
        current_date = datetime.now()
        
        if (self.last_optimization_date is None or 
            (current_date - self.last_optimization_date).days >= self.optimization_frequency or
            force_update):
            
            print(f"\n🔄 执行季度优化 ({current_date.strftime('%Y-%m-%d')})")
            print("="*60)
            
            # 1. 更新策略表现数据
            self.update_strategy_performance()
            
            # 2. 重新计算协方差矩阵
            cov_matrix = self.calculate_rolling_covariance()
            
            # 3. 马科维茨重新优化
            strategy_names = list(self.strategies_data.keys())
            expected_returns = np.array([self.strategies_data[s]['return'] for s in strategy_names])
            
            optimal_weights = self.optimize_portfolio(expected_returns, cov_matrix)
            
            if optimal_weights is not None:
                # 4. 更新目标权重
                old_weights = [self.strategies_data[s]['current_weight'] for s in strategy_names]
                
                print(f"\n📊 权重优化结果:")
                for i, strategy in enumerate(strategy_names):
                    old_weight = old_weights[i]
                    new_weight = optimal_weights[i]
                    change = new_weight - old_weight
                    
                    self.strategies_data[strategy]['target_weight'] = new_weight
                    
                    print(f"   {strategy}: {old_weight:.1%} → {new_weight:.1%} ({change:+.1%})")
                
                # 5. 记录优化历史
                optimization_record = {
                    'date': current_date.isoformat(),
                    'old_weights': {strategy_names[i]: old_weights[i] for i in range(len(strategy_names))},
                    'new_weights': {strategy_names[i]: optimal_weights[i] for i in range(len(strategy_names))},
                    'trigger': 'scheduled' if not force_update else 'manual'
                }
                self.optimization_history.append(optimization_record)
                
                self.last_optimization_date = current_date
                print(f"✅ 季度优化完成")
                
                return True
            else:
                print(f"❌ 优化失败，保持当前权重")
                return False
        else:
            days_until_next = self.optimization_frequency - (current_date - self.last_optimization_date).days
            print(f"⏱️ 距离下次优化还有 {days_until_next} 天")
            return False
    
    def update_strategy_performance(self):
        """更新策略表现数据"""
        print(f"\n📈 更新策略表现数据")
        print("="*40)
        
        # 模拟更新（实际应该从实时数据获取）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        for strategy_name in self.strategies_data.keys():
            symbol, strategy_type = strategy_name.split('_', 1)
            df = self.load_strategy_data(symbol, strategy_type, start_date, end_date)
            
            if df is not None and len(df) > 1000:
                # 计算最新表现指标
                strategy_returns = df['strategy_returns']
                total_return = (1 + strategy_returns).prod() - 1
                days = len(df) / (24 * 60)
                annualized_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
                
                volatility = strategy_returns.std() * np.sqrt(365 * 24 * 60)
                sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
                
                # 更新数据
                old_return = self.strategies_data[strategy_name]['return']
                old_sharpe = self.strategies_data[strategy_name]['sharpe']
                
                self.strategies_data[strategy_name]['return'] = annualized_return
                self.strategies_data[strategy_name]['sharpe'] = sharpe_ratio
                self.strategies_data[strategy_name]['volatility'] = volatility
                
                change_return = annualized_return - old_return
                change_sharpe = sharpe_ratio - old_sharpe
                
                print(f"   📊 {strategy_name}:")
                print(f"      收益: {old_return:.1%} → {annualized_return:.1%} ({change_return:+.1%})")
                print(f"      夏普: {old_sharpe:.2f} → {sharpe_ratio:.2f} ({change_sharpe:+.2f})")
    
    def optimize_portfolio(self, expected_returns, cov_matrix, risk_aversion=0.5):
        """优化投资组合权重"""
        n = len(expected_returns)
        
        def objective(weights):
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            return -(portfolio_return - 0.5 * risk_aversion * portfolio_variance)
        
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = [(0.0, 0.8) for _ in range(n)]
        x0 = np.array([1/n] * n)
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            portfolio_vol = np.sqrt(portfolio_variance)
            sharpe_ratio = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
            
            print(f"\n   ✅ 优化成功:")
            print(f"   📈 预期收益: {portfolio_return:.2%}")
            print(f"   📊 预期波动: {portfolio_vol:.2%}")
            print(f"   ⚡ 预期夏普: {sharpe_ratio:.3f}")
            
            return weights
        else:
            print(f"   ❌ 优化失败: {result.message}")
            return None
    
    def check_rebalance_needed(self):
        """检查是否需要再平衡"""
        print(f"\n⚖️ 检查再平衡需求")
        print("="*40)
        
        rebalance_needed = False
        strategy_names = list(self.strategies_data.keys())
        
        for strategy_name in strategy_names:
            current_weight = self.strategies_data[strategy_name]['current_weight']
            target_weight = self.strategies_data[strategy_name].get('target_weight', current_weight)
            
            deviation = abs(current_weight - target_weight)
            deviation_pct = deviation / target_weight if target_weight > 0 else 0
            
            if deviation_pct > self.rebalance_threshold:
                rebalance_needed = True
                print(f"   ⚠️ {strategy_name}: {current_weight:.1%} vs {target_weight:.1%} (偏离{deviation_pct:.1%})")
            else:
                print(f"   ✅ {strategy_name}: {current_weight:.1%} vs {target_weight:.1%} (偏离{deviation_pct:.1%})")
        
        if rebalance_needed:
            print(f"\n🔄 需要再平衡 (偏离阈值: ±{self.rebalance_threshold:.0%})")
            return True
        else:
            print(f"\n✅ 无需再平衡 (偏离均在阈值内)")
            return False
    
    def execute_rebalance(self):
        """执行再平衡"""
        print(f"\n🔄 执行投资组合再平衡")
        print("="*50)
        
        strategy_names = list(self.strategies_data.keys())
        rebalance_trades = []
        
        total_value = self.portfolio_value
        
        for strategy_name in strategy_names:
            current_weight = self.strategies_data[strategy_name]['current_weight']
            target_weight = self.strategies_data[strategy_name].get('target_weight', current_weight)
            
            current_value = current_weight * total_value
            target_value = target_weight * total_value
            trade_amount = target_value - current_value
            
            if abs(trade_amount) > total_value * 0.001:  # 最小交易金额0.1%
                rebalance_trades.append({
                    'strategy': strategy_name,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'trade_amount': trade_amount,
                    'action': 'BUY' if trade_amount > 0 else 'SELL'
                })
                
                # 更新权重
                self.strategies_data[strategy_name]['current_weight'] = target_weight
        
        if rebalance_trades:
            print(f"📊 执行 {len(rebalance_trades)} 笔再平衡交易:")
            
            total_transaction_cost = 0
            for trade in rebalance_trades:
                transaction_cost = abs(trade['trade_amount']) * 0.0005  # 0.05%交易成本
                total_transaction_cost += transaction_cost
                
                print(f"   {trade['action']} {trade['strategy']}: ${trade['trade_amount']:+,.0f}")
                print(f"      权重: {trade['current_weight']:.1%} → {trade['target_weight']:.1%}")
            
            print(f"\n💰 总交易成本: ${total_transaction_cost:,.2f}")
            
            # 记录再平衡历史
            rebalance_record = {
                'date': datetime.now().isoformat(),
                'trades': rebalance_trades,
                'total_cost': total_transaction_cost,
                'portfolio_value': total_value
            }
            self.rebalance_history.append(rebalance_record)
            
            print(f"✅ 再平衡完成")
            return True
        else:
            print(f"⚠️ 无需要执行的交易")
            return False
    
    def monte_carlo_stress_test(self, num_simulations=5000, time_horizon=90):
        """蒙特卡罗压力测试"""
        current_date = datetime.now()
        
        if (self.last_stress_test_date is None or 
            (current_date - self.last_stress_test_date).days >= self.stress_test_frequency):
            
            print(f"\n🎲 蒙特卡罗压力测试 ({current_date.strftime('%Y-%m-%d')})")
            print("="*60)
            print(f"📊 模拟参数: {num_simulations:,} 次 × {time_horizon} 天")
            
            # 获取当前权重和协方差矩阵
            strategy_names = list(self.strategies_data.keys())
            current_weights = np.array([self.strategies_data[s]['current_weight'] for s in strategy_names])
            expected_returns = np.array([self.strategies_data[s]['return'] for s in strategy_names])
            
            cov_matrix = self.calculate_rolling_covariance(lookback_days=60)
            
            # 组合参数
            portfolio_return = np.sum(current_weights * expected_returns)
            portfolio_vol = np.sqrt(np.dot(current_weights.T, np.dot(cov_matrix, current_weights)))
            
            # 日收益参数
            daily_return = portfolio_return / 365
            daily_vol = portfolio_vol / np.sqrt(365)
            
            # 蒙特卡罗模拟
            print(f"⚡ 执行蒙特卡罗模拟...")
            simulations = []
            
            for i in range(num_simulations):
                random_returns = np.random.normal(daily_return, daily_vol, time_horizon)
                cumulative_return = np.prod(1 + random_returns) - 1
                simulations.append(cumulative_return)
            
            simulations = np.array(simulations)
            
            # 风险指标计算
            mean_return = np.mean(simulations)
            std_return = np.std(simulations)
            var_95 = np.percentile(simulations, 5)
            var_99 = np.percentile(simulations, 1)
            cvar_95 = np.mean(simulations[simulations <= var_95])  # 条件风险价值
            max_loss = np.min(simulations)
            prob_loss = np.mean(simulations < 0)
            prob_large_loss = np.mean(simulations < -0.2)  # 大损失概率
            
            # 压力测试结果
            print(f"\n📈 压力测试结果 ({time_horizon}天):")
            print(f"   💰 预期收益: {mean_return:.2%} ± {std_return:.2%}")
            print(f"   📉 95% VaR: {var_95:.2%}")
            print(f"   📉 99% VaR: {var_99:.2%}")
            print(f"   💥 95% CVaR: {cvar_95:.2%}")
            print(f"   🚨 最大损失: {max_loss:.2%}")
            print(f"   📊 亏损概率: {prob_loss:.1%}")
            print(f"   ⚠️ 大损失概率(>20%): {prob_large_loss:.1%}")
            
            # 风险等级评估
            risk_score = self.assess_risk_level(var_95, var_99, prob_loss, prob_large_loss)
            
            # 记录压力测试历史
            stress_test_record = {
                'date': current_date.isoformat(),
                'time_horizon': time_horizon,
                'num_simulations': num_simulations,
                'results': {
                    'mean_return': mean_return,
                    'std_return': std_return,
                    'var_95': var_95,
                    'var_99': var_99,
                    'cvar_95': cvar_95,
                    'max_loss': max_loss,
                    'prob_loss': prob_loss,
                    'prob_large_loss': prob_large_loss,
                    'risk_score': risk_score
                },
                'portfolio_weights': {strategy_names[i]: current_weights[i] for i in range(len(strategy_names))}
            }
            self.stress_test_history.append(stress_test_record)
            
            self.last_stress_test_date = current_date
            
            print(f"\n🎯 风险评级: {risk_score}")
            self.generate_risk_recommendations(stress_test_record)
            
            return stress_test_record
        else:
            days_until_next = self.stress_test_frequency - (current_date - self.last_stress_test_date).days
            print(f"⏱️ 距离下次压力测试还有 {days_until_next} 天")
            return None
    
    def assess_risk_level(self, var_95, var_99, prob_loss, prob_large_loss):
        """评估风险等级"""
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
        
        # 大损失概率评分
        if prob_large_loss < 0.05:
            risk_score += 1
        elif prob_large_loss < 0.15:
            risk_score += 2
        else:
            risk_score += 3
        
        if risk_score <= 4:
            return "🟢 低风险"
        elif risk_score <= 6:
            return "🟡 中等风险"
        else:
            return "🔴 高风险"
    
    def generate_risk_recommendations(self, stress_test_record):
        """生成风险建议"""
        print(f"\n💡 风险管理建议:")
        results = stress_test_record['results']
        
        if results['var_95'] < -0.20:
            print("   ⚠️ 95% VaR过高，建议降低组合风险敞口")
        
        if results['prob_large_loss'] > 0.10:
            print("   🚨 大损失概率较高，建议增加防御性策略")
        
        if results['prob_loss'] > 0.40:
            print("   📉 亏损概率偏高，建议重新评估策略配置")
        
        if results['risk_score'] == "🔴 高风险":
            print("   🛑 风险等级过高，建议立即优化投资组合")
            print("      建议减少高波动策略权重，增加稳健策略配置")
        
        if results['std_return'] > 0.30:
            print("   📊 收益波动过大，建议提高组合稳定性")
    
    def generate_management_report(self):
        """生成管理报告"""
        print(f"\n📋 动态投资组合管理报告")
        print("="*60)
        
        current_date = datetime.now()
        print(f"📅 报告日期: {current_date.strftime('%Y-%m-%d %H:%M')}")
        
        # 1. 当前组合状态
        print(f"\n1️⃣ 当前组合状态:")
        strategy_names = list(self.strategies_data.keys())
        total_return = 0
        total_vol = 0
        
        for strategy_name in strategy_names:
            weight = self.strategies_data[strategy_name]['current_weight']
            return_rate = self.strategies_data[strategy_name]['return']
            volatility = self.strategies_data[strategy_name]['volatility']
            
            if weight > 0:
                print(f"   💰 {strategy_name}: {weight:.1%} (预期收益: {return_rate:.1%})")
                total_return += weight * return_rate
                total_vol += weight * volatility  # 简化计算
        
        print(f"\n   📈 组合预期收益: {total_return:.2%}")
        print(f"   📊 组合预估波动: {total_vol:.2%}")
        
        # 2. 近期管理活动
        print(f"\n2️⃣ 近期管理活动:")
        print(f"   🔄 上次优化: {self.last_optimization_date.strftime('%Y-%m-%d') if self.last_optimization_date else '未执行'}")
        print(f"   🎲 上次压力测试: {self.last_stress_test_date.strftime('%Y-%m-%d') if self.last_stress_test_date else '未执行'}")
        print(f"   ⚖️ 再平衡次数: {len(self.rebalance_history)} 次")
        
        # 3. 下次行动计划
        print(f"\n3️⃣ 下次行动计划:")
        if self.last_optimization_date:
            days_to_next_opt = self.optimization_frequency - (current_date - self.last_optimization_date).days
            print(f"   🔄 距离下次优化: {max(0, days_to_next_opt)} 天")
        else:
            print(f"   🔄 建议立即执行优化")
        
        if self.last_stress_test_date:
            days_to_next_stress = self.stress_test_frequency - (current_date - self.last_stress_test_date).days
            print(f"   🎲 距离下次压力测试: {max(0, days_to_next_stress)} 天")
        else:
            print(f"   🎲 建议立即执行压力测试")
    
    def save_management_results(self):
        """保存管理结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dynamic_portfolio_management_{timestamp}.json"
        
        save_data = {
            'system_info': {
                'name': '动态CTA投资组合管理系统',
                'version': '1.0',
                'timestamp': timestamp,
                'parameters': {
                    'rebalance_threshold': self.rebalance_threshold,
                    'optimization_frequency': self.optimization_frequency,
                    'stress_test_frequency': self.stress_test_frequency
                }
            },
            'current_portfolio': {
                strategy: {
                    'current_weight': data['current_weight'],
                    'target_weight': data.get('target_weight', data['current_weight']),
                    'return': data['return'],
                    'sharpe': data['sharpe'],
                    'volatility': data['volatility']
                } for strategy, data in self.strategies_data.items()
            },
            'management_history': {
                'optimizations': self.optimization_history,
                'rebalances': self.rebalance_history,
                'stress_tests': self.stress_test_history
            },
            'last_update_dates': {
                'optimization': self.last_optimization_date.isoformat() if self.last_optimization_date else None,
                'stress_test': self.last_stress_test_date.isoformat() if self.last_stress_test_date else None
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 管理状态已保存: {filename}")
        return filename
    
    def run_comprehensive_management_cycle(self):
        """运行完整管理周期"""
        print(f"\n🤖 启动动态投资组合管理周期")
        print("="*70)
        
        # 1. 季度优化检查
        optimization_executed = self.quarterly_optimization()
        
        # 2. 再平衡检查
        if optimization_executed or self.check_rebalance_needed():
            self.execute_rebalance()
        
        # 3. 压力测试
        self.monte_carlo_stress_test()
        
        # 4. 生成报告
        self.generate_management_report()
        
        # 5. 保存结果
        filename = self.save_management_results()
        
        print(f"\n✅ 动态管理周期完成！")
        return filename

def main():
    """主函数"""
    manager = DynamicPortfolioManager()
    
    print("🚀 开始动态投资组合管理...")
    filename = manager.run_comprehensive_management_cycle()
    
    print(f"\n🎯 管理建议:")
    print("1. 定期运行此系统进行自动化管理")
    print("2. 关注压力测试结果的风险预警")
    print("3. 根据市场变化调整管理参数")
    print(f"4. 查看详细结果: {filename}")

if __name__ == "__main__":
    main()