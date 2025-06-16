#!/usr/bin/env python3
"""
xDAN-Agentic-Search-Test 主程序入口
使用智能工具选择器进行交互式查询，支持单轮和多轮模式
"""

import asyncio
import sys
from intelligent_tool_selector import IntelligentToolSelector, MultiTurnToolSelector


async def interactive_mode():
    """交互式模式"""
    print("🚀 欢迎使用 xDAN 智能工具选择器!")
    print("=" * 60)
    print("💡 输入您的查询，系统将自动选择最合适的工具")
    print("🔍 支持股票查询、财务数据、港股信息等")
    print("🧠 智能识别复杂查询并自动执行多轮工具调用")
    print("⏹️  输入 'exit' 或 'quit' 退出程序")
    print("=" * 60)
    
    # 初始化多轮智能工具选择器
    multi_selector = MultiTurnToolSelector()
    
    print("\n📡 正在连接MCP服务器并加载工具...")
    success = await multi_selector.initialize()
    
    if not success:
        print("❌ 初始化失败，请检查MCP服务器连接")
        return
    
    print(f"✅ 成功加载 {multi_selector.single_turn_selector.get_tools_count()} 个工具，准备就绪！\n")
    
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
            print("⏳ 智能分析查询复杂度并选择执行模式...")
            
            # 使用多轮工具选择器（会自动判断是否需要多轮）
            result = await multi_selector.multi_turn_execution(user_query)
            
            if result['success']:
                print("\n✅ 执行成功!")
                print(f"🔧 执行模式: {result.get('type', 'unknown')}")
                
                if result.get('type') == 'multi_turn':
                    # 多轮执行结果
                    print(f"🔄 执行轮次: {result.get('turns_executed', 0)}")
                    execution_summary = result.get('execution_summary', {})
                    print(f"✅ 成功任务: {execution_summary.get('completed_tasks', 0)}")
                    print(f"❌ 失败任务: {execution_summary.get('failed_tasks', 0)}")
                    
                    # 显示最终综合分析结果
                    final_result = result.get('final_result', {})
                    if final_result.get('success') and 'integrated_analysis' in final_result:
                        print(f"\n📊 综合分析结果:")
                        analysis = final_result['integrated_analysis']
                        if len(analysis) > 1000:
                            preview = analysis[:1000] + "..."
                            print(preview)
                            print(f"\n💬 完整分析报告共 {len(analysis)} 个字符")
                        else:
                            print(analysis)
                    else:
                        print(f"\n⚠️ 结果整合失败，显示原始结果摘要")
                        for task_result in execution_summary.get('task_results', [])[:3]:
                            if task_result['result'].get('success'):
                                task = task_result['task']
                                exec_result = task_result['result'].get('execution_result', {})
                                print(f"\n📋 {task.get('description', '')}:")
                                print(f"   🔧 工具: {exec_result.get('tool_name', '未知')}")
                                response_preview = str(exec_result.get('response', ''))[:200] + "..."
                                print(f"   📄 结果: {response_preview}")
                                
                elif result.get('type') in ['single_turn_fallback', 'single_turn']:
                    # 单轮执行结果
                    execution_result = result.get('execution_result', {})
                    selection_result = result.get('selection_result', {})
                    
                    print(f"🎯 选择工具: {execution_result.get('tool_name', '未知')}")
                    print(f"📝 使用参数: {execution_result.get('parameters', {})}")
                    
                    if selection_result and 'tool_selection' in selection_result:
                        reason = selection_result['tool_selection']['primary_tool']['reason']
                        print(f"💡 选择理由: {reason}")
                    
                    # 显示结果预览
                    if execution_result.get('response'):
                        response_str = str(execution_result['response'])
                        if len(response_str) > 500:
                            preview = response_str[:500] + "..."
                            print(f"\n📄 结果预览:\n{preview}")
                            print(f"\n💬 完整结果已获取，共 {len(response_str)} 个字符")
                        else:
                            print(f"\n📄 执行结果:\n{response_str}")
                
            else:
                print(f"\n❌ 执行失败: {result.get('error', '未知错误')}")
            
            print("\n" + "─" * 60)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 用户中断程序")
            break
        except Exception as e:
            print(f"\n❌ 程序执行出错: {e}")
            print("请重试或输入 'exit' 退出")


async def demo_mode():
    """演示模式"""
    print("🎬 演示模式 - 多轮智能工具选择器")
    print("=" * 60)
    
    # 初始化
    multi_selector = MultiTurnToolSelector()
    
    print("📡 初始化多轮智能工具选择器...")
    success = await multi_selector.initialize()
    
    if not success:
        print("❌ 初始化失败")
        return
    
    print(f"✅ 成功加载 {multi_selector.single_turn_selector.get_tools_count()} 个工具")
    
    # 演示查询（包含简单和复杂查询）
    demo_queries = [
        "搜索平安银行的股票信息",  # 简单查询
        "分析比亚迪的投资价值，包括基本面和财务数据",  # 复杂查询
        "获取腾讯控股的港股行情数据",  # 简单查询
        "比较招商银行和平安银行的投资价值"  # 复杂查询
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n📋 演示 {i}/{len(demo_queries)}: {query}")
        print("-" * 40)
        
        result = await multi_selector.multi_turn_execution(query)
        
        if result['success']:
            print(f"🔧 执行模式: {result.get('type', 'unknown')}")
            
            if result.get('type') == 'multi_turn':
                # 多轮执行
                print(f"🔄 执行轮次: {result.get('turns_executed', 0)}")
                execution_summary = result.get('execution_summary', {})
                print(f"✅ 成功任务: {execution_summary.get('completed_tasks', 0)}")
                
                # 显示部分综合分析结果
                final_result = result.get('final_result', {})
                if final_result.get('success') and 'integrated_analysis' in final_result:
                    analysis_preview = final_result['integrated_analysis'][:300] + "..."
                    print(f"📊 分析预览: {analysis_preview}")
                    
            else:
                # 单轮执行
                execution_result = result.get('execution_result', {})
                print(f"🎯 选择工具: {execution_result.get('tool_name', '未知')}")
                print(f"✅ 执行状态: {execution_result.get('message', '执行完成')}")
        else:
            print(f"❌ 执行失败: {result.get('error', '未知错误')}")
        
        if i < len(demo_queries):
            await asyncio.sleep(3)  # 演示间隔
    
    print("\n🎉 演示完成!")


async def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            await demo_mode()
        elif sys.argv[1] == "multi":
            # 直接启动多轮演示
            print("🔧 多轮工具调用专用演示")
            from intelligent_tool_selector.examples.multi_turn_usage import main as multi_main
            await multi_main()
        else:
            print("可用参数: demo (演示模式), multi (多轮演示)")
            await interactive_mode()
    else:
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序启动失败: {e}")
