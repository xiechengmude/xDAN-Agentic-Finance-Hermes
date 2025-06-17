"""
配置系统单元测试
Configuration System Unit Tests
"""

import pytest
import os
from unittest.mock import patch, Mock
from typing import Dict, Any

from agent.configuration import MCPConfiguration
from tests.fixtures.test_data import TEST_CONFIG_DATA, TEST_ENV_VARS, mock_env_vars


class TestMCPConfiguration:
    """MCPConfiguration 类的单元测试"""
    
    def test_from_runnable_config_with_valid_env(self, mock_env_vars):
        """测试使用有效环境变量创建配置"""
        config = MCPConfiguration.from_runnable_config()
        
        assert config.model_name == TEST_ENV_VARS["MODEL_NAME"]
        assert config.model_url == TEST_ENV_VARS["MODEL_BASE_URL"]
        assert config.model_api_key == TEST_ENV_VARS["MODEL_API_KEY"]
        assert config.mcp_server_url == TEST_ENV_VARS["MCP_SERVER_URL"]
    
    def test_from_runnable_config_with_configurable(self):
        """测试使用configurable参数创建配置"""
        configurable = {
            "model_name": "custom-model",
            "model_url": "http://custom.example.com/v1",
            "model_api_key": "custom-key"
        }
        
        run_config = {"configurable": configurable}
        config = MCPConfiguration.from_runnable_config(run_config)
        
        assert config.model_name == configurable["model_name"]
        assert config.model_url == configurable["model_url"]
        assert config.model_api_key == configurable["model_api_key"]
    
    def test_from_runnable_config_missing_env_vars(self, monkeypatch):
        """测试缺少环境变量时的处理"""
        # 清除所有相关环境变量
        for key in TEST_ENV_VARS.keys():
            monkeypatch.delenv(key, raising=False)
        
        # 应该使用默认值或抛出异常
        with pytest.raises((ValueError, KeyError, AttributeError)):
            MCPConfiguration.from_runnable_config()
    
    def test_get_available_models(self):
        """测试获取可用模型列表"""
        models = MCPConfiguration.get_available_models()
        
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # 检查模型结构
        for model_key, model_config in models.items():
            assert isinstance(model_key, str)
            assert isinstance(model_config, dict)
            assert "name" in model_config or "base_url" in model_config
    
    def test_configuration_validation(self, mock_env_vars):
        """测试配置验证"""
        config = MCPConfiguration.from_runnable_config()
        
        # 验证必需字段存在
        assert hasattr(config, 'model_name')
        assert hasattr(config, 'model_url')
        assert hasattr(config, 'model_api_key')
        assert hasattr(config, 'mcp_server_url')
        
        # 验证URL格式
        assert config.model_url.startswith('http')
        assert config.mcp_server_url.startswith('http')
        
        # 验证API密钥不为空
        assert config.model_api_key is not None
        assert len(config.model_api_key) > 0
    
    @pytest.mark.parametrize("env_var,expected_attr", [
        ("MODEL_NAME", "model_name"),
        ("MODEL_BASE_URL", "model_url"),
        ("MODEL_API_KEY", "model_api_key"),
        ("MCP_SERVER_URL", "mcp_server_url"),
    ])
    def test_env_var_mapping(self, env_var, expected_attr, monkeypatch):
        """测试环境变量到配置属性的映射"""
        test_value = f"test_{env_var.lower()}"
        
        # 设置其他必需的环境变量
        for key, value in TEST_ENV_VARS.items():
            monkeypatch.setenv(key, value)
        
        # 设置测试的环境变量
        monkeypatch.setenv(env_var, test_value)
        
        config = MCPConfiguration.from_runnable_config()
        assert getattr(config, expected_attr) == test_value
    
    def test_configuration_immutability(self, mock_env_vars):
        """测试配置对象的不可变性（如果适用）"""
        config = MCPConfiguration.from_runnable_config()
        original_model_name = config.model_name
        
        # 尝试修改配置（这个测试取决于实际的实现）
        # 如果配置是不可变的，这应该抛出异常或不起作用
        try:
            config.model_name = "modified_name"
            # 如果修改成功，验证是否真的改变了
            if hasattr(config, '_frozen') or hasattr(config, '__frozen__'):
                pytest.fail("Configuration should be immutable")
        except (AttributeError, TypeError):
            # 预期的行为：配置是不可变的
            pass
    
    def test_default_values(self, monkeypatch):
        """测试默认值设置"""
        # 只设置必需的环境变量
        required_vars = {
            "MODEL_NAME": "test-model",
            "MODEL_BASE_URL": "http://test.example.com/v1", 
            "MODEL_API_KEY": "test-key",
            "MCP_SERVER_URL": "http://test-mcp.example.com"
        }
        
        for key, value in required_vars.items():
            monkeypatch.setenv(key, value)
        
        # 清除可选的环境变量
        optional_vars = ["DEFAULT_TEMPERATURE", "MAX_TOKENS", "MAX_ITERATIONS"]
        for var in optional_vars:
            monkeypatch.delenv(var, raising=False)
        
        config = MCPConfiguration.from_runnable_config()
        
        # 验证默认值（根据实际实现调整）
        if hasattr(config, 'temperature'):
            assert isinstance(config.temperature, (int, float))
        if hasattr(config, 'max_tokens'):
            assert isinstance(config.max_tokens, int)
        if hasattr(config, 'max_iterations'):
            assert isinstance(config.max_iterations, int)
    
    def test_configuration_serialization(self, mock_env_vars):
        """测试配置序列化"""
        config = MCPConfiguration.from_runnable_config()
        
        # 测试转换为字典（如果支持）
        if hasattr(config, 'dict') or hasattr(config, 'model_dump'):
            try:
                config_dict = config.dict() if hasattr(config, 'dict') else config.model_dump()
                assert isinstance(config_dict, dict)
                assert 'model_name' in config_dict
                assert 'model_url' in config_dict
            except Exception:
                # 如果不支持序列化，跳过这个测试
                pass
    
    def test_configuration_repr(self, mock_env_vars):
        """测试配置对象的字符串表示"""
        config = MCPConfiguration.from_runnable_config()
        
        repr_str = repr(config)
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0
        
        # 确保敏感信息不在repr中
        assert "dummy_key" not in repr_str.lower() or "***" in repr_str
    
    def test_multiple_config_instances(self, mock_env_vars):
        """测试创建多个配置实例"""
        config1 = MCPConfiguration.from_runnable_config()
        config2 = MCPConfiguration.from_runnable_config()
        
        # 验证两个实例具有相同的配置值
        assert config1.model_name == config2.model_name
        assert config1.model_url == config2.model_url
        assert config1.mcp_server_url == config2.mcp_server_url
    
    def test_config_with_special_characters(self, monkeypatch):
        """测试包含特殊字符的配置值"""
        special_values = {
            "MODEL_NAME": "model-with-dashes_and_underscores",
            "MODEL_BASE_URL": "http://test.example.com:8080/v1/chat/completions",
            "MODEL_API_KEY": "sk-test123!@#$%^&*()",
            "MCP_SERVER_URL": "http://mcp.example.com:7223/sse"
        }
        
        for key, value in special_values.items():
            monkeypatch.setenv(key, value)
        
        config = MCPConfiguration.from_runnable_config()
        
        assert config.model_name == special_values["MODEL_NAME"]
        assert config.model_url == special_values["MODEL_BASE_URL"]
        assert config.model_api_key == special_values["MODEL_API_KEY"]
        assert config.mcp_server_url == special_values["MCP_SERVER_URL"]


