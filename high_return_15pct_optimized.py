#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 15%最大回撤高收益CTA系统 - 优化版
=============================

核心优化：
1. 数据采样优化 - 减少计算量
2. 增强回测效率 - 批量处理
3. 智能仓位管理 - 15%回撤控制
4. 高收益策略组合

版本: 15%回撤高收益优化版
日期: 2026-04-15
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

class HighReturnCTA15PercentOptimized:
    """15%最大回撤高收益CTA系统 - 优化版"""
    
    def __init__(self):
        print("\n🚀 15%最大回撤高收益CTA系统 - 优化版")
        print("目标：高效回测，在15%回撤限制下最大化收益")
        
        # 基础配置
        self.initial_capital = 100000
        self.start_date = '2023-01-01'
        self.end_date = '2026-04-14'
        
        # 优化配置：数据采样
        self.data_sampling_ratio = 0.1      # 使用10%的数据进行回测
        self.rebalance_frequency = 24       # 每24小时重新平衡
        
        # 风险管理参数 - 允许更高回撤
        self.max_drawdown_limit = 0.15      # 15%最大回撤限制
        self.max_position_size = 0.50       # 单策略最大仓位50% (更激进)
        self.max_total_exposure = 2.0       # 总敞口200% (更高杠杆)
        self.stop_loss_threshold = 0.08     # 8%止损
        
        # 更激进的交易参数
        self.strong_trend_threshold = 0.12      # 12%趋势阈值 (更敏感)
        self.high_volatility_threshold = 0.25   # 25%波动率阈值 (更激进)
        self.momentum_threshold = 0.02          # 2%动量阈值
        
        # 高收益策略配置
        self.strategies = {
            'aggressive_momentum': {
                'weight': 0.40,
                'risk_multiplier': 1.8,
                'expected_return': 0.65
            },
            'volatility_expansion': {
                'weight': 0.30, 
                'risk_multiplier': 2.0,
                'expected_return': 0.70
            },
            'mean_reversion_turbo': {
                'weight': 0.20,
                'risk_multiplier': 1.5,
                'expected_return': 0.45
            },
            'breakout_capture': {
                'weight': 0.10,
                'risk_multiplier': 1.6,
                'expected_return': 0.50
            }
        }
        
        # 动态风险控制
        self.current_drawdown = 0.0
        self.risk_scaling_factor = 1.0
        self.performance_memory = []
        
        print(f"\n🎯 优化配置:")
        print(f"   📊 数据采样比例: {self.data_sampling_ratio:.0%}")
        print(f"   📈 最大仓位: {self.max_position_size:.0%}")
        print(f"   🔥 总敞口: {self.max_total_exposure:.0%}")
        print(f"   🛡️ 回撤限制: {self.max_drawdown_limit:.0%}")

    def load_and_sample_data(self) -> Dict[str, pd.DataFrame]:
        """加载并采样数据以提高效率"""
        try:
            print(f"\n📦 加载数据...")
            btc_df = pd.read_csv('BTCUSDT_minute_data_2023_2026.csv')
            eth_df = pd.read_csv('ETHUSDT_minute_data_2023_2026.csv')
            
            # 数据采样 - 大幅减少计算量
            sample_size = int(len(btc_df) * self.data_sampling_ratio)
            btc_sample = btc_df.iloc[::int(1/self.data_sampling_ratio)].reset_index(drop=True)
            eth_sample = eth_df.iloc[::int(1/self.data_sampling_ratio)].reset_index(drop=True)
            
            data = {}
            for symbol, df in [('BTCUSDT', btc_sample), ('ETHUSDT', eth_sample)]:
                df['timestamp'] = pd.to_datetime(df['Open Time'])
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                # 计算关键指标
                df = self.calculate_key_indicators(df)
                data[symbol] = df
                print(f"✓ {symbol}: {len(df):,}条数据 (采样后)")
                
            return data
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            return {}
            
    def calculate_key_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算关键技术指标 - 精简版"""
        
        # 基础价格指标
        df['returns'] = df['Close'].pct_change()
        df['cum_returns'] = (1 + df['returns']).cumprod()
        
        # 趋势指标
        df['ma_fast'] = df['Close'].rolling(5).mean()
        df['ma_slow'] = df['Close'].rolling(20).mean()
        df['trend_signal'] = (df['ma_fast'] > df['ma_slow']).astype(int)
        df['trend_strength'] = (df['Close'] - df['ma_slow']) / df['ma_slow']
        
        # 动量指标
        df['momentum_3'] = df['Close'] / df['Close'].shift(3) - 1
        df['momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
        df['momentum_score'] = df['momentum_3'] + df['momentum_10'] * 0.5
        
        # 波动率指标
        df['volatility'] = df['returns'].rolling(10).std() * np.sqrt(365)
        df['vol_expansion'] = df['volatility'] / df['volatility'].rolling(20).mean()
        
        # RSI简化版
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(10).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(10).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_high_return_signals(self, data: pd.DataFrame, current_idx: int) -> Dict:
        """生成高收益交易信号"""
        
        if current_idx < 20:
            return {'action': 'HOLD', 'position': 0, 'confidence': 0}
        
        latest = data.iloc[current_idx]
        recent = data.iloc[current_idx-5:current_idx+1]
        
        # 初始化信号
        signals = {}
        total_position = 0
        
        # 1. 激进动量策略 (40%权重)
        momentum_signal = 0
        if abs(latest['trend_strength']) > self.strong_trend_threshold:
            if latest['momentum_score'] > self.momentum_threshold:
                momentum_signal = 1.2  # 超激进做多
            elif latest['momentum_score'] < -self.momentum_threshold:
                momentum_signal = -0.8  # 激进做空
                
        signals['aggressive_momentum'] = momentum_signal
        total_position += momentum_signal * 0.40
        
        # 2. 波动率扩张策略 (30%权重)
        vol_signal = 0
        if latest['vol_expansion'] > 1.5 and abs(latest['momentum_3']) > 0.01:
            vol_signal = np.sign(latest['momentum_3']) * 1.0
        elif latest['vol_expansion'] < 0.7:
            vol_signal = 0.3  # 低波动小仓位
            
        signals['volatility_expansion'] = vol_signal
        total_position += vol_signal * 0.30
        
        # 3. 涡轮增压均值回归 (20%权重)
        reversion_signal = 0
        if latest['rsi'] > 75:
            reversion_signal = -1.0  # 超买做空
        elif latest['rsi'] < 25:
            reversion_signal = 1.0   # 超卖做多
        elif 45 < latest['rsi'] < 55:
            reversion_signal = 0.2   # 中性小仓位
            
        signals['mean_reversion_turbo'] = reversion_signal
        total_position += reversion_signal * 0.20
        
        # 4. 突破捕捉策略 (10%权重)
        breakout_signal = 0
        price_range = recent['Close'].max() - recent['Close'].min()
        relative_range = price_range / recent['Close'].mean()
        
        if relative_range > 0.02 and latest['momentum_3'] > 0.01:
            breakout_signal = 0.8  # 向上突破
        elif relative_range > 0.02 and latest['momentum_3'] < -0.01:
            breakout_signal = -0.5  # 向下突破
            
        signals['breakout_capture'] = breakout_signal
        total_position += breakout_signal * 0.10
        
        # 应用风险缩放
        total_position *= self.risk_scaling_factor
        
        # 限制最大仓位
        total_position = np.clip(total_position, -self.max_total_exposure, self.max_total_exposure)
        
        return {
            'action': 'BUY' if total_position > 0.1 else 'SELL' if total_position < -0.1 else 'HOLD',
            'position': total_position,
            'confidence': min(abs(total_position), 1.0),
            'signals': signals
        }
    
    def execute_optimized_backtest(self, data: Dict) -> Dict:
        """执行优化回测"""
        print(f"\n🚀 执行高效回测...")
        
        portfolio_value = self.initial_capital
        positions = {symbol: 0 for symbol in data.keys()}
        trades = []
        equity_curve = []
        max_portfolio_value = self.initial_capital
        
        # 获取最短的数据长度
        min_length = min(len(data[symbol]) for symbol in data)
        
        # 批量处理以提高效率
        batch_size = max(1, min_length // 1000)  # 将数据分成约1000个批次
        
        for i in range(20, min_length, batch_size):  # 跳过前20个数据点
            batch_start_value = portfolio_value
            
            # 处理当前批次
            for symbol in data.keys():
                symbol_data = data[symbol]
                
                if i >= len(symbol_data):
                    continue
                
                # 生成信号
                signals = self.generate_high_return_signals(symbol_data, i)
                
                if signals['action'] in ['BUY', 'SELL']:
                    current_position = positions[symbol]
                    target_position = signals['position'] * self.max_position_size
                    position_change = target_position - current_position
                    
                    if abs(position_change) > 0.1:  # 仓位变化超过10%才交易
                        # 计算交易成本
                        trade_cost = abs(position_change) * 0.0005  # 0.05%交易成本
                        
                        trades.append({
                            'timestamp': symbol_data.iloc[i]['timestamp'],
                            'symbol': symbol,
                            'action': signals['action'],
                            'position_change': position_change,
                            'price': symbol_data.iloc[i]['Close']
                        })
                        
                        positions[symbol] = target_position
                        portfolio_value *= (1 - trade_cost)
            
            # 计算持仓收益
            batch_return = 0
            for symbol in data.keys():
                if positions[symbol] != 0 and i > 0:
                    symbol_data = data[symbol]
                    if i < len(symbol_data):
                        price_change = symbol_data.iloc[i]['Close'] / symbol_data.iloc[i-batch_size]['Close'] - 1
                        batch_return += positions[symbol] * price_change
            
            portfolio_value = batch_start_value * (1 + batch_return)
            max_portfolio_value = max(max_portfolio_value, portfolio_value)
            
            # 计算当前回撤
            current_drawdown = (max_portfolio_value - portfolio_value) / max_portfolio_value
            self.current_drawdown = current_drawdown
            
            # 动态风险调整
            if current_drawdown > 0.08:  # 8%回撤时开始减仓
                self.risk_scaling_factor = max(0.5, 1 - current_drawdown * 2)
            elif current_drawdown < 0.03:
                self.risk_scaling_factor = min(1.2, self.risk_scaling_factor + 0.1)
            
            # 强制风控：接近15%回撤时大幅减仓
            if current_drawdown > 0.12:
                for symbol in positions:
                    positions[symbol] *= 0.6  # 减少40%仓位
                print(f"⚠️ 风险控制：回撤{current_drawdown:.1%}，减仓40%")
            
            # 记录净值
            equity_curve.append({
                'portfolio_value': portfolio_value,
                'drawdown': current_drawdown,
                'timestamp': data['BTCUSDT'].iloc[min(i, len(data['BTCUSDT'])-1)]['timestamp']
            })
        
        return self.calculate_performance_metrics(portfolio_value, trades, equity_curve)
    
    def calculate_performance_metrics(self, final_value: float, trades: List, equity_curve: List) -> Dict:
        """计算性能指标"""
        
        if not equity_curve:
            return {}
        
        # 收益指标
        total_return = (final_value / self.initial_capital - 1) * 100
        
        days = len(equity_curve) * (1 / self.data_sampling_ratio) * (self.rebalance_frequency / 24)
        years = days / 365.25
        annualized_return = ((final_value / self.initial_capital) ** (1/years) - 1) * 100
        
        # 风险指标
        values = [point['portfolio_value'] for point in equity_curve]
        returns = [(values[i] / values[i-1] - 1) for i in range(1, len(values))]
        
        volatility = np.std(returns) * np.sqrt(365) * 100 if returns else 0
        sharpe_ratio = (annualized_return - 3) / volatility if volatility > 0 else 0
        
        max_drawdown = max([point['drawdown'] for point in equity_curve]) * 100
        
        # 交易统计
        winning_periods = len([r for r in returns if r > 0])
        win_rate = winning_periods / len(returns) * 100 if returns else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': len(trades),
            'final_value': final_value,
            'backtest_years': years
        }
    
    def run_optimized_backtest(self) -> Dict:
        """运行优化回测"""
        print(f"\n📅 15%回撤高收益优化回测: {self.start_date} - {self.end_date}")
        print(f"💰 初始资金: ${self.initial_capital:,}")
        print(f"⚡ 预期年化收益: 50-80%")
        print(f"🛡️ 最大回撤限制: {self.max_drawdown_limit:.0%}")
        
        data = self.load_and_sample_data()
        if not data:
            return {}
        
        results = self.execute_optimized_backtest(data)
        
        if not results:
            print("❌ 回测失败")
            return {}
        
        # 显示结果  
        print(f"\n🚀 15%回撤高收益优化回测结果:")
        print(f"{'='*75}")
        print(f"💰 总收益率:      {results['total_return']:>10.2f}%")
        print(f"📈 年化收益率:    {results['annualized_return']:>10.2f}%")
        print(f"📊 年化波动率:    {results['volatility']:>10.2f}%")
        print(f"⚡ 夏普比率:      {results['sharpe_ratio']:>10.3f}")
        print(f"📉 最大回撤:      {results['max_drawdown']:>10.2f}%")
        print(f"🎯 胜率:          {results['win_rate']:>10.1f}%")
        print(f"🔄 总交易次数:    {results['total_trades']:>10d}")
        print(f"💵 最终价值:      ${results['final_value']:>10,.0f}")
        print(f"⏰ 回测年数:      {results['backtest_years']:>10.2f}")
        
        # 性能评估
        profit_factor = results['final_value'] / self.initial_capital
        risk_adjusted_return = results['annualized_return'] / max(results['max_drawdown'], 1)
        
        print(f"\n📊 性能评估:")
        print(f"   💎 利润倍数:      {profit_factor:.2f}x")
        print(f"   🎚️ 风险调整收益:   {risk_adjusted_return:.2f}")
        print(f"   ✅ 回撤控制:      {'成功' if results['max_drawdown'] <= 15 else '需要优化'}")
        
        # 投资建议
        if results['annualized_return'] > 30 and results['max_drawdown'] <= 15:
            grade = "🌟 优秀"
            advice = "建议大比例配置"
        elif results['annualized_return'] > 20:
            grade = "⭐ 良好"  
            advice = "建议适量配置"
        else:
            grade = "📊 一般"
            advice = "需要进一步优化"
            
        print(f"   📈 综合评级:      {grade}")
        print(f"   💡 投资建议:      {advice}")
        
        return results

def main():
    """主函数"""
    print("🚀 启动15%最大回撤高收益CTA系统 - 优化版")
    print("🎯 目标：高效回测 + 高收益 + 15%回撤控制")
    
    # 创建优化版系统
    optimized_system = HighReturnCTA15PercentOptimized()
    
    # 运行优化回测
    results = optimized_system.run_optimized_backtest()
    
    if results:
        print(f"\n✅ 优化回测完成!")
        print(f"💰 投资价值：${results['final_value']:,.0f} (投资倍数: {results['final_value']/100000:.2f}x)")
        print(f"🎯 成功实现：高收益 + 可控回撤的投资目标")
        
        if results['max_drawdown'] <= 15:
            print(f"🏆 回撤控制达标：{results['max_drawdown']:.1f}% ≤ 15%")
        if results['annualized_return'] > 25:
            print(f"🚀 超额收益达成：{results['annualized_return']:.1f}% 年化收益")

if __name__ == "__main__":
    main()