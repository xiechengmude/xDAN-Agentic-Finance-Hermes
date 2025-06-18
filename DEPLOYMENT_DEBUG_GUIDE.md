# xDAN 项目部署与本地调试指南

> **📅 更新时间**: 2025-06-17  
> **🏗️ 架构版本**: v2.0 (双架构分离版)  
> **🎯 适用范围**: 本地开发、测试部署、生产环境

## 🚀 快速开始

### 1. 环境安装

#### 🐍 Python 环境安装

**macOS:**
```bash
# 方式1: 使用 Homebrew (推荐)
brew install python@3.11
brew install pip

# 方式2: 使用 pyenv (版本管理)
brew install pyenv
pyenv install 3.11.0
pyenv global 3.11.0

# 验证安装
python3 --version  # 应显示 3.11.x
pip3 --version
```

**Windows:**
```bash
# 方式1: 官网下载安装包
# 访问 https://www.python.org/downloads/
# 下载 Python 3.11.x 安装包，记得勾选 "Add to PATH"

# 方式2: 使用 Chocolatey
choco install python311

# 验证安装
python --version
pip --version
```

**Linux (Ubuntu/Debian):**
```bash
# 更新包列表
sudo apt update

# 安装 Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv

# 设置默认版本
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# 验证安装
python3 --version
pip3 --version
```

#### 📦 Node.js 环境安装

**macOS:**
```bash
# 方式1: 使用 Homebrew (推荐)
brew install node@18
brew install npm

# 方式2: 使用 nvm (版本管理)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.zshrc  # 或 ~/.bash_profile
nvm install 18
nvm use 18
nvm alias default 18

# 验证安装
node --version  # 应显示 v18.x.x
npm --version
```

**Windows:**
```bash
# 方式1: 官网下载安装包
# 访问 https://nodejs.org/
# 下载 LTS 版本 (18.x) 安装包

# 方式2: 使用 Chocolatey
choco install nodejs

# 方式3: 使用 nvm-windows
# 下载 nvm-windows: https://github.com/coreybutler/nvm-windows
nvm install 18.17.0
nvm use 18.17.0

# 验证安装
node --version
npm --version
```

**Linux (Ubuntu/Debian):**
```bash
# 方式1: 使用 NodeSource 仓库 (推荐)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 方式2: 使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# 验证安装
node --version
npm --version
```

#### 🛠️ 系统工具安装

**macOS:**
```bash
# 安装 Xcode Command Line Tools (包含 git, curl)
xcode-select --install

# 使用 Homebrew 安装额外工具
brew install git curl wget jq

# 验证安装
git --version
curl --version
```

**Windows:**
```bash
# 安装 Git
# 下载: https://git-scm.com/download/win

# 安装 curl (Windows 10+ 自带)
curl --version

# 使用 Chocolatey 安装工具
choco install git curl wget jq
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install git curl wget jq build-essential

# CentOS/RHEL
sudo yum install git curl wget jq gcc gcc-c++ make

# 验证安装
git --version
curl --version
```

### 2. 项目依赖安装

#### 🔧 后端依赖安装

```bash
# 1. 克隆项目
git clone https://github.com/xiechengmude/xDAN-Agentic-Finance-Hermes.git
cd xDAN-Agentic-Search-Test

# 2. 创建虚拟环境 (推荐)
python3 -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 3. 升级 pip
pip install --upgrade pip

# 4. 安装核心依赖
pip install fastapi uvicorn pydantic

# 5. 安装完整依赖 (如果有 requirements.txt)
pip install -r requirements.txt

# 6. 验证安装
python -c "import fastapi, uvicorn; print('✅ 后端依赖安装成功')"
```

#### 🎨 前端依赖安装

```bash
# 1. 进入前端目录 (根据实际情况选择)
cd gstack-langgraph/frontend
# 或
cd frontend

# 2. 安装依赖
npm install
# 或使用 yarn
yarn install

# 3. 验证安装
npm list --depth=0
npm run --silent build > /dev/null && echo "✅ 前端依赖安装成功"
```

### 3. 环境要求总结

| 组件 | 最低版本 | 推荐版本 | 验证命令 |
|------|----------|----------|----------|
| **Python** | 3.8+ | 3.11 | `python3 --version` |
| **pip** | 21.0+ | 最新 | `pip3 --version` |
| **Node.js** | 16.0+ | 18.17+ | `node --version` |
| **npm** | 8.0+ | 9.0+ | `npm --version` |
| **Git** | 2.20+ | 最新 | `git --version` |
| **curl** | 7.68+ | 最新 | `curl --version` |

