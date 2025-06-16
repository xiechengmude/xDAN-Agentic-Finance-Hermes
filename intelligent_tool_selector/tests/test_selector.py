#!/usr/bin/env python3
"""
智能工具选择器测试模块
Test Module for Intelligent Tool Selector
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# 添加父目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from intelligent_tool_selector import IntelligentToolSelector


class TestIntelligentToolSelector:
    """智能工具选择器测试类"""
    
    def __init__(self):
        self.selector = IntelligentToolSelector()
        self.test_results = []
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始运行智能工具选择器测试套件")
        print("=" * 60)
        
        # 初始化
        success = await self.selector.initialize()
        if not success:
            print("❌ 初始化失败，终止测试")
            return {"success": False, "error": "初始化失败"}
        
        # 运行各类测试
        await self.test_basic_functionality()
        await self.test_tool_selection_accuracy()
        await self.test_parameter_mapping()
        await self.test_error_handling()
        await self.test_edge_cases()
        
        # 生成测试报告
        return self.generate_test_report()
    
    async def test_basic_functionality(self):
        """基本功能测试"""
        print("\n📋 基本功能测试")
        print("-" * 40)
        
        test_cases = [
            {
                "name": "工具计数",
                "description": "验证工具数量大于0",
                "test": lambda: self.selector.get_tools_count() > 0
            },
            {
                "name": "初始化状态",
                "description": "验证选择器已初始化",
                "test": lambda: self.selector.is_initialized()
            }
        ]
        
        for case in test_cases:
            try:
                result = case["test"]()
                status = "✅ 通过" if result else "❌ 失败"
                print(f"{case['name']}: {status}")
                self.test_results.append({
                    "category": "基本功能",
                    "name": case['name'],
                    "success": result,
                    "description": case['description']
                })
            except Exception as e:
                print(f"{case['name']}: ❌ 异常 - {e}")
                self.test_results.append({
                    "category": "基本功能",
                    "name": case['name'],
                    "success": False,
                    "error": str(e)
                })
    
    async def test_tool_selection_accuracy(self):
        """工具选择准确性测试"""
        print("\n🎯 工具选择准确性测试")
        print("-" * 40)
        
        test_queries = [
            {
                "query": "搜索平安银行的股票信息",
                "expected_tool_pattern": "stock_basic",
                "description": "股票基本信息查询"
            },
            {
                "query": "获取腾讯控股的港股数据",
                "expected_tool_pattern": "hk_",
                "description": "港股数据查询"
            },
            {
                "query": "查询龙虎榜数据",
                "expected_tool_pattern": "top_list",
                "description": "龙虎榜数据查询"
            }
        ]
        
        for i, case in enumerate(test_queries, 1):
            print(f"测试 {i}: {case['query']}")
            
            try:
                result = await self.selector.select_and_execute_tool(case['query'])
                
                success = result['success']
                if success:
                    selected_tool = result['execution_result']['tool_name']
                    pattern_match = case['expected_tool_pattern'] in selected_tool
                    
                    print(f"  选择工具: {selected_tool}")
                    print(f"  匹配期望: {'✅' if pattern_match else '❌'}")
                    
                    self.test_results.append({
                        "category": "工具选择准确性",
                        "name": case['description'],
                        "success": success and pattern_match,
                        "selected_tool": selected_tool,
                        "query": case['query']
                    })
                else:
                    print(f"  ❌ 选择失败: {result['error']}")
                    self.test_results.append({
                        "category": "工具选择准确性",
                        "name": case['description'],
                        "success": False,
                        "error": result['error'],
                        "query": case['query']
                    })
                    
            except Exception as e:
                print(f"  ❌ 异常: {e}")
                self.test_results.append({
                    "category": "工具选择准确性",
                    "name": case['description'],
                    "success": False,
                    "error": str(e),
                    "query": case['query']
                })
    
    async def test_parameter_mapping(self):
        """参数映射测试"""
        print("\n📊 参数映射测试")
        print("-" * 40)
        
        # 测试能否正确映射参数
        query = "搜索中国银行的股票"
        
        try:
            result = await self.selector.select_and_execute_tool(query)
            
            if result['success']:
                parameters = result['execution_result']['parameters']
                has_valid_params = len(parameters) > 0
                
                print(f"参数映射: {'✅ 成功' if has_valid_params else '❌ 失败'}")
                print(f"参数内容: {parameters}")
                
                self.test_results.append({
                    "category": "参数映射",
                    "name": "参数组装",
                    "success": has_valid_params,
                    "parameters": parameters,
                    "query": query
                })
            else:
                print(f"❌ 测试失败: {result['error']}")
                self.test_results.append({
                    "category": "参数映射",
                    "name": "参数组装",
                    "success": False,
                    "error": result['error']
                })
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            self.test_results.append({
                "category": "参数映射",
                "name": "参数组装",
                "success": False,
                "error": str(e)
            })
    
    async def test_error_handling(self):
        """错误处理测试"""
        print("\n🛡️ 错误处理测试")
        print("-" * 40)
        
        # 测试无意义查询
        invalid_query = "这是一个完全无关的查询，不涉及任何金融数据"
        
        try:
            result = await self.selector.select_and_execute_tool(invalid_query)
            
            # 对于无效查询，系统应该能处理但可能不会成功执行
            handled_gracefully = 'error' in result or 'success' in result
            
            print(f"无效查询处理: {'✅ 优雅处理' if handled_gracefully else '❌ 处理失败'}")
            
            self.test_results.append({
                "category": "错误处理",
                "name": "无效查询处理",
                "success": handled_gracefully,
                "query": invalid_query,
                "result": result
            })
            
        except Exception as e:
            print(f"❌ 异常: {e}")
            self.test_results.append({
                "category": "错误处理",
                "name": "无效查询处理",
                "success": False,
                "error": str(e)
            })
    
    async def test_edge_cases(self):
        """边界情况测试"""
        print("\n🔄 边界情况测试")
        print("-" * 40)
        
        edge_cases = [
            {
                "name": "空查询",
                "query": "",
                "description": "处理空字符串查询"
            },
            {
                "name": "超长查询",
                "query": "查询" * 100,
                "description": "处理超长查询字符串"
            },
            {
                "name": "特殊字符查询",
                "query": "查询@#$%^&*()股票信息",
                "description": "处理包含特殊字符的查询"
            }
        ]
        
        for case in edge_cases:
            print(f"测试: {case['name']}")
            
            try:
                result = await self.selector.select_and_execute_tool(case['query'])
                handled = 'success' in result and 'error' in result
                
                print(f"  结果: {'✅ 处理成功' if handled else '❌ 处理失败'}")
                
                self.test_results.append({
                    "category": "边界情况",
                    "name": case['name'],
                    "success": handled,
                    "description": case['description'],
                    "query": case['query']
                })
                
            except Exception as e:
                print(f"  ❌ 异常: {e}")
                self.test_results.append({
                    "category": "边界情况",
                    "name": case['name'],
                    "success": False,
                    "error": str(e)
                })
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n📊 测试报告")
        print("=" * 60)
        
        # 统计结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 按类别统计
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
        
        # 打印统计结果
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        print(f"\n各类别统计:")
        for category, stats in categories.items():
            category_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {category}: {stats['passed']}/{stats['total']} ({category_rate:.1f}%)")
        
        # 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate
            },
            "categories": categories,
            "detailed_results": self.test_results
        }
        
        # 保存到文件
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存至: {report_file}")
        
        return report


async def main():
    """主函数"""
    try:
        tester = TestIntelligentToolSelector()
        report = await tester.run_all_tests()
        
        print(f"\n🎉 测试完成!")
        print(f"整体成功率: {report['summary']['success_rate']:.1f}%")
        
        if report['summary']['success_rate'] >= 80:
            print("🏆 测试评级: 优秀 (≥80%)")
        elif report['summary']['success_rate'] >= 60:
            print("👍 测试评级: 良好 (≥60%)")
        else:
            print("⚠️ 测试评级: 需要改进 (<60%)")
            
    except KeyboardInterrupt:
        print(f"\n⏹️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 