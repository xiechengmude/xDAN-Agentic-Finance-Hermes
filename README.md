# xDAN-Agentic-Search-Test

A testing framework for xDAN-Agent-Medium-v2-step300-0525 with agentic capabilities and tool calling through FastMCP.

## Overview

This project tests an intelligent agent system that can:
- Perform intent recognition and task planning
- Execute multi-turn reasoning with tool integration
- Handle complex queries like financial analysis
- Integrate with MCP (Model Context Protocol) servers for tool calling

## Model Configuration

- **Model URL**: http://159.54.182.15:8003/v1
- **Model Name**: xDAN-Agent-Medium-v2-step300-0525
- **Deployment**: vLLM

## Project Structure

```
xDAN-Agentic-Search-Test/
├── README.md
├── requirements.txt
├── system_prompt.py      # System prompts for the agent
├── agent_client.py       # Main client for testing
└── test_results/         # Test outputs and analysis
```

## Features

### System Prompts
- **Full System Prompt**: Comprehensive instructions for complex reasoning
- **Compact System Prompt**: Optimized for smaller models with essential instructions

### Agent Capabilities
- Intent analysis and task decomposition
- Multi-step reasoning with tool integration
- Financial data analysis and stock research
- Web search and information gathering

### Tool Integration
- Web search tools
- Stock market data retrieval
- Sector performance analysis
- Extensible MCP server integration

## Installation

```bash
cd /Users/gump_m2/CascadeProjects/xDAN-Agentic-Search-Test
pip install -r requirements.txt
```

## Usage

### Basic Testing
```bash
python agent_client.py
```

### Custom Query Testing
```python
from agent_client import xDANAgentClient

client = xDANAgentClient()
await client.setup_mcp_tools()
result = await client.process_user_query("Your query here")
print(result)
```

## Test Cases

### 1. Basic Interaction
- Simple greeting and capability introduction
- Model response quality assessment

### 2. Complex Financial Query
**Query**: "帮我查询上周涨幅最大的板块股票是哪些然后逐个分析股票强度和未来的龙头股是什么?"

**Expected Behavior**:
1. Intent recognition: Financial analysis request
2. Task planning: Sector analysis → Stock identification → Individual analysis
3. Tool calling: Sector performance analysis, stock data retrieval
4. Synthesis: Comprehensive report with recommendations

### 3. Multi-turn Reasoning
- Complex queries requiring multiple tool calls
- Context maintenance across iterations
- Error handling and recovery

## System Prompt Optimization

The system prompts are designed to:
- Provide clear structure for small model reasoning
- Enable effective tool calling with proper parameter handling
- Maintain context across multi-turn conversations
- Generate actionable insights and recommendations

## Next Steps

1. **Integration Testing**: Connect to actual MCP servers
2. **Performance Optimization**: Fine-tune prompts based on model responses
3. **Error Handling**: Improve robustness for edge cases
4. **Evaluation Metrics**: Implement automated testing and scoring

## 🧠 智能工具选择器系统

基于大语言模型的智能MCP工具选择系统，能够自动理解用户查询意图并选择最合适的工具。

### 🌟 核心特性

- **🧠 智能理解**: 基于LLM的用户意图识别和分析
- **🎯 精准选择**: 从138+个MCP工具中智能选择最合适的工具
- **📊 自动映射**: 智能参数组装和验证机制
- **🔧 强容错性**: 多层次JSON解析和错误处理
- **⚡ 高性能**: 优化的工具加载和缓存机制
- **🛡️ 安全可靠**: 完整的参数验证和错误恢复

### 🚀 快速开始

#### 1. 交互式模式
```bash
# 主程序交互式模式
python main.py

# 演示模式
python main.py demo
```

#### 2. 使用示例
```bash
# 基本使用示例
python intelligent_tool_selector/examples/basic_usage.py

# 运行测试套件
python intelligent_tool_selector/tests/test_selector.py
```

#### 3. 编程接口
```python
from intelligent_tool_selector import IntelligentToolSelector

# 创建选择器
selector = IntelligentToolSelector()

# 初始化
await selector.initialize()

# 智能选择并执行工具
result = await selector.select_and_execute_tool("搜索平安银行的股票信息")
```

### 📁 系统架构

```
intelligent_tool_selector/
├── core/                    # 核心模块
│   ├── selector.py         # 智能工具选择器
│   └── json_parser.py      # JSON解析器
├── utils/                   # 工具模块
│   ├── config.py           # 配置管理
│   └── mcp_client.py       # MCP客户端管理器
├── examples/                # 使用示例
│   └── basic_usage.py      # 基本使用示例
├── tests/                   # 测试模块
│   └── test_selector.py    # 测试套件
└── docs/                    # 文档
    └── README.md           # 项目文档
```

### 🎯 支持的查询类型

- **股票基本信息**: "搜索平安银行的股票信息"
- **港股数据**: "获取腾讯控股的港股行情"
- **财务数据**: "查询贵州茅台的财务指标"
- **游资数据**: "查询龙虎榜数据"
- **模糊搜索**: "搜索所有银行类股票"
- **技术分析**: "生成腾讯股价走势图"

### ⚙️ 配置说明

系统默认配置：
- **模型服务器**: http://161.248.3.20:32790/v1
- **模型名称**: xDAN-Agent-Medium-v2-step300-0525
- **MCP服务器**: http://43.134.62.139:7223/sse

可通过环境变量或代码配置进行自定义。

### 📈 性能指标

基于测试套件的性能表现：

| 指标 | 数值 |
|------|------|
| 工具选择成功率 | 100% |
| 工具执行成功率 | 80% |
| 平均响应时间 | 3-5秒 |
| 支持工具数量 | 138+ |
| JSON解析成功率 | 100% |