### 4. 环境检查脚本

创建一个快速检查脚本来验证所有环境是否正确安装：

```bash
#!/bin/bash
# 环境检查脚本 - check_environment.sh

echo "🔍 xDAN 项目环境检查"
echo "========================="

# 检查函数
check_command() {
    local cmd=$1
    local name=$2
    local required_version=$3
    
    if command -v $cmd &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -1)
        echo "✅ $name: $version"
        return 0
    else
        echo "❌ $name: 未安装 (需要 $required_version+)"
        return 1
    fi
}

# 检查 Python
echo "🐍 Python 环境检查:"
check_command "python3" "Python3" "3.8"
check_command "pip3" "pip3" "21.0"

# 检查 Node.js
echo ""
echo "📦 Node.js 环境检查:"
check_command "node" "Node.js" "16.0"
check_command "npm" "npm" "8.0"

# 检查系统工具
echo ""
echo "🛠️ 系统工具检查:"
check_command "git" "Git" "2.20"
check_command "curl" "curl" "7.68"

# 检查 Python 包
echo ""
echo "📚 Python 包检查:"
python3 -c "
import sys
packages = ['fastapi', 'uvicorn', 'pydantic']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}: 已安装')
    except ImportError:
        print(f'❌ {pkg}: 未安装')
"

# 检查端口可用性
echo ""
echo "🌐 端口可用性检查:"
ports=(8000 8001 8003 5173)
for port in "${ports[@]}"; do
    if lsof -i :$port &> /dev/null; then
        echo "⚠️  端口 $port: 已被占用"
    else
        echo "✅ 端口 $port: 可用"
    fi
done

echo ""
echo "🎯 快速修复命令:"
echo "# 安装 Python 依赖:"
echo "pip3 install fastapi uvicorn pydantic"
echo ""
echo "# 如果端口被占用，终止进程:"
echo "lsof -ti:8003 | xargs kill -9"
echo ""
echo "========================="
echo "✅ 环境检查完成"
```

**使用方法：**
```bash
# 1. 创建检查脚本
cat > check_environment.sh << 'EOF'
[上面的脚本内容]
EOF

# 2. 赋予执行权限
chmod +x check_environment.sh

# 3. 运行检查
./check_environment.sh
```

### 5. 完整安装示例

以下是一个完整的从零开始安装示例（以 macOS 为例）：

```bash
# ========================================
# 完整安装流程示例 (macOS)
# ========================================

# 1. 安装 Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装基础环境
brew install python@3.11 node@18 git curl

# 3. 克隆项目
git clone https://github.com/xiechengmude/xDAN-Agentic-Finance-Hermes.git
cd xDAN-Agentic-Search-Test

# 4. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 5. 安装 Python 依赖
pip install --upgrade pip
pip install fastapi uvicorn pydantic

# 6. 环境检查
./check_environment.sh

# 7. 一键启动
./start_fullstack.sh simple

# 8. 验证安装
curl http://localhost:8003/health
open http://localhost:8003/docs
```

**Windows 完整安装示例：**
```powershell
# 1. 安装 Chocolatey (管理员权限运行)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. 安装基础环境
choco install python311 nodejs git curl

# 3. 克隆项目
git clone https://github.com/xiechengmude/xDAN-Agentic-Finance-Hermes.git
cd xDAN-Agentic-Search-Test

# 4. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 5. 安装依赖
pip install --upgrade pip
pip install fastapi uvicorn pydantic

# 6. 启动服务
python simple_api.py
```

**Ubuntu 完整安装示例：**
```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装基础环境
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y python3.11 python3.11-pip python3.11-venv nodejs git curl build-essential

# 3. 克隆项目
git clone https://github.com/xiechengmude/xDAN-Agentic-Finance-Hermes.git
cd xDAN-Agentic-Search-Test

# 4. 设置 Python 环境
python3.11 -m venv .venv
source .venv/bin/activate

# 5. 安装依赖
pip install --upgrade pip
pip install fastapi uvicorn pydantic

# 6. 启动服务
./start_fullstack.sh simple
```

### 6. 项目结构概览

