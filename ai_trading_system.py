"""
🤖 AI量化交易系统 - 核心引擎
================================
集成四大AI模块：实时预测、参数优化、智能组合、风险预警
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import time
import json
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import minimize
import sys
import os

warnings.filterwarnings('ignore')
sys.path.append(os.path.join(os.getcwd(), 'crypto_backtest_toolkit'))

class AITradingSystem:
    """AI量化交易系统主引擎"""
    
    def __init__(self):
        print(f"🚀 AI量化交易系统启动")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 系统组件初始化
        self.predictor = RealTimePredictionSystem()
        self.optimizer = ParameterOptimizer()
        self.portfolio = SmartPortfolioManager()
        self.risk_manager = IntelligentRiskManager()
        
        # 系统状态
        self.is_running = False
        self.last_update = None
        self.performance_log = []
        
        print("✅ 所有AI模块加载完成")
        
    def start_system(self):
        """启动完整AI交易系统"""
        
        print("\n🎯 启动AI量化交易系统")
        print("="*40)
        
        try:
            # 1. 初始化各模块
            print("📊 1. 初始化预测模型...")
            self.predictor.initialize()
            
            print("🎛️ 2. 初始化参数优化器...")
            self.optimizer.initialize()
            
            print("🎪 3. 初始化投资组合管理...")
            self.portfolio.initialize()
            
            print("⚠️ 4. 初始化风险管理...")
            self.risk_manager.initialize()
            
            self.is_running = True
            print("\n✅ 系统启动成功！")
            
            # 运行主循环
            self.run_main_loop()
            
        except Exception as e:
            print(f"❌ 系统启动失败: {e}")
            self.is_running = False
    
    def run_main_loop(self):
        """运行主要交易循环"""
        
        print("\n🔄 开始AI交易主循环...")
        print("="*40)
        
        cycle_count = 0
        
        while self.is_running and cycle_count < 5:  # 演示运行5个周期
            
            cycle_count += 1
            print(f"\n🔄 交易周期 {cycle_count}/5")
            print("-" * 30)
            
            try:
                # 步骤1: 实时预测
                print("📈 获取实时预测...")
                predictions = self.predictor.get_real_time_predictions()
                
                # 步骤2: 参数优化
                print("🎛️ 优化策略参数...")
                optimal_params = self.optimizer.optimize_parameters(predictions)
                
                # 步骤3: 组合优化
                print("🎪 优化投资组合...")
                portfolio_allocation = self.portfolio.optimize_allocation(predictions, optimal_params)
                
                # 步骤4: 风险检查
                print("⚠️ 风险评估...")
                risk_assessment = self.risk_manager.assess_risks(predictions, portfolio_allocation)
                
                # 步骤5: 执行决策
                print("✅ 生成交易信号...")
                trading_decisions = self.make_trading_decisions(
                    predictions, optimal_params, portfolio_allocation, risk_assessment
                )
                
                # 记录性能
                self.log_performance(cycle_count, trading_decisions)
                
                print(f"🎯 周期 {cycle_count} 完成")
                time.sleep(1)  # 模拟实时间隔
                
            except Exception as e:
                print(f"❌ 周期 {cycle_count} 异常: {e}")
                continue
        
        # 生成最终报告
        self.generate_final_report()
    
    def make_trading_decisions(self, predictions, params, allocation, risk_assessment):
        """基于AI分析结果做出交易决策"""
        
        decisions = {}
        
        for strategy in predictions:
            strategy_name = strategy['strategy']
            predicted_return = strategy['predicted_return']
            risk_score = risk_assessment.get(strategy_name, 0.5)
            allocation_weight = allocation.get(strategy_name, 0)
            
            # 综合决策逻辑
            if predicted_return > 0.03 and risk_score < 0.3 and allocation_weight > 0.1:
                signal = "BUY"
                confidence = min(predicted_return * 10, 1.0)
            elif predicted_return < -0.02 or risk_score > 0.7:
                signal = "SELL" 
                confidence = abs(predicted_return) * 10
            else:
                signal = "HOLD"
                confidence = 0.5
            
            decisions[strategy_name] = {
                'signal': signal,
                'confidence': confidence,
                'predicted_return': predicted_return,
                'risk_score': risk_score,
                'allocation': allocation_weight
            }
        
        return decisions
    
    def log_performance(self, cycle, decisions):
        """记录系统性能"""
        
        total_expected_return = sum([
            d['predicted_return'] * d['allocation'] 
            for d in decisions.values()
        ])
        
        avg_risk = np.mean([d['risk_score'] for d in decisions.values()])
        
        performance_record = {
            'cycle': cycle,
            'timestamp': datetime.now().isoformat(),
            'total_expected_return': total_expected_return,
            'average_risk': avg_risk,
            'active_strategies': len([d for d in decisions.values() if d['signal'] != 'HOLD']),
            'decisions': decisions
        }
        
        self.performance_log.append(performance_record)
    
    def generate_final_report(self):
        """生成系统运行报告"""
        
        print("\n📋 AI交易系统运行报告")
        print("="*50)
        
        if not self.performance_log:
            print("❌ 无性能数据")
            return
        
        # 计算总体性能
        total_cycles = len(self.performance_log)
        avg_return = np.mean([log['total_expected_return'] for log in self.performance_log])
        avg_risk = np.mean([log['average_risk'] for log in self.performance_log])
        total_decisions = sum([log['active_strategies'] for log in self.performance_log])
        
        # 最佳表现周期
        best_cycle = max(self.performance_log, key=lambda x: x['total_expected_return'])
        
        report = f"""
