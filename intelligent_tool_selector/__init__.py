"""
智能工具选择器模块
Intelligent Tool Selector Module

这个模块提供了基于大语言模型的智能MCP工具选择功能，
能够自动从大量可用工具中选择最合适的工具来回答用户查询。

主要特性:
- 🧠 智能理解用户意图
- 🎯 从138+个MCP工具中精准选择
- 📊 智能参数组装和验证
- 🔧 多层次JSON解析
- 🛡️ 错误处理和容错机制
"""

try:
    from .core.selector import IntelligentToolSelector
    from .core.json_parser import JSONParser
    from .utils.mcp_client import MCPClientManager
    from .utils.config import Config
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from intelligent_tool_selector.core.selector import IntelligentToolSelector
    from intelligent_tool_selector.core.json_parser import JSONParser
    from intelligent_tool_selector.utils.mcp_client import MCPClientManager
    from intelligent_tool_selector.utils.config import Config

__version__ = "1.0.0"
__author__ = "xDAN-Agent Team"

__all__ = [
    "IntelligentToolSelector",
    "JSONParser", 
    "MCPClientManager",
    "Config"
] 