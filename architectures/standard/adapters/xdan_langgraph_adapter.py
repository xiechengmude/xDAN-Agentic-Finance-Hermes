"""
xDAN到LangGraph的适配器
XDANLangGraphAdapter for converting xDAN backend to LangGraph-compatible API
"""

import asyncio
import json
import uuid
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime

# 加载环境变量
from pathlib import Path
import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "tests"))
from load_env import load_dotenv
load_dotenv()

from intelligent_tool_selector import MultiTurnToolSelector
from .event_mapper import EventMapper


class XDANLangGraphAdapter:
    """xDAN到LangGraph的核心适配器"""
    
    def __init__(self, xdan_selector: Optional[MultiTurnToolSelector] = None):
        """
        初始化适配器
        
        Args:
            xdan_selector: xDAN多轮工具选择器实例
        """
        self.xdan_selector = xdan_selector or MultiTurnToolSelector()
        self.event_mapper = EventMapper()
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """初始化适配器"""
        if not self.is_initialized:
            success = await self.xdan_selector.initialize()
            if success:
                self.is_initialized = True
                print("✅ XDANLangGraphAdapter 初始化成功")
            else:
                # 尝试在无MCP工具的情况下运行
                print("⚠️ MCP工具加载失败，尝试启用降级模式...")
                self.is_initialized = True  # 允许在没有MCP的情况下运行
                self.xdan_selector._initialized = True  # 设置选择器为已初始化
                print("✅ XDANLangGraphAdapter 已在降级模式下初始化（无MCP工具）")
                return True  # 返回成功，允许服务启动
            return success
        return True
    
    async def stream_execution(self, 
                             messages: List[Dict[str, Any]], 
                             config: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式执行接口，兼容LangGraph SDK
        
        Args:
            messages: 消息列表
            config: 配置参数
            
        Yields:
            LangGraph格式的事件
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 1. 参数转换
            query = self._extract_user_query(messages)
            if not query:
                yield self.event_mapper.create_error_event("No valid query found", "generate_query")
                return
            
            print(f"🔄 开始流式执行查询: {query}")
            
            # 2. 执行xDAN并转换事件流
            async for event in self._execute_with_events(query, config):
                yield event
                
        except Exception as e:
            print(f"❌ 流式执行出错: {e}")
            yield self.event_mapper.create_error_event(str(e), "finalize_answer")
    
    async def _execute_with_events(self, 
                                 query: str, 
                                 config: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        执行xDAN并生成LangGraph兼容事件流
        
        Args:
            query: 用户查询
            config: 配置参数
            
        Yields:
            转换后的事件
        """
        try:
            # 重置选择器上下文
            self.xdan_selector.reset_context()
            
            # 开始执行并监听过程
            print("📡 开始xDAN多轮执行...")
            
            # 发送初始的generate_query事件
            yield {
                "generate_query": {
                    "query_list": [f"Analyzing: {query}"]
                }
            }
            
            # 添加小延迟，让前端有时间处理第一个事件
            await asyncio.sleep(0.2)
            
            # 执行xDAN多轮工具调用
            try:
                result = await self.xdan_selector.multi_turn_execution(query)
            except Exception as e:
                # 降级模式：返回简单的文本响应
                print(f"⚠️ 多轮执行失败，使用降级响应: {e}")
                result = {
                    'type': 'degraded',
                    'success': True,
                    'final_result': {
                        'answer': f"抱歉，由于MCP工具服务暂时不可用，我无法执行具体的数据查询。您的问题是: {query}\n\n请稍后再试，或联系系统管理员。",
                        'sources': []
                    }
                }
            
            # 根据执行类型转换事件
            if result.get('type') == 'degraded':
                print("⚠️ 处理降级模式结果...")
                # 发送降级模式的最终答案
                yield {
                    "finalize_answer": {
                        "answer": result['final_result']['answer'],
                        "sources": []
                    }
                }
            elif result.get('type') == 'multi_turn':
                print("🔄 处理多轮执行结果...")
                async for event in self._process_multi_turn_result(result):
                    yield event
                    await asyncio.sleep(0.1)  # 控制事件发送频率
            else:
                print("🎯 处理单轮执行结果...")
                async for event in self._process_single_turn_result(result):
                    yield event
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            print(f"❌ 执行过程出错: {e}")
            yield self.event_mapper.create_error_event(str(e), "finalize_answer")
    
    async def _process_multi_turn_result(self, result: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        处理多轮执行结果并生成事件流
        
        Args:
            result: xDAN多轮执行结果
            
        Yields:
            转换后的事件
        """
        # 1. 任务规划事件（如果有的话，可能在前面已经发送过了，这里检查一下）
        task_plan = result.get('task_plan', {})
        if task_plan and task_plan.get('sub_tasks'):
            sub_tasks = task_plan['sub_tasks']
            if len(sub_tasks) > 1:  # 只有多个子任务时才重新发送
                yield self.event_mapper.convert_task_planning_event(task_plan)
        
        # 2. 执行过程事件
        execution_summary = result.get('execution_summary', {})
        task_results = execution_summary.get('task_results', [])
        
        # 按任务分组发送web_research事件
        for i, task_result in enumerate(task_results):
            task_exec_result = task_result.get('result', {}).get('execution_result', {})
            if task_exec_result:
                print(f"🔧 处理第 {i+1} 个任务结果...")
                yield self.event_mapper.convert_execution_event(
                    task_exec_result, 
                    task_result.get('task', {})
                )
        
        # 3. 反思事件
        final_result = result.get('final_result', {})
        print("🤔 生成反思事件...")
        yield self.event_mapper.convert_integration_event(final_result, execution_summary)
        
        # 4. 最终答案事件
        print("📝 生成最终答案事件...")
        yield self.event_mapper.convert_final_event(final_result)
    
    async def _process_single_turn_result(self, result: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        处理单轮执行结果并生成事件流
        
        Args:
            result: xDAN单轮执行结果
            
        Yields:
            转换后的事件
        """
        # 1. web_research事件
        execution_result = result.get('execution_result', {})
        if execution_result:
            print("🔧 处理单轮执行结果...")
            yield self.event_mapper.convert_execution_event(execution_result)
        
        # 2. reflection事件
        print("🤔 生成反思事件...")
        yield {
            "reflection": {
                "is_sufficient": result.get('success', False),
                "follow_up_queries": [] if result.get('success') else ["Single query execution incomplete"]
            }
        }
        
        # 3. finalize_answer事件
        print("📝 生成最终答案事件...")
        yield self.event_mapper.convert_final_event(result)
    
    def _extract_user_query(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """
        从消息列表中提取用户查询
        
        Args:
            messages: LangGraph格式的消息列表
            
        Returns:
            用户查询字符串
        """
        if not messages:
            return None
        
        # 查找最后一条用户消息
        for message in reversed(messages):
            if message.get('type') == 'human' or message.get('role') == 'user':
                content = message.get('content', '')
                if content and content.strip():
                    return content.strip()
        
        # 如果没有找到用户消息，尝试提取第一条消息的内容
        if messages:
            first_message = messages[0]
            content = first_message.get('content', '')
            if content and content.strip():
                return content.strip()
        
        return None
    
    def _convert_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换LangGraph配置为xDAN配置
        
        Args:
            config: LangGraph配置参数
            
        Returns:
            xDAN配置参数
        """
        # 提取相关配置参数
        xdan_config = {}
        
        # 映射参数
        if 'initial_search_query_count' in config:
            xdan_config['initial_query_count'] = config['initial_search_query_count']
        
        if 'max_research_loops' in config:
            xdan_config['max_turns'] = config['max_research_loops']
        
        if 'reasoning_model' in config:
            xdan_config['model_name'] = config['reasoning_model']
        
        return xdan_config
    
    async def create_thread(self) -> str:
        """创建新的线程ID"""
        return str(uuid.uuid4())
    
    async def get_thread_status(self, thread_id: str) -> Dict[str, Any]:
        """获取线程状态"""
        return {
            "thread_id": thread_id,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
    
    def get_available_tools_count(self) -> int:
        """获取可用工具数量"""
        if self.is_initialized:
            try:
                return self.xdan_selector.single_turn_selector.get_tools_count()
            except:
                return 0  # 降级模式下返回0
        return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            tools_count = self.get_available_tools_count()
            
            return {
                "status": "healthy",
                "initialized": self.is_initialized,
                "tools_available": tools_count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }