#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📈 高效动态CTA投资组合管理系统 2023-2026 历史回测
================================================
优化版本：减少计算量，提高回测效率
包含：定期重新优化、动态再平衡、压力测试
"""

import pandas as pd 
import numpy as np
import json
from datetime import datetime, timedelta
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class EfficientDynamicBacktest:
    def __init__(self):
        print("📈 高效动态CTA投资组合管理系统 2023-2026 历史回测")
        print("="*70)
        
        # 策略配置
        self.strategies_config = {
            'BTCUSDT_FixedBreakout': {'symbol': 'BTCUSDT', 'weight': 0.2},
            'ETHUSDT_FixedBreakout': {'symbol': 'ETHUSDT', 'weight': 0.8}
        }
        
        # 管理参数
        self.rebalance_threshold = 0.05  # 5%
        self.optimization_frequency = 7   # 7天（每周）
        self.stress_test_frequency = 30   # 30天
        self.transaction_cost = 0.0005    # 0.05%
        
        # 回测参数
        self.start_date = '2023-01-01'
        self.end_date = '2026-04-14'
        self.initial_capital = 100000
        
        # 预加载所有数据
        self.preload_all_data()
        
        # 记录历史
        self.portfolio_history = []
        self.rebalance_history = []
        self.optimization_history = []
        self.stress_test_history = []
        
        print(f"📊 回测期间: {self.start_date} - {self.end_date}")
        print(f"💰 初始资金: ${self.initial_capital:,}")
        print(f"⚖️ 再平衡阈值: ±{self.rebalance_threshold:.0%}")
    
    def preload_all_data(self):
        """预加载所有策略数据"""
        print(f"\n📂 预加载历史数据...")
        
        self.strategy_data = {}
        
        for strategy_name, config in self.strategies_config.items():
            symbol = config['symbol']
            
            try:
                datafile = f"{symbol}_minute_data_2023_2026.csv"
                print(f"   📈 加载 {datafile}")
                
                df = pd.read_csv(datafile)  # 移除行数限制，加载完整数据
                
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
                
                # 生成突破策略
                df = self.generate_breakout_strategy(df)
                
                # 只保留指定时间段
                df = df[self.start_date:self.end_date]
                
                self.strategy_data[strategy_name] = df
                
                print(f"      ✅ {strategy_name}: {len(df):,} 条记录")
                
            except Exception as e:
                print(f"      ❌ {strategy_name} 加载失败: {e}")
                
        print(f"✅ 数据预加载完成，共 {len(self.strategy_data)} 个策略")
    
    def generate_breakout_strategy(self, df):
        """生成突破策略信号"""
        signals = pd.Series(0, index=df.index)
        
        # 每4小时重采样
        try:
            data_4h = df.resample('4H').last().dropna()
            
            # 突破信号
            breakout_up = (data_4h['close'] > data_4h['bb_upper']) & (data_4h['volume_ratio'] > 1.2)
            breakout_down = (data_4h['close'] < data_4h['bb_lower']) & (data_4h['volume_ratio'] > 1.2)
            
            signals_4h = pd.Series(0, index=data_4h.index)
            signals_4h[breakout_up] = 1
            signals_4h[breakout_down] = -1
            
            # 回采样到分钟级
            signals = signals_4h.reindex(df.index, method='ffill').fillna(0)
            
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
    
    def calculate_strategy_metrics(self, strategy_name, end_date, lookback_days=7):
        """计算策略指标"""
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
        
        if days < 5:  # 至少5天数据（适合每周优化）
            return None
            
        annualized_return = (1 + total_return) ** (365 / days) - 1
        volatility = strategy_returns.std() * np.sqrt(365 * 24 * 60)
        
        return {
            'annualized_return': annualized_return,
            'volatility': max(volatility, 0.001),  # 避免零波动
            'total_return': total_return
        }
    
    def optimize_portfolio_weights(self, current_date):
        """优化投资组合权重"""
        print(f"   🔄 执行权重优化 ({current_date.strftime('%Y-%m-%d')})")
        
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
                
                print(f"      📊 {strategy_name}: 收益{metrics['annualized_return']:.1%}, 波动{metrics['volatility']:.1%}")
        
        if len(valid_strategies) < 2:
            print(f"      ⚠️ 有效策略不足 ({len(valid_strategies)}个)，保持现有权重")
            return None
        
        # 简化的权重优化：基于夏普比率分配
        expected_returns = np.array(expected_returns)
        volatilities = np.array(volatilities)
        
        sharpe_ratios = expected_returns / volatilities
        sharpe_ratios[sharpe_ratios < 0] = 0  # 负夏普设为0
        
        if np.sum(sharpe_ratios) == 0:
            # 如果所有夏普比率都<=0，等权重分配
            weights = np.ones(len(valid_strategies)) / len(valid_strategies)
        else:
            weights = sharpe_ratios / np.sum(sharpe_ratios)
        
        # 构建权重字典
        weight_dict = {}
        for i, strategy_name in enumerate(valid_strategies):
            weight_dict[strategy_name] = weights[i]
        
        # 补充缺失策略权重为0
        for strategy_name in strategy_names:
            if strategy_name not in weight_dict:
                weight_dict[strategy_name] = 0.0
        
        portfolio_return = np.sum(weights * expected_returns)
        portfolio_vol = np.sqrt(np.sum((weights * volatilities) ** 2))
        sharpe = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
        
        print(f"      ✅ 优化完成: 预期收益{portfolio_return:.1%}, 夏普{sharpe:.2f}")
        
        return weight_dict
    
    def calculate_daily_portfolio_return(self, date, weights):
        """计算日投资组合收益"""
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
        """检查再平衡需求"""
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
        """执行再平衡"""
        trades = []
        total_cost = 0
        
        for strategy, target_weight in target_weights.items():
            current_weight = current_weights.get(strategy, 0)
            
            if abs(target_weight - current_weight) > 0.001:  # 最小调整阈值
                trade_amount = (target_weight - current_weight) * portfolio_value
                cost = abs(trade_amount) * self.transaction_cost
                total_cost += cost
                
                trades.append({
                    'strategy': strategy,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'trade_amount': trade_amount,
                    'cost': cost
                })
        
        return trades, total_cost
    
    def run_stress_test(self, current_date, current_weights):
        """运行简化压力测试"""
        try:
            print(f"      🎲 压力测试 ({current_date.strftime('%Y-%m-%d')})")
            
            portfolio_returns = {}
            
            # 计算各策略近期收益
            for strategy_name, weight in current_weights.items():
                if weight > 0 and strategy_name in self.strategy_data:
                    metrics = self.calculate_strategy_metrics(strategy_name, current_date, 30)
                    if metrics:
                        portfolio_returns[strategy_name] = {
                            'return': metrics['annualized_return'],
                            'volatility': metrics['volatility'],
                            'weight': weight
                        }
            
            if not portfolio_returns:
                return None
            
            # 简化的投资组合指标
            portfolio_return = sum(data['return'] * data['weight'] for data in portfolio_returns.values())
            portfolio_vol = np.sqrt(sum((data['volatility'] * data['weight']) ** 2 for data in portfolio_returns.values()))
            
            # 简化的蒙特卡罗模拟（每周优化）
            time_horizon = 7
            num_sim = 1000
            
            daily_return = portfolio_return / 365
            daily_vol = max(portfolio_vol / np.sqrt(365), 0.001)
            
            simulations = np.random.normal(daily_return, daily_vol, (num_sim, time_horizon))
            cumulative_returns = np.prod(1 + simulations, axis=1) - 1
            
            var_95 = np.percentile(cumulative_returns, 5)
            prob_loss = np.mean(cumulative_returns < 0)
            
            risk_level = self.assess_risk_level(var_95, prob_loss)
            
            print(f"         ✅ VaR95: {var_95:.1%}, 亏损概率: {prob_loss:.1%}, {risk_level}")
            
            return {
                'date': current_date.strftime('%Y-%m-%d'),
                'portfolio_return': float(portfolio_return),
                'portfolio_volatility': float(portfolio_vol),
                'var_95': float(var_95),
                'prob_loss': float(prob_loss),
                'risk_level': risk_level
            }
            
        except Exception as e:
            print(f"         ❌ 压力测试失败: {e}")
            return None
    
    def assess_risk_level(self, var_95, prob_loss):
        """评估风险等级"""
        if var_95 > -0.10 and prob_loss < 0.2:
            return "🟢 低风险"
        elif var_95 > -0.25 and prob_loss < 0.4:
            return "🟡 中等风险"
        else:
            return "🔴 高风险"
    
    def run_backtest(self):
        """运行回测"""
        print(f"\n🚀 开始高效回测 ({self.start_date} - {self.end_date})")
        print("="*70)
        
        # 初始化
        current_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        portfolio_value = self.initial_capital
        
        # 初始权重
        current_weights = {name: config['weight'] for name, config in self.strategies_config.items()}
        target_weights = current_weights.copy()
        
        last_optimization = current_date
        last_stress_test = current_date
        
        # 按周回测（提高效率）
        date_range = pd.date_range(start=current_date, end=end_date, freq='7D')
        
        print(f"📅 回测周期: {len(date_range)} 周")
        
        for i, date in enumerate(date_range):
            if i % 4 == 0:  # 每月打印进度
                print(f"📈 回测进度: {i}/{len(date_range)} 周 ({date.strftime('%Y-%m-%d')})")
            
            # 1. 定期优化 (7天，每周)
            if (date - last_optimization).days >= self.optimization_frequency:
                new_weights = self.optimize_portfolio_weights(date)
                if new_weights:
                    old_weights = target_weights.copy()
                    target_weights = new_weights
                    
                    self.optimization_history.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'old_weights': old_weights,
                        'new_weights': target_weights
                    })
                    
                    last_optimization = date
            
            # 2. 再平衡检查
            needs_rebalance, max_deviation = self.check_rebalance_needed(current_weights, target_weights)
            
            if needs_rebalance:
                print(f"      ⚖️ 再平衡: 最大偏离 {max_deviation:.1%}")
                trades, cost = self.execute_rebalance(current_weights, target_weights, portfolio_value)
                
                if trades:
                    portfolio_value -= cost
                    current_weights = target_weights.copy()
                    
                    self.rebalance_history.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'trades': trades,
                        'cost': cost,
                        'max_deviation': max_deviation
                    })
            
            # 3. 计算周收益
            week_return = 0
            week_start = date
            week_end = min(date + timedelta(days=7), end_date)
            
            current_week_dates = pd.date_range(start=week_start, end=week_end, freq='D')
            
            for daily_date in current_week_dates:
                daily_return = self.calculate_daily_portfolio_return(daily_date, current_weights)
                portfolio_value *= (1 + daily_return)
                week_return += daily_return
            
            # 记录周数据
            self.portfolio_history.append({
                'date': date.strftime('%Y-%m-%d'),
                'portfolio_value': portfolio_value,
                'week_return': week_return,
                'weights': current_weights.copy()
            })
            
            # 4. 压力测试 (30天)
            if (date - last_stress_test).days >= self.stress_test_frequency:
                stress_result = self.run_stress_test(date, current_weights)
                if stress_result:
                    self.stress_test_history.append(stress_result)
                last_stress_test = date
        
        print(f"\n✅ 回测完成！")
        self.analyze_performance()
    
    def analyze_performance(self):
        """分析回测表现"""
        print(f"\n📊 回测表现分析")
        print("="*50)
        
        if not self.portfolio_history:
            print("❌ 无历史数据")
            return
        
        # 转换为DataFrame
        df = pd.DataFrame(self.portfolio_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # 基本统计
        initial_value = self.initial_capital
        final_value = df['portfolio_value'].iloc[-1]
        total_return = (final_value / initial_value - 1)
        
        weeks = len(df)
        years = weeks / 52
        annualized_return = (final_value / initial_value) ** (1/years) - 1 if years > 0 else 0
        
        # 波动率（基于周收益）
        week_returns = pd.Series(df['week_return'])
        volatility = week_returns.std() * np.sqrt(52)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        portfolio_values = df['portfolio_value']
        running_max = portfolio_values.expanding().max()
        drawdowns = (portfolio_values - running_max) / running_max
        max_drawdown = drawdowns.min()
        
        # 胜率
        win_rate = (week_returns > 0).mean()
        
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
        
        return {
            'final_value': final_value,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate
        }
    
    def save_results(self):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"efficient_dynamic_backtest_{timestamp}.json"
        
        # 获取性能指标
        performance = self.analyze_performance()
        
        results = {
            'backtest_info': {
                'system': '高效动态CTA投资组合管理系统',
                'period': f"{self.start_date} - {self.end_date}",
                'timestamp': timestamp
            },
            'parameters': {
                'initial_capital': self.initial_capital,
                'rebalance_threshold': self.rebalance_threshold,
                'optimization_frequency': self.optimization_frequency,
                'stress_test_frequency': self.stress_test_frequency
            },
            'performance': performance if performance else {},
            'activities': {
                'optimizations': len(self.optimization_history),
                'rebalances': len(self.rebalance_history), 
                'stress_tests': len(self.stress_test_history)
            },
            'history': {
                'portfolio': self.portfolio_history,
                'optimizations': self.optimization_history,
                'rebalances': self.rebalance_history,
                'stress_tests': self.stress_test_history
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存: {filename}")
        return filename

def main():
    """主函数"""
    backtest = EfficientDynamicBacktest()
    
    try:
        backtest.run_backtest()
        filename = backtest.save_results()
        
        print(f"\n🎉 高效回测完成！")
        print(f"📄 结果文件: {filename}")
        
    except Exception as e:
        print(f"❌ 回测失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()