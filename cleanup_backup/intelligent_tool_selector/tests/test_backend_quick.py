#!/usr/bin/env python3
"""
快速后端服务测试
Quick backend service test
"""

import asyncio
import aiohttp
import json
from api.fastapi_app import app
import uvicorn
import threading
import time


async def test_api_endpoints():
    """测试API端点"""
    
    # 等待服务器启动
    await asyncio.sleep(2)
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 测试健康检查
            print("🔍 测试健康检查...")
            async with session.get(f"{base_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ 健康检查通过: {data['status']}")
                else:
                    print(f"❌ 健康检查失败: {resp.status}")
                    return False
            
            # 2. 测试根路径
            print("🏠 测试根路径...")
            async with session.get(f"{base_url}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ 根路径访问成功: {data['name']}")
                else:
                    print(f"❌ 根路径访问失败: {resp.status}")
            
            # 3. 测试工具数量
            print("🔧 测试工具数量...")
            async with session.get(f"{base_url}/tools/count") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ 工具数量: {data['tools_count']}")
                else:
                    print(f"❌ 工具数量获取失败: {resp.status}")
            
            # 4. 测试创建线程
            print("🧵 测试创建线程...")
            async with session.post(f"{base_url}/assistants/xdan-agent/threads") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ 线程创建成功: {data['thread_id']}")
                    thread_id = data['thread_id']
                else:
                    print(f"❌ 线程创建失败: {resp.status}")
                    return False
            
            print("🎉 所有API端点测试通过！")
            return True
            
        except Exception as e:
            print(f"❌ API测试失败: {e}")
            return False


def start_server():
    """在后台启动服务器"""
    print("🚀 启动测试服务器...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


async def main():
    """主测试函数"""
    print("🧪 开始后端API测试")
    print("=" * 50)
    
    # 在后台线程启动服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    await asyncio.sleep(3)
    
    # 运行API测试
    success = await test_api_endpoints()
    
    if success:
        print("✅ 后端API测试全部通过")
    else:
        print("❌ 后端API测试失败")
    
    print("=" * 50)
    print("📋 测试完成")


if __name__ == "__main__":
    asyncio.run(main())