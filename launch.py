#!/usr/bin/env python3
"""
xDAN项目统一启动器
xDAN Project Unified Launcher

支持启动不同架构的服务
"""

import sys
import subprocess
import argparse
from pathlib import Path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='xDAN项目统一启动器')
    parser.add_argument('architecture', choices=['standard', 'langgraph', 'both'], 
                       help='选择架构')
    parser.add_argument('--mode', choices=['api', 'interactive', 'demo', 'test'],
                       default='api', help='运行模式')
    parser.add_argument('--port', type=int, help='API端口')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent
    
    if args.architecture == 'standard':
        print("🚀 启动标准xDAN架构...")
        standard_dir = project_root / "architectures" / "standard"
        port = args.port or 8000
        
        cmd = [sys.executable, "run.py", "--mode", args.mode]
        if args.mode == 'api':
            cmd.extend(["--port", str(port)])
        
        subprocess.run(cmd, cwd=standard_dir)
        
    elif args.architecture == 'langgraph':
        print("🚀 启动LangGraph原生架构...")
        langgraph_dir = project_root / "architectures" / "langgraph_native"
        port = args.port or 8001
        
        cmd = [sys.executable, "run.py", "--mode", args.mode]
        if args.mode == 'api':
            cmd.extend(["--port", str(port)])
        
        subprocess.run(cmd, cwd=langgraph_dir)
        
    elif args.architecture == 'both':
        print("🚀 启动双架构并行服务...")
        print("标准架构: http://localhost:8000")
        print("LangGraph架构: http://localhost:8001")
        
        # 启动标准架构 (端口8000)
        standard_dir = project_root / "architectures" / "standard"
        standard_cmd = [sys.executable, "run.py", "--mode", "api", "--port", "8000"]
        
        # 启动LangGraph架构 (端口8001)
        langgraph_dir = project_root / "architectures" / "langgraph_native"  
        langgraph_cmd = [sys.executable, "run.py", "--mode", "api", "--port", "8001"]
        
        # 并行启动
        import threading
        
        def run_standard():
            subprocess.run(standard_cmd, cwd=standard_dir)
        
        def run_langgraph():
            subprocess.run(langgraph_cmd, cwd=langgraph_dir)
        
        standard_thread = threading.Thread(target=run_standard)
        langgraph_thread = threading.Thread(target=run_langgraph)
        
        standard_thread.start()
        langgraph_thread.start()
        
        try:
            standard_thread.join()
            langgraph_thread.join()
        except KeyboardInterrupt:
            print("\n⏹️ 停止所有服务")

if __name__ == "__main__":
    main()
