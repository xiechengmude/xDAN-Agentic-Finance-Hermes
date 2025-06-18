#!/usr/bin/env python3
"""
测试结果统计评估脚本
用于分析多轮智能体测试的结果并生成详细报告
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class TestResultAnalyzer:
    """测试结果分析器"""
    
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.results_data = []
        self.df = None
        
    def load_results(self):
        """加载测试结果"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                self.results_data = json.load(f)
            self.df = pd.DataFrame(self.results_data)
            print(f"✅ 成功加载 {len(self.results_data)} 条测试结果")
        except Exception as e:
            print(f"❌ 加载测试结果失败: {e}")
            return False
        return True
    
    def generate_report(self):
        """生成完整的评估报告"""
        if not self.df is not None or self.df.empty:
            print("❌ 没有可分析的数据")
            return
        
        # 创建报告目录
        report_dir = Path(self.results_file).parent / "analysis_reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"analysis_report_{timestamp}"
        report_path.mkdir(exist_ok=True)
        
        # 1. 基础统计分析
        self.basic_statistics()
        
        # 2. 工具使用分析
        self.tool_usage_analysis(report_path)
        
        # 3. 性能分析
        self.performance_analysis(report_path)
        
        # 4. 错误分析
        self.error_analysis()
        
        # 5. 生成详细报告
        self.generate_detailed_report(report_path)
        
        print(f"\n📊 分析报告已生成到: {report_path}")
    
    def basic_statistics(self):
        """基础统计分析"""
        print("\n" + "="*60)
        print("📊 基础统计信息")
        print("="*60)
        
        total_tests = len(self.df)
        successful_tests = self.df['success'].sum()
        failed_tests = total_tests - successful_tests
        success_rate = successful_tests / total_tests * 100 if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"成功数: {successful_tests}")
        print(f"失败数: {failed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        # 执行时间统计
        print(f"\n⏱️ 执行时间统计:")
        print(f"平均时间: {self.df['execution_time'].mean():.2f}秒")
        print(f"最短时间: {self.df['execution_time'].min():.2f}秒")
        print(f"最长时间: {self.df['execution_time'].max():.2f}秒")
        print(f"标准差: {self.df['execution_time'].std():.2f}秒")
        
        # 工具覆盖率统计
        print(f"\n🔧 工具覆盖率统计:")
        print(f"平均覆盖率: {self.df['tool_coverage'].mean():.1%}")
        print(f"最高覆盖率: {self.df['tool_coverage'].max():.1%}")
        print(f"最低覆盖率: {self.df['tool_coverage'].min():.1%}")
        
        # 轮数统计
        print(f"\n🔄 执行轮数统计:")
        print(f"平均轮数: {self.df['actual_turns'].mean():.1f}")
        print(f"最少轮数: {self.df['actual_turns'].min()}")
        print(f"最多轮数: {self.df['actual_turns'].max()}")
    
    def tool_usage_analysis(self, report_path: Path):
        """工具使用分析"""
        print("\n" + "="*60)
        print("🔧 工具使用分析")
        print("="*60)
        
        # 统计所有使用的工具
        all_tools = []
        expected_tools = []
        
        for _, row in self.df.iterrows():
            all_tools.extend(row['actual_tools'])
            expected_tools.extend(row['expected_tools'])
        
        # 工具使用频率
        tool_counts = pd.Series(all_tools).value_counts()
        expected_counts = pd.Series(expected_tools).value_counts()
        
        print("\n📈 最常用的工具 (前10):")
        for tool, count in tool_counts.head(10).items():
            print(f"  {tool}: {count}次")
        
        # 绘制工具使用频率图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 实际使用的工具
        tool_counts.head(15).plot(kind='barh', ax=ax1, color='skyblue')
        ax1.set_title('实际使用的工具频率 (前15)', fontsize=14)
        ax1.set_xlabel('使用次数')
        
        # 预期使用的工具
        expected_counts.head(15).plot(kind='barh', ax=ax2, color='lightcoral')
        ax2.set_title('预期使用的工具频率 (前15)', fontsize=14)
        ax2.set_xlabel('预期次数')
        
        plt.tight_layout()
        plt.savefig(report_path / 'tool_usage_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 工具匹配度分析
        self.analyze_tool_matching()
    
    def analyze_tool_matching(self):
        """分析工具匹配度"""
        print("\n🎯 工具匹配度分析:")
        
        perfect_matches = 0
        partial_matches = 0
        no_matches = 0
        
        for _, row in self.df.iterrows():
            actual_set = set(row['actual_tools'])
            expected_set = set(row['expected_tools'])
            
            if not expected_set:
                continue
                
            coverage = row['tool_coverage']
            if coverage >= 1.0:
                perfect_matches += 1
            elif coverage > 0:
                partial_matches += 1
            else:
                no_matches += 1
        
        total = perfect_matches + partial_matches + no_matches
        if total > 0:
            print(f"  完全匹配: {perfect_matches} ({perfect_matches/total:.1%})")
            print(f"  部分匹配: {partial_matches} ({partial_matches/total:.1%})")
            print(f"  无匹配: {no_matches} ({no_matches/total:.1%})")
    
    def performance_analysis(self, report_path: Path):
        """性能分析"""
        print("\n" + "="*60)
        print("⚡ 性能分析")
        print("="*60)
        
        # 创建性能分析图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 执行时间分布
        axes[0, 0].hist(self.df['execution_time'], bins=20, color='green', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('执行时间分布', fontsize=12)
        axes[0, 0].set_xlabel('执行时间 (秒)')
        axes[0, 0].set_ylabel('测试数量')
        
        # 2. 成功率vs执行时间
        success_times = self.df[self.df['success'] == True]['execution_time']
        failed_times = self.df[self.df['success'] == False]['execution_time']
        
        axes[0, 1].boxplot([success_times, failed_times], labels=['成功', '失败'])
        axes[0, 1].set_title('成功/失败案例的执行时间对比', fontsize=12)
        axes[0, 1].set_ylabel('执行时间 (秒)')
        
        # 3. 轮数vs工具覆盖率
        axes[1, 0].scatter(self.df['actual_turns'], self.df['tool_coverage'], 
                          c=self.df['success'], cmap='coolwarm', alpha=0.6)
        axes[1, 0].set_title('执行轮数 vs 工具覆盖率', fontsize=12)
        axes[1, 0].set_xlabel('执行轮数')
        axes[1, 0].set_ylabel('工具覆盖率')
        
        # 4. 执行时间vs轮数
        axes[1, 1].scatter(self.df['actual_turns'], self.df['execution_time'],
                          c=self.df['tool_coverage'], cmap='viridis', alpha=0.6)
        axes[1, 1].set_title('执行轮数 vs 执行时间', fontsize=12)
        axes[1, 1].set_xlabel('执行轮数')
        axes[1, 1].set_ylabel('执行时间 (秒)')
        
        # 添加颜色条
        cbar = plt.colorbar(axes[1, 1].collections[0], ax=axes[1, 1])
        cbar.set_label('工具覆盖率')
        
        plt.tight_layout()
        plt.savefig(report_path / 'performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 轮数准确性分析
        self.analyze_turn_accuracy()
    
    def analyze_turn_accuracy(self):
        """分析轮数准确性"""
        print("\n🎯 轮数准确性分析:")
        
        within_range = 0
        below_range = 0
        above_range = 0
        
        for _, row in self.df.iterrows():
            actual = row['actual_turns']
            expected_min, expected_max = row['expected_turns_range']
            
            if expected_min <= actual <= expected_max:
                within_range += 1
            elif actual < expected_min:
                below_range += 1
            else:
                above_range += 1
        
        total = len(self.df)
        if total > 0:
            print(f"  在预期范围内: {within_range} ({within_range/total:.1%})")
            print(f"  低于预期: {below_range} ({below_range/total:.1%})")
            print(f"  高于预期: {above_range} ({above_range/total:.1%})")
    
    def error_analysis(self):
        """错误分析"""
        print("\n" + "="*60)
        print("❌ 错误分析")
        print("="*60)
        
        # 获取失败的测试
        failed_tests = self.df[self.df['success'] == False]
        
        if failed_tests.empty:
            print("✅ 没有失败的测试！")
            return
        
        print(f"\n失败测试数: {len(failed_tests)}")
        
        # 错误原因分类
        error_types = {}
        for _, row in failed_tests.iterrows():
            error = row.get('error', 'Unknown')
            if pd.notna(error) and error:
                # 简化错误信息
                if 'timeout' in str(error).lower():
                    error_type = 'Timeout'
                elif 'connection' in str(error).lower():
                    error_type = 'Connection Error'
                elif 'tool' in str(error).lower():
                    error_type = 'Tool Error'
                else:
                    error_type = 'Other'
                
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if error_types:
            print("\n错误类型分布:")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count}")
        
        # 失败测试的特征
        print("\n失败测试的特征:")
        print(f"  平均工具覆盖率: {failed_tests['tool_coverage'].mean():.1%}")
        print(f"  平均执行时间: {failed_tests['execution_time'].mean():.2f}秒")
        print(f"  平均执行轮数: {failed_tests['actual_turns'].mean():.1f}")
    
    def generate_detailed_report(self, report_path: Path):
        """生成详细的文本报告"""
        report_file = report_path / 'detailed_report.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 多轮智能体测试评估报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 概览
            f.write("## 1. 测试概览\n\n")
            total = len(self.df)
            successful = self.df['success'].sum()
            f.write(f"- 总测试数: {total}\n")
            f.write(f"- 成功数: {successful}\n")
            f.write(f"- 失败数: {total - successful}\n")
            f.write(f"- 成功率: {successful/total:.1%}\n\n")
            
            # 性能指标
            f.write("## 2. 性能指标\n\n")
            f.write("### 2.1 执行时间\n")
            f.write(f"- 平均: {self.df['execution_time'].mean():.2f}秒\n")
            f.write(f"- 中位数: {self.df['execution_time'].median():.2f}秒\n")
            f.write(f"- 标准差: {self.df['execution_time'].std():.2f}秒\n\n")
            
            f.write("### 2.2 工具覆盖率\n")
            f.write(f"- 平均: {self.df['tool_coverage'].mean():.1%}\n")
            f.write(f"- 中位数: {self.df['tool_coverage'].median():.1%}\n")
            f.write(f"- 标准差: {self.df['tool_coverage'].std():.1%}\n\n")
            
            f.write("### 2.3 执行轮数\n")
            f.write(f"- 平均: {self.df['actual_turns'].mean():.1f}\n")
            f.write(f"- 最小: {self.df['actual_turns'].min()}\n")
            f.write(f"- 最大: {self.df['actual_turns'].max()}\n\n")
            
            # 失败案例分析
            f.write("## 3. 失败案例分析\n\n")
            failed_tests = self.df[self.df['success'] == False]
            if not failed_tests.empty:
                f.write("### 失败的测试用例:\n\n")
                for _, row in failed_tests.iterrows():
                    f.write(f"**测试ID**: {row['test_id']}\n")
                    f.write(f"- 问题: {row['question']}\n")
                    f.write(f"- 错误: {row.get('error', 'Unknown')}\n")
                    f.write(f"- 工具覆盖率: {row['tool_coverage']:.1%}\n")
                    f.write(f"- 执行轮数: {row['actual_turns']}\n\n")
            else:
                f.write("所有测试均成功通过！\n\n")
            
            # 优化建议
            f.write("## 4. 优化建议\n\n")
            
            # 基于分析结果给出建议
            avg_coverage = self.df['tool_coverage'].mean()
            if avg_coverage < 0.7:
                f.write("- ⚠️ 平均工具覆盖率较低，建议优化工具选择算法\n")
            
            avg_time = self.df['execution_time'].mean()
            if avg_time > 30:
                f.write("- ⚠️ 平均执行时间较长，考虑优化并行执行策略\n")
            
            failure_rate = (total - successful) / total if total > 0 else 0
            if failure_rate > 0.2:
                f.write("- ⚠️ 失败率较高，建议检查错误处理机制\n")
            
            # 轮数准确性
            within_range = sum(1 for _, row in self.df.iterrows() 
                             if row['expected_turns_range'][0] <= row['actual_turns'] <= row['expected_turns_range'][1])
            accuracy = within_range / total if total > 0 else 0
            if accuracy < 0.8:
                f.write("- ⚠️ 轮数预测准确率较低，建议优化任务分解算法\n")
            
            f.write("\n## 5. 结论\n\n")
            if successful / total >= 0.8 and avg_coverage >= 0.7:
                f.write("✅ 智能体整体表现良好，能够有效处理多轮复杂查询。\n")
            else:
                f.write("⚠️ 智能体在某些方面还需要改进，请参考上述优化建议。\n")
        
        print(f"\n📄 详细报告已生成: {report_file}")
    
    def generate_html_report(self, report_path: Path):
        """生成HTML格式的报告（可选）"""
        # 这里可以使用模板引擎生成更美观的HTML报告
        pass


def main():
    """主函数"""
    # 查找最新的测试结果文件
    results_dir = Path(__file__).parent.parent / "test_results"
    if not results_dir.exists():
        print("❌ 测试结果目录不存在")
        return
    
    # 获取最新的结果文件
    result_files = list(results_dir.glob("multi_turn_test_results_*.json"))
    if not result_files:
        print("❌ 没有找到测试结果文件")
        return
    
    latest_file = max(result_files, key=lambda p: p.stat().st_mtime)
    print(f"📂 分析文件: {latest_file}")
    
    # 创建分析器
    analyzer = TestResultAnalyzer(str(latest_file))
    
    # 加载并分析结果
    if analyzer.load_results():
        analyzer.generate_report()


if __name__ == "__main__":
    main()