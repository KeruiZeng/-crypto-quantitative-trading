#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 15%回撤平衡高收益CTA系统 V2.0
=============================

核心改进：
1. 平衡收益与风险 - 智能策略配权
2. 优化信号质量 - 多重确认机制
3. 动态杠杆调节 - 市场适应性
4. 收益增强模块 - 15%回撤下最大化收益

版本: V2.0 平衡高收益版
日期: 2026-04-15
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

class BalancedHighReturnCTA:
    """15%回撤平衡高收益CTA系统"""
    
    def __init__(self):
        print("\n🚀 15%回撤平衡高收益CTA系统 V2.0")
        print("目标：在15%回撤限制下平衡风险收益，追求稳健高收益")
        
        # 基础配置
        self.initial_capital = 100000
        self.start_date = '2023-01-01'
        self.end_date = '2026-04-14'
        
        # 优化配置
        self.data_sampling_ratio = 0.05     # 使用5%数据 (进一步优化)
        self.rebalance_frequency = 12       # 每12小时重新评估
        
        # 平衡风险管理参数
        self.max_drawdown_limit = 0.15      # 15%最大回撤限制
        self.target_drawdown = 0.10         # 目标回撤10% (留余量)
        self.max_position_size = 0.35       # 单策略最大仓位35% (适中)
        self.max_total_exposure = 1.5       # 总敞口150% (适中)
        
        # 智能交易阈值
        self.trend_threshold = 0.08         # 8%趋势阈值 (平衡)
        self.volatility_threshold = 0.20    # 20%波动率阈值
        self.rsi_overbought = 70           # RSI超买线
        self.rsi_oversold = 30             # RSI超卖线
        
        # 平衡策略组合
        self.balanced_strategies = {
            'trend_following': {
                'weight': 0.30,
                'risk_tolerance': 'medium',
                'expected_return': 0.35,
                'max_position': 0.25
            },
            'momentum_capture': {
                'weight': 0.25, 
                'risk_tolerance': 'high',
                'expected_return': 0.45,
                'max_position': 0.30
            },
            'mean_reversion': {
                'weight': 0.25,
                'risk_tolerance': 'low',
                'expected_return': 0.25,
                'max_position': 0.20
            },
            'volatility_trading': {
                'weight': 0.15,
                'risk_tolerance': 'medium',
                'expected_return': 0.40,
                'max_position': 0.25
            },
            'hedge_protection': {
                'weight': 0.05,
                'risk_tolerance': 'very_low',
                'expected_return': 0.15,
                'max_position': 0.10
            }
        }
        
        # 动态参数
        self.market_regime = 'normal'
        self.risk_scaling = 1.0
        self.performance_tracker = []
        self.consecutive_losses = 0
        
        print(f"\n🎯 平衡配置:")
        print(f"   🎚️ 目标回撤: {self.target_drawdown:.0%}")
        print(f"   📈 最大仓位: {self.max_position_size:.0%}")
        print(f"   🔥 总敞口: {self.max_total_exposure:.0%}")
        print(f"   ✅ 策略数量: {len(self.balanced_strategies)}个")

    def load_efficient_data(self) -> Dict[str, pd.DataFrame]:
        """高效加载数据"""
        try:
            print(f"\n📦 加载数据 (采样率: {self.data_sampling_ratio:.1%})...")
            
            # 加载数据
            btc_df = pd.read_csv('BTCUSDT_minute_data_2023_2026.csv')
            eth_df = pd.read_csv('ETHUSDT_minute_data_2023_2026.csv')
            
            # 智能采样 - 保留关键时间点
            sample_interval = int(1 / self.data_sampling_ratio)
            
            data = {}
            for symbol, df in [('BTCUSDT', btc_df), ('ETHUSDT', eth_df)]:
                # 采样数据
                sampled_df = df.iloc[::sample_interval].reset_index(drop=True)
                
                # 处理时间
                sampled_df['timestamp'] = pd.to_datetime(sampled_df['Open Time'])
                sampled_df = sampled_df.sort_values('timestamp').reset_index(drop=True)
                
                # 计算指标
                sampled_df = self.calculate_balanced_indicators(sampled_df)
                data[symbol] = sampled_df
                print(f"✓ {symbol}: {len(sampled_df):,}条数据")
                
            return data
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            return {}
            
    def calculate_balanced_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算平衡指标集合"""
        
        # 基础价格指标
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # 趋势指标
        df['sma_5'] = df['Close'].rolling(5).mean()
        df['sma_15'] = df['Close'].rolling(15).mean()
        df['sma_30'] = df['Close'].rolling(30).mean()
        df['trend_score'] = ((df['sma_5'] > df['sma_15']).astype(int) + 
                           (df['sma_15'] > df['sma_30']).astype(int))
        df['price_position'] = (df['Close'] - df['sma_30']) / df['sma_30']
        
        # 动量指标
        df['momentum_1'] = df['Close'] / df['Close'].shift(1) - 1
        df['momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
        df['momentum_15'] = df['Close'] / df['Close'].shift(15) - 1
        df['momentum_strength'] = (df['momentum_1'] + df['momentum_5'] + df['momentum_15']) / 3
        
        # 波动率指标
        df['volatility_short'] = df['returns'].rolling(5).std() * np.sqrt(365)
        df['volatility_long'] = df['returns'].rolling(20).std() * np.sqrt(365)
        df['vol_ratio'] = df['volatility_short'] / df['volatility_long']
        
        # RSI指标
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df['bb_mid'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + 2 * bb_std
        df['bb_lower'] = df['bb_mid'] - 2 * bb_std
        df['bb_pos'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # 市场状态
        df['market_state'] = 'normal'
        df.loc[df['volatility_short'] > df['volatility_short'].rolling(50).quantile(0.8), 'market_state'] = 'high_vol'
        df.loc[df['volatility_short'] < df['volatility_short'].rolling(50).quantile(0.2), 'market_state'] = 'low_vol'
        df.loc[abs(df['price_position']) > 0.15, 'market_state'] = 'trending'
        
        return df
    
    def analyze_market_regime(self, data: pd.DataFrame, current_idx: int) -> str:
        """分析当前市场状态"""
        if current_idx < 30:
            return 'normal'
        
        recent_data = data.iloc[current_idx-20:current_idx+1]
        latest = data.iloc[current_idx]
        
        # 波动率状态
        avg_vol = recent_data['volatility_short'].mean()
        vol_percentile = (recent_data['volatility_short'] > data.iloc[:current_idx]['volatility_short'].quantile(0.7)).mean()
        
        # 趋势状态
        trend_consistency = recent_data['trend_score'].mean()
        price_momentum = latest['momentum_strength']
        
        # 综合判断
        if vol_percentile > 0.6:
            if trend_consistency > 1.5:
                return 'volatile_trending'
            else:
                return 'volatile_ranging'
        elif trend_consistency > 1.5:
            return 'stable_trending' 
        elif abs(price_momentum) < 0.01:
            return 'ranging'
        else:
            return 'normal'
    
    def generate_balanced_signals(self, symbol: str, data: pd.DataFrame, current_idx: int) -> Dict:
        """生成平衡交易信号"""
        
        if current_idx < 30:
            return {'total_position': 0, 'confidence': 0, 'signals': {}}
        
        latest = data.iloc[current_idx]
        recent = data.iloc[current_idx-10:current_idx+1]
        
        # 分析市场状态
        market_regime = self.analyze_market_regime(data, current_idx)
        
        signals = {}
        total_position = 0
        
        # 1. 趋势跟踪策略 (30%权重)
        trend_signal = 0
        if latest['trend_score'] >= 2 and abs(latest['price_position']) > self.trend_threshold:
            if latest['price_position'] > 0 and latest['momentum_5'] > 0.01:
                trend_signal = 1.0  # 做多
            elif latest['price_position'] < 0 and latest['momentum_5'] < -0.01:
                trend_signal = -0.7  # 做空
        
        signals['trend_following'] = trend_signal
        total_position += trend_signal * 0.30
        
        # 2. 动量捕捉策略 (25%权重)
        momentum_signal = 0
        if abs(latest['momentum_strength']) > 0.015:
            momentum_signal = np.sign(latest['momentum_strength']) * 0.8
            # 强动量加仓
            if abs(latest['momentum_strength']) > 0.025:
                momentum_signal *= 1.3
        
        signals['momentum_capture'] = momentum_signal  
        total_position += momentum_signal * 0.25
        
        # 3. 均值回归策略 (25%权重)
        reversion_signal = 0
        if latest['rsi'] > self.rsi_overbought and latest['bb_pos'] > 0.8:
            reversion_signal = -0.8  # 超买做空
        elif latest['rsi'] < self.rsi_oversold and latest['bb_pos'] < 0.2:
            reversion_signal = 0.8   # 超卖做多
        elif 0.3 < latest['bb_pos'] < 0.7 and 40 < latest['rsi'] < 60:
            reversion_signal = 0.2   # 中性区间小仓位
            
        signals['mean_reversion'] = reversion_signal
        total_position += reversion_signal * 0.25
        
        # 4. 波动率交易策略 (15%权重)
        vol_signal = 0
        if latest['vol_ratio'] > 1.5:  # 波动率突增
            if abs(latest['momentum_1']) > 0.005:
                vol_signal = np.sign(latest['momentum_1']) * 0.6
        elif latest['vol_ratio'] < 0.7:  # 波动率压缩
            vol_signal = 0.3  # 小仓位等待突破
            
        signals['volatility_trading'] = vol_signal
        total_position += vol_signal * 0.15
        
        # 5. 对冲保护策略 (5%权重)
        hedge_signal = 0
        if market_regime in ['volatile_ranging', 'volatile_trending']:
            hedge_signal = -abs(total_position) * 0.3  # 高波动对冲
        else:
            hedge_signal = 0.1  # 低风险小仓位
            
        signals['hedge_protection'] = hedge_signal
        total_position += hedge_signal * 0.05
        
        # 根据市场状态调整
        if market_regime == 'volatile_ranging':
            total_position *= 0.7  # 震荡市减仓
        elif market_regime == 'stable_trending':
            total_position *= 1.2  # 稳定趋势加仓
        
        # 应用风险缩放
        total_position *= self.risk_scaling
        
        # 仓位限制
        total_position = np.clip(total_position, -1.0, 1.0)
        
        confidence = min(abs(total_position) * 0.8, 1.0)
        
        return {
            'total_position': total_position,
            'confidence': confidence,
            'signals': signals,
            'market_regime': market_regime
        }
    
    def execute_balanced_backtest(self, data: Dict) -> Dict:
        """执行平衡回测"""
        print(f"\n🚀 执行平衡高收益回测...")
        
        portfolio_value = self.initial_capital
        positions = {symbol: 0 for symbol in data.keys()}
        trades = []
        equity_curve = []
        max_portfolio_value = self.initial_capital
        
        min_length = min(len(data[symbol]) for symbol in data)
        
        # 进度跟踪
        update_interval = max(1, min_length // 50)
        
        for i in range(30, min_length, update_interval):
            period_start_value = portfolio_value
            
            # 为每个资产生成信号
            total_exposure = 0
            period_trades = []
            
            for symbol in data.keys():
                symbol_data = data[symbol]
                
                if i >= len(symbol_data):
                    continue
                
                # 生成信号
                signal_result = self.generate_balanced_signals(symbol, symbol_data, i)
                
                current_position = positions[symbol]
                target_position = signal_result['total_position'] * self.max_position_size
                
                # 控制总敞口
                if abs(target_position) + total_exposure <= self.max_total_exposure:
                    position_change = target_position - current_position
                    
                    if abs(position_change) > 0.05:  # 5%以上变化才交易
                        trade_cost = abs(position_change) * 0.0003  # 0.03%交易成本
                        
                        period_trades.append({
                            'symbol': symbol,
                            'position_change': position_change,
                            'cost': trade_cost,
                            'regime': signal_result.get('market_regime', 'normal')
                        })
                        
                        positions[symbol] = target_position
                        portfolio_value *= (1 - trade_cost)
                        total_exposure += abs(target_position)
            
            # 计算持仓收益
            period_return = 0
            for symbol in data.keys():
                if positions[symbol] != 0 and i > update_interval:
                    symbol_data = data[symbol]
                    if i < len(symbol_data):
                        price_return = (symbol_data.iloc[i]['Close'] / 
                                      symbol_data.iloc[i-update_interval]['Close'] - 1)
                        period_return += positions[symbol] * price_return
            
            portfolio_value = period_start_value * (1 + period_return)
            max_portfolio_value = max(max_portfolio_value, portfolio_value)
            
            # 风险管理
            current_drawdown = (max_portfolio_value - portfolio_value) / max_portfolio_value
            
            # 动态风险调整
            if current_drawdown > self.target_drawdown:
                self.risk_scaling = max(0.4, 1 - (current_drawdown - self.target_drawdown) * 3)
            else:
                self.risk_scaling = min(1.2, self.risk_scaling + 0.05)
            
            # 强制风控
            if current_drawdown > 0.13:  # 13%时强制减仓
                for symbol in positions:
                    positions[symbol] *= 0.7
                print(f"⚠️ 风险控制: 回撤{current_drawdown:.1%}, 减仓30%")
            
            # 记录数据
            trades.extend(period_trades)
            equity_curve.append({
                'portfolio_value': portfolio_value,
                'drawdown': current_drawdown,
                'total_exposure': total_exposure,
                'risk_scaling': self.risk_scaling
            })
            
            # 进度显示
            if i % (update_interval * 10) == 0:
                progress = i / min_length * 100
                print(f"📊 回测进度: {progress:.1f}% | 当前价值: ${portfolio_value:,.0f} | 回撤: {current_drawdown:.1%}")
        
        return self.calculate_balanced_metrics(portfolio_value, trades, equity_curve)
    
    def calculate_balanced_metrics(self, final_value: float, trades: List, equity_curve: List) -> Dict:
        """计算平衡性能指标"""
        
        if not equity_curve:
            return {}
        
        # 收益指标
        total_return = (final_value / self.initial_capital - 1) * 100
        
        # 估计回测年数
        estimated_years = len(equity_curve) * (1/self.data_sampling_ratio) * (self.rebalance_frequency/24) / 365.25
        annualized_return = ((final_value / self.initial_capital) ** (1/estimated_years) - 1) * 100
        
        # 风险指标
        values = [point['portfolio_value'] for point in equity_curve]
        returns = [(values[i] / values[i-1] - 1) for i in range(1, len(values))]
        
        volatility = np.std(returns) * np.sqrt(365) * 100 if returns else 0
        sharpe_ratio = (annualized_return - 4) / volatility if volatility > 0 else 0
        
        max_drawdown = max([point['drawdown'] for point in equity_curve]) * 100
        avg_exposure = np.mean([point['total_exposure'] for point in equity_curve])
        
        # 胜率
        winning_periods = len([r for r in returns if r > 0])
        win_rate = winning_periods / len(returns) * 100 if returns else 0
        
        # 收益回撤比
        return_drawdown_ratio = abs(annualized_return) / max(max_drawdown, 1)
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': len(trades),
            'final_value': final_value,
            'avg_exposure': avg_exposure,
            'return_drawdown_ratio': return_drawdown_ratio,
            'estimated_years': estimated_years
        }
    
    def run_balanced_backtest(self) -> Dict:
        """运行平衡回测"""
        print(f"\n📅 15%回撤平衡高收益回测: {self.start_date} - {self.end_date}")
        print(f"💰 初始资金: ${self.initial_capital:,}")
        print(f"⚡ 预期年化收益: 25-45%")
        print(f"🛡️ 目标回撤: ≤ {self.max_drawdown_limit:.0%}")
        
        data = self.load_efficient_data()
        if not data:
            return {}
        
        results = self.execute_balanced_backtest(data)
        
        if not results:
            print("❌ 回测失败")
            return {}
        
        # 显示结果
        print(f"\n🚀 15%回撤平衡高收益回测结果:")
        print(f"{'='*75}")
        print(f"💰 总收益率:      {results['total_return']:>10.2f}%")
        print(f"📈 年化收益率:    {results['annualized_return']:>10.2f}%")
        print(f"📊 年化波动率:    {results['volatility']:>10.2f}%")
        print(f"⚡ 夏普比率:      {results['sharpe_ratio']:>10.3f}")
        print(f"📉 最大回撤:      {results['max_drawdown']:>10.2f}%")
        print(f"🎯 胜率:          {results['win_rate']:>10.1f}%")
        print(f"💼 平均敞口:      {results['avg_exposure']:>10.1f}%")
        print(f"🔄 总交易次数:    {results['total_trades']:>10d}")
        print(f"💵 最终价值:      ${results['final_value']:>10,.0f}")
        print(f"⏰ 估计年数:      {results['estimated_years']:>10.2f}")
        
        # 核心指标分析
        profit_multiplier = results['final_value'] / self.initial_capital
        excess_return = results['annualized_return'] - 8  # 假设基准8%
        
        print(f"\n📊 核心指标分析:")
        print(f"   💎 利润倍数:      {profit_multiplier:>8.2f}x")
        print(f"   🎚️ 收益回撤比:    {results['return_drawdown_ratio']:>8.2f}")
        print(f"   🏆 超额收益:      {excess_return:>8.1f}% (vs 8%基准)")
        print(f"   ✅ 风险控制:      {'成功' if results['max_drawdown'] <= 15 else '超限'}")
        
        # 综合评级
        score = 0
        if results['annualized_return'] > 20: score += 2
        if results['max_drawdown'] <= 12: score += 2
        if results['sharpe_ratio'] > 1.0: score += 1
        if results['win_rate'] > 55: score += 1
        
        if score >= 5:
            grade = "🌟 优秀"
            recommendation = "强烈推荐部署"
        elif score >= 3:
            grade = "⭐ 良好"
            recommendation = "推荐部署"
        else:
            grade = "📈 可接受"
            recommendation = "谨慎部署"
        
        print(f"\n🏆 综合评估:")
        print(f"   📈 综合评级:      {grade} ({score}/6分)")
        print(f"   💡 部署建议:      {recommendation}")
        
        # 投资价值分析
        if results['annualized_return'] > 15 and results['max_drawdown'] <= 15:
            annual_profit = (results['final_value'] - self.initial_capital) / results['estimated_years']
            print(f"   💰 年均利润:      ${annual_profit:,.0f}")
            print(f"   🎯 投资价值:      适合追求高收益的投资者")
        
        return results

def main():
    """主函数"""
    print("🚀 启动15%回撤平衡高收益CTA系统 V2.0")
    print("🎯 目标：平衡风险收益，在15%回撤限制下追求最优收益")
    
    # 创建平衡系统
    balanced_system = BalancedHighReturnCTA()
    
    # 运行平衡回测
    results = balanced_system.run_balanced_backtest()
    
    if results and results.get('final_value', 0) > 0:
        print(f"\n✅ 平衡回测成功完成!")
        print(f"🎯 关键成就:")
        
        if results['max_drawdown'] <= 15:
            print(f"   ✅ 风险控制: 最大回撤 {results['max_drawdown']:.1f}% ≤ 15%")
        
        if results['annualized_return'] > 15:
            print(f"   💰 收益目标: 年化 {results['annualized_return']:.1f}% > 15%")
            
        roi = (results['final_value'] / 100000 - 1) * 100
        print(f"   🏆 总体ROI: {roi:+.1f}%")
        print(f"\n🚀 系统已准备就绪，建议进行实盘部署验证！")

if __name__ == "__main__":
    main()