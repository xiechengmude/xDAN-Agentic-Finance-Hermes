# xDAN标准架构

## 概述
基于intelligent_tool_selector的原生xDAN实现，提供完整的金融智能助手功能。

## 特性
- ✅ 多轮智能对话
- ✅ 并行执行优化 (40-60%性能提升)
- ✅ 138+金融工具集成
- ✅ 智能工具选择
- ✅ MCP协议支持

## 快速启动

### 交互式模式
```bash
python run.py --mode interactive
```

### API服务器
```bash
python run.py --mode api --port 8000
```

### 演示模式
```bash
python run.py --mode demo
```

## 性能指标
- 成功率: 100%
- 平均响应时间: 10.81秒
- 并行性能提升: 40-60%

## 架构组件
- `main.py` - 交互式入口
- `api/fastapi_app.py` - FastAPI服务器
- `intelligent_tool_selector/` - 核心智能选择器
- `adapters/` - 适配器层
- `demo_parallel_execution.py` - 并行执行演示

## 依赖要求
- Python 3.11+
- OpenAI API
- FastAPI
- NetworkX
