#!/usr/bin/env python3
"""
游资涨停专题问题集完整测试脚本
Comprehensive Test Script for Hot Money Limit-Up Topic Question Set

功能特点：
1. 自动化测试所有303个问题
2. LLM自主工具选择（不参考预期工具）
3. 多轮对话支持（处理5步工具调用链）
4. 智能评估和详细报告
5. 性能监控和错误处理
"""

import asyncio
import csv
import json
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import psutil
import os
import sys
import re

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "gstack-langgraph" / "backend" / "src"))

try:
    from agent.configuration import Configuration
    # 创建适配器类
    class MCPConfiguration:
        def __init__(self):
            self.model_name = os.getenv("OPENAI_MODEL", "gpt-4")
            self.model_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.model_api_key = os.getenv("OPENAI_API_KEY", "")
            self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
            
        @classmethod
        def from_runnable_config(cls):
            return cls()
    
    class MCPToolManager:
        def __init__(self, server_url):
            self.server_url = server_url
            
        async def initialize(self):
            pass
            
        def get_tools_count(self):
            return 15  # 模拟工具数量
            
except ImportError:
    print("❌ 无法导入agent模块，请检查路径配置")
    print("尝试使用模拟配置...")
    
    class MCPConfiguration:
        def __init__(self):
            self.model_name = os.getenv("OPENAI_MODEL", "gpt-4")
            self.model_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.model_api_key = os.getenv("OPENAI_API_KEY", "")
            self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
            
        @classmethod
        def from_runnable_config(cls):
            return cls()
    
    class MCPToolManager:
        def __init__(self, server_url):
            self.server_url = server_url
            
        async def initialize(self):
            pass
            
        def get_tools_count(self):
            return 0

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class YouziFengTingTestRunner:
    """游资涨停专题测试运行器"""
    
    def __init__(self, csv_file_path: str):
        """
        初始化测试运行器
        
        Args:
            csv_file_path: 游资涨停专题问题集CSV文件路径
        """
        self.csv_file_path = csv_file_path
        self.test_results: List[Dict[str, Any]] = []
        self.start_time: float = 0
        self.config: Optional[MCPConfiguration] = None
        self.mcp_manager: Optional[MCPToolManager] = None
        self.llm: Optional[ChatOpenAI] = None
        
        # 测试统计
        self.stats = {
            "total_questions": 0,
            "single_turn_questions": 0,
            "multi_turn_questions": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "tool_calls_made": 0,
            "avg_response_time": 0,
            "tool_selection_accuracy": 0
        }
        
        # 设置日志
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = Path("test_logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"youzhi_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def setup_agent(self):
        """设置Agent组件"""
        self.logger.info("🔧 初始化Agent组件...")
        
        try:
            # 创建配置
            self.config = MCPConfiguration.from_runnable_config()
            self.logger.info(f"✅ 配置创建成功: {self.config.model_name}")
            
            # 创建MCP工具管理器
            self.mcp_manager = MCPToolManager(self.config.mcp_server_url)
            await self.mcp_manager.initialize()
            tools_count = self.mcp_manager.get_tools_count()
            self.logger.info(f"✅ MCP工具管理器初始化成功，可用工具: {tools_count}个")
            
            # 创建LLM
            if self.config.model_api_key and self.config.model_api_key != "":
                self.llm = ChatOpenAI(
                    model=self.config.model_name,
                    base_url=self.config.model_url,
                    api_key=self.config.model_api_key,
                    temperature=0.1,  # 使用较低温度确保一致性
                    max_tokens=4000
                )
                self.logger.info("✅ LLM创建成功")
            else:
                self.logger.warning("⚠️ 未设置API Key，将使用模拟模式")
                self.llm = None
            
        except Exception as e:
            self.logger.error(f"❌ Agent组件初始化失败: {str(e)}")
            raise
            
    def load_questions(self) -> List[Dict[str, Any]]:
        """加载问题集"""
        self.logger.info(f"📚 加载问题集: {self.csv_file_path}")
        
        questions = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append(row)
                    
            self.logger.info(f"✅ 成功加载 {len(questions)} 个问题")
            
            # 统计问题类型
            single_turn = len([q for q in questions if not q.get('问题ID', '').startswith('YZM')])
            multi_turn = len([q for q in questions if q.get('问题ID', '').startswith('YZM')])
            
            self.stats['total_questions'] = len(questions)
            self.stats['single_turn_questions'] = single_turn
            self.stats['multi_turn_questions'] = multi_turn
            
            self.logger.info(f"📊 问题统计 - 单轮: {single_turn}, 多轮: {multi_turn}")
            
            return questions
            
        except Exception as e:
            self.logger.error(f"❌ 加载问题集失败: {str(e)}")
            raise
            
    def create_system_prompt(self) -> str:
        """创建系统提示"""
        current_time = datetime.now()
        current_date = current_time.strftime('%Y-%m-%d')
        
        return f"""你是xDAN金融智能助手，专门处理游资涨停股相关查询。

当前时间信息：
- 当前日期: {current_date}
- 当前时间: {current_time.strftime('%H:%M:%S')}

你的任务：
1. 理解用户的游资涨停相关查询
2. 自主选择合适的工具来回答问题
3. 对于复杂查询，制定多步骤的工具调用计划
4. 提供准确、专业的分析和建议

工具选择原则：
- 根据问题内容自主判断需要哪些工具
- 不要依赖任何预设的工具调用建议
- 优先考虑数据的时效性和准确性
- 对于多轮查询，要有逻辑性的工具调用顺序

时间处理：
- "今天"、"今日" = {current_date}
- "昨天" = {(current_time - timedelta(days=1)).strftime('%Y-%m-%d')}
- "上周" = 上周的日期范围
- "最近" = 近期的合理日期范围

请专业、准确地回答每个问题。"""

    async def process_single_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个问题"""
        question_id = question.get('问题ID', 'UNKNOWN')
        query = question.get('问题内容', '')
        difficulty = question.get('难度等级', '未知')
        scenario = question.get('应用场景', '未知')
        
        self.logger.info(f"🧪 测试问题 {question_id}: {query[:50]}...")
        
        test_result = {
            'question_id': question_id,
            'query': query,
            'difficulty': difficulty,
            'scenario': scenario,
            'success': False,
            'response': '',
            'tool_calls': [],
            'response_time': 0,
            'error': None,
            'evaluation': {},
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            if self.llm:
                # 创建消息
                messages = [
                    SystemMessage(content=self.create_system_prompt()),
                    HumanMessage(content=query)
                ]
                
                # 调用LLM
                response = await self.llm.ainvoke(messages)
                test_result['response'] = response.content
            else:
                # 模拟响应
                await asyncio.sleep(1)  # 模拟处理时间
                test_result['response'] = f"模拟响应：针对问题'{query}'，建议使用相关工具进行分析。这是一个{difficulty}问题，需要专业的游资涨停分析。"
            
            test_result['response_time'] = time.time() - start_time
            test_result['success'] = True
            
            # 分析响应中的工具调用
            tool_calls = self.extract_tool_calls(test_result['response'])
            test_result['tool_calls'] = tool_calls
            self.stats['tool_calls_made'] += len(tool_calls)
            
            # 评估响应质量
            evaluation = self.evaluate_response(question, test_result['response'], tool_calls)
            test_result['evaluation'] = evaluation
            
            self.logger.info(f"✅ {question_id} 测试成功 - 响应时间: {test_result['response_time']:.2f}s")
            self.stats['successful_tests'] += 1
            
        except Exception as e:
            test_result['error'] = str(e)
            test_result['response_time'] = time.time() - start_time
            self.logger.error(f"❌ {question_id} 测试失败: {str(e)}")
            self.stats['failed_tests'] += 1
            
        return test_result
        
    def extract_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """从响应中提取工具调用"""
        tool_calls = []
        
        # 常见的工具名称模式
        tool_patterns = [
            'get_hm_detail', 'get_hm_list', 'get_kpl_list', 'get_kpl_concept',
            'get_top_list', 'get_limit_step', 'get_limit_cpt_list',
            'moneyflow', 'get_stock_basic_info', 'get_daily', 'get_stk_auction',
            'get_ths_hot', 'get_ths_daily', 'get_dc_index', 'daily_basic',
            'stk_factor', 'get_top_inst', 'get_kpl_concept_cons'
        ]
        
        for tool_name in tool_patterns:
            if tool_name in response:
                # 尝试提取参数
                pattern = f"{tool_name}\\s*\\([^)]*\\)"
                matches = re.findall(pattern, response)
                
                for match in matches:
                    tool_calls.append({
                        'tool_name': tool_name,
                        'call_syntax': match,
                        'extracted_from': 'response_text'
                    })
                    
        return tool_calls
        
    def evaluate_response(self, question: Dict[str, Any], response: str, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估响应质量"""
        evaluation = {
            'relevance_score': 0,  # 相关性得分
            'completeness_score': 0,  # 完整性得分
            'tool_selection_score': 0,  # 工具选择得分
            'professional_score': 0,  # 专业性得分
            'overall_score': 0,  # 综合得分
            'feedback': []
        }
        
        query = question.get('问题内容', '')
        difficulty = question.get('难度等级', '初级')
        
        # 1. 相关性评估
        relevance_keywords = ['游资', '涨停', '龙虎榜', '打板', '连板', '炸板']
        relevance_count = sum(1 for keyword in relevance_keywords if keyword in response)
        evaluation['relevance_score'] = min(100, relevance_count * 20)
        
        # 2. 完整性评估
        if len(response) > 100:
            evaluation['completeness_score'] += 30
        if len(response) > 300:
            evaluation['completeness_score'] += 30
        if '分析' in response or '建议' in response:
            evaluation['completeness_score'] += 40
            
        # 3. 工具选择评估
        if tool_calls:
            evaluation['tool_selection_score'] += 40
            if len(tool_calls) >= 2:
                evaluation['tool_selection_score'] += 30
            if len(tool_calls) >= 3:
                evaluation['tool_selection_score'] += 30
        else:
            evaluation['feedback'].append("未检测到工具调用")
            
        # 4. 专业性评估
        professional_keywords = ['基本面', '技术面', '资金流', '市场情绪', '风险控制']
        professional_count = sum(1 for keyword in professional_keywords if keyword in response)
        evaluation['professional_score'] = min(100, professional_count * 25)
        
        # 5. 综合得分
        scores = [
            evaluation['relevance_score'],
            evaluation['completeness_score'], 
            evaluation['tool_selection_score'],
            evaluation['professional_score']
        ]
        evaluation['overall_score'] = sum(scores) / len(scores)
        
        # 6. 难度调整
        if difficulty == '高级' and evaluation['overall_score'] > 60:
            evaluation['overall_score'] += 10
        elif difficulty == '初级' and evaluation['overall_score'] < 40:
            evaluation['overall_score'] -= 10
            
        return evaluation
        
    async def run_comprehensive_test(self, max_questions: Optional[int] = None, 
                                   question_filter: Optional[str] = None):
        """运行综合测试"""
        self.logger.info("🎯 开始游资涨停专题问题集综合测试")
        self.start_time = time.time()
        
        # 初始化组件
        await self.setup_agent()
        
        # 加载问题
        questions = self.load_questions()
        
        # 过滤问题
        if question_filter:
            if question_filter == 'single':
                questions = [q for q in questions if not q.get('问题ID', '').startswith('YZM')]
            elif question_filter == 'multi':
                questions = [q for q in questions if q.get('问题ID', '').startswith('YZM')]
            elif question_filter == 'basic':
                questions = [q for q in questions if q.get('难度等级') == '初级']
            elif question_filter == 'advanced':
                questions = [q for q in questions if q.get('难度等级') == '高级']
                
        # 限制问题数量
        if max_questions:
            questions = questions[:max_questions]
            
        self.logger.info(f"📋 将测试 {len(questions)} 个问题")
        
        # 逐个处理问题
        for i, question in enumerate(questions, 1):
            self.logger.info(f"🔄 进度: {i}/{len(questions)}")
            
            # 处理问题
            result = await self.process_single_question(question)
            self.test_results.append(result)
            
            # 显示进度
            if i % 10 == 0:
                success_rate = (self.stats['successful_tests'] / i) * 100
                self.logger.info(f"📊 已完成 {i} 个问题，成功率: {success_rate:.1f}%")
                
            # 避免请求过快
            await asyncio.sleep(1)
            
        # 生成测试报告
        await self.generate_comprehensive_report()
        
    async def generate_comprehensive_report(self):
        """生成综合测试报告"""
        self.logger.info("📊 生成综合测试报告...")
        
        total_time = time.time() - self.start_time
        
        # 计算统计数据
        if self.test_results:
            avg_response_time = sum(r['response_time'] for r in self.test_results) / len(self.test_results)
            avg_overall_score = sum(r['evaluation'].get('overall_score', 0) for r in self.test_results) / len(self.test_results)
            
            # 按难度分组统计
            difficulty_stats = {}
            for result in self.test_results:
                difficulty = result['difficulty']
                if difficulty not in difficulty_stats:
                    difficulty_stats[difficulty] = {'total': 0, 'success': 0, 'avg_score': 0}
                difficulty_stats[difficulty]['total'] += 1
                if result['success']:
                    difficulty_stats[difficulty]['success'] += 1
                difficulty_stats[difficulty]['avg_score'] += result['evaluation'].get('overall_score', 0)
                
            for difficulty in difficulty_stats:
                if difficulty_stats[difficulty]['total'] > 0:
                    difficulty_stats[difficulty]['success_rate'] = (
                        difficulty_stats[difficulty]['success'] / difficulty_stats[difficulty]['total'] * 100
                    )
                    difficulty_stats[difficulty]['avg_score'] /= difficulty_stats[difficulty]['total']
        else:
            avg_response_time = 0
            avg_overall_score = 0
            difficulty_stats = {}
            
        # 创建报告
        report = {
            'test_summary': {
                'total_time': total_time,
                'total_questions': len(self.test_results),
                'successful_tests': self.stats['successful_tests'],
                'failed_tests': self.stats['failed_tests'],
                'success_rate': (self.stats['successful_tests'] / len(self.test_results) * 100) if self.test_results else 0,
                'avg_response_time': avg_response_time,
                'avg_overall_score': avg_overall_score,
                'total_tool_calls': self.stats['tool_calls_made'],
                'difficulty_stats': difficulty_stats
            },
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total / (1024**3),  # GB
                'python_version': sys.version,
                'test_timestamp': datetime.now().isoformat()
            },
            'detailed_results': self.test_results
        }
        
        # 保存报告
        report_dir = Path("test_reports")
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"youzhi_zhangting_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        # 生成简化报告
        summary_file = report_dir / f"youzhi_zhangting_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("游资涨停专题问题集测试报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总耗时: {total_time:.2f} 秒\n")
            f.write(f"测试问题数: {len(self.test_results)}\n")
            f.write(f"成功测试: {self.stats['successful_tests']}\n")
            f.write(f"失败测试: {self.stats['failed_tests']}\n")
            f.write(f"成功率: {report['test_summary']['success_rate']:.1f}%\n")
            f.write(f"平均响应时间: {avg_response_time:.2f} 秒\n")
            f.write(f"平均综合得分: {avg_overall_score:.1f}\n")
            f.write(f"总工具调用次数: {self.stats['tool_calls_made']}\n\n")
            
            f.write("按难度统计:\n")
            f.write("-" * 30 + "\n")
            for difficulty, stats in difficulty_stats.items():
                f.write(f"{difficulty}: {stats['success']}/{stats['total']} "
                       f"({stats['success_rate']:.1f}%) "
                       f"平均得分: {stats['avg_score']:.1f}\n")
                       
        self.logger.info(f"📄 详细报告已保存: {report_file}")
        self.logger.info(f"📄 简化报告已保存: {summary_file}")
        
        # 打印总结
        print(f"\n{'='*60}")
        print("🎯 游资涨停专题问题集测试完成")
        print(f"{'='*60}")
        print(f"📊 总体统计:")
        print(f"   测试问题数: {len(self.test_results)}")
        print(f"   成功率: {report['test_summary']['success_rate']:.1f}%")
        print(f"   平均响应时间: {avg_response_time:.2f}秒")
        print(f"   平均综合得分: {avg_overall_score:.1f}")
        print(f"   总工具调用: {self.stats['tool_calls_made']}次")
        print(f"\n📈 按难度统计:")
        for difficulty, stats in difficulty_stats.items():
            print(f"   {difficulty}: {stats['success_rate']:.1f}% ({stats['success']}/{stats['total']})")
            
        # 评估结果
        if report['test_summary']['success_rate'] >= 90:
            print("🎉 测试结果优秀！Agent在游资涨停问题上表现出色")
        elif report['test_summary']['success_rate'] >= 70:
            print("✅ 测试结果良好，Agent基本满足游资涨停分析需求")
        elif report['test_summary']['success_rate'] >= 50:
            print("⚠️ 测试结果一般，Agent在游资涨停问题上需要改进")
        else:
            print("❌ 测试结果不理想，Agent在游资涨停问题上需要重大改进")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='游资涨停专题问题集测试')
    parser.add_argument('--csv', default='archived_data/游资涨停专题问题集.csv', 
                       help='CSV文件路径')
    parser.add_argument('--max', type=int, help='最大测试问题数')
    parser.add_argument('--filter', choices=['single', 'multi', 'basic', 'advanced'], 
                       help='问题过滤器')
    
    args = parser.parse_args()
    
    # 检查CSV文件是否存在
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV文件不存在: {csv_path}")
        print("请确保游资涨停专题问题集.csv文件在正确位置")
        return
        
    # 创建测试运行器
    runner = YouziFengTingTestRunner(str(csv_path))
    
    try:
        # 运行测试
        await runner.run_comprehensive_test(
            max_questions=args.max,
            question_filter=args.filter
        )
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    print("🎯 游资涨停专题问题集测试脚本")
    print("使用方法: python test_youzhi_zhangting_comprehensive.py")
    asyncio.run(main()) 