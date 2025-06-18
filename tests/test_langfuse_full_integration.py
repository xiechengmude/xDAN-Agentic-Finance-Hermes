#!/usr/bin/env python3
"""
完整的Langfuse集成测试
验证Langfuse在智能体全流程中的追踪
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "architectures" / "standard"))

# 加载环境变量
from load_env import load_dotenv
load_dotenv()

# 导入必要的模块
from intelligent_tool_selector import MultiTurnToolSelector
from langfuse import Langfuse

async def test_langfuse_integration():
    """测试Langfuse完整集成"""
    print("🚀 开始Langfuse全流程集成测试\n")
    
    # 1. 验证环境变量
    print("📋 检查环境变量:")
    print(f"  - LANGFUSE_HOST: {os.getenv('LANGFUSE_HOST')}")
    print(f"  - LANGFUSE_PUBLIC_KEY: {os.getenv('LANGFUSE_PUBLIC_KEY')[:20]}...")
    print(f"  - LANGFUSE_SECRET_KEY: {os.getenv('LANGFUSE_SECRET_KEY')[:20]}...")
    
    # 2. 初始化Langfuse客户端
    print("\n🔍 初始化Langfuse客户端...")
    try:
        langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )
        
        # 测试连接（带超时）
        import ssl
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 尝试测试连接
        try:
            langfuse.auth_check()
            print("✅ Langfuse客户端初始化成功")
        except ssl.SSLError as e:
            print(f"⚠️ SSL错误，尝试不验证SSL证书: {e}")
            # 重新创建客户端，禁用SSL验证
            langfuse = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST"),
                httpx_client_kwargs={"verify": False}
            )
            langfuse.auth_check()
            print("✅ Langfuse客户端初始化成功（已禁用SSL验证）")
        
        # 创建trace ID
        trace_id = langfuse.create_trace_id()
        print(f"📊 Trace ID: {trace_id}")
        
    except Exception as e:
        print(f"❌ Langfuse初始化失败: {e}")
        return
    
    # 3. 初始化智能体
    print("\n🤖 初始化智能体...")
    selector = MultiTurnToolSelector()
    
    # 检查langfuse集成是否启用
    from intelligent_tool_selector.utils.langfuse_integration import langfuse_integration
    print(f"  - Langfuse集成状态: {'✅ 已启用' if langfuse_integration.enabled else '❌ 未启用'}")
    
    # 初始化
    success = await selector.initialize()
    print(f"  - 智能体初始化: {'✅ 成功' if success else '❌ 失败'}")
    
    if not success:
        print("⚠️ 智能体初始化失败，无法继续测试")
        return
    
    # 4. 执行测试查询
    test_queries = [
        {
            "query": "你好",
            "type": "simple",
            "description": "简单问候"
        },
        {
            "query": "比较贵州茅台和五粮液最近一年的股价表现",
            "type": "complex",
            "description": "复杂分析查询"
        }
    ]
    
    for test_case in test_queries:
        print(f"\n{'='*60}")
        print(f"📝 测试用例: {test_case['description']}")
        print(f"❓ 查询: {test_case['query']}")
        print(f"📊 预期类型: {test_case['type']}")
        
        try:
            # 创建trace和span
            trace = langfuse.trace(
                id=trace_id,
                name=f"test_{test_case['type']}",
                input=test_case['query'],
                metadata={
                    "query": test_case['query'],
                    "expected_type": test_case['type']
                }
            )
            
            # 执行查询
            result = await selector.multi_turn_execution(test_case['query'])
            
            # 记录结果
            trace.event(
                name=f"test_{test_case['type']}_result",
                input=test_case['query'],
                output=str(result.get('type', 'unknown')),
                metadata={
                    "success": result.get('success', False),
                    "turns": result.get('execution_summary', {}).get('total_turns', 0)
                }
            )
            
            print(f"✅ 执行成功")
            print(f"  - 类型: {result.get('type')}")
            print(f"  - 成功: {result.get('success')}")
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            trace.event(
                name=f"test_{test_case['type']}_error",
                input=test_case['query'],
                output=str(e),
                metadata={"error": True}
            )
    
    # 5. 刷新并完成
    print(f"\n{'='*60}")
    print("🏁 测试完成，刷新Langfuse数据...")
    
    # 创建总结事件
    langfuse.create_event(
        name="test_summary",
        input="Integration test completed",
        output="测试完成",
        metadata={
            "total_tests": len(test_queries),
            "langfuse_enabled": langfuse_integration.enabled
        },
        trace_id=trace_id
    )
    
    # 刷新数据
    langfuse.flush()
    
    # 如果集成模块有客户端，也刷新它
    if langfuse_integration.enabled and langfuse_integration.client:
        langfuse_integration.flush()
    
    print("✅ 数据已发送到Langfuse")
    print(f"🔗 查看结果: {os.getenv('LANGFUSE_HOST')}/trace/{trace_id}")
    
    # 6. 生成评分
    print("\n📊 生成测试评分...")
    langfuse.create_score(
        trace_id=trace_id,
        name="integration_test_score",
        value=1.0 if langfuse_integration.enabled else 0.5,
        comment="Full integration test completed"
    )
    
    # 最终刷新
    langfuse.flush()
    print("✅ 评分已提交")


async def main():
    """主函数"""
    await test_langfuse_integration()


if __name__ == "__main__":
    asyncio.run(main())