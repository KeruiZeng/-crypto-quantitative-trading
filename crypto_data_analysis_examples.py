# 📊 加密货币数据分析 - 快速上手示例

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# ============================================================
# 💡 数据加载和基础处理
# ============================================================

def load_crypto_data(symbol='BTCUSDT'):
    """加载并预处理单个加密货币数据"""
    filename = f'{symbol}_minute_data_2023_2026.csv'
    
    # 读取数据
    df = pd.read_csv(filename)
    
    # 时间戳转换
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
    
    # 设置时间索引
    df.set_index('Open Time', inplace=True)
    
    # 添加实用字段
    df['Returns'] = df['Close'].pct_change()
    df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    df['Price_Range'] = df['High'] - df['Low']
    df['Body_Size'] = abs(df['Close'] - df['Open'])
    
    print(f"✅ {symbol} 数据加载完成")
    print(f"📅 时间范围: {df.index.min()} → {df.index.max()}")
    print(f"📊 记录总数: {len(df):,} 条")
    print(f"💰 价格区间: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
    print("-" * 50)
    
    return df

# ============================================================
# 📈 快速分析示例
# ============================================================

def quick_analysis():
    """15种货币的快速对比分析"""
    
    # 币种列表
    symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
        'XRPUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT',
        'LINKUSDT', 'UNIUSDT', 'LTCUSDT', 'BCHUSDT', 'ATOMUSDT'
    ]
    
    print("🔄 开始快速分析...")
    results = {}
    
    for symbol in symbols:
        try:
            # 加载数据
            df = load_crypto_data(symbol)
            
            # 计算关键指标
            results[symbol] = {
                'records': len(df),
                'start_price': df['Close'].iloc[0],
                'end_price': df['Close'].iloc[-1],
                'total_return': (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100,
                'volatility': df['Returns'].std() * np.sqrt(525600) * 100,  # 年化波动率
                'max_price': df['Close'].max(),
                'min_price': df['Close'].min(),
                'avg_volume': df['Volume'].mean()
            }
            
            print(f"✅ {symbol} 分析完成")
            
        except FileNotFoundError:
            print(f"❌ 文件未找到: {symbol}")
        except Exception as e:
            print(f"❌ {symbol} 处理错误: {e}")
    
    # 生成结果表格
    print("\n" + "="*80)
    print("📊 **15种加密货币汇总分析**")
    print("="*80)
    
    # 转换为DataFrame便于显示
    summary_df = pd.DataFrame.from_dict(results, orient='index')
    summary_df = summary_df.round(2)
    
    # 按总回报率排序
    summary_df = summary_df.sort_values('total_return', ascending=False)
    
    print(summary_df[['total_return', 'volatility', 'max_price', 'min_price']].to_string())
    
    return results, summary_df

# ============================================================
# 📊 可视化示例
# ============================================================

def plot_comparison(symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT']):
    """绘制多币种价格对比图"""
    
    plt.figure(figsize=(15, 10))
    
    for i, symbol in enumerate(symbols, 1):
        df = load_crypto_data(symbol)
        
        # 归一化处理 (以第一个价格为基准1)
        normalized_price = df['Close'] / df['Close'].iloc[0]
        
        plt.subplot(2, 2, i)
        plt.plot(normalized_price.index, normalized_price.values)
        plt.title(f'{symbol} 归一化价格走势')
        plt.ylabel('相对价格 (起始=1)')
        plt.grid(True)
        
        if i == len(symbols):
            # 最后一个子图显示所有币种对比
            plt.subplot(2, 2, 4)
            for sym in symbols:
                df_temp = load_crypto_data(sym)
                norm_temp = df_temp['Close'] / df_temp['Close'].iloc[0]
                plt.plot(norm_temp.index, norm_temp.values, label=sym.replace('USDT', ''))
            
            plt.title('多币种归一化对比')
            plt.ylabel('相对价格 (起始=1)')
            plt.legend()
            plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('crypto_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================
# 🎯 技术指标计算
# ============================================================

def calculate_indicators(symbol='BTCUSDT', save_result=False):
    """计算常用技术指标"""
    
    df = load_crypto_data(symbol)
    
    # RSI指标
    def calc_rsi(prices, window=14):
        deltas = prices.diff()
        gain = (deltas.where(deltas > 0, 0)).rolling(window=window).mean()
        loss = (-deltas.where(deltas < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    # 移动平均线
    df['MA_7'] = df['Close'].rolling(window=7*24*60).mean()    # 7日均线
    df['MA_30'] = df['Close'].rolling(window=30*24*60).mean()  # 30日均线
    
    # 布林带
    df['BB_Middle'] = df['Close'].rolling(window=20*24*60).mean()
    bb_std = df['Close'].rolling(window=20*24*60).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # RSI
    df['RSI'] = calc_rsi(df['Close'])
    
    # MACD
    exp1 = df['Close'].ewm(span=12*24*60).mean()
    exp2 = df['Close'].ewm(span=26*24*60).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9*24*60).mean()
    
    print(f"✅ {symbol} 技术指标计算完成")
    print(f"📊 新增字段: MA_7, MA_30, BB_Upper/Middle/Lower, RSI, MACD, MACD_Signal")
    
    if save_result:
        output_filename = f'{symbol}_with_indicators.csv'
        df.to_csv(output_filename)
        print(f"💾 结果已保存: {output_filename}")
    
    return df

# ============================================================
# 🚀 主执行示例
# ============================================================

if __name__ == "__main__":
    print("🎯 加密货币数据分析示例")
    print("="*50)
    
    print("\n1️⃣ 单币种数据加载示例:")
    btc_data = load_crypto_data('BTCUSDT')
    print(btc_data[['Open', 'High', 'Low', 'Close', 'Volume']].head())
    
    print("\n2️⃣ 批量分析示例:")
    # results, summary = quick_analysis()
    
    print("\n3️⃣ 技术指标示例:")
    # btc_with_indicators = calculate_indicators('BTCUSDT')
    
    print("\n4️⃣ 可视化示例:")
    # plot_comparison(['BTCUSDT', 'ETHUSDT', 'SOLUSDT'])
    
    print("\n✅ 示例完成！取消注释上述代码来执行完整分析")
    
    print("""
    📌 **后续分析建议**:
    1. 相关性分析: 计算币种间价格相关系数
    2. 波动率分析: 研究不同时期的市场波动特征  
    3. 交易策略回测: 使用backtest_framework进行策略验证
    4. 机器学习预测: 基于历史数据训练预测模型
    5. 风险管理分析: VaR计算和风险指标构建
    """)