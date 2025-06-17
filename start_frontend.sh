#!/bin/bash

# xDAN 前端启动脚本 (架构分离后版本)
# Frontend Startup Script for xDAN Dual Architecture (v2.0)

echo "🚀 启动 xDAN 前端服务 (架构分离版)..."
echo "=================================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 项目根目录: $SCRIPT_DIR"

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

echo "📦 Node.js 版本: $(node --version)"
echo "📦 npm 版本: $(npm --version)"

# 检查前端目录
FRONTEND_DIRS=(
    "$SCRIPT_DIR/frontend"
    "$SCRIPT_DIR/gstack-langgraph/frontend"
    "$SCRIPT_DIR/shared/frontend"
)

FRONTEND_DIR=""
for dir in "${FRONTEND_DIRS[@]}"; do
    if [ -d "$dir" ] && [ -f "$dir/package.json" ]; then
        FRONTEND_DIR="$dir"
        break
    fi
done

if [ -z "$FRONTEND_DIR" ]; then
    echo "❌ 未找到前端目录，请检查以下位置："
    for dir in "${FRONTEND_DIRS[@]}"; do
        echo "   - $dir"
    done
    echo ""
    echo "💡 建议："
    echo "   1. 如果要对接GStack前端："
    echo "      cp -r gstack-langgraph/frontend ./frontend"
    echo "   2. 或创建新的前端项目："
    echo "      npx create-react-app frontend --template typescript"
    exit 1
fi

echo "✅ 找到前端目录: $FRONTEND_DIR"
cd "$FRONTEND_DIR" || {
    echo "❌ 无法进入前端目录: $FRONTEND_DIR"
    exit 1
}

echo "📁 当前工作目录: $(pwd)"

# 检查 package.json
if [ ! -f "package.json" ]; then
    echo "❌ 未找到 package.json 文件"
    exit 1
fi

echo "📋 项目信息:"
if command -v jq &> /dev/null && [ -f "package.json" ]; then
    PROJECT_NAME=$(cat package.json | jq -r '.name // "未知"')
    PROJECT_VERSION=$(cat package.json | jq -r '.version // "未知"')
    echo "   - 项目名称: $PROJECT_NAME"
    echo "   - 项目版本: $PROJECT_VERSION"
fi

# 安装依赖（如果 node_modules 不存在）
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 安装前端依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        echo "💡 尝试清理缓存后重新安装:"
        echo "   npm cache clean --force"
        echo "   rm -rf node_modules package-lock.json"
        echo "   npm install"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 前端依赖已存在"
fi

echo ""
echo "🏗️ xDAN 双架构信息:"
echo "   📊 架构状态: 已完成双架构分离"
echo "   🔧 标准架构: 100%成功率，138个工具"
echo "   ⚗️ LangGraph架构: 71.43%成功率，3个工具"
echo ""
echo "🌐 前端服务将在以下地址启动:"
echo "   本地访问: http://localhost:5173"
echo "   网络访问: http://0.0.0.0:5173"
echo ""
echo "🔗 可用的后端服务:"
echo "   标准架构API:     http://localhost:8000"
echo "   LangGraph架构API: http://localhost:8001"
echo "   简化API服务:     http://localhost:8003"
echo ""
echo "🚀 后端启动命令:"
echo "   python launch.py standard --mode api --port 8000"
echo "   python launch.py langgraph --mode api --port 8001"
echo "   python simple_api.py  # 简化服务，无外部依赖"
echo ""
echo "📖 API文档地址:"
echo "   http://localhost:8000/docs (标准架构)"
echo "   http://localhost:8001/docs (LangGraph架构)"
echo "   http://localhost:8003/docs (简化服务)"
echo ""
echo "⏹️  按 Ctrl+C 停止服务"
echo "=================================================="

# 启动开发服务器
echo "🎬 启动前端开发服务器..."
npm run dev