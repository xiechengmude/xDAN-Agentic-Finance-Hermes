"""
事件转换映射器
Event Mapper for converting xDAN events to LangGraph format
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class EventMapper:
    """xDAN事件到LangGraph事件的映射器"""
    
    # 事件类型映射
    EVENT_MAPPING = {
        'task_planning': 'generate_query',
        'tool_execution': 'web_research', 
        'parallel_execution': 'web_research',
        'result_integration': 'reflection',
        'final_result': 'finalize_answer'
    }
    
    def __init__(self):
        self.event_counter = 0
    
    def convert_task_planning_event(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换任务规划事件为generate_query格式
        
        Args:
            task_plan: xDAN任务规划结果
            
        Returns:
            LangGraph格式的generate_query事件
        """
        if not task_plan or not task_plan.get('sub_tasks'):
            # 如果没有子任务，使用原始查询
            return {
                "generate_query": {
                    "query_list": ["Processing your query..."]
                }
            }
        
        sub_tasks = task_plan.get('sub_tasks', [])
        query_list = []
        
        for task in sub_tasks:
            description = task.get('description', task.get('query', 'Unknown task'))
            query_list.append(description)
        
        return {
            "generate_query": {
                "query_list": query_list
            }
        }
    
    def convert_execution_event(self, execution_result: Dict[str, Any], task_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        转换工具执行事件为web_research格式
        
        Args:
            execution_result: xDAN工具执行结果
            task_info: 任务信息
            
        Returns:
            LangGraph格式的web_research事件
        """
        tool_name = execution_result.get('tool_name', 'Unknown Tool')
        response = execution_result.get('response', {})
        success = execution_result.get('success', False)
        
        # 创建模拟的sources_gathered
        sources = []
        
        if success and response:
            # 尝试解析响应数据
            if isinstance(response, dict):
                # 如果响应是字典，提取关键信息
                for key, value in response.items():
                    if value and str(value).strip():
                        sources.append({
                            "label": f"{tool_name} - {key}",
                            "value": str(value)[:200] + ("..." if len(str(value)) > 200 else ""),
                            "short_url": f"#{tool_name}_{key}".replace(" ", "_")
                        })
            elif isinstance(response, list) and len(response) > 0:
                # 如果响应是列表
                for i, item in enumerate(response[:5]):  # 限制最多5个项目
                    sources.append({
                        "label": f"{tool_name} - Item {i+1}",
                        "value": str(item)[:200] + ("..." if len(str(item)) > 200 else ""),
                        "short_url": f"#{tool_name}_item_{i+1}".replace(" ", "_")
                    })
            else:
                # 其他情况，直接使用响应内容
                sources.append({
                    "label": tool_name,
                    "value": str(response)[:200] + ("..." if len(str(response)) > 200 else ""),
                    "short_url": f"#{tool_name}".replace(" ", "_")
                })
        else:
            # 执行失败的情况
            error_msg = execution_result.get('error', 'Execution failed')
            sources.append({
                "label": f"{tool_name} (Failed)",
                "value": f"Error: {error_msg}",
                "short_url": f"#{tool_name}_error".replace(" ", "_")
            })
        
        return {
            "web_research": {
                "sources_gathered": sources
            }
        }
    
    def convert_integration_event(self, integration_result: Dict[str, Any], execution_summary: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        转换结果整合事件为reflection格式
        
        Args:
            integration_result: xDAN结果整合结果
            execution_summary: 执行摘要
            
        Returns:
            LangGraph格式的reflection事件
        """
        is_successful = integration_result.get('success', False)
        
        # 确定是否有足够的信息
        is_sufficient = True
        follow_up_queries = []
        
        if execution_summary:
            completed_tasks = execution_summary.get('completed_tasks', 0)
            total_tasks = execution_summary.get('total_tasks', 1)
            failed_tasks = execution_summary.get('failed_tasks', 0)
            
            # 如果失败任务过多，认为信息不足
            if failed_tasks > total_tasks * 0.5:
                is_sufficient = False
                follow_up_queries = ["Need to retry failed data queries", "Require additional data sources"]
            elif completed_tasks == 0:
                is_sufficient = False
                follow_up_queries = ["No successful data retrieved", "Need alternative approach"]
        
        if not is_successful:
            is_sufficient = False
            error_msg = integration_result.get('error', 'Integration failed')
            follow_up_queries = [f"Integration issue: {error_msg}"]
        
        return {
            "reflection": {
                "is_sufficient": is_sufficient,
                "follow_up_queries": follow_up_queries
            }
        }
    
    def convert_final_event(self, final_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换最终结果事件为finalize_answer格式
        
        Args:
            final_result: xDAN最终结果
            
        Returns:
            LangGraph格式的finalize_answer事件
        """
        return {
            "finalize_answer": {
                "status": "completed",
                "success": final_result.get('success', False),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def convert_single_turn_events(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        转换单轮执行结果为事件序列
        
        Args:
            result: xDAN单轮执行结果
            
        Returns:
            LangGraph格式的事件序列
        """
        events = []
        
        # 1. 模拟generate_query事件
        selection_result = result.get('selection_result', {})
        if selection_result and 'tool_selection' in selection_result:
            primary_tool = selection_result['tool_selection'].get('primary_tool', {})
            tool_name = primary_tool.get('name', 'Selected Tool')
            events.append({
                "generate_query": {
                    "query_list": [f"Using {tool_name} for analysis"]
                }
            })
        else:
            events.append({
                "generate_query": {
                    "query_list": ["Processing single query..."]
                }
            })
        
        # 2. 添加web_research事件
        execution_result = result.get('execution_result', {})
        if execution_result:
            events.append(self.convert_execution_event(execution_result))
        
        # 3. 添加reflection事件
        events.append({
            "reflection": {
                "is_sufficient": result.get('success', False),
                "follow_up_queries": [] if result.get('success') else ["Single query execution incomplete"]
            }
        })
        
        # 4. 添加finalize_answer事件
        events.append(self.convert_final_event(result))
        
        return events
    
    def convert_multi_turn_events(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        转换多轮执行结果为事件序列
        
        Args:
            result: xDAN多轮执行结果
            
        Returns:
            LangGraph格式的事件序列
        """
        events = []
        
        # 1. 任务规划事件
        task_plan = result.get('task_plan', {})
        if task_plan:
            events.append(self.convert_task_planning_event(task_plan))
        
        # 2. 执行过程事件
        execution_summary = result.get('execution_summary', {})
        task_results = execution_summary.get('task_results', [])
        
        for task_result in task_results:
            task_exec_result = task_result.get('result', {}).get('execution_result', {})
            if task_exec_result:
                events.append(self.convert_execution_event(
                    task_exec_result, 
                    task_result.get('task', {})
                ))
        
        # 3. 反思事件
        final_result = result.get('final_result', {})
        events.append(self.convert_integration_event(final_result, execution_summary))
        
        # 4. 最终答案事件
        events.append(self.convert_final_event(final_result))
        
        return events
    
    def create_error_event(self, error_msg: str, event_type: str = "web_research") -> Dict[str, Any]:
        """
        创建错误事件
        
        Args:
            error_msg: 错误消息
            event_type: 事件类型
            
        Returns:
            错误事件
        """
        if event_type == "generate_query":
            return {
                "generate_query": {
                    "query_list": [f"Error: {error_msg}"]
                }
            }
        elif event_type == "web_research":
            return {
                "web_research": {
                    "sources_gathered": [{
                        "label": "Error",
                        "value": error_msg,
                        "short_url": "#error"
                    }]
                }
            }
        elif event_type == "reflection":
            return {
                "reflection": {
                    "is_sufficient": False,
                    "follow_up_queries": [f"Error occurred: {error_msg}"]
                }
            }
        else:
            return {
                "finalize_answer": {
                    "status": "error",
                    "error": error_msg
                }
            }