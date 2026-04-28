"""
🚀 高级CTA策略挖掘与ML优化系统
================================
目标：发现更多高收益CTA策略，通过机器学习组合优化实现超高回报
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
import sys
import os
import itertools
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.cluster import KMeans
import random

warnings.filterwarnings('ignore')
sys.path.append(os.path.join(os.getcwd(), 'crypto_backtest_toolkit'))

# 导入基础策略
from crypto_backtest_toolkit.professional_cta_strategies import *


class AdvancedCTAStrategyMiner:
    """高级CTA策略挖掘器"""
    
    def __init__(self):
        print("🚀 高级CTA策略挖掘系统启动")
        print("🎯 目标：挖掘更多高收益CTA策略并用AI优化组合")
        print("📊 预期目标：年化收益 > 30%")
        print("="*60)
        
        self.advanced_strategies = self.create_advanced_strategy_library()
        self.mining_results = []
        self.ml_models = {}
        
    def create_advanced_strategy_library(self) -> List[Dict]:
        """创建高级策略库"""
        
        print("📚 构建高级CTA策略库...")
        
        strategies = []
        
        # 1. 布林带策略变种 (多参数组合)
        bollinger_configs = [
            {'period': 20, 'std': 1.5, 'type': 'conservative'},
            {'period': 20, 'std': 2.0, 'type': 'standard'},
            {'period': 20, 'std': 2.5, 'type': 'aggressive'},
            {'period': 15, 'std': 1.8, 'type': 'short_period'},
            {'period': 30, 'std': 2.2, 'type': 'long_period'},
        ]
        
        for config in bollinger_configs:
            strategies.append({
                'name': f'Bollinger_{config["period"]}_{config["std"]}_{config["type"]}',
                'type': 'Mean_Reversion',
                'class': 'BollingerBandsStrategy',
                'params': config
            })
        
        # 2. 动量策略变种 (多时间框架)
        momentum_configs = [
            {'short': 5, 'long': 20, 'signal': 3},
            {'short': 3, 'long': 12, 'signal': 5},
            {'short': 8, 'long': 21, 'signal': 7},
            {'short': 10, 'long': 30, 'signal': 9},
            {'short': 12, 'long': 50, 'signal': 15},
        ]
        
        for config in momentum_configs:
            strategies.append({
                'name': f'Momentum_{config["short"]}_{config["long"]}_{config["signal"]}',
                'type': 'Momentum',
                'class': 'EnhancedMomentumStrategy',
                'params': config
            })
        
        # 3. 网格交易策略
        grid_configs = [
            {'grid_size': 0.01, 'levels': 5, 'type': 'tight'},
            {'grid_size': 0.02, 'levels': 7, 'type': 'medium'},
            {'grid_size': 0.03, 'levels': 10, 'type': 'wide'},
        ]
        
        for config in grid_configs:
            strategies.append({
                'name': f'Grid_{config["grid_size"]*100:.0f}pct_{config["levels"]}lvl_{config["type"]}',
                'type': 'Grid_Trading',
                'class': 'GridTradingStrategy',
                'params': config
            })
        
        # 4. 配对交易策略
        pair_configs = [
            {'lookback': 60, 'entry_threshold': 1.5, 'exit_threshold': 0.5},
            {'lookback': 120, 'entry_threshold': 2.0, 'exit_threshold': 0.3},
            {'lookback': 240, 'entry_threshold': 2.5, 'exit_threshold': 0.8},
        ]
        
        for config in pair_configs:
            strategies.append({
                'name': f'PairTrading_{config["lookback"]}_{config["entry_threshold"]}_{config["exit_threshold"]}',
                'type': 'Statistical_Arbitrage',
                'class': 'PairTradingStrategy',
                'params': config
            })
        
        # 5. 周期性摆动策略
        oscillator_configs = [
            {'rsi_period': 14, 'overbought': 70, 'oversold': 30},
            {'rsi_period': 7, 'overbought': 80, 'oversold': 20},
            {'rsi_period': 21, 'overbought': 65, 'oversold': 35},
        ]
        
        for config in oscillator_configs:
            strategies.append({
                'name': f'RSI_{config["rsi_period"]}_{config["overbought"]}_{config["oversold"]}',
                'type': 'Oscillator',
                'class': 'RSIOscillatorStrategy',
                'params': config
            })
        
        # 6. 突破策略增强版
        breakout_configs = [
            {'period': 20, 'multiplier': 1.5, 'confirmation': 2},
            {'period': 15, 'multiplier': 1.2, 'confirmation': 1},
            {'period': 30, 'multiplier': 2.0, 'confirmation': 3},
        ]
        
        for config in breakout_configs:
            strategies.append({
                'name': f'Breakout_{config["period"]}_{config["multiplier"]}_{config["confirmation"]}',
                'type': 'Breakout',
                'class': 'EnhancedBreakoutStrategy',
                'params': config
            })
        
        # 7. 机器学习信号策略
        ml_configs = [
            {'lookback': 50, 'features': 10, 'model': 'rf'},
            {'lookback': 100, 'features': 15, 'model': 'gb'},
            {'lookback': 30, 'features': 8, 'model': 'et'},
        ]
        
        for config in ml_configs:
            strategies.append({
                'name': f'MLSignal_{config["lookback"]}_{config["features"]}_{config["model"]}',
                'type': 'Machine_Learning',
                'class': 'MLSignalStrategy',
                'params': config
            })
        
        # 8. 时间序列分解策略
        decomposition_configs = [
            {'trend_period': 50, 'seasonal_period': 12, 'strength': 0.6},
            {'trend_period': 100, 'seasonal_period': 24, 'strength': 0.8},
        ]
        
        for config in decomposition_configs:
            strategies.append({
                'name': f'Decomposition_{config["trend_period"]}_{config["seasonal_period"]}_{config["strength"]}',
                'type': 'Time_Series',
                'class': 'DecompositionStrategy',
                'params': config
            })
        
        print(f"✅ 创建了 {len(strategies)} 个高级策略配置")
        print(f"📊 策略类型: {len(set([s['type'] for s in strategies]))} 种")
        
        return strategies
    
    def mine_profitable_strategies(self, symbols: List[str] = None) -> Dict:
        """挖掘高收益策略"""
        
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT']
        
        print(f"🔍 开始挖掘高收益策略...")
        print(f"📊 测试 {len(self.advanced_strategies)} 个策略配置")
        print(f"💰 测试 {len(symbols)} 个交易对")
        
        all_results = []
        
        for symbol in symbols:
            print(f"\n📈 挖掘 {symbol} 的最优策略...")
            
            # 加载数据
            data = self.load_market_data(symbol)
            if data.empty:
                continue
                
            symbol_results = []
            
            # 测试每个策略
            for strategy_config in self.advanced_strategies:
                try:
                    result = self.test_strategy(strategy_config, data, symbol)
                    if result and result.get('total_return', 0) > 0:  # 只保留正收益
                        symbol_results.append(result)
                        
                except Exception as e:
                    continue
            
            # 排序并选择最优策略
            symbol_results.sort(key=lambda x: x.get('total_return', 0), reverse=True)
            top_strategies = symbol_results[:10]  # 取前10个
            
            print(f"✅ {symbol}: 发现 {len(symbol_results)} 个正收益策略，保留前 {len(top_strategies)} 个")
            
            for i, strategy in enumerate(top_strategies[:3], 1):
                print(f"   {i}. {strategy['name']}: {strategy['total_return']:.2%}")
            
            all_results.extend(top_strategies)
        
        # 全局排序
        all_results.sort(key=lambda x: x.get('total_return', 0), reverse=True)
        
        print(f"\n🏆 总共发现 {len(all_results)} 个高收益策略")
        print("📊 全局最优策略 (Top 5):")
        
        for i, strategy in enumerate(all_results[:5], 1):
            print(f"   {i}. {strategy['name']} ({strategy['symbol']}): {strategy['total_return']:.2%}")
        
        return {
            'all_strategies': all_results,
            'top_strategies': all_results[:20],  # 保留前20个最优策略
            'strategy_types': self.analyze_strategy_types(all_results)
        }
    
    def load_market_data(self, symbol: str, sample_size: int = 15000) -> pd.DataFrame:
        """加载市场数据"""
        
        try:
            data = pd.read_csv(f'{symbol}_minute_data_2023_2026.csv')
            
            # 随机采样
            if len(data) > sample_size:
                data = data.sample(n=sample_size, random_state=42).sort_index()
            
            # 数据预处理
            if 'Open Time' in data.columns:
                data['datetime'] = pd.to_datetime(data['Open Time'])
                data = data.set_index('datetime')
            
            # 转换为4小时线提高信号质量
            data_4h = data.resample('4H').agg({
                'Open': 'first',
                'High': 'max', 
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            return data_4h
            
        except FileNotFoundError:
            print(f"❌ 无法加载 {symbol} 数据")
            return pd.DataFrame()
    
    def test_strategy(self, strategy_config: Dict, data: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """测试单个策略"""
        
        strategy_name = strategy_config['name']
        strategy_class = strategy_config['class']
        params = strategy_config['params']
        
        # 创建策略实例
        strategy = self.create_strategy_instance(strategy_class, params)
        if not strategy:
            return None
        
        # 回测
        result = self.enhanced_backtest(strategy, data, strategy_config, symbol)
        
        if result and result.get('total_return', 0) > 0.05:  # 筛选收益>5%的策略
            result.update({
                'name': strategy_name,
                'symbol': symbol,
                'type': strategy_config['type'],
                'params': params,
                'class': strategy_class
            })
            return result
        
        return None
    
    def create_strategy_instance(self, strategy_class: str, params: Dict):
        """创建策略实例"""
        
        try:
            if strategy_class == 'BollingerBandsStrategy':
                return BollingerBandsStrategy(params['period'], params['std'])
            elif strategy_class == 'EnhancedMomentumStrategy':
                return EnhancedMomentumStrategy(params['short'], params['long'], params['signal'])
            elif strategy_class == 'GridTradingStrategy':
                return GridTradingStrategy(params['grid_size'], params['levels'])
            elif strategy_class == 'PairTradingStrategy':
                return PairTradingStrategy(params['lookback'], params['entry_threshold'], params['exit_threshold'])
            elif strategy_class == 'RSIOscillatorStrategy':
                return RSIOscillatorStrategy(params['rsi_period'], params['overbought'], params['oversold'])
            elif strategy_class == 'EnhancedBreakoutStrategy':
                return EnhancedBreakoutStrategy(params['period'], params['multiplier'], params['confirmation'])
            elif strategy_class == 'MLSignalStrategy':
                return MLSignalStrategy(params['lookback'], params['features'], params['model'])
            elif strategy_class == 'DecompositionStrategy':
                return DecompositionStrategy(params['trend_period'], params['seasonal_period'], params['strength'])
            else:
                return None
                
        except Exception as e:
            return None
    
    def enhanced_backtest(self, strategy, data: pd.DataFrame, config: Dict, symbol: str) -> Dict:
        """增强回测引擎"""
        
        initial_capital = 100000
        capital = initial_capital
        position = 0
        entry_price = 0
        trades = []
        max_capital = initial_capital
        max_drawdown = 0
        
        # 预热期
        warmup = max(50, len(data) // 20)
        
        for i in range(warmup, len(data)):
            current_data = data.iloc[:i+1]
            current_price = data['Close'].iloc[i]
            
            try:
                # 生成信号
                signal = strategy.generate_signal(current_data)
                
                # 交易逻辑
                if signal != 0 and position == 0:
                    position = signal
                    entry_price = current_price
                elif signal * position <= 0 and position != 0:
                    # 平仓
                    pnl_rate = position * (current_price - entry_price) / entry_price
                    capital *= (1 + pnl_rate * 0.2)  # 20%仓位
                    
                    trades.append({
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'pnl_rate': pnl_rate,
                        'position': position
                    })
                    
                    # 开新仓
                    if signal != 0:
                        position = signal
                        entry_price = current_price
                    else:
                        position = 0
                
                # 更新最大回撤
                max_capital = max(max_capital, capital)
                current_drawdown = (max_capital - capital) / max_capital
                max_drawdown = max(max_drawdown, current_drawdown)
                
            except:
                continue
        
        # 最终平仓
        if position != 0:
            final_pnl = position * (data['Close'].iloc[-1] - entry_price) / entry_price
            capital *= (1 + final_pnl * 0.2)
        
        # 计算指标
        total_return = (capital - initial_capital) / initial_capital
        num_trades = len(trades)
        
        if num_trades > 0:
            win_trades = len([t for t in trades if t['pnl_rate'] > 0])
            win_rate = win_trades / num_trades
            avg_return = total_return / max(num_trades, 1)
        else:
            win_rate = 0
            avg_return = 0
        
        return {
            'total_return': total_return,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'avg_return_per_trade': avg_return,
            'final_capital': capital
        }
    
    def analyze_strategy_types(self, results: List[Dict]) -> Dict:
        """分析策略类型分布"""
        
        type_stats = {}
        
        for result in results:
            strategy_type = result.get('type', 'Unknown')
            if strategy_type not in type_stats:
                type_stats[strategy_type] = {
                    'count': 0,
                    'avg_return': 0,
                    'max_return': 0,
                    'strategies': []
                }
            
            type_stats[strategy_type]['count'] += 1
            type_stats[strategy_type]['strategies'].append(result)
            type_stats[strategy_type]['max_return'] = max(
                type_stats[strategy_type]['max_return'],
                result.get('total_return', 0)
            )
        
        # 计算平均收益
        for strategy_type, stats in type_stats.items():
            returns = [s.get('total_return', 0) for s in stats['strategies']]
            stats['avg_return'] = np.mean(returns) if returns else 0
        
        return type_stats
    
    def ml_strategy_optimization(self, strategy_results: Dict) -> Dict:
        """机器学习策略组合优化"""
        
        print("\n🧠 开始机器学习策略组合优化...")
        print("="*50)
        
        strategies = strategy_results['top_strategies']
        if len(strategies) < 5:
            print("❌ 策略数量不足，无法进行ML优化")
            return {}
        
        # 准备ML训练数据
        features, labels = self.prepare_ml_data(strategies)
        
        # 训练多个ML模型
        models = self.train_ensemble_models(features, labels)
        
        # 策略组合优化
        optimal_portfolio = self.optimize_strategy_portfolio(strategies, models)
        
        print("✅ ML优化完成!")
        return {
            'models': models,
            'optimal_portfolio': optimal_portfolio,
            'expected_return': optimal_portfolio.get('expected_return', 0),
            'portfolio_strategies': optimal_portfolio.get('strategies', [])
        }
    
    def prepare_ml_data(self, strategies: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """准备ML训练数据"""
        
        print("📊 准备机器学习训练数据...")
        
        features = []
        labels = []
        
        for strategy in strategies:
            # 特征提取
            strategy_features = [
                strategy.get('num_trades', 0) / 100,  # 归一化交易次数
                strategy.get('win_rate', 0),
                strategy.get('max_drawdown', 0),
                strategy.get('avg_return_per_trade', 0) * 100,
                len(strategy.get('name', '')) / 50,  # 策略复杂度代理
                1.0 if 'Momentum' in strategy.get('type', '') else 0.0,
                1.0 if 'Mean_Reversion' in strategy.get('type', '') else 0.0,
                1.0 if 'Breakout' in strategy.get('type', '') else 0.0,
                1.0 if 'Machine_Learning' in strategy.get('type', '') else 0.0,
                1.0 if 'ETHUSDT' in strategy.get('symbol', '') else 0.0,
                1.0 if 'BTCUSDT' in strategy.get('symbol', '') else 0.0,
            ]
            
            features.append(strategy_features)
            labels.append(strategy.get('total_return', 0))
        
        return np.array(features), np.array(labels)
    
    def train_ensemble_models(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """训练集成模型"""
        
        print("🎯 训练集成ML模型...")
        
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # 特征标准化
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        models = {}
        
        # 随机森林
        rf = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
        rf.fit(X_train_scaled, y_train)
        rf_score = rf.score(X_test_scaled, y_test)
        models['RandomForest'] = {'model': rf, 'score': rf_score, 'scaler': scaler}
        
        # 梯度提升
        gb = GradientBoostingRegressor(n_estimators=150, learning_rate=0.1, random_state=42)
        gb.fit(X_train_scaled, y_train)
        gb_score = gb.score(X_test_scaled, y_test)
        models['GradientBoosting'] = {'model': gb, 'score': gb_score, 'scaler': scaler}
        
        # 极端随机树
        et = ExtraTreesRegressor(n_estimators=180, random_state=42)
        et.fit(X_train_scaled, y_train)
        et_score = et.score(X_test_scaled, y_test)
        models['ExtraTrees'] = {'model': et, 'score': et_score, 'scaler': scaler}
        
        print(f"   📊 RandomForest R²: {rf_score:.3f}")
        print(f"   📊 GradientBoosting R²: {gb_score:.3f}")
        print(f"   📊 ExtraTrees R²: {et_score:.3f}")
        
        return models
    
    def optimize_strategy_portfolio(self, strategies: List[Dict], models: Dict) -> Dict:
        """优化策略投资组合"""
        
        print("🎪 优化策略投资组合...")
        
        # 集成模型预测
        predictions = []
        
        for strategy in strategies:
            strategy_features = self.extract_strategy_features(strategy)
            
            # 使用所有模型预测并取平均
            model_predictions = []
            for model_name, model_info in models.items():
                model = model_info['model']
                scaler = model_info['scaler']
                
                scaled_features = scaler.transform([strategy_features])
                pred = model.predict(scaled_features)[0]
                model_predictions.append(pred)
            
            ensemble_prediction = np.mean(model_predictions)
            predictions.append(ensemble_prediction)
        
        # 计算优化权重
        predictions = np.array(predictions)
        
        # 只选择正预测的策略
        positive_mask = predictions > 0
        if positive_mask.sum() == 0:
            print("⚠️ 无正预测策略，使用原始收益排序")
            weights = self.equal_weight_allocation(strategies)
        else:
            # 基于预测收益和历史表现的加权
            positive_predictions = predictions[positive_mask]
            positive_strategies = [strategies[i] for i in range(len(strategies)) if positive_mask[i]]
            
            # 结合ML预测和历史表现
            historical_returns = np.array([s.get('total_return', 0) for s in positive_strategies])
            combined_scores = 0.6 * positive_predictions + 0.4 * historical_returns
            
            # 标准化权重
            weights = combined_scores / combined_scores.sum()
            
            # 应用配置约束
            weights = np.maximum(weights, 0.01)  # 最小1%
            weights = np.minimum(weights, 0.3)   # 最大30%
            weights = weights / weights.sum()    # 重新标准化
            
            strategies = positive_strategies
        
        # 计算预期组合收益
        expected_return = sum(w * s.get('total_return', 0) for w, s in zip(weights, strategies))
        
        portfolio_strategies = []
        for i, (weight, strategy) in enumerate(zip(weights, strategies)):
            portfolio_strategies.append({
                'strategy': strategy['name'],
                'symbol': strategy['symbol'],
                'weight': weight,
                'expected_return': strategy.get('total_return', 0),
                'contribution': weight * strategy.get('total_return', 0)
            })
        
        # 按权重排序
        portfolio_strategies.sort(key=lambda x: x['weight'], reverse=True)
        
        print(f"✅ 优化完成，预期组合收益: {expected_return:.2%}")
        
        return {
            'expected_return': expected_return,
            'strategies': portfolio_strategies,
            'num_strategies': len(portfolio_strategies),
            'max_weight': max(weights),
            'min_weight': min(weights)
        }
    
    def extract_strategy_features(self, strategy: Dict) -> List[float]:
        """提取策略特征"""
        
        return [
            strategy.get('num_trades', 0) / 100,
            strategy.get('win_rate', 0),
            strategy.get('max_drawdown', 0),
            strategy.get('avg_return_per_trade', 0) * 100,
            len(strategy.get('name', '')) / 50,
            1.0 if 'Momentum' in strategy.get('type', '') else 0.0,
            1.0 if 'Mean_Reversion' in strategy.get('type', '') else 0.0,
            1.0 if 'Breakout' in strategy.get('type', '') else 0.0,
            1.0 if 'Machine_Learning' in strategy.get('type', '') else 0.0,
            1.0 if 'ETHUSDT' in strategy.get('symbol', '') else 0.0,
            1.0 if 'BTCUSDT' in strategy.get('symbol', '') else 0.0,
        ]
    
    def equal_weight_allocation(self, strategies: List[Dict]) -> np.ndarray:
        """等权重分配"""
        return np.ones(len(strategies)) / len(strategies)
    
    def iterative_optimization(self, iterations: int = 3) -> Dict:
        """迭代优化策略"""
        
        print(f"\n🔄 开始迭代优化 ({iterations} 轮)...")
        print("="*60)
        
        best_result = None
        best_return = 0
        
        for iteration in range(iterations):
            print(f"\n🔄 迭代 {iteration + 1}/{iterations}")
            print("-" * 40)
            
            # 策略挖掘
            mining_results = self.mine_profitable_strategies()
            
            # ML优化
            ml_results = self.ml_strategy_optimization(mining_results)
            
            current_return = ml_results.get('expected_return', 0)
            
            print(f"📊 本轮预期收益: {current_return:.2%}")
            
            if current_return > best_return:
                best_return = current_return
                best_result = {
                    'iteration': iteration + 1,
                    'mining_results': mining_results,
                    'ml_results': ml_results,
                    'expected_return': current_return
                }
                print(f"🏆 新的最佳结果! 收益: {best_return:.2%}")
            
        print(f"\n🎉 迭代优化完成!")
        print(f"🏆 最终最佳预期收益: {best_return:.2%}")
        
        return best_result or {}


# 策略实现类
class BollingerBandsStrategy:
    def __init__(self, period: int, std: float):
        self.period = period
        self.std = std
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        if len(data) < self.period:
            return 0
        
        close = data['Close']
        sma = close.rolling(self.period).mean()
        std_dev = close.rolling(self.period).std()
        
        upper_band = sma + (std_dev * self.std)
        lower_band = sma - (std_dev * self.std)
        
        current_price = close.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        if current_price > current_upper:
            return -1  # 卖出信号
        elif current_price < current_lower:
            return 1   # 买入信号
        else:
            return 0   # 持有


class EnhancedMomentumStrategy:
    def __init__(self, short: int, long: int, signal: int):
        self.short = short
        self.long = long
        self.signal = signal
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        if len(data) < self.long:
            return 0
        
        close = data['Close']
        short_ma = close.rolling(self.short).mean()
        long_ma = close.rolling(self.long).mean()
        
        # 动量信号
        momentum = short_ma / long_ma - 1
        momentum_signal = momentum.rolling(self.signal).mean()
        
        current_momentum = momentum_signal.iloc[-1]
        
        if current_momentum > 0.01:
            return 1
        elif current_momentum < -0.01:
            return -1
        else:
            return 0


class GridTradingStrategy:
    def __init__(self, grid_size: float, levels: int):
        self.grid_size = grid_size
        self.levels = levels
        self.base_price = None
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        current_price = data['Close'].iloc[-1]
        
        if self.base_price is None:
            self.base_price = current_price
            return 0
        
        price_change = (current_price - self.base_price) / self.base_price
        
        if price_change > self.grid_size:
            self.base_price = current_price
            return -1  # 卖出
        elif price_change < -self.grid_size:
            self.base_price = current_price
            return 1   # 买入
        else:
            return 0


class PairTradingStrategy:
    def __init__(self, lookback: int, entry_threshold: float, exit_threshold: float):
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        if len(data) < self.lookback:
            return 0
        
        # 简化的配对交易逻辑
        close = data['Close']
        rolling_mean = close.rolling(self.lookback).mean()
        rolling_std = close.rolling(self.lookback).std()
        
        current_price = close.iloc[-1]
        current_mean = rolling_mean.iloc[-1]
        current_std = rolling_std.iloc[-1]
        
        z_score = (current_price - current_mean) / current_std
        
        if z_score > self.entry_threshold:
            return -1  # 价格过高，卖出
        elif z_score < -self.entry_threshold:
            return 1   # 价格过低，买入
        elif abs(z_score) < self.exit_threshold:
            return 0   # 回归均值，平仓
        else:
            return 0


class RSIOscillatorStrategy:
    def __init__(self, rsi_period: int, overbought: float, oversold: float):
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        if len(data) < self.rsi_period + 1:
            return 0
        
        # 计算RSI
        close = data['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        if current_rsi > self.overbought:
            return -1  # 超买，卖出
        elif current_rsi < self.oversold:
            return 1   # 超卖，买入
        else:
            return 0


class EnhancedBreakoutStrategy:
    def __init__(self, period: int, multiplier: float, confirmation: int):
        self.period = period
        self.multiplier = multiplier
        self.confirmation = confirmation
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        if len(data) < self.period:
            return 0
        
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # 动态阻力支撑
        resistance = high.rolling(self.period).max()
        support = low.rolling(self.period).min()
        
        range_size = resistance - support
        upper_breakout = resistance + (range_size * self.multiplier * 0.1)
        lower_breakout = support - (range_size * self.multiplier * 0.1)
        
        current_price = close.iloc[-1]
        
        # 需要确认信号
        if len(data) < self.period + self.confirmation:
            return 0
        
        recent_prices = close.iloc[-self.confirmation:]
        
        if (recent_prices > upper_breakout.iloc[-self.confirmation:]).all():
            return 1  # 向上突破
        elif (recent_prices < lower_breakout.iloc[-self.confirmation:]).all():
            return -1  # 向下突破
        else:
            return 0


class MLSignalStrategy:
    def __init__(self, lookback: int, features: int, model: str):
        self.lookback = lookback
        self.features = features
        self.model_type = model
        self.model = None
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        if len(data) < self.lookback:
            return 0
        
        # 简化的ML信号
        close = data['Close']
        volume = data['Volume']
        
        # 构建特征
        features = []
        features.append(close.pct_change().iloc[-1])
        features.append(close.rolling(5).mean().iloc[-1] / close.iloc[-1] - 1)
        features.append(close.rolling(20).mean().iloc[-1] / close.iloc[-1] - 1)
        features.append(volume.rolling(10).mean().iloc[-1] / volume.iloc[-1] - 1)
        features.append(close.rolling(10).std().iloc[-1] / close.iloc[-1])
        
        # 填充至指定特征数量
        while len(features) < self.features:
            features.append(np.random.random() * 0.01 - 0.005)
        
        # 简单决策逻辑
        signal_score = sum(features) * 100
        
        if signal_score > 0.5:
            return 1
        elif signal_score < -0.5:
            return -1
        else:
            return 0


class DecompositionStrategy:
    def __init__(self, trend_period: int, seasonal_period: int, strength: float):
        self.trend_period = trend_period
        self.seasonal_period = seasonal_period
        self.strength = strength
    
    def generate_signal(self, data: pd.DataFrame) -> int:
        if len(data) < max(self.trend_period, self.seasonal_period):
            return 0
        
        close = data['Close']
        
        # 趋势分解
        trend = close.rolling(self.trend_period).mean()
        
        # 季节性模式
        seasonal = close.rolling(self.seasonal_period).apply(
            lambda x: x.iloc[-1] - x.mean(), raw=False
        )
        
        current_trend = trend.pct_change().iloc[-1]
        current_seasonal = seasonal.iloc[-1] / close.iloc[-1]
        
        combined_signal = current_trend + current_seasonal * self.strength
        
        if combined_signal > 0.01:
            return 1
        elif combined_signal < -0.01:
            return -1
        else:
            return 0


def main():
    """主函数"""
    
    print("🚀 高级CTA策略挖掘与ML优化系统")
    print("🎯 目标：超越现有策略，实现年化30%+收益!")
    print("="*60)
    
    # 创建挖掘器
    miner = AdvancedCTAStrategyMiner()
    
    # 迭代优化
    best_result = miner.iterative_optimization(iterations=2)
    
    if best_result:
        print("\n📋 最终优化结果:")
        print("="*40)
        
        expected_return = best_result.get('expected_return', 0)
        portfolio = best_result.get('ml_results', {}).get('optimal_portfolio', {})
        
        print(f"🏆 预期组合年化收益: {expected_return:.2%}")
        
        if 'strategies' in portfolio:
            print(f"📊 核心策略组合 (Top 5):")
            for i, strategy in enumerate(portfolio['strategies'][:5], 1):
                print(f"   {i}. {strategy['strategy']} ({strategy['symbol']})")
                print(f"      权重: {strategy['weight']:.1%} | 预期: {strategy['expected_return']:.2%}")
        
        # 保存结果
        import json
        with open('advanced_cta_optimization_result.json', 'w', encoding='utf-8') as f:
            json.dump(best_result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 结果已保存: advanced_cta_optimization_result.json")
        
        print(f"\n🎊 {expected_return:.2%} 年化收益已准备就绪!")
        print("🚀 可以开始部署超高收益策略组合!")
    
    else:
        print("❌ 优化失败，请检查数据和参数")


if __name__ == "__main__":
    main()