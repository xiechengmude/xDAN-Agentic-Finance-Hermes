#!/usr/bin/env python3
"""
多轮智能体测试脚本
用于验证智能体能否正确拆解复杂问题并调用相应的工具
"""

import asyncio
import csv
import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "architectures" / "standard"))

# 加载环境变量
from load_env import load_dotenv
load_dotenv()

from intelligent_tool_selector import MultiTurnToolSelector

try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    # 创建空的装饰器
    def observe(name=None):
        def decorator(func):
            return func
        return decorator
    
    class MockLangfuseContext:
        def update_current_trace(self, **kwargs):
            pass
        def get_current_trace_id(self):
            return None
    
    langfuse_context = MockLangfuseContext()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """测试用例数据类"""
    id: str
    category: str
    question: str
    expected_tools: List[str]
    expected_turns: str
    difficulty: str
    scenario: str

@dataclass
class TestResult:
    """测试结果数据类"""
    test_id: str
    question: str
    success: bool
    actual_tools: List[str]
    expected_tools: List[str]
    actual_turns: int
    expected_turns_range: tuple
    execution_time: float
    error: Optional[str] = None
    response: Optional[str] = None
    tool_coverage: float = 0.0
    trace_id: Optional[str] = None

class MultiTurnAgentTester:
    """多轮智能体测试器"""
    
    def __init__(self, csv_file_path: str, enable_langfuse: bool = True):
        self.csv_file_path = csv_file_path
        self.test_results: List[TestResult] = []
        self.selector = MultiTurnToolSelector()
        
        # Langfuse配置
        self.enable_langfuse = enable_langfuse
        if enable_langfuse:
            self.init_langfuse()
    
    def init_langfuse(self):
        """初始化Langfuse客户端"""
        if not LANGFUSE_AVAILABLE:
            logger.info("ℹ️ Langfuse未安装，观测功能已禁用")
            self.enable_langfuse = False
            return
            
        try:
            # 从环境变量读取配置
            self.langfuse = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            )
            logger.info("✅ Langfuse初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ Langfuse初始化失败: {e}")
            self.enable_langfuse = False
    
    def load_test_cases(self, max_cases: Optional[int] = None) -> List[TestCase]:
        """加载测试用例"""
        test_cases = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if max_cases and i >= max_cases:
                        break
                    
                    # 解析预期工具列表
                    expected_tools = [tool.strip() for tool in row['涉及工具'].split(',')]
                    
                    test_case = TestCase(
                        id=row['问题编号'],
                        category=row['问题类别'],
                        question=row['具体问题'],
                        expected_tools=expected_tools,
                        expected_turns=row['预期轮数'],
                        difficulty=row['难度等级'],
                        scenario=row['应用场景']
                    )
                    test_cases.append(test_case)
            
            logger.info(f"✅ 成功加载 {len(test_cases)} 个测试用例")
            return test_cases
            
        except Exception as e:
            logger.error(f"❌ 加载测试用例失败: {e}")
            return []
    
    @observe(name="test_single_case")
    async def test_single_case(self, test_case: TestCase) -> TestResult:
        """测试单个用例"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 测试用例 {test_case.id}: {test_case.question}")
        logger.info(f"📋 类别: {test_case.category} | 难度: {test_case.difficulty}")
        logger.info(f"🔧 预期工具: {', '.join(test_case.expected_tools[:3])}...")
        
        start_time = time.time()
        trace_id = None
        
        try:
            # 在Langfuse中记录测试信息
            if self.enable_langfuse:
                langfuse_context.update_current_trace(
                    name=f"test_case_{test_case.id}",
                    metadata={
                        "category": test_case.category,
                        "difficulty": test_case.difficulty,
                        "expected_tools": test_case.expected_tools
                    }
                )
                trace_id = langfuse_context.get_current_trace_id()
            
            # 初始化选择器
            if not self.selector._initialized:
                await self.selector.initialize()
            
            # 重置上下文
            self.selector.reset_context()
            
            # 执行多轮查询
            result = await self.selector.multi_turn_execution(test_case.question)
            
            # 提取实际使用的工具
            actual_tools = self._extract_used_tools(result)
            
            # 计算实际轮数
            actual_turns = self._calculate_turns(result)
            
            # 解析预期轮数范围
            expected_turns_range = self._parse_expected_turns(test_case.expected_turns)
            
            # 计算工具覆盖率
            tool_coverage = self._calculate_tool_coverage(actual_tools, test_case.expected_tools)
            
            # 提取最终答案
            final_answer = result.get('final_result', {}).get('answer', '无答案')
            
            # 判断测试是否成功
            success = (
                result.get('success', False) and
                tool_coverage >= 0.5 and  # 至少覆盖50%的预期工具
                expected_turns_range[0] <= actual_turns <= expected_turns_range[1]
            )
            
            execution_time = time.time() - start_time
            
            logger.info(f"✅ 测试完成 | 用时: {execution_time:.2f}s | 轮数: {actual_turns}")
            logger.info(f"📊 工具覆盖率: {tool_coverage:.1%}")
            
            return TestResult(
                test_id=test_case.id,
                question=test_case.question,
                success=success,
                actual_tools=actual_tools,
                expected_tools=test_case.expected_tools,
                actual_turns=actual_turns,
                expected_turns_range=expected_turns_range,
                execution_time=execution_time,
                response=final_answer[:200] + "..." if len(final_answer) > 200 else final_answer,
                tool_coverage=tool_coverage,
                trace_id=trace_id
            )
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            execution_time = time.time() - start_time
            
            return TestResult(
                test_id=test_case.id,
                question=test_case.question,
                success=False,
                actual_tools=[],
                expected_tools=test_case.expected_tools,
                actual_turns=0,
                expected_turns_range=self._parse_expected_turns(test_case.expected_turns),
                execution_time=execution_time,
                error=str(e),
                trace_id=trace_id
            )
    
    def _extract_used_tools(self, result: Dict[str, Any]) -> List[str]:
        """从执行结果中提取使用的工具"""
        tools = set()
        
        # 从执行摘要中提取
        execution_summary = result.get('execution_summary', {})
        task_results = execution_summary.get('task_results', [])
        
        for task_result in task_results:
            exec_result = task_result.get('result', {}).get('execution_result', {})
            if exec_result:
                tool_name = exec_result.get('tool_name')
                if tool_name:
                    tools.add(tool_name)
        
        # 从单轮执行结果中提取
        if result.get('type') == 'single_turn':
            exec_result = result.get('execution_result', {})
            tool_name = exec_result.get('tool_name')
            if tool_name:
                tools.add(tool_name)
        
        return list(tools)
    
    def _calculate_turns(self, result: Dict[str, Any]) -> int:
        """计算实际执行轮数"""
        if result.get('type') == 'multi_turn':
            execution_summary = result.get('execution_summary', {})
            return len(execution_summary.get('task_results', []))
        else:
            return 1 if result.get('success') else 0
    
    def _parse_expected_turns(self, expected_turns: str) -> tuple:
        """解析预期轮数范围（如 '3-4' -> (3, 4)）"""
        if '-' in expected_turns:
            parts = expected_turns.split('-')
            return (int(parts[0]), int(parts[1]))
        else:
            turns = int(expected_turns)
            return (turns, turns)
    
    def _calculate_tool_coverage(self, actual_tools: List[str], expected_tools: List[str]) -> float:
        """计算工具覆盖率"""
        if not expected_tools:
            return 1.0
        
        # 更智能的工具匹配逻辑
        covered_count = 0
        
        for expected_tool in expected_tools:
            # 检查是否有实际工具匹配预期功能
            expected_keywords = self._extract_tool_keywords(expected_tool)
            
            for actual_tool in actual_tools:
                actual_keywords = self._extract_tool_keywords(actual_tool)
                
                # 如果有共同的关键词，认为是匹配的
                if expected_keywords & actual_keywords:
                    covered_count += 1
                    break
        
        return covered_count / len(expected_tools)
    
    def _extract_tool_keywords(self, tool_name: str) -> set:
        """提取工具名称中的关键词"""
        # 转换为小写并分割
        parts = tool_name.lower().replace('_', ' ').replace('-', ' ').split()
        
        # 关键词映射
        keyword_map = {
            'fund': {'fund', '基金'},
            'stock': {'stock', 'stk', '股票'},
            'trade': {'trade', 'block', '交易'},
            'money': {'money', 'moneyflow', '资金'},
            'income': {'income', '收入'},
            'balance': {'balance', 'balancesheet', '资产'},
            'concept': {'concept', '概念'},
            'search': {'search', 'get', 'query'},
            'detail': {'detail', 'info', 'basic'},
            'performance': {'performance', 'bar', 'daily'}
        }
        
        keywords = set()
        for part in parts:
            for key, values in keyword_map.items():
                if part in values:
                    keywords.add(key)
        
        return keywords
    
    async def run_tests(self, max_cases: Optional[int] = None):
        """运行所有测试"""
        logger.info("🚀 开始运行多轮智能体测试...")
        
        # 加载测试用例
        test_cases = self.load_test_cases(max_cases)
        if not test_cases:
            logger.error("❌ 没有可用的测试用例")
            return
        
        # 初始化选择器
        logger.info("🔄 初始化智能体...")
        await self.selector.initialize()
        
        # 执行测试
        for i, test_case in enumerate(test_cases):
            logger.info(f"\n📍 进度: {i+1}/{len(test_cases)}")
            result = await self.test_single_case(test_case)
            self.test_results.append(result)
            
            # 避免请求过于频繁
            await asyncio.sleep(2)
        
        # 保存结果
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """保存测试结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = project_root / "test_results"
        output_dir.mkdir(exist_ok=True)
        
        # 保存详细结果
        output_file = output_dir / f"multi_turn_test_results_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            results_data = [asdict(result) for result in self.test_results]
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 测试结果已保存到: {output_file}")
    
    def print_summary(self):
        """打印测试摘要"""
        total = len(self.test_results)
        successful = sum(1 for r in self.test_results if r.success)
        
        logger.info(f"\n{'='*60}")
        logger.info("📊 测试摘要")
        logger.info(f"{'='*60}")
        logger.info(f"总测试数: {total}")
        logger.info(f"成功数: {successful}")
        logger.info(f"失败数: {total - successful}")
        logger.info(f"成功率: {successful/total:.1%}" if total > 0 else "N/A")
        
        # 平均指标
        if self.test_results:
            avg_time = sum(r.execution_time for r in self.test_results) / len(self.test_results)
            avg_coverage = sum(r.tool_coverage for r in self.test_results) / len(self.test_results)
            logger.info(f"平均执行时间: {avg_time:.2f}秒")
            logger.info(f"平均工具覆盖率: {avg_coverage:.1%}")


async def main():
    """主函数"""
    # 配置测试参数
    csv_file = project_root / "data" / "多轮金融智能体问题集.csv"
    
    # 检查文件是否存在
    if not csv_file.exists():
        logger.error(f"❌ 测试文件不存在: {csv_file}")
        return
    
    # 创建测试器
    tester = MultiTurnAgentTester(str(csv_file))
    
    # 运行测试（限制数量以避免长时间运行）
    await tester.run_tests(max_cases=1)


if __name__ == "__main__":
    asyncio.run(main())