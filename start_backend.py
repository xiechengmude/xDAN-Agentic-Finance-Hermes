#!/usr/bin/env python3
"""
xDAN-LangGraph 适配器后端启动脚本
Backend Startup Script for xDAN-LangGraph Adapter
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn
from api.fastapi_app import app


def main():
    """主函数"""
    print("🚀 启动 xDAN-LangGraph 适配器后端服务...")
    print("=" * 60)
    print("📡 API 服务: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    print("🔧 工具列表: http://localhost:8000/tools/list")
    print("📊 WebSocket: ws://localhost:8000/ws/stream")
    print("=" * 60)
    print()
    
    # 检查环境
    print("🔍 检查环境配置...")
    
    # 检查必需的环境变量
    required_env_vars = [
        "MCP_SERVER_URL",
        "MODEL_URL", 
        "MODEL_API_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ 缺少环境变量: {', '.join(missing_vars)}")
        print("💡 使用默认配置启动...")
    else:
        print("✅ 环境配置检查通过")
    
    print()
    
    # 启动服务器
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False,  # 生产环境关闭自动重载
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n⏹️ 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()