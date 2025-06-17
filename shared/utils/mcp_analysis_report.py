#!/usr/bin/env python3
"""
MCP服务器能力分析报告
分析FastMCP客户端与MCP服务器的连接状况、工具调用成功率和失败原因
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastmcp import Client
from fastmcp.client.transports import SSETransport

class MCPCapabilityAnalyzer:
    """MCP服务器能力分析器"""
    
    def __init__(self, server_url: str = "http://43.134.62.139:7223/sse"):
        self.server_url = server_url
        self.transport = SSETransport(
            url=server_url,
            headers={
                'User-Agent': 'MCP-Analyzer/1.0',
                'Accept': 'application/json, text/event-stream',
                'Content-Type': 'application/json'
            }
        )
        self.client = Client(self.transport)
        self.available_tools = []
        self.test_results = []
        
    async def analyze_connection(self) -> Dict[str, Any]:
        """分析连接状况"""
        print("🔌 分析MCP服务器连接状况...")
        
        connection_result = {
            'server_url': self.server_url,
            'connection_success': False,
            'response_time': 0,
            'tools_count': 0,
            'error': None
        }
        
        try:
            start_time = time.time()
            
            async with self.client:
                # 测试连接
                await self.client.ping()
                
                # 获取工具列表
                tools_result = await self.client.list_tools()
                
                # 处理工具列表
                if hasattr(tools_result, 'tools'):
                    self.available_tools = tools_result.tools
                elif isinstance(tools_result, list):
                    self.available_tools = tools_result
                else:
                    self.available_tools = []
                
                connection_result['connection_success'] = True
                connection_result['response_time'] = time.time() - start_time
                connection_result['tools_count'] = len(self.available_tools)
                
                print(f"✅ 连接成功，响应时间: {connection_result['response_time']:.2f}秒")
                print(f"📋 发现工具数量: {connection_result['tools_count']}")
                
        except Exception as e:
            connection_result['error'] = str(e)
            print(f"❌ 连接失败: {e}")
            
        return connection_result
    
    async def test_tool_categories(self) -> Dict[str, List[str]]:
        """分析工具分类"""
        print("\n📊 分析工具分类...")
        
        categories = {
            "股票基础": [],
            "行情数据": [],
            "财务数据": [],
            "基金数据": [],
            "港股数据": [],
            "美股数据": [],
            "宏观数据": [],
            "特色功能": [],
            "其他": []
        }
        
        for tool in self.available_tools:
            tool_name = tool.name.lower()
            
            if any(keyword in tool_name for keyword in ['basic', 'search', 'info']):
                categories["股票基础"].append(tool.name)
            elif any(keyword in tool_name for keyword in ['daily', 'weekly', 'monthly']):
                categories["行情数据"].append(tool.name)
            elif any(keyword in tool_name for keyword in ['income', 'balance', 'cashflow', 'financial']):
                categories["财务数据"].append(tool.name)
            elif 'fund' in tool_name:
                categories["基金数据"].append(tool.name)
            elif 'hk' in tool_name:
                categories["港股数据"].append(tool.name)
            elif 'us' in tool_name:
                categories["美股数据"].append(tool.name)
            elif any(keyword in tool_name for keyword in ['gdp', 'cpi', 'ppi', 'macro']):
                categories["宏观数据"].append(tool.name)
            elif any(keyword in tool_name for keyword in ['fuzzy', 'match', 'concept', 'top']):
                categories["特色功能"].append(tool.name)
            else:
                categories["其他"].append(tool.name)
        
        # 打印分类结果
        for category, tools in categories.items():
            if tools:
                print(f"  📁 {category}: {len(tools)}个工具")
                for tool in tools[:3]:  # 只显示前3个
                    print(f"    - {tool}")
                if len(tools) > 3:
                    print(f"    ... 还有{len(tools)-3}个工具")
        
        return categories
    
    async def test_sample_tools(self) -> List[Dict[str, Any]]:
        """测试样本工具调用"""
        print("\n🧪 测试样本工具调用...")
        
        # 定义测试用例
        test_cases = [
            {
                'name': 'tushareMcp_get_stock_basic_info',
                'params': {'name': '平安银行'},
                'description': '股票基本信息查询'
            },
            {
                'name': 'tushareMcp_search_stocks', 
                'params': {'keyword': '银行'},
                'description': '股票搜索功能'
            },
            {
                'name': 'tushareMcp_fuzzy_match_stocks',
                'params': {'keyword': '腾讯', 'top_n': 3},
                'description': '模糊匹配功能'
            },
            {
                'name': 'tushareMcp_get_daily',
                'params': {'ts_code': '000001.SZ', 'start_date': '20231201', 'end_date': '20231210'},
                'description': '日线数据获取'
            },
            {
                'name': 'tushareMcp_get_income_statement',
                'params': {'ts_code': '000001.SZ', 'period': '20231231'},
                'description': '利润表数据'
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n  🔍 测试: {test_case['description']}")
            
            result = {
                'tool_name': test_case['name'],
                'description': test_case['description'],
                'success': False,
                'response_time': 0,
                'data_format': 'unknown',
                'data_size': 0,
                'error': None
            }
            
            try:
                start_time = time.time()
                
                async with self.client:
                    response = await self.client.call_tool(test_case['name'], test_case['params'])
                
                result['response_time'] = time.time() - start_time
                result['success'] = True
                
                # 分析返回数据格式
                if response:
                    if isinstance(response, list) and len(response) > 0:
                        first_item = response[0]
                        if hasattr(first_item, 'text'):
                            try:
                                # 尝试解析为JSON
                                json.loads(first_item.text)
                                result['data_format'] = 'json'
                            except:
                                if 'ts_code' in first_item.text and 'name' in first_item.text:
                                    result['data_format'] = 'dataframe_string'
                                else:
                                    result['data_format'] = 'text'
                            result['data_size'] = len(first_item.text)
                        else:
                            result['data_format'] = 'structured'
                            result['data_size'] = len(str(first_item))
                    else:
                        result['data_format'] = 'empty_or_unknown'
                
                print(f"    ✅ 成功 - 响应时间: {result['response_time']:.2f}秒, 格式: {result['data_format']}")
                
            except Exception as e:
                result['error'] = str(e)
                print(f"    ❌ 失败: {e}")
            
            results.append(result)
            
            # 避免请求过于频繁
            await asyncio.sleep(0.5)
        
        return results
    
    def analyze_failure_patterns(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析失败模式"""
        print("\n📈 分析失败模式和成功率...")
        
        total_tests = len(test_results)
        successful_tests = sum(1 for r in test_results if r['success'])
        
        # 数据格式分析
        format_distribution = {}
        for result in test_results:
            if result['success']:
                fmt = result['data_format']
                format_distribution[fmt] = format_distribution.get(fmt, 0) + 1
        
        # 响应时间分析
        response_times = [r['response_time'] for r in test_results if r['success']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # 错误类型分析
        error_types = {}
        for result in test_results:
            if not result['success'] and result['error']:
                error_type = type(result['error']).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        analysis = {
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': total_tests - successful_tests,
            'avg_response_time': avg_response_time,
            'format_distribution': format_distribution,
            'error_types': error_types
        }
        
        # 打印分析结果
        print(f"  📊 总体成功率: {analysis['success_rate']:.1%} ({successful_tests}/{total_tests})")
        print(f"  ⏱️ 平均响应时间: {avg_response_time:.2f}秒")
        
        if format_distribution:
            print("  📋 数据格式分布:")
            for fmt, count in format_distribution.items():
                print(f"    - {fmt}: {count}次")
        
        if error_types:
            print("  ❌ 错误类型分布:")
            for error_type, count in error_types.items():
                print(f"    - {error_type}: {count}次")
        
        return analysis
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if analysis['success_rate'] < 0.8:
            recommendations.append("🔧 建议提高工具调用的稳定性和成功率")
        
        if 'dataframe_string' in analysis['format_distribution']:
            recommendations.append("📝 建议统一数据返回格式，避免DataFrame字符串混合JSON")
        
        if analysis['avg_response_time'] > 3.0:
            recommendations.append("⚡ 建议优化响应时间，当前平均响应时间较长")
        
        if analysis['failed_tests'] > 0:
            recommendations.append("🛠️ 建议增强错误处理和重试机制")
        
        recommendations.append("📊 建议实施工具质量分级，优先保证核心工具的稳定性")
        recommendations.append("🔍 建议增加工具调用的监控和日志记录")
        
        return recommendations
    
    async def run_full_analysis(self):
        """运行完整分析"""
        print("🚀 MCP服务器能力全面分析")
        print("=" * 60)
        
        # 1. 连接分析
        connection_result = await self.analyze_connection()
        
        if not connection_result['connection_success']:
            print("❌ 连接失败，无法进行后续分析")
            return
        
        # 2. 工具分类分析
        categories = await self.test_tool_categories()
        
        # 3. 样本工具测试
        test_results = await self.test_sample_tools()
        
        # 4. 失败模式分析
        analysis = self.analyze_failure_patterns(test_results)
        
        # 5. 生成建议
        recommendations = self.generate_recommendations(analysis)
        
        # 6. 生成报告
        print("\n" + "=" * 60)
        print("📋 分析报告总结")
        print("=" * 60)
        
        print(f"🔗 服务器地址: {self.server_url}")
        print(f"📊 工具总数: {connection_result['tools_count']}")
        print(f"✅ 调用成功率: {analysis['success_rate']:.1%}")
        print(f"⏱️ 平均响应时间: {analysis['avg_response_time']:.2f}秒")
        
        print(f"\n🎯 主要问题:")
        if analysis['success_rate'] < 1.0:
            print(f"  - 部分工具调用失败 ({analysis['failed_tests']}/{analysis['total_tests']})")
        
        if 'dataframe_string' in analysis['format_distribution']:
            print("  - 数据格式不统一 (JSON与DataFrame字符串混合)")
        
        if analysis['avg_response_time'] > 2.0:
            print("  - 响应时间较长")
        
        print(f"\n💡 改进建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        return {
            'connection': connection_result,
            'categories': categories,
            'test_results': test_results,
            'analysis': analysis,
            'recommendations': recommendations
        }

async def main():
    """主函数"""
    analyzer = MCPCapabilityAnalyzer()
    await analyzer.run_full_analysis()

if __name__ == "__main__":
    asyncio.run(main()) 