# xDAN-LangGraph Deployment Guide

## 🚀 Docker Compose部署指南

本指南提供了基于Docker Compose的完整部署方案，适用于开发和生产环境。

### 📋 系统要求

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0
- **内存**: >= 4GB
- **存储**: >= 10GB
- **网络**: 需要访问外部MCP服务器

### 🏗️ 架构概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Frontend      │    │    Backend      │
│   (Optional)    │────│   (React)       │────│  (FastAPI)      │
│   Port: 80      │    │   Port: 5173    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                               ┌─────────────────┐
                                               │  xDAN MCP       │
                                               │   Servers       │
                                               └─────────────────┘
```

## 🚀 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/xiechengmude/xDAN-Agentic-Finance-Hermes.git
cd xDAN-Agentic-Finance-Hermes
git checkout graph-web-v2
```

### 2. 环境配置

创建环境变量文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# 模型服务器配置
MODEL_BASE_URL=http://161.248.3.20:32790/v1
MODEL_NAME=xDAN-Agent-Medium-v2-step300-0525
MODEL_API_KEY=dummy_key

# MCP 服务器配置
MCP_SERVER_URL=http://43.134.62.139:7223/sse

# 系统配置
MAX_ITERATIONS=3
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=2048
LOG_LEVEL=INFO
ENABLE_DEBUG=false
```

### 3. 启动服务

#### 生产环境部署（包含Nginx）
```bash
cd deploy
docker-compose up -d
```

#### 开发环境部署（热重载支持）
```bash
cd deploy
docker-compose -f docker-compose.dev.yml up -d
```

#### 仅前后端服务
```bash
cd deploy
docker-compose up -d xdan-backend xdan-frontend
```

#### 开发模式（查看日志）
```bash
cd deploy
docker-compose up
# 或开发环境
docker-compose -f docker-compose.dev.yml up
```

### 4. 验证部署

#### 健康检查
```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端访问
curl http://localhost:5173/

# 通过Nginx访问（如果启用）
curl http://localhost/
```

#### 预期响应
```json
{
  "status": "healthy",
  "initialized": true,
  "tools_available": 3,
  "timestamp": "2025-06-17T18:00:00.000000",
  "architecture": "langgraph_native_mcp"
}
```

## 🔧 高级配置

### 环境变量说明

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `MODEL_BASE_URL` | LLM模型服务地址 | - | `http://161.248.3.20:32790/v1` |
| `MODEL_NAME` | 模型名称 | `gpt-4o-mini` | `xDAN-Agent-Medium-v2-step300-0525` |
| `MODEL_API_KEY` | API密钥 | `dummy_key` | `your-api-key` |
| `MCP_SERVER_URL` | MCP服务器地址 | - | `http://43.134.62.139:7223/sse` |
| `MAX_ITERATIONS` | 最大迭代次数 | `3` | `5` |
| `DEFAULT_TEMPERATURE` | 模型温度 | `0.7` | `0.1` |
| `MAX_TOKENS` | 最大令牌数 | `2048` | `4096` |
| `LOG_LEVEL` | 日志级别 | `INFO` | `DEBUG` |

### 自定义配置

#### 修改端口映射
```yaml
# docker-compose.yml
services:
  xdan-backend:
    ports:
      - "8080:8000"  # 自定义后端端口
  
  xdan-frontend:
    ports:
      - "3000:5173"  # 自定义前端端口
```

#### 数据持久化
```yaml
# docker-compose.yml
services:
  xdan-backend:
    volumes:
      - xdan-data:/app/data
      - ./logs:/app/logs
```

#### 内存限制
```yaml
# docker-compose.yml
services:
  xdan-backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## 🔍 监控与日志

### 查看服务状态
```bash
docker-compose ps
```

### 查看服务日志
```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f xdan-backend
docker-compose logs -f xdan-frontend
```

### 进入容器调试
```bash
# 进入后端容器
docker-compose exec xdan-backend bash

