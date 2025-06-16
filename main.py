#!/usr/bin/env python3
"""
xDAN-Agentic-Search-Test 主程序入口
使用智能工具选择器进行交互式查询
"""

import asyncio
import sys
from intelligent_tool_selector import IntelligentToolSelector


async def interactive_mode():
    """交互式模式"""
    print("🚀 欢迎使用 xDAN 智能工具选择器!")
    print("=" * 60)
    print("💡 输入您的查询，系统将自动选择最合适的工具")
    print("🔍 支持股票查询、财务数据、港股信息等")
    print("⏹️  输入 'exit' 或 'quit' 退出程序")
    print("=" * 60)
    
    # 初始化智能工具选择器
    selector = IntelligentToolSelector()
    
    print("\n📡 正在连接MCP服务器并加载工具...")
    success = await selector.initialize()
    
    if not success:
        print("❌ 初始化失败，请检查MCP服务器连接")
        return
    
    print(f"✅ 成功加载 {selector.get_tools_count()} 个工具，准备就绪！\n")
    
    while True:
        try:
            # 获取用户输入
            user_query = input("🔍 请输入您的查询: ").strip()
            
            # 检查退出条件
            if user_query.lower() in ['exit', 'quit', '退出']:
                print("👋 感谢使用，再见！")
                break
            
            if not user_query:
                print("⚠️ 请输入有效的查询内容")
                continue
            
            print(f"\n🤔 正在分析您的查询: {user_query}")
            print("⏳ 智能选择工具中...")
            
            # 智能选择并执行工具
            result = await selector.select_and_execute_tool(user_query)
            
            if result['success']:
                execution_result = result['execution_result']
                selection_result = result['selection_result']
                
                print("\n✅ 执行成功!")
                print(f"🎯 选择工具: {execution_result['tool_name']}")
                print(f"📝 使用参数: {execution_result['parameters']}")
                print(f"💡 选择理由: {selection_result['tool_selection']['primary_tool']['reason']}")
                
                # 显示结果预览
                if execution_result['response']:
                    response_str = str(execution_result['response'])
                    if len(response_str) > 500:
                        preview = response_str[:500] + "..."
                        print(f"\n📄 结果预览:\n{preview}")
                        print(f"\n💬 完整结果已获取，共 {len(response_str)} 个字符")
                    else:
                        print(f"\n📄 执行结果:\n{response_str}")
                
            else:
                print(f"\n❌ 执行失败: {result['error']}")
            
            print("\n" + "─" * 60)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 用户中断程序")
            break
        except Exception as e:
            print(f"\n❌ 程序执行出错: {e}")
            print("请重试或输入 'exit' 退出")


async def demo_mode():
    """演示模式"""
    print("🎬 演示模式 - 智能工具选择器")
    print("=" * 60)
    
    # 初始化
    selector = IntelligentToolSelector()
    
    print("📡 初始化智能工具选择器...")
    success = await selector.initialize()
    
    if not success:
        print("❌ 初始化失败")
        return
    
    print(f"✅ 成功加载 {selector.get_tools_count()} 个工具")
    
    # 演示查询
    demo_queries = [
        "搜索平安银行的股票信息",
        "获取腾讯控股的港股行情数据", 
        "查询贵州茅台的财务指标",
        "搜索所有银行类股票"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n📋 演示 {i}/{len(demo_queries)}: {query}")
        print("-" * 40)
        
        result = await selector.select_and_execute_tool(query)
        
        if result['success']:
            execution_result = result['execution_result']
            selection_result = result['selection_result']
            
            print(f"🎯 选择工具: {execution_result['tool_name']}")
            print(f"📝 使用参数: {execution_result['parameters']}")
            print(f"💡 选择理由: {selection_result['tool_selection']['primary_tool']['reason']}")
            print(f"✅ 执行状态: {execution_result['message']}")
        else:
            print(f"❌ 执行失败: {result['error']}")
        
        if i < len(demo_queries):
            await asyncio.sleep(2)  # 演示间隔
    
    print("\n🎉 演示完成!")


async def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        await demo_mode()
    else:
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序启动失败: {e}")
