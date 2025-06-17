"""
并行执行管理器
Parallel Execution Manager

提供任务依赖分析和并行执行优化功能
"""

import asyncio
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
import networkx as nx


class ParallelExecutor:
    """并行执行管理器"""
    
    def __init__(self, max_concurrent_tasks: int = 3):
        """
        初始化并行执行管理器
        
        Args:
            max_concurrent_tasks: 最大并发任务数
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.execution_semaphore = asyncio.Semaphore(max_concurrent_tasks)
    
    def analyze_task_dependencies(self, sub_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析任务依赖关系
        
        Args:
            sub_tasks: 子任务列表
            
        Returns:
            依赖分析结果
        """
        # 构建依赖图
        dependency_graph = nx.DiGraph()
        task_map = {}
        
        # 添加所有任务节点
        for task in sub_tasks:
            step = f"step{task.get('step', 0)}"
            task_map[step] = task
            dependency_graph.add_node(step, **task)
        
        # 添加依赖边
        for task in sub_tasks:
            current_step = f"step{task.get('step', 0)}"
            dependency = task.get('dependency')
            
            if dependency and dependency != 'null' and dependency != 'None':
                # 解析依赖关系
                if isinstance(dependency, str):
                    if 'step' in dependency:
                        dep_step = dependency
                    else:
                        dep_step = f"step{dependency}"
                    
                    if dep_step in task_map:
                        dependency_graph.add_edge(dep_step, current_step)
        
        # 检测循环依赖
        try:
            cycles = list(nx.simple_cycles(dependency_graph))
            has_cycles = len(cycles) > 0
        except:
            cycles = []
            has_cycles = False
        
        # 拓扑排序获取执行层级
        try:
            execution_levels = self._get_execution_levels(dependency_graph, task_map)
        except:
            # 如果拓扑排序失败，回退到串行执行
            execution_levels = [[task] for task in sub_tasks]
        
        return {
            'dependency_graph': dependency_graph,
            'task_map': task_map,
            'has_cycles': has_cycles,
            'cycles': cycles,
            'execution_levels': execution_levels,
            'parallelizable': not has_cycles and len(execution_levels) > 0
        }
    
    def _get_execution_levels(self, graph: nx.DiGraph, task_map: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """
        获取可并行执行的任务层级
        
        Args:
            graph: 依赖图
            task_map: 任务映射
            
        Returns:
            按层级组织的任务列表
        """
        levels = []
        remaining_nodes = set(graph.nodes())
        
        while remaining_nodes:
            # 找到当前层级中没有未满足依赖的节点
            current_level_nodes = []
            for node in remaining_nodes:
                predecessors = set(graph.predecessors(node))
                if predecessors.issubset(set(graph.nodes()) - remaining_nodes):
                    current_level_nodes.append(node)
            
            if not current_level_nodes:
                # 如果没有可执行的节点，可能存在循环依赖，破坏循环
                current_level_nodes = [list(remaining_nodes)[0]]
            
            # 将节点转换为任务对象
            current_level_tasks = [task_map[node] for node in current_level_nodes if node in task_map]
            if current_level_tasks:
                levels.append(current_level_tasks)
            
            # 从剩余节点中移除当前层级的节点
            remaining_nodes -= set(current_level_nodes)
        
        return levels
    
    async def execute_tasks_parallel(self, 
                                   tasks: List[Dict[str, Any]], 
                                   executor_func,
                                   context_updater=None) -> List[Dict[str, Any]]:
        """
        并行执行任务列表
        
        Args:
            tasks: 要执行的任务列表
            executor_func: 任务执行函数
            context_updater: 上下文更新函数
            
        Returns:
            执行结果列表
        """
        print(f"🔄 开始并行执行 {len(tasks)} 个任务...")
        
        async def execute_single_task(task: Dict[str, Any]) -> Dict[str, Any]:
            """执行单个任务"""
            async with self.execution_semaphore:
                try:
                    task_query = task.get('query', task.get('description', ''))
                    print(f"🎯 并行执行: {task.get('description', task_query)}")
                    
                    result = await executor_func(task_query)
                    
                    task_result = {
                        'turn': task.get('step', 0),
                        'task': task,
                        'result': result,
                        'timestamp': datetime.now().isoformat(),
                        'execution_mode': 'parallel'
                    }
                    
                    # 更新上下文
                    if context_updater and result.get('success'):
                        context_updater(task_query, result)
                    
                    status = "✅ 成功" if result.get('success') else "❌ 失败"
                    print(f"{status} 并行任务: {task.get('description', task_query)}")
                    
                    return task_result
                    
                except Exception as e:
                    print(f"❌ 并行任务执行异常: {e}")
                    return {
                        'turn': task.get('step', 0),
                        'task': task,
                        'result': {'success': False, 'error': str(e)},
                        'timestamp': datetime.now().isoformat(),
                        'execution_mode': 'parallel'
                    }
        
        # 创建并发任务
        concurrent_tasks = [execute_single_task(task) for task in tasks]
        
        # 等待所有任务完成
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'turn': tasks[i].get('step', 0),
                    'task': tasks[i],
                    'result': {'success': False, 'error': str(result)},
                    'timestamp': datetime.now().isoformat(),
                    'execution_mode': 'parallel'
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def execute_levels_parallel(self, 
                                    execution_levels: List[List[Dict[str, Any]]], 
                                    executor_func,
                                    context_updater=None) -> List[Dict[str, Any]]:
        """
        按层级并行执行任务
        
        Args:
            execution_levels: 按层级组织的任务
            executor_func: 任务执行函数
            context_updater: 上下文更新函数
            
        Returns:
            所有任务的执行结果
        """
        all_results = []
        
        for level_idx, level_tasks in enumerate(execution_levels, 1):
            print(f"\n🔧 执行第 {level_idx} 层级 ({len(level_tasks)} 个并行任务)")
            
            # 并行执行当前层级的所有任务
            level_results = await self.execute_tasks_parallel(
                level_tasks, executor_func, context_updater
            )
            
            all_results.extend(level_results)
            
            # 短暂延迟，让系统缓冲
            if level_idx < len(execution_levels):
                await asyncio.sleep(0.3)
        
        return all_results
    
    def optimize_execution_plan(self, sub_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        优化执行计划
        
        Args:
            sub_tasks: 子任务列表
            
        Returns:
            优化的执行计划
        """
        dependency_analysis = self.analyze_task_dependencies(sub_tasks)
        
        if dependency_analysis['parallelizable']:
            execution_levels = dependency_analysis['execution_levels']
            
            # 计算性能提升
            total_tasks = len(sub_tasks)
            max_parallel_in_level = max(len(level) for level in execution_levels)
            estimated_time_reduction = self._estimate_time_reduction(execution_levels)
            
            optimization_plan = {
                'can_parallelize': True,
                'execution_mode': 'parallel',
                'execution_levels': execution_levels,
                'total_tasks': total_tasks,
                'parallel_levels': len(execution_levels),
                'max_concurrent_tasks': min(max_parallel_in_level, self.max_concurrent_tasks),
                'estimated_time_reduction': estimated_time_reduction,
                'dependency_analysis': dependency_analysis
            }
        else:
            optimization_plan = {
                'can_parallelize': False,
                'execution_mode': 'serial',
                'reason': 'Circular dependencies detected' if dependency_analysis['has_cycles'] else 'Complex dependencies',
                'fallback_to_serial': True,
                'dependency_analysis': dependency_analysis
            }
        
        return optimization_plan
    
    def _estimate_time_reduction(self, execution_levels: List[List[Dict[str, Any]]]) -> float:
        """
        估算时间缩减比例
        
        Args:
            execution_levels: 执行层级
            
        Returns:
            时间缩减比例 (0-1)
        """
        total_tasks = sum(len(level) for level in execution_levels)
        if total_tasks <= 1:
            return 0.0
        
        # 串行执行时间 = 总任务数
        serial_time = total_tasks
        
        # 并行执行时间 = 层级数（每层并行执行）
        parallel_time = len(execution_levels)
        
        # 时间缩减比例
        time_reduction = (serial_time - parallel_time) / serial_time
        
        return max(0.0, min(1.0, time_reduction))
    
    def print_optimization_summary(self, optimization_plan: Dict[str, Any]):
        """打印优化摘要"""
        print(f"\n📊 并行执行优化分析:")
        print(f"   可并行化: {'✅' if optimization_plan['can_parallelize'] else '❌'}")
        
        if optimization_plan['can_parallelize']:
            print(f"   执行模式: {optimization_plan['execution_mode']}")
            print(f"   总任务数: {optimization_plan['total_tasks']}")
            print(f"   并行层级: {optimization_plan['parallel_levels']}")
            print(f"   最大并发: {optimization_plan['max_concurrent_tasks']}")
            print(f"   预估提速: {optimization_plan['estimated_time_reduction']:.1%}")
            
            # 显示执行层级
            for i, level in enumerate(optimization_plan['execution_levels'], 1):
                tasks_desc = [task.get('description', '')[:30] + '...' for task in level]
                print(f"   层级 {i}: {len(level)} 个任务 - {', '.join(tasks_desc)}")
        else:
            print(f"   回退原因: {optimization_plan.get('reason', '未知')}")
            print(f"   执行模式: 串行执行") 