# 进入前端容器
docker-compose exec xdan-frontend sh
```

## 🔒 生产环境配置

### SSL/TLS配置

1. **生成SSL证书**
```bash
# 创建SSL目录
mkdir -p deploy/ssl

# 生成自签名证书（测试用）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout deploy/ssl/key.pem \
  -out deploy/ssl/cert.pem

# 或使用Let's Encrypt
certbot certonly --standalone -d your-domain.com
cp /etc/letsencrypt/live/your-domain.com/* deploy/ssl/
```

2. **启用HTTPS**
取消注释 `nginx.conf` 中的HTTPS服务器配置。

### 安全加固

#### 1. 网络安全
```yaml
# docker-compose.yml
networks:
  xdan-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### 2. 非root用户
所有Dockerfile已配置非root用户运行。

#### 3. 资源限制
```yaml
# docker-compose.yml
services:
  xdan-backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
    restart: unless-stopped
```

### 备份策略

#### 数据备份
```bash
# 备份数据卷
docker run --rm -v xdan-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/xdan-data-backup-$(date +%Y%m%d).tar.gz -C /data .

# 恢复数据
docker run --rm -v xdan-data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/xdan-data-backup-20250617.tar.gz -C /data
```

#### 配置备份
```bash
# 备份配置文件
tar czf xdan-config-backup-$(date +%Y%m%d).tar.gz .env deploy/
```

## 🔧 故障排除

### 常见问题

#### 1. 前端构建失败
```bash
# 错误：tsc: not found 或 Node版本不兼容
# 解决方案：使用开发环境配置
cd deploy
docker-compose -f docker-compose.dev.yml up -d

# 或强制重新构建
docker-compose build --no-cache xdan-frontend
```

#### 2. 后端启动失败
```bash
# 检查日志
docker-compose logs xdan-backend

# 常见原因：
# - 环境变量配置错误
# - MCP服务器连接失败
# - 模型服务不可用
# - Python路径问题

# 解决方案：检查环境变量配置
cat .env
```

#### 3. 前端无法访问后端
```bash
# 检查网络连接
docker-compose exec xdan-frontend curl http://xdan-backend:8000/health

# 检查端口映射
docker-compose ps

# 检查代理配置
docker-compose logs xdan-frontend
```

#### 4. 内存不足
```bash
# 查看资源使用
docker stats

# 增加内存限制或优化配置
```

#### 5. Node版本兼容性问题
```bash
# 如果遇到Node版本警告，可以：
# 1. 使用开发环境配置（推荐）
docker-compose -f docker-compose.dev.yml up -d

# 2. 或修改package.json移除版本限制
# 然后重新构建
docker-compose build --no-cache
```

### 性能优化

#### 1. 调整工作进程
```bash
# 在环境变量中设置
WORKERS=4
```

#### 2. 缓存配置
```bash
# Redis缓存（可选）
docker run -d --name redis --network xdan-network redis:alpine
```

#### 3. 负载均衡
```yaml
# docker-compose.yml
services:
  xdan-backend:
    deploy:
      replicas: 3
```

## 📊 健康检查

所有服务都配置了健康检查：

- **后端**: `GET /health`
- **前端**: `GET /`
- **检查间隔**: 30秒
- **超时时间**: 10秒
- **重试次数**: 3次

## 🆙 更新部署

### 更新代码
```bash
# 拉取最新代码
git pull origin graph-web-v2

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 滚动更新
```bash
# 单独更新后端
docker-compose up -d --no-deps xdan-backend

# 单独更新前端
docker-compose up -d --no-deps xdan-frontend
```

## 📞 支持

- **项目仓库**: https://github.com/xiechengmude/xDAN-Agentic-Finance-Hermes
- **分支**: graph-web-v2
- **架构**: LangGraph Native MCP
- **问题反馈**: 请在GitHub Issues中提交

---

🎉 **部署完成！访问 http://localhost 开始使用 xDAN-LangGraph 智能金融助手**