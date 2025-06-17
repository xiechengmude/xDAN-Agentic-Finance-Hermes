#!/usr/bin/env python3
"""
LangGraph后端服务综合测试套件
Comprehensive LangGraph Backend Service Test Suite

测试整个后端数据流转和组件调用
"""

import asyncio
import json
import time
import sys
from typing import Dict, List, Any
from datetime import datetime
import aiohttp
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "architectures/standard"))
sys.path.append(str(project_root / "architectures/langgraph_native"))

from architectures.standard.intelligent_tool_selector import MultiTurnToolSelector, IntelligentToolSelector
from architectures.langgraph_native.adapters.langgraph_native_mcp_adapter import LangGraphNativeMCPAdapter
from architectures.standard.adapters.xdan_langgraph_adapter import XDANLangGraphAdapter


class LangGraphBackendTester:
    """LangGraph后端服务综合测试器"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        
    async def test_component_initialization(self):
        """测试组件初始化"""
        print("\n🧪 测试1: 组件初始化测试")
        print("=" * 60)
        
        test_results = {}
        
        # 测试1.1: 智能工具选择器初始化
        try:
            selector = IntelligentToolSelector()
            test_results["intelligent_tool_selector"] = "✅ 成功"
            print("✅ IntelligentToolSelector 初始化成功")
        except Exception as e:
            test_results["intelligent_tool_selector"] = f"❌ 失败: {e}"
            print(f"❌ IntelligentToolSelector 初始化失败: {e}")
        
        # 测试1.2: 多轮选择器初始化
        try:
            multi_selector = MultiTurnToolSelector(enable_parallel=True)
            test_results["multi_turn_selector"] = "✅ 成功"
            print("✅ MultiTurnToolSelector 初始化成功")
            print(f"   📊 并行执行: {multi_selector.enable_parallel}")
        except Exception as e:
            test_results["multi_turn_selector"] = f"❌ 失败: {e}"
            print(f"❌ MultiTurnToolSelector 初始化失败: {e}")
        
        # 测试1.3: LangGraph原生适配器初始化
        try:
            native_adapter = LangGraphNativeMCPAdapter()
            test_results["langgraph_native_adapter"] = "✅ 成功"
            print("✅ LangGraphNativeMCPAdapter 初始化成功")
        except Exception as e:
            test_results["langgraph_native_adapter"] = f"❌ 失败: {e}"
            print(f"❌ LangGraphNativeMCPAdapter 初始化失败: {e}")
        
        # 测试1.4: xDAN适配器初始化
        try:
            xdan_adapter = XDANLangGraphAdapter()
            test_results["xdan_adapter"] = "✅ 成功"
            print("✅ XDANLangGraphAdapter 初始化成功")
        except Exception as e:
            test_results["xdan_adapter"] = f"❌ 失败: {e}"
            print(f"❌ XDANLangGraphAdapter 初始化失败: {e}")
        
        self.results["component_initialization"] = test_results
        return test_results

    async def test_mcp_connection_and_tools(self):
        """测试MCP连接和工具加载"""
        print("\n🧪 测试2: MCP连接和工具加载测试")
        print("=" * 60)
        
        test_results = {}
        
        try:
            # 使用单轮选择器测试MCP连接
            selector = IntelligentToolSelector()
            
            # 尝试初始化MCP连接
            print("📡 正在连接MCP服务器...")
            success = await selector.initialize()
            
            if success:
                tools_count = selector.get_tools_count()
                test_results["mcp_connection"] = "✅ 成功"
                test_results["tools_loaded"] = f"✅ {tools_count}个工具"
                print(f"✅ MCP连接成功，加载了 {tools_count} 个工具")
                
                # 获取工具列表样例
                if hasattr(selector, 'mcp_manager') and selector.mcp_manager:
                    tools_info = selector.mcp_manager.get_all_tools_info()
                    sample_tools = list(tools_info.keys())[:5]
                    print(f"📋 工具样例: {sample_tools}")
                    test_results["sample_tools"] = sample_tools
                
            else:
                test_results["mcp_connection"] = "❌ 连接失败"
                test_results["tools_loaded"] = "❌ 0个工具"
                print("❌ MCP连接失败")
                
        except Exception as e:
            test_results["mcp_connection"] = f"❌ 异常: {e}"
            print(f"❌ MCP连接测试异常: {e}")
        
        self.results["mcp_connection_and_tools"] = test_results
        return test_results

    async def test_single_turn_execution(self):
        """测试单轮工具执行"""
        print("\n🧪 测试3: 单轮工具执行测试")
        print("=" * 60)
        
        test_results = {}
        test_queries = [
            "搜索平安银行的股票信息",
            "查询腾讯控股的港股数据",
            "搜索银行类股票"
        ]
        
        try:
            selector = IntelligentToolSelector()
            await selector.initialize()
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n📋 测试查询 {i}: {query}")
                print("-" * 40)
                
                start_time = time.time()
                result = await selector.select_and_execute_tool(query)
                execution_time = time.time() - start_time
                
                if result and result.get('success'):
                    execution_result = result.get('execution_result', {})
                    tool_name = execution_result.get('tool_name', '未知')
                    parameters = execution_result.get('parameters', {})
                    
                    test_results[f"query_{i}"] = {
                        "status": "✅ 成功",
                        "tool": tool_name,
                        "time": f"{execution_time:.2f}s",
                        "parameters": parameters
                    }
                    
                    print(f"✅ 执行成功")
                    print(f"🔧 选择工具: {tool_name}")
                    print(f"📝 参数: {parameters}")
                    print(f"⏱️ 耗时: {execution_time:.2f}秒")
                    
                else:
                    error_msg = result.get('error', '未知错误') if result else '结果为空'
                    test_results[f"query_{i}"] = {
                        "status": f"❌ 失败: {error_msg}",
                        "time": f"{execution_time:.2f}s"
                    }
                    print(f"❌ 执行失败: {error_msg}")
                
        except Exception as e:
            test_results["single_turn_execution"] = f"❌ 异常: {e}"
            print(f"❌ 单轮执行测试异常: {e}")
        
        self.results["single_turn_execution"] = test_results
        return test_results

    async def test_multi_turn_execution(self):
        """测试多轮工具执行"""
        print("\n🧪 测试4: 多轮工具执行测试")
        print("=" * 60)
        
        test_results = {}
        complex_queries = [
            "分析比亚迪的投资价值，包括基本面和财务数据",
            "比较招商银行和平安银行的投资价值"
        ]
        
        try:
            multi_selector = MultiTurnToolSelector(enable_parallel=True)
            await multi_selector.initialize()
            
            for i, query in enumerate(complex_queries, 1):
                print(f"\n📋 复杂查询测试 {i}: {query}")
                print("-" * 50)
                
                start_time = time.time()
                result = await multi_selector.multi_turn_execution(query)
                execution_time = time.time() - start_time
                
                if result and result.get('success'):
                    execution_type = result.get('type', 'unknown')
                    turns_executed = result.get('turns_executed', 0)
                    
                    test_results[f"complex_query_{i}"] = {
                        "status": "✅ 成功",
                        "type": execution_type,
                        "turns": turns_executed,
                        "time": f"{execution_time:.2f}s"
                    }
                    
                    print(f"✅ 多轮执行成功")
                    print(f"🔧 执行类型: {execution_type}")
                    print(f"🔄 执行轮次: {turns_executed}")
                    print(f"⏱️ 总耗时: {execution_time:.2f}秒")
                    
                    # 显示执行摘要
                    if execution_type == 'multi_turn':
                        summary = result.get('execution_summary', {})
                        completed = summary.get('completed_tasks', 0)
                        failed = summary.get('failed_tasks', 0)
                        print(f"📊 任务统计: {completed}成功, {failed}失败")
                    
                else:
                    error_msg = result.get('error', '未知错误') if result else '结果为空'
                    test_results[f"complex_query_{i}"] = {
                        "status": f"❌ 失败: {error_msg}",
                        "time": f"{execution_time:.2f}s"
                    }
                    print(f"❌ 多轮执行失败: {error_msg}")
                
        except Exception as e:
            test_results["multi_turn_execution"] = f"❌ 异常: {e}"
            print(f"❌ 多轮执行测试异常: {e}")
        
        self.results["multi_turn_execution"] = test_results
        return test_results

    async def test_parallel_execution_optimization(self):
        """测试并行执行优化"""
        print("\n🧪 测试5: 并行执行优化测试")
        print("=" * 60)
        
        test_results = {}
        
        try:
            from intelligent_tool_selector.core.parallel_executor import ParallelExecutor
            
            executor = ParallelExecutor(max_concurrent_tasks=3)
            
            # 创建测试任务集
            test_tasks = [
                {
                    "step": 1,
                    "task": "获取公司基本信息",
                    "tool": "search_stocks",
                    "parameters": {"keyword": "比亚迪"},
                    "dependency": None
                },
                {
                    "step": 2,
                    "task": "财务数据分析",
                    "tool": "get_financial_data",
                    "parameters": {"ts_code": "002594.SZ"},
                    "dependency": "step1"
                },
                {
                    "step": 3,
                    "task": "技术分析指标",
                    "tool": "get_technical_indicators",
                    "parameters": {"ts_code": "002594.SZ"},
                    "dependency": "step1"
                },
                {
                    "step": 4,
                    "task": "市场表现分析",
                    "tool": "get_market_performance",
                    "parameters": {"ts_code": "002594.SZ"},
                    "dependency": "step1"
                },
                {
                    "step": 5,
                    "task": "行业对比分析",
                    "tool": "industry_comparison",
                    "parameters": {"ts_code": "002594.SZ"},
                    "dependency": "step2"
                }
            ]
            
            print("📊 分析任务依赖关系...")
            analysis_result = executor.analyze_task_dependencies(test_tasks)
            
            can_parallelize = analysis_result.get('can_parallelize', False)
            has_cycles = analysis_result.get('has_cycles', True)
            execution_levels = analysis_result.get('execution_levels', [])
            
            test_results["dependency_analysis"] = {
                "can_parallelize": can_parallelize,
                "has_cycles": has_cycles,
                "levels": len(execution_levels)
            }
            
            print(f"🔗 可并行化: {'✅ 是' if can_parallelize else '❌ 否'}")
            print(f"🔄 循环依赖: {'❌ 有' if has_cycles else '✅ 无'}")
            print(f"📊 执行层级: {len(execution_levels)} 层")
            
            # 显示执行层级
            for i, level in enumerate(execution_levels):
                tasks_in_level = [task.get('task', f'步骤{task.get("step", "?")}') for task in level]
                print(f"   层级 {i+1}: {len(level)} 个任务 - {tasks_in_level}")
            
            # 计算性能提升
            total_tasks = len(test_tasks)
            serial_time = total_tasks
            parallel_time = len(execution_levels)
            improvement = ((serial_time - parallel_time) / serial_time) * 100 if serial_time > 0 else 0
            
            test_results["performance"] = {
                "serial_time": serial_time,
                "parallel_time": parallel_time,
                "improvement": f"{improvement:.1f}%"
            }
            
            print(f"📈 性能分析:")
            print(f"   串行执行: {serial_time} 单位时间")
            print(f"   并行执行: {parallel_time} 单位时间")
            print(f"   性能提升: {improvement:.1f}%")
            
        except Exception as e:
            test_results["parallel_execution"] = f"❌ 异常: {e}"
            print(f"❌ 并行执行测试异常: {e}")
        
        self.results["parallel_execution_optimization"] = test_results
        return test_results

    async def test_adapter_streaming(self):
        """测试适配器流式响应"""
        print("\n🧪 测试6: 适配器流式响应测试")
        print("=" * 60)
        
        test_results = {}
        
        # 测试xDAN适配器流式响应
        try:
            print("📡 测试xDAN适配器流式响应...")
            adapter = XDANLangGraphAdapter()
            await adapter.initialize()
            
            messages = [{"type": "human", "content": "搜索平安银行的股票信息"}]
            config = {"max_research_loops": 2}
            
            event_count = 0
            start_time = time.time()
            
            async for event in adapter.stream_execution(messages, config):
                event_count += 1
                if event_count <= 3:  # 只显示前3个事件
                    print(f"   📨 事件 {event_count}: {type(event).__name__}")
                
                if event_count >= 10:  # 限制事件数量避免无限循环
                    break
            
            execution_time = time.time() - start_time
            
            test_results["xdan_adapter_streaming"] = {
                "status": "✅ 成功",
                "events": event_count,
                "time": f"{execution_time:.2f}s"
            }
            
            print(f"✅ xDAN适配器流式响应测试成功")
            print(f"📊 生成事件数: {event_count}")
            print(f"⏱️ 耗时: {execution_time:.2f}秒")
            
        except Exception as e:
            test_results["xdan_adapter_streaming"] = f"❌ 异常: {e}"
            print(f"❌ xDAN适配器流式响应测试异常: {e}")
        
        # 测试LangGraph原生适配器
        try:
            print("\n📡 测试LangGraph原生适配器...")
            native_adapter = LangGraphNativeMCPAdapter()
            
            test_results["langgraph_native_adapter"] = {
                "status": "✅ 初始化成功",
                "has_stream_method": hasattr(native_adapter, 'stream_execution')
            }
            
            print(f"✅ LangGraph原生适配器初始化成功")
            print(f"📊 包含流式方法: {hasattr(native_adapter, 'stream_execution')}")
            
        except Exception as e:
            test_results["langgraph_native_adapter"] = f"❌ 异常: {e}"
            print(f"❌ LangGraph原生适配器测试异常: {e}")
        
        self.results["adapter_streaming"] = test_results
        return test_results

    async def test_fastapi_endpoints(self):
        """测试FastAPI端点"""
        print("\n🧪 测试7: FastAPI端点测试")
        print("=" * 60)
        
        test_results = {}
        
        # 测试端点连接（如果服务器在运行）
        endpoints = [
            "http://localhost:8000/health",
            "http://localhost:8000/tools/count",
            "http://localhost:8000/tools/list"
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    print(f"📡 测试端点: {endpoint}")
                    async with session.get(endpoint, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            test_results[endpoint.split('/')[-1]] = {
                                "status": f"✅ {response.status}",
                                "response_size": len(str(data))
                            }
                            print(f"✅ 端点响应正常: {response.status}")
                        else:
                            test_results[endpoint.split('/')[-1]] = f"⚠️ {response.status}"
                            print(f"⚠️ 端点响应异常: {response.status}")
                
                except asyncio.TimeoutError:
                    test_results[endpoint.split('/')[-1]] = "⏱️ 超时"
                    print(f"⏱️ 端点连接超时")
                except Exception as e:
                    test_results[endpoint.split('/')[-1]] = f"❌ 连接失败"
                    print(f"❌ 端点连接失败: 服务器可能未启动")
        
        self.results["fastapi_endpoints"] = test_results
        return test_results

    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("📊 LangGraph后端服务综合测试报告")
        print("=" * 80)
        
        total_time = time.time() - self.start_time if self.start_time else 0
        
        print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 总耗时: {total_time:.2f}秒")
        print("\n📋 测试结果摘要:")
        
        # 统计测试结果
        total_tests = 0
        passed_tests = 0
        
        for test_name, results in self.results.items():
            print(f"\n🔍 {test_name}:")
            
            if isinstance(results, dict):
                for item, result in results.items():
                    total_tests += 1
                    status = "✅" if "✅" in str(result) or "成功" in str(result) else "❌"
                    if status == "✅":
                        passed_tests += 1
                    print(f"   {item}: {result}")
            else:
                total_tests += 1
                if "✅" in str(results) or "成功" in str(results):
                    passed_tests += 1
                print(f"   结果: {results}")
        
        # 总结
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过测试: {passed_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        
        # 保存报告到文件
        report_data = {
            "test_time": datetime.now().isoformat(),
            "total_time": total_time,
            "results": self.results,
            "statistics": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            }
        }
        
        report_file = f"langgraph_backend_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
        if success_rate >= 80:
            print("\n🎉 后端服务测试总体成功! 系统运行正常。")
        elif success_rate >= 60:
            print("\n⚠️ 后端服务部分功能正常，建议检查失败项目。")
        else:
            print("\n❌ 后端服务存在较多问题，需要进一步调试。")

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 启动LangGraph后端服务综合测试")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # 依次运行所有测试
        await self.test_component_initialization()
        await self.test_mcp_connection_and_tools()
        await self.test_single_turn_execution()
        await self.test_multi_turn_execution()
        await self.test_parallel_execution_optimization()
        await self.test_adapter_streaming()
        await self.test_fastapi_endpoints()
        
        # 生成测试报告
        self.generate_test_report()


async def main():
    """主函数"""
    tester = LangGraphBackendTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试运行出错: {e}")
        import traceback
        traceback.print_exc()