"""
xDAN-Agent Client for testing agentic capabilities with tool calling
"""

import json
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from system_prompt import SYSTEM_PROMPT, COMPACT_SYSTEM_PROMPT

@dataclass
class ToolCall:
    name: str
    parameters: Dict[str, Any]
    call_id: str = None

@dataclass
class Message:
    role: str
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

class xDANAgentClient:
    def __init__(self, 
                 model_url: str = "http://161.248.3.20:32790/v1",
                 model_name: str = "xDAN-Agent-Medium-v2-step300-0525"):
        self.model_url = model_url
        self.model_name = model_name
        self.conversation_history: List[Message] = []
        self.available_tools = []
        
    async def setup_mcp_tools(self):
        """Setup available MCP tools - placeholder for actual MCP integration"""
        # This would connect to actual MCP servers
        self.available_tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "num_results": {"type": "integer", "description": "Number of results to return", "default": 5}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_stock_data",
                    "description": "Get stock market data and analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock symbol"},
                            "period": {"type": "string", "description": "Time period (1d, 1w, 1m, etc.)"},
                            "data_type": {"type": "string", "description": "Type of data (price, volume, analysis)"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_sector_performance",
                    "description": "Analyze sector performance and top performers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "string", "description": "Analysis period"},
                            "metric": {"type": "string", "description": "Performance metric"},
                            "top_n": {"type": "integer", "description": "Number of top performers to return"}
                        },
                        "required": ["period"]
                    }
                }
            }
        ]
    
    async def call_model(self, messages: List[Dict], use_tools: bool = True) -> Dict:
        """Call the xDAN model with messages and optional tool calling"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer dummy-key"  # Adjust as needed
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        if use_tools and self.available_tools:
            payload["tools"] = self.available_tools
            payload["tool_choice"] = "auto"
        
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
    
    async def execute_tool_call(self, tool_call: ToolCall) -> str:
        """Execute a tool call - placeholder for actual MCP integration"""
        # This would call actual MCP servers
        if tool_call.name == "search_web":
            query = tool_call.parameters.get("query", "")
            return f"Web search results for '{query}': [Mock results - financial news, market data, analysis reports]"
        
        elif tool_call.name == "get_stock_data":
            symbol = tool_call.parameters.get("symbol", "")
            return f"Stock data for {symbol}: [Mock data - price movements, volume, technical indicators]"
        
        elif tool_call.name == "analyze_sector_performance":
            period = tool_call.parameters.get("period", "1w")
            return f"Sector performance analysis for {period}: [Mock analysis - top performing sectors, growth rates, market trends]"
        
        return f"Tool {tool_call.name} executed with parameters: {tool_call.parameters}"
    
    async def process_user_query(self, user_query: str, use_compact_prompt: bool = False) -> str:
        """Process a user query with multi-turn reasoning and tool calling"""
        # Initialize conversation with system prompt
        system_prompt = COMPACT_SYSTEM_PROMPT if use_compact_prompt else SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        max_iterations = 5
        iteration = 0
        
        print(f"\n=== Processing Query ===")
        print(f"User: {user_query}")
        print(f"Using {'Compact' if use_compact_prompt else 'Full'} System Prompt")
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # Call the model
            response = await self.call_model(messages)
            
            if "error" in response:
                return f"Error: {response['error']}"
            
            # Extract the assistant's response
            assistant_message = response.get("choices", [{}])[0].get("message", {})
            content = assistant_message.get("content", "")
            tool_calls = assistant_message.get("tool_calls", [])
            
            print(f"Assistant Response: {content[:200]}...")
            
            # Add assistant message to conversation
            messages.append({
                "role": "assistant", 
                "content": content,
                "tool_calls": tool_calls if tool_calls else None
            })
            
            # If no tool calls, we're done
            if not tool_calls:
                return content
            
            # Execute tool calls
            print(f"Executing {len(tool_calls)} tool calls...")
            for tool_call in tool_calls:
                tool_name = tool_call.get("function", {}).get("name", "")
                tool_params = tool_call.get("function", {}).get("arguments", {})
                tool_id = tool_call.get("id", f"call_{iteration}")
                
                if isinstance(tool_params, str):
                    try:
                        tool_params = json.loads(tool_params)
                    except:
                        tool_params = {}
                
                print(f"  - {tool_name}({tool_params})")
                
                # Execute tool
                tool_result = await self.execute_tool_call(
                    ToolCall(name=tool_name, parameters=tool_params, call_id=tool_id)
                )
                
                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_id
                })
        
        return "Maximum iterations reached. The agent may need more steps to complete the task."

async def test_agent():
    """Test the xDAN agent with various queries"""
    client = xDANAgentClient()
    await client.setup_mcp_tools()
    
    # Test queries
    test_queries = [
        "Hello, can you introduce yourself?",
        "What's the weather like today?",
        "帮我查询上周涨幅最大的板块股票是哪些然后逐个分析股票强度和未来的龙头股是什么?"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n{'='*60}")
        print(f"TEST {i+1}: {query}")
        print(f"{'='*60}")
        
        # Test with both prompt versions
        for compact in [False, True]:
            print(f"\n--- Testing with {'Compact' if compact else 'Full'} Prompt ---")
            result = await client.process_user_query(query, use_compact_prompt=compact)
            print(f"\nFinal Result:\n{result}")
            print(f"\n{'-'*40}")

if __name__ == "__main__":
    asyncio.run(test_agent())
