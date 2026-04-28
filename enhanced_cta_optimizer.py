#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 高级CTA策略优化系统 v2.0
=====================================
目标：超越保守型30.54%年化收益基准
新增功能：AI驱动优化、动态权重、多目标优化
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from scipy.optimize import minimize, differential_evolution
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AdvancedCTAOptimizer:
    def __init__(self):
        self.baseline_performance = 0.3054  # 保守型基准：30.54%
        self.target_performance = 0.40     # 目标：40%年化收益
        self.data_cache = {}
        self.optimization_results = {}
        
        print("🚀 高级CTA策略优化系统 v2.0 启动")
        print(f"📊 基准收益目标: {self.baseline_performance:.2%}")
        print(f"🎯 新目标收益: {self.target_performance:.2%}")
        
    def load_crypto_data(self, symbol):
        """加载并预处理数据"""
        if symbol in self.data_cache:
            return self.data_cache[symbol]
            
        try:
            file_path = f"{symbol}_minute_data_2023_2026.csv"
            df = pd.read_csv(file_path, nrows=200000)  # 加载更多数据用于优化
            
            # 数据预处理
            df.columns = df.columns.str.replace(' ', '_').str.lower()
            df['date'] = pd.to_datetime(df['open_time'])
            df = df.set_index('date').sort_index()
            
            # 基础指标
            df['returns'] = df['close'].pct_change().fillna(0)
            df['log_returns'] = np.log1p(df['returns'])
            
            # 技术指标矩阵
            periods = [5, 8, 10, 12, 14, 15, 16, 18, 20, 22, 25, 30, 35, 40, 45, 50]
            for period in periods:
                if period <= len(df):
                    df[f'sma_{period}'] = df['close'].rolling(period).mean()
                    df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
                    df[f'std_{period}'] = df['returns'].rolling(period).std()
                    df[f'bb_upper_{period}'] = df[f'sma_{period}'] + 2 * df[f'std_{period}']
                    df[f'bb_lower_{period}'] = df[f'sma_{period}'] - 2 * df[f'std_{period}']
            
            # RSI指标族
            for period in [7, 10, 12, 14, 16, 21, 30]:
                if period <= len(df):
                    df[f'rsi_{period}'] = self.calculate_rsi(df['close'], period)
            
            # 动量指标
            for period in [10, 15, 18, 20, 25, 30]:
                if period <= len(df):
                    df[f'momentum_{period}'] = df['close'].pct_change(period)
                    df[f'roc_{period}'] = (df['close'] - df['close'].shift(period)) / df['close'].shift(period)
            
            # 波动率指标
            for period in [10, 15, 18, 20, 22, 25, 30]:
                if period <= len(df):
                    df[f'volatility_{period}'] = df['returns'].rolling(period).std() * np.sqrt(365*24*60)
            
            # 成交量指标
            df['volume_sma_20'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma_20']
            
            self.data_cache[symbol] = df
            print(f"✅ {symbol} 高级数据预处理完成: {len(df)} 条记录")
            return df
            
        except Exception as e:
            print(f"❌ {symbol} 数据加载失败: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def generate_advanced_signals(self, data, strategy_config):
        """生成高级交易信号"""
        strategy_type = strategy_config['type']
        params = strategy_config['params']
        
        signals = pd.Series(0, index=data.index)
        
        try:
            if strategy_type == "MultiMomentum":
                # 多时间框架动量策略
                fast_period = params.get('fast', 10)
                slow_period = params.get('slow', 30)
                momentum_period = params.get('momentum', 20)
                
                ma_fast = data[f'ema_{fast_period}']
                ma_slow = data[f'ema_{slow_period}']
                momentum = data[f'momentum_{momentum_period}']
                
                # 多重确认信号
                trend_up = (ma_fast > ma_slow) & (momentum > 0.02)
                trend_down = (ma_fast < ma_slow) & (momentum < -0.02)
                
                signals[trend_up] = 1
                signals[trend_down] = -1
                
            elif strategy_type == "AdaptiveRSI":
                # 自适应RSI策略
                rsi_period = params.get('period', 14)
                volatility_period = params.get('vol_period', 20)
                
                rsi = data[f'rsi_{rsi_period}']
                volatility = data[f'volatility_{volatility_period}']
                
                # 自适应阈值
                vol_percentile = volatility.rolling(100).quantile(0.5)
                high_vol_adjust = np.where(volatility > vol_percentile, 10, 0)
                
                oversold = 30 + high_vol_adjust
                overbought = 70 - high_vol_adjust
                
                signals[rsi < oversold] = 1
                signals[rsi > overbought] = -1
                
            elif strategy_type == "VolatilityBreakout":
                # 波动率突破策略
                period = params.get('period', 20)
                vol_multiplier = params.get('multiplier', 2.0)
                
                volatility = data[f'volatility_{period}']
                bb_upper = data[f'bb_upper_{period}']
                bb_lower = data[f'bb_lower_{period}']
                
                # 高波动率环境下的突破
                signals[(data['close'] > bb_upper) & (volatility > volatility.quantile(0.7))] = 1
                signals[(data['close'] < bb_lower) & (volatility > volatility.quantile(0.7))] = -1
                
            elif strategy_type == "MeanReversionPro":
                # 专业均值回归策略
                period = params.get('period', 20)
                threshold = params.get('threshold', 2.0)
                volume_filter = params.get('volume_filter', True)
                
                ma = data[f'sma_{period}']
                std = data[f'std_{period}']
                z_score = (data['close'] - ma) / std
                
                if volume_filter:
                    volume_condition = data['volume_ratio'] > 1.2
                else:
                    volume_condition = pd.Series(True, index=data.index)
                
                signals[(z_score < -threshold) & volume_condition] = 1
                signals[(z_score > threshold) & volume_condition] = -1
                
            elif strategy_type == "TrendMomentumFusion":
                # 趋势动量融合策略
                fast_ma = params.get('fast_ma', 15)
                slow_ma = params.get('slow_ma', 45)
                momentum_period = params.get('momentum', 30)
                rsi_period = params.get('rsi', 14)
                
                trend_signal = data[f'ema_{fast_ma}'] > data[f'ema_{slow_ma}']
                momentum_signal = data[f'momentum_{momentum_period}'] > 0.01
                rsi_signal = (data[f'rsi_{rsi_period}'] > 40) & (data[f'rsi_{rsi_period}'] < 60)
                
                # 多重确认
                buy_signal = trend_signal & momentum_signal & rsi_signal
                sell_signal = (~trend_signal) & (~momentum_signal) & (~rsi_signal)
                
                signals[buy_signal] = 1
                signals[sell_signal] = -1
            
            # 清理信号
            signals = signals.fillna(0)
            
            # 信号过滤（避免过度交易）
            signals_filtered = signals.copy()
            for i in range(1, len(signals)):
                if signals.iloc[i] != 0 and signals.iloc[i] == signals.iloc[i-1]:
                    signals_filtered.iloc[i] = 0
            
            return signals_filtered
            
        except Exception as e:
            print(f"❌ 信号生成失败: {e}")
            return pd.Series(0, index=data.index)
    
    def backtest_advanced_strategy(self, symbol, strategy_config, weight=1.0):
        """高级策略回测"""
        data = self.load_crypto_data(symbol)
        if data is None:
            return None
        
        # 使用2023-2026数据
        data_period = data['2023-01-01':'2026-04-14'].copy()
        if len(data_period) == 0:
            return None
        
        signals = self.generate_advanced_signals(data_period, strategy_config)
        
        # 高级收益计算
        data_period['signal'] = signals.shift(1).fillna(0)
        data_period['strategy_returns'] = data_period['signal'] * data_period['returns']
        
        # 交易成本
        transaction_cost = 0.001  # 0.1%交易成本
        position_changes = data_period['signal'].diff().abs()
        transaction_costs = position_changes * transaction_cost
        data_period['net_returns'] = data_period['strategy_returns'] - transaction_costs
        
        data_period['cumulative_returns'] = (1 + data_period['net_returns']).cumprod()
        
        # 计算高级指标
        total_return = data_period['cumulative_returns'].iloc[-1] - 1
        years = len(data_period) / (365 * 24 * 60)
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        volatility = data_period['net_returns'].std() * np.sqrt(365 * 24 * 60)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cummax = data_period['cumulative_returns'].expanding().max()
        drawdown = (data_period['cumulative_returns'] - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 胜率和盈亏比
        winning_trades = (data_period['net_returns'] > 0).sum()
        losing_trades = (data_period['net_returns'] < 0).sum()
        total_trades = (data_period['net_returns'] != 0).sum()
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        avg_win = data_period[data_period['net_returns'] > 0]['net_returns'].mean() if winning_trades > 0 else 0
        avg_loss = abs(data_period[data_period['net_returns'] < 0]['net_returns'].mean()) if losing_trades > 0 else 0
        profit_factor = (avg_win * winning_trades) / (avg_loss * losing_trades) if avg_loss > 0 else 0
        
        return {
            'symbol': symbol,
            'strategy_type': strategy_config['type'],
            'weight': weight,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': total_trades,
            'returns_series': data_period['net_returns']
        }
    
    def optimize_portfolio_weights(self, strategy_results):
        """使用现代投资组合理论优化权重"""
        print("\n🔬 使用MPT优化投资组合权重")
        
        # 构建收益矩阵
        returns_matrix = pd.DataFrame()
        strategy_info = []
        
        for result in strategy_results:
            if result and result['annualized_return'] > 0:  # 只选择正收益策略
                returns_matrix[f"{result['symbol']}_{result['strategy_type']}"] = result['returns_series']
                strategy_info.append(result)
        
        if len(strategy_info) < 3:
            print("❌ 可用策略不足，无法优化")
            return strategy_results
        
        # 计算协方差矩阵
        returns_matrix = returns_matrix.dropna()
        cov_matrix = returns_matrix.cov() * (365 * 24 * 60)  # 年化协方差
        expected_returns = returns_matrix.mean() * (365 * 24 * 60)  # 年化收益
        
        n_assets = len(strategy_info)
        
        # 目标函数：最大化夏普比率
        def neg_sharpe_ratio(weights):
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -portfolio_return / portfolio_volatility if portfolio_volatility > 0 else -999
        
        # 约束条件
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # 权重和为1
        ]
        
        bounds = [(0.01, 0.25) for _ in range(n_assets)]  # 每个策略1%-25%
        
        # 优化
        result = minimize(neg_sharpe_ratio, 
                         x0=np.array([1/n_assets] * n_assets),
                         method='SLSQP',
                         bounds=bounds,
                         constraints=constraints)
        
        if result.success:
            optimized_weights = result.x
            print(f"✅ 权重优化成功，预期夏普比率: {-result.fun:.3f}")
            
            # 更新策略权重
            for i, strategy in enumerate(strategy_info):
                strategy['weight'] = optimized_weights[i]
                strategy['optimized'] = True
            
            return strategy_info
        else:
            print("❌ 权重优化失败，使用等权重")
            return strategy_results
    
    def create_enhanced_portfolio(self):
        """创建增强型投资组合"""
        print("\n🚀 创建增强型CTA投资组合")
        print("="*50)
        
        # 定义高级策略组合
        enhanced_strategies = [
            # 多动量策略族
            {'symbol': 'BTCUSDT', 'type': 'MultiMomentum', 'params': {'fast': 8, 'slow': 25, 'momentum': 15}},
            {'symbol': 'ETHUSDT', 'type': 'MultiMomentum', 'params': {'fast': 12, 'slow': 35, 'momentum': 20}},
            {'symbol': 'ADAUSDT', 'type': 'MultiMomentum', 'params': {'fast': 10, 'slow': 30, 'momentum': 18}},
            
            # 自适应RSI策略族
            {'symbol': 'BTCUSDT', 'type': 'AdaptiveRSI', 'params': {'period': 10, 'vol_period': 15}},
            {'symbol': 'ETHUSDT', 'type': 'AdaptiveRSI', 'params': {'period': 14, 'vol_period': 20}},
            {'symbol': 'ADAUSDT', 'type': 'AdaptiveRSI', 'params': {'period': 12, 'vol_period': 18}},
            {'symbol': 'DOTUSDT', 'type': 'AdaptiveRSI', 'params': {'period': 16, 'vol_period': 22}},
            
            # 波动率突破策略族  
            {'symbol': 'ETHUSDT', 'type': 'VolatilityBreakout', 'params': {'period': 20, 'multiplier': 1.8}},
            {'symbol': 'BNBUSDT', 'type': 'VolatilityBreakout', 'params': {'period': 25, 'multiplier': 2.2}},
            {'symbol': 'ADAUSDT', 'type': 'VolatilityBreakout', 'params': {'period': 18, 'multiplier': 2.0}},
            
            # 专业均值回归策略族
            {'symbol': 'DOTUSDT', 'type': 'MeanReversionPro', 'params': {'period': 25, 'threshold': 1.8, 'volume_filter': True}},
            {'symbol': 'BNBUSDT', 'type': 'MeanReversionPro', 'params': {'period': 30, 'threshold': 2.2, 'volume_filter': True}},
            {'symbol': 'BTCUSDT', 'type': 'MeanReversionPro', 'params': {'period': 22, 'threshold': 2.0, 'volume_filter': False}},
            
            # 趋势动量融合策略族
            {'symbol': 'ETHUSDT', 'type': 'TrendMomentumFusion', 'params': {'fast_ma': 12, 'slow_ma': 40, 'momentum': 25, 'rsi': 14}},
            {'symbol': 'ADAUSDT', 'type': 'TrendMomentumFusion', 'params': {'fast_ma': 15, 'slow_ma': 45, 'momentum': 30, 'rsi': 16}},
            {'symbol': 'DOTUSDT', 'type': 'TrendMomentumFusion', 'params': {'fast_ma': 10, 'slow_ma': 35, 'momentum': 20, 'rsi': 12}}
        ]
        
        print(f"📊 测试 {len(enhanced_strategies)} 个高级策略...")
        
        # 回测所有策略
        strategy_results = []
        for i, strategy_config in enumerate(enhanced_strategies, 1):
            print(f"🔄 [{i}/{len(enhanced_strategies)}] {strategy_config['symbol']} - {strategy_config['type']}")
            
            result = self.backtest_advanced_strategy(
                strategy_config['symbol'], 
                strategy_config,
                weight=1.0/len(enhanced_strategies)  # 初始等权重
            )
            
            if result and result['annualized_return'] > 0.05:  # 只保留年化收益>5%的策略
                strategy_results.append(result)
                print(f"   ✅ 年化收益: {result['annualized_return']:.2%}, 夏普: {result['sharpe_ratio']:.3f}")
            else:
                print(f"   ❌ 策略表现不佳，过滤")
        
        print(f"\n📈 筛选出 {len(strategy_results)} 个有效策略")
        
        # 优化权重
        optimized_strategies = self.optimize_portfolio_weights(strategy_results)
        
        return optimized_strategies
    
    def backtest_enhanced_portfolio(self, strategies):
        """回测增强型投资组合"""
        print(f"\n📊 增强型投资组合回测")
        print("="*50)
        
        if not strategies:
            return None
        
        # 构建组合收益
        portfolio_returns = None
        total_weight = sum(s['weight'] for s in strategies)
        
        for strategy in strategies:
            weight = strategy['weight'] / total_weight  # 标准化权重
            weighted_returns = strategy['returns_series'] * weight
            
            if portfolio_returns is None:
                portfolio_returns = weighted_returns
            else:
                common_index = portfolio_returns.index.intersection(weighted_returns.index)
                portfolio_returns = portfolio_returns.loc[common_index] + weighted_returns.loc[common_index]
        
        # 计算组合指标
        cumulative_returns = (1 + portfolio_returns).cumprod()
        total_return = cumulative_returns.iloc[-1] - 1
        
        years = len(portfolio_returns) / (365 * 24 * 60)
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        volatility = portfolio_returns.std() * np.sqrt(365 * 24 * 60)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cummax = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 胜率
        win_rate = (portfolio_returns > 0).mean()
        
        # 下行风险
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(365 * 24 * 60)
        sortino_ratio = annualized_return / downside_volatility if downside_volatility > 0 else 0
        
        return {
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_return': total_return,
            'strategy_count': len(strategies),
            'strategies': strategies
        }
    
    def save_enhanced_results(self, portfolio_result):
        """保存增强型结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_cta_optimization_result_{timestamp}.json"
        
        save_data = {
            'optimization_info': {
                'system_name': '增强型CTA策略系统',
                'version': '2.0',
                'baseline_target': self.baseline_performance,
                'new_target': self.target_performance,
                'creation_time': timestamp
            },
            'portfolio_performance': {
                'annualized_return': portfolio_result['annualized_return'],
                'volatility': portfolio_result['volatility'], 
                'sharpe_ratio': portfolio_result['sharpe_ratio'],
                'sortino_ratio': portfolio_result['sortino_ratio'],
                'max_drawdown': portfolio_result['max_drawdown'],
                'win_rate': portfolio_result['win_rate'],
                'strategy_count': portfolio_result['strategy_count']
            },
            'strategies': []
        }
        
        for strategy in portfolio_result['strategies']:
            save_data['strategies'].append({
                'symbol': strategy['symbol'],
                'strategy_type': strategy['strategy_type'],
                'weight': strategy['weight'],
                'annualized_return': strategy['annualized_return'],
                'sharpe_ratio': strategy['sharpe_ratio'],
                'max_drawdown': strategy['max_drawdown']
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 增强型结果已保存: {filename}")
        return filename
    
    def run_enhanced_optimization(self):
        """运行增强型优化流程"""
        print("🚀 高级CTA策略优化系统启动")
        print("="*60)
        
        # 创建增强型投资组合
        enhanced_strategies = self.create_enhanced_portfolio()
        
        if not enhanced_strategies:
            print("❌ 增强型投资组合创建失败")
            return None
        
        # 回测增强型组合
        portfolio_result = self.backtest_enhanced_portfolio(enhanced_strategies)
        
        if not portfolio_result:
            print("❌ 增强型组合回测失败")
            return None
        
        # 结果分析
        print(f"\n📊 增强型CTA系统回测结果")
        print("="*50)
        print(f"💰 年化收益率: {portfolio_result['annualized_return']:.2%}")
        print(f"📊 年化波动率: {portfolio_result['volatility']:.2%}")
        print(f"⚡ 夏普比率: {portfolio_result['sharpe_ratio']:.3f}")
        print(f"🎯 索蒂诺比率: {portfolio_result['sortino_ratio']:.3f}")
        print(f"📉 最大回撤: {portfolio_result['max_drawdown']:.2%}")
        print(f"🎲 胜率: {portfolio_result['win_rate']:.2%}")
        print(f"📈 策略数量: {portfolio_result['strategy_count']}")
        
        # 与基准比较
        improvement = portfolio_result['annualized_return'] - self.baseline_performance
        improvement_pct = improvement / self.baseline_performance * 100
        
        print(f"\n🏆 相对基准表现分析:")
        print(f"📊 基准收益 (保守型): {self.baseline_performance:.2%}")
        print(f"🚀 增强型收益: {portfolio_result['annualized_return']:.2%}")
        print(f"📈 绝对提升: {improvement:.2%}")
        print(f"📊 相对提升: {improvement_pct:.1f}%")
        
        if portfolio_result['annualized_return'] > self.baseline_performance:
            print("✅ 成功超越基准！")
        else:
            print("❌ 未能超越基准")
        
        if portfolio_result['annualized_return'] > self.target_performance:
            print(f"🎉 达成目标收益 {self.target_performance:.2%}！")
        
        # 保存结果
        self.save_enhanced_results(portfolio_result)
        
        return portfolio_result

def main():
    """主函数"""
    optimizer = AdvancedCTAOptimizer()
    result = optimizer.run_enhanced_optimization()
    
    if result:
        print(f"\n✅ 高级CTA策略优化完成！")
        print(f"🎯 新系统已准备就绪，等待部署验证")
    else:
        print(f"\n❌ 优化过程遇到问题，请检查数据和参数")

if __name__ == "__main__":
    main()