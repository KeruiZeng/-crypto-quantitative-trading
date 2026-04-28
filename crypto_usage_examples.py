"""
使用示例：如何运行和使用加密货币数据收集器
"""

# 运行方式 1: 使用简化版收集器
print("🚀 方式1: 运行简化版收集器")
print("-" * 40)
print("python simple_crypto_collector.py")
print("python simple_crypto_collector.py check     # 检查现有文件")
print("python simple_crypto_collector.py overview  # 查看数据概况")

# 运行方式 2: 使用完整版收集器
print("\n🔧 方式2: 运行完整版收集器")
print("-" * 40)
print("python crypto_multi_collector_2023_2026.py")

# 数据使用示例
print("\n📊 数据使用示例")
print("-" * 40)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_crypto_data():
    """分析收集到的加密货币数据"""
    
    # 示例：读取比特币数据
    try:
        btc_data = pd.read_csv("BTCUSDT_minute_data_2023_2026.csv")
        print(f"✅ 比特币数据: {len(btc_data):,} 条记录")
        print(f"📅 时间范围: {btc_data['Open Time'].iloc[0]} ~ {btc_data['Open Time'].iloc[-1]}")
        
        # 转换时间列
        btc_data['Open Time'] = pd.to_datetime(btc_data['Open Time'])
        btc_data['Close'] = pd.to_numeric(btc_data['Close'])
        
        # 基础统计
        print(f"💰 价格统计:")
        print(f"   最高价: ${btc_data['Close'].max():,.2f}")
        print(f"   最低价: ${btc_data['Close'].min():,.2f}")
        print(f"   平均价: ${btc_data['Close'].mean():,.2f}")
        
        return btc_data
        
    except FileNotFoundError:
        print("❌ 比特币数据文件不存在，请先运行数据收集器")
        return None

def compare_multiple_cryptos():
    """比较多个加密货币的表现"""
    
    cryptos_to_compare = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    comparison_data = {}
    
    for crypto in cryptos_to_compare:
        filename = f"{crypto}_minute_data_2023_2026.csv"
        try:
            df = pd.read_csv(filename)
            df['Open Time'] = pd.to_datetime(df['Open Time'])
            df['Close'] = pd.to_numeric(df['Close'])
            
            # 计算日收益率
            df_daily = df.set_index('Open Time').resample('D')['Close'].last().dropna()
            daily_returns = df_daily.pct_change().dropna()
            
            comparison_data[crypto] = {
                'data': df,
                'daily_prices': df_daily,
                'daily_returns': daily_returns,
                'total_return': (df_daily.iloc[-1] / df_daily.iloc[0] - 1) * 100,
                'volatility': daily_returns.std() * np.sqrt(365) * 100
            }
            
            print(f"📈 {crypto}:")
            print(f"   总收益率: {comparison_data[crypto]['total_return']:.2f}%")
            print(f"   年化波动率: {comparison_data[crypto]['volatility']:.2f}%")
            
        except FileNotFoundError:
            print(f"❌ {crypto} 数据文件不存在")
    
    return comparison_data

def create_sample_analysis():
    """创建示例分析"""
    
    print("\n📊 数据分析示例:")
    
    # 1. 单币种分析
    btc_data = analyze_crypto_data()
    
    if btc_data is not None:
        print("\n📈 比较分析:")
        comparison_results = compare_multiple_cryptos()
        
        # 2. 相关性分析示例
        if len(comparison_results) >= 2:
            print(f"\n🔗 相关性分析示例:")
            print("# 计算不同货币的价格相关性")
            print("correlation_matrix = pd.DataFrame()")
            print("for crypto, data in comparison_results.items():")
            print("    correlation_matrix[crypto] = data['daily_returns']")
            print("print(correlation_matrix.corr())")

def batch_analysis_template():
    """批量分析模板"""
    
    template_code = '''
# 批量分析所有收集的加密货币数据
import pandas as pd
import numpy as np
import os

def analyze_all_cryptos():
    """分析所有收集的加密货币数据"""
    
    crypto_files = [f for f in os.listdir('.') if f.endswith('_minute_data_2023_2026.csv')]
    results = {}
    
    for file in crypto_files:
        crypto_name = file.split('_')[0]
        
        try:
            # 读取数据
            df = pd.read_csv(file)
            df['Open Time'] = pd.to_datetime(df['Open Time'])
            df['Close'] = pd.to_numeric(df['Close'])
            
            # 基础统计
            price_stats = {
                'count': len(df),
                'min_price': df['Close'].min(),
                'max_price': df['Close'].max(),
                'mean_price': df['Close'].mean(),
                'start_price': df['Close'].iloc[0],
                'end_price': df['Close'].iloc[-1],
                'total_return': (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
            }
            
            results[crypto_name] = price_stats
            
        except Exception as e:
            print(f"分析 {crypto_name} 时出错: {e}")
    
    # 转换为DataFrame便于查看
    results_df = pd.DataFrame(results).T
    return results_df

# 运行分析
if __name__ == "__main__":
    analysis_results = analyze_all_cryptos()
    print("\\n📊 所有加密货币表现汇总:")
    print(analysis_results)
    
    # 保存结果
    analysis_results.to_csv('crypto_analysis_summary.csv')
    print("\\n✅ 分析结果已保存至 crypto_analysis_summary.csv")
'''
    
    # 保存模板到文件
    with open("batch_analysis_template.py", "w", encoding="utf-8") as f:
        f.write(template_code)
    
    print(f"\n📄 批量分析模板已保存至: batch_analysis_template.py")

if __name__ == "__main__":
    print("📚 加密货币数据收集器使用指南")
    print("=" * 60)
    
    print("\n1️⃣ 收集数据:")
    print("   运行数据收集器脚本，自动下载所有主要加密货币的分钟级数据")
    
    print("\n2️⃣ 分析数据:")
    create_sample_analysis()
    
    print("\n3️⃣ 批量分析:")
    batch_analysis_template()
    
    print("\n" + "=" * 60)
    print("💡 提示:")
    print("- 数据收集可能需要几个小时完成")
    print("- 建议在网络稳定的环境下运行")  
    print("- 每个文件大约包含 1-2 百万条记录")
    print("- 总数据量约为 30-50GB")
    print("- 可以中断后继续收集（会跳过已存在的文件）")