"""
Final xDAN-Agent Client with MCP Integration and Comprehensive Testing
"""

import json
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from optimized_prompt import OPTIMIZED_SYSTEM_PROMPT

@dataclass
class MCPToolCall:
    name: str
    parameters: Dict[str, Any]
    call_id: str = None

class FinalxDANAgentClient:
    def __init__(self, 
                 model_url: str = "http://161.248.3.20:32790/v1",
                 model_name: str = "xDAN-Agent-Medium-v2-step300-0525"):
        self.model_url = model_url
        self.model_name = model_name
        self.conversation_history: List[Dict] = []
        self.mcp_servers = {}  # Will store MCP server connections
        
    async def setup_mcp_servers(self):
        """Setup MCP server connections (placeholder for actual implementation)"""
        # This would connect to actual MCP servers
        # For now, we'll simulate the available tools
        self.mcp_servers = {
            "financial_data": {
                "tools": [
                    "get_sector_performance",
                    "get_stock_data", 
                    "analyze_market_trends",
                    "get_top_performers"
                ]
            },
            "web_search": {
                "tools": [
                    "search_financial_news",
                    "search_company_info",
                    "search_market_analysis"
                ]
            }
        }
        print("MCP servers configured (simulated)")
    
    async def call_model(self, messages: List[Dict]) -> Dict:
        """Call the xDAN model"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer dummy-key"
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.model_url}/chat/completions", 
                                      headers=headers, 
                                      json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        return {"error": f"HTTP {response.status}: {error_text}"}
            except Exception as e:
                return {"error": f"Request failed: {str(e)}"}
    
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute MCP tool call (simulated)"""
        # This would call actual MCP servers
        # For now, we'll return realistic mock data
        
        if tool_name == "get_sector_performance":
            period = parameters.get("period", "1w")
            return f"""上周涨幅最大的板块排名：
1. 新能源汽车板块 (+12.5%)
   - 主要股票：宁德时代(300750), 比亚迪(002594), 亿纬锂能(300014)
2. 人工智能板块 (+8.7%)
   - 主要股票：科大讯飞(002230), 海康威视(002415), 大华股份(002236)
3. 半导体板块 (+6.3%)
   - 主要股票：中芯国际(688981), 韦尔股份(603501), 北方华创(002371)"""
        
        elif tool_name == "get_stock_data":
            symbol = parameters.get("symbol", "")
            return f"""{symbol} 详细数据：
- 当前价格：¥85.60 (+3.2%)
- 成交量：1.2亿股 (较前日+45%)
- 市盈率：25.6
- 市净率：3.8
- 总市值：2156亿元
- 技术指标：RSI=72 (超买区间), MACD金叉"""
        
        elif tool_name == "analyze_market_trends":
            return """市场趋势分析：
- 整体趋势：上升通道，成交量放大
- 资金流向：主力资金净流入，北向资金持续买入
- 政策环境：新能源政策支持，AI发展规划利好
- 风险提示：估值偏高，注意回调风险"""
        
        elif tool_name == "search_financial_news":
            query = parameters.get("query", "")
            return f"""关于 {query} 的最新财经新闻：
1. 新能源汽车销量创新高，产业链公司受益
2. 政府发布AI产业发展规划，相关概念股活跃
3. 机构看好新能源板块长期投资价值
4. 外资持续增持A股核心资产"""
        
        return f"工具 {tool_name} 执行完成，参数：{parameters}"
    
    async def process_financial_query(self, user_query: str) -> str:
        """Process the specific financial query with full agent capabilities"""
        
        # Enhanced system prompt for financial analysis
        enhanced_prompt = f"""{OPTIMIZED_SYSTEM_PROMPT}

## MCP Tool Integration
You have access to the following tools through MCP servers:
- get_sector_performance(period, metric, top_n): Get sector performance rankings
- get_stock_data(symbol, period, data_type): Get detailed stock information  
- analyze_market_trends(timeframe): Analyze overall market trends
- search_financial_news(query): Search for relevant financial news

## Tool Calling Instructions
When you need data, specify the exact tool calls in this format:
TOOL_CALL: tool_name(parameter1="value1", parameter2="value2")

## Response Requirements
For financial analysis queries, provide:
1. Clear intent recognition
2. Systematic data gathering plan
3. Specific tool calls with parameters
4. Comprehensive analysis of results
5. Actionable investment insights"""

        messages = [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_query}
        ]
        
        max_iterations = 3
        iteration = 0
        
        print(f"\n{'='*60}")
        print(f"Processing Financial Query")
        print(f"Query: {user_query}")
        print(f"{'='*60}")
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # Call the model
            response = await self.call_model(messages)
            
            if "error" in response:
                return f"Error: {response['error']}"
            
            # Extract response
            assistant_message = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"Model Response Length: {len(assistant_message)} characters")
            
            # Add assistant message to conversation
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Check for tool calls in the response
            tool_calls = self.extract_tool_calls(assistant_message)
            
            if not tool_calls:
                print("No tool calls found. Analysis complete.")
                return assistant_message
            
            # Execute tool calls
            print(f"Executing {len(tool_calls)} tool calls...")
            tool_results = []
            
            for tool_call in tool_calls:
                print(f"  - {tool_call.name}({tool_call.parameters})")
                result = await self.execute_mcp_tool(tool_call.name, tool_call.parameters)
                tool_results.append(f"Tool: {tool_call.name}\nResult: {result}")
            
            # Add tool results to conversation
            tool_summary = "\n\n".join(tool_results)
            messages.append({
                "role": "user", 
                "content": f"工具执行结果：\n{tool_summary}\n\n请基于这些数据进行综合分析并给出最终结论。"
            })
        
        return "Analysis completed after maximum iterations."
    
    def extract_tool_calls(self, response: str) -> List[MCPToolCall]:
        """Extract tool calls from model response"""
        tool_calls = []
        lines = response.split('\n')
        
        for line in lines:
            if 'TOOL_CALL:' in line or '工具调用:' in line:
                # Extract tool call from line
                tool_part = line.split('TOOL_CALL:')[-1].split('工具调用:')[-1].strip()
                
                # Parse tool name and parameters
                if '(' in tool_part and ')' in tool_part:
                    tool_name = tool_part.split('(')[0].strip()
                    params_str = tool_part.split('(')[1].split(')')[0]
                    
                    # Simple parameter parsing
                    parameters = {}
                    if params_str:
                        for param in params_str.split(','):
                            if '=' in param:
                                key, value = param.split('=', 1)
                                key = key.strip().strip('"').strip("'")
                                value = value.strip().strip('"').strip("'")
                                parameters[key] = value
                    
                    tool_calls.append(MCPToolCall(name=tool_name, parameters=parameters))
            
            # Also look for common tool patterns
            if any(tool in line for tool in ['get_sector_performance', 'get_stock_data', 'analyze_market_trends']):
                # Extract based on common patterns
                for tool in ['get_sector_performance', 'get_stock_data', 'analyze_market_trends', 'search_financial_news']:
                    if tool in line:
                        tool_calls.append(MCPToolCall(name=tool, parameters={"period": "1w"}))
                        break
        
        return tool_calls

