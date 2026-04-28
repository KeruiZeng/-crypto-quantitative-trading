#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 快速数据诊断和修复
====================
检查数据结构并修复转换问题
"""

import pandas as pd
import numpy as np
import os

# 测试加载一个数据文件
file_path = "c:/Users/Kerui/Desktop/thesis/BTCUSDT_minute_data_2023_2026.csv"

print("🔍 检查数据文件结构...")
df = pd.read_csv(file_path, nrows=100)

print("📊 数据形状:", df.shape)
print("📋 列名:", df.columns.tolist())
print("🏷️ 数据类型:")
print(df.dtypes)

print("\n📝 前5行数据:")
print(df.head())

print("\n🔍 检查各列的数据类型:")
for col in df.columns:
    print(f"{col}: {df[col].dtype} - 示例值: {df[col].iloc[0]}")

# 检查是否有时间戳列
timestamp_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
print(f"\n⏰ 时间戳相关列: {timestamp_cols}")

# 测试技术指标计算
print("\n🧮 测试技术指标计算...")

# 确保有OHLCV数据
required_cols = ['open', 'high', 'low', 'close', 'volume']
for col in required_cols:
    if col not in df.columns and col.capitalize() in df.columns:
        df[col] = df[col.capitalize()]
    elif col not in df.columns:
        print(f"⚠️ 缺少{col}列")

# 计算简单的返回率
if 'close' in df.columns:
    df['return_1'] = df['close'].pct_change(1)
    print(f"✅ 返回率计算成功，样本: {df['return_1'].iloc[5:10].tolist()}")

# 检查哪些列是数值列
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"\n🔢 数值列: {numeric_cols}")

non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
print(f"📝 非数值列: {non_numeric_cols}")