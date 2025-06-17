"""
多轮工具调用使用示例
Multi-turn Tool Calling Usage Example

演示如何使用多轮工具选择器处理复杂查询
"""

import asyncio
import json
from typing import Dict, Any

# 导入多轮工具选择器
try:
    from intelligent_tool_selector import MultiTurnToolSelector
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from intelligent_tool_selector import MultiTurnToolSelector


async def test_multi_turn_selector():
    """测试多轮工具选择器"""
    print("🚀 多轮工具选择器测试开始\n")
    
    # 创建多轮选择器
    selector = MultiTurnToolSelector()
    
    # 初始化
    success = await selector.initialize()
    if not success:
        print("❌ 多轮工具选择器初始化失败")
        return
    
    # 测试案例：复杂的金融分析查询
    complex_queries = [
        "分析平安银行的投资价值，包括基本面、财务指标和技术面分析",
        "比较腾讯控股和阿里巴巴的投资价值，给出详细对比分析",
        "查询新能源汽车板块的龙头股票，并分析其未来发展前景",
        "搜索游戏概念股票并分析其当前市场表现和投资机会"
    ]
    
    for i, query in enumerate(complex_queries, 1):
        print(f"\n{'='*60}")
        print(f"🧪 测试案例 {i}: {query}")
        print(f"{'='*60}")
        
        try:
            # 执行多轮调用
            result = await selector.multi_turn_execution(query)
            
            # 输出结果摘要
            print_result_summary(result)
            
            # 重置上下文，准备下一个测试
            selector.reset_context()
            
        except Exception as e:
            print(f"❌ 测试案例 {i} 执行失败: {e}")
        
        print("\n" + "-"*60)
    
    print("\n🎉 多轮工具选择器测试完成")


def print_result_summary(result: Dict[str, Any]):
    """打印结果摘要"""
    print(f"\n📊 执行结果摘要:")
    print(f"   类型: {result.get('type', 'unknown')}")
    print(f"   成功: {'✅' if result.get('success') else '❌'}")
    
    if result.get('type') == 'multi_turn':
        # 多轮执行结果
        task_plan = result.get('task_plan', {})
        execution_summary = result.get('execution_summary', {})
        
        print(f"   任务分解: {'成功' if task_plan.get('is_complex') else '失败'}")
        if task_plan.get('sub_tasks'):
            print(f"   子任务数: {len(task_plan['sub_tasks'])}")
        
        print(f"   执行轮次: {result.get('turns_executed', 0)}")
        print(f"   成功任务: {execution_summary.get('completed_tasks', 0)}")
        print(f"   失败任务: {execution_summary.get('failed_tasks', 0)}")
        
        # 显示最终分析结果预览
        final_result = result.get('final_result', {})
        if final_result.get('success') and 'integrated_analysis' in final_result:
            analysis_preview = final_result['integrated_analysis'][:200] + "..."
            print(f"   分析预览: {analysis_preview}")
    
    elif result.get('type') == 'single_turn_fallback':
        # 单轮回退结果
        print(f"   回退原因: 任务无法分解")
        execution_result = result.get('execution_result', {})
        if execution_result:
            print(f"   使用工具: {execution_result.get('tool_name', '未知')}")


async def test_conversation_context():
    """测试对话上下文功能"""
    print("\n🧠 对话上下文测试开始")
    
    selector = MultiTurnToolSelector()
    await selector.initialize()
    
    # 执行几个相关查询
    queries = [
        "搜索平安银行的基本信息",
        "查询平安银行的财务指标",
        "分析平安银行的投资价值"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        result = await selector.multi_turn_execution(query)
        print(f"结果: {'成功' if result.get('success') else '失败'}")
    
    # 查看上下文历史
    context = selector.get_conversation_context()
    history = selector.get_execution_history()
    
    print(f"\n📚 对话上下文 ({len(context)} 条):")
    for i, ctx in enumerate(context, 1):
        print(f"   {i}. {ctx['query']} -> {ctx['tool_used']} ({'成功' if ctx['success'] else '失败'})")
    
    print(f"\n📜 执行历史 ({len(history)} 条):")
    for i, hist in enumerate(history, 1):
        task = hist.get('task', {})
        result = hist.get('result', {})
        print(f"   {i}. 轮次{hist['turn']}: {task.get('description', '未知任务')} ({'成功' if result.get('success') else '失败'})")


async def interactive_multi_turn_demo():
    """交互式多轮演示"""
    print("\n🎮 交互式多轮演示模式")
    print("输入复杂查询，系统将自动分解并执行多轮工具调用")
    print("输入 'quit' 退出")
    
    selector = MultiTurnToolSelector()
    await selector.initialize()
    
    while True:
        try:
            query = input("\n请输入您的查询: ").strip()
            
            if query.lower() == 'quit':
                break
            
            if not query:
                continue
            
            print(f"\n🔄 处理查询: {query}")
            result = await selector.multi_turn_execution(query)
            
            # 显示详细结果
            if result.get('success'):
                if result.get('type') == 'multi_turn':
                    final_result = result.get('final_result', {})
                    if final_result.get('success'):
                        print("\n📝 综合分析结果:")
                        print(final_result.get('integrated_analysis', '无分析结果'))
                    else:
                        print("\n⚠️ 结果整合失败，显示原始结果")
                        execution_summary = result.get('execution_summary', {})
                        for task_result in execution_summary.get('task_results', []):
                            if task_result['result'].get('success'):
                                execution_result = task_result['result'].get('execution_result', {})
                                print(f"\n{task_result['task'].get('description', '')}:")
                                print(f"工具: {execution_result.get('tool_name', '')}")
                                print(f"结果: {str(execution_result.get('response', ''))[:300]}...")
                else:
                    execution_result = result.get('execution_result', {})
                    print(f"\n使用工具: {execution_result.get('tool_name', '')}")
                    print(f"结果: {str(execution_result.get('response', ''))[:500]}...")
            else:
                print(f"\n❌ 执行失败: {result.get('error', '未知错误')}")
            
            # 显示执行统计
            print_result_summary(result)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 处理查询时出错: {e}")
    
    print("\n👋 演示结束")


async def main():
    """主函数"""
    print("🔧 多轮工具调用系统演示")
    print("选择演示模式:")
    print("1. 自动测试模式")
    print("2. 上下文测试模式") 
    print("3. 交互式演示模式")
    
    try:
        choice = input("\n请选择模式 (1-3): ").strip()
        
        if choice == "1":
            await test_multi_turn_selector()
        elif choice == "2":
            await test_conversation_context()
        elif choice == "3":
            await interactive_multi_turn_demo()
        else:
            print("无效选择，执行默认测试模式")
            await test_multi_turn_selector()
            
    except KeyboardInterrupt:
        print("\n👋 程序退出")
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 