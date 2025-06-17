# LangGraph原生架构

## 概述
基于LangGraph官方SDK的原生实现，使用现代化的状态图工作流。

## 特性
- ✅ LangGraph StateGraph
- ✅ 官方MCP集成
- ✅ ToolNode支持
- ✅ 事件流处理
- 🚧 开发中功能

## 快速启动

### API服务器
```bash
python run.py --mode api --port 8001
```

### 测试模式
```bash
python run.py --mode test
```

## 当前状态
- 开发版本: 0.5.0
- 成功率: 71.43%
- 平均响应时间: 12.60秒

## 开发路线图
- [ ] 完善MCP工具集成
- [ ] 实现并行执行
- [ ] 多轮对话支持
- [ ] 性能优化

## 架构组件
- `api/fastapi_app.py` - FastAPI服务器
- `adapters/langgraph_native_mcp_adapter.py` - LangGraph适配器

## 依赖要求
- Python 3.11+
- LangGraph
- LangChain Core
- LangChain OpenAI
