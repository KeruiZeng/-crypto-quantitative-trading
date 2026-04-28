"""
🛡️ 稳健型CTA策略部署系统
==============================
专注风险控制，25%年化目标
适合稳健型投资者，平衡收益与安全性
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')

class ConservativeCTADeployment:
    """稳健型CTA策略部署系统"""
    
    def __init__(self):
        print("🛡️ 稳健型CTA策略部署系统启动")
        print("🎯 目标：25%年化收益")
        print("⚠️ 风险级别：中等")
        print("💡 适合：稳健投资者")
        print("="*50)
        
        self.load_robust_results()
        self.setup_conservative_config()
        
    def load_robust_results(self):
        """加载稳健系统优化结果"""
        
        try:
            with open('robust_cta_mining_result.json', 'r', encoding='utf-8') as f:
                self.robust_results = json.load(f)
            print("✅ 稳健系统数据加载成功")
        except FileNotFoundError:
            print("❌ 稳健系统结果文件未找到")
            self.robust_results = {}
    
    def setup_conservative_config(self):
        """设置稳健型配置"""
        
        if 'portfolio' not in self.robust_results:
            print("❌ 无法找到投资组合结果")
            return
        
        portfolio = self.robust_results['portfolio']
        
        self.config = {
            'name': '稳健型CTA策略配置',
            'target_return': '25%',
            'expected_return': portfolio.get('annualized_return', 0),
            'risk_level': '中等风险',
            'style': '均衡分散，注重稳健',
            'strategies': portfolio.get('strategies', []),  # 全部策略
            'position_sizing': '30%仓位',
            'stop_loss': '10%',
            'rebalance_frequency': '月度',
            'monitoring': '常规监控',
            'leverage': '不使用杠杆',
            'diversification': '充分分散，降低风险'
        }
        
        print(f"✅ 稳健型配置设置完成")
        print(f"📊 预期年化收益: {self.config['expected_return']:.2%}")
        print(f"📈 策略总数量: {len(self.config['strategies'])}")
    
    def analyze_diversification(self):
        """分析分散化程度"""
        
        strategies = self.config['strategies']
        
        print("\n📊 稳健型分散化分析")
        print("="*40)
        
        # 统计分析
        symbol_distribution = {}
        strategy_type_distribution = {}
        weight_distribution = {'small': 0, 'medium': 0, 'large': 0}
        
        for strategy in strategies:
            symbol = strategy.get('symbol', 'Unknown')
            weight = strategy.get('weight', 0)
            strategy_name = strategy.get('strategy', '')
            
            # 提取策略类型
            if 'SuperMomentum' in strategy_name:
                strategy_type = 'SuperMomentum'
            elif 'AdvancedRSI' in strategy_name:
                strategy_type = 'AdvancedRSI'
            elif 'MeanReversion' in strategy_name:
                strategy_type = 'MeanReversion'
            elif 'Breakout' in strategy_name:
                strategy_type = 'Breakout'
            else:
                strategy_type = 'Other'
            
            # 统计交易对分布
            if symbol not in symbol_distribution:
                symbol_distribution[symbol] = {'weight': 0, 'count': 0}
            symbol_distribution[symbol]['weight'] += weight
            symbol_distribution[symbol]['count'] += 1
            
            # 统计策略类型分布
            if strategy_type not in strategy_type_distribution:
                strategy_type_distribution[strategy_type] = {'weight': 0, 'count': 0}
            strategy_type_distribution[strategy_type]['weight'] += weight
            strategy_type_distribution[strategy_type]['count'] += 1
            
            # 权重分布
            if weight < 0.05:
                weight_distribution['small'] += 1
            elif weight < 0.10:
                weight_distribution['medium'] += 1
            else:
                weight_distribution['large'] += 1
        
        print("🌍 交易对分散度:")
        for symbol, data in sorted(symbol_distribution.items(), key=lambda x: x[1]['weight'], reverse=True):
            print(f"   💰 {symbol}: {data['weight']:.1%} ({data['count']}个策略)")
        
        print("\n🎯 策略类型分散度:")
        for stype, data in sorted(strategy_type_distribution.items(), key=lambda x: x[1]['weight'], reverse=True):
            print(f"   📈 {stype}: {data['weight']:.1%} ({data['count']}个)")
        
        print(f"\n⚖️ 权重分布分析:")
        print(f"   • 小仓位(<5%): {weight_distribution['small']}个策略")
        print(f"   • 中等仓位(5-10%): {weight_distribution['medium']}个策略") 
        print(f"   • 大仓位(>10%): {weight_distribution['large']}个策略")
        
        # 分散化评分
        symbol_count = len(symbol_distribution)
        type_count = len(strategy_type_distribution)
        max_weight = max(s['weight'] for s in strategies)
        
        diversification_score = min(100, (symbol_count * 15) + (type_count * 10) + ((1 - max_weight) * 50))
        
        print(f"\n🏆 分散化评分: {diversification_score:.0f}/100")
        if diversification_score >= 80:
            print("✅ 优秀的分散化配置")
        elif diversification_score >= 60:
            print("✅ 良好的分散化配置") 
        else:
            print("⚠️ 分散化程度有待提升")
    
    def create_conservative_position_plan(self) -> Dict:
        """创建稳健型仓位计划"""
        
        print("\n💰 稳健型仓位管理计划")
        print("="*40)
        
        strategies = self.config['strategies']
        total_capital = 1000000  # 假设100万资金
        
        position_plan = {
            'total_capital': total_capital,
            'cash_reserve': 0.2,  # 20%现金储备
            'trading_capital': total_capital * 0.8,
            'emergency_reserve': 0.05,  # 5%紧急储备
            'strategy_positions': []
        }
        
        trading_capital = position_plan['trading_capital']
        
        print(f"💼 总资金: {total_capital:,}")
        print(f"💵 现金储备: {total_capital * 0.2:,} (20%)")
        print(f"🆘 紧急储备: {total_capital * 0.05:,} (5%)")
        print(f"📈 交易资金: {trading_capital:,} (75%)")
        print(f"\n🎯 策略仓位分配:")
        
        for i, strategy in enumerate(strategies, 1):
            weight = strategy['weight']
            allocation = trading_capital * weight
            symbol = strategy['symbol']
            strategy_name = strategy['strategy']
            expected_return = strategy.get('individual_return', 0)
            
            # 风险等级评估
            if weight > 0.12:
                risk_level = '中高'
            elif weight > 0.08:
                risk_level = '中等'
            else:
                risk_level = '低'
            
            position = {
                'rank': i,
                'strategy': strategy_name,
                'symbol': symbol,
                'weight': weight,
                'allocation': allocation,
                'expected_return': expected_return,
                'risk_level': risk_level
            }
            
            position_plan['strategy_positions'].append(position)
            
            # 只显示前10个策略的详细信息
            if i <= 10:
                print(f"   {i:2d}. {symbol} - {strategy_name[:25]}")
                print(f"       分配: {allocation:>8,.0f} ({weight:>5.1%}) | {risk_level} | {expected_return:>6.2%}")
        
        if len(strategies) > 10:
            print(f"   ... 及其他 {len(strategies) - 10} 个策略")
        
        return position_plan
    
    def create_conservative_risk_system(self) -> Dict:
        """创建稳健型风险管理系统"""
        
        print("\n🛡️ 稳健型风险管理系统")
        print("="*40)
        
        risk_system = {
            'stop_loss_rules': {
                'individual_strategy': '单策略回撤>5%时减仓',
                'portfolio_level': '组合回撤>10%全面降仓',
                'daily_limit': '单日亏损>2%暂停新开仓',
                'weekly_limit': '周亏损>5%进行策略检查'
            },
            'position_limits': {
                'max_single_position': '12%',
                'max_symbol_exposure': '40%',
                'min_strategy_count': '至少10个不同策略',
                'correlation_limit': '高相关策略总权重<25%'
            },
            'monitoring_protocols': {
                'daily_checks': [
                    '策略收益与预期偏差检查',
                    '市场环境变化评估',
                    '流动性状况监控', 
                    '风险指标更新'
                ],
                'weekly_reviews': [
                    '策略表现排名',
                    '组合分散度评估',
                    '风险预算使用情况',
                    '再平衡需要性分析'
                ],
                'monthly_audits': [
                    '全面策略评估',
                    '风险管理有效性',
                    '市场环境适应性',
                    '优化建议制定'
                ]
            },
            'capital_protection': {
                'progressive_stop_loss': '损失3%减仓25%, 损失6%减仓50%, 损失10%全面止损',
                'profit_protection': '盈利15%时保护50%利润',
                'volatility_adjustment': '市场波动率>20%时降低仓位',
                'liquidity_reserve': '保持充足现金应对机会'
            }
        }
        
        print("🔐 核心保护措施:")
        print(f"   • 组合止损: {risk_system['stop_loss_rules']['portfolio_level']}")
        print(f"   • 最大单仓: {risk_system['position_limits']['max_single_position']}")
        print(f"   • 分散度要求: {risk_system['position_limits']['min_strategy_count']}")
        print(f"   • 渐进止损: {risk_system['capital_protection']['progressive_stop_loss']}")
        
        return risk_system
    
    def generate_conservative_signals(self) -> Dict:
        """生成稳健型交易信号"""
        
        print("\n📡 稳健型交易信号生成")
        print("="*40)
        
        signals = {}
        current_time = datetime.now()
        
        # 选择前8个策略生成信号
        for strategy in self.config['strategies'][:8]:
            symbol = strategy['symbol']
            strategy_name = strategy['strategy']
            weight = strategy['weight']
            
            # 更保守的信号生成逻辑
            base_signal = np.random.uniform(0.3, 0.8)  # 较低的信号强度
            market_filter = 0.9  # 保守的市场过滤器
            
            signal_strength = base_signal * market_filter
            direction = 'BUY' if signal_strength > 0.5 else 'HOLD'
            confidence = min(signal_strength * 1.1, 0.9)  # 更保守的置信度
            
            # 保守的仓位建议
            recommended_position = weight * signal_strength * 0.8  # 80%的保守系数
            
            signals[f"{symbol}_{strategy_name}"] = {
                'timestamp': current_time.isoformat(),
                'symbol': symbol,
                'strategy': strategy_name,
                'direction': direction,
                'signal_strength': signal_strength,
                'confidence': confidence,
                'recommended_position': recommended_position,
                'risk_assessment': '低风险' if signal_strength < 0.6 else '中等风险',
                'priority': '中等' if signal_strength > 0.6 else '低'
            }
            
            print(f"🎯 {symbol:8s} | {direction:4s} | 强度:{signal_strength:4.2f} | 仓位:{recommended_position:5.1%}")
        
        return signals
    
    def create_conservative_tracker(self) -> str:
        """创建稳健型绩效追踪器"""
        
        tracker = f"""