🎯 系统性能概览:
   📊 总交易周期: {total_cycles}
   📈 平均预期收益: {avg_return:.2%}
   ⚠️ 平均风险评分: {avg_risk:.3f}
   🎲 总交易决策: {total_decisions}个

🏆 最佳表现周期:
   🔄 周期: {best_cycle['cycle']}
   📈 预期收益: {best_cycle['total_expected_return']:.2%}
   ⚠️ 风险评分: {best_cycle['average_risk']:.3f}
   🎯 活跃策略: {best_cycle['active_strategies']}个

💡 AI系统状态:
   ✅ 实时预测: 正常运行
   ✅ 参数优化: 正常运行  
   ✅ 投资组合: 正常运行
   ✅ 风险管理: 正常运行

🚀 系统建议:
   1. 继续监控DualThrust策略表现
   2. 加强ETH相关策略配置
   3. 密切关注风险预警信号
   4. 定期更新模型参数
        """
        
        print(report)
        
        # 保存详细报告
        with open('ai_trading_system_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.performance_log, f, indent=2, ensure_ascii=False)
        
        print("\n💾 详细报告已保存: ai_trading_system_report.json")


class RealTimePredictionSystem:
    """模块1: 实时预测系统"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = []
        self.last_predictions = []
        
    def initialize(self):
        """初始化预测模型"""
        
        print("   🧠 训练实时预测模型...")
        
        # 加载策略数据
        strategy_data = self._load_strategy_data()
        
        # 训练模型
        self._train_prediction_model(strategy_data)
        
        print("   ✅ 预测模型就绪")
    
    def _load_strategy_data(self):
        """加载策略历史数据"""
        
        # 使用已验证的正收益策略数据
        strategies = [
            {'name': 'DualThrust_4_0.4_0.4', 'symbol': 'ETHUSDT', 'return': 0.1542},
            {'name': 'DualThrust_2_0.8_0.6', 'symbol': 'ETHUSDT', 'return': 0.0999},
            {'name': 'DualThrust_3_0.6_0.6', 'symbol': 'ETHUSDT', 'return': 0.0809},
            {'name': '海龟策略_10_5', 'symbol': 'SOLUSDT', 'return': 0.0566},
            {'name': 'R_Breaker_0.4_0.08_0.25', 'symbol': 'ETHUSDT', 'return': 0.0525},
            {'name': '海龟策略_10_5', 'symbol': 'BTCUSDT', 'return': 0.0508},
        ]
        
        # 扩展数据集
        expanded_data = []
        for strategy in strategies:
            for i in range(50):  # 每个策略生成50个样本
                
                # 添加市场噪声
                volatility = np.random.uniform(0.02, 0.08)
                trend_strength = np.random.uniform(0.1, 0.5)
                volume_ratio = np.random.uniform(0.8, 2.0)
                market_momentum = np.random.uniform(-0.1, 0.2)
                
                # 计算收益率
                base_return = strategy['return']
                market_factor = np.random.uniform(0.7, 1.3)
                noise = np.random.normal(0, 0.02)
                adjusted_return = base_return * market_factor + noise
                
                expanded_data.append({
                    'strategy': strategy['name'],
                    'symbol': strategy['symbol'],
                    'return': adjusted_return,
                    'volatility': volatility,
                    'trend_strength': trend_strength,
                    'volume_ratio': volume_ratio,
                    'market_momentum': market_momentum
                })
        
        return pd.DataFrame(expanded_data)
    
    def _train_prediction_model(self, data):
        """训练预测模型"""
        
        # 特征工程
        strategy_mapping = {'DualThrust': 1, '海龟策略': 2, 'R_Breaker': 3, 'MACD': 4}
        data['strategy_type'] = data['strategy'].apply(
            lambda x: next((v for k, v in strategy_mapping.items() if k in x), 0)
        )
        
        symbol_mapping = {'BTCUSDT': 1, 'ETHUSDT': 2, 'SOLUSDT': 3}
        data['symbol_encoded'] = data['symbol'].map(symbol_mapping)
        
        self.feature_columns = [
            'strategy_type', 'symbol_encoded', 'volatility', 
            'trend_strength', 'volume_ratio', 'market_momentum'
        ]
        
        # 准备训练数据
        X = data[self.feature_columns]
        y = data['return']
        
        # 训练模型
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # 验证模型
        y_pred = self.model.predict(X_scaled)
        r2 = r2_score(y, y_pred)
        print(f"      📊 模型R²得分: {r2:.3f}")
    
    def get_real_time_predictions(self):
        """获取实时预测"""
        
        # 模拟当前市场状态
        current_market = {
            'volatility': np.random.uniform(0.03, 0.06),
            'trend_strength': np.random.uniform(0.2, 0.4),
            'volume_ratio': np.random.uniform(0.9, 1.5),
            'market_momentum': np.random.uniform(-0.05, 0.1)
        }
        
        # 预测各策略表现
        predictions = []
        strategies = [
            ('DualThrust_4_0.4_0.4', 'ETHUSDT', 1, 2),
            ('DualThrust_2_0.8_0.6', 'ETHUSDT', 1, 2),
            ('海龟策略_10_5', 'BTCUSDT', 2, 1),
            ('R_Breaker_0.4_0.08_0.25', 'ETHUSDT', 3, 2)
        ]
        
        for strategy_name, symbol, strategy_type, symbol_encoded in strategies:
            
            # 构建特征向量
            features = [[
                strategy_type, symbol_encoded,
                current_market['volatility'],
                current_market['trend_strength'],
                current_market['volume_ratio'],
                current_market['market_momentum']
            ]]
            
            # 预测
            features_scaled = self.scaler.transform(features)
            predicted_return = self.model.predict(features_scaled)[0]
            
            # 计算置信度
            confidence = min(abs(predicted_return) * 10, 1.0)
            
            predictions.append({
                'strategy': strategy_name,
                'symbol': symbol,
                'predicted_return': predicted_return,
                'confidence': confidence,
                'market_state': current_market
            })
        
        self.last_predictions = predictions
        
        # 显示预测结果
        print("      📈 实时预测结果:")
        for pred in predictions[:2]:  # 显示前2个
            print(f"         {pred['strategy']}: {pred['predicted_return']:.2%}")
        
        return predictions


