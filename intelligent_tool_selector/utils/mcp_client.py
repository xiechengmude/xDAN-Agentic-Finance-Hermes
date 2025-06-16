"""
MCP客户端管理模块
MCP Client Manager Module

提供MCP服务器连接和工具管理功能
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple

try:
    from fastmcp import Client
    from fastmcp.client.transports import SSETransport
    FASTMCP_AVAILABLE = True
except ImportError as e:
    FASTMCP_AVAILABLE = False
    print(f"⚠️ FastMCP 未安装，MCP功能将不可用: {e}")
    
    # 创建模拟类以避免运行时错误
    class Client:
        def __init__(self, *args, **kwargs):
            pass
    
    class SSETransport:
        def __init__(self, *args, **kwargs):
            pass

from .config import Config


class MCPClientManager:
    """MCP客户端管理器"""
    
    def __init__(self, server_url: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """
        初始化MCP客户端管理器
        
        Args:
            server_url: MCP服务器URL
            headers: 请求头
        """
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP 库未安装，请安装后再使用MCP功能")
            
        self.server_url = server_url or Config.MCP_SERVER_URL
        self.headers = headers or Config.get_mcp_headers()
        
        self.transport = SSETransport(
            url=self.server_url,
            headers=self.headers
        )
        self.client = Client(self.transport)
        
        # 工具缓存
        self.tools = []
        self.tool_schemas = {}
        self._tools_loaded = False
    
    async def load_tools_with_schemas(self) -> bool:
        """
        加载所有工具及其详细参数定义
        
        Returns:
            是否加载成功
        """
        try:
            async with self.client:
                tools_result = await self.client.list_tools()
                
                if hasattr(tools_result, 'tools'):
                    self.tools = tools_result.tools
                elif isinstance(tools_result, list):
                    self.tools = tools_result
                else:
                    return False
                
                # 构建详细的工具schema映射
                for tool in self.tools:
                    schema_info = {
                        'name': tool.name,
                        'description': tool.description,
                        'parameters': {}
                    }
                    
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        schema = tool.inputSchema
                        if isinstance(schema, dict) and 'properties' in schema:
                            for param_name, param_info in schema['properties'].items():
                                schema_info['parameters'][param_name] = {
                                    'type': param_info.get('type', 'string'),
                                    'description': param_info.get('description', ''),
                                    'required': param_name in schema.get('required', [])
                                }
                    
                    self.tool_schemas[tool.name] = schema_info
                
                self._tools_loaded = True
                return True
                
        except Exception as e:
            print(f"❌ 加载工具失败: {e}")
            return False
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Any, str]:
        """
        调用指定工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            (是否成功, 响应数据, 错误信息)
        """
        # 验证工具是否存在
        if tool_name not in self.tool_schemas:
            return False, None, f"工具 {tool_name} 不存在"
        
        # 验证和清理参数
        validated_params = self._validate_parameters(tool_name, parameters)
        if validated_params is None:
            return False, None, "参数验证失败"
        
        try:
            async with self.client:
                response = await self.client.call_tool(tool_name, validated_params)
                return True, response, "调用成功"
        except Exception as e:
            return False, None, str(e)
    
    def _validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        验证工具参数
        
        Args:
            tool_name: 工具名称
            parameters: 参数字典
            
        Returns:
            验证后的参数字典，验证失败返回None
        """
        tool_schema = self.tool_schemas[tool_name]
        validated_params = {}
        
        # 检查必需参数
        for param_name, param_info in tool_schema['parameters'].items():
            if param_info['required'] and param_name not in parameters:
                print(f"❌ 缺少必需参数: {param_name}")
                return None
        
        # 过滤有效参数
        for param_name, param_value in parameters.items():
            if param_name in tool_schema['parameters']:
                validated_params[param_name] = param_value
            else:
                print(f"⚠️ 忽略无效参数: {param_name}")
        
        return validated_params
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定工具的信息
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具信息字典
        """
        return self.tool_schemas.get(tool_name)
    
    def get_all_tools_info(self) -> Dict[str, Any]:
        """
        获取所有工具的信息
        
        Returns:
            所有工具信息的字典
        """
        return self.tool_schemas.copy()
    
    def get_tools_count(self) -> int:
        """
        获取工具总数
        
        Returns:
            工具总数
        """
        return len(self.tools)
    
    def is_tools_loaded(self) -> bool:
        """
        检查工具是否已加载
        
        Returns:
            是否已加载
        """
        return self._tools_loaded
    
    def search_tools(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索包含关键词的工具
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的工具列表
        """
        matching_tools = []
        keyword_lower = keyword.lower()
        
        for tool_name, tool_info in self.tool_schemas.items():
            if (keyword_lower in tool_name.lower() or 
                keyword_lower in tool_info['description'].lower()):
                matching_tools.append(tool_info)
        
        return matching_tools 