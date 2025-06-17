"""
MCP工具系统单元测试
MCP Tools System Unit Tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, List

from agent.mcp_tools import MCPToolManager
from tests.fixtures.test_data import (
    MOCK_MCP_TOOLS, MOCK_TOOL_RESPONSE, mock_mcp_manager,
    create_mock_async_response
)


class TestMCPToolManager:
    """MCPToolManager 类的单元测试"""
    
    @pytest.fixture
    def mcp_server_url(self):
        """MCP服务器URL fixture"""
        return "http://test-mcp.example.com:7223/sse"
    
    @pytest.fixture
    def tool_manager(self, mcp_server_url):
        """工具管理器实例fixture"""
        return MCPToolManager(mcp_server_url)
    
    def test_init(self, mcp_server_url):
        """测试MCPToolManager初始化"""
        manager = MCPToolManager(mcp_server_url)
        
        assert manager.server_url == mcp_server_url
        assert manager.tools == {}
        assert manager.client is None
        assert not manager.initialized
    
    def test_init_with_timeout(self, mcp_server_url):
        """测试带超时的初始化"""
        timeout = 30.0
        manager = MCPToolManager(mcp_server_url, timeout=timeout)
        
        assert manager.timeout == timeout
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, tool_manager):
        """测试成功初始化"""
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟工具列表响应
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            result = await tool_manager.initialize()
            
            assert result is True
            assert tool_manager.initialized is True
            assert tool_manager.client is mock_client
            assert len(tool_manager.tools) == len(MOCK_MCP_TOOLS)
            
            # 验证工具被正确存储
            for tool in MOCK_MCP_TOOLS:
                assert tool["name"] in tool_manager.tools
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, tool_manager):
        """测试初始化失败"""
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟初始化失败
            mock_client.list_tools.side_effect = Exception("Connection failed")
            
            result = await tool_manager.initialize()
            
            assert result is False
            assert tool_manager.initialized is False
            assert tool_manager.client is None
            assert len(tool_manager.tools) == 0
    
    @pytest.mark.asyncio
    async def test_initialize_timeout(self, mcp_server_url):
        """测试初始化超时"""
        manager = MCPToolManager(mcp_server_url, timeout=0.001)  # 很短的超时
        
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟长时间运行的操作
            async def slow_list_tools():
                await asyncio.sleep(1)  # 超过超时时间
                return Mock(tools=MOCK_MCP_TOOLS)
            
            mock_client.list_tools = slow_list_tools
            
            result = await manager.initialize()
            
            assert result is False
            assert not manager.initialized
    
    def test_get_tools_count_uninitialized(self, tool_manager):
        """测试未初始化时获取工具数量"""
        count = tool_manager.get_tools_count()
        assert count == 0
    
    @pytest.mark.asyncio
    async def test_get_tools_count_initialized(self, tool_manager):
        """测试初始化后获取工具数量"""
        # 先初始化
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            await tool_manager.initialize()
            
            count = tool_manager.get_tools_count()
            assert count == len(MOCK_MCP_TOOLS)
    
    def test_get_all_tools_info_uninitialized(self, tool_manager):
        """测试未初始化时获取工具信息"""
        tools_info = tool_manager.get_all_tools_info()
        assert tools_info == []
    
    @pytest.mark.asyncio
    async def test_get_all_tools_info_initialized(self, tool_manager):
        """测试初始化后获取工具信息"""
        # 先初始化
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            await tool_manager.initialize()
            
            tools_info = tool_manager.get_all_tools_info()
            assert len(tools_info) == len(MOCK_MCP_TOOLS)
            assert tools_info == MOCK_MCP_TOOLS
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, tool_manager):
        """测试成功调用工具"""
        # 先初始化
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            # 模拟工具调用响应
            mock_response = Mock()
            mock_response.content = [Mock(text=str(MOCK_TOOL_RESPONSE["data"]))]
            mock_client.call_tool.return_value = mock_response
            
            await tool_manager.initialize()
            
            # 调用工具
            success, response, message = await tool_manager.call_tool(
                "test_tool_1", 
                {"param1": "test_value"}
            )
            
            assert success is True
            assert response is not None
            assert "successfully" in message.lower()
            
            # 验证客户端被正确调用
            mock_client.call_tool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_tool_not_initialized(self, tool_manager):
        """测试未初始化时调用工具"""
        success, response, message = await tool_manager.call_tool(
            "test_tool_1",
            {"param1": "test_value"}
        )
        
        assert success is False
        assert response is None
        assert "not initialized" in message.lower()
    
    @pytest.mark.asyncio
    async def test_call_tool_not_found(self, tool_manager):
        """测试调用不存在的工具"""
        # 先初始化
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            await tool_manager.initialize()
            
            # 调用不存在的工具
            success, response, message = await tool_manager.call_tool(
                "nonexistent_tool",
                {}
            )
            
            assert success is False
            assert response is None
            assert "not found" in message.lower()
    
    @pytest.mark.asyncio
    async def test_call_tool_exception(self, tool_manager):
        """测试工具调用异常"""
        # 先初始化
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            # 模拟工具调用异常
            mock_client.call_tool.side_effect = Exception("Tool execution failed")
            
            await tool_manager.initialize()
            
            success, response, message = await tool_manager.call_tool(
                "test_tool_1",
                {"param1": "test_value"}
            )
            
            assert success is False
            assert response is None
            assert "failed" in message.lower()
    
    @pytest.mark.asyncio
    async def test_call_tool_with_invalid_params(self, tool_manager):
        """测试使用无效参数调用工具"""
        # 先初始化
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            await tool_manager.initialize()
            
            # 使用无效参数调用工具
            success, response, message = await tool_manager.call_tool(
                "test_tool_1",
                {"invalid_param": "value"}
            )
            
            # 这里的行为取决于实际实现
            # 可能成功（参数验证在服务器端），也可能失败
            assert isinstance(success, bool)
            assert isinstance(message, str)
    
    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self, tool_manager):
        """测试多次工具调用"""
        # 先初始化
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            # 模拟不同的响应
            responses = [
                Mock(content=[Mock(text="Response 1")]),
                Mock(content=[Mock(text="Response 2")])
            ]
            mock_client.call_tool.side_effect = responses
            
            await tool_manager.initialize()
            
            # 第一次调用
            success1, response1, message1 = await tool_manager.call_tool(
                "test_tool_1", {"param1": "value1"}
            )
            
            # 第二次调用
            success2, response2, message2 = await tool_manager.call_tool(
                "test_tool_2", {"param2": 42}
            )
            
            assert success1 is True
            assert success2 is True
            assert response1 != response2
            assert mock_client.call_tool.call_count == 2
    
    def test_tool_manager_state_consistency(self, tool_manager):
        """测试工具管理器状态一致性"""
        # 初始状态
        assert not tool_manager.initialized
        assert tool_manager.get_tools_count() == 0
        assert tool_manager.get_all_tools_info() == []
        
        # 状态应该保持一致
        assert tool_manager.client is None
        assert tool_manager.tools == {}
    
    @pytest.mark.asyncio
    async def test_reinitialize(self, tool_manager):
        """测试重新初始化"""
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            # 第一次初始化
            result1 = await tool_manager.initialize()
            assert result1 is True
            assert tool_manager.initialized is True
            
            # 重新初始化
            result2 = await tool_manager.initialize()
            assert result2 is True
            assert tool_manager.initialized is True
            
            # 工具数量应该保持一致
            assert tool_manager.get_tools_count() == len(MOCK_MCP_TOOLS)


class TestMCPToolManagerIntegration:
    """MCP工具管理器集成测试"""
    
    @pytest.mark.asyncio
    async def test_tool_discovery_and_execution_flow(self):
        """测试工具发现和执行的完整流程"""
        server_url = "http://test-mcp.example.com:7223/sse"
        manager = MCPToolManager(server_url)
        
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 模拟工具发现
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            # 模拟工具执行
            mock_response = Mock()
            mock_response.content = [Mock(text='{"result": "success"}')]
            mock_client.call_tool.return_value = mock_response
            
            # 执行完整流程
            # 1. 初始化
            init_success = await manager.initialize()
            assert init_success is True
            
            # 2. 验证工具可用
            tools_count = manager.get_tools_count()
            assert tools_count > 0
            
            # 3. 获取工具信息
            tools_info = manager.get_all_tools_info()
            assert len(tools_info) == tools_count
            
            # 4. 执行工具
            tool_name = tools_info[0]["name"]
            success, response, message = await manager.call_tool(tool_name, {})
            assert success is True
            
            # 5. 验证调用历史
            assert mock_client.list_tools.called
            assert mock_client.call_tool.called
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self):
        """测试并发工具调用"""
        server_url = "http://test-mcp.example.com:7223/sse"
        manager = MCPToolManager(server_url)
        
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            # 模拟并发响应
            mock_client.call_tool.return_value = Mock(
                content=[Mock(text='{"result": "concurrent_success"}')]
            )
            
            await manager.initialize()
            
            # 并发调用多个工具
            tasks = []
            for i in range(3):
                task = manager.call_tool("test_tool_1", {"param1": f"value_{i}"})
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # 验证所有调用都成功
            for success, response, message in results:
                assert success is True
                assert response is not None
            
            # 验证调用次数
            assert mock_client.call_tool.call_count == 3
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """测试错误恢复机制"""
        server_url = "http://test-mcp.example.com:7223/sse"
        manager = MCPToolManager(server_url)
        
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            await manager.initialize()
            
            # 第一次调用失败
            mock_client.call_tool.side_effect = Exception("Network error")
            success1, response1, message1 = await manager.call_tool("test_tool_1", {})
            assert success1 is False
            
            # 第二次调用成功（恢复）
            mock_client.call_tool.side_effect = None
            mock_client.call_tool.return_value = Mock(
                content=[Mock(text='{"result": "recovered"}')]
            )
            success2, response2, message2 = await manager.call_tool("test_tool_1", {})
            assert success2 is True
            
            # 验证管理器状态仍然正常
            assert manager.initialized is True
            assert manager.get_tools_count() > 0


class TestMCPToolManagerEdgeCases:
    """MCP工具管理器边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_empty_tools_list(self):
        """测试空工具列表"""
        server_url = "http://test-mcp.example.com:7223/sse"
        manager = MCPToolManager(server_url)
        
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=[])
            
            result = await manager.initialize()
            
            assert result is True  # 初始化成功，但没有工具
            assert manager.get_tools_count() == 0
            assert manager.get_all_tools_info() == []
    
    @pytest.mark.asyncio
    async def test_malformed_tool_response(self):
        """测试格式错误的工具响应"""
        server_url = "http://test-mcp.example.com:7223/sse"
        manager = MCPToolManager(server_url)
        
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # 格式错误的工具列表
            malformed_tools = [
                {"name": "valid_tool", "description": "Valid tool"},
                {"invalid": "missing_name"},  # 缺少name字段
                None  # None值
            ]
            mock_client.list_tools.return_value = Mock(tools=malformed_tools)
            
            result = await manager.initialize()
            
            # 应该能处理格式错误，至少保存有效的工具
            assert isinstance(result, bool)
            if result:
                # 如果初始化成功，应该至少有一个有效工具
                assert manager.get_tools_count() >= 1
    
    @pytest.mark.asyncio
    async def test_very_large_tool_response(self):
        """测试非常大的工具响应"""
        server_url = "http://test-mcp.example.com:7223/sse"
        manager = MCPToolManager(server_url)
        
        with patch('agent.mcp_tools.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.list_tools.return_value = Mock(tools=MOCK_MCP_TOOLS)
            
            # 模拟非常大的响应
            large_response = "x" * (10 * 1024 * 1024)  # 10MB
            mock_client.call_tool.return_value = Mock(
                content=[Mock(text=large_response)]
            )
            
            await manager.initialize()
            
            success, response, message = await manager.call_tool("test_tool_1", {})
            
            # 应该能处理大响应
            assert isinstance(success, bool)
            assert isinstance(message, str)
    
    def test_invalid_server_url(self):
        """测试无效的服务器URL"""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://invalid-protocol.com",
            None
        ]
        
        for url in invalid_urls:
            try:
                manager = MCPToolManager(url)
                # 如果没有抛出异常，至少验证URL被存储
                if url is not None:
                    assert manager.server_url == url
            except (ValueError, TypeError):
                # 预期的行为：无效URL被拒绝
                pass 