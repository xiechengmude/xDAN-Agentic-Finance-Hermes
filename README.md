# xDAN-Agentic-Search-Test

## 🏗️ LangGraph Native MCP架构

基于LangGraph原生MCP集成的智能金融助手，支持多轮对话、并行执行和智能工具调用。

### ✨ 核心特性

- 🧠 **LangGraph原生MCP集成**: 使用官方MCP SDK和LangGraph ToolNode
- 🔄 **多轮智能对话**: 支持复杂查询的智能分解和多轮执行
- ⚡ **并行执行优化**: 基于依赖分析的智能并行任务执行
- 🛠️ **138+金融工具**: 涵盖股票、基金、宏观经济等金融数据工具
- 🌐 **现代Web界面**: React + TypeScript + Tailwind CSS
- 🐳 **Docker容器化**: 完整的Docker Compose部署方案

### 🚀 快速开始

#### 本地开发

1. **克隆项目**
```bash
git clone https://github.com/xiechengmude/xDAN-Agentic-Finance-Hermes.git
cd xDAN-Agentic-Finance-Hermes
git checkout graph-web-v2
```

2. **环境配置**
```bash
cp .env.example .env
# 编辑 .env 文件配置模型和MCP服务器
```

3. **安装依赖**
```bash
# 后端依赖
pip install -r requirements.txt -r requirements-api.txt

# 前端依赖
cd frontend && npm install && cd ..
```

4. **启动服务**
```bash
# 后端 (端口 8000)
python api/fastapi_app_langgraph_native.py

# 前端 (端口 5173)
cd frontend && npm run dev
```

5. **访问应用**
- 前端界面: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

#### Docker部署

```bash
# 快速部署
cd deploy
docker-compose up -d

# 访问应用
open http://localhost
```

详细部署指南请参考: [deploy/README.md](deploy/README.md)

## 🧠 智能工具选择器系统

基于大语言模型的智能MCP工具选择系统，支持单轮和多轮工具调用，能够自动理解用户查询意图并选择最合适的工具。

### 🌟 核心特性

#### 单轮工具调用
- **🧠 智能理解**: 基于LLM的用户意图识别和分析
- **🎯 精准选择**: 从138+个MCP工具中智能选择最合适的工具
- **📊 自动映射**: 智能参数组装和验证机制

#### 多轮工具调用 ⭐ 新功能
- **🔄 任务规划**: 自动将复杂查询分解为可执行的子任务序列
- **🧩 智能分解**: 识别查询复杂度并决定是否需要多轮执行
- **🔗 上下文记忆**: 维护对话历史和执行上下文
- **📊 结果整合**: 智能整合多个工具的执行结果生成综合分析报告
- **⚡ 并行执行**: 自动分析任务依赖关系，支持无依赖任务并行执行 🆕

#### 🚀 并行执行优化 🆕
- **📈 依赖分析**: 基于图论的智能任务依赖关系分析
- **🔀 层级执行**: 自动识别可并行执行的任务层级
- **⚡ 性能提升**: 相比串行执行可提升40-60%的执行效率
- **🛡️ 智能回退**: 检测到循环依赖时自动回退到串行模式
- **🎛️ 并发控制**: 可配置最大并发任务数量避免系统过载

#### 通用特性
- **🔧 强容错性**: 多层次JSON解析和错误处理
- **⚡ 高性能**: 优化的工具加载和缓存机制
- **🛡️ 安全可靠**: 完整的参数验证和错误恢复
- **🔄 自动回退**: 复杂任务失败时自动回退到单轮模式

### 🚀 快速开始

#### 1. 交互式模式
```bash
# 主程序交互式模式（自动多轮）
python main.py

# 演示模式
python main.py demo

# 多轮专用演示
python main.py multi
```

#### 2. 使用示例
```bash
# 单轮基本使用示例
python intelligent_tool_selector/examples/basic_usage.py

# 多轮使用示例
python intelligent_tool_selector/examples/multi_turn_usage.py

# 运行测试套件
python intelligent_tool_selector/tests/test_selector.py
python intelligent_tool_selector/tests/test_multi_turn_selector.py
```

#### 3. 编程接口

**单轮工具调用**:
```python
from intelligent_tool_selector import IntelligentToolSelector

# 创建选择器
selector = IntelligentToolSelector()

# 初始化
await selector.initialize()

# 智能选择并执行工具
result = await selector.select_and_execute_tool("搜索平安银行的股票信息")
```

**多轮工具调用**:
```python
from intelligent_tool_selector import MultiTurnToolSelector

# 创建多轮选择器（支持并行执行）
multi_selector = MultiTurnToolSelector(
    enable_parallel=True,      # 启用并行执行
    max_concurrent_tasks=3     # 最大并发数
)

# 初始化
await multi_selector.initialize()

# 多轮智能执行（自动并行优化）
result = await multi_selector.multi_turn_execution(
    "分析比亚迪的投资价值，包括基本面、财务指标和技术分析"
)
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

#### 单轮查询（简单、直接）
- **股票基本信息**: "搜索平安银行的股票信息"
- **港股数据**: "获取腾讯控股的港股行情"
- **财务数据**: "查询贵州茅台的财务指标"
- **游资数据**: "查询龙虎榜数据"
- **模糊搜索**: "搜索所有银行类股票"

#### 多轮查询（复杂、综合） ⭐ 新功能
- **投资价值分析**: "分析比亚迪的投资价值，包括基本面、财务指标和技术分析"
- **股票对比分析**: "比较招商银行和平安银行的投资价值，给出详细对比"
- **板块龙头分析**: "查询新能源汽车板块的龙头股票并分析未来发展前景"
- **概念股分析**: "搜索游戏概念股票并分析其当前市场表现和投资机会"
- **综合研究报告**: "研究医药行业的投资机会，包括行业分析和个股推荐"

### ⚙️ 配置说明

系统默认配置：
- **模型服务器**: http://161.248.3.20:32790/v1
- **模型名称**: xDAN-Agent-Medium-v2-step300-0525
- **MCP服务器**: http://43.134.62.139:7223/sse

可通过环境变量或代码配置进行自定义。

### 📈 性能指标

基于测试套件的性能表现：

#### 单轮工具调用
| 指标 | 数值 |
|------|------|
| 工具选择成功率 | 100% |
| 工具执行成功率 | 80% |
| 平均响应时间 | 3-5秒 |
| 支持工具数量 | 138+ |
| JSON解析成功率 | 100% |

#### 多轮工具调用 ⭐ 新功能
| 指标 | 串行模式 | 并行模式 🆕 |
|------|---------|-----------|
| 任务规划成功率 | 85% | 85% |
| 多轮执行成功率 | 70% | 75% |
| 平均执行轮次 | 2-3轮 | 2-3轮 |
| 平均响应时间 | 20-30秒 | 10-15秒 |
| 性能提升 | - | 40-60% |
| 结果整合成功率 | 90% | 90% |
| 自动回退成功率 | 100% | 100% |
| 上下文记忆长度 | 10条 | 10条 |
