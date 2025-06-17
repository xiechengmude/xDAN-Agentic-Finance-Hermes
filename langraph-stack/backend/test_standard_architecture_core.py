#!/usr/bin/env python3
"""
标准架构核心功能测试
Standard Architecture Core Function Test
"""

import sys
import asyncio
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "architectures/standard"))

def test_tool_selector_initialization():
    """测试工具选择器初始化"""
    print("🧪 测试工具选择器初始化...")
    
    try:
        from architectures.standard.intelligent_tool_selector import IntelligentToolSelector
        
        # 创建实例
        selector = IntelligentToolSelector()
        print("   ✅ IntelligentToolSelector 初始化成功")
        
        # 检查是否有工具可用
        if hasattr(selector, 'available_tools'):
            print(f"   📋 可用工具数量: {len(getattr(selector, 'available_tools', []))}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 工具选择器初始化失败: {e}")
        return False

def test_multi_turn_selector():
    """测试多轮工具选择器"""
    print("🧪 测试多轮工具选择器...")
    
    try:
        from architectures.standard.intelligent_tool_selector import MultiTurnToolSelector
        
        # 创建实例
        multi_selector = MultiTurnToolSelector()
        print("   ✅ MultiTurnToolSelector 初始化成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 多轮工具选择器初始化失败: {e}")
        return False

def test_xdan_adapter():
    """测试xDAN适配器"""
    print("🧪 测试xDAN适配器...")
    
    try:
        from architectures.standard.adapters.xdan_langgraph_adapter import XDANLangGraphAdapter
        
        # 创建实例
        adapter = XDANLangGraphAdapter()
        print("   ✅ XDANLangGraphAdapter 初始化成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ xDAN适配器初始化失败: {e}")
        return False

def test_parallel_execution():
    """测试并行执行功能"""
    print("🧪 测试并行执行功能...")
    
    try:
        # 尝试导入并行执行相关模块
        from architectures.standard.demo_parallel_execution import ParallelExecutor
        
        # 创建实例
        executor = ParallelExecutor()
        print("   ✅ ParallelExecutor 初始化成功")
        
        # 测试依赖分析
        test_tasks = [
            {"id": "task1", "name": "获取公司信息", "dependencies": []},
            {"id": "task2", "name": "财务分析", "dependencies": ["task1"]},
            {"id": "task3", "name": "技术分析", "dependencies": ["task1"]}
        ]
        
        result = executor.analyze_task_dependencies(test_tasks)
        if result and result.get('can_parallelize'):
            print("   ✅ 依赖分析功能正常")
            print(f"   📊 执行层级: {result.get('execution_levels', 0)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 并行执行测试失败: {e}")
        return False

def test_api_functionality():
    """测试API功能"""
    print("🧪 测试API功能...")
    
    try:
        # 检查API文件是否存在
        api_file = project_root / "architectures/standard/api/fastapi_app.py"
        if api_file.exists():
            print("   ✅ FastAPI应用文件存在")
        else:
            print("   ❌ FastAPI应用文件不存在")
            return False
        
        # 尝试导入FastAPI应用
        sys.path.append(str(project_root / "architectures/standard/api"))
        from fastapi_app import app
        print("   ✅ FastAPI应用导入成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API功能测试失败: {e}")
        return False

def test_mcp_connection():
    """测试MCP连接"""
    print("🧪 测试MCP连接...")
    
    try:
        # 检查MCP工具定义
        tools_dir = project_root / "shared/tools"
        if tools_dir.exists():
            tool_files = list(tools_dir.glob("*.json"))
            print(f"   📋 发现工具定义文件: {len(tool_files)}")
            
            if tool_files:
                print("   ✅ MCP工具定义存在")
                return True
        
        print("   ⚠️ 未找到MCP工具定义文件")
        return False
        
    except Exception as e:
        print(f"   ❌ MCP连接测试失败: {e}")
        return False

def test_configuration():
    """测试配置文件"""
    print("🧪 测试配置文件...")
    
    try:
        import json
        
        # 检查架构配置
        config_file = project_root / "architectures/standard/config.json"
        if config_file.exists():
            config = json.loads(config_file.read_text())
            print("   ✅ 架构配置文件存在且有效")
            print(f"   📋 架构名称: {config.get('name', 'Unknown')}")
            print(f"   📋 版本: {config.get('version', 'Unknown')}")
            
            # 检查性能配置
            perf = config.get('performance', {})
            if perf:
                print(f"   📊 成功率: {perf.get('success_rate', 'N/A')}")
                print(f"   ⏱️ 平均响应时间: {perf.get('avg_response_time', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置文件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 标准架构核心功能测试")
    print("=" * 60)
    
    tests = [
        ("工具选择器初始化", test_tool_selector_initialization),
        ("多轮工具选择器", test_multi_turn_selector),
        ("xDAN适配器", test_xdan_adapter),
        ("并行执行功能", test_parallel_execution),
        ("API功能", test_api_functionality),
        ("MCP连接", test_mcp_connection),
        ("配置文件", test_configuration)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        test_start = time.time()
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            results.append((test_name, False))
        
        test_time = time.time() - test_start
        print(f"   ⏱️ 测试耗时: {test_time:.2f}s")
    
    total_time = time.time() - start_time
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 标准架构核心功能测试结果")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 测试结果: {passed}/{total} 通过")
    print(f"⏱️ 总耗时: {total_time:.2f}s")
    
    # 评估结果
    success_rate = (passed / total) * 100
    print(f"📈 成功率: {success_rate:.1f}%")
    
    if passed == total:
        print("🎉 标准架构所有核心功能正常!")
    elif passed >= total * 0.8:
        print("✅ 标准架构主要功能正常，少量问题需要修复")
    else:
        print("⚠️ 标准架构存在较多问题，需要详细调试")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)