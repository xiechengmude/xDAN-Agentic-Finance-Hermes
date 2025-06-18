"""
MCP客户端管理模块
MCP Client Manager Module

提供MCP服务器连接和工具管理功能
"""

import asyncio
import time
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
from .langfuse_integration import log_tool_call


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
        # 重试机制
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 尝试连接MCP服务器 (第 {attempt + 1}/{max_retries} 次)...")
                
                # 使用超时控制
                async with asyncio.timeout(15):  # 15 second total timeout
                    async with self.client:
                        tools_result = await self.client.list_tools()
                        
                        if hasattr(tools_result, 'tools'):
                            self.tools = tools_result.tools
                        elif isinstance(tools_result, list):
                            self.tools = tools_result
                        else:
                            print(f"⚠️ 意外的工具结果类型: {type(tools_result)}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)
                                continue
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
                        print(f"✅ 成功连接到MCP服务器并加载 {len(self.tools)} 个工具")
                        return True
                        
            except asyncio.TimeoutError:
                print(f"⏱️ 连接超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"⏳ 等待 {retry_delay} 秒后重试...")
                    await asyncio.sleep(retry_delay)
                else:
                    print("❌ 连接MCP服务器超时，已达最大重试次数")
                    
            except Exception as e:
                print(f"❌ 连接失败 (尝试 {attempt + 1}/{max_retries}): {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ 等待 {retry_delay} 秒后重试...")
                    await asyncio.sleep(retry_delay)
                else:
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
        
        start_time = time.time()
        try:
            async with self.client:
                response = await self.client.call_tool(tool_name, validated_params)
                duration = time.time() - start_time
                
                # 记录工具调用到Langfuse
                log_tool_call(
                    tool_name=tool_name,
                    parameters=validated_params,
                    result=response,
                    success=True,
                    duration=duration
                )
                
                return True, response, "调用成功"
        except Exception as e:
            duration = time.time() - start_time
            
            # 记录失败的工具调用
            log_tool_call(
                tool_name=tool_name,
                parameters=validated_params,
                result=None,
                success=False,
                duration=duration
            )
            
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
        if not tool_name or tool_name not in self.tool_schemas:
            print(f"❌ 工具 {tool_name} 不存在")
            return None
        
        tool_schema = self.tool_schemas[tool_name]
        validated_params = {}
        
        # 安全检查：确保 parameters 不为 None
        if parameters is None:
            parameters = {}
        
        # 检查必需参数
        tool_parameters = tool_schema.get('parameters', {})
        for param_name, param_info in tool_parameters.items():
            if param_info.get('required', False) and param_name not in parameters:
                print(f"❌ 缺少必需参数: {param_name}")
                return None
        
        # 过滤有效参数
        for param_name, param_value in parameters.items():
            if param_name in tool_parameters:
                # 确保参数值不为 None（如果工具不接受 None 值）
                if param_value is not None:
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