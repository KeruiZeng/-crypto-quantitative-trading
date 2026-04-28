#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 基准系统监控工具
==================
确保成功基准系统的持续稳定运行
"""

import json
import os
import shutil
from datetime import datetime, timedelta
import pandas as pd
import glob

class BaselineSystemMonitor:
    """基准系统监控器"""
    
    def __init__(self):
        self.baseline_file = 'efficient_dynamic_backtest_20260414_223221.json'
        self.backup_dir = 'baseline_system_backups'
        self.monitoring_log = []
        
    def create_backup_directory(self):
        """创建备份目录"""
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"📁 创建备份目录: {self.backup_dir}")
    
    def backup_baseline_system(self):
        """备份基准系统"""
        
        print("💾 备份基准系统...")
        
        self.create_backup_directory()
        
        # 需要备份的文件
        files_to_backup = [
            'efficient_dynamic_backtest_2023_2026.py',
            'efficient_dynamic_backtest_20260414_223221.json',
            'BTCUSDT_minute_data_2023_2026.csv',
            'ETHUSDT_minute_data_2023_2026.csv'
        ]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_success = []
        
        for file in files_to_backup:
            if os.path.exists(file):
                backup_name = f"{self.backup_dir}/backup_{timestamp}_{file}"
                shutil.copy2(file, backup_name)
                backup_success.append(file)
                print(f"   ✅ 备份: {file}")
            else:
                print(f"   ⚠️ 文件不存在: {file}")
        
        print(f"📋 成功备份 {len(backup_success)} 个文件")
        return len(backup_success)
    
    def validate_baseline_performance(self):
        """验证基准系统性能"""
        
        print("\n🔍 验证基准系统性能...")
        
        try:
            with open(self.baseline_file, 'r', encoding='utf-8') as f:
                baseline_data = json.load(f)
            
            performance = baseline_data['performance']
            
            # 验证关键指标
            validations = [
                {
                    'metric': '总收益率',
                    'value': performance['total_return'],
                    'expected': 1.947,  # 194.7%
                    'tolerance': 0.01,
                    'status': 'unknown'
                },
                {
                    'metric': '夏普比率', 
                    'value': performance['sharpe_ratio'],
                    'expected': 3.057,
                    'tolerance': 0.1,
                    'status': 'unknown'
                },
                {
                    'metric': '最大回撤',
                    'value': abs(performance['max_drawdown']),
                    'expected': 0.088,  # 8.8%
                    'tolerance': 0.01,
                    'status': 'unknown'
                }
            ]
            
            all_valid = True
            
            for validation in validations:
                actual = validation['value']
                expected = validation['expected']
                tolerance = validation['tolerance']
                
                if abs(actual - expected) <= tolerance:
                    validation['status'] = '✅ 通过'
                else:
                    validation['status'] = '❌ 异常'
                    all_valid = False
                
                print(f"   {validation['metric']}: {actual:.3f} vs {expected:.3f} {validation['status']}")
            
            if all_valid:
                print("🎯 基准系统性能验证通过")
                return True
            else:
                print("⚠️ 基准系统性能存在异常")
                return False
                
        except Exception as e:
            print(f"❌ 基准系统验证失败: {e}")
            return False
    
    def check_system_integrity(self):
        """检查系统完整性"""
        
        print("\n🔧 检查系统完整性...")
        
        # 检查必要文件
        required_files = [
            'efficient_dynamic_backtest_2023_2026.py',
            'efficient_dynamic_backtest_20260414_223221.json'
        ]
        
        missing_files = []
        for file in required_files:
            if os.path.exists(file):
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ 缺失: {file}")
                missing_files.append(file)
        
        # 检查数据文件
        data_files = [
            'BTCUSDT_minute_data_2023_2026.csv',
            'ETHUSDT_minute_data_2023_2026.csv'
        ]
        
        for file in data_files:
            if os.path.exists(file):
                # 检查文件大小
                size_mb = os.path.getsize(file) / (1024*1024)
                print(f"   ✅ {file} ({size_mb:.1f} MB)")
            else:
                print(f"   ❌ 缺失: {file}")
                missing_files.append(file)
        
        if len(missing_files) == 0:
            print("🎯 系统完整性检查通过")
            return True
        else:
            print(f"⚠️ 发现 {len(missing_files)} 个文件缺失")
            return False
    
    def test_system_execution(self):
        """测试系统可执行性"""
        
        print("\n🧪 测试基准系统可执行性...")
        
        try:
            # 尝试导入基准系统
            import sys
            if 'efficient_dynamic_backtest_2023_2026' in sys.modules:
                del sys.modules['efficient_dynamic_backtest_2023_2026']
            
            from efficient_dynamic_backtest_2023_2026 import EfficientDynamicBacktest
            
            # 创建实例
            backtest = EfficientDynamicBacktest()
            
            # 检查关键属性
            attributes = ['initial_capital', 'optimization_frequency', 'rebalance_threshold']
            
            for attr in attributes:
                if hasattr(backtest, attr):
                    value = getattr(backtest, attr)
                    print(f"   ✅ {attr}: {value}")
                else:
                    print(f"   ❌ 缺失属性: {attr}")
                    return False
            
            print("🎯 系统可执行性测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 系统执行测试失败: {e}")
            return False
    
    def generate_system_health_report(self):
        """生成系统健康报告"""
        
        print("\n📋 生成系统健康报告...")
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'baseline_system': 'efficient_dynamic_backtest_2023_2026.py',
            'baseline_performance_file': self.baseline_file,
            'checks': {
                'backup_created': False,
                'performance_validated': False,
                'integrity_verified': False,
                'execution_tested': False
            },
            'overall_status': 'Unknown',
            'recommendations': []
        }
        
        # 执行所有检查
        report['checks']['backup_created'] = self.backup_baseline_system() > 0
        report['checks']['performance_validated'] = self.validate_baseline_performance()
        report['checks']['integrity_verified'] = self.check_system_integrity()
        report['checks']['execution_tested'] = self.test_system_execution()
        
        # 确定整体状态
        passed_checks = sum(report['checks'].values())
        total_checks = len(report['checks'])
        
        if passed_checks == total_checks:
            report['overall_status'] = '🟢 优秀'
            report['recommendations'].append('基准系统运行良好，可以安全继续使用')
        elif passed_checks >= total_checks * 0.75:
            report['overall_status'] = '🟡 良好'
            report['recommendations'].append('基准系统基本正常，建议关注失败的检查项')
        else:
            report['overall_status'] = '🔴 警告'
            report['recommendations'].append('基准系统存在问题，需要立即修复')
        
        # 添加具体建议
        if not report['checks']['backup_created']:
            report['recommendations'].append('立即创建系统备份')
        
        if not report['checks']['performance_validated']:
            report['recommendations'].append('验证基准系统性能数据')
        
        if not report['checks']['integrity_verified']:
            report['recommendations'].append('修复缺失的系统文件')
        
        if not report['checks']['execution_tested']:
            report['recommendations'].append('修复系统代码问题')
        
        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"baseline_system_health_report_{timestamp}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📁 健康报告已保存: {report_filename}")
        
        return report
    
    def display_health_summary(self, report):
        """显示健康摘要"""
        
        print("\n" + "="*60)
        print("📊 基准系统健康摘要")
        print("="*60)
        
        print(f"🕐 检查时间: {report['timestamp']}")
        print(f"📊 整体状态: {report['overall_status']}")
        
        print(f"\n🔍 检查结果:")
        for check_name, result in report['checks'].items():
            status = "✅ 通过" if result else "❌ 失败"
            name_display = check_name.replace('_', ' ').title()
            print(f"   {name_display}: {status}")
        
        print(f"\n💡 建议操作:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # 基准系统性能展示
        if report['checks']['performance_validated']:
            try:
                with open(self.baseline_file, 'r', encoding='utf-8') as f:
                    baseline_data = json.load(f)
                
                perf = baseline_data['performance']
                print(f"\n📈 基准系统性能 (已验证):")
                print(f"   💰 总收益率: {perf['total_return']:.1%}")
                print(f"   📊 夏普比率: {perf['sharpe_ratio']:.3f}")
                print(f"   📉 最大回撤: {perf['max_drawdown']:.1%}")
                print(f"   🎯 胜率: {perf['win_rate']:.1%}")
                
            except:
                pass
        
        print(f"\n🚀 下一步操作:")
        if report['overall_status'] == '🟢 优秀':
            print("   ✅ 可以安全实施阶段1优化")
            print("   🔧 运行: python conservative_enhancement_phase1.py")
        else:
            print("   ⚠️ 先修复基准系统问题")
            print("   🔄 重新运行健康检查")
    
    def monitor_system_files(self):
        """监控系统文件变化"""
        
        print("\n👁️ 监控系统文件...")
        
        key_files = [
            'efficient_dynamic_backtest_2023_2026.py',
            'efficient_dynamic_backtest_20260414_223221.json'
        ]
        
        file_info = {}
        for file in key_files:
            if os.path.exists(file):
                stat = os.stat(file)
                file_info[file] = {
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': '✅ 正常'
                }
            else:
                file_info[file] = {
                    'size': 0,
                    'modified': 'N/A',
                    'status': '❌ 缺失'
                }
        
        print("📁 文件状态:")
        for file, info in file_info.items():
            print(f"   {file}")
            print(f"      大小: {info['size']:,} 字节")
            print(f"      修改: {info['modified']}")
            print(f"      状态: {info['status']}")
        
        return file_info

def main():
    """主函数"""
    
    print("📊 基准系统监控工具")
    print("="*60)
    print("🎯 确保成功基准系统的持续稳定运行")
    print()
    
    monitor = BaselineSystemMonitor()
    
    # 执行全面健康检查
    report = monitor.generate_system_health_report()
    
    # 显示结果
    monitor.display_health_summary(report)
    
    # 文件监控
    monitor.monitor_system_files()
    
    print(f"\n📋 监控完成")
    print(f"   报告文件: baseline_system_health_report_*.json")
    print(f"   备份目录: {monitor.backup_dir}/")

if __name__ == "__main__":
    main()