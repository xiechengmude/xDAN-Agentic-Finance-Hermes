"""
多轮工具选择器核心模块
Multi-turn Tool Selector Core Module

提供多轮工具调用、任务规划和结果整合功能
"""

import asyncio
import openai
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..utils.config import Config
from ..utils.mcp_client import MCPClientManager
from .json_parser import JSONParser
from .selector import IntelligentToolSelector
from .parallel_executor import ParallelExecutor


class MultiTurnToolSelector:
    """多轮智能工具选择器"""
    
    def __init__(self, 
                 mcp_server_url: Optional[str] = None,
                 model_url: Optional[str] = None,
                 model_name: Optional[str] = None,
                 max_turns: int = 5,
                 enable_parallel: bool = True,
                 max_concurrent_tasks: int = 3):
        """
        初始化多轮工具选择器
        
        Args:
            mcp_server_url: MCP服务器URL
            model_url: 模型服务器URL
            model_name: 模型名称
            max_turns: 最大轮次
            enable_parallel: 是否启用并行执行
            max_concurrent_tasks: 最大并发任务数
        """
        # 继承单轮选择器的能力
        self.single_turn_selector = IntelligentToolSelector(
            mcp_server_url, model_url, model_name
        )
        
        # 配置初始化
        self.config = Config.from_env()
        if mcp_server_url:
            self.config['mcp_server_url'] = mcp_server_url
        if model_url:
            self.config['model_url'] = model_url
        if model_name:
            self.config['model_name'] = model_name
        
        Config.validate(self.config)
        
        # 模型客户端
        self.llm_client = openai.OpenAI(
            base_url=self.config['model_url'],
            api_key=self.config['model_api_key']
        )
        
        # JSON解析器
        self.json_parser = JSONParser()
        
        # 多轮配置
        self.max_turns = max_turns
        self.enable_parallel = enable_parallel
        
        # 并行执行器
        self.parallel_executor = ParallelExecutor(max_concurrent_tasks) if enable_parallel else None
        
        # 上下文记忆
        self.conversation_context = []
        self.execution_results = []
        
        # 状态
        self._initialized = False
    
    async def initialize(self) -> bool:
        """初始化多轮工具选择器"""
        success = await self.single_turn_selector.initialize()
        if success:
            self._initialized = True
            print(f"✅ 多轮工具选择器初始化成功")
        return success
    
    async def multi_turn_execution(self, complex_query: str) -> Dict[str, Any]:
        """
        多轮工具执行主函数
        
        Args:
            complex_query: 复杂查询
            
        Returns:
            包含完整执行过程和结果的字典
        """
        if not self._initialized:
            await self.initialize()
        
        print(f"🔄 开始多轮工具调用处理: {complex_query}")
        
        # 重置上下文
        self.conversation_context = []
        self.execution_results = []
        
        try:
            # 1. 任务规划阶段
            task_plan = await self._task_planning(complex_query)
            
            if not task_plan or not task_plan.get('sub_tasks'):
                # 如果无法分解任务，回退到单轮模式
                print("⚠️ 任务无法分解，回退到单轮模式")
                return await self._fallback_to_single_turn(complex_query)
            
            # 2. 多轮执行阶段（支持并行优化）
            execution_summary = await self._execute_multi_turn_plan(task_plan)
            
            # 3. 结果整合阶段
            final_result = await self._integrate_results(complex_query, execution_summary)
            
            return {
                'success': True,
                'type': 'multi_turn',
                'original_query': complex_query,
                'task_plan': task_plan,
                'execution_summary': execution_summary,
                'final_result': final_result,
                'turns_executed': len(self.execution_results),
                'context': self.conversation_context
            }
            
        except Exception as e:
            print(f"❌ 多轮执行失败: {e}")
            # 出错时回退到单轮模式
            return await self._fallback_to_single_turn(complex_query)
    
    async def _task_planning(self, complex_query: str) -> Dict[str, Any]:
        """
        任务规划阶段
        
        Args:
            complex_query: 复杂查询
            
        Returns:
            任务规划结果
        """
        print("📋 开始任务规划...")
        
        prompt = self._generate_task_planning_prompt(complex_query)
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config['model_name'],
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的任务规划专家，擅长将复杂查询分解为可执行的子任务序列。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # 解析任务规划结果
            task_plan = self.json_parser.extract_json_from_response(response_text)
            
            if task_plan and 'sub_tasks' in task_plan:
                print(f"✅ 任务规划完成，共分解为 {len(task_plan['sub_tasks'])} 个子任务")
                return task_plan
            else:
                print("❌ 任务规划解析失败")
                return {}
                
        except Exception as e:
            print(f"❌ 任务规划失败: {e}")
            return {}
    
    async def _execute_multi_turn_plan(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行多轮任务计划（支持并行优化）
        
        Args:
            task_plan: 任务规划结果
            
        Returns:
            执行摘要
        """
        print("🔧 开始执行多轮任务...")
        
        sub_tasks = task_plan.get('sub_tasks', [])
        execution_summary = {
            'total_tasks': len(sub_tasks),
            'completed_tasks': 0,
            'failed_tasks': 0,
            'task_results': [],
            'execution_mode': 'unknown'
        }
        
        # 限制任务数量
        sub_tasks = sub_tasks[:self.max_turns]
        
        # 检查是否可以并行执行
        if self.enable_parallel and self.parallel_executor and len(sub_tasks) > 1:
            try:
                # 分析并行执行可能性
                optimization_plan = self.parallel_executor.optimize_execution_plan(sub_tasks)
                self.parallel_executor.print_optimization_summary(optimization_plan)
                
                if optimization_plan['can_parallelize']:
                    # 并行执行
                    execution_summary['execution_mode'] = 'parallel'
                    task_results = await self.parallel_executor.execute_levels_parallel(
                        optimization_plan['execution_levels'],
                        self.single_turn_selector.select_and_execute_tool,
                        self._update_context
                    )
                else:
                    # 回退到串行执行
                    print("⚠️ 无法并行执行，回退到串行模式")
                    execution_summary['execution_mode'] = 'serial_fallback'
                    task_results = await self._execute_serial(sub_tasks)
                    
            except Exception as e:
                print(f"❌ 并行执行出错，回退到串行模式: {e}")
                execution_summary['execution_mode'] = 'serial_fallback'
                task_results = await self._execute_serial(sub_tasks)
        else:
            # 串行执行
            execution_summary['execution_mode'] = 'serial'
            task_results = await self._execute_serial(sub_tasks)
        
        # 统计结果
        for task_result in task_results:
            self.execution_results.append(task_result)
            execution_summary['task_results'].append(task_result)
            
            if task_result['result'].get('success'):
                execution_summary['completed_tasks'] += 1
            else:
                execution_summary['failed_tasks'] += 1
        
        print(f"\n📊 多轮执行完成 ({execution_summary['execution_mode']}): {execution_summary['completed_tasks']}/{execution_summary['total_tasks']} 成功")
        return execution_summary
    
    async def _execute_serial(self, sub_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        串行执行任务列表
        
        Args:
            sub_tasks: 子任务列表
            
        Returns:
            执行结果列表
        """
        task_results = []
        
        for i, task in enumerate(sub_tasks, 1):
            print(f"\n🎯 执行第 {i} 轮任务: {task.get('description', task.get('query', ''))}")
            
            try:
                # 使用单轮选择器执行子任务
                task_query = task.get('query', task.get('description', ''))
                result = await self.single_turn_selector.select_and_execute_tool(task_query)
                
                # 记录结果
                task_result = {
                    'turn': i,
                    'task': task,
                    'result': result,
                    'timestamp': datetime.now().isoformat(),
                    'execution_mode': 'serial'
                }
                
                task_results.append(task_result)
                
                if result.get('success'):
                    print(f"✅ 第 {i} 轮任务执行成功")
                    
                    # 更新上下文
                    self._update_context(task_query, result)
                else:
                    print(f"❌ 第 {i} 轮任务执行失败: {result.get('error')}")
                
                # 短暂延迟，避免请求过快
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ 第 {i} 轮任务执行异常: {e}")
                
                error_result = {
                    'turn': i,
                    'task': task,
                    'result': {'success': False, 'error': str(e)},
                    'timestamp': datetime.now().isoformat(),
                    'execution_mode': 'serial'
                }
                task_results.append(error_result)
        
        return task_results
    
    async def _integrate_results(self, original_query: str, execution_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        结果整合阶段
        
        Args:
            original_query: 原始查询
            execution_summary: 执行摘要
            
        Returns:
            整合后的最终结果
        """
        print("📊 开始结果整合...")
        
        # 收集所有成功的执行结果
        successful_results = []
        for task_result in execution_summary['task_results']:
            if task_result['result'].get('success'):
                successful_results.append(task_result)
        
        if not successful_results:
            return {
                'success': False,
                'message': '所有子任务都执行失败，无法生成综合结果',
                'details': execution_summary
            }
        
        # 生成结果整合prompt
        integration_prompt = self._generate_integration_prompt(original_query, successful_results)
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config['model_name'],
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的数据分析师，擅长整合多个数据源的信息，生成综合性的分析报告。"
                    },
                    {"role": "user", "content": integration_prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            integrated_result = response.choices[0].message.content.strip()
            
            print("✅ 结果整合完成")
            return {
                'success': True,
                'integrated_analysis': integrated_result,
                'source_results': successful_results,
                'summary': execution_summary
            }
            
        except Exception as e:
            print(f"❌ 结果整合失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_results': successful_results,
                'summary': execution_summary
            }
    
    async def _fallback_to_single_turn(self, query: str) -> Dict[str, Any]:
        """
        回退到单轮模式
        
        Args:
            query: 查询
            
        Returns:
            单轮执行结果
        """
        print("🔄 回退到单轮模式...")
        result = await self.single_turn_selector.select_and_execute_tool(query)
        result['type'] = 'single_turn_fallback'
        return result
    
    def _update_context(self, query: str, result: Dict[str, Any]):
        """更新对话上下文"""
        context_item = {
            'query': query,
            'tool_used': result.get('execution_result', {}).get('tool_name'),
            'success': result.get('success'),
            'timestamp': datetime.now().isoformat()
        }
        self.conversation_context.append(context_item)
        
        # 限制上下文长度
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]
    
    def _generate_task_planning_prompt(self, complex_query: str) -> str:
        """生成任务规划提示词"""
        
        # 获取可用工具信息
        tools_summary = self._get_tools_summary()
        
        prompt = f"""你是一个专业的任务规划专家。用户提出了一个复杂的查询，你需要分析是否需要分解为多个子任务，以及如何分解。

## 用户查询
{complex_query}

## 可用工具类型
{tools_summary}

## 任务分解原则
1. **复杂度判断**: 判断查询是否需要多个步骤才能完成
2. **依赖关系**: 考虑子任务之间的依赖关系和执行顺序
3. **工具匹配**: 确保每个子任务都有对应的工具可以执行
4. **结果关联**: 考虑如何整合多个子任务的结果

## 需要分解的查询类型示例
- "分析XX股票的投资价值" (需要基本信息+财务数据+技术分析)
- "比较XX和YY两只股票" (需要分别查询两只股票的信息)
- "查询XX板块的龙头股并分析" (需要板块查询+个股分析)

## 输出格式
如果需要分解，请以JSON格式输出：

```json
{{
  "is_complex": true,
  "complexity_reason": "查询原因说明",
  "sub_tasks": [
    {{
      "step": 1,
      "description": "子任务描述",
      "query": "具体的查询语句",
      "expected_tool_type": "期望的工具类型",
      "dependency": "依赖的前置任务(如无则为null)"
    }}
  ],
  "integration_strategy": "如何整合各子任务结果的策略"
}}
```

如果不需要分解，请输出：
```json
{{
  "is_complex": false,
  "reason": "不需要分解的原因"
}}
```

请开始分析："""
        
        return prompt
    
    def _generate_integration_prompt(self, original_query: str, successful_results: List[Dict]) -> str:
        """生成结果整合提示词"""
        
        # 构建结果摘要
        results_summary = []
        for i, task_result in enumerate(successful_results, 1):
            task = task_result['task']
            result = task_result['result']
            
            execution_result = result.get('execution_result', {})
            tool_name = execution_result.get('tool_name', '未知工具')
            response_preview = str(execution_result.get('response', ''))[:200] + "..."
            
            results_summary.append(f"""
### 子任务 {i}: {task.get('description', task.get('query', ''))}
- 使用工具: {tool_name}
- 执行参数: {execution_result.get('parameters', {})}
- 结果预览: {response_preview}
""")
        
        results_text = "\n".join(results_summary)
        
        prompt = f"""你是一个专业的数据分析师，需要整合多个数据查询的结果，为用户的原始问题提供综合性的分析答案。

## 用户原始查询
{original_query}

## 子任务执行结果
{results_text}

## 整合要求
1. **完整性**: 确保回答涵盖用户查询的所有方面
2. **逻辑性**: 将各个子任务的结果有机整合，形成逻辑清晰的分析
3. **专业性**: 使用专业的金融分析语言和结构
4. **实用性**: 提供有价值的洞察和建议

## 输出格式
请生成一个结构化的综合分析报告，包含：

1. **执行摘要**: 简要概述分析结果
2. **详细分析**: 基于各子任务结果的深入分析
3. **关键发现**: 重要的发现和洞察
4. **建议结论**: 基于分析的建议或结论

请开始整合分析："""
        
        return prompt
    
    def _get_tools_summary(self) -> str:
        """获取工具摘要信息"""
        if not self.single_turn_selector.is_initialized():
            return "工具信息加载中..."
        
        # 简化的工具分类摘要
        tool_categories = {
            "股票基本信息": ["stock_basic_info", "search_stocks"],
            "财务数据": ["financial_indicators", "financial_data"],
            "港股数据": ["hk_daily", "hk_basic"],
            "市场数据": ["top_list", "market_data"],
            "技术分析": ["daily_basic", "technical"],
            "概念板块": ["concept", "industry"],
            "其他工具": ["其他专业工具"]
        }
        
        summary_lines = []
        for category, tools in tool_categories.items():
            summary_lines.append(f"- {category}: {', '.join(tools)}")
        
        return "\n".join(summary_lines)
    
    def get_conversation_context(self) -> List[Dict[str, Any]]:
        """获取对话上下文"""
        return self.conversation_context.copy()
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_results.copy()
    
    def reset_context(self):
        """重置上下文"""
        self.conversation_context = []
        self.execution_results = []
        print("🔄 上下文已重置")
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized 