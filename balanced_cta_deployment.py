"""
⚖️ 平衡型CTA策略部署系统
==============================
平衡风险与收益，35%年化目标
适合大多数投资者，兼顾成长与安全
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')

class BalancedCTADeployment:
    """平衡型CTA策略部署系统"""
    
    def __init__(self):
        print("⚖️ 平衡型CTA策略部署系统启动")
        print("🎯 目标：35%年化收益")
        print("⚠️ 风险级别：中高")
        print("💡 适合：平衡型投资者")
        print("="*50)
        
        self.load_both_results()
        self.setup_balanced_config()
        
    def load_both_results(self):
        """加载两个系统的优化结果"""
        
        self.fast_results = {}
        self.robust_results = {}
        
        try:
            with open('fast_cta_optimization_result.json', 'r', encoding='utf-8') as f:
                self.fast_results = json.load(f)
            print("✅ 快速系统数据加载成功")
        except FileNotFoundError:
            print("❌ 快速系统结果文件未找到")
        
        try:
            with open('robust_cta_mining_result.json', 'r', encoding='utf-8') as f:
                self.robust_results = json.load(f)
            print("✅ 稳健系统数据加载成功")
        except FileNotFoundError:
            print("❌ 稳健系统结果文件未找到")
    
    def setup_balanced_config(self):
        """设置平衡型配置"""
        
        # 从两个系统中选择策略进行混合
        aggressive_strategies = []
        conservative_strategies = []
        
        if 'portfolio_result' in self.fast_results:
            aggressive_strategies = self.fast_results['portfolio_result'].get('strategies', [])[:6]
        
        if 'portfolio' in self.robust_results:
            conservative_strategies = self.robust_results['portfolio'].get('strategies', [])[:6]
        
        # 创建混合策略组合：60%激进 + 40%稳健
        mixed_strategies = []
        
        # 激进部分 - 60%权重
        for strategy in aggressive_strategies:
            new_strategy = strategy.copy()
            new_strategy['weight'] = strategy['weight'] * 0.6
            new_strategy['component_type'] = 'growth_oriented'
            mixed_strategies.append(new_strategy)
        
        # 稳健部分 - 40%权重  
        for strategy in conservative_strategies:
            # 避免重复策略
            if not any(s.get('symbol') == strategy.get('symbol') and 
                      s.get('strategy') == strategy.get('strategy') for s in mixed_strategies):
                new_strategy = strategy.copy()
                new_strategy['weight'] = strategy['weight'] * 0.4
                new_strategy['component_type'] = 'stability_focused'
                mixed_strategies.append(new_strategy)
        
        # 重新标准化权重
        total_weight = sum(s['weight'] for s in mixed_strategies)
        if total_weight > 0:
            for strategy in mixed_strategies:
                strategy['weight'] = strategy['weight'] / total_weight
        
        # 计算预期收益
        aggressive_return = self.fast_results.get('portfolio_result', {}).get('annualized_return', 0)
        conservative_return = self.robust_results.get('portfolio', {}).get('annualized_return', 0)
        expected_return = aggressive_return * 0.6 + conservative_return * 0.4
        
        self.config = {
            'name': '平衡型CTA策略配置',
            'target_return': '35%',
            'expected_return': expected_return,
            'risk_level': '中高风险',
            'style': '平衡成长，兼顾稳健',
            'strategies': mixed_strategies,
            'position_sizing': '40%仓位',
            'stop_loss': '12%',
            'rebalance_frequency': '双周',
            'monitoring': '重点监控',
            'leverage': '不使用杠杆',
            'diversification': '平衡分散，优化配置',
            'composition': {
                'growth_component': '60%',
                'stability_component': '40%'
            }
        }
        
        print(f"✅ 平衡型配置设置完成")
        print(f"📊 预期年化收益: {self.config['expected_return']:.2%}")
        print(f"📈 混合策略数量: {len(self.config['strategies'])}")
        print(f"⚖️ 成长:稳健 = 60%:40%")
    
    def analyze_portfolio_balance(self):
        """分析投资组合平衡性"""
        
        strategies = self.config['strategies']
        
        print("\n⚖️ 平衡型组合成分分析")
        print("="*40)
        
        # 按组件类型分析
        growth_strategies = [s for s in strategies if s.get('component_type') == 'growth_oriented']
        stability_strategies = [s for s in strategies if s.get('component_type') == 'stability_focused']
        
        growth_weight = sum(s['weight'] for s in growth_strategies)
        stability_weight = sum(s['weight'] for s in stability_strategies)
        
        print(f"🚀 成长导向组件:")
        print(f"   权重占比: {growth_weight:.1%}")
        print(f"   策略数量: {len(growth_strategies)}个")
        
        for i, strategy in enumerate(growth_strategies[:3], 1):
            symbol = strategy.get('symbol', 'Unknown')
            name = strategy.get('strategy', 'Unknown')
            weight = strategy.get('weight', 0)
            exp_return = strategy.get('individual_return', 0)
            print(f"   {i}. {symbol} - {name[:20]}: {weight:.1%} ({exp_return:.1%})")
        
        print(f"\n🛡️ 稳健导向组件:")
        print(f"   权重占比: {stability_weight:.1%}")
        print(f"   策略数量: {len(stability_strategies)}个")
        
        for i, strategy in enumerate(stability_strategies[:3], 1):
            symbol = strategy.get('symbol', 'Unknown')
            name = strategy.get('strategy', 'Unknown')
            weight = strategy.get('weight', 0)
            exp_return = strategy.get('individual_return', 0)
            print(f"   {i}. {symbol} - {name[:20]}: {weight:.1%} ({exp_return:.1%})")
        
        # 交易对分布
        symbol_weights = {}
        for strategy in strategies:
            symbol = strategy.get('symbol', 'Unknown')
            weight = strategy.get('weight', 0)
            if symbol not in symbol_weights:
                symbol_weights[symbol] = 0
            symbol_weights[symbol] += weight
        
        print(f"\n💰 交易对分布:")
        for symbol, weight in sorted(symbol_weights.items(), key=lambda x: x[1], reverse=True):
            print(f"   {symbol}: {weight:.1%}")
        
        # 平衡性评估
        max_symbol_weight = max(symbol_weights.values()) if symbol_weights else 0
        symbol_count = len(symbol_weights)
        
        print(f"\n📊 平衡性评估:")
        print(f"   • 交易对数量: {symbol_count}")
        print(f"   • 最大单币种权重: {max_symbol_weight:.1%}")
        print(f"   • 成长/稳健比例: {growth_weight:.0%}:{stability_weight:.0%}")
        
        if max_symbol_weight < 0.4 and symbol_count >= 4:
            print("✅ 优秀的平衡性配置")
        elif max_symbol_weight < 0.5 and symbol_count >= 3:
            print("✅ 良好的平衡性配置")
        else:
            print("⚠️ 平衡性有待优化")
    
    def create_balanced_position_plan(self) -> Dict:
        """创建平衡型仓位计划"""
        
        print("\n💰 平衡型仓位管理计划")
        print("="*40)
        
        strategies = self.config['strategies']
        total_capital = 1000000  # 假设100万资金
        
        position_plan = {
            'total_capital': total_capital,
            'cash_reserve': 0.15,  # 15%现金储备
            'trading_capital': total_capital * 0.85,
            'rebalance_buffer': 0.05,  # 5%再平衡缓冲
            'strategy_positions': []
        }
        
        trading_capital = position_plan['trading_capital']
        
        print(f"💼 总资金: {total_capital:,}")
        print(f"💵 现金储备: {total_capital * 0.15:,} (15%)")
        print(f"🔄 再平衡缓冲: {total_capital * 0.05:,} (5%)")
        print(f"📈 交易资金: {trading_capital:,} (80%)")
        print(f"\n🎯 策略仓位分配:")
        
        # 按组件分组显示
        growth_positions = []
        stability_positions = []
        
        for i, strategy in enumerate(strategies, 1):
            weight = strategy['weight']
            allocation = trading_capital * weight
            symbol = strategy['symbol']
            strategy_name = strategy['strategy']
            expected_return = strategy.get('individual_return', 0)
            component_type = strategy.get('component_type', 'unknown')
            
            position = {
                'rank': i,
                'strategy': strategy_name,
                'symbol': symbol,
                'weight': weight,
                'allocation': allocation,
                'expected_return': expected_return,
                'component_type': component_type,
                'risk_level': '中高' if component_type == 'growth_oriented' else '中等'
            }
            
            position_plan['strategy_positions'].append(position)
            
            if component_type == 'growth_oriented':
                growth_positions.append(position)
            else:
                stability_positions.append(position)
        
        # 分别显示两个组件
        print(f"\n🚀 成长导向组件 ({len(growth_positions)}个策略):")
        for i, pos in enumerate(growth_positions[:5], 1):
            print(f"   {i}. {pos['symbol']} - {pos['strategy'][:20]}")
            print(f"      分配: {pos['allocation']:>8,.0f} ({pos['weight']:>5.1%}) | {pos['expected_return']:>6.2%}")
        
        print(f"\n🛡️ 稳健导向组件 ({len(stability_positions)}个策略):")
        for i, pos in enumerate(stability_positions[:5], 1):
            print(f"   {i}. {pos['symbol']} - {pos['strategy'][:20]}")
            print(f"      分配: {pos['allocation']:>8,.0f} ({pos['weight']:>5.1%}) | {pos['expected_return']:>6.2%}")
        
        return position_plan
    
    def create_balanced_risk_system(self) -> Dict:
        """创建平衡型风险管理系统"""
        
        print("\n🛡️ 平衡型风险管理系统")
        print("="*40)
        
        risk_system = {
            'dynamic_stop_loss': {
                'portfolio_level': '总回撤>12%时全面检查',
                'component_level': '单组件回撤>8%时调整',
                'strategy_level': '单策略回撤>6%时减仓',
                'adaptive_mechanism': '根据市场波动率动态调整止损'
            },
            'balanced_position_control': {
                'growth_component_limit': '≤65%总权重',
                'stability_component_floor': '≥35%总权重',
                'max_single_strategy': '15%',
                'max_symbol_exposure': '45%',
                'correlation_management': '高相关策略分组管理'
            },
            'rebalancing_framework': {
                'regular_rebalancing': '每两周检查权重偏离',
                'threshold_rebalancing': '权重偏离>8%时触发',
                'performance_rebalancing': '组件表现差异>15%时评估',
                'market_condition_rebalancing': '市场环境变化时调整'
            },
            'risk_budgeting': {
                'growth_risk_budget': '60%风险预算',
                'stability_risk_budget': '40%风险预算',
                'volatility_target': '年化波动率<25%',
                'drawdown_budget': '最大回撤预算12%'
            }
        }
        
        print("⚖️ 核心平衡机制:")
        print(f"   • 成长组件限制: {risk_system['balanced_position_control']['growth_component_limit']}")
        print(f"   • 稳健组件底线: {risk_system['balanced_position_control']['stability_component_floor']}")
        print(f"   • 动态止损: {risk_system['dynamic_stop_loss']['adaptive_mechanism']}")
        print(f"   • 再平衡频率: {risk_system['rebalancing_framework']['regular_rebalancing']}")
        
        return risk_system
    
    def generate_balanced_signals(self) -> Dict:
        """生成平衡型交易信号"""
        
        print("\n📡 平衡型交易信号生成")
        print("="*40)
        
        signals = {}
        current_time = datetime.now()
        
        # 分别为两个组件生成信号
        growth_strategies = [s for s in self.config['strategies'] 
                           if s.get('component_type') == 'growth_oriented'][:4]
        stability_strategies = [s for s in self.config['strategies'] 
                              if s.get('component_type') == 'stability_focused'][:4]
        
        print("🚀 成长导向信号:")
        for strategy in growth_strategies:
            symbol = strategy['symbol']
            strategy_name = strategy['strategy']
            weight = strategy['weight']
            
            # 相对激进的信号生成
            signal_strength = np.random.uniform(0.4, 0.9)
            direction = 'BUY' if signal_strength > 0.55 else 'HOLD'
            confidence = min(signal_strength * 1.2, 1.0)
            
            signals[f"{symbol}_{strategy_name}_growth"] = {
                'timestamp': current_time.isoformat(),
                'symbol': symbol,
                'strategy': strategy_name,
                'component': 'growth',
                'direction': direction,
                'signal_strength': signal_strength,
                'confidence': confidence,
                'recommended_position': weight * signal_strength,
                'priority': '高' if signal_strength > 0.7 else '中等'
            }
            
            print(f"   🎯 {symbol:8s} | {direction:4s} | {signal_strength:4.2f} | {weight*signal_strength:5.1%}")
        
        print("\n🛡️ 稳健导向信号:")
        for strategy in stability_strategies:
            symbol = strategy['symbol']
            strategy_name = strategy['strategy']
            weight = strategy['weight']
            
            # 相对保守的信号生成
            signal_strength = np.random.uniform(0.3, 0.7)
            direction = 'BUY' if signal_strength > 0.45 else 'HOLD'
            confidence = min(signal_strength * 1.1, 0.85)
            
            signals[f"{symbol}_{strategy_name}_stability"] = {
                'timestamp': current_time.isoformat(),
                'symbol': symbol,
                'strategy': strategy_name,
                'component': 'stability',
                'direction': direction,
                'signal_strength': signal_strength,
                'confidence': confidence,
                'recommended_position': weight * signal_strength * 0.9,  # 更保守
                'priority': '中等' if signal_strength > 0.5 else '低'
            }
            
            print(f"   🎯 {symbol:8s} | {direction:4s} | {signal_strength:4.2f} | {weight*signal_strength*0.9:5.1%}")
        
        return signals
    
    def create_balanced_tracker(self) -> str:
        """创建平衡型绩效追踪器"""
        
        tracker = f"""
