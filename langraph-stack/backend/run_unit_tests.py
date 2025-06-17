#!/usr/bin/env python3
"""
单元测试运行脚本
Unit Tests Runner Script

提供便捷的测试运行接口和报告生成
"""

import argparse
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import List, Optional
import json


class TestRunner:
    """测试运行器类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "coverage": {}
        }
    
    def run_tests(
        self,
        test_type: str = "all",
        verbose: bool = True,
        coverage: bool = True,
        parallel: bool = False,
        markers: Optional[List[str]] = None,
        output_format: str = "detailed"
    ) -> bool:
        """
        运行测试
        
        Args:
            test_type: 测试类型 (unit, integration, all)
            verbose: 详细输出
            coverage: 生成覆盖率报告
            parallel: 并行运行
            markers: pytest标记过滤
            output_format: 输出格式 (simple, detailed, json)
            
        Returns:
            测试是否成功
        """
        self.test_results["start_time"] = time.time()
        
        print(f"🧪 开始运行{test_type}测试...")
        print(f"📁 项目根目录: {self.project_root}")
        print("=" * 60)
        
        # 构建pytest命令
        cmd = self._build_pytest_command(
            test_type, verbose, coverage, parallel, markers
        )
        
        print(f"🔧 执行命令: {' '.join(cmd)}")
        print("=" * 60)
        
        # 运行测试
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            success = result.returncode == 0
            
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            success = False
        
        self.test_results["end_time"] = time.time()
        self.test_results["duration"] = self.test_results["end_time"] - self.test_results["start_time"]
        
        # 解析测试结果
        self._parse_test_results()
        
        # 生成报告
        self._generate_report(output_format)
        
        return success
    
    def _build_pytest_command(
        self,
        test_type: str,
        verbose: bool,
        coverage: bool,
        parallel: bool,
        markers: Optional[List[str]]
    ) -> List[str]:
        """构建pytest命令"""
        cmd = ["python", "-m", "pytest"]
        
        # 测试路径
        if test_type == "unit":
            cmd.append("tests/unit/")
        elif test_type == "integration":
            cmd.append("tests/integration/")
        else:
            cmd.append("tests/")
        
        # 基本选项
        if verbose:
            cmd.extend(["-v", "--tb=short"])
        else:
            cmd.extend(["-q"])
        
        # 覆盖率
        if coverage:
            cmd.extend([
                "--cov=src/agent",
                "--cov-report=html:htmlcov", 
                "--cov-report=term-missing",
                "--cov-report=xml"
            ])
        
        # 并行运行
        if parallel:
            try:
                import pytest_xdist
                cmd.extend(["-n", "auto"])
            except ImportError:
                print("⚠️  pytest-xdist未安装，跳过并行运行")
        
        # 标记过滤
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # 其他选项
        cmd.extend([
            "--color=yes",
            "--durations=10",
            "--junit-xml=test-results.xml"
        ])
        
        return cmd
    
    def _parse_test_results(self):
        """解析测试结果"""
        # 尝试解析JUnit XML结果
        junit_file = self.project_root / "test-results.xml"
        if junit_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(junit_file)
                root = tree.getroot()
                
                # 解析测试统计
                for testsuite in root.findall('testsuite'):
                    self.test_results["total_tests"] += int(testsuite.get('tests', 0))
                    self.test_results["failed"] += int(testsuite.get('failures', 0))
                    self.test_results["errors"].extend([
                        error.text for error in testsuite.findall('.//error')
                    ])
                
                self.test_results["passed"] = (
                    self.test_results["total_tests"] - 
                    self.test_results["failed"] - 
                    len(self.test_results["errors"])
                )
                
            except Exception as e:
                print(f"⚠️  解析测试结果失败: {e}")
        
        # 尝试解析覆盖率结果
        coverage_file = self.project_root / "coverage.xml"
        if coverage_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                
                coverage_elem = root.find('.//coverage')
                if coverage_elem is not None:
                    self.test_results["coverage"] = {
                        "line_rate": float(coverage_elem.get('line-rate', 0)),
                        "branch_rate": float(coverage_elem.get('branch-rate', 0))
                    }
                    
            except Exception as e:
                print(f"⚠️  解析覆盖率结果失败: {e}")
    
    def _generate_report(self, output_format: str):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试结果报告")
        print("=" * 60)
        
        if output_format == "json":
            self._generate_json_report()
        elif output_format == "simple":
            self._generate_simple_report()
        else:
            self._generate_detailed_report()
    
    def _generate_detailed_report(self):
        """生成详细报告"""
        duration = self.test_results["duration"]
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        errors = len(self.test_results["errors"])
        
        print(f"⏱️  执行时间: {duration:.2f}秒")
        print(f"📈 测试统计:")
        print(f"   总计: {total}")
        print(f"   通过: {passed} ✅")
        print(f"   失败: {failed} ❌")
        print(f"   错误: {errors} 🚫")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"   成功率: {success_rate:.1f}%")
        
        # 覆盖率信息
        coverage = self.test_results.get("coverage", {})
        if coverage:
            line_rate = coverage.get("line_rate", 0) * 100
            branch_rate = coverage.get("branch_rate", 0) * 100
            print(f"📊 代码覆盖率:")
            print(f"   行覆盖率: {line_rate:.1f}%")
            print(f"   分支覆盖率: {branch_rate:.1f}%")
        
        # 错误详情
        if self.test_results["errors"]:
            print(f"\n🚫 错误详情:")
            for i, error in enumerate(self.test_results["errors"][:3], 1):
                print(f"   {i}. {error[:100]}...")
            
            if len(self.test_results["errors"]) > 3:
                print(f"   ... 还有 {len(self.test_results['errors']) - 3} 个错误")
        
        # 建议
        self._generate_suggestions()
    
    def _generate_simple_report(self):
        """生成简单报告"""
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        
        if total > 0:
            success_rate = (passed / total) * 100
            status = "✅ 通过" if failed == 0 else "❌ 失败"
            print(f"{status} - {passed}/{total} ({success_rate:.1f}%)")
        else:
            print("⚠️  未找到测试结果")
    
    def _generate_json_report(self):
        """生成JSON格式报告"""
        report_file = self.project_root / "test-report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON报告已保存到: {report_file}")
        print(json.dumps(self.test_results, indent=2, ensure_ascii=False))
    
    def _generate_suggestions(self):
        """生成改进建议"""
        print(f"\n💡 改进建议:")
        
        # 覆盖率建议
        coverage = self.test_results.get("coverage", {})
        if coverage:
            line_rate = coverage.get("line_rate", 0) * 100
            if line_rate < 80:
                print(f"   - 提高代码覆盖率 (当前: {line_rate:.1f}%, 建议: >80%)")
        
        # 失败测试建议
        if self.test_results["failed"] > 0:
            print(f"   - 修复失败的测试用例")
            print(f"   - 检查测试环境配置")
        
        # 性能建议
        duration = self.test_results["duration"]
        total = self.test_results["total_tests"]
        if total > 0:
            avg_time = duration / total
            if avg_time > 1.0:
                print(f"   - 优化测试性能 (平均: {avg_time:.2f}秒/测试)")
        
        print(f"   - 查看详细报告: htmlcov/index.html")
        print(f"   - 查看测试结果: test-results.xml")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="xDAN Agent 单元测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run_unit_tests.py                    # 运行所有测试
  python run_unit_tests.py --type unit        # 只运行单元测试
  python run_unit_tests.py --type integration # 只运行集成测试
  python run_unit_tests.py --no-coverage      # 不生成覆盖率报告
  python run_unit_tests.py --parallel         # 并行运行测试
  python run_unit_tests.py --markers slow     # 只运行标记为slow的测试
  python run_unit_tests.py --format json      # 生成JSON格式报告
        """
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["unit", "integration", "all"],
        default="all",
        help="测试类型 (默认: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="详细输出 (默认: True)"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="不生成覆盖率报告"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="并行运行测试"
    )
    
    parser.add_argument(
        "--markers", "-m",
        nargs="+",
        help="pytest标记过滤"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["simple", "detailed", "json"],
        default="detailed",
        help="输出格式 (默认: detailed)"
    )
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestRunner()
    
    # 运行测试
    success = runner.run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=not args.no_coverage,
        parallel=args.parallel,
        markers=args.markers,
        output_format=args.format
    )
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 