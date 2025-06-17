#!/bin/bash

# xDAN金融智能体快速启动脚本
# 一键清理、启动前后端服务

echo "🚀 xDAN金融智能体快速启动"
echo "=========================="

# 清理代理设置
echo "清理代理设置..."
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy
export NO_PROXY="localhost,127.0.0.1"

# 杀死现有进程
echo "清理现有进程..."
pkill -f "langgraph dev" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true
sleep 2

# 启动后端
echo "启动后端服务..."
cd langraph-stack/backend
source .venv/bin/activate
nohup langgraph dev --host 0.0.0.0 --port 8123 > /dev/null 2>&1 &
cd ../..

# 等待后端启动
echo "等待后端启动..."
sleep 8

# 启动前端
echo "启动前端服务..."
cd langraph-stack/frontend
nohup npm run dev > /dev/null 2>&1 &
cd ../..

# 等待前端启动
echo "等待前端启动..."
sleep 5

echo ""
echo "🎉 服务启动完成！"
echo "• 前端界面: http://localhost:5173"
echo "• 后端API: http://localhost:8123"
echo ""
echo "停止服务: pkill -f 'langgraph dev'; pkill -f 'node.*vite'" 