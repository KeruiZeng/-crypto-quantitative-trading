import numpy as np
import pandas as pd
import requests
import time
import os
from datetime import datetime, timedelta
from tqdm import tqdm
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptoDataCollector:
    """加密货币数据收集器"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.columns = [
            "Open Time", "Open", "High", "Low", "Close", "Volume", 
            "Close Time", "Quote Asset Volume", "Number of Trades", 
            "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
        ]
        
        # 主要加密货币列表（至少10种）
        self.crypto_pairs = [
            "BTCUSDT",   # 比特币
            "ETHUSDT",   # 以太坊
            "BNBUSDT",   # 币安币
            "ADAUSDT",   # 卡尔达诺
            "SOLUSDT",   # Solana
            "XRPUSDT",   # 瑞波币
            "DOTUSDT",   # Polkadot
            "DOGEUSDT",  # 狗狗币
            "AVAXUSDT",  # Avalanche
            "MATICUSDT", # Polygon
            "LINKUSDT",  # Chainlink
            "UNIUSDT",   # Uniswap
            "LTCUSDT",   # 莱特币
            "BCHUSDT",   # 比特币现金
            "ATOMUSDT"   # Cosmos
        ]
        
        # 创建输出目录
        self.output_dir = "crypto_data_2023_2026"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def fetch_binance_ohlcv(self, symbol, interval, start_time, end_time, max_retries=3):
        """
        获取币安OHLCV数据，带重试机制
        
        Args:
            symbol: 交易对符号（如 BTCUSDT）
            interval: 时间间隔（1m, 5m, 1h等）
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）
            max_retries: 最大重试次数
        """
        all_data = []
        current_start = start_time
        
        while current_start < end_time:
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    params = {
                        "symbol": symbol,
                        "interval": interval,
                        "startTime": current_start,
                        "endTime": end_time,
                        "limit": 1000  # 每次请求最大限制
                    }
                    
                    response = requests.get(self.base_url, params=params, timeout=30)
                    response.raise_for_status()  # 检查HTTP错误
                    
                    data = response.json()
                    
                    if not data:
                        logger.info(f"{symbol}: 没有更多数据")
                        return all_data
                        
                    all_data.extend(data)
                    current_start = data[-1][0] + 60000  # 添加1分钟（60000ms）避免重复
                    success = True
                    
                    # 避免超过API限制
                    time.sleep(0.1)
                    
                except requests.RequestException as e:
                    retry_count += 1
                    logger.warning(f"{symbol}: 请求失败 (重试 {retry_count}/{max_retries}): {e}")
                    if retry_count < max_retries:
                        time.sleep(2 ** retry_count)  # 指数退避
                    else:
                        logger.error(f"{symbol}: 达到最大重试次数，跳过此时间段")
                        return all_data
                        
                except Exception as e:
                    logger.error(f"{symbol}: 未知错误: {e}")
                    return all_data
        
        return all_data
    
    def generate_date_ranges(self, start_date, end_date, days_per_chunk=7):
        """
        生成日期范围，分块处理以避免单次请求过大
        
        Args:
            start_date: 开始日期
            end_date: 结束日期  
            days_per_chunk: 每块天数
        """
        current_date = pd.Timestamp(start_date)
        end_timestamp = pd.Timestamp(end_date)
        date_ranges = []
        
        while current_date < end_timestamp:
            chunk_end = min(current_date + timedelta(days=days_per_chunk), end_timestamp)
            date_ranges.append((current_date, chunk_end))
            current_date = chunk_end
            
        return date_ranges
    
    def collect_crypto_data(self, symbol, start_date="2023-01-01", end_date="2026-03-31", interval="1m"):
        """
        收集单个加密货币的历史数据
        
        Args:
            symbol: 加密货币交易对
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间间隔（分钟级别）
        """
        logger.info(f"开始收集 {symbol} 数据...")
        
        # 检查文件是否已存在
        output_file = os.path.join(self.output_dir, f"{symbol}_minute_data_2023_2026.csv")
        if os.path.exists(output_file):
            logger.info(f"{symbol} 数据文件已存在，跳过收集")
            return
        
        # 生成日期范围
        date_ranges = self.generate_date_ranges(start_date, end_date)
        all_price_data = pd.DataFrame()
        
        # 使用tqdm显示进度
        for start_chunk, end_chunk in tqdm(date_ranges, desc=f"{symbol} 进度"):
            try:
                start_time = int(start_chunk.timestamp() * 1000)
                end_time = int(end_chunk.timestamp() * 1000)
                
                # 获取数据
                chunk_data = self.fetch_binance_ohlcv(symbol, interval, start_time, end_time)
                
                if chunk_data:
                    # 转换为DataFrame
                    chunk_df = pd.DataFrame(chunk_data, columns=self.columns)
                    
                    # 转换时间戳
                    chunk_df['Open Time'] = pd.to_datetime(chunk_df['Open Time'], unit='ms')
                    chunk_df['Close Time'] = pd.to_datetime(chunk_df['Close Time'], unit='ms')
                    
                    # 转换数值类型
                    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 
                                     'Quote Asset Volume', 'Number of Trades',
                                     'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume']
                    for col in numeric_columns:
                        chunk_df[col] = pd.to_numeric(chunk_df[col], errors='coerce')
                    
                    # 添加货币对信息
                    chunk_df['Symbol'] = symbol
                    
                    # 合并数据
                    all_price_data = pd.concat([all_price_data, chunk_df], ignore_index=True)
                    
                    logger.info(f"{symbol}: 已收集到 {len(all_price_data)} 条记录")
                
            except Exception as e:
                logger.error(f"{symbol}: 处理时间段 {start_chunk} - {end_chunk} 时出错: {e}")
                continue
        
        # 保存数据
        if not all_price_data.empty:
            # 移除重复数据
            all_price_data.drop_duplicates(subset=['Open Time'], inplace=True)
            
            # 按时间排序
            all_price_data.sort_values('Open Time', inplace=True)
            all_price_data.reset_index(drop=True, inplace=True)
            
            # 保存到CSV
            all_price_data.to_csv(output_file, index=False)
            logger.info(f"{symbol}: 数据收集完成，共 {len(all_price_data)} 条记录，已保存到 {output_file}")
        else:
            logger.warning(f"{symbol}: 没有收集到任何数据")
    
    def collect_all_cryptos(self, start_date="2023-01-01", end_date="2026-03-31", interval="1m"):
        """
        收集所有加密货币数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间间隔
        """
        logger.info(f"开始收集 {len(self.crypto_pairs)} 种加密货币的数据")
        logger.info(f"时间范围: {start_date} 到 {end_date}")
        logger.info(f"频率: {interval}")
        logger.info(f"将保存到目录: {self.output_dir}")
        
        success_count = 0
        failed_pairs = []
        
        for i, symbol in enumerate(self.crypto_pairs, 1):
            try:
                logger.info(f"正在处理第 {i}/{len(self.crypto_pairs)} 个: {symbol}")
                self.collect_crypto_data(symbol, start_date, end_date, interval)
                success_count += 1
                
                # 在每个货币对之间添加延迟，避免API限制
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"收集 {symbol} 数据时发生错误: {e}")
                failed_pairs.append(symbol)
                continue
        
        # 汇总报告
        logger.info("\n" + "="*60)
        logger.info("数据收集完成汇总:")
        logger.info(f"成功收集: {success_count}/{len(self.crypto_pairs)} 种加密货币")
        
        if failed_pairs:
            logger.warning(f"收集失败的货币对: {', '.join(failed_pairs)}")
        
        logger.info(f"数据保存在目录: {self.output_dir}")
        
        # 生成数据概览
        self.generate_summary()
    
    def generate_summary(self):
        """生成数据收集汇总报告"""
        summary_data = []
        
        for symbol in self.crypto_pairs:
            file_path = os.path.join(self.output_dir, f"{symbol}_minute_data_2023_2026.csv")
            
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path, nrows=1)  # 只读第一行检查
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    
                    # 读取完整数据获取统计信息
                    full_df = pd.read_csv(file_path)
                    
                    summary_data.append({
                        'Symbol': symbol,
                        'Status': '成功',
                        'Records': len(full_df),
                        'File_Size_MB': round(file_size, 2),
                        'Date_Range': f"{full_df['Open Time'].iloc[0]} ~ {full_df['Open Time'].iloc[-1]}"
                    })
                    
                except Exception as e:
                    summary_data.append({
                        'Symbol': symbol,
                        'Status': f'错误: {e}',
                        'Records': 0,
                        'File_Size_MB': 0,
                        'Date_Range': 'N/A'
                    })
            else:
                summary_data.append({
                    'Symbol': symbol,
                    'Status': '文件不存在',
                    'Records': 0,
                    'File_Size_MB': 0,
                    'Date_Range': 'N/A'
                })
        
        # 保存汇总报告
        summary_df = pd.DataFrame(summary_data)
        summary_file = os.path.join(self.output_dir, "collection_summary.csv")
        summary_df.to_csv(summary_file, index=False)
        
        logger.info(f"\n数据收集汇总报告已保存到: {summary_file}")
        logger.info("\n汇总信息:")
        for _, row in summary_df.iterrows():
            logger.info(f"  {row['Symbol']}: {row['Status']} | {row['Records']:,} 条记录 | {row['File_Size_MB']} MB")


def main():
    """主函数"""
    print("🚀 加密货币数据收集器")
    print("="*60)
    print("收集范围: 2023年1月1日 - 2026年3月31日")
    print("数据频率: 分钟级别")
    print(f"加密货币数量: {len(CryptoDataCollector().crypto_pairs)} 种")
    print("="*60)
    
    # 创建收集器实例
    collector = CryptoDataCollector()
    
    # 显示要收集的加密货币
    print("将收集以下加密货币的数据:")
    for i, symbol in enumerate(collector.crypto_pairs, 1):
        print(f"  {i:2d}. {symbol}")
    
    print("\n开始数据收集...")
    
    try:
        # 开始收集所有数据
        collector.collect_all_cryptos(
            start_date="2023-01-01",
            end_date="2026-03-31", 
            interval="1m"
        )
        
        print("\n✅ 所有任务完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了任务")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        logger.error(f"主程序错误: {e}")


if __name__ == "__main__":
    main()