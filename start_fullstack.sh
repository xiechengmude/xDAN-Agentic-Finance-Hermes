#!/bin/bash

# xDAN 全栈启动脚本 (架构分离后版本)
# Full-stack Startup Script for xDAN Dual Architecture (v2.0)

echo "🚀 启动 xDAN 全栈应用 (双架构版)..."
echo "========================================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 项目根目录: $SCRIPT_DIR"
echo "📊 架构状态: 已完成双架构分离"
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

echo "🐍 Python 版本: $($PYTHON_CMD --version)"

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

echo "📦 Node.js 版本: $(node --version)"
echo ""

# 选择后端架构
echo "🏗️ 选择要启动的后端架构:"
echo "   1) 标准架构 (100%成功率, 138个工具) [推荐生产]"
echo "   2) LangGraph原生架构 (71.43%成功率, 3个工具) [实验]"
echo "   3) 简化API服务 (无外部依赖) [快速测试]"
echo "   4) 双架构并行启动"
echo ""

# 自动选择或用户选择
if [ "$1" = "auto" ] || [ "$1" = "standard" ]; then
    BACKEND_CHOICE="1"
    echo "🎯 自动选择: 标准架构"
elif [ "$1" = "langgraph" ]; then
    BACKEND_CHOICE="2"
    echo "🎯 自动选择: LangGraph架构"
elif [ "$1" = "simple" ]; then
    BACKEND_CHOICE="3"
    echo "🎯 自动选择: 简化API服务"
elif [ "$1" = "both" ]; then
    BACKEND_CHOICE="4"
    echo "🎯 自动选择: 双架构并行"
else
    read -p "请选择 (1-4) [默认: 3]: " BACKEND_CHOICE
    BACKEND_CHOICE=${BACKEND_CHOICE:-3}
fi

echo ""

# 全局变量存储进程ID
BACKEND_PIDS=()

# 函数：启动标准架构后端
start_standard_backend() {
    echo "🔧 启动标准架构后端服务..."
    
    # 检查依赖
    echo "📋 检查后端依赖..."
    $PYTHON_CMD -c "import fastapi, uvicorn" 2>/dev/null || {
        echo "⚠️ 缺少必要的 Python 包，尝试安装..."
        pip install fastapi uvicorn || {
            echo "❌ 无法安装依赖，请手动运行: pip install fastapi uvicorn"
            return 1
        }
    }
    
    # 启动标准架构
    echo "🚀 启动标准架构API服务 (端口 8000)..."
    $PYTHON_CMD launch.py standard --mode api --port 8000 > /tmp/xdan_standard.log 2>&1 &
    local PID=$!
    BACKEND_PIDS+=($PID)
    echo "标准架构 PID: $PID"
    
    # 等待启动
    echo "⏳ 等待标准架构启动..."
    sleep 8
    
    # 检查是否启动成功
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ 标准架构启动成功"
        return 0
    else
        echo "⚠️ 标准架构可能还在启动中，查看日志: tail -f /tmp/xdan_standard.log"
        return 1
    fi
}

# 函数：启动LangGraph架构后端
start_langgraph_backend() {
    echo "🔧 启动LangGraph原生架构后端服务..."
    
    echo "🚀 启动LangGraph架构API服务 (端口 8001)..."
    $PYTHON_CMD launch.py langgraph --mode api --port 8001 > /tmp/xdan_langgraph.log 2>&1 &
    local PID=$!
    BACKEND_PIDS+=($PID)
    echo "LangGraph架构 PID: $PID"
    
    # 等待启动
    echo "⏳ 等待LangGraph架构启动..."
    sleep 8
    
    # 检查是否启动成功
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo "✅ LangGraph架构启动成功"
        return 0
    else
        echo "⚠️ LangGraph架构可能还在启动中，查看日志: tail -f /tmp/xdan_langgraph.log"
        return 1
    fi
}

# 函数：启动简化API服务
start_simple_backend() {
    echo "🔧 启动简化API服务..."
    
    echo "🚀 启动简化API服务 (端口 8003, 无外部依赖)..."
    $PYTHON_CMD simple_api.py > /tmp/xdan_simple.log 2>&1 &
    local PID=$!
    BACKEND_PIDS+=($PID)
    echo "简化API PID: $PID"
    
    # 等待启动
    echo "⏳ 等待简化API启动..."
    sleep 3
    
    # 检查是否启动成功
    if curl -s http://localhost:8003/health >/dev/null 2>&1; then
        echo "✅ 简化API启动成功"
        return 0
    else
        echo "⚠️ 简化API启动失败，查看日志: tail -f /tmp/xdan_simple.log"
        return 1
    fi
}

# 函数：启动前端
start_frontend() {
    echo ""
    echo "🎨 启动前端服务..."
    
    # 查找前端目录
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
        echo "⚠️ 未找到前端目录，跳过前端启动"
        echo "💡 如需前端，请运行: ./start_frontend.sh"
        return 1
    fi
    
    echo "✅ 找到前端目录: $FRONTEND_DIR"
    cd "$FRONTEND_DIR"
    
    # 检查依赖
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
    echo "🛑 正在停止所有服务..."
    
    # 停止所有后端进程
    for PID in "${BACKEND_PIDS[@]}"; do
        if [ ! -z "$PID" ]; then
            echo "⏹️ 停止后端服务 (PID: $PID)"
            kill $PID 2>/dev/null
        fi
    done
    
    # 停止相关进程
    pkill -f "launch.py" 2>/dev/null
    pkill -f "simple_api.py" 2>/dev/null
    pkill -f "uvicorn" 2>/dev/null
    
    echo "✅ 清理完成"
    exit 0
}

# 捕获中断信号
trap cleanup SIGINT SIGTERM

# 根据选择启动后端
case $BACKEND_CHOICE in
    1)
        echo "🎯 启动标准架构后端..."
        start_standard_backend
        ;;
    2)
        echo "🎯 启动LangGraph架构后端..."
        start_langgraph_backend
        ;;
    3)
        echo "🎯 启动简化API服务..."
        start_simple_backend
        ;;
    4)
        echo "🎯 启动双架构并行服务..."
        start_standard_backend
        start_langgraph_backend
        start_simple_backend
        ;;
    *)
        echo "❌ 无效选择，使用简化API服务"
        start_simple_backend
        ;;
esac

echo ""
echo "📋 服务信息总览:"
echo "================================================="
echo "🏗️ xDAN双架构系统 v2.0"
echo "   📊 架构状态: 已完成分离和清理"
echo "   🔧 标准架构: 100%成功率，138个工具"
echo "   ⚗️ LangGraph架构: 71.43%成功率，3个工具"
echo ""
echo "🌐 可用服务地址:"
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "   ✅ 标准架构API:     http://localhost:8000"
    echo "      - API文档:      http://localhost:8000/docs"
fi
if curl -s http://localhost:8001/health >/dev/null 2>&1; then
    echo "   ✅ LangGraph架构API: http://localhost:8001"
    echo "      - API文档:      http://localhost:8001/docs"
fi
if curl -s http://localhost:8003/health >/dev/null 2>&1; then
    echo "   ✅ 简化API服务:     http://localhost:8003"
    echo "      - API文档:      http://localhost:8003/docs"
fi
echo "   🎨 前端界面:        http://localhost:5173"
echo ""
echo "📋 架构对比:"
echo "   /architectures/status - 查看详细架构状态"
echo ""
echo "⏹️  按 Ctrl+C 停止所有服务"
echo "================================================="
echo ""

# 启动前端
start_frontend

# 等待前端进程结束
wait