#!/usr/bin/env python3
"""
配置管理模块
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """模型配置"""
    base_url: str = "http://161.248.3.20:32790/v1"
    model_name: str = "xDAN-Agent-Medium-v2-step300-0525"
    api_key: str = "dummy_key"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 60

@dataclass
class MCPConfig:
    """MCP 服务器配置"""
    server_url: str = "http://43.134.62.139:7223/sse"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class AgentConfig:
    """智能体配置"""
    max_iterations: int = 3
    enable_debug: bool = False
    log_level: str = "INFO"
    tools_csv_path: str = "tools/xdan_finance_tools_info.csv"
    
    # 工具选择配置
    max_recommended_tools: int = 8
    confidence_threshold: float = 0.1
    
    # 响应格式配置
    enable_structured_output: bool = True
    include_execution_summary: bool = True

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.model = ModelConfig()
        self.mcp = MCPConfig()
        self.agent = AgentConfig()
        
        # 从环境变量加载配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        
        # 模型配置
        if os.getenv("MODEL_BASE_URL"):
            self.model.base_url = os.getenv("MODEL_BASE_URL")
        if os.getenv("MODEL_NAME"):
            self.model.model_name = os.getenv("MODEL_NAME")
        if os.getenv("MODEL_API_KEY"):
            self.model.api_key = os.getenv("MODEL_API_KEY")
        if os.getenv("DEFAULT_TEMPERATURE"):
            self.model.temperature = float(os.getenv("DEFAULT_TEMPERATURE"))
        if os.getenv("MAX_TOKENS"):
            self.model.max_tokens = int(os.getenv("MAX_TOKENS"))
        
        # MCP 配置
        if os.getenv("MCP_SERVER_URL"):
            self.mcp.server_url = os.getenv("MCP_SERVER_URL")
        
        # 智能体配置
        if os.getenv("MAX_ITERATIONS"):
            self.agent.max_iterations = int(os.getenv("MAX_ITERATIONS"))
        if os.getenv("ENABLE_DEBUG"):
            self.agent.enable_debug = os.getenv("ENABLE_DEBUG").lower() == "true"
        if os.getenv("LOG_LEVEL"):
            self.agent.log_level = os.getenv("LOG_LEVEL")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "model": {
                "base_url": self.model.base_url,
                "model_name": self.model.model_name,
                "temperature": self.model.temperature,
                "max_tokens": self.model.max_tokens
            },
            "mcp": {
                "server_url": self.mcp.server_url,
                "timeout": self.mcp.timeout
            },
            "agent": {
                "max_iterations": self.agent.max_iterations,
                "enable_debug": self.agent.enable_debug,
                "max_recommended_tools": self.agent.max_recommended_tools
            }
        }
    
    def print_config(self):
        """打印当前配置"""
        print("🔧 当前配置:")
        print(f"  模型服务器: {self.model.base_url}")
        print(f"  模型名称: {self.model.model_name}")
        print(f"  MCP服务器: {self.mcp.server_url}")
        print(f"  最大迭代次数: {self.agent.max_iterations}")
        print(f"  调试模式: {self.agent.enable_debug}")

# 全局配置实例
config = ConfigManager()
