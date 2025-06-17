# xDAN Intelligent Agent System

An intelligent agent testing framework with MCP (Model Context Protocol) integration, featuring single-turn and multi-turn tool calling capabilities with parallel execution optimization.

## Table of Contents
- [Overview](#overview)
- [Core Features](#core-features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Performance Metrics](#performance-metrics)
- [Advanced Usage](#advanced-usage)

## Overview

This system provides an intelligent MCP tool selection framework that automatically understands user queries and selects the most appropriate tools from 138+ available options.

### Model Configuration
- **Model URL**: http://159.54.182.15:8003/v1 / http://161.248.3.20:32790/v1
- **Model Name**: xDAN-Agent-Medium-v2-step300-0525
- **MCP Server**: http://43.134.62.139:7223/sse
- **Deployment**: vLLM

## Core Features

### Single-Turn Tool Calling
- **Intelligent Understanding**: LLM-based user intent recognition and analysis
- **Precise Selection**: Smart tool selection from 138+ available MCP tools
- **Auto Parameter Mapping**: Intelligent parameter assembly and validation

### Multi-Turn Tool Calling ⭐
- **Task Planning**: Automatically decompose complex queries into executable sub-task sequences
- **Smart Decomposition**: Identify query complexity and decide whether multi-turn execution is needed
- **Context Memory**: Maintain conversation history and execution context
- **Result Integration**: Intelligently integrate multiple tool execution results into comprehensive analysis reports
- **Parallel Execution**: Analyze task dependencies and support parallel execution of independent tasks 🆕

### Parallel Execution Optimization 🆕
- **Dependency Analysis**: Graph theory-based intelligent task dependency analysis
- **Hierarchical Execution**: Automatically identify task levels that can be executed in parallel
- **Performance Improvement**: 40-60% efficiency improvement compared to serial execution
- **Smart Fallback**: Automatically fallback to serial mode when circular dependencies are detected
- **Concurrency Control**: Configurable maximum concurrent task count to avoid system overload

### General Features
- **Strong Fault Tolerance**: Multi-level JSON parsing and error handling
- **High Performance**: Optimized tool loading and caching mechanisms
- **Security & Reliability**: Complete parameter validation and error recovery
- **Auto Fallback**: Automatically fallback to single-turn mode when complex tasks fail

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Interactive Mode
```bash
# Main program (automatic multi-turn)
python main.py

# Demo mode
python main.py demo

# Multi-turn specific demo
python main.py multi

# Parallel execution demo
python main.py parallel
```

### Basic Usage Examples
```bash
# Single-turn basic usage
python intelligent_tool_selector/examples/basic_usage.py

# Multi-turn usage
python intelligent_tool_selector/examples/multi_turn_usage.py

# Run test suites
python intelligent_tool_selector/tests/test_selector.py
```

### Programming Interface

**Single-Turn Tool Calling**:
```python
from intelligent_tool_selector import IntelligentToolSelector

selector = IntelligentToolSelector()
await selector.initialize()
result = await selector.select_and_execute_tool("Search for Ping An Bank stock information")
```

**Multi-Turn Tool Calling**:
```python
from intelligent_tool_selector import MultiTurnToolSelector

multi_selector = MultiTurnToolSelector(
    enable_parallel=True,      # Enable parallel execution
    max_concurrent_tasks=3     # Maximum concurrent tasks
)
await multi_selector.initialize()
result = await multi_selector.multi_turn_execution(
    "Analyze BYD's investment value including fundamentals, financial metrics and technical analysis"
)
```

## Architecture

```
xDAN-Agentic-Search-Test/
├── intelligent_tool_selector/
│   ├── core/                    # Core modules
│   │   ├── selector.py         # Intelligent tool selector
│   │   ├── multi_turn_selector.py # Multi-turn tool selector  
│   │   ├── parallel_executor.py   # Parallel execution manager
│   │   └── json_parser.py      # JSON parser
│   ├── utils/                   # Utility modules
│   │   ├── config.py           # Configuration management
│   │   └── mcp_client.py       # MCP client manager
│   ├── examples/                # Usage examples
│   │   ├── basic_usage.py      # Basic usage example
│   │   ├── multi_turn_usage.py # Multi-turn usage example
│   │   └── parallel_demo.py    # Parallel execution demo
│   ├── tests/                   # Test modules
│   │   ├── test_selector.py    # Single-turn test suite
│   │   └── test_multi_turn_selector.py # Multi-turn test suite
│   └── docs/                    # Documentation
├── main.py                      # Main entry point
├── agent_client.py             # Legacy agent client
├── system_prompt.py            # System prompts
└── requirements.txt            # Dependencies
```

### Supported Query Types

#### Single-Turn Queries (Simple & Direct)
- **Stock Information**: "Search for Ping An Bank stock information"
- **Hong Kong Stocks**: "Get Tencent Holdings stock quotes"
- **Financial Data**: "Query Kweichow Moutai financial indicators"
- **Trading Data**: "Query dragon-tiger list data"
- **Fuzzy Search**: "Search all banking stocks"

#### Multi-Turn Queries (Complex & Comprehensive) ⭐
- **Investment Analysis**: "Analyze BYD's investment value including fundamentals, financial metrics and technical analysis"
- **Stock Comparison**: "Compare the investment value of China Merchants Bank and Ping An Bank with detailed comparison"
- **Sector Analysis**: "Query leading stocks in the new energy vehicle sector and analyze future prospects"
- **Concept Stock Analysis**: "Search gaming concept stocks and analyze current market performance and investment opportunities"
- **Research Reports**: "Research investment opportunities in the pharmaceutical industry including sector analysis and individual stock recommendations"

## Configuration

Default system configuration:
- **Model Server**: http://161.248.3.20:32790/v1
- **Model Name**: xDAN-Agent-Medium-v2-step300-0525
- **MCP Server**: http://43.134.62.139:7223/sse

Configuration can be customized through environment variables or code configuration.

## Performance Metrics

Performance based on test suite results:

### Single-Turn Tool Calling
| Metric | Value |
|--------|-------|
| Tool Selection Success Rate | 100% |
| Tool Execution Success Rate | 80% |
| Average Response Time | 3-5 seconds |
| Supported Tools Count | 138+ |
| JSON Parsing Success Rate | 100% |

### Multi-Turn Tool Calling ⭐
| Metric | Serial Mode | Parallel Mode 🆕 |
|--------|-------------|------------------|
| Task Planning Success Rate | 85% | 85% |
| Multi-turn Execution Success Rate | 70% | 75% |
| Average Execution Rounds | 2-3 rounds | 2-3 rounds |
| Average Response Time | 20-30 seconds | 10-15 seconds |
| Performance Improvement | - | 40-60% |
| Result Integration Success Rate | 90% | 90% |
| Auto Fallback Success Rate | 100% | 100% |
| Context Memory Length | 10 items | 10 items |

## Advanced Usage

### Legacy Agent Client
```python
from agent_client import xDANAgentClient

client = xDANAgentClient()
await client.setup_mcp_tools()
result = await client.process_user_query("Your query here")
```

### Test Cases
1. **Basic Interaction**: Simple greeting and capability assessment
2. **Complex Financial Query**: Multi-step financial analysis with tool integration
3. **Multi-turn Reasoning**: Context maintenance and error handling across iterations

### Development
```bash
# Run specific tests
python -m pytest intelligent_tool_selector/tests/

# Run with coverage
python -m pytest --cov=intelligent_tool_selector

# Performance benchmarks
python intelligent_tool_selector/benchmarks/performance_test.py
```