```
xDAN-Agentic-Search-Test/
├── 📁 architectures/              # 双架构分离目录
│   ├── standard/                  # 标准架构 (生产推荐)
│   └── langgraph_native/          # LangGraph架构 (实验)
├── 📁 shared/                     # 共享组件
├── 📁 gstack-langgraph/           # GStack前端
├── 🚀 simple_api.py              # 简化API服务
├── 🚀 launch.py                  # 统一启动器
├── 📜 start_fullstack.sh         # 全栈启动脚本
├── 📜 start_frontend.sh          # 前端启动脚本
└── 📋 API_DOCUMENTATION.md       # API接口文档
```

## 🏗️ 架构选择指南

### 架构对比表

| 特性 | 简化API | 标准架构 | LangGraph架构 |
|------|---------|----------|---------------|
| **推荐场景** | 快速测试 | 生产环境 | 实验研究 |
| **端口** | 8003 | 8000/8001 | 8001 |
| **外部依赖** | ❌ 无 | ✅ MCP服务 | ✅ MCP服务 |
| **启动速度** | ⚡ 极快(2s) | 🔧 中等(8s) | 🔧 中等(8s) |
| **功能完整性** | 🎭 模拟 | ✅ 完整 | 🚧 部分 |
| **成功率** | 100%(模拟) | 100% | 71.43% |
| **工具数量** | 138(模拟) | 138 | 3 |
| **并行执行** | ❌ 模拟 | ✅ 40-60%提升 | ❌ 未实现 |

### 选择建议

1. **🎯 新手/快速测试**: 使用简化API服务
2. **🏭 生产环境**: 使用标准架构
3. **🔬 技术研究**: 使用LangGraph架构

## 🚀 部署方式

### 方式1: 一键启动 (推荐)

```bash
# 1. 进入项目目录
cd /Users/gump_m2/CascadeProjects/xDAN-Agentic-Search-Test

# 2. 选择启动方式
./start_fullstack.sh simple     # 简化API + 前端
./start_fullstack.sh standard   # 标准架构 + 前端
./start_fullstack.sh langgraph  # LangGraph架构 + 前端
./start_fullstack.sh both       # 双架构并行 + 前端
```

### 方式2: 手动启动

#### 后端服务启动

```bash
# 简化API服务 (推荐新手)
python simple_api.py
# ✅ 服务地址: http://localhost:8003
# ✅ API文档: http://localhost:8003/docs

# 标准架构API (生产推荐)
python launch.py standard --mode api --port 8000
# ✅ 服务地址: http://localhost:8000
# ✅ API文档: http://localhost:8000/docs

# LangGraph架构API (实验)
python launch.py langgraph --mode api --port 8001
# ✅ 服务地址: http://localhost:8001
# ✅ API文档: http://localhost:8001/docs
```

#### 前端服务启动

```bash
# 启动前端开发服务器
./start_frontend.sh
# ✅ 前端地址: http://localhost:5173
```

### 方式3: Docker部署 (生产环境)

```bash
# 构建Docker镜像
docker build -t xdan-api .

# 运行容器
docker run -p 8003:8003 xdan-api

# 使用docker-compose (推荐)
docker-compose up -d
```

## 🔧 调试指南

### 1. 服务健康检查

```bash
# 检查简化API服务
curl http://localhost:8003/health

# 检查标准架构API
curl http://localhost:8000/health

# 检查LangGraph架构API
curl http://localhost:8001/health

# 检查双架构状态
curl http://localhost:8003/architectures/status
```

### 2. 常见问题排查

#### 问题1: 端口占用
```bash
# 查看端口占用
lsof -i :8003
lsof -i :8000
lsof -i :8001
lsof -i :5173

# 终止占用进程
kill -9 <PID>
```

#### 问题2: Python依赖缺失
```bash
# 安装核心依赖
pip install fastapi uvicorn pydantic

# 安装完整依赖
pip install -r requirements.txt

# 检查Python版本
python --version  # 需要 3.8+
```

#### 问题3: Node.js依赖问题
```bash
# 清理缓存
npm cache clean --force
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 检查Node.js版本
node --version  # 需要 16+
npm --version
```

#### 问题4: 导入路径错误
```bash
# 检查Python路径
echo $PYTHONPATH

# 设置项目路径
export PYTHONPATH=/Users/gump_m2/CascadeProjects/xDAN-Agentic-Search-Test:$PYTHONPATH
```

### 3. 调试日志查看

```bash
# 查看简化API日志
tail -f /tmp/xdan_simple.log

# 查看标准架构日志
tail -f /tmp/xdan_standard.log

# 查看LangGraph架构日志
tail -f /tmp/xdan_langgraph.log

# 查看实时日志 (启动时)
tail -f /tmp/simple_api.log
```

