#!/usr/bin/env python3
"""
测试带有实时时间注入的xDAN-Agent系统
主要测试：
1. 时间识别能力
2. 任务规划能力  
3. 多轮工具调用能力
"""

import asyncio
import json
from datetime import datetime, timedelta
from system_prompt import generate_system_prompt, get_current_time_info
from advanced_mcp_agent import AdvancedMCPAgent

class TimeAwareAgentTester:
    def __init__(self):
        self.agent = None
        self.test_results = []
        
    async def setup_agent(self):
        """初始化agent"""
        print("🚀 初始化时间感知Agent...")
        self.agent = AdvancedMCPAgent()
        
        # 初始化MCP连接
        success = await self.agent.initialize_mcp_connection()
        if not success:
            print("⚠️ MCP连接失败，将使用模拟模式进行测试")
        
        # 显示当前时间信息
        time_info = get_current_time_info()
        print(f"📅 当前时间信息已注入系统提示")
        print(f"⏰ 系统时间: {time_info['current_datetime']} ({time_info['weekday']})")
        print(f"🕐 北京时间: {time_info['beijing_datetime']} ({time_info['weekday_cn']})")
        print(f"📆 当前日期: {time_info['current_date']}")
        
        return True
        
    def analyze_time_recognition(self, response: str, query: str) -> dict:
        """分析agent的时间识别能力"""
        time_info = get_current_time_info()
        current_date = time_info['current_date']
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        analysis = {
            'query_contains_time_reference': False,
            'agent_recognized_time': False,
            'correct_date_usage': False,
            'time_context_analysis': False,
            'date_parameters_mentioned': False
        }
        
        # 检查查询是否包含时间引用
        time_keywords = ['今日', '今天', '昨天', '上周', '本月', '最近']
        if any(keyword in query for keyword in time_keywords):
            analysis['query_contains_time_reference'] = True
            
        # 检查agent是否识别了时间
        if any(keyword in response for keyword in ['时间', '日期', '今日', '今天']):
            analysis['agent_recognized_time'] = True
            
        # 检查是否使用了正确的日期
        if current_date in response or yesterday in response:
            analysis['correct_date_usage'] = True
            
        # 检查是否进行了时间上下文分析
        time_analysis_keywords = ['当前时间', '基于.*时间', '时间.*分析', '日期.*参数']
        if any(keyword in response for keyword in time_analysis_keywords):
            analysis['time_context_analysis'] = True
            
        # 检查是否提到了日期参数
        date_params = ['trade_date', 'start_date', 'end_date', 'YYYYMMDD', 'YYYY-MM-DD']
        if any(param in response for param in date_params):
            analysis['date_parameters_mentioned'] = True
            
        return analysis
        
    def analyze_task_planning(self, response: str) -> dict:
        """分析agent的任务规划能力"""
        analysis = {
            'has_analysis_section': False,
            'has_plan_section': False,
            'has_tool_calls_section': False,
            'has_results_section': False,
            'has_conclusion_section': False,
            'step_by_step_planning': False,
            'logical_sequence': False,
            'specific_parameters': False
        }
        
        # 检查是否有各个必需的部分
        sections = ['## Analysis', '## Plan', '## Tool Calls', '## Results', '## Conclusion']
        section_checks = ['has_analysis_section', 'has_plan_section', 'has_tool_calls_section', 
                         'has_results_section', 'has_conclusion_section']
        
        for section, check in zip(sections, section_checks):
            if section in response:
                analysis[check] = True
                
        # 检查是否有步骤规划
        step_indicators = ['步骤', '第一步', '第二步', '1.', '2.', '3.', 'Step']
        if any(indicator in response for indicator in step_indicators):
            analysis['step_by_step_planning'] = True
            
        # 检查逻辑顺序
        logical_keywords = ['首先', '然后', '接下来', '最后', '基于', '根据']
        if any(keyword in response for keyword in logical_keywords):
            analysis['logical_sequence'] = True
            
        # 检查具体参数
        param_keywords = ['参数', 'parameter', 'tag=', 'name=', 'date=']
        if any(keyword in response for keyword in param_keywords):
            analysis['specific_parameters'] = True
            
        return analysis
        
    def analyze_tool_calling_capability(self, response: str) -> dict:
        """分析agent的工具调用能力"""
        analysis = {
            'mentions_multiple_tools': False,
            'correct_tool_sequence': False,
            'proper_parameter_format': False,
            'explains_tool_purpose': False,
            'handles_dependencies': False,
            'expected_tool_count': 0,
            'mentioned_tool_count': 0
        }
        
        # 预期的工具调用（基于YZM002）
        expected_tools = [
            'get_kpl_list',
            'get_hm_detail', 
            'get_top_list',
            'moneyflow',
            'get_stock_basic_info'
        ]
        
        analysis['expected_tool_count'] = len(expected_tools)
        
        # 统计提到的工具
        mentioned_tools = []
        for tool in expected_tools:
            if tool in response:
                mentioned_tools.append(tool)
                
        analysis['mentioned_tool_count'] = len(mentioned_tools)
        analysis['mentions_multiple_tools'] = len(mentioned_tools) >= 3
        
        # 检查工具序列
        if len(mentioned_tools) >= 3:
            analysis['correct_tool_sequence'] = True
            
        # 检查参数格式
        param_patterns = ['(', ')', 'tag=', 'name=', 'hm_name=']
        if any(pattern in response for pattern in param_patterns):
            analysis['proper_parameter_format'] = True
            
        # 检查是否解释了工具用途
        purpose_keywords = ['用于', '获取', '分析', '查看', '评估']
        if any(keyword in response for keyword in purpose_keywords):
            analysis['explains_tool_purpose'] = True
            
        # 检查依赖关系处理
        dependency_keywords = ['基于', '根据.*结果', '结合', '对比']
        if any(keyword in response for keyword in dependency_keywords):
            analysis['handles_dependencies'] = True
            
        return analysis
        
    async def run_test(self, query: str, test_name: str):
        """运行单个测试"""
        print(f"\n{'='*60}")
        print(f"🧪 测试: {test_name}")
        print(f"❓ 查询: {query}")
        print(f"{'='*60}")
        
        try:
            # 执行查询
            print("🤖 Agent正在处理查询...")
            response = await self.agent.process_query(query)
            
            print(f"\n📝 Agent响应:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
            # 分析结果
            time_analysis = self.analyze_time_recognition(response, query)
            planning_analysis = self.analyze_task_planning(response)
            tool_analysis = self.analyze_tool_calling_capability(response)
            
            # 计算得分
            time_score = sum(time_analysis.values()) / len(time_analysis) * 100
            planning_score = sum(planning_analysis.values()) / len(planning_analysis) * 100
            tool_score = sum(tool_analysis.values()) / len(tool_analysis) * 100
            overall_score = (time_score + planning_score + tool_score) / 3
            
            test_result = {
                'test_name': test_name,
                'query': query,
                'response': response,
                'time_recognition': time_analysis,
                'task_planning': planning_analysis,
                'tool_calling': tool_analysis,
                'scores': {
                    'time_recognition': time_score,
                    'task_planning': planning_score,
                    'tool_calling': tool_score,
                    'overall': overall_score
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            
            # 显示分析结果
            print(f"\n📊 测试分析结果:")
            print(f"⏰ 时间识别能力: {time_score:.1f}%")
            print(f"📋 任务规划能力: {planning_score:.1f}%")
            print(f"🔧 工具调用能力: {tool_score:.1f}%")
            print(f"🎯 综合得分: {overall_score:.1f}%")
            
            # 详细分析
            print(f"\n🔍 详细分析:")
            print(f"时间识别: {time_analysis}")
            print(f"任务规划: {planning_analysis}")
            print(f"工具调用: {tool_analysis}")
            
            return test_result
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return None
            
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("🎯 开始时间感知Agent综合测试")
        
        # 设置agent
        await self.setup_agent()
        
        # 测试用例
        test_cases = [
            {
                'name': '游资涨停股集中度分析',
                'query': '如何分析今日涨停股的游资集中度和投资价值？',
                'description': '测试时间识别("今日")、多轮工具调用和综合分析能力'
            },
            {
                'name': '时间推算测试',
                'query': '帮我查询上周涨幅最大的板块股票是哪些然后逐个分析股票强度',
                'description': '测试时间推算("上周")和复杂任务规划能力'
            },
            {
                'name': '当前时间上下文测试',
                'query': '赵老哥今天买了哪些涨停股？请查看交易记录',
                'description': '测试当前时间上下文理解和具体查询能力'
            }
        ]
        
        # 执行测试
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔄 执行测试 {i}/{len(test_cases)}: {test_case['name']}")
            print(f"📝 测试描述: {test_case['description']}")
            
            await self.run_test(test_case['query'], test_case['name'])
            
            # 等待一下避免请求过快
            await asyncio.sleep(2)
            
        # 生成测试报告
        await self.generate_test_report()
        
    async def generate_test_report(self):
        """生成测试报告"""
        print(f"\n{'='*60}")
        print("📊 测试报告生成")
        print(f"{'='*60}")
        
        if not self.test_results:
            print("❌ 没有测试结果")
            return
            
        # 计算平均分数
        avg_scores = {
            'time_recognition': 0,
            'task_planning': 0,
            'tool_calling': 0,
            'overall': 0
        }
        
        for result in self.test_results:
            for key in avg_scores:
                avg_scores[key] += result['scores'][key]
                
        for key in avg_scores:
            avg_scores[key] /= len(self.test_results)
            
        print(f"\n🎯 综合测试结果:")
        print(f"⏰ 平均时间识别能力: {avg_scores['time_recognition']:.1f}%")
        print(f"📋 平均任务规划能力: {avg_scores['task_planning']:.1f}%")
        print(f"🔧 平均工具调用能力: {avg_scores['tool_calling']:.1f}%")
        print(f"🏆 综合平均得分: {avg_scores['overall']:.1f}%")
        
        # 保存详细报告
        report_file = f"test_results/time_aware_agent_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            import os
            os.makedirs('test_results', exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'test_summary': {
                        'total_tests': len(self.test_results),
                        'average_scores': avg_scores,
                        'test_timestamp': datetime.now().isoformat()
                    },
                    'detailed_results': self.test_results
                }, f, ensure_ascii=False, indent=2)
                
            print(f"📄 详细报告已保存: {report_file}")
            
        except Exception as e:
            print(f"⚠️ 报告保存失败: {str(e)}")
            
        # 评估结果
        if avg_scores['overall'] >= 80:
            print("🎉 测试结果优秀！Agent表现出色")
        elif avg_scores['overall'] >= 60:
            print("✅ 测试结果良好，Agent基本达到预期")
        else:
            print("⚠️ 测试结果需要改进，Agent能力有待提升")

async def main():
    """主函数"""
    tester = TimeAwareAgentTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main()) 