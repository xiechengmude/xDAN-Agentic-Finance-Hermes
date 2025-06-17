#!/usr/bin/env python3
"""
FastAPI集成测试
FastAPI Integration Test

测试FastAPI服务与后端组件的完整集成
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, List, Any
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


class FastAPIIntegrationTester:
    """FastAPI集成测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = {}
    
    async def setup(self):
        """设置测试环境"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
    
    async def test_health_endpoint(self):
        """测试健康检查端点"""
        print("🧪 测试健康检查端点")
        print("=" * 40)
        
        try:
            url = f"{self.base_url}/health"
            print(f"📡 请求: GET {url}")
            
            async with self.session.get(url) as response:
                status = response.status
                data = await response.json() if response.status == 200 else None
                
                print(f"📊 状态码: {status}")
                
                if status == 200 and data:
                    print(f"✅ 健康检查成功")
                    print(f"📋 响应数据: {data}")
                    
                    self.test_results["health_endpoint"] = {
                        "status": "✅ 成功",
                        "status_code": status,
                        "data": data
                    }
                    return True
                else:
                    print(f"❌ 健康检查失败: {status}")
                    self.test_results["health_endpoint"] = f"❌ 失败: {status}"
                    return False
                    
        except Exception as e:
            print(f"❌ 健康检查端点测试异常: {e}")
            self.test_results["health_endpoint"] = f"❌ 异常: {e}"
            return False
    
    async def test_tools_endpoints(self):
        """测试工具相关端点"""
        print("\n🧪 测试工具相关端点")
        print("=" * 40)
        
        results = {}
        
        # 测试工具数量端点
        try:
            url = f"{self.base_url}/tools/count"
            print(f"📡 请求: GET {url}")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    tools_count = data.get('tools_count', 0)
                    
                    print(f"✅ 工具数量查询成功: {tools_count}个工具")
                    results["count"] = f"✅ {tools_count}个工具"
                else:
                    print(f"❌ 工具数量查询失败: {response.status}")
                    results["count"] = f"❌ 失败: {response.status}"
                    
        except Exception as e:
            print(f"❌ 工具数量端点异常: {e}")
            results["count"] = f"❌ 异常: {e}"
        
        # 测试工具列表端点
        try:
            url = f"{self.base_url}/tools/list"
            print(f"📡 请求: GET {url}")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    tools = data.get('tools', [])
                    total = data.get('total', 0)
                    
                    print(f"✅ 工具列表查询成功: {total}个工具")
                    if tools:
                        print(f"📋 工具样例: {tools[:3]}")
                    
                    results["list"] = f"✅ {total}个工具"
                else:
                    print(f"❌ 工具列表查询失败: {response.status}")
                    results["list"] = f"❌ 失败: {response.status}"
                    
        except Exception as e:
            print(f"❌ 工具列表端点异常: {e}")
            results["list"] = f"❌ 异常: {e}"
        
        self.test_results["tools_endpoints"] = results
        return any("✅" in str(result) for result in results.values())
    
    async def test_thread_management(self):
        """测试线程管理端点"""
        print("\n🧪 测试线程管理端点")
        print("=" * 40)
        
        results = {}
        assistant_id = "test-assistant"
        
        # 测试创建线程
        try:
            url = f"{self.base_url}/assistants/{assistant_id}/threads"
            print(f"📡 请求: POST {url}")
            
            async with self.session.post(url) as response:
                if response.status == 200:
                    data = await response.json()
                    thread_id = data.get('thread_id')
                    
                    print(f"✅ 线程创建成功: {thread_id}")
                    results["create"] = f"✅ 成功: {thread_id}"
                    
                    # 测试获取线程信息
                    if thread_id:
                        thread_url = f"{self.base_url}/assistants/{assistant_id}/threads/{thread_id}"
                        print(f"📡 请求: GET {thread_url}")
                        
                        async with self.session.get(thread_url) as thread_response:
                            if thread_response.status == 200:
                                thread_data = await thread_response.json()
                                print(f"✅ 线程信息获取成功: {thread_data}")
                                results["get"] = "✅ 成功"
                            else:
                                print(f"❌ 线程信息获取失败: {thread_response.status}")
                                results["get"] = f"❌ 失败: {thread_response.status}"
                    
                else:
                    print(f"❌ 线程创建失败: {response.status}")
                    results["create"] = f"❌ 失败: {response.status}"
                    
        except Exception as e:
            print(f"❌ 线程管理测试异常: {e}")
            results["create"] = f"❌ 异常: {e}"
        
        self.test_results["thread_management"] = results
        return any("✅" in str(result) for result in results.values())
    
    async def test_streaming_execution(self):
        """测试流式执行端点"""
        print("\n🧪 测试流式执行端点")
        print("=" * 40)
        
        try:
            assistant_id = "test-assistant"
            thread_id = "test-thread"
            
            url = f"{self.base_url}/assistants/{assistant_id}/threads/{thread_id}/runs/stream"
            print(f"📡 请求: POST {url}")
            
            # 准备请求数据
            request_data = {
                "messages": [
                    {
                        "type": "human",
                        "content": "搜索平安银行的股票信息",
                        "id": "test-msg-1"
                    }
                ],
                "initial_search_query_count": 1,
                "max_research_loops": 2
            }
            
            print(f"📨 请求数据: {request_data['messages'][0]['content']}")
            
            async with self.session.post(url, json=request_data) as response:
                print(f"📊 响应状态: {response.status}")
                print(f"📋 响应头: {dict(response.headers)}")
                
                if response.status == 200:
                    print("✅ 流式执行端点响应成功")
                    
                    # 读取流式响应
                    event_count = 0
                    max_events = 5  # 限制事件数量
                    
                    async for line in response.content:
                        try:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                event_data = line_str[6:]  # 移除 'data: ' 前缀
                                event = json.loads(event_data)
                                
                                event_count += 1
                                event_type = event.get('type', 'unknown')
                                print(f"   📨 事件 {event_count}: {event_type}")
                                
                                if event_count >= max_events:
                                    print(f"   ⏱️ 达到最大事件数限制，停止读取")
                                    break
                                    
                        except (json.JSONDecodeError, UnicodeDecodeError) as e:
                            # 忽略解析错误，继续处理下一行
                            continue
                        except Exception as e:
                            print(f"   ⚠️ 事件处理错误: {e}")
                            continue
                    
                    if event_count > 0:
                        print(f"✅ 流式执行测试成功，接收到 {event_count} 个事件")
                        self.test_results["streaming_execution"] = {
                            "status": "✅ 成功",
                            "events": event_count
                        }
                        return True
                    else:
                        print("⚠️ 没有接收到有效事件")
                        self.test_results["streaming_execution"] = "⚠️ 无事件"
                        return False
                        
                else:
                    print(f"❌ 流式执行端点失败: {response.status}")
                    response_text = await response.text()
                    print(f"📄 错误响应: {response_text}")
                    
                    self.test_results["streaming_execution"] = f"❌ 失败: {response.status}"
                    return False
                    
        except Exception as e:
            print(f"❌ 流式执行测试异常: {e}")
            self.test_results["streaming_execution"] = f"❌ 异常: {e}"
            return False
    
    async def test_websocket_connection(self):
        """测试WebSocket连接"""
        print("\n🧪 测试WebSocket连接")
        print("=" * 40)
        
        try:
            # 将HTTP URL转换为WebSocket URL
            ws_url = self.base_url.replace('http', 'ws') + '/ws/stream'
            print(f"📡 WebSocket URL: {ws_url}")
            
            async with self.session.ws_connect(ws_url) as ws:
                print("✅ WebSocket连接成功")
                
                # 发送测试消息
                test_message = {
                    "type": "run",
                    "messages": [
                        {"type": "human", "content": "测试WebSocket连接"}
                    ],
                    "config": {"max_research_loops": 1}
                }
                
                print("📨 发送测试消息...")
                await ws.send_str(json.dumps(test_message))
                
                # 接收响应
                event_count = 0
                max_events = 3
                timeout = 10  # 10秒超时
                
                async with asyncio.timeout(timeout):
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                event = json.loads(msg.data)
                                event_count += 1
                                event_type = event.get('type', 'unknown')
                                print(f"   📨 WebSocket事件 {event_count}: {event_type}")
                                
                                if event_count >= max_events:
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print(f"❌ WebSocket错误: {ws.exception()}")
                            break
                
                if event_count > 0:
                    print(f"✅ WebSocket测试成功，接收到 {event_count} 个事件")
                    self.test_results["websocket"] = {
                        "status": "✅ 成功",
                        "events": event_count
                    }
                    return True
                else:
                    print("⚠️ WebSocket没有接收到事件")
                    self.test_results["websocket"] = "⚠️ 无事件"
                    return False
                    
        except asyncio.TimeoutError:
            print("⏱️ WebSocket连接超时")
            self.test_results["websocket"] = "⏱️ 超时"
            return False
        except Exception as e:
            print(f"❌ WebSocket测试异常: {e}")
            self.test_results["websocket"] = f"❌ 异常: {e}"
            return False
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n🧪 测试错误处理")
        print("=" * 40)
        
        results = {}
        
        # 测试404错误
        try:
            url = f"{self.base_url}/nonexistent/endpoint"
            print(f"📡 测试404: GET {url}")
            
            async with self.session.get(url) as response:
                if response.status == 404:
                    print("✅ 404错误处理正确")
                    results["404"] = "✅ 正确"
                else:
                    print(f"⚠️ 预期404，实际: {response.status}")
                    results["404"] = f"⚠️ 实际: {response.status}"
                    
        except Exception as e:
            print(f"❌ 404测试异常: {e}")
            results["404"] = f"❌ 异常: {e}"
        
        # 测试方法不允许错误
        try:
            url = f"{self.base_url}/health"
            print(f"📡 测试405: DELETE {url}")
            
            async with self.session.delete(url) as response:
                if response.status == 405:
                    print("✅ 405错误处理正确")
                    results["405"] = "✅ 正确"
                else:
                    print(f"⚠️ 预期405，实际: {response.status}")
                    results["405"] = f"⚠️ 实际: {response.status}"
                    
        except Exception as e:
            print(f"❌ 405测试异常: {e}")
            results["405"] = f"❌ 异常: {e}"
        
        self.test_results["error_handling"] = results
        return any("✅" in str(result) for result in results.values())
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 70)
        print("📊 FastAPI集成测试报告")
        print("=" * 70)
        
        print(f"🕒 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 测试服务器: {self.base_url}")
        print("\n📋 测试结果:")
        
        for test_name, result in self.test_results.items():
            print(f"\n🔍 {test_name}:")
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"   {key}: {value}")
            else:
                print(f"   结果: {result}")
        
        # 计算成功率
        total_tests = 0
        successful_tests = 0
        
        for result in self.test_results.values():
            if isinstance(result, dict):
                total_tests += len(result)
                successful_tests += sum(1 for v in result.values() if "✅" in str(v))
            else:
                total_tests += 1
                if "✅" in str(result):
                    successful_tests += 1
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功测试: {successful_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        
        # 保存报告
        report_file = f"fastapi_integration_test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                "server_url": self.base_url,
                "results": self.test_results,
                "statistics": {
                    "total": total_tests,
                    "successful": successful_tests,
                    "success_rate": success_rate
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 报告已保存: {report_file}")
        
        if success_rate >= 80:
            print("\n🎉 FastAPI集成测试总体成功!")
        elif success_rate >= 60:
            print("\n⚠️ FastAPI集成部分功能正常")
        else:
            print("\n❌ FastAPI集成存在问题，需要检查服务器状态")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 启动FastAPI集成测试")
        print("=" * 70)
        print(f"🌐 目标服务器: {self.base_url}")
        print("⚠️ 确保FastAPI服务器正在运行!")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # 依次运行测试
            await self.test_health_endpoint()
            await self.test_tools_endpoints()
            await self.test_thread_management()
            await self.test_streaming_execution()
            await self.test_websocket_connection()
            await self.test_error_handling()
            
            # 生成报告
            self.generate_report()
            
        finally:
            await self.cleanup()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FastAPI集成测试')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='FastAPI服务器URL (默认: http://localhost:8000)')
    
    args = parser.parse_args()
    
    tester = FastAPIIntegrationTester(args.url)
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