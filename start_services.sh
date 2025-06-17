#!/bin/bash

# xDAN金融智能体服务启动脚本
# 包含进程管理、代理清理和重启功能

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查当前目录
check_directory() {
    if [[ ! -d "langraph-stack/backend" || ! -d "langraph-stack/frontend" ]]; then
        log_error "请在项目根目录运行此脚本 (应包含 langraph-stack 目录)"
        exit 1
    fi
}

# 清理代理设置
clear_proxy() {
    log_step "清理HTTP代理设置..."
    unset HTTP_PROXY
    unset HTTPS_PROXY
    unset http_proxy
    unset https_proxy
    export NO_PROXY="localhost,127.0.0.1"
    log_info "代理设置已清理"
}

# 杀死现有进程
kill_existing_processes() {
    log_step "清理现有进程..."
    
    # 杀死LangGraph进程
    if pgrep -f "langgraph dev" > /dev/null; then
        log_info "停止现有的LangGraph服务..."
        pkill -f "langgraph dev" || true
        sleep 2
    fi
    
    # 杀死Vite进程
    if pgrep -f "node.*vite" > /dev/null; then
        log_info "停止现有的Vite服务..."
        pkill -f "node.*vite" || true
        sleep 2
    fi
    
    # 杀死npm dev进程
    if pgrep -f "npm.*dev" > /dev/null; then
        log_info "停止现有的npm dev进程..."
        pkill -f "npm.*dev" || true
        sleep 2
    fi
    
    # 检查端口占用
    if lsof -ti:8123 > /dev/null 2>&1; then
        log_info "端口8123被占用，尝试释放..."
        lsof -ti:8123 | xargs kill -9 || true
        sleep 1
    fi
    
    if lsof -ti:5173 > /dev/null 2>&1; then
        log_info "端口5173被占用，尝试释放..."
        lsof -ti:5173 | xargs kill -9 || true
        sleep 1
    fi
    
    log_info "进程清理完成"
}

# 启动后端服务
start_backend() {
    log_step "启动后端服务 (LangGraph)..."
    
    cd langraph-stack/backend
    
    # 检查虚拟环境
    if [[ ! -d ".venv" ]]; then
        log_error "后端虚拟环境不存在，请先运行: cd langraph-stack/backend && python -m venv .venv"
        exit 1
    fi
    
    # 激活虚拟环境并启动服务
    source .venv/bin/activate
    
    log_info "启动LangGraph服务在端口8123..."
    nohup langgraph dev --host 0.0.0.0 --port 8123 > ../../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    
    cd ../..
    
    # 等待后端启动
    log_info "等待后端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8123/health > /dev/null 2>&1; then
            log_info "后端服务启动成功！(PID: $BACKEND_PID)"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    log_error "后端服务启动超时"
    return 1
}

# 启动前端服务
start_frontend() {
    log_step "启动前端服务 (React + Vite)..."
    
    cd langraph-stack/frontend
    
    # 检查node_modules
    if [[ ! -d "node_modules" ]]; then
        log_warn "前端依赖未安装，正在安装..."
        npm install
    fi
    
    log_info "启动Vite服务在端口5173..."
    nohup npm run dev > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    cd ../..
    
    # 等待前端启动
    log_info "等待前端服务启动..."
    for i in {1..20}; do
        if curl -s http://localhost:5173/ > /dev/null 2>&1; then
            log_info "前端服务启动成功！(PID: $FRONTEND_PID)"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    log_error "前端服务启动超时"
    return 1
}

# 检查服务状态
check_services() {
    log_step "检查服务状态..."
    
    # 检查后端
    if curl -s http://localhost:8123/health > /dev/null 2>&1; then
        log_info "✅ 后端服务正常 (http://localhost:8123)"
    else
        log_error "❌ 后端服务异常"
    fi
    
    # 检查前端
    if curl -s http://localhost:5173/ > /dev/null 2>&1; then
        log_info "✅ 前端服务正常 (http://localhost:5173)"
    else
        log_error "❌ 前端服务异常"
    fi
}

# 显示服务信息
show_service_info() {
    echo ""
    echo "🎉 服务启动完成！"
    echo ""
    echo "📋 服务信息:"
    echo "  • 后端API: http://localhost:8123"
    echo "  • 前端界面: http://localhost:5173"
    echo "  • API文档: http://localhost:8123/docs"
    echo "  • LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://localhost:8123"
    echo ""
    echo "📝 日志文件:"
    echo "  • 后端日志: logs/backend.log"
    echo "  • 前端日志: logs/frontend.log"
    echo ""
    echo "🛠️  管理命令:"
    echo "  • 查看日志: tail -f logs/backend.log 或 tail -f logs/frontend.log"
    echo "  • 停止服务: ./start_services.sh stop"
    echo "  • 重启服务: ./start_services.sh restart"
    echo ""
    echo "🔍 测试建议:"
    echo "  • 简单查询: '请帮我查询平安银行的基本信息'"
    echo "  • 复杂分析: '分析比亚迪公司的投资价值，包括基本面和股价表现'"
    echo ""
}

# 停止服务
stop_services() {
    log_step "停止所有服务..."
    kill_existing_processes
    log_info "所有服务已停止"
}

# 创建日志目录
create_log_dir() {
    if [[ ! -d "logs" ]]; then
        mkdir -p logs
        log_info "创建日志目录: logs/"
    fi
}

# 主函数
main() {
    echo "🚀 xDAN金融智能体服务管理脚本"
    echo "=================================="
    
    # 检查参数
    case "${1:-start}" in
        "start")
            check_directory
            create_log_dir
            clear_proxy
            kill_existing_processes
            
            if start_backend && start_frontend; then
                sleep 3
                check_services
                show_service_info
            else
                log_error "服务启动失败，请检查日志文件"
                exit 1
            fi
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            log_info "重启服务..."
            stop_services
            sleep 3
            $0 start
            ;;
        "status")
            check_services
            ;;
        "logs")
            if [[ -f "logs/backend.log" && -f "logs/frontend.log" ]]; then
                echo "=== 后端日志 (最近20行) ==="
                tail -20 logs/backend.log
                echo ""
                echo "=== 前端日志 (最近20行) ==="
                tail -20 logs/frontend.log
            else
                log_warn "日志文件不存在，请先启动服务"
            fi
            ;;
        "help"|"-h"|"--help")
            echo "用法: $0 [命令]"
            echo ""
            echo "命令:"
            echo "  start    启动所有服务 (默认)"
            echo "  stop     停止所有服务"
            echo "  restart  重启所有服务"
            echo "  status   检查服务状态"
            echo "  logs     查看日志"
            echo "  help     显示帮助信息"
            ;;
        *)
            log_error "未知命令: $1"
            echo "使用 '$0 help' 查看帮助"
            exit 1
            ;;
    esac
}

# 信号处理
trap 'log_warn "收到中断信号，正在清理..."; kill_existing_processes; exit 1' INT TERM

# 执行主函数
main "$@" 