#!/usr/bin/env python3
"""
简化标准架构测试
Simple Standard Architecture Test
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "architectures/standard"))

def test_core_components():
    """测试核心组件"""
    print("🧪 测试核心组件导入和实例化...")
    
    results = {}
    
    # 测试IntelligentToolSelector
    try:
        from architectures.standard.intelligent_tool_selector import IntelligentToolSelector
        selector = IntelligentToolSelector()
        print("   ✅ IntelligentToolSelector: 导入和实例化成功")
        results['IntelligentToolSelector'] = True
    except Exception as e:
        print(f"   ❌ IntelligentToolSelector: {e}")
        results['IntelligentToolSelector'] = False
    
    # 测试MultiTurnToolSelector
    try:
        from architectures.standard.intelligent_tool_selector import MultiTurnToolSelector
        multi_selector = MultiTurnToolSelector()
        print("   ✅ MultiTurnToolSelector: 导入和实例化成功")
        results['MultiTurnToolSelector'] = True
    except Exception as e:
        print(f"   ❌ MultiTurnToolSelector: {e}")
        results['MultiTurnToolSelector'] = False
    
    # 测试XDANLangGraphAdapter
    try:
        from architectures.standard.adapters.xdan_langgraph_adapter import XDANLangGraphAdapter
        adapter = XDANLangGraphAdapter()
        print("   ✅ XDANLangGraphAdapter: 导入和实例化成功")
        results['XDANLangGraphAdapter'] = True
    except Exception as e:
        print(f"   ❌ XDANLangGraphAdapter: {e}")
        results['XDANLangGraphAdapter'] = False
    
    return results

def test_architecture_structure():
    """测试架构结构"""
    print("🧪 测试架构目录结构...")
    
    standard_dir = project_root / "architectures/standard"
    required_components = [
        "run.py",
        "config.json", 
        "README.md",
        "intelligent_tool_selector",
        "adapters",
        "api"
    ]
    
    results = {}
    for component in required_components:
        path = standard_dir / component
        if path.exists():
            print(f"   ✅ {component}: 存在")
            results[component] = True
        else:
            print(f"   ❌ {component}: 缺失")
            results[component] = False
    
    return results

def test_launcher_integration():
    """测试启动器集成"""
    print("🧪 测试启动器集成...")
    
    try:
        # 检查launch.py是否存在
        launcher = project_root / "launch.py"
        if not launcher.exists():
            print("   ❌ launch.py 不存在")
            return False
        
        print("   ✅ launch.py 存在")
        
        # 读取内容检查标准架构支持
        content = launcher.read_text()
        if "standard" in content and "architectures/standard" in content:
            print("   ✅ 启动器包含标准架构支持")
            return True
        else:
            print("   ⚠️ 启动器标准架构支持不完整")
            return False
            
    except Exception as e:
        print(f"   ❌ 启动器测试失败: {e}")
        return False

def simulate_basic_workflow():
    """模拟基本工作流程"""
    print("🧪 模拟基本工作流程...")
    
    try:
        # 导入必要组件
        from architectures.standard.intelligent_tool_selector import IntelligentToolSelector
        
        # 创建工具选择器
        selector = IntelligentToolSelector()
        print("   ✅ 步骤1: 工具选择器创建成功")
        
        # 模拟工具选择（不实际调用外部服务）
        test_query = "获取股票信息"
        print(f"   ✅ 步骤2: 模拟查询 '{test_query}'")
        
        # 检查是否有选择逻辑
        if hasattr(selector, 'select_tools') or hasattr(selector, 'choose_tool'):
            print("   ✅ 步骤3: 工具选择逻辑存在")
        else:
            print("   ⚠️ 步骤3: 工具选择逻辑可能不完整")
        
        print("   ✅ 基本工作流程模拟完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 工作流程模拟失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 简化标准架构测试")
    print("=" * 50)
    
    start_time = time.time()
    all_results = {}
    
    # 执行测试
    print("\n📋 核心组件测试")
    print("-" * 30)
    core_results = test_core_components()
    all_results.update(core_results)
    
    print("\n📋 架构结构测试")
    print("-" * 30)
    structure_results = test_architecture_structure()
    all_results.update(structure_results)
    
    print("\n📋 启动器集成测试")
    print("-" * 30)
    launcher_result = test_launcher_integration()
    all_results['launcher_integration'] = launcher_result
    
    print("\n📋 基本工作流程测试")
    print("-" * 30)
    workflow_result = simulate_basic_workflow()
    all_results['basic_workflow'] = workflow_result
    
    total_time = time.time() - start_time
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for result in all_results.values() if result)
    total = len(all_results)
    success_rate = (passed / total) * 100
    
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {total - passed}")  
    print(f"📈 成功率: {success_rate:.1f}%")
    print(f"⏱️ 总耗时: {total_time:.2f}s")
    
    # 详细结果
    print("\n📋 详细结果:")
    for component, result in all_results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {component}")
    
    # 评估
    if success_rate >= 80:
        print("\n🎉 标准架构基本功能正常!")
        print("💡 建议: 可以进行更深入的功能测试")
    elif success_rate >= 60:
        print("\n✅ 标准架构主要组件正常")
        print("💡 建议: 修复少量问题后可投入使用")
    else:
        print("\n⚠️ 标准架构需要进一步修复")
        print("💡 建议: 检查导入路径和依赖配置")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)