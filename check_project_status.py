#!/usr/bin/env python3
"""
项目状态检查脚本
Project Status Check Script

检查项目的完整性和可运行性
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_files_exist():
    """检查关键文件是否存在"""
    print("📁 检查关键文件...")
    
    required_files = [
        "main.py",
        "README.md",
        "requirements.txt",
        "pyproject.toml",
        "intelligent_tool_selector/__init__.py",
        "intelligent_tool_selector/core/selector.py",
        "intelligent_tool_selector/core/json_parser.py",
        "intelligent_tool_selector/utils/config.py",
        "intelligent_tool_selector/utils/mcp_client.py",
        "intelligent_tool_selector/examples/basic_usage.py",
        "intelligent_tool_selector/tests/test_selector.py",
        "tools/__init__.py",
        "tools/xdan_finance_tools_info.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少以下文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ 所有关键文件都存在")
        return True

def check_virtual_env():
    """检查虚拟环境"""
    print("\n🐍 检查虚拟环境...")
    
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ 虚拟环境不存在")
        return False
    
    print("✅ 虚拟环境存在")
    return True

def check_dependencies():
    """检查依赖是否安装"""
    print("\n📦 检查依赖...")
    
    try:
        # 激活虚拟环境并检查关键包
        result = subprocess.run([
            "bash", "-c", 
            "source .venv/bin/activate && python -c 'import openai, fastmcp; print(\"✅ 关键依赖已安装\")'"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print("❌ 依赖检查失败:")
            print(result.stderr.strip())
            return False
    except Exception as e:
        print(f"❌ 依赖检查出错: {e}")
        return False

def check_module_imports():
    """检查模块导入"""
    print("\n🔌 检查模块导入...")
    
    try:
        result = subprocess.run([
            "bash", "-c", 
            "source .venv/bin/activate && python -c 'from intelligent_tool_selector import IntelligentToolSelector, Config; from tools import load_tools_info; print(\"✅ 模块导入成功\")'"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 所有关键模块导入成功")
            return True
        else:
            print("❌ 模块导入失败:")
            print(result.stderr.strip())
            return False
    except Exception as e:
        print(f"❌ 模块导入检查出错: {e}")
        return False

def check_tools_loading():
    """检查工具加载"""
    print("\n🔧 检查工具加载...")
    
    try:
        result = subprocess.run([
            "bash", "-c", 
            "source .venv/bin/activate && python -c 'from tools import load_tools_info; tools = load_tools_info(); print(f\"✅ 成功加载 {len(tools)} 个工具信息\")'"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print("❌ 工具加载失败:")
            print(result.stderr.strip())
            return False
    except Exception as e:
        print(f"❌ 工具加载检查出错: {e}")
        return False

def check_main_program():
    """检查主程序"""
    print("\n🚀 检查主程序...")
    
    try:
        result = subprocess.run([
            "bash", "-c", 
            "source .venv/bin/activate && echo 'quit' | python main.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "成功加载" in result.stdout:
            print("✅ 主程序可正常启动")
            return True
        else:
            print("❌ 主程序启动失败:")
            print(result.stderr.strip())
            return False
    except Exception as e:
        print(f"❌ 主程序检查出错: {e}")
        return False

def main():
    """主函数"""
    print("🔍 xDAN-Agentic-Search-Test 项目状态检查")
    print("=" * 60)
    
    checks = [
        ("文件完整性", check_files_exist),
        ("虚拟环境", check_virtual_env),
        ("依赖安装", check_dependencies),
        ("模块导入", check_module_imports),
        ("工具加载", check_tools_loading),
        ("主程序", check_main_program)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查出错: {e}")
            results.append((name, False))
    
    # 总结报告
    print("\n📊 检查结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:.<20} {status}")
    
    print("-" * 60)
    print(f"总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 项目状态良好，可以正常使用！")
        
        print("\n🚀 快速开始:")
        print("  交互模式: python main.py")
        print("  演示模式: python main.py demo")
        print("  运行示例: python intelligent_tool_selector/examples/basic_usage.py")
        
        return True
    else:
        print("⚠️ 项目存在问题，请检查失败的项目")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 