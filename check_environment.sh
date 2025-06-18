#!/bin/bash
# xDAN 项目环境检查脚本
# Environment Check Script for xDAN Project

echo "🔍 xDAN 项目环境检查"
echo "========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    local cmd=$1
    local name=$2
    local required_version=$3
    
    if command -v $cmd &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -1)
        echo -e "${GREEN}✅ $name${NC}: $version"
        return 0
    else
        echo -e "${RED}❌ $name${NC}: 未安装 (需要 $required_version+)"
        return 1
    fi
}

# 检查 Python 版本
check_python_version() {
    if command -v python3 &> /dev/null; then
        local version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            echo -e "${GREEN}✅ Python3${NC}: $version (满足要求 ≥3.10)"
        else
            echo -e "${YELLOW}⚠️  Python3${NC}: $version (建议升级到 3.10+)"
        fi
    else
        echo -e "${RED}❌ Python3${NC}: 未安装"
    fi
}

# 检查 Node.js 版本
check_node_version() {
    if command -v node &> /dev/null; then
        local version=$(node --version | sed 's/v//')
        local major=$(echo $version | cut -d. -f1)
        
        if [ "$major" -ge 16 ]; then
            echo -e "${GREEN}✅ Node.js${NC}: v$version (满足要求 ≥16)"
        else
            echo -e "${YELLOW}⚠️  Node.js${NC}: v$version (建议升级到 16+)"
        fi
    else
        echo -e "${RED}❌ Node.js${NC}: 未安装"
    fi
}

# 主检查流程
echo "🐍 Python 环境检查:"
check_python_version
check_command "uv" "uv (推荐)" "0.1"
check_command "pip3" "pip3 (备用)" "21.0"

echo ""
echo "📦 Node.js 环境检查:"
check_node_version
check_command "npm" "npm" "8.0"

echo ""
echo "🛠️ 系统工具检查:"
check_command "git" "Git" "2.20"
check_command "curl" "curl" "7.68"

# 检查 Python 包
echo ""
echo "📚 Python 包检查:"
if command -v python3 &> /dev/null; then
    python3 -c "
import sys
packages = ['fastapi', 'uvicorn', 'pydantic']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}: 已安装')
    except ImportError:
        print(f'❌ {pkg}: 未安装')
        missing.append(pkg)

if missing:
    print(f'\\n💡 安装缺失包: pip3 install {\" \".join(missing)}')
"
else
    echo -e "${RED}❌ Python3 未安装，无法检查包${NC}"
fi

# 检查端口可用性
echo ""
echo "🌐 端口可用性检查:"
ports=(8000 8001 8003 5173)
occupied_ports=()

for port in "${ports[@]}"; do
    if command -v lsof &> /dev/null; then
        if lsof -i :$port &> /dev/null; then
            echo -e "${YELLOW}⚠️  端口 $port${NC}: 已被占用"
            occupied_ports+=($port)
        else
            echo -e "${GREEN}✅ 端口 $port${NC}: 可用"
        fi
    else
        echo -e "${YELLOW}⚠️  lsof 未安装，无法检查端口 $port${NC}"
    fi
done

# 检查项目文件
echo ""
echo "📁 项目文件检查:"
files=(
    "simple_api.py"
    "launch.py"
    "start_fullstack.sh"
    "start_frontend.sh"
    "API_DOCUMENTATION.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}: 存在"
    else
        echo -e "${RED}❌ $file${NC}: 不存在"
    fi
done

# 输出修复建议
echo ""
echo "🎯 修复建议:"
echo "========================="

if ! command -v python3 &> /dev/null; then
    echo "📋 安装 Python 3.10+:"
    echo "# macOS: brew install python@3.11 uv"
    echo "# Ubuntu: sudo apt install python3.11 && curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "# Windows: https://www.python.org/downloads/ && pip install uv"
    echo ""
fi

if ! command -v uv &> /dev/null; then
    echo "📋 安装 uv 包管理器 (推荐):"
    echo "# macOS: brew install uv"
    echo "# Ubuntu: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "# Windows: pip install uv"
    echo ""
fi

if ! command -v node &> /dev/null; then
    echo "📋 安装 Node.js 16+:"
    echo "# macOS: brew install node@18"
    echo "# Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "# Windows: https://nodejs.org/"
    echo ""
fi

if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📋 安装 Python 依赖:"
    if command -v uv &> /dev/null; then
        echo "uv pip install fastapi uvicorn pydantic  # 推荐 (极速安装)"
    else
        echo "pip3 install fastapi uvicorn pydantic   # 传统方式"
    fi
    echo ""
fi

if [ ${#occupied_ports[@]} -gt 0 ]; then
    echo "📋 释放占用端口:"
    for port in "${occupied_ports[@]}"; do
        echo "# 端口 $port: lsof -ti:$port | xargs kill -9"
    done
    echo ""
fi

echo "🚀 快速启动命令:"
echo "./start_fullstack.sh simple    # 启动简化API服务"
echo "curl http://localhost:8003/health  # 测试API"
echo ""
echo "========================="
echo -e "${GREEN}✅ 环境检查完成${NC}"