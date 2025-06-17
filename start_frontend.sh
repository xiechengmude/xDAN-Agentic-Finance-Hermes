#!/bin/bash

# xDAN-LangGraph 前端启动脚本
# Frontend Startup Script for xDAN-LangGraph Integration

echo "🚀 启动 xDAN-LangGraph 前端服务..."
echo "=========================================="

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

# 检查 npm 是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装 npm"
    exit 1
fi

# 进入前端目录
cd "$(dirname "$0")/frontend" || {
    echo "❌ 无法进入前端目录"
    exit 1
}

echo "📁 当前目录: $(pwd)"

# 检查是否存在 package.json
if [ ! -f "package.json" ]; then
    echo "❌ 未找到 package.json 文件"
    exit 1
fi

# 安装依赖（如果 node_modules 不存在）
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 前端依赖已存在"
fi

echo ""
echo "🌐 前端服务将在以下地址启动:"
echo "   本地访问: http://localhost:5173"
echo "   网络访问: http://0.0.0.0:5173"
echo ""
echo "🔗 后端API地址: http://localhost:8000"
echo "📖 确保后端服务已启动: python start_backend.py"
echo ""
echo "⏹️  按 Ctrl+C 停止服务"
echo "=========================================="

# 启动开发服务器
npm run dev