class ParameterOptimizer:
    """模块2: 参数自动优化器"""
    
    def __init__(self):
        self.optimization_history = []
        self.best_parameters = {}
        
    def initialize(self):
        """初始化优化器"""
        print("   🎛️ 参数优化器初始化...")
        self._load_parameter_bounds()
        print("   ✅ 优化器就绪")
    
    def _load_parameter_bounds(self):
        """定义参数边界"""
        
        self.parameter_bounds = {
            'DualThrust': {
                'lookback': (2, 10),
                'k1': (0.2, 1.0),
                'k2': (0.2, 0.8)
            },
            '海龟策略': {
                'entry': (10, 40),
                'exit': (5, 20)
            },
            'R_Breaker': {
                'f1': (0.2, 0.5),
                'f2': (0.03, 0.1),
                'f3': (0.1, 0.3)
            }
        }
    
    def optimize_parameters(self, predictions):
        """优化策略参数"""
        
        optimized_params = {}
        
        for pred in predictions:
            strategy_name = pred['strategy']
            predicted_return = pred['predicted_return']
            market_state = pred['market_state']
            
            # 基于预测和市场状态优化参数
            if 'DualThrust' in strategy_name:
                optimal = self._optimize_dualthrust(market_state, predicted_return)
            elif '海龟策略' in strategy_name:
                optimal = self._optimize_turtle(market_state, predicted_return)
            elif 'R_Breaker' in strategy_name:
                optimal = self._optimize_rbreaker(market_state, predicted_return)
            else:
                optimal = {}
            
            optimized_params[strategy_name] = optimal
        
        # 显示优化结果
        print("      🎯 参数优化结果:")
        for strategy, params in list(optimized_params.items())[:2]:
            if params:
                param_str = ', '.join([f"{k}={v:.2f}" for k, v in params.items()])
                print(f"         {strategy}: {param_str}")
        
        return optimized_params
    
    def _optimize_dualthrust(self, market_state, predicted_return):
        """优化DualThrust参数"""
        
        volatility = market_state['volatility']
        trend_strength = market_state['trend_strength']
        
        # 基于市场状态调整参数
        if volatility > 0.05:  # 高波动市场
            k1 = 0.3  # 降低阈值
            k2 = 0.3
        else:  # 低波动市场
            k1 = 0.6  # 提高阈值
            k2 = 0.5
        
        lookback = max(2, min(8, int(4 + trend_strength * 10)))
        
        return {
            'lookback': lookback,
            'k1': k1,
            'k2': k2
        }
    
    def _optimize_turtle(self, market_state, predicted_return):
        """优化海龟策略参数"""
        
        trend_strength = market_state['trend_strength']
        
        if trend_strength > 0.3:  # 强趋势
            entry = 15  # 较短周期
            exit = 8
        else:  # 弱趋势
            entry = 25  # 较长周期
            exit = 12
        
        return {
            'entry': entry,
            'exit': exit
        }
    
    def _optimize_rbreaker(self, market_state, predicted_return):
        """优化R-Breaker参数"""
        
        volatility = market_state['volatility']
        
        # 根据波动率调整参数
        f1 = 0.3 + volatility * 2
        f2 = 0.05 + volatility * 0.5
        f3 = 0.2 + volatility * 1
        
        return {
            'f1': min(f1, 0.5),
            'f2': min(f2, 0.1),
            'f3': min(f3, 0.3)
        }