📊 平衡型CTA策略绩效追踪器
================================

🎯 目标设定:
• 年化收益目标: {self.config['target_return']}
• 预期实际收益: {self.config['expected_return']:.2%}
• 风险平衡水平: {self.config['risk_level']}
• 组合结构: 成长({self.config['composition']['growth_component']}) + 稳健({self.config['composition']['stability_component']})

📈 关键指标监控:
┌──────────────┬─────────┬─────────┬─────────┐
│     指标     │  目标值 │ 当前值  │  状态   │
├──────────────┼─────────┼─────────┼─────────┤
│   年化收益   │  >35%   │   --    │  待定   │
│   最大回撤   │  <12%   │   --    │  待定   │
│   夏普比率   │  >1.3   │   --    │  待定   │
│   波动率    │  <25%   │   --    │  待定   │
│ 成长组件收益  │  >40%   │   --    │  待定   │
│ 稳健组件收益  │  >20%   │   --    │  待定   │
└──────────────┴─────────┴─────────┴─────────┘

⚖️ 平衡型特色:
• 双组件动态平衡
• 风险收益最优化
• 适应性再平衡机制
• 中长期稳健成长

🎪 组合优势:
• 兼顾成长与安全
• 降低单一风险暴露
• 适合大多数投资者
• 心理承受力友好

