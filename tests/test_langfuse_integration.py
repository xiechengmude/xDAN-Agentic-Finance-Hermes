#!/usr/bin/env python3
"""
Langfuse集成测试脚本
用于验证Langfuse配置是否正确
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "architectures" / "standard"))

# 加载环境变量
from load_env import load_dotenv
load_dotenv()

def test_langfuse_config():
    """测试Langfuse配置"""
    print("🔍 检查Langfuse配置...")
    
    # 检查环境变量
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    print(f"📋 配置信息:")
    print(f"  - LANGFUSE_HOST: {host}")
    print(f"  - LANGFUSE_PUBLIC_KEY: {'已设置' if public_key and public_key != 'pk-lf-xxx' else '❌ 未设置或使用默认值'}")
    print(f"  - LANGFUSE_SECRET_KEY: {'已设置' if secret_key and secret_key != 'sk-lf-xxx' else '❌ 未设置或使用默认值'}")
    
    if not public_key or not secret_key or public_key == "pk-lf-xxx" or secret_key == "sk-lf-xxx":
        print("\n⚠️ 请在.env文件中设置实际的Langfuse密钥")
        print("访问 https://cloud.langfuse.com 获取您的密钥")
        return False
    
    return True

def test_langfuse_import():
    """测试Langfuse导入"""
    print("\n🔍 测试Langfuse导入...")
    try:
        from langfuse import Langfuse
        print("✅ Langfuse已成功安装")
        return True
    except ImportError as e:
        print(f"❌ Langfuse未安装: {e}")
        print("请运行: uv pip install langfuse")
        return False

async def test_langfuse_connection():
    """测试Langfuse连接"""
    print("\n🔍 测试Langfuse连接...")
    
    try:
        from langfuse import Langfuse
        
        # 初始化客户端
        langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        
        # 创建一个测试事件
        langfuse.auth_check()
        
        # 创建追踪ID
        trace_id = langfuse.create_trace_id()
        
        # 创建事件
        langfuse.create_event(
            name="test_connection",
            input="Hello Langfuse",
            output="Connection test successful",
            metadata={"type": "integration_test", "test": True},
            trace_id=trace_id
        )
        
        # 刷新事件
        langfuse.flush()
        
        print("✅ Langfuse连接成功!")
        print(f"📊 追踪ID: {trace_id}")
        trace_url = langfuse.get_trace_url(trace_id)
        print(f"🔗 查看追踪: {trace_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Langfuse连接失败: {e}")
        return False

async def test_langfuse_with_selector():
    """测试Langfuse与智能体集成"""
    print("\n🔍 测试Langfuse与智能体集成...")
    
    try:
        from intelligent_tool_selector.utils.langfuse_integration import langfuse_integration
        
        if langfuse_integration.enabled:
            print("✅ Langfuse集成已启用")
            
            # 测试装饰器
            from intelligent_tool_selector.utils.langfuse_integration import trace_async
            
            @trace_async(name="test_function")
            async def test_func():
                await asyncio.sleep(0.1)
                return "Test completed"
            
            result = await test_func()
            print(f"✅ 测试函数执行成功: {result}")
            
            # 刷新事件
            if langfuse_integration.client:
                langfuse_integration.flush()
                
            return True
        else:
            print("⚠️ Langfuse集成未启用")
            return False
            
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始Langfuse集成测试\n")
    
    # 1. 测试配置
    config_ok = test_langfuse_config()
    if not config_ok:
        print("\n❌ 请先配置Langfuse密钥")
        return
    
    # 2. 测试导入
    import_ok = test_langfuse_import()
    if not import_ok:
        return
    
    # 3. 测试连接
    connection_ok = await test_langfuse_connection()
    
    # 4. 测试集成
    integration_ok = await test_langfuse_with_selector()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试总结:")
    print(f"  配置检查: {'✅' if config_ok else '❌'}")
    print(f"  导入测试: {'✅' if import_ok else '❌'}")
    print(f"  连接测试: {'✅' if connection_ok else '❌'}")
    print(f"  集成测试: {'✅' if integration_ok else '❌'}")
    
    if all([config_ok, import_ok, connection_ok, integration_ok]):
        print("\n✅ 所有测试通过! Langfuse已正确配置。")
        print("\n下一步:")
        print("1. 运行完整测试: python tests/test_multi_turn_agent.py")
        print("2. 在Langfuse平台查看追踪数据")
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")

if __name__ == "__main__":
    asyncio.run(main())