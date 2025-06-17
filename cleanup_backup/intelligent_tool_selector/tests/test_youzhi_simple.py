#!/usr/bin/env python3
"""
游资涨停专题问题集测试脚本（简化版）
"""

import asyncio
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "src"))

from agent.configuration import MCPConfiguration
from agent.mcp_tools import MCPToolManager
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class SimpleYouzhiTester:
    """简化版游资涨停测试器"""
    
    def __init__(self):
        self.results = []
        self.stats = {"success": 0, "failed": 0, "tool_calls": 0}
        
    async def setup(self):
        """初始化组件"""
        print("🔧 初始化Agent组件...")
        
        # 创建配置
        self.config = MCPConfiguration.from_runnable_config()
        print(f"✅ 配置: {self.config.model_name}")
        
        # 创建MCP工具管理器
        self.mcp_manager = MCPToolManager(self.config.mcp_server_url)
        await self.mcp_manager.initialize()
        tools_count = self.mcp_manager.get_tools_count()
        print(f"✅ MCP工具: {tools_count}个")
        
        # 创建LLM
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            base_url=self.config.model_url,
            api_key=self.config.model_api_key,
            temperature=0.1,
            max_tokens=2000
        )
        print("✅ LLM已创建")
        
    def create_prompt(self):
        """创建系统提示"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        return f"""你是xDAN金融智能助手，专门处理游资涨停股相关查询。

当前日期: {current_date}

你的任务：
1. 理解用户的游资涨停相关查询
2. 自主选择合适的工具来回答问题
3. 提供准确、专业的分析

工具选择原则：
- 根据问题内容自主判断需要哪些工具
- 不要依赖预设的工具调用建议
- 优先考虑数据准确性

请专业地回答问题。"""

    async def test_question(self, question_id: str, query: str):
        """测试单个问题"""
        print(f"\n🧪 测试 {question_id}: {query[:60]}...")
        
        start_time = time.time()
        
        try:
            # 创建消息
            messages = [
                SystemMessage(content=self.create_prompt()),
                HumanMessage(content=query)
            ]
            
            # 调用LLM
            response = await self.llm.ainvoke(messages)
            
            response_time = time.time() - start_time
            
            # 分析工具调用
            tool_calls = self.extract_tools(response.content)
            
            result = {
                'question_id': question_id,
                'query': query,
                'response': response.content,
                'tool_calls': tool_calls,
                'response_time': response_time,
                'success': True
            }
            
            self.results.append(result)
            self.stats['success'] += 1
            self.stats['tool_calls'] += len(tool_calls)
            
            print(f"✅ 成功 - {response_time:.2f}s - 工具调用: {len(tool_calls)}个")
            
            if tool_calls:
                for tool in tool_calls:
                    print(f"   🔧 {tool}")
            
            return result
            
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
            self.stats['failed'] += 1
            return None
            
    def extract_tools(self, response: str) -> List[str]:
        """提取工具调用"""
        tools = []
        tool_names = [
            'get_hm_detail', 'get_hm_list', 'get_kpl_list', 
            'get_top_list', 'get_limit_step', 'moneyflow',
            'get_stock_basic_info', 'get_daily'
        ]
        
        for tool in tool_names:
            if tool in response:
                tools.append(tool)
                
        return list(set(tools))  # 去重
        
    async def run_test(self, max_questions: int = 5):
        """运行测试"""
        print("🎯 游资涨停专题测试开始")
        print("=" * 50)
        
        # 初始化
        await self.setup()
        
        # 测试样本问题
        sample_questions = [
            ("YZ001", "今天有哪些知名游资在操作涨停股？请帮我查看"),
            ("YZ003", "赵老哥今天买了哪些涨停股？请查看交易记录"),
            ("YZ008", "今天游资最活跃的涨停股是哪只？"),
            ("YZ013", "如何通过游资明细预测明日涨停股？"),
            ("YZ018", "今天游资在新能源涨停股上的布局如何？")
        ]
        
        # 限制测试数量
        test_questions = sample_questions[:max_questions]
        
        print(f"📋 将测试 {len(test_questions)} 个问题")
        
        # 逐个测试
        for i, (qid, query) in enumerate(test_questions, 1):
            print(f"\n🔄 进度: {i}/{len(test_questions)}")
            
            await self.test_question(qid, query)
            
            # 避免请求过快
            if i < len(test_questions):
                await asyncio.sleep(2)
                
        # 生成报告
        self.generate_report()
        
    def generate_report(self):
        """生成报告"""
        print(f"\n{'='*60}")
        print("📊 测试报告")
        print(f"{'='*60}")
        
        total_tests = self.stats['success'] + self.stats['failed']
        success_rate = (self.stats['success'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {self.stats['success']}")
        print(f"失败: {self.stats['failed']}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"总工具调用: {self.stats['tool_calls']}")
        
        if self.results:
            avg_time = sum(r['response_time'] for r in self.results) / len(self.results)
            print(f"平均响应时间: {avg_time:.2f}秒")
            
        # 保存详细结果
        report_dir = Path("test_reports")
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"youzhi_simple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'summary': self.stats,
            'success_rate': success_rate,
            'results': self.results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        print(f"\n📄 详细报告已保存: {report_file}")
        
        # 评估结果
        if success_rate >= 80:
            print("🎉 测试结果优秀！")
        elif success_rate >= 60:
            print("✅ 测试结果良好")
        else:
            print("⚠️ 测试结果需要改进")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='游资涨停专题简化测试')
    parser.add_argument('--max', type=int, default=5, help='最大测试问题数')
    
    args = parser.parse_args()
    
    tester = SimpleYouzhiTester()
    
    try:
        await tester.run_test(max_questions=args.max)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🎯 游资涨停专题问题集测试脚本（简化版）")
    print("使用方法:")
    print("  python test_youzhi_simple.py")
    print("  python test_youzhi_simple.py --max 3")
    print()
    asyncio.run(main()) 