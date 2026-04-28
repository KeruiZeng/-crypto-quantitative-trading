#!/usr/bin/env python3
"""
回测进度监控器 - 检查每周优化回测状态
"""

import os
import time
import json
from datetime import datetime

def check_backtest_progress():
    """检查回测进度和结果文件"""
    
    print("🔍 每周优化回测进度监控")
    print("=" * 50)
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查可能的结果文件
    result_files = []
    for file in os.listdir('.'):
        if file.endswith('.json') and ('backtest' in file.lower() or 'dynamic' in file.lower()):
            if '2026' in file:  # 今年的文件
                result_files.append(file)
    
    print(f"\n📁 找到 {len(result_files)} 个相关结果文件:")
    
    latest_file = None
    latest_time = 0
    
    for file in sorted(result_files):
        try:
            file_time = os.path.getmtime(file)
            size_mb = os.path.getsize(file) / (1024 * 1024)
            
            time_str = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   📄 {file}")
            print(f"      📅 修改时间: {time_str}")
            print(f"      📏 文件大小: {size_mb:.2f} MB")
            
            if file_time > latest_time:
                latest_time = file_time
                latest_file = file
            
        except Exception as e:
            print(f"   ❌ 读取文件信息失败: {e}")
    
    # 检查最新结果文件
    if latest_file:
        print(f"\n🎯 最新结果文件: {latest_file}")
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取关键信息
            if 'backtest_summary' in data:
                summary = data['backtest_summary']
                print(f"\n📊 回测结果摘要:")
                print(f"   💰 总收益: {summary.get('total_return', 'N/A'):.2%}" if isinstance(summary.get('total_return'), (int, float)) else f"   💰 总收益: {summary.get('total_return', 'N/A')}")
                print(f"   📈 年化收益: {summary.get('annualized_return', 'N/A'):.2%}" if isinstance(summary.get('annualized_return'), (int, float)) else f"   📈 年化收益: {summary.get('annualized_return', 'N/A')}")
                print(f"   ⚡ 夏普比率: {summary.get('sharpe_ratio', 'N/A'):.3f}" if isinstance(summary.get('sharpe_ratio'), (int, float)) else f"   ⚡ 夏普比率: {summary.get('sharpe_ratio', 'N/A')}")
                print(f"   📉 最大回撤: {summary.get('max_drawdown', 'N/A'):.2%}" if isinstance(summary.get('max_drawdown'), (int, float)) else f"   📉 最大回撤: {summary.get('max_drawdown', 'N/A')}")
                
                if 'optimization_frequency' in summary:
                    print(f"   🔄 优化频率: {summary['optimization_frequency']} 天")
            
            elif 'performance_summary' in data:
                perf = data['performance_summary']
                print(f"\n📊 表现摘要:")
                for key, value in perf.items():
                    if isinstance(value, (int, float)) and key.endswith(('return', 'ratio')):
                        print(f"   {key}: {value:.3f}")
                    else:
                        print(f"   {key}: {value}")
            
            # 检查优化历史
            if 'optimization_history' in data:
                opt_history = data['optimization_history']
                print(f"\n🔄 优化记录: {len(opt_history)} 次")
                if len(opt_history) > 0:
                    print(f"   📅 首次优化: {opt_history[0].get('date', 'N/A')}")
                    print(f"   📅 末次优化: {opt_history[-1].get('date', 'N/A')}")
            
            print(f"\n✅ 回测数据加载成功")
                
        except Exception as e:
            print(f"   ❌ 解析结果文件失败: {e}")
    else:
        print(f"\n⏳ 暂未发现完成的回测结果")
    
    print(f"\n" + "=" * 50)

def monitor_running_backtests():
    """监控正在运行的回测"""
    
    print(f"\n🔄 正在运行的回测检查:")
    
    # 检查是否有Python进程在运行
    try:
        import psutil
        
        backtest_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'python' in proc.info['name'].lower() and any(
                    keyword in cmdline.lower() 
                    for keyword in ['backtest', 'dynamic', 'portfolio']
                ):
                    backtest_processes.append(proc.info)
            except:
                continue
        
        if backtest_processes:
            print(f"   🔥 发现 {len(backtest_processes)} 个相关Python进程")
            for proc in backtest_processes:
                runtime = time.time() - proc['create_time']
                print(f"      PID {proc['pid']}: 运行时长 {runtime/60:.1f} 分钟")
        else:
            print(f"   💤 当前没有检测到回测进程")
                
    except ImportError:
        print(f"   ℹ️  需要安装psutil来监控进程: pip install psutil")
    except Exception as e:
        print(f"   ⚠️  进程监控失败: {e}")

if __name__ == "__main__":
    check_backtest_progress()
    monitor_running_backtests()
    
    print(f"\n💡 提示:")
    print(f"   - 如果回测仍在运行，请稍等片刻再次执行此脚本")
    print(f"   - 每周优化回测通常需要5-15分钟完成")
    print(f"   - 完成后会生成新的JSON结果文件")