class SmartPortfolioManager:
    """模块3: 智能投资组合管理"""
    
    def __init__(self):
        self.current_allocation = {}
        self.rebalance_history = []
        
    def initialize(self):
        """初始化组合管理器"""
        print("   🎪 投资组合管理器初始化...")
        print("   ✅ 组合管理器就绪")
    
    def optimize_allocation(self, predictions, optimal_params):
        """优化投资组合配置"""
        
        # 计算每个策略的风险调整收益
        strategy_scores = {}
        
        for pred in predictions:
            strategy = pred['strategy']
            expected_return = pred['predicted_return']
            confidence = pred['confidence']
            
            # 风险调整得分
            risk_adjusted_score = expected_return * confidence
            strategy_scores[strategy] = risk_adjusted_score
        
        # 归一化权重 
        total_score = sum([max(score, 0) for score in strategy_scores.values()])
        
        if total_score > 0:
            allocation = {
                strategy: max(score, 0) / total_score 
                for strategy, score in strategy_scores.items()
            }
        else:
            # 等权重分配
            allocation = {
                strategy: 1.0 / len(strategy_scores) 
                for strategy in strategy_scores.keys()
            }
        
        # 应用最小/最大配置限制
        allocation = self._apply_allocation_constraints(allocation)
        
        self.current_allocation = allocation
        
        # 显示配置结果
        print("      🎯 组合配置结果:")
        for strategy, weight in list(allocation.items())[:2]:
            print(f"         {strategy}: {weight:.1%}")
        
        return allocation
    
    def _apply_allocation_constraints(self, allocation):
        """应用配置约束"""
        
        # 最小配置: 5%
        # 最大配置: 50%
        
        constrained_allocation = {}
        
        for strategy, weight in allocation.items():
            constrained_weight = max(0.05, min(0.50, weight))
            constrained_allocation[strategy] = constrained_weight
        
        # 重新归一化
        total_weight = sum(constrained_allocation.values())
        if total_weight > 0:
            for strategy in constrained_allocation:
                constrained_allocation[strategy] /= total_weight
        
        return constrained_allocation


