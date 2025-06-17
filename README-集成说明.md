# xDAN-LangGraph 集成使用说明

## 🚀 快速启动

### 一键启动全栈应用
```bash
# 启动前后端服务
./start_fullstack.sh

# 或者分别启动
python start_backend.py    # 后端 (端口 8000)
./start_frontend.sh        # 前端 (端口 5173)
```

### 访问地址
- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## 📋 环境要求

### 系统要求
- **Python**: 3.10+ 
- **Node.js**: 16.0+
- **npm**: 8.0+

### Python 依赖安装
```bash
# 安装API依赖
pip install -r requirements-api.txt

# 或者安装现有项目依赖
pip install -r requirements.txt
```

### 前端依赖安装
```bash
cd frontend
npm install
```

---

## 🏗️ 架构说明

### 核心组件
```
xDAN-LangGraph集成/
├── adapters/                    # 适配器层
│   ├── xdan_langgraph_adapter.py  # 核心适配器
│   └── event_mapper.py            # 事件转换器
├── api/                         # FastAPI接口层
│   └── fastapi_app.py             # Web服务
├── frontend/                    # React前端
│   └── src/App.tsx                # 主应用组件
└── intelligent_tool_selector/   # xDAN后端核心
```

### 数据流
```
前端UI → FastAPI → 适配器 → xDAN后端 → MCP工具 → 数据返回
```

---

## 🔧 配置说明

### 环境变量 (.env 文件)
```bash
# MCP服务器配置
MCP_SERVER_URL=http://43.134.62.139:7223/sse

# 模型服务配置  
MODEL_URL=http://161.248.3.20:32790/v1
MODEL_NAME=xDAN-Agent-Medium-v2-step300-0525
MODEL_API_KEY=dummy-key

# API服务配置
API_HOST=0.0.0.0
API_PORT=8000
```

### 前端配置修改
主要修改在 `frontend/src/App.tsx`:
```typescript
// API地址配置
apiUrl: "http://localhost:8000"
assistantId: "xdan-agent"

// 事件处理已适配xDAN格式
```

---

## 📡 API接口

### 核心端点
```bash
# 健康检查
GET /health

# 创建线程
POST /assistants/{assistant_id}/threads

# 流式执行 (兼容LangGraph SDK)
POST /assistants/{assistant_id}/threads/{thread_id}/runs/stream

# WebSocket流式接口
WS /ws/stream

# 工具信息
GET /tools/count
GET /tools/list
```

### 流式执行示例
```bash
curl -X POST "http://localhost:8000/assistants/xdan-agent/threads/test/runs/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"type": "human", "content": "查询平安银行股票信息"}],
    "initial_search_query_count": 3,
    "max_research_loops": 5,
    "reasoning_model": "xDAN-Agent-Medium-v2-step300-0525"
  }'
```

---

## 🎯 使用示例

### 支持的查询类型
```
✅ 简单查询: "查询平安银行股票信息"
✅ 复杂分析: "分析比亚迪的投资价值，包括基本面和技术面"  
✅ 对比分析: "比较腾讯和阿里巴巴的投资潜力"
✅ 板块分析: "查询新能源板块龙头股并分析前景"
```

### 前端功能
- 🧠 **智能分析**: 自动工具选择和任务规划
- 🔧 **工具执行**: 实时显示数据获取过程
- 🤔 **结果分析**: 智能整合多数据源
- 📊 **最终报告**: 生成专业分析报告

---

## 🔍 故障排除

### 后端启动问题
```bash
# 检查Python依赖
python -c "import fastapi, uvicorn, openai"

# 检查MCP连接
curl http://43.134.62.139:7223/sse

# 查看详细日志
python start_backend.py --log-level debug
```

### 前端启动问题
```bash
# 清理并重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
npm install

# 检查端口占用
lsof -i :5173
```

### 常见错误

**1. CORS错误**
- 确保后端CORS配置正确
- 检查前端API URL配置

**2. 连接超时**
- 检查MCP服务器是否可访问
- 验证模型服务器连接

**3. 事件格式错误**
- 检查适配器事件转换逻辑
- 查看浏览器控制台错误信息

---

## 📈 性能优化

### 后端优化
- **并行执行**: 启用任务依赖分析和并行优化
- **连接池**: 复用MCP和模型服务连接
- **缓存**: 工具定义和常用结果缓存

### 前端优化
- **懒加载**: 按需加载组件
- **防抖**: 输入防抖减少请求
- **虚拟滚动**: 长列表性能优化

---

## 🛠️ 开发说明

### 扩展新功能
1. **添加新工具**: 在MCP服务器注册新工具
2. **修改事件映射**: 更新 `event_mapper.py`
3. **调整UI**: 修改前端组件和样式
4. **API扩展**: 在 `fastapi_app.py` 添加端点

### 调试技巧
```bash
# 后端调试模式
python start_backend.py --reload --log-level debug

# 前端开发模式
cd frontend && npm run dev

# 查看API调用
curl -v http://localhost:8000/health
```

---

## 📚 相关文档

- [xDAN后端架构分析](./xDAN-后端架构分析与gstack前端对接方案.md)
- [GStack项目分析](./gstack-langgraph-项目分析.md)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [React官方文档](https://react.dev/)

---

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交改动
4. 推送到分支
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。