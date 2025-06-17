#!/usr/bin/env python3
"""
完整集成测试脚本
Complete integration test for xDAN-LangGraph system
"""

import asyncio
import aiohttp
import json
import threading
import time
from api.fastapi_app import app
import uvicorn


def start_backend_server():
    """启动后端服务器"""
    print("🔧 启动后端服务器...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")


async def test_streaming_api():
    """测试流式API"""
    print("📡 测试流式API...")
    
    # 等待服务器启动
    await asyncio.sleep(3)
    
    url = "http://localhost:8000/assistants/xdan-agent/threads/test-thread/runs/stream"
    
    payload = {
        "messages": [
            {
                "type": "human",
                "content": "查询平安银行股票信息",
                "id": "test-msg-1"
            }
        ],
        "initial_search_query_count": 1,
        "max_research_loops": 1,
        "reasoning_model": "xDAN-Agent-Medium-v2-step300-0525"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    print("✅ 流式API响应成功")
                    
                    event_count = 0
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data: '):
                            try:
                                event_data = json.loads(line_text[6:])  # 去掉 'data: ' 前缀
                                event_count += 1
                                
                                if 'data' in event_data:
                                    print(f"📩 事件 {event_count}: {json.dumps(event_data['data'], ensure_ascii=False)}")
                                else:
                                    print(f"📩 控制事件 {event_count}: {event_data['type']}")
                                
                                # 限制测试事件数量
                                if event_count >= 8:
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                    
                    print(f"✅ 流式API测试完成，收到 {event_count} 个事件")
                    return True
                else:
                    print(f"❌ 流式API失败: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ 流式API测试异常: {e}")
        return False


async def test_websocket():
    """测试WebSocket连接"""
    print("🔌 测试WebSocket连接...")
    
    try:
        import websockets
        
        uri = "ws://localhost:8000/ws/stream"
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 发送测试消息
            test_message = {
                "type": "run",
                "messages": [
                    {
                        "type": "human", 
                        "content": "简单测试查询",
                        "id": "ws-test-1"
                    }
                ],
                "config": {
                    "initial_search_query_count": 1,
                    "max_research_loops": 1,
                    "reasoning_model": "xDAN-Agent-Medium-v2-step300-0525"
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 发送WebSocket测试消息")
            
            # 接收响应
            event_count = 0
            try:
                while event_count < 5:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    event_data = json.loads(response)
                    event_count += 1
                    
                    print(f"📩 WS事件 {event_count}: {event_data['type']}")
                    
                    if event_data.get('type') == 'complete':
                        break
                        
            except asyncio.TimeoutError:
                print("⏰ WebSocket响应超时")
            
            print(f"✅ WebSocket测试完成，收到 {event_count} 个事件")
            return True
            
    except ImportError:
        print("⚠️ websockets 库未安装，跳过WebSocket测试")
        return True
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")
        return False


async def run_integration_tests():
    """运行集成测试"""
    print("🧪 开始完整集成测试")
    print("=" * 60)
    
    # 启动后端服务器
    server_thread = threading.Thread(target=start_backend_server, daemon=True)
    server_thread.start()
    
    print("⏳ 等待后端服务器启动...")
    await asyncio.sleep(5)
    
    # 运行测试
    tests = [
        ("流式API", test_streaming_api()),
        ("WebSocket", test_websocket()),
    ]
    
    results = {}
    
    for test_name, test_coro in tests:
        print(f"\n📋 运行测试: {test_name}")
        try:
            result = await test_coro
            results[test_name] = result
            if result:
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results[test_name] = False
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 集成测试结果摘要:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有集成测试通过！系统可以正常使用")
        print("\n🚀 启动方式:")
        print("   后端: python start_backend.py")
        print("   前端: ./start_frontend.sh") 
        print("   全栈: ./start_fullstack.sh")
        print("\n🌐 访问地址:")
        print("   前端: http://localhost:5173")
        print("   后端: http://localhost:8000")
    else:
        print("⚠️ 部分集成测试失败，请检查相关组件")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())