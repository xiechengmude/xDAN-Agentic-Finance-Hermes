#!/usr/bin/env python3
"""
MCP连接测试脚本
"""

import asyncio
import aiohttp
import json

async def test_mcp_connection():
    """测试MCP服务器连接"""
    server_url = "http://43.134.62.139:7223/sse"
    
    print(f"🔗 测试MCP服务器连接: {server_url}")
    
    try:
        # 测试基本HTTP连接
        async with aiohttp.ClientSession() as session:
            async with session.get(server_url, timeout=10) as response:
                print(f"📡 HTTP状态码: {response.status}")
                print(f"📋 响应头: {dict(response.headers)}")
                
                if response.status == 200:
                    content = await response.text()
                    print(f"📄 响应内容 (前200字符): {content[:200]}...")
                    return True
                else:
                    print(f"❌ HTTP请求失败: {response.status}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 连接异常: {e}")
        return False

async def test_alternative_mcp():
    """测试备用MCP服务器"""
    # 尝试其他可能的端点
    alternative_urls = [
        "http://43.134.62.139:7223",
        "http://43.134.62.139:7223/mcp",
        "http://43.134.62.139:7223/api",
        "http://43.134.62.139:7223/tools"
    ]
    
    for url in alternative_urls:
        print(f"\n🔍 尝试连接: {url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    print(f"  状态码: {response.status}")
                    if response.status == 200:
                        content = await response.text()
                        print(f"  响应: {content[:100]}...")
        except Exception as e:
            print(f"  失败: {e}")

async def main():
    """主函数"""
    print("🚀 开始MCP连接测试")
    print("=" * 50)
    
    # 测试主要连接
    success = await test_mcp_connection()
    
    if not success:
        print("\n🔄 尝试备用连接...")
        await test_alternative_mcp()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 