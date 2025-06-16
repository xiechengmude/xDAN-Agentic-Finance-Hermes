"""
智能工具选择器核心模块
Intelligent Tool Selector Core Module

提供基于大语言模型的智能工具选择功能
"""

import asyncio
import openai
from typing import Dict, List, Any, Optional, Tuple

from ..utils.config import Config
from ..utils.mcp_client import MCPClientManager
from .json_parser import JSONParser


class IntelligentToolSelector:
    """智能工具选择器"""
    
    def __init__(self, 
                 mcp_server_url: Optional[str] = None,
                 model_url: Optional[str] = None,
                 model_name: Optional[str] = None):
        """
        初始化智能工具选择器
        
        Args:
            mcp_server_url: MCP服务器URL
            model_url: 模型服务器URL
            model_name: 模型名称
        """
        # 配置初始化
        self.config = Config.from_env()
        if mcp_server_url:
            self.config['mcp_server_url'] = mcp_server_url
        if model_url:
            self.config['model_url'] = model_url
        if model_name:
            self.config['model_name'] = model_name
        
        Config.validate(self.config)
        
        # MCP客户端管理器
        self.mcp_manager = MCPClientManager(
            server_url=self.config['mcp_server_url']
        )
        
        # 模型客户端
        self.llm_client = openai.OpenAI(
            base_url=self.config['model_url'],
            api_key=self.config['model_api_key']
        )
        
        # JSON解析器
        self.json_parser = JSONParser()
        
        # 状态
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        初始化工具选择器（加载工具定义）
        
        Returns:
            是否初始化成功
        """
        success = await self.mcp_manager.load_tools_with_schemas()
        if success:
            self._initialized = True
            print(f"✅ 成功加载 {self.mcp_manager.get_tools_count()} 个MCP工具")
        else:
            print("❌ 无法加载MCP工具")
        return success
    
    async def select_and_execute_tool(self, user_query: str) -> Dict[str, Any]:
        """
        智能选择并执行工具
        
        Args:
            user_query: 用户查询
            
        Returns:
            包含选择结果和执行结果的字典
        """
        if not self._initialized:
            await self.initialize()
        
        # 1. 智能工具选择
        selection_result = await self._intelligent_tool_selection(user_query)
        
        if not selection_result:
            return {
                'success': False,
                'error': '工具选择失败',
                'selection_result': None,
                'execution_result': None
            }
        
        # 2. 提取选择的工具和参数
        primary_tool = selection_result.get('tool_selection', {}).get('primary_tool', {})
        tool_name = primary_tool.get('name', '')
        parameter_mapping = selection_result.get('parameter_mapping', {})
        
        if not tool_name:
            return {
                'success': False,
                'error': '未选择到有效工具',
                'selection_result': selection_result,
                'execution_result': None
            }
        
        # 3. 执行工具
        success, response, message = await self.mcp_manager.call_tool(tool_name, parameter_mapping)
        
        return {
            'success': success,
            'error': message if not success else None,
            'selection_result': selection_result,
            'execution_result': {
                'tool_name': tool_name,
                'parameters': parameter_mapping,
                'response': response,
                'message': message
            }
        }
    
    async def _intelligent_tool_selection(self, user_query: str) -> Dict[str, Any]:
        """
        使用大模型进行智能工具选择
        
        Args:
            user_query: 用户查询
            
        Returns:
            工具选择结果
        """
        prompt = self._generate_tool_selection_prompt(user_query)
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.config['model_name'],
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一个专业的金融数据分析工具选择专家，擅长理解用户需求并选择最合适的工具。你必须严格按照工具的真实参数定义来组装参数，不能自创参数名称。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['model_temperature'],
                max_tokens=self.config['model_max_tokens']
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # 使用增强的JSON解析
            result = self.json_parser.extract_json_from_response(response_text)
            
            # 验证JSON结构
            if result and self.json_parser.validate_json_structure(result):
                return result
            else:
                print("❌ JSON结构验证失败")
                return {}
                
        except Exception as e:
            print(f"❌ 工具选择失败: {e}")
            return {}
    
    def _generate_tool_selection_prompt(self, user_query: str) -> str:
        """生成工具选择提示词"""
        
        # 构建工具列表信息（包含参数定义）
        tools_info = []
        all_tools_info = self.mcp_manager.get_all_tools_info()
        
        for i, (tool_name, schema) in enumerate(all_tools_info.items(), 1):
            tools_info.append(f"{i:3d}. {tool_name}")
            tools_info.append(f"     描述: {schema['description']}")
            
            if schema['parameters']:
                tools_info.append("     参数:")
                for param_name, param_info in schema['parameters'].items():
                    required_mark = "🔴必需" if param_info['required'] else "⚪可选"
                    param_type = param_info['type']
                    param_desc = param_info['description']
                    tools_info.append(f"       {required_mark} {param_name} ({param_type}): {param_desc}")
            else:
                tools_info.append("     参数: 无")
            tools_info.append("")
        
        tools_text = "\n".join(tools_info)
        
        prompt = f"""你是一个专业的金融数据分析工具选择专家。用户提出了一个问题，你需要从可用的MCP工具中选择最合适的工具来回答这个问题。

## 用户问题
{user_query}

## 可用工具列表 (共{len(all_tools_info)}个)
{tools_text}

## 分析要求
请仔细分析用户的问题，理解其核心需求，然后从上述工具中选择最合适的工具。

考虑因素：
1. **问题类型**: 是查询股票信息、财务数据、游资动向、还是其他？
2. **数据需求**: 需要什么类型的数据（基础信息、行情数据、财务报表等）？
3. **时间范围**: 是否涉及特定时间的数据？
4. **参数匹配**: 选择的工具参数是否能满足查询需求？

## 重要提醒
- 必须使用工具的真实参数名称，不能自创参数
- 参数值必须符合工具要求的格式（如日期格式YYYYMMDD）
- 🔴标记的参数是必需的，必须提供
- ⚪标记的参数是可选的，可以不提供

## 输出格式
请以JSON格式输出你的分析结果：

```json
{{
  "analysis": {{
    "user_intent": "用户意图分析",
    "data_type_needed": "需要的数据类型",
    "time_scope": "时间范围分析",
    "complexity": "复杂度评估"
  }},
  "tool_selection": {{
    "primary_tool": {{
      "name": "主要工具名称",
      "reason": "选择理由",
      "confidence": 0.9
    }},
    "alternative_tools": [
      {{
        "name": "备选工具名称",
        "reason": "备选理由",
        "confidence": 0.7
      }}
    ]
  }},
  "parameter_mapping": {{
    "参数名1": "参数值1",
    "参数名2": "参数值2"
  }}
}}
```

请开始分析并选择工具："""
        
        return prompt
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取指定工具的信息"""
        return self.mcp_manager.get_tool_info(tool_name)
    
    def search_tools(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索工具"""
        return self.mcp_manager.search_tools(keyword)
    
    def get_tools_count(self) -> int:
        """获取工具总数"""
        return self.mcp_manager.get_tools_count()
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized 