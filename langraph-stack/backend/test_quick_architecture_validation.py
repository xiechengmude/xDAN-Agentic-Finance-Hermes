#!/usr/bin/env python3
"""
架构分离后快速验证测试
Quick Architecture Validation Test After Separation
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "architectures/standard"))
sys.path.append(str(project_root / "architectures/langgraph_native"))

def test_standard_architecture():
    """测试标准架构组件导入"""
    print("🧪 测试标准架构组件导入...")
    
    try:
        # 测试智能工具选择器导入
        from architectures.standard.intelligent_tool_selector import MultiTurnToolSelector, IntelligentToolSelector
        print("   ✅ IntelligentToolSelector 导入成功")
        
        # 测试适配器导入
        from architectures.standard.adapters.xdan_langgraph_adapter import XDANLangGraphAdapter
        print("   ✅ XDANLangGraphAdapter 导入成功")
        
        # 测试实例化
        selector = IntelligentToolSelector()
        print("   ✅ IntelligentToolSelector 实例化成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 标准架构测试失败: {e}")
        return False

def test_langgraph_architecture():
    """测试LangGraph架构组件导入"""
    print("🧪 测试LangGraph架构组件导入...")
    
    try:
        # 测试LangGraph适配器导入
        from architectures.langgraph_native.adapters.langgraph_native_mcp_adapter import LangGraphNativeMCPAdapter
        print("   ✅ LangGraphNativeMCPAdapter 导入成功")
        
        # 测试实例化
        adapter = LangGraphNativeMCPAdapter()
        print("   ✅ LangGraphNativeMCPAdapter 实例化成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ LangGraph架构测试失败: {e}")
        return False

def test_shared_components():
    """测试共享组件"""
    print("🧪 测试共享组件...")
    
    # 检查共享目录结构
    shared_dir = project_root / "shared"
    
    if not shared_dir.exists():
        print("   ❌ shared目录不存在")
        return False
    
    utils_dir = shared_dir / "utils"
    if utils_dir.exists():
        print("   ✅ shared/utils 目录存在")
        utils_files = list(utils_dir.glob("*.py"))
        print(f"   📋 工具文件数量: {len(utils_files)}")
    
    tools_dir = shared_dir / "tools"
    if tools_dir.exists():
        print("   ✅ shared/tools 目录存在")
    
    return True

def test_unified_launcher():
    """测试统一启动器"""
    print("🧪 测试统一启动器...")
    
    launcher_path = project_root / "launch.py"
    if not launcher_path.exists():
        print("   ❌ launch.py 不存在")
        return False
    
    print("   ✅ launch.py 存在")
    
    # 读取内容检查
    content = launcher_path.read_text()
    if "standard" in content and "langgraph" in content:
        print("   ✅ 启动器包含两个架构支持")
        return True
    else:
        print("   ❌ 启动器内容不完整")
        return False

def test_architecture_isolation():
    """测试架构隔离性"""
    print("🧪 测试架构隔离性...")
    
    arch_dir = project_root / "architectures"
    if not arch_dir.exists():
        print("   ❌ architectures目录不存在")
        return False
    
    standard_dir = arch_dir / "standard"
    langgraph_dir = arch_dir / "langgraph_native"
    
    if standard_dir.exists():
        print("   ✅ architectures/standard 存在")
        
        # 检查关键文件
        key_files = ["run.py", "config.json", "README.md"]
        for file in key_files:
            if (standard_dir / file).exists():
                print(f"     ✅ {file} 存在")
            else:
                print(f"     ⚠️ {file} 缺失")
    
    if langgraph_dir.exists():
        print("   ✅ architectures/langgraph_native 存在")
        
        # 检查关键文件
        key_files = ["run.py", "config.json", "README.md"]
        for file in key_files:
            if (langgraph_dir / file).exists():
                print(f"     ✅ {file} 存在")
            else:
                print(f"     ⚠️ {file} 缺失")
    
    return True

def test_backup_integrity():
    """测试备份完整性"""
    print("🧪 测试备份完整性...")
    
    original_backup = project_root / "original_backup"
    cleanup_backup = project_root / "cleanup_backup"
    
    if original_backup.exists():
        print("   ✅ original_backup 存在")
        backup_files = list(original_backup.rglob("*"))
        print(f"     📋 备份文件数: {len(backup_files)}")
    else:
        print("   ❌ original_backup 不存在")
    
    if cleanup_backup.exists():
        print("   ✅ cleanup_backup 存在")
        cleanup_files = list(cleanup_backup.rglob("*"))
        print(f"     📋 清理备份文件数: {len(cleanup_files)}")
    else:
        print("   ⚠️ cleanup_backup 不存在")
    
    return True

def main():
    """主测试函数"""
    print("🚀 架构分离后快速验证测试")
    print("=" * 60)
    
    tests = [
        ("标准架构组件测试", test_standard_architecture),
        ("LangGraph架构组件测试", test_langgraph_architecture),
        ("共享组件测试", test_shared_components),
        ("统一启动器测试", test_unified_launcher),
        ("架构隔离性测试", test_architecture_isolation),
        ("备份完整性测试", test_backup_integrity)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过! 架构分离成功完成!")
    elif passed >= total * 0.8:
        print("⚠️ 大部分测试通过，需要修复少量问题")
    else:
        print("❌ 多个测试失败，需要进一步调试")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)