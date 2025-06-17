#!/bin/bash

# xDAN-LangGraph 全栈启动脚本
# Full-stack Startup Script for xDAN-LangGraph Integration

echo "🚀 启动 xDAN-LangGraph 全栈应用..."
echo "============================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 项目目录: $SCRIPT_DIR"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 使用 python3 或 python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Python 命令: $PYTHON_CMD"

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

echo "📦 Node.js 版本: $(node --version)"
echo ""

# 函数：启动后端
start_backend() {
    echo "🔧 启动后端服务..."
    cd "$SCRIPT_DIR"
    
    # 检查 Python 依赖
    echo "📋 检查后端依赖..."
    $PYTHON_CMD -c "import fastapi, uvicorn" 2>/dev/null || {
        echo "⚠️ 缺少必要的 Python 包，尝试安装..."
        pip install fastapi uvicorn || {
            echo "❌ 无法安装依赖，请手动运行: pip install fastapi uvicorn"
            exit 1
        }
    }
    
    # 启动后端（在后台）
    echo "🚀 启动后端服务 (端口 8000)..."
    $PYTHON_CMD start_backend.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    # 等待后端启动
    echo "⏳ 等待后端服务启动..."
    sleep 5
    
    # 检查后端是否启动成功
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ 后端服务启动成功"
    else
        echo "⚠️ 后端服务可能还在启动中..."
    fi
}

# 函数：启动前端
start_frontend() {
    echo ""
    echo "🎨 启动前端服务..."
    cd "$SCRIPT_DIR/frontend"
    
    # 检查 package.json
    if [ ! -f "package.json" ]; then
        echo "❌ 前端 package.json 不存在"
        return 1
    fi
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        echo "📦 安装前端依赖..."
        npm install || {
            echo "❌ 前端依赖安装失败"
            return 1
        }
    fi
    
    echo "🚀 启动前端开发服务器 (端口 5173)..."
    npm run dev
}

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    
    # 停止后端进程
    if [ ! -z "$BACKEND_PID" ]; then
        echo "⏹️ 停止后端服务 (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # 停止所有相关进程
    pkill -f "start_backend.py" 2>/dev/null
    pkill -f "uvicorn" 2>/dev/null
    
    echo "✅ 清理完成"
    exit 0
}

# 捕获中断信号
trap cleanup SIGINT SIGTERM

echo "📋 启动序列:"
echo "   1. 后端服务 (FastAPI + xDAN适配器)"
echo "   2. 前端服务 (React + Vite)"
echo ""
echo "🌐 访问地址:"
echo "   前端界面: http://localhost:5173"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "⏹️  按 Ctrl+C 停止所有服务"
echo "============================================"
echo ""

# 启动后端
start_backend

# 启动前端
start_frontend

# 等待前端进程结束
wait