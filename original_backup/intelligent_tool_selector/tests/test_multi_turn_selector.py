"""
多轮工具选择器测试模块
Multi-turn Tool Selector Test Module

测试多轮工具调用、任务规划和结果整合功能
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# 添加路径以导入测试模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from intelligent_tool_selector import MultiTurnToolSelector
    from intelligent_tool_selector.core.multi_turn_selector import MultiTurnToolSelector as DirectMultiTurnToolSelector
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)


class TestMultiTurnToolSelector(unittest.TestCase):
    """多轮工具选择器测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.selector = MultiTurnToolSelector(
            mcp_server_url="http://43.134.62.139:7223/sse",
            model_url="http://161.248.3.20:32790/v1",
            model_name="xDAN-Agent-Medium-v2-step300-0525"
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.selector)
        self.assertFalse(self.selector.is_initialized())
        self.assertEqual(self.selector.max_turns, 5)
        self.assertEqual(len(self.selector.conversation_context), 0)
        self.assertEqual(len(self.selector.execution_results), 0)
    
    @patch('intelligent_tool_selector.core.multi_turn_selector.openai.OpenAI')
    async def test_task_planning_complex_query(self, mock_openai):
        """测试复杂查询的任务规划"""
        # Mock LLM响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "is_complex": true,
            "complexity_reason": "需要多个步骤分析股票投资价值",
            "sub_tasks": [
                {
                    "step": 1,
                    "description": "获取股票基本信息",
                    "query": "搜索平安银行的基本信息",
                    "expected_tool_type": "股票基本信息",
                    "dependency": null
                },
                {
                    "step": 2,
                    "description": "查询财务数据",
                    "query": "查询平安银行的财务指标",
                    "expected_tool_type": "财务数据",
                    "dependency": "step1"
                }
            ],
            "integration_strategy": "综合基本面和财务数据分析"
        }
        '''
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 初始化选择器（模拟）
        self.selector._initialized = True
        self.selector.single_turn_selector._initialized = True
        
        # 测试任务规划
        result = await self.selector._task_planning("分析平安银行的投资价值")
        
        self.assertTrue(result.get('is_complex'))
        self.assertEqual(len(result.get('sub_tasks', [])), 2)
        self.assertEqual(result['sub_tasks'][0]['step'], 1)
        self.assertEqual(result['sub_tasks'][1]['step'], 2)
    
    @patch('intelligent_tool_selector.core.multi_turn_selector.openai.OpenAI')
    async def test_task_planning_simple_query(self, mock_openai):
        """测试简单查询的任务规划"""
        # Mock LLM响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "is_complex": false,
            "reason": "简单的股票信息查询，单个工具即可完成"
        }
        '''
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 初始化选择器（模拟）
        self.selector._initialized = True
        self.selector.single_turn_selector._initialized = True
        
        # 测试任务规划
        result = await self.selector._task_planning("搜索平安银行的股票代码")
        
        self.assertFalse(result.get('is_complex'))
        self.assertIn('reason', result)
    
    def test_context_management(self):
        """测试上下文管理"""
        # 测试初始状态
        self.assertEqual(len(self.selector.get_conversation_context()), 0)
        self.assertEqual(len(self.selector.get_execution_history()), 0)
        
        # 模拟添加上下文
        self.selector._update_context(
            "测试查询",
            {"success": True, "execution_result": {"tool_name": "test_tool"}}
        )
        
        context = self.selector.get_conversation_context()
        self.assertEqual(len(context), 1)
        self.assertEqual(context[0]['query'], "测试查询")
        self.assertEqual(context[0]['tool_used'], "test_tool")
        self.assertTrue(context[0]['success'])
        
        # 测试重置上下文
        self.selector.reset_context()
        self.assertEqual(len(self.selector.get_conversation_context()), 0)
        self.assertEqual(len(self.selector.get_execution_history()), 0)
    
    def test_context_limit(self):
        """测试上下文长度限制"""
        # 添加超过限制的上下文
        for i in range(15):
            self.selector._update_context(
                f"查询 {i}",
                {"success": True, "execution_result": {"tool_name": f"tool_{i}"}}
            )
        
        context = self.selector.get_conversation_context()
        # 应该限制在10条以内
        self.assertLessEqual(len(context), 10)
        # 应该保留最新的记录
        self.assertEqual(context[-1]['query'], "查询 14")
    
    def test_tools_summary_generation(self):
        """测试工具摘要生成"""
        # 模拟单轮选择器已初始化
        self.selector.single_turn_selector._initialized = True
        
        summary = self.selector._get_tools_summary()
        self.assertIsInstance(summary, str)
        self.assertIn("股票基本信息", summary)
        self.assertIn("财务数据", summary)
        self.assertIn("港股数据", summary)
    
    def test_prompt_generation(self):
        """测试提示词生成"""
        # 模拟单轮选择器已初始化
        self.selector.single_turn_selector._initialized = True
        
        # 测试任务规划提示词
        planning_prompt = self.selector._generate_task_planning_prompt("分析腾讯股票")
        self.assertIn("分析腾讯股票", planning_prompt)
        self.assertIn("任务分解原则", planning_prompt)
        self.assertIn("输出格式", planning_prompt)
        
        # 测试结果整合提示词
        mock_results = [{
            'task': {'description': '测试任务', 'query': '测试查询'},
            'result': {
                'success': True,
                'execution_result': {
                    'tool_name': 'test_tool',
                    'parameters': {'param': 'value'},
                    'response': '测试响应数据'
                }
            }
        }]
        
        integration_prompt = self.selector._generate_integration_prompt(
            "原始查询", mock_results
        )
        self.assertIn("原始查询", integration_prompt)
        self.assertIn("测试任务", integration_prompt)
        self.assertIn("整合要求", integration_prompt)


