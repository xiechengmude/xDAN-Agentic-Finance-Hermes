"""
配置管理模块
Configuration Management Module
"""

from typing import Dict, Any
import os


class Config:
    """配置管理类"""
    
    # MCP服务器配置
    MCP_SERVER_URL = "http://43.134.62.139:7223/sse"
    
    # 模型服务器配置
    MODEL_URL = "http://185.151.171.36:47683/v1"
    MODEL_NAME = "xDAN-Agent-Medium-v2-step300-0525"
    MODEL_API_KEY = "dummy-key"
    
    # 模型参数
    MODEL_TEMPERATURE = 0.1
    MODEL_MAX_TOKENS = 2000
    
    # MCP客户端配置
    MCP_HEADERS = {
        'User-Agent': 'Intelligent-Tool-Selector/1.0',
        'Accept': 'application/json, text/event-stream',
        'Content-Type': 'application/json'
    }
    
    # 超时配置
    REQUEST_TIMEOUT = 30
    TOOL_CALL_TIMEOUT = 60
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """从环境变量加载配置"""
        return {
            'mcp_server_url': os.getenv('MCP_SERVER_URL', cls.MCP_SERVER_URL),
            'model_url': os.getenv('MODEL_URL', cls.MODEL_URL),
            'model_name': os.getenv('MODEL_NAME', cls.MODEL_NAME),
            'model_api_key': os.getenv('MODEL_API_KEY', cls.MODEL_API_KEY),
            'model_temperature': float(os.getenv('MODEL_TEMPERATURE', cls.MODEL_TEMPERATURE)),
            'model_max_tokens': int(os.getenv('MODEL_MAX_TOKENS', cls.MODEL_MAX_TOKENS)),
            'request_timeout': int(os.getenv('REQUEST_TIMEOUT', cls.REQUEST_TIMEOUT)),
            'tool_call_timeout': int(os.getenv('TOOL_CALL_TIMEOUT', cls.TOOL_CALL_TIMEOUT)),
            'max_retries': int(os.getenv('MAX_RETRIES', cls.MAX_RETRIES)),
            'retry_delay': float(os.getenv('RETRY_DELAY', cls.RETRY_DELAY))
        }
    
    @classmethod
    def get_mcp_headers(cls) -> Dict[str, str]:
        """获取MCP客户端请求头"""
        return cls.MCP_HEADERS.copy()
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> bool:
        """验证配置参数"""
        required_keys = [
            'mcp_server_url', 'model_url', 'model_name', 
            'model_temperature', 'model_max_tokens'
        ]
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"缺少必需的配置参数: {key}")
        
        # 验证参数范围
        if not 0 <= config['model_temperature'] <= 2:
            raise ValueError("model_temperature 必须在 0-2 之间")
        
        if config['model_max_tokens'] <= 0:
            raise ValueError("model_max_tokens 必须大于 0")
        
        return True 