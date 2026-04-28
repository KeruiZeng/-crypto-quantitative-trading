#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 CTA回测进度查询工具
===================
实时查询和监控回测系统的运行进度
"""

import os
import glob
import json
import time
import subprocess
from datetime import datetime, timedelta
import re

class BacktestProgressTracker:
    """回测进度追踪器"""
    
    def __init__(self):
        self.start_time = datetime.now()
        
    def check_running_processes(self):
        """检查正在运行的Python进程"""
        
        print("🔍 检查运行中的回测进程...")
        
        try:
            # 检查python进程
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True, shell=True)
            
            python_processes = [line for line in result.stdout.split('\n') 
                              if 'python.exe' in line]
            
            if python_processes:
                print(f"✅ 发现 {len(python_processes)} 个Python进程:")
                for i, proc in enumerate(python_processes[:3], 1):  # 只显示前3个
                    parts = proc.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        print(f"   {i}. PID: {pid}")
                
                return len(python_processes) > 0
            else:
                print("❌ 未发现活跃的Python进程")
                return False
                
        except Exception as e:
            print(f"❌ 进程检查失败: {e}")
            return False
    
    def analyze_terminal_output(self):
        """分析终端输出获取进度"""
        
        print("\n📈 分析回测进度...")
        
        # 尝试从当前目录的日志或输出文件获取信息
        log_patterns = [
            "enhanced_*.log",
            "*.log"
        ]
        
        latest_log = None
        for pattern in log_patterns:
            files = glob.glob(pattern)
            if files:
                latest_log = max(files, key=os.path.getctime)
                break
        
        if latest_log:
            print(f"📝 分析日志文件: {latest_log}")
            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.extract_progress_from_text(content)
                return True
            except Exception as e:
                print(f"❌ 日志读取失败: {e}")
        
        print("⚠️ 未找到日志文件，尝试其他方法...")
        return False
    
    def extract_progress_from_text(self, text):
        """从文本中提取进度信息"""
        
        # 查找进度信息
        progress_pattern = r"回测进度:\s*(\d+\.?\d*)%\s*\(([\d-]+)\)"
        progress_matches = re.findall(progress_pattern, text)
        
        if progress_matches:
            latest_progress = progress_matches[-1]
            percentage = float(latest_progress[0])
            date = latest_progress[1]
            
            print(f"📊 当前进度: {percentage:.1f}% (处理至: {date})")
            
            # 计算预估完成时间
            if percentage > 0:
                total_time_estimated = (100 / percentage) * (datetime.now() - self.start_time)
                remaining_time = total_time_estimated - (datetime.now() - self.start_time)
                eta = datetime.now() + remaining_time
                
                print(f"⏱️ 预估完成时间: {eta.strftime('%H:%M:%S')}")
                print(f"⏳ 预估剩余时间: {str(remaining_time).split('.')[0]}")
        
        # 查找优化信息
        optimization_pattern = r"执行增强权重优化.*?\(([\d-]+)\)"
        opt_matches = re.findall(optimization_pattern, text)
        
        if opt_matches:
            print(f"🎯 已完成优化次数: {len(opt_matches)} 次")
            print(f"📅 最新优化日期: {opt_matches[-1]}")
        
        # 查找风险预警
        risk_pattern = r"风险预警.*?(\d+)项.*?(LOW|MEDIUM|HIGH)"
        risk_matches = re.findall(risk_pattern, text)
        
        if risk_matches:
            risk_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
            for count, level in risk_matches:
                risk_counts[level] += 1
            
            print(f"⚠️ 风险预警统计:")
            for level, count in risk_counts.items():
                if count > 0:
                    print(f"   {level}: {count} 次")
    
    def check_result_files(self):
        """检查结果文件状态"""
        
        print("\n💾 检查结果文件...")
        
        # 查找增强版结果文件
        enhanced_files = glob.glob("enhanced_dynamic_backtest_*.json")
        baseline_files = glob.glob("efficient_dynamic_backtest_*.json")
        
        print(f"📁 增强版结果文件: {len(enhanced_files)} 个")
        print(f"📁 基准结果文件: {len(baseline_files)} 个")
        
        # 分析最新的增强版文件
        if enhanced_files:
            latest_enhanced = max(enhanced_files, key=os.path.getctime)
            mod_time = datetime.fromtimestamp(os.path.getctime(latest_enhanced))
            file_age = datetime.now() - mod_time
            
            print(f"📋 最新增强版文件: {latest_enhanced}")
            print(f"🕐 文件创建时间: {mod_time.strftime('%H:%M:%S')}")
            print(f"⏱️ 文件年龄: {str(file_age).split('.')[0]}")
            
            # 尝试读取文件内容
            try:
                with open(latest_enhanced, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                perf = data.get('performance', {})
                if perf:
                    print(f"📈 当前表现:")
                    print(f"   总收益: {perf.get('total_return', 0):.1%}")
                    print(f"   夏普比率: {perf.get('sharpe_ratio', 0):.3f}")
                    print(f"   最大回撤: {perf.get('max_drawdown', 0):.1%}")
                
                activities = data.get('activities', {})
                if activities:
                    print(f"📊 系统活动:")
                    print(f"   优化次数: {activities.get('optimizations', 0)}")
                    print(f"   再平衡: {activities.get('rebalances', 0)}")
                    
                return True
                
            except Exception as e:
                print(f"❌ 文件读取失败: {e}")
        
        else:
            print("⏳ 增强版结果文件尚未生成")
            
        return False
    
    def estimate_completion_time(self):
        """估算完成时间"""
        
        print("\n⏰ 完成时间估算...")
        
        # 基本参数
        total_days = 1186  # 2023-01-01 到 2026-04-14
        optimization_frequency = 7  # 每7天优化一次
        expected_optimizations = total_days // optimization_frequency
        
        print(f"📅 总回测天数: {total_days} 天")
        print(f"🎯 预期优化次数: {expected_optimizations} 次")
        
        # 如果有进度信息，计算更精确的估算
        runtime = datetime.now() - self.start_time
        print(f"🕐 当前运行时长: {str(runtime).split('.')[0]}")
    
    def show_quick_status(self):
        """显示快速状态概览"""
        
        print("=" * 60)
        print("📊 CTA回测系统进度查询")
        print("=" * 60)
        print(f"🕐 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查进程状态
        is_running = self.check_running_processes()
        
        # 检查结果文件
        has_results = self.check_result_files()
        
        # 分析进度
        has_logs = self.analyze_terminal_output()
        
        # 估算完成时间
        self.estimate_completion_time()
        
        # 状态总结
        print("\n" + "=" * 60)
        print("📋 状态总结")
        print("-" * 30)
        
        if is_running:
            print("✅ 系统正在运行中")
        else:
            print("❌ 系统可能已停止或未启动")
        
        if has_results:
            print("✅ 有中间结果文件")
        else:
            print("⏳ 等待结果生成")
        
        if has_logs:
            print("✅ 找到进度信息")
        else:
            print("⚠️ 进度信息不可用")
        
        # 操作建议
        print("\n🎯 操作建议:")
        
        if is_running:
            print("📊 系统运行正常，请耐心等待")
            print("🔄 可以定期运行此脚本查看进度")
        else:
            print("🚀 如需重启，运行: python enhanced_dynamic_backtest_2023_2026.py")
        
        print("📈 实时监控: python enhanced_system_monitor.py")
        print("📊 对比分析: python optimization_comparison_tool.py")

def main():
    """主程序"""
    
    tracker = BacktestProgressTracker()
    tracker.show_quick_status()

if __name__ == "__main__":
    main()