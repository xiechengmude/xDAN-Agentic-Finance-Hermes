#!/usr/bin/env python3
"""
并行执行功能演示
Parallel Execution Demo
"""

import asyncio
import time
from intelligent_tool_selector import MultiTurnToolSelector


def print_banner(title: str):
    """打印标题横幅"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """打印段落标题"""
    print(f"\n{'-'*40}")
    print(f"📋 {title}")
    print(f"{'-'*40}")


async def demo_parallel_optimization():
    """演示并行执行优化"""
    print_banner("并行执行优化演示")
    
    print("🎯 本演示将展示多轮工具调用系统的并行执行优化功能")
    print("   - 智能依赖分析")
    print("   - 自动任务层级划分") 
    print("   - 并行执行与性能提升")
    print("   - 错误处理和回退机制")
    
    # 创建并行和串行选择器进行对比
    parallel_selector = MultiTurnToolSelector(
        enable_parallel=True,
        max_concurrent_tasks=3
    )
    
    print_section("初始化系统")
    await parallel_selector.initialize()
    
    # 测试案例
    demo_cases = [
        {
            "name": "📊 投资价值分析",
            "query": "分析比亚迪的投资价值，包括基本面、财务指标和技术分析",
            "description": "复杂查询，预期可以并行执行多个独立的数据获取任务"
        },
        {
            "name": "⚖️ 股票对比分析",
            "query": "比较腾讯控股和阿里巴巴的投资价值",
            "description": "对比查询，两个公司的数据获取可以并行进行"
        },
        {
            "name": "🔍 简单查询",
            "query": "搜索平安银行的基本信息",
            "description": "简单查询，预期会回退到单轮模式"
        }
    ]
    
    for i, case in enumerate(demo_cases, 1):
        print_section(f"案例 {i}: {case['name']}")
        print(f"🎯 查询: {case['query']}")
        print(f"💡 说明: {case['description']}")
        
        start_time = time.time()
        
        # 执行查询
        result = await parallel_selector.multi_turn_execution(case['query'])
        
        execution_time = time.time() - start_time
        
        # 显示结果
        print(f"\n📊 执行结果:")
        print(f"   ⏱️  执行时间: {execution_time:.2f} 秒")
        print(f"   ✅ 执行成功: {result.get('success')}")
        print(f"   🔧 执行类型: {result.get('type', 'unknown')}")
        
        if result.get('execution_summary'):
            summary = result['execution_summary']
            execution_mode = summary.get('execution_mode', 'unknown')
            completed = summary.get('completed_tasks', 0)
            total = summary.get('total_tasks', 0)
            
            print(f"   🚀 执行模式: {execution_mode}")
            print(f"   📈 成功率: {completed}/{total} ({completed/total*100:.1f}%)" if total > 0 else "   📈 成功率: N/A")
            
            # 分析执行模式
            if 'parallel' in execution_mode:
                print(f"   🎉 成功使用并行执行优化!")
            elif 'serial' in execution_mode:
                print(f"   ⚠️  回退到串行执行模式")
            else:
                print(f"   🔄 使用单轮执行模式")
        
        # 重置上下文准备下一个测试
        parallel_selector.reset_context()
        
        # 添加延迟避免过快请求
        if i < len(demo_cases):
            print("   💤 等待3秒后进行下一个测试...")
            await asyncio.sleep(3)


async def demo_dependency_analysis():
    """演示依赖分析功能"""
    print_banner("依赖分析功能演示")
    
    from intelligent_tool_selector.core.parallel_executor import ParallelExecutor
    
    executor = ParallelExecutor(max_concurrent_tasks=3)
    
    print("🧠 本演示将展示系统如何分析任务依赖关系并优化执行计划")
    
    # 模拟一个复杂的投资分析任务
    investment_analysis_tasks = [
        {
            "step": 1,
            "description": "获取公司基本信息",
            "query": "获取比亚迪基本信息、行业分类",
            "dependency": None
        },
        {
            "step": 2,
            "description": "财务数据分析",
            "query": "获取最近四个季度财务数据",
            "dependency": "step1"
        },
        {
            "step": 3,
            "description": "技术分析指标",
            "query": "获取技术分析指标（均线、MACD等）",
            "dependency": "step1"
        },
        {
            "step": 4,
            "description": "市场表现分析",
            "query": "获取市场表现数据（换手率、市盈率等）",
            "dependency": "step1"
        },
        {
            "step": 5,
            "description": "行业对比分析",
            "query": "对比同行业公司表现",
            "dependency": "step2"
        },
        {
            "step": 6,
            "description": "投资建议生成",
            "query": "基于所有数据生成投资建议",
            "dependency": "step5"
        }
    ]
    
    print_section("任务依赖关系")
    for task in investment_analysis_tasks:
        dependency_info = f"依赖: {task['dependency']}" if task['dependency'] else "无依赖"
        print(f"   📋 步骤{task['step']}: {task['description']} ({dependency_info})")
    
    print_section("依赖分析结果")
    
    # 分析依赖关系
    analysis = executor.analyze_task_dependencies(investment_analysis_tasks)
    
    print(f"🔗 可并行化: {'✅ 是' if analysis['parallelizable'] else '❌ 否'}")
    print(f"🔄 循环依赖: {'❌ 检测到' if analysis['has_cycles'] else '✅ 无'}")
    print(f"📊 执行层级: {len(analysis['execution_levels'])} 层")
    
    print_section("执行层级规划")
    for i, level in enumerate(analysis['execution_levels'], 1):
        tasks_in_level = []
        for task in level:
            tasks_in_level.append(f"步骤{task['step']}: {task['description']}")
        
        print(f"🔧 层级 {i} ({len(level)} 个并行任务):")
        for task_desc in tasks_in_level:
            print(f"   • {task_desc}")
    
    # 生成优化计划
    optimization_plan = executor.optimize_execution_plan(investment_analysis_tasks)
    
    print_section("性能优化分析")
    if optimization_plan['can_parallelize']:
        total_tasks = optimization_plan['total_tasks']
        parallel_levels = optimization_plan['parallel_levels']
        time_reduction = optimization_plan['estimated_time_reduction']
        
        print(f"📈 总任务数: {total_tasks}")
        print(f"🚀 并行层级: {parallel_levels}")
        print(f"⚡ 预估加速: {time_reduction:.1%}")
        print(f"📊 理论耗时: 串行 {total_tasks} 单位 → 并行 {parallel_levels} 单位")
        print(f"🎉 性能提升显著! 建议使用并行执行")
    else:
        print(f"⚠️  无法并行化原因: {optimization_plan.get('reason', '未知')}")
        print(f"🔄 建议使用串行执行模式")


async def main():
    """主演示函数"""
    print("🚀 欢迎使用xDAN智能工具选择器并行执行演示!")
    print("    本演示将展示多轮工具调用的并行执行优化功能")
    
    try:
        # 依赖分析演示
        await demo_dependency_analysis()
        
        # 等待用户继续
        input("\n⏳ 按回车键继续实际执行演示...")
        
        # 并行执行演示
        await demo_parallel_optimization()
        
        print_banner("演示完成")
        print("🎉 并行执行优化演示已完成!")
        print("    主要收获:")
        print("    ✅ 了解了智能依赖分析机制")
        print("    ✅ 观察了并行执行的性能提升")
        print("    ✅ 体验了自动回退和错误处理")
        print("    ✅ 看到了不同查询类型的执行策略")
        
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 