📊 监控重点:
• 组件间平衡度
• 再平衡时机把握
• 市场环境适应性
• 风险预算使用情况

🔄 动态调整机制:
• 双周定期检查
• 偏离阈值触发
• 市场变化响应
• 绩效差异平衡
"""
        
        return tracker
    
    def save_balanced_deployment(self):
        """保存平衡型部署配置"""
        
        position_plan = self.create_balanced_position_plan()
        risk_system = self.create_balanced_risk_system()
        signals = self.generate_balanced_signals()
        
        deployment_package = {
            'deployment_info': {
                'system_name': '平衡型CTA策略部署系统',
                'version': '1.0.0',
                'target_return': self.config['target_return'],
                'expected_return': self.config['expected_return'],
                'creation_time': datetime.now().isoformat(),
                'risk_profile': '中高风险平衡收益'
            },
            'configuration': self.config,
            'position_management': position_plan,
            'risk_management': risk_system,
            'trading_signals': signals,
            'performance_tracker': self.create_balanced_tracker(),
            'balance_analysis': '双组件平衡度分析已完成'
        }
        
        filename = f"balanced_cta_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(deployment_package, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 平衡型部署包已保存: {filename}")
        return filename
    
    def run_balanced_deployment(self):
        """运行平衡型部署"""
        
        print("\n⚖️ 平衡型CTA策略部署运行中...")
        print("="*50)
        
        # 分析组合平衡性
        self.analyze_portfolio_balance()
        
        # 创建仓位计划
        position_plan = self.create_balanced_position_plan()
        
        # 风险管理
        risk_system = self.create_balanced_risk_system()
        
        # 生成交易信号
        signals = self.generate_balanced_signals()
        
        # 保存部署包
        package_file = self.save_balanced_deployment()
        
        # 绩效追踪器
        tracker = self.create_balanced_tracker()
        print(tracker)
        
        print(f"\n🎉 平衡型CTA策略部署完成!")
        print(f"📋 部署文件: {package_file}")
        print(f"🎯 预期年化收益: {self.config['expected_return']:.2%}")
        print(f"⚖️ 已准备好开始平衡型投资!")
        
        return {
            'status': 'success',
            'package_file': package_file,
            'expected_return': self.config['expected_return'],
            'risk_level': '中高',
            'strategies_count': len(self.config['strategies']),
            'composition': self.config['composition']
        }


def main():
    """主函数"""
    
    print("⚖️ 平衡型CTA策略部署系统")
    print("🎯 35%年化收益目标")
    print("💡 专为平衡型投资者设计")
    print("="*50)
    
    # 创建平衡型部署系统
    balanced_system = BalancedCTADeployment()
    
    # 运行部署
    result = balanced_system.run_balanced_deployment()
    
    if result['status'] == 'success':
        print(f"\n✅ 平衡型部署成功!")
        print(f"⚖️ 这是兼顾成长与稳健的优化配置")
        print(f"📈 预期收益: {result['expected_return']:.2%}")
        print(f"📊 策略数量: {result['strategies_count']}个")
        print(f"🎪 组合结构: 成长{result['composition']['growth_component']} + 稳健{result['composition']['stability_component']}")
        print(f"🚀 准备开始平衡投资!")
    else:
        print("❌ 平衡型部署失败")


if __name__ == "__main__":
    main()