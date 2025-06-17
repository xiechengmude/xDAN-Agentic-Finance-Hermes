#!/usr/bin/env python3
"""
LangGraph原生工作流测试
LangGraph Native Workflow Test

专门测试LangGraph原生MCP集成的工作流程
"""

import asyncio
import json
import sys
from typing import Dict, List, Any
from pathlib import Path
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from adapters.langgraph_native_mcp_adapter import LangGraphNativeMCPAdapter


class LangGraphNativeWorkflowTester:
    """LangGraph原生工作流测试器"""
    
    def __init__(self):
        self.adapter = None
        self.test_results = {}
    
    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        print("🧪 测试LangGraph原生适配器初始化")
        print("=" * 50)
        
        try:
            self.adapter = LangGraphNativeMCPAdapter()
            print("✅ LangGraphNativeMCPAdapter 创建成功")
            
            # 检查关键组件
            components = {
                "graph": hasattr(self.adapter, 'graph'),
                "checkpointer": hasattr(self.adapter, 'checkpointer'),
                "tools": hasattr(self.adapter, 'tools'),
                "config": hasattr(self.adapter, 'config')
            }
            
            for component, exists in components.items():
                status = "✅" if exists else "❌"
                print(f"{status} {component}: {'存在' if exists else '缺失'}")
            
            # 尝试初始化
            if hasattr(self.adapter, 'initialize'):
                print("\n📡 正在初始化适配器...")
                success = await self.adapter.initialize()
                
                if success:
                    print("✅ 适配器初始化成功")
                    self.test_results["initialization"] = "✅ 成功"
                    return True
                else:
                    print("❌ 适配器初始化失败")
                    self.test_results["initialization"] = "❌ 失败"
                    return False
            else:
                print("⚠️ 适配器没有initialize方法")
                self.test_results["initialization"] = "⚠️ 无初始化方法"
                return False
                
        except Exception as e:
            print(f"❌ 适配器初始化异常: {e}")
            self.test_results["initialization"] = f"❌ 异常: {e}"
            return False
    
    async def test_langgraph_state_graph(self):
        """测试LangGraph StateGraph功能"""
        print("\n🧪 测试LangGraph StateGraph功能")
        print("=" * 50)
        
        try:
            if not self.adapter:
                print("❌ 适配器未初始化")
                return False
            
            # 检查StateGraph相关组件
            if hasattr(self.adapter, 'graph'):
                print("✅ 包含StateGraph")
                
                # 检查节点
                if hasattr(self.adapter.graph, 'nodes'):
                    nodes = list(self.adapter.graph.nodes.keys()) if hasattr(self.adapter.graph.nodes, 'keys') else []
                    print(f"📊 图节点: {nodes}")
                    self.test_results["graph_nodes"] = nodes
                
                # 检查边
                if hasattr(self.adapter.graph, 'edges'):
                    edges = list(self.adapter.graph.edges) if hasattr(self.adapter.graph, 'edges') else []
                    print(f"🔗 图边: {len(edges)}条")
                    self.test_results["graph_edges"] = len(edges)
                
            else:
                print("❌ 没有StateGraph")
                self.test_results["state_graph"] = "❌ 缺失"
                return False
            
            self.test_results["state_graph"] = "✅ 成功"
            return True
            
        except Exception as e:
            print(f"❌ StateGraph测试异常: {e}")
            self.test_results["state_graph"] = f"❌ 异常: {e}"
            return False
    
    async def test_mcp_tool_integration(self):
        """测试MCP工具集成"""
        print("\n🧪 测试MCP工具集成")
        print("=" * 50)
        
        try:
            if not self.adapter:
                print("❌ 适配器未初始化")
                return False
            
            # 检查工具加载
            if hasattr(self.adapter, 'tools'):
                tools = self.adapter.tools
                if tools:
                    print(f"✅ 加载了 {len(tools)} 个MCP工具")
                    
                    # 显示部分工具信息
                    for i, tool in enumerate(tools[:3]):
                        tool_name = tool.name if hasattr(tool, 'name') else f"工具{i+1}"
                        print(f"   🔧 {tool_name}")
                    
                    self.test_results["mcp_tools"] = f"✅ {len(tools)}个工具"
                else:
                    print("❌ 没有加载MCP工具")
                    self.test_results["mcp_tools"] = "❌ 空工具列表"
                    return False
            else:
                print("❌ 没有工具属性")
                self.test_results["mcp_tools"] = "❌ 无工具属性"
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ MCP工具集成测试异常: {e}")
            self.test_results["mcp_tools"] = f"❌ 异常: {e}"
            return False
    
    async def test_streaming_execution(self):
        """测试流式执行"""
        print("\n🧪 测试流式执行")
        print("=" * 50)
        
        try:
            if not self.adapter:
                print("❌ 适配器未初始化")
                return False
            
            # 准备测试消息
            test_messages = [
                {"type": "human", "content": "搜索平安银行的股票信息"}
            ]
            test_config = {"max_steps": 3}
            
            print(f"📨 测试消息: {test_messages[0]['content']}")
            
            # 检查流式执行方法
            if hasattr(self.adapter, 'stream_execution'):
                print("✅ 包含stream_execution方法")
                
                # 尝试流式执行（限制时间和事件数量）
                event_count = 0
                start_time = time.time()
                max_events = 5
                max_time = 10  # 最多10秒
                
                try:
                    async for event in self.adapter.stream_execution(test_messages, test_config):
                        event_count += 1
                        current_time = time.time() - start_time
                        
                        print(f"   📨 事件 {event_count}: {type(event).__name__}")
                        
                        # 限制条件
                        if event_count >= max_events or current_time >= max_time:
                            print(f"   ⏱️ 达到限制条件，停止测试")
                            break
                    
                    execution_time = time.time() - start_time
                    
                    if event_count > 0:
                        print(f"✅ 流式执行成功")
                        print(f"📊 生成事件: {event_count}个")
                        print(f"⏱️ 执行时间: {execution_time:.2f}秒")
                        
                        self.test_results["streaming_execution"] = {
                            "status": "✅ 成功",
                            "events": event_count,
                            "time": f"{execution_time:.2f}s"
                        }
                        return True
                    else:
                        print(f"❌ 没有生成事件")
                        self.test_results["streaming_execution"] = "❌ 无事件"
                        return False
                
                except asyncio.TimeoutError:
                    print(f"⏱️ 流式执行超时")
                    self.test_results["streaming_execution"] = "⏱️ 超时"
                    return False
                    
            else:
                print("❌ 没有stream_execution方法")
                self.test_results["streaming_execution"] = "❌ 无方法"
                return False
            
        except Exception as e:
            print(f"❌ 流式执行测试异常: {e}")
            self.test_results["streaming_execution"] = f"❌ 异常: {e}"
            return False
    
    async def test_health_check(self):
        """测试健康检查"""
        print("\n🧪 测试健康检查")
        print("=" * 50)
        
        try:
            if not self.adapter:
                print("❌ 适配器未初始化")
                return False
            
            if hasattr(self.adapter, 'health_check'):
                print("✅ 包含health_check方法")
                
                health_info = await self.adapter.health_check()
                
                if health_info:
                    print("✅ 健康检查成功")
                    print(f"📊 健康信息: {health_info}")
                    
                    self.test_results["health_check"] = {
                        "status": "✅ 成功",
                        "info": health_info
                    }
                    return True
                else:
                    print("❌ 健康检查返回空")
                    self.test_results["health_check"] = "❌ 返回空"
                    return False
            else:
                print("❌ 没有health_check方法")
                self.test_results["health_check"] = "❌ 无方法"
                return False
                
        except Exception as e:
            print(f"❌ 健康检查测试异常: {e}")
            self.test_results["health_check"] = f"❌ 异常: {e}"
            return False
    
    async def test_thread_management(self):
        """测试线程管理"""
        print("\n🧪 测试线程管理")
        print("=" * 50)
        
        try:
            if not self.adapter:
                print("❌ 适配器未初始化")
                return False
            
            # 测试创建线程
            if hasattr(self.adapter, 'create_thread'):
                print("✅ 包含create_thread方法")
                
                thread_id = await self.adapter.create_thread()
                
                if thread_id:
                    print(f"✅ 线程创建成功: {thread_id}")
                    
                    # 测试获取线程状态
                    if hasattr(self.adapter, 'get_thread_status'):
                        status = await self.adapter.get_thread_status(thread_id)
                        print(f"📊 线程状态: {status}")
                        
                        self.test_results["thread_management"] = {
                            "create": "✅ 成功",
                            "thread_id": thread_id,
                            "status": status
                        }
                    else:
                        self.test_results["thread_management"] = {
                            "create": "✅ 成功",
                            "thread_id": thread_id,
                            "status": "❌ 无状态方法"
                        }
                    
                    return True
                else:
                    print("❌ 线程创建失败")
                    self.test_results["thread_management"] = "❌ 创建失败"
                    return False
            else:
                print("❌ 没有create_thread方法")
                self.test_results["thread_management"] = "❌ 无方法"
                return False
                
        except Exception as e:
            print(f"❌ 线程管理测试异常: {e}")
            self.test_results["thread_management"] = f"❌ 异常: {e}"
            return False
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 70)
        print("📊 LangGraph原生工作流测试报告")
        print("=" * 70)
        
        print(f"🕒 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📋 测试结果:")
        
        for test_name, result in self.test_results.items():
            print(f"\n🔍 {test_name}:")
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"   {key}: {value}")
            else:
                print(f"   结果: {result}")
        
        # 计算成功率
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() 
                             if "✅" in str(result) or "成功" in str(result))
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功测试: {successful_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        
        # 保存报告
        report_file = f"langgraph_native_test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                "results": self.test_results,
                "statistics": {
                    "total": total_tests,
                    "successful": successful_tests,
                    "success_rate": success_rate
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 报告已保存: {report_file}")
        
        if success_rate >= 80:
            print("\n🎉 LangGraph原生工作流测试总体成功!")
        elif success_rate >= 60:
            print("\n⚠️ LangGraph原生工作流部分功能正常")
        else:
            print("\n❌ LangGraph原生工作流存在问题，需要调试")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 启动LangGraph原生工作流测试")
        print("=" * 70)
        
        # 依次运行测试
        await self.test_adapter_initialization()
        await self.test_langgraph_state_graph()
        await self.test_mcp_tool_integration()
        await self.test_streaming_execution()
        await self.test_health_check()
        await self.test_thread_management()
        
        # 生成报告
        self.generate_report()


async def main():
    """主函数"""
    tester = LangGraphNativeWorkflowTester()
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