#!/usr/bin/env python3
"""
智能工具选择器基本使用示例
Basic Usage Example for Intelligent Tool Selector
"""

import asyncio
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from intelligent_tool_selector import IntelligentToolSelector


async def basic_example():
    """基本使用示例"""
    
    print("🚀 智能工具选择器基本使用示例")
    print("=" * 60)
    
    # 1. 创建智能工具选择器
    selector = IntelligentToolSelector()
    
    # 2. 初始化（加载工具定义）
    print("📡 正在连接MCP服务器并加载工具...")
    success = await selector.initialize()
    
    if not success:
        print("❌ 初始化失败，请检查MCP服务器连接")
        return
    
    print(f"✅ 成功加载 {selector.get_tools_count()} 个工具")
    
    # 3. 测试查询
    test_queries = [
        "搜索平安银行的股票信息",
        "获取腾讯控股的港股行情数据",
        "查询贵州茅台的财务指标",
        "搜索所有银行类股票"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 测试 {i}: {query}")
        print("-" * 40)
        
        # 智能选择并执行工具
        result = await selector.select_and_execute_tool(query)
        
        if result['success']:
            execution_result = result['execution_result']
            selection_result = result['selection_result']
            
            print(f"🎯 选择工具: {execution_result['tool_name']}")
            print(f"📝 使用参数: {execution_result['parameters']}")
            print(f"💡 选择理由: {selection_result['tool_selection']['primary_tool']['reason']}")
            print(f"✅ 执行状态: {execution_result['message']}")
            
            # 显示响应预览
            if execution_result['response']:
                response_str = str(execution_result['response'])
                preview = response_str[:200] + "..." if len(response_str) > 200 else response_str
                print(f"📄 响应预览: {preview}")
        else:
            print(f"❌ 执行失败: {result['error']}")


async def search_tools_example():
    """搜索工具示例"""
    
    print(f"\n🔍 工具搜索示例")
    print("=" * 60)
    
    selector = IntelligentToolSelector()
    await selector.initialize()
    
    # 搜索包含"银行"关键词的工具
    matching_tools = selector.search_tools("银行")
    
    print(f"搜索关键词: '银行'")
    print(f"找到 {len(matching_tools)} 个相关工具:")
    
    for tool in matching_tools[:5]:  # 只显示前5个
        print(f"  - {tool['name']}: {tool['description']}")


async def tool_info_example():
    """获取工具信息示例"""
    
    print(f"\n📋 工具信息示例")
    print("=" * 60)
    
    selector = IntelligentToolSelector()
    await selector.initialize()
    
    # 获取特定工具的详细信息
    tool_name = "tushareMcp_get_stock_basic_info"
    tool_info = selector.get_tool_info(tool_name)
    
    if tool_info:
        print(f"工具名称: {tool_info['name']}")
        print(f"工具描述: {tool_info['description']}")
        print(f"参数列表:")
        
        for param_name, param_info in tool_info['parameters'].items():
            required = "必需" if param_info['required'] else "可选"
            print(f"  - {param_name} ({param_info['type']}, {required}): {param_info['description']}")
    else:
        print(f"未找到工具: {tool_name}")


async def main():
    """主函数"""
    try:
        await basic_example()
        await search_tools_example()
        await tool_info_example()
        
        print(f"\n🎉 示例运行完成!")
        print(f"💡 智能工具选择器的优势:")
        print(f"  - 🧠 自动理解用户意图")
        print(f"  - 🎯 智能选择最合适的工具")
        print(f"  - 📊 自动组装工具参数")
        print(f"  - 🔧 处理各种格式问题")
        print(f"  - ✅ 一站式工具调用解决方案")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 