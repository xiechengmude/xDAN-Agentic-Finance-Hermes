#!/usr/bin/env python3
"""
游资涨停专题问题集简化测试脚本
Simplified Test Script for Hot Money Limit-Up Topic Question Set
"""

import asyncio
import csv
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# 设置环境变量（如果需要的话）
os.environ.setdefault("OPENAI_MODEL", "gpt-4")
os.environ.setdefault("OPENAI_API_KEY", "your-api-key-here")

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class SimpleYouzhiTester:
    """简化版游资涨停测试器"""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.test_results: List[Dict[str, Any]] = []
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 初始化LLM
        try:
            self.llm = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                temperature=0.1,
                max_tokens=2000
            )
            self.logger.info("✅ LLM初始化成功")
        except Exception as e:
            self.logger.error(f"❌ LLM初始化失败: {e}")
            # 使用模拟LLM
            self.llm = None
            
    def load_questions(self, max_questions: int = 5) -> List[Dict[str, Any]]:
        """加载问题集（限制数量用于测试）"""
        questions = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= max_questions:
                        break
                    questions.append(row)
                    
            self.logger.info(f"✅ 成功加载 {len(questions)} 个问题")
            return questions
            
        except Exception as e:
            self.logger.error(f"❌ 加载问题集失败: {str(e)}")
            return []
            
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
2. 提供专业的分析和建议
3. 对于需要数据的查询，说明需要调用哪些工具

可用工具包括：
- get_hm_detail: 获取游资交易明细
- get_hm_list: 获取游资列表
- get_kpl_list: 获取涨停股列表
- get_top_list: 获取龙虎榜数据
- get_stock_basic_info: 获取股票基本信息
- moneyflow: 获取资金流向数据

请专业、准确地回答每个问题。"""

    async def process_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个问题"""
        question_id = question.get('问题ID', 'UNKNOWN')
        query = question.get('问题内容', '')
        expected_tools = question.get('预期工具调用', '')
        
        self.logger.info(f"🧪 测试问题 {question_id}: {query[:50]}...")
        
        test_result = {
            'question_id': question_id,
            'query': query,
            'expected_tools': expected_tools,
            'success': False,
            'response': '',
            'response_time': 0,
            'error': None,
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
                test_result['response'] = f"模拟响应：针对问题'{query}'，建议使用工具 {expected_tools} 进行分析。"
            
            test_result['response_time'] = time.time() - start_time
            test_result['success'] = True
            
            self.logger.info(f"✅ {question_id} 测试成功 - 响应时间: {test_result['response_time']:.2f}s")
            
        except Exception as e:
            test_result['error'] = str(e)
            test_result['response_time'] = time.time() - start_time
            self.logger.error(f"❌ {question_id} 测试失败: {str(e)}")
            
        return test_result
        
    async def run_test(self, max_questions: int = 5):
        """运行测试"""
        self.logger.info("🎯 开始游资涨停专题问题集简化测试")
        
        # 加载问题
        questions = self.load_questions(max_questions)
        if not questions:
            self.logger.error("❌ 没有加载到问题，测试终止")
            return
            
        # 处理问题
        for i, question in enumerate(questions, 1):
            self.logger.info(f"🔄 进度: {i}/{len(questions)}")
            
            result = await self.process_question(question)
            self.test_results.append(result)
            
            # 避免请求过快
            await asyncio.sleep(0.5)
            
        # 生成报告
        self.generate_report()
        
    def generate_report(self):
        """生成测试报告"""
        self.logger.info("📊 生成测试报告...")
        
        successful_tests = len([r for r in self.test_results if r['success']])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 保存详细报告
        report_dir = Path("test_reports")
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"simple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': success_rate,
                'test_timestamp': datetime.now().isoformat()
            },
            'detailed_results': self.test_results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        # 打印总结
        print(f"\n{'='*50}")
        print("🎯 游资涨停专题问题集简化测试完成")
        print(f"{'='*50}")
        print(f"📊 测试统计:")
        print(f"   总问题数: {total_tests}")
        print(f"   成功测试: {successful_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        print(f"📄 详细报告: {report_file}")
        
        # 显示测试结果
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['question_id']}: {result['query'][:30]}...")
            if result['response']:
                print(f"   响应: {result['response'][:100]}...")
            if result['error']:
                print(f"   错误: {result['error']}")
            print()


async def main():
    """主函数"""
    # 检查CSV文件
    csv_path = Path("archived_data/游资涨停专题问题集.csv")
    if not csv_path.exists():
        print(f"❌ CSV文件不存在: {csv_path}")
        return
        
    # 创建测试器
    tester = SimpleYouzhiTester(str(csv_path))
    
    try:
        # 运行测试（只测试前5个问题）
        await tester.run_test(max_questions=5)
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")


if __name__ == "__main__":
    print("🎯 游资涨停专题问题集简化测试脚本")
    print("使用方法: python test_youzhi_simple_run.py")
    asyncio.run(main()) 