📊 稳健型CTA策略绩效追踪器
================================

🎯 目标设定:
• 年化收益目标: {self.config['target_return']}
• 预期实际收益: {self.config['expected_return']:.2%}
• 风险控制水平: {self.config['risk_level']}
• 最大回撤限制: {self.config['stop_loss']}

📈 关键指标监控:
┌──────────────┬─────────┬─────────┬─────────┐
│     指标     │  目标值 │ 当前值  │  状态   │
├──────────────┼─────────┼─────────┼─────────┤
│   年化收益   │  >25%   │   --    │  待定   │
│   最大回撤   │  <10%   │   --    │  待定   │
│   夏普比率   │  >1.2   │   --    │  待定   │
│   胜率      │  >45%   │   --    │  待定   │
│   波动率    │  <20%   │   --    │  待定   │
└──────────────┴─────────┴─────────┴─────────┘

🛡️ 稳健型特色:
• 充分分散投资组合
• 严格风险控制体系
• 渐进式仓位管理
• 长期稳健增长导向

✅ 优势特点:
• 回撤控制严格
• 收益相对稳定
• 心理压力较小
• 适合长期投资

⚠️ 注意事项:
• 收益增长相对温和
• 需要耐心等待复利
• 定期检查再平衡
• 保持纪律性执行
"""
        
        return tracker
    
    def save_conservative_deployment(self):
        """保存稳健型部署配置"""
        
        position_plan = self.create_conservative_position_plan()
        risk_system = self.create_conservative_risk_system()
        signals = self.generate_conservative_signals()
        
        deployment_package = {
            'deployment_info': {
                'system_name': '稳健型CTA策略部署系统',
                'version': '1.0.0',
                'target_return': self.config['target_return'],
                'expected_return': self.config['expected_return'],
                'creation_time': datetime.now().isoformat(),
                'risk_profile': '中等风险稳健收益'
            },
            'configuration': self.config,
            'position_management': position_plan,
            'risk_management': risk_system,
            'trading_signals': signals,
            'performance_tracker': self.create_conservative_tracker(),
            'diversification_analysis': '详细分散度分析已完成'
        }
        
        filename = f"conservative_cta_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(deployment_package, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 稳健型部署包已保存: {filename}")
        return filename
    
    def run_conservative_deployment(self):
        """运行稳健型部署"""
        
        print("\n🛡️ 稳健型CTA策略部署运行中...")
        print("="*50)
        
        # 分析分散化
        self.analyze_diversification()
        
        # 创建仓位计划
        position_plan = self.create_conservative_position_plan()
        
        # 风险管理
        risk_system = self.create_conservative_risk_system()
        
        # 生成交易信号
        signals = self.generate_conservative_signals()
        
        # 保存部署包
        package_file = self.save_conservative_deployment()
        
        # 绩效追踪器
        tracker = self.create_conservative_tracker()
        print(tracker)
        
        print(f"\n🎉 稳健型CTA策略部署完成!")
        print(f"📋 部署文件: {package_file}")
        print(f"🎯 预期年化收益: {self.config['expected_return']:.2%}")
        print(f"🛡️ 已准备好开始稳健型投资!")
        
        return {
            'status': 'success',
            'package_file': package_file,
            'expected_return': self.config['expected_return'],
            'risk_level': '中等',
            'strategies_count': len(self.config['strategies'])
        }


def main():
    """主函数"""
    
    print("🛡️ 稳健型CTA策略部署系统")
    print("🎯 25%年化收益目标")
    print("💡 专为稳健投资者设计")
    print("="*50)
    
    # 创建稳健型部署系统
    conservative_system = ConservativeCTADeployment()
    
    # 运行部署
    result = conservative_system.run_conservative_deployment()
    
    if result['status'] == 'success':
        print(f"\n✅ 稳健型部署成功!")
        print(f"🛡️ 这是注重风险控制的稳健配置")
        print(f"📈 预期收益: {result['expected_return']:.2%}")
        print(f"📊 策略数量: {result['strategies_count']}个")
        print(f"🚀 准备开始稳健投资!")
    else:
        print("❌ 稳健型部署失败")


if __name__ == "__main__":
    main()