class TestMultiTurnIntegration(unittest.TestCase):
    """多轮工具调用集成测试"""
    
    def setUp(self):
        """测试初始化"""
        self.selector = MultiTurnToolSelector()
    
    async def test_fallback_mechanism(self):
        """测试回退机制"""
        # 模拟初始化失败的情况
        with patch.object(self.selector.single_turn_selector, 'select_and_execute_tool') as mock_execute:
            mock_execute.return_value = {
                'success': True,
                'type': 'single_turn',
                'execution_result': {'tool_name': 'fallback_tool'}
            }
            
            result = await self.selector._fallback_to_single_turn("测试查询")
            
            self.assertTrue(result.get('success'))
            self.assertEqual(result.get('type'), 'single_turn_fallback')
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试JSON解析错误处理
        self.selector._initialized = True
        self.selector.single_turn_selector._initialized = True
        
        # 测试工具摘要在未初始化时的处理
        self.selector.single_turn_selector._initialized = False
        summary = self.selector._get_tools_summary()
        self.assertEqual(summary, "工具信息加载中...")


async def run_integration_test():
    """运行集成测试"""
    print("🧪 开始多轮工具选择器集成测试")
    
    try:
        # 创建真实的选择器实例进行测试
        selector = MultiTurnToolSelector()
        
        # 测试初始化
        print("1. 测试初始化...")
        success = await selector.initialize()
        if success:
            print("   ✅ 初始化成功")
        else:
            print("   ❌ 初始化失败")
            return
        
        # 测试简单查询（应该回退到单轮）
        print("\n2. 测试简单查询...")
        simple_result = await selector.multi_turn_execution("搜索平安银行")
        print(f"   结果类型: {simple_result.get('type')}")
        print(f"   执行成功: {simple_result.get('success')}")
        
        # 测试复杂查询（应该尝试多轮）
        print("\n3. 测试复杂查询...")
        complex_result = await selector.multi_turn_execution(
            "分析比亚迪的投资价值，包括基本面和财务指标分析"
        )
        print(f"   结果类型: {complex_result.get('type')}")
        print(f"   执行成功: {complex_result.get('success')}")
        if complex_result.get('type') == 'multi_turn':
            print(f"   执行轮次: {complex_result.get('turns_executed')}")
            execution_summary = complex_result.get('execution_summary', {})
            print(f"   成功任务: {execution_summary.get('completed_tasks', 0)}")
        
        # 测试上下文功能
        print("\n4. 测试上下文功能...")
        context = selector.get_conversation_context()
        history = selector.get_execution_history()
        print(f"   上下文条数: {len(context)}")
        print(f"   历史记录数: {len(history)}")
        
        print("\n✅ 集成测试完成")
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")


def main():
    """主测试函数"""
    print("🔧 多轮工具选择器测试套件")
    print("=" * 50)
    
    # 运行单元测试
    print("\n📋 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行集成测试
    print("\n📊 运行集成测试...")
    asyncio.run(run_integration_test())


if __name__ == "__main__":
    main() 