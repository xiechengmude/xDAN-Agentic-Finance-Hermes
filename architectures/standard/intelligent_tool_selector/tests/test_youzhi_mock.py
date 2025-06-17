#!/usr/bin/env python3
"""
游资涨停专题问题集模拟测试脚本
Mock Test Script for Hot Money Limit-Up Topic Question Set
"""

import asyncio
import csv
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging


class MockYouzhiTester:
    """模拟版游资涨停测试器"""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.test_results: List[Dict[str, Any]] = []
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 模拟工具响应
        self.mock_responses = {
            'get_hm_detail': "获取到游资交易明细数据，显示今日活跃游资包括赵老哥、章盟主等。",
            'get_hm_list': "获取到游资列表，包含知名游资席位信息。",
            'get_kpl_list': "获取到涨停股列表，今日共有XX只股票涨停。",
            'get_top_list': "获取到龙虎榜数据，显示资金流向和席位变化。",
            'get_stock_basic_info': "获取到股票基本信息，包含行业、概念等数据。",
            'moneyflow': "获取到资金流向数据，显示主力资金动向。"
        }
        
    def load_questions(self, max_questions: int = 10) -> List[Dict[str, Any]]:
        """加载问题集"""
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
            
    def generate_mock_response(self, question: Dict[str, Any]) -> str:
        """生成模拟响应"""
        query = question.get('问题内容', '')
        expected_tools = question.get('预期工具调用', '')
        difficulty = question.get('难度等级', '初级')
        
        # 提取预期工具
        tools_mentioned = []
        for tool in self.mock_responses.keys():
            if tool in expected_tools:
                tools_mentioned.append(tool)
        
        if not tools_mentioned:
            # 根据问题内容推测需要的工具
            if '游资' in query and ('明细' in query or '交易' in query):
                tools_mentioned.append('get_hm_detail')
            if '涨停' in query:
                tools_mentioned.append('get_kpl_list')
            if '龙虎榜' in query:
                tools_mentioned.append('get_top_list')
        
        # 构建响应
        response_parts = []
        
        # 添加分析开头
        response_parts.append(f"针对您的问题：{query}")
        response_parts.append("\n我将为您进行专业分析：")
        
        # 添加工具调用模拟
        if tools_mentioned:
            response_parts.append(f"\n📊 数据获取：")
            for tool in tools_mentioned:
                response_parts.append(f"- 调用 {tool}: {self.mock_responses[tool]}")
        
        # 添加分析内容
        response_parts.append(f"\n🔍 专业分析：")
        if difficulty == '初级':
            response_parts.append("基于当前市场数据，建议关注以下要点：")
            response_parts.append("1. 游资活跃度较高，市场情绪积极")
            response_parts.append("2. 涨停股集中在热门概念板块")
            response_parts.append("3. 建议关注龙虎榜席位变化")
        elif difficulty == '中级':
            response_parts.append("深度分析显示：")
            response_parts.append("1. 游资操作呈现明显的板块轮动特征")
            response_parts.append("2. 连板股持续性需要结合资金流向判断")
            response_parts.append("3. 建议构建多维度监控体系")
        else:  # 高级
            response_parts.append("高级策略分析：")
            response_parts.append("1. 需要建立量化模型进行游资行为预测")
            response_parts.append("2. 结合技术面和基本面进行综合判断")
            response_parts.append("3. 构建风险控制和预警机制")
        
        # 添加建议
        response_parts.append(f"\n💡 投资建议：")
        response_parts.append("- 保持理性，控制风险")
        response_parts.append("- 关注市场热点变化")
        response_parts.append("- 建立系统性的跟踪机制")
        
        return "\n".join(response_parts)
            
    async def process_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个问题"""
        question_id = question.get('问题ID', 'UNKNOWN')
        query = question.get('问题内容', '')
        expected_tools = question.get('预期工具调用', '')
        difficulty = question.get('难度等级', '初级')
        
        self.logger.info(f"🧪 测试问题 {question_id}: {query[:50]}...")
        
        test_result = {
            'question_id': question_id,
            'query': query,
            'expected_tools': expected_tools,
            'difficulty': difficulty,
            'success': False,
            'response': '',
            'response_time': 0,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            # 模拟处理时间
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # 生成模拟响应
            test_result['response'] = self.generate_mock_response(question)
            test_result['response_time'] = time.time() - start_time
            test_result['success'] = True
            
            self.logger.info(f"✅ {question_id} 测试成功 - 响应时间: {test_result['response_time']:.2f}s")
            
        except Exception as e:
            test_result['error'] = str(e)
            test_result['response_time'] = time.time() - start_time
            self.logger.error(f"❌ {question_id} 测试失败: {str(e)}")
            
        return test_result
        
    async def run_test(self, max_questions: int = 10):
        """运行测试"""
        self.logger.info("🎯 开始游资涨停专题问题集模拟测试")
        start_time = time.time()
        
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
            
        total_time = time.time() - start_time
        
        # 生成报告
        self.generate_report(total_time)
        
    def generate_report(self, total_time: float):
        """生成测试报告"""
        self.logger.info("📊 生成测试报告...")
        
        successful_tests = len([r for r in self.test_results if r['success']])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = sum(r['response_time'] for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        # 按难度统计
        difficulty_stats = {}
        for result in self.test_results:
            difficulty = result['difficulty']
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {'total': 0, 'success': 0}
            difficulty_stats[difficulty]['total'] += 1
            if result['success']:
                difficulty_stats[difficulty]['success'] += 1
        
        for difficulty in difficulty_stats:
            stats = difficulty_stats[difficulty]
            stats['success_rate'] = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        # 保存详细报告
        report_dir = Path("test_reports")
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"mock_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'test_summary': {
                'total_time': total_time,
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'difficulty_stats': difficulty_stats,
                'test_timestamp': datetime.now().isoformat()
            },
            'detailed_results': self.test_results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        # 生成简化报告
        summary_file = report_dir / f"mock_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("游资涨停专题问题集模拟测试报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总耗时: {total_time:.2f} 秒\n")
            f.write(f"测试问题数: {total_tests}\n")
            f.write(f"成功测试: {successful_tests}\n")
            f.write(f"成功率: {success_rate:.1f}%\n")
            f.write(f"平均响应时间: {avg_response_time:.2f} 秒\n\n")
            
            f.write("按难度统计:\n")
            f.write("-" * 30 + "\n")
            for difficulty, stats in difficulty_stats.items():
                f.write(f"{difficulty}: {stats['success']}/{stats['total']} "
                       f"({stats['success_rate']:.1f}%)\n")
                       
        # 打印总结
        print(f"\n{'='*60}")
        print("🎯 游资涨停专题问题集模拟测试完成")
        print(f"{'='*60}")
        print(f"📊 总体统计:")
        print(f"   测试问题数: {total_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        print(f"   平均响应时间: {avg_response_time:.2f}秒")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"\n📈 按难度统计:")
        for difficulty, stats in difficulty_stats.items():
            print(f"   {difficulty}: {stats['success_rate']:.1f}% ({stats['success']}/{stats['total']})")
            
        print(f"\n📄 详细报告: {report_file}")
        print(f"📄 简化报告: {summary_file}")
        
        # 显示部分测试结果示例
        print(f"\n📋 测试结果示例:")
        for i, result in enumerate(self.test_results[:3]):
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['question_id']}: {result['query'][:40]}...")
            if result['response']:
                print(f"   响应: {result['response'][:120]}...")
            print()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='游资涨停专题问题集模拟测试')
    parser.add_argument('--csv', default='archived_data/游资涨停专题问题集.csv', 
                       help='CSV文件路径')
    parser.add_argument('--max', type=int, default=10, help='最大测试问题数')
    
    args = parser.parse_args()
    
    # 检查CSV文件
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV文件不存在: {csv_path}")
        return
        
    # 创建测试器
    tester = MockYouzhiTester(str(csv_path))
    
    try:
        # 运行测试
        await tester.run_test(max_questions=args.max)
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🎯 游资涨停专题问题集模拟测试脚本")
    print("使用方法: python test_youzhi_mock.py [--max 数量]")
    asyncio.run(main()) 