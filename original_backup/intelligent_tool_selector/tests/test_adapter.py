#!/usr/bin/env python3
"""
适配器功能测试脚本
Test script for xDAN-LangGraph Adapter
"""

import asyncio
import json
from adapters import XDANLangGraphAdapter
from intelligent_tool_selector import MultiTurnToolSelector


async def test_adapter_basic():
    """测试适配器基本功能"""
    print("🧪 测试适配器基本功能...")
    
    try:
        # 1. 创建适配器
        adapter = XDANLangGraphAdapter()
        print("✅ 适配器创建成功")
        
        # 2. 测试初始化
        success = await adapter.initialize()
        if success:
            print("✅ 适配器初始化成功")
            tools_count = adapter.get_available_tools_count()
            print(f"📊 可用工具数量: {tools_count}")
        else:
            print("❌ 适配器初始化失败")
            return False
        
        # 3. 测试健康检查
        health = await adapter.health_check()
        print(f"🔍 健康检查结果: {health['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False


async def test_stream_execution():
    """测试流式执行功能"""
    print("\n🧪 测试流式执行功能...")
    
    try:
        # 创建适配器
        adapter = XDANLangGraphAdapter()
        await adapter.initialize()
        
        # 模拟LangGraph消息格式
        messages = [
            {
                "type": "human",
                "content": "查询平安银行的股票信息",
                "id": "test-message-1"
            }
        ]
        
        config = {
            "initial_search_query_count": 1,
            "max_research_loops": 1,
            "reasoning_model": "xDAN-Agent-Medium-v2-step300-0525"
        }
        
        print("📡 开始流式执行测试...")
        event_count = 0
        
        # 执行流式处理
        async for event in adapter.stream_execution(messages, config):
            event_count += 1
            print(f"📩 事件 {event_count}: {json.dumps(event, ensure_ascii=False, indent=2)}")
            
            # 限制测试事件数量
            if event_count >= 10:
                print("⏹️ 达到测试事件限制，停止测试")
                break
        
        print(f"✅ 流式执行测试完成，共收到 {event_count} 个事件")
        return True
        
    except Exception as e:
        print(f"❌ 流式执行测试失败: {e}")
        return False


async def test_event_mapping():
    """测试事件映射功能"""
    print("\n🧪 测试事件映射功能...")
    
    try:
        from adapters.event_mapper import EventMapper
        
        mapper = EventMapper()
        
        # 测试任务规划事件转换
        task_plan = {
            "is_complex": True,
            "sub_tasks": [
                {"step": 1, "description": "查询基本信息", "query": "股票基本信息"},
                {"step": 2, "description": "获取财务数据", "query": "财务指标"}
            ]
        }
        
        event1 = mapper.convert_task_planning_event(task_plan)
        print(f"📋 任务规划事件: {json.dumps(event1, ensure_ascii=False, indent=2)}")
        
        # 测试执行事件转换
        execution_result = {
            "tool_name": "search_stocks",
            "success": True,
            "response": {"stock_code": "000001", "name": "平安银行"}
        }
        
        event2 = mapper.convert_execution_event(execution_result)
        print(f"🔧 执行事件: {json.dumps(event2, ensure_ascii=False, indent=2)}")
        
        print("✅ 事件映射测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 事件映射测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始 xDAN-LangGraph 适配器测试")
    print("=" * 60)
    
    # 运行测试
    tests = [
        ("基本功能", test_adapter_basic()),
        ("事件映射", test_event_mapping()),
        ("流式执行", test_stream_execution()),
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
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果摘要:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！适配器功能正常")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")


if __name__ == "__main__":
    asyncio.run(main())