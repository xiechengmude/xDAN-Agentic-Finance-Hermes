#!/usr/bin/env python3
"""
并行执行优化测试
Test Parallel Execution Optimization
"""

import asyncio
import time
from intelligent_tool_selector import MultiTurnToolSelector


async def test_parallel_vs_serial():
    """测试并行执行与串行执行的性能对比"""
    print("🚀 并行执行优化测试")
    print("=" * 60)
    
    # 创建两个选择器：并行和串行
    parallel_selector = MultiTurnToolSelector(
        enable_parallel=True,
        max_concurrent_tasks=3
    )
    
    serial_selector = MultiTurnToolSelector(
        enable_parallel=False  # 禁用并行
    )
    
    # 初始化
    print("📡 初始化选择器...")
    await parallel_selector.initialize()
    await serial_selector.initialize()
    
    # 测试查询 - 选择有多个独立子任务的复杂查询
    test_query = "比较腾讯控股和阿里巴巴的投资价值，给出详细对比分析"
    
    print(f"\n🔍 测试查询: {test_query}")
    print("\n" + "="*60)
    
    # 测试串行执行
    print("📋 1. 串行执行测试")
    print("-" * 40)
    start_time = time.time()
    
    serial_result = await serial_selector.multi_turn_execution(test_query)
    
    serial_time = time.time() - start_time
    
    print(f"⏱️ 串行执行耗时: {serial_time:.2f} 秒")
    print(f"✅ 串行执行成功: {serial_result.get('success')}")
    if serial_result.get('execution_summary'):
        summary = serial_result['execution_summary']
        print(f"📊 成功/总数: {summary.get('completed_tasks', 0)}/{summary.get('total_tasks', 0)}")
        print(f"🔧 执行模式: {summary.get('execution_mode', 'unknown')}")
    
    # 重置上下文
    serial_selector.reset_context()
    
    print("\n" + "="*60)
    
    # 测试并行执行
    print("📋 2. 并行执行测试")
    print("-" * 40)
    start_time = time.time()
    
    parallel_result = await parallel_selector.multi_turn_execution(test_query)
    
    parallel_time = time.time() - start_time
    
    print(f"⏱️ 并行执行耗时: {parallel_time:.2f} 秒")
    print(f"✅ 并行执行成功: {parallel_result.get('success')}")
    if parallel_result.get('execution_summary'):
        summary = parallel_result['execution_summary']
        print(f"📊 成功/总数: {summary.get('completed_tasks', 0)}/{summary.get('total_tasks', 0)}")
        print(f"🔧 执行模式: {summary.get('execution_mode', 'unknown')}")
    
    # 性能对比
    print("\n" + "="*60)
    print("📈 性能对比结果")
    print("-" * 40)
    
    if parallel_time > 0 and serial_time > 0:
        speedup = serial_time / parallel_time
        time_saved = serial_time - parallel_time
        improvement = (time_saved / serial_time) * 100
        
        print(f"🚀 加速比: {speedup:.2f}x")
        print(f"⏰ 节省时间: {time_saved:.2f} 秒")
        print(f"📊 性能提升: {improvement:.1f}%")
        
        if speedup > 1.2:
            print("🎉 并行执行显著提升性能！")
        elif speedup > 1.0:
            print("✅ 并行执行略有提升")
        else:
            print("⚠️ 并行执行未能提升性能")
    else:
        print("❌ 无法计算性能对比")


async def test_dependency_analysis():
    """测试依赖分析功能"""
    print("\n🧠 依赖分析测试")
    print("=" * 60)
    
    from intelligent_tool_selector.core.parallel_executor import ParallelExecutor
    
    executor = ParallelExecutor()
    
    # 模拟复杂的任务依赖
    complex_tasks = [
        {
            "step": 1,
            "description": "获取基本信息",
            "query": "搜索公司基本信息",
            "dependency": None
        },
        {
            "step": 2,
            "description": "获取财务数据",
            "query": "查询财务指标",
            "dependency": "step1"
        },
        {
            "step": 3,
            "description": "获取市场数据", 
            "query": "获取市场行情",
            "dependency": "step1"
        },
        {
            "step": 4,
            "description": "技术分析",
            "query": "技术指标分析",
            "dependency": "step1"
        },
        {
            "step": 5,
            "description": "综合评估",
            "query": "投资价值评估",
            "dependency": "step2"
        }
    ]
    
    print("📋 分析任务依赖关系...")
    analysis = executor.analyze_task_dependencies(complex_tasks)
    
    print(f"🔗 可并行化: {'✅' if analysis['parallelizable'] else '❌'}")
    print(f"🔄 循环依赖: {'❌' if analysis['has_cycles'] else '✅'}")
    print(f"📊 执行层级: {len(analysis['execution_levels'])} 层")
    
    for i, level in enumerate(analysis['execution_levels'], 1):
        task_descriptions = [task.get('description', '') for task in level]
        print(f"   层级 {i}: {len(level)} 个任务 - {', '.join(task_descriptions)}")
    
    # 生成优化计划
    plan = executor.optimize_execution_plan(complex_tasks)
    executor.print_optimization_summary(plan)


async def test_different_query_types():
    """测试不同类型查询的并行优化效果"""
    print("\n🎯 不同查询类型测试")
    print("=" * 60)
    
    selector = MultiTurnToolSelector(enable_parallel=True, max_concurrent_tasks=3)
    await selector.initialize()
    
    test_cases = [
        {
            "name": "投资价值分析",
            "query": "分析比亚迪的投资价值，包括基本面、财务指标和技术分析",
            "expected_parallel": True
        },
        {
            "name": "股票对比分析", 
            "query": "比较招商银行和平安银行的投资价值",
            "expected_parallel": True
        },
        {
            "name": "简单查询",
            "query": "搜索平安银行",
            "expected_parallel": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试案例 {i}: {test_case['name']}")
        print(f"🔍 查询: {test_case['query']}")
        print("-" * 40)
        
        start_time = time.time()
        result = await selector.multi_turn_execution(test_case['query'])
        execution_time = time.time() - start_time
        
        print(f"⏱️ 执行时间: {execution_time:.2f} 秒")
        print(f"✅ 执行成功: {result.get('success')}")
        print(f"🔧 执行类型: {result.get('type', 'unknown')}")
        
        if result.get('execution_summary'):
            execution_mode = result['execution_summary'].get('execution_mode', 'unknown')
            print(f"🚀 执行模式: {execution_mode}")
            
            parallel_achieved = 'parallel' in execution_mode
            expectation_met = parallel_achieved == test_case['expected_parallel']
            
            print(f"🎯 预期并行: {'✅' if test_case['expected_parallel'] else '❌'}")
            print(f"📊 实际并行: {'✅' if parallel_achieved else '❌'}")
            print(f"✅ 符合预期: {'✅' if expectation_met else '❌'}")
        
        selector.reset_context()


async def main():
    """主测试函数"""
    try:
        # 依赖分析测试
        await test_dependency_analysis()
        
        # 不同查询类型测试
        await test_different_query_types()
        
        # 性能对比测试（注释掉以避免耗时过长）
        # await test_parallel_vs_serial()
        
        print("\n🎉 并行执行测试完成！")
        
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 