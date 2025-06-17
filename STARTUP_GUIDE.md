# xDAN金融智能体启动脚本使用指南

## 📋 脚本概览

项目提供了两个启动脚本，满足不同的使用需求：

### 1. 完整版脚本 (`start_services.sh`)
功能最全面的服务管理脚本，包含：
- ✅ 进程管理 (启动/停止/重启)
- ✅ 代理清理
- ✅ 健康检查
- ✅ 日志管理
- ✅ 状态监控

### 2. 快速版脚本 (`quick_start.sh`)
简化版一键启动脚本，适合快速测试：
- ✅ 一键启动
- ✅ 代理清理
- ✅ 进程清理

## 🚀 使用方法

### 完整版脚本使用

```bash
# 启动所有服务 (默认)
./start_services.sh
# 或者
./start_services.sh start

# 停止所有服务
./start_services.sh stop

# 重启所有服务
./start_services.sh restart

# 检查服务状态
./start_services.sh status

# 查看日志
./start_services.sh logs

# 显示帮助
./start_services.sh help
```

### 快速版脚本使用

```bash
# 一键启动
./quick_start.sh

# 停止服务
pkill -f 'langgraph dev'; pkill -f 'node.*vite'
```

## 🔧 脚本功能详解

### 自动处理的问题

1. **代理设置清理**
   - 自动清除 `HTTP_PROXY`, `HTTPS_PROXY`, `http_proxy`, `https_proxy`
   - 设置 `NO_PROXY="localhost,127.0.0.1"`
   - 解决阻塞调用问题

2. **进程管理**
   - 自动杀死现有的 LangGraph 进程
   - 自动杀死现有的 Vite/npm 进程
   - 释放端口占用 (8123, 5173)

3. **服务启动**
   - 后端: LangGraph 服务在 8123 端口
   - 前端: Vite 服务在 5173 端口
   - 自动等待服务就绪

4. **健康检查**
   - 检查服务是否正常启动
   - 验证 API 端点可访问性

### 日志管理 (仅完整版)

脚本会在 `logs/` 目录下创建日志文件：
- `logs/backend.log` - 后端服务日志
- `logs/frontend.log` - 前端服务日志

查看实时日志：
```bash
# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
tail -f logs/frontend.log
```

## 🎯 启动后的服务

启动成功后，你可以访问：

### 前端界面
- **URL**: http://localhost:5173
- **功能**: 金融智能体对话界面
- **测试查询**: "请帮我查询平安银行的基本信息"

### 后端API
- **URL**: http://localhost:8123
- **健康检查**: http://localhost:8123/health
- **API文档**: http://localhost:8123/docs

### LangGraph Studio
- **URL**: https://smith.langchain.com/studio/?baseUrl=http://localhost:8123
- **功能**: 可视化调试和监控

## 🛠️ 故障排除

### 常见问题

1. **端口占用**
   ```bash
   # 检查端口占用
   lsof -ti:8123
   lsof -ti:5173
   
   # 杀死占用进程
   lsof -ti:8123 | xargs kill -9
   lsof -ti:5173 | xargs kill -9
   ```

2. **代理问题**
   ```bash
   # 手动清理代理
   unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy
   export NO_PROXY="localhost,127.0.0.1"
   ```

3. **虚拟环境问题**
   ```bash
   # 重新创建后端虚拟环境
   cd langraph-stack/backend
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **前端依赖问题**
   ```bash
   # 重新安装前端依赖
   cd langraph-stack/frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### 日志调试

如果服务启动失败，检查日志：

```bash
# 查看启动错误
./start_services.sh logs

# 或者直接查看日志文件
cat logs/backend.log
cat logs/frontend.log
```

## 🎉 快速开始

最简单的启动方式：

```bash
# 克隆或进入项目目录
cd xDAN-Agentic-Search-Test

# 一键启动 (推荐使用完整版)
./start_services.sh

# 或者快速启动
./quick_start.sh

# 打开浏览器访问
open http://localhost:5173
```

## 📝 注意事项

1. **运行目录**: 必须在项目根目录运行脚本
2. **权限**: 脚本已设置执行权限，如果没有请运行 `chmod +x *.sh`
3. **依赖**: 确保已安装 Python、Node.js 和相关依赖
4. **代理**: 如果系统设置了代理，脚本会自动清理
5. **端口**: 确保 8123 和 5173 端口未被其他程序占用

## 🔄 服务管理命令总结

| 命令 | 功能 | 脚本 |
|------|------|------|
| `./start_services.sh` | 启动所有服务 | 完整版 |
| `./start_services.sh stop` | 停止所有服务 | 完整版 |
| `./start_services.sh restart` | 重启所有服务 | 完整版 |
| `./start_services.sh status` | 检查服务状态 | 完整版 |
| `./start_services.sh logs` | 查看日志 | 完整版 |
| `./quick_start.sh` | 快速启动 | 快速版 |

现在你可以轻松管理 xDAN 金融智能体服务了！🎊 