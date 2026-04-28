# 🚀 AI量化交易系统 (AI Quantitative Trading System)

一个基于人工智能的量化交易系统，专注于加密货币市场的CTA策略交易。

## 🌟 项目特色

- **AI驱动**: 集成机器学习模型进行实时预测
- **多策略**: 支持DualThrust、海龟、R-Breaker等经典策略
- **智能优化**: 参数自动调优和组合管理
- **风险控制**: 智能风险预警和资金管理
- **数据收集**: 支持15种主要加密货币的数据获取

## 🏗️ 系统架构

### 核心模块
- **AI交易系统** (`ai_trading_system.py`) - 主系统引擎
- **高级策略引擎** (`advanced_strategy_engine.py`) - 策略集合
- **CTA挖掘系统** (`advanced_cta_mining_system.py`) - 策略挖掘
- **投资组合优化** (`asset_allocation_optimizer.py`) - 资产配置

### 数据处理
- **多币种数据收集** (`crypto_multi_collector_2023_2026.py`)
- **数据诊断** (`data_diagnostic.py`)
- **市场分析** (`crypto_data_analysis_examples.py`)

### 回测系统
- **综合回测** (`comprehensive_cta_backtest_2023_2026.py`)
- **动态投资组合回测** (`dynamic_portfolio_backtest_2023_2026.py`)
- **增强回测系统** (`enhanced_dynamic_backtest_2023_2026.py`)

## 📊 支持的策略

| 序号 | 符号 | 名称 | 市值排名 |
|------|------|------|----------|
| 1 | BTCUSDT | 比特币 | #1 |
| 2 | ETHUSDT | 以太坊 | #2 |
| 3 | BNBUSDT | 币安币 | #3 |
| 4 | ADAUSDT | 卡尔达诺 | #4 |
| 5 | SOLUSDT | Solana | #5 |
| 6 | XRPUSDT | 瑞波币 | #6 |
| 7 | DOTUSDT | Polkadot | #7 |
| 8 | DOGEUSDT | 狗狗币 | #8 |
| 9 | AVAXUSDT | Avalanche | #9 |
| 10 | MATICUSDT | Polygon | #10 |
| 11 | LINKUSDT | Chainlink | #11 |
| 12 | UNIUSDT | Uniswap | #12 |
| 13 | LTCUSDT | 莱特币 | #13 |
| 14 | BCHUSDT | 比特币现金 | #14 |
| 15 | ATOMUSDT | Cosmos | #15 |

## 🚀 快速开始

### 方式1: 简化版收集器 (推荐新手)

```bash
# 运行数据收集
python simple_crypto_collector.py

# 检查现有文件
python simple_crypto_collector.py check

# 查看数据概况  
python simple_crypto_collector.py overview
```

### 方式2: 完整版收集器 (推荐生产环境)

```bash
# 运行完整收集器
python crypto_multi_collector_2023_2026.py
```

## 📊 数据格式

每个加密货币的数据保存为独立的 CSV 文件:

```
[货币对]_minute_data_2023_2026.csv
```

**数据列说明:**
- `Open Time`: 开盘时间
- `Open`: 开盘价
- `High`: 最高价  
- `Low`: 最低价
- `Close`: 收盘价
- `Volume`: 交易量
- `Close Time`: 收盘时间
- `Quote Asset Volume`: 计价资产交易量
- `Number of Trades`: 交易笔数
- `Taker Buy Base Asset Volume`: 主动买入基础资产交易量
- `Taker Buy Quote Asset Volume`: 主动买入计价资产交易量
- `Symbol`: 交易对符号

## 📈 使用示例

### 基础数据读取

```python
import pandas as pd

# 读取比特币数据
btc_data = pd.read_csv("BTCUSDT_minute_data_2023_2026.csv")

# 转换时间格式
btc_data['Open Time'] = pd.to_datetime(btc_data['Open Time'])

# 查看基础信息
print(f"数据条数: {len(btc_data):,}")
print(f"时间范围: {btc_data['Open Time'].min()} ~ {btc_data['Open Time'].max()}")
print(f"价格范围: ${btc_data['Close'].min():.2f} ~ ${btc_data['Close'].max():.2f}")
```

### 多币种对比分析

```python
# 读取多个加密货币数据进行对比
cryptos = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
comparison_data = {}

for crypto in cryptos:
    df = pd.read_csv(f"{crypto}_minute_data_2023_2026.csv")
    df['Open Time'] = pd.to_datetime(df['Open Time'])
    
    # 计算总涨幅
    total_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
    comparison_data[crypto] = total_return
    print(f"{crypto}: {total_return:.2f}%")
```

## ⚙️ 配置说明

### 时间设置
```python
START_DATE = "2023-01-01"  # 开始日期
END_DATE = "2026-03-31"    # 结束日期  
INTERVAL = "1m"            # 数据频率(分钟)
```

### 货币列表
可以在脚本顶部修改 `CRYPTOCURRENCIES` 列表来自定义收集的货币种类。

## 📊 预期数据量

| 项目 | 估算值 |
|------|--------|
| **单个货币数据量** | ~2-3GB |
| **总数据量** | ~30-45GB |
| **单币种记录数** | ~150万-200万条 |
| **总记录数** | ~2000万-3000万条 |
| **预计收集时间** | 2-6小时 |

## ⚠️ 注意事项

1. **网络稳定性**: 建议在稳定的网络环境下运行
2. **API限制**: 代码已包含延迟机制避免触发Binance API限制
3. **存储空间**: 确保有足够的磁盘空间 (建议50GB以上)
4. **断点续传**: 可以随时中断，重新运行会跳过已存在的文件
5. **数据完整性**: 收集完成后建议检查文件完整性

## 🛠️ 故障排除

### 常见问题

**Q: 请求超时怎么办？**
A: 代码已包含重试机制，会自动重试。如果频繁超时，检查网络连接。

**Q: 某些货币收集失败？**
A: 部分货币可能在某些时间段没有数据，这是正常的。检查日志了解具体原因。

**Q: 如何只收集特定货币？**
A: 修改脚本中的 `CRYPTOCURRENCIES` 列表，只保留需要的货币对。

**Q: 数据不完整怎么办？**
A: 删除对应的CSV文件，重新运行收集器会自动补全。

## 📞 技术支持

- 基于Binance API官方文档开发
- 代码结构基于你原始的BTC收集脚本
- 如有问题，请检查网络连接和API可用性

## 🔄 更新日志

- **v1.0**: 基础多货币收集功能
- **v1.1**: 添加错误处理和重试机制
- **v1.2**: 优化内存使用和文件管理
- **v2.0**: 完整版收集器，支持日志和汇总报告

---

💡 **提示**: 建议先用简化版测试单个货币，确认无误后再运行完整收集。