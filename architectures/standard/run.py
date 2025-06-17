#!/usr/bin/env python3
"""
标准xDAN架构启动脚本
Standard xDAN Architecture Launcher
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
    
    parser = argparse.ArgumentParser(description='xDAN标准架构启动器')
    parser.add_argument('--mode', choices=['interactive', 'api', 'demo'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--port', type=int, default=8000, help='API端口')
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        # 启动FastAPI服务器
        import uvicorn
        uvicorn.run("api.fastapi_app:app", host="0.0.0.0", port=args.port, reload=True)
    elif args.mode == 'demo':
        # 运行演示模式
        from demo_parallel_execution import main as demo_main
        asyncio.run(demo_main())
    else:
        # 交互式模式
        from main import main as interactive_main
        asyncio.run(interactive_main())

if __name__ == "__main__":
    main()