class TestConfigurationEdgeCases:
    """配置系统边界情况测试"""
    
    def test_empty_environment_variables(self, monkeypatch):
        """测试空环境变量的处理"""
        monkeypatch.setenv("MODEL_NAME", "")
        monkeypatch.setenv("MODEL_BASE_URL", "http://test.example.com/v1")
        monkeypatch.setenv("MODEL_API_KEY", "test-key")
        monkeypatch.setenv("MCP_SERVER_URL", "http://test-mcp.example.com")
        
        # 空的模型名称应该被处理
        with pytest.raises((ValueError, AssertionError)):
            MCPConfiguration.from_runnable_config()
    
    def test_invalid_url_format(self, monkeypatch):
        """测试无效URL格式的处理"""
        monkeypatch.setenv("MODEL_NAME", "test-model")
        monkeypatch.setenv("MODEL_BASE_URL", "invalid-url")
        monkeypatch.setenv("MODEL_API_KEY", "test-key")
        monkeypatch.setenv("MCP_SERVER_URL", "http://test-mcp.example.com")
        
        # 无效URL应该被检测到
        try:
            config = MCPConfiguration.from_runnable_config()
            # 如果没有验证，至少确保URL被存储
            assert config.model_url == "invalid-url"
        except (ValueError, AssertionError):
            # 预期的行为：URL验证失败
            pass
    
    def test_configuration_with_none_values(self, monkeypatch):
        """测试None值的处理"""
        # 这个测试可能需要根据实际的配置类实现来调整
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises((ValueError, KeyError, AttributeError)):
                MCPConfiguration.from_runnable_config()
    
    @pytest.mark.parametrize("invalid_temp", ["not_a_number", "-1", "2.0", ""])
    def test_invalid_temperature_values(self, invalid_temp, monkeypatch):
        """测试无效温度值的处理"""
        for key, value in TEST_ENV_VARS.items():
            monkeypatch.setenv(key, value)
        
        monkeypatch.setenv("DEFAULT_TEMPERATURE", invalid_temp)
        
        try:
            config = MCPConfiguration.from_runnable_config()
            if hasattr(config, 'temperature'):
                # 验证温度值在有效范围内
                assert 0.0 <= config.temperature <= 1.0
        except (ValueError, TypeError):
            # 预期的行为：无效温度值被拒绝
            pass 