### 4. API测试

```bash
# 健康检查
curl http://localhost:8003/health

# 获取项目信息
curl http://localhost:8003/

# 测试聊天接口
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"type": "human", "content": "测试API功能"}
    ]
  }'

# 测试流式接口
curl -X POST http://localhost:8003/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"type": "human", "content": "流式测试"}
    ]
  }'
```

## 🌐 前端对接

### GStack前端配置

```typescript
// 修改API配置文件
const apiUrl = import.meta.env.DEV
  ? "http://localhost:8003"  // 开发环境使用简化API
  : "http://localhost:8000"; // 生产环境使用标准架构

// 流式接口兼容LangGraph SDK
const thread = useStream({
  apiUrl,
  assistantId: "xdan-agent",
  messagesKey: "messages",
  onUpdateEvent: (event: any) => {
    // 事件处理逻辑保持不变
    if (event.generate_query) { /* 处理查询生成 */ }
    if (event.web_research) { /* 处理数据研究 */ }
    if (event.reflection) { /* 处理反思阶段 */ }
    if (event.finalize_answer) { /* 处理最终答案 */ }
  }
});
```

### 前端环境变量

```bash
# .env.development
VITE_API_URL=http://localhost:8003
VITE_WS_URL=ws://localhost:8003

# .env.production
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📊 性能监控

### 1. 服务监控

```bash
# 查看进程状态
ps aux | grep -E "(simple_api|launch\.py|uvicorn)" | grep -v grep

# 查看端口监听
netstat -tulpn | grep -E "(8000|8001|8003|5173)"

# 查看系统资源
top -p $(pgrep -f "simple_api\|launch\.py")
```

### 2. API性能测试

```bash
# 使用ab进行压力测试
ab -n 100 -c 10 http://localhost:8003/health

# 使用curl测试响应时间
time curl -s http://localhost:8003/health > /dev/null
```

## 🔐 安全配置

### 1. 生产环境配置

```bash
# 环境变量设置
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=info

# HTTPS配置 (生产环境)
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

### 2. 访问控制

```python
# 在API服务中添加CORS配置
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🛠️ 开发工具

### 1. 推荐IDE插件

```
VS Code:
- Python (Microsoft)
- REST Client (HTTP测试)
- Docker (容器管理)
- GitLens (Git增强)

PyCharm:
- FastAPI Plugin
- Docker Integration
```

### 2. 调试配置

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Simple API",
      "type": "python",
      "request": "launch",
      "program": "simple_api.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

## 📋 部署检查清单

### 启动前检查

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装 (如需前端)
- [ ] 端口 8000, 8001, 8003, 5173 未被占用
- [ ] 项目依赖已安装 (`pip install -r requirements.txt`)
- [ ] 环境变量已设置 (如需要)

### 启动后验证

- [ ] 后端健康检查通过 (`curl http://localhost:8003/health`)
- [ ] API文档可访问 (`http://localhost:8003/docs`)
- [ ] 聊天接口正常响应
- [ ] 前端页面可访问 (如已启动)
- [ ] 前后端通信正常

### 生产环境额外检查

- [ ] HTTPS配置正确
- [ ] 域名解析正常
- [ ] 防火墙规则配置
- [ ] 日志轮转配置
- [ ] 监控告警配置
- [ ] 备份策略实施

## 🆘 故障排除

### 常见错误及解决方案

1. **ModuleNotFoundError**
   ```bash
   export PYTHONPATH=$PWD:$PYTHONPATH
   ```

2. **端口占用错误**
   ```bash
   pkill -f "simple_api\|launch\.py\|uvicorn"
   ```

3. **权限不足错误**
   ```bash
   chmod +x start_fullstack.sh start_frontend.sh
   ```

4. **依赖版本冲突**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

## 📞 技术支持

- **项目仓库**: https://github.com/xiechengmude/xDAN-Agentic-Finance-Hermes
- **API文档**: http://localhost:8003/docs
- **架构文档**: API_DOCUMENTATION.md
- **问题报告**: GitHub Issues

---

**🎯 快速命令参考**

```bash
# 一键启动 (推荐)
./start_fullstack.sh simple

# 健康检查
curl http://localhost:8003/health

# 查看日志
tail -f /tmp/simple_api.log

# 停止服务
pkill -f "simple_api\|uvicorn"
```

**✅ 部署完成标志**: 所有健康检查通过，API文档可访问，前端正常加载