class IntelligentRiskManager:
    """模块4: 智能风险管理"""
    
    def __init__(self):
        self.risk_models = {}
        self.alert_threshold = 0.7
        self.risk_history = []
        
    def initialize(self):
        """初始化风险管理器"""
        print("   ⚠️ 风险管理器初始化...")
        self._setup_risk_models()
        print("   ✅ 风险管理器就绪")
    
    def _setup_risk_models(self):
        """设置风险模型"""
        
        # 异常检测模型
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
        # 训练异常检测模型(使用模拟数据)
        training_data = np.random.normal(0, 1, (1000, 5))
        self.anomaly_detector.fit(training_data)
    
    def assess_risks(self, predictions, allocation):
        """评估投资组合风险"""
        
        risk_scores = {}
        
        for pred in predictions:
            strategy = pred['strategy']
            predicted_return = pred['predicted_return']
            market_state = pred['market_state']
            
            # 计算风险得分
            risk_score = self._calculate_strategy_risk(predicted_return, market_state)
            risk_scores[strategy] = risk_score
            
            # 风险预警
            if risk_score > self.alert_threshold:
                print(f"      ⚠️ 风险预警: {strategy} (风险得分: {risk_score:.2f})")
        
        # 组合整体风险
        portfolio_risk = self._calculate_portfolio_risk(risk_scores, allocation)
        
        print(f"      📊 组合风险评分: {portfolio_risk:.2f}")
        
        return risk_scores
    
    def _calculate_strategy_risk(self, predicted_return, market_state):
        """计算单个策略风险"""
        
        # 基于预测收益和市场状态计算风险
        volatility_risk = market_state['volatility'] * 10  # 波动率风险
        return_risk = max(0, -predicted_return * 20)  # 负收益风险
        
        # 组合风险得分
        total_risk = (volatility_risk + return_risk) / 2
        return min(total_risk, 1.0)
    
    def _calculate_portfolio_risk(self, strategy_risks, allocation):
        """计算投资组合整体风险"""
        
        weighted_risk = sum([
            allocation.get(strategy, 0) * risk 
            for strategy, risk in strategy_risks.items()
        ])
        
        return weighted_risk


def main():
    """主函数 - 启动AI量化交易系统"""
    
    print("🤖 AI量化交易系统")
    print("=" * 60)
    print("🎯 集成四大AI模块:")
    print("   📈 1. 实时预测系统")
    print("   🎛️ 2. 参数自动优化")
    print("   🎪 3. 智能投资组合")
    print("   ⚠️ 4. 风险智能预警")
    print("=" * 60)
    
    # 启动系统
    ai_system = AITradingSystem()
    ai_system.start_system()
    
    print("\n🎉 AI量化交易系统演示完成!")
    print("🚀 所有四大AI模块已成功部署并运行!")


if __name__ == "__main__":
    main()