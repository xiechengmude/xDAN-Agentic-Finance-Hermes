#!/usr/bin/env python3
"""
LangGraph原生架构启动脚本
LangGraph Native Architecture Launcher
"""

import sys
import asyncio
from pathlib import Path

# 添加共享组件到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "shared"))
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LangGraph原生架构启动器')
    parser.add_argument('--mode', choices=['api', 'test'], 
                       default='api', help='运行模式')
    parser.add_argument('--port', type=int, default=8001, help='API端口')
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        # 启动FastAPI服务器
        import uvicorn
        uvicorn.run("api.fastapi_app:app", host="0.0.0.0", port=args.port, reload=True)
    elif args.mode == 'test':
        # 运行测试模式
        print("🧪 LangGraph原生架构测试模式")
        print("功能开发中...")
    else:
        print("❌ 未知模式")

if __name__ == "__main__":
    main()