async def test_financial_analysis():
    """Test the financial analysis capabilities"""
    client = FinalxDANAgentClient()
    await client.setup_mcp_servers()
    
    # The specific financial query from the requirements
    financial_query = "帮我查询上周涨幅最大的板块股票是哪些然后逐个分析股票强度和未来的龙头股是什么?"
    
    print("Starting comprehensive financial analysis test...")
    result = await client.process_financial_query(financial_query)
    
    print(f"\n{'='*80}")
    print("FINAL ANALYSIS RESULT")
    print(f"{'='*80}")
    print(result)
    
    # Evaluate the result
    evaluation_criteria = [
        ("Intent Recognition", "分析" in result or "Analysis" in result),
        ("Task Planning", "规划" in result or "Plan" in result),
        ("Tool Integration", "工具" in result or "Tool" in result),
        ("Stock Analysis", "股票" in result and "强度" in result),
        ("Future Prediction", "龙头" in result or "未来" in result),
        ("Comprehensive Response", len(result) > 500),
    ]
    
    print(f"\n{'='*80}")
    print("EVALUATION RESULTS")
    print(f"{'='*80}")
    
    passed_criteria = 0
    for criterion, passed in evaluation_criteria:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{criterion}: {status}")
        if passed:
            passed_criteria += 1
    
    success_rate = (passed_criteria / len(evaluation_criteria)) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_criteria}/{len(evaluation_criteria)})")
    
    if success_rate >= 80:
        print("🎉 Agent performance is EXCELLENT!")
    elif success_rate >= 60:
        print("👍 Agent performance is GOOD!")
    else:
        print("⚠️  Agent performance needs improvement.")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_financial_analysis())
