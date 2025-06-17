#!/usr/bin/env python3
"""
架构分离重构脚本
Architecture Separation Refactoring Script

将混合的双架构代码分离到独立文件夹
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List


class ArchitectureSeparator:
    """架构分离器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.architectures_dir = self.project_root / "architectures"
        self.shared_dir = self.project_root / "shared"
        self.original_backup = self.project_root / "original_backup"
        
        # 架构映射配置
        self.architecture_mapping = {
            "standard": {
                "name": "标准xDAN架构",
                "description": "基于intelligent_tool_selector的原生xDAN实现",
                "files": [
                    "main.py",
                    "start_backend.py", 
                    "api/fastapi_app.py",
                    "adapters/xdan_langgraph_adapter.py",
                    "adapters/event_mapper.py",
                    "intelligent_tool_selector/",
                    "demo_parallel_execution.py"
                ],
                "dependencies": [
                    "openai>=1.0.0",
                    "fastapi>=0.104.0",
                    "networkx>=3.0",
                    "aiohttp>=3.9.0"
                ]
            },
            "langgraph_native": {
                "name": "LangGraph原生架构", 
                "description": "基于LangGraph官方SDK的原生实现",
                "files": [
                    "api/fastapi_app_langgraph_native.py",
                    "adapters/langgraph_native_mcp_adapter.py"
                ],
                "dependencies": [
                    "langgraph>=0.1.0",
                    "langchain-core>=0.2.0",
                    "langchain-openai>=0.1.0"
                ]
            },
            "shared": {
                "name": "共享组件",
                "description": "两个架构共同使用的工具和配置",
                "files": [
                    "requirements.txt",
                    "requirements-api.txt",
                    "pyproject.toml",
                    ".env.example",
                    "tools/",
                    "data/",
                    "deploy/"
                ]
            }
        }
    
    def create_directory_structure(self):
        """创建新的目录结构"""
        print("📁 创建新的目录结构...")
        
        # 创建主要架构目录
        directories = [
            self.architectures_dir / "standard",
            self.architectures_dir / "standard" / "api",
            self.architectures_dir / "standard" / "adapters", 
            self.architectures_dir / "standard" / "tests",
            self.architectures_dir / "standard" / "docs",
            
            self.architectures_dir / "langgraph_native",
            self.architectures_dir / "langgraph_native" / "api",
            self.architectures_dir / "langgraph_native" / "adapters",
            self.architectures_dir / "langgraph_native" / "tests",
            self.architectures_dir / "langgraph_native" / "docs",
            
            self.shared_dir,
            self.shared_dir / "config",
            self.shared_dir / "utils", 
            self.shared_dir / "types",
            self.shared_dir / "tools",
            
            self.project_root / "tests" / "integration",
            self.project_root / "docs" / "architectures"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ 创建目录: {directory.relative_to(self.project_root)}")
    
    def backup_original_structure(self):
        """备份原始结构"""
        print("\n💾 备份原始项目结构...")
        
        if self.original_backup.exists():
            shutil.rmtree(self.original_backup)
        
        # 备份关键文件和目录
        backup_items = [
            "api",
            "adapters", 
            "intelligent_tool_selector",
            "main.py",
            "start_backend.py",
            "demo_parallel_execution.py",
            "requirements.txt",
            "pyproject.toml"
        ]
        
        self.original_backup.mkdir(parents=True, exist_ok=True)
        
        for item in backup_items:
            source = self.project_root / item
            if source.exists():
                if source.is_dir():
                    shutil.copytree(source, self.original_backup / item)
                else:
                    shutil.copy2(source, self.original_backup / item)
                print(f"   ✅ 备份: {item}")
    
    def move_standard_architecture_files(self):
        """移动标准架构文件"""
        print("\n🔄 移动标准架构文件...")
        
        standard_dir = self.architectures_dir / "standard"
        
        file_moves = [
            # 主要入口文件
            ("main.py", "main.py"),
            ("start_backend.py", "start_backend.py"),
            ("demo_parallel_execution.py", "demo_parallel_execution.py"),
            
            # API文件
            ("api/fastapi_app.py", "api/fastapi_app.py"),
            
            # 适配器文件
            ("adapters/xdan_langgraph_adapter.py", "adapters/xdan_langgraph_adapter.py"),
            ("adapters/event_mapper.py", "adapters/event_mapper.py"),
            
            # 核心模块
            ("intelligent_tool_selector", "intelligent_tool_selector")
        ]
        
        for source_path, target_path in file_moves:
            source = self.project_root / source_path
            target = standard_dir / target_path
            
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
                print(f"   ✅ 移动: {source_path} → standard/{target_path}")
    
    def move_langgraph_native_files(self):
        """移动LangGraph原生架构文件"""
        print("\n🔄 移动LangGraph原生架构文件...")
        
        langgraph_dir = self.architectures_dir / "langgraph_native"
        
        file_moves = [
            # API文件
            ("api/fastapi_app_langgraph_native.py", "api/fastapi_app.py"),
            
            # 适配器文件
            ("adapters/langgraph_native_mcp_adapter.py", "adapters/langgraph_native_mcp_adapter.py")
        ]
        
        for source_path, target_path in file_moves:
            source = self.project_root / source_path
            target = langgraph_dir / target_path
            
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                print(f"   ✅ 移动: {source_path} → langgraph_native/{target_path}")
    
    def move_shared_components(self):
        """移动共享组件"""
        print("\n🔄 移动共享组件...")
        
        shared_moves = [
            # 配置文件
            ("requirements.txt", "requirements.txt"),
            ("requirements-api.txt", "requirements-api.txt"), 
            ("pyproject.toml", "pyproject.toml"),
            
            # 工具和数据
            ("tools", "tools"),
            ("data", "data"),
            
            # 部署配置
            ("deploy", "deploy")
        ]
        
        for source_path, target_path in shared_moves:
            source = self.project_root / source_path
            target = self.shared_dir / target_path
            
            if source.exists():
                if source.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
                print(f"   ✅ 移动: {source_path} → shared/{target_path}")
    
    def create_architecture_entry_points(self):
        """创建架构入口点"""
        print("\n🚀 创建架构入口点...")
        
        # 标准架构入口点
        standard_main = self.architectures_dir / "standard" / "run.py"
        standard_main.write_text('''#!/usr/bin/env python3
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
''')
        
        # LangGraph原生架构入口点
        langgraph_main = self.architectures_dir / "langgraph_native" / "run.py"
        langgraph_main.write_text('''#!/usr/bin/env python3
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
''')
        
        print(f"   ✅ 创建标准架构入口: standard/run.py")
        print(f"   ✅ 创建LangGraph入口: langgraph_native/run.py")
    
    def create_architecture_configs(self):
        """创建架构配置文件"""
        print("\n⚙️ 创建架构配置文件...")
        
        # 标准架构配置
        standard_config = {
            "name": "xDAN标准架构",
            "version": "1.0.0",
            "description": "基于intelligent_tool_selector的原生xDAN实现",
            "architecture": "standard_xdan",
            "features": [
                "多轮智能对话",
                "并行执行优化", 
                "138+金融工具集成",
                "智能工具选择",
                "MCP协议支持"
            ],
            "entry_points": {
                "interactive": "python run.py --mode interactive",
                "api_server": "python run.py --mode api --port 8000",
                "demo": "python run.py --mode demo"
            },
            "dependencies": self.architecture_mapping["standard"]["dependencies"],
            "performance": {
                "success_rate": "100%",
                "avg_response_time": "10.81s",
                "parallel_improvement": "40-60%"
            }
        }
        
        # LangGraph原生架构配置
        langgraph_config = {
            "name": "LangGraph原生架构",
            "version": "0.5.0",
            "description": "基于LangGraph官方SDK的原生实现",
            "architecture": "langgraph_native_mcp",
            "features": [
                "LangGraph StateGraph",
                "官方MCP集成",
                "ToolNode支持",
                "事件流处理"
            ],
            "entry_points": {
                "api_server": "python run.py --mode api --port 8001",
                "test": "python run.py --mode test"
            },
            "dependencies": self.architecture_mapping["langgraph_native"]["dependencies"],
            "performance": {
                "success_rate": "71.43%",
                "avg_response_time": "12.60s", 
                "parallel_improvement": "0%"
            },
            "status": "开发中",
            "roadmap": [
                "完善MCP工具集成",
                "实现并行执行",
                "多轮对话支持"
            ]
        }
        
        # 保存配置文件
        (self.architectures_dir / "standard" / "config.json").write_text(
            json.dumps(standard_config, ensure_ascii=False, indent=2)
        )
        (self.architectures_dir / "langgraph_native" / "config.json").write_text(
            json.dumps(langgraph_config, ensure_ascii=False, indent=2)
        )
        
        print(f"   ✅ 创建标准架构配置")
        print(f"   ✅ 创建LangGraph架构配置")
    
    def create_architecture_readme(self):
        """创建架构README文件"""
        print("\n📝 创建架构README文件...")
        
        # 标准架构README
        standard_readme = '''# xDAN标准架构

## 概述
基于intelligent_tool_selector的原生xDAN实现，提供完整的金融智能助手功能。

## 特性
- ✅ 多轮智能对话
- ✅ 并行执行优化 (40-60%性能提升)
- ✅ 138+金融工具集成
- ✅ 智能工具选择
- ✅ MCP协议支持

## 快速启动

### 交互式模式
```bash
python run.py --mode interactive
```

### API服务器
```bash
python run.py --mode api --port 8000
```

### 演示模式
```bash
python run.py --mode demo
```

## 性能指标
- 成功率: 100%
- 平均响应时间: 10.81秒
- 并行性能提升: 40-60%

## 架构组件
- `main.py` - 交互式入口
- `api/fastapi_app.py` - FastAPI服务器
- `intelligent_tool_selector/` - 核心智能选择器
- `adapters/` - 适配器层
- `demo_parallel_execution.py` - 并行执行演示

## 依赖要求
- Python 3.11+
- OpenAI API
- FastAPI
- NetworkX
'''
        
        # LangGraph原生架构README
        langgraph_readme = '''# LangGraph原生架构

## 概述
基于LangGraph官方SDK的原生实现，使用现代化的状态图工作流。

## 特性
- ✅ LangGraph StateGraph
- ✅ 官方MCP集成
- ✅ ToolNode支持
- ✅ 事件流处理
- 🚧 开发中功能

## 快速启动

### API服务器
```bash
python run.py --mode api --port 8001
```

### 测试模式
```bash
python run.py --mode test
```

## 当前状态
- 开发版本: 0.5.0
- 成功率: 71.43%
- 平均响应时间: 12.60秒

## 开发路线图
- [ ] 完善MCP工具集成
- [ ] 实现并行执行
- [ ] 多轮对话支持
- [ ] 性能优化

## 架构组件
- `api/fastapi_app.py` - FastAPI服务器
- `adapters/langgraph_native_mcp_adapter.py` - LangGraph适配器

## 依赖要求
- Python 3.11+
- LangGraph
- LangChain Core
- LangChain OpenAI
'''
        
        (self.architectures_dir / "standard" / "README.md").write_text(standard_readme)
        (self.architectures_dir / "langgraph_native" / "README.md").write_text(langgraph_readme)
        
        print(f"   ✅ 创建标准架构README")
        print(f"   ✅ 创建LangGraph架构README")
    
    def create_unified_launcher(self):
        """创建统一启动器"""
        print("\n🚀 创建统一项目启动器...")
        
        launcher_content = '''#!/usr/bin/env python3
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
            print("\\n⏹️ 停止所有服务")

if __name__ == "__main__":
    main()
'''
        
        launcher_file = self.project_root / "launch.py"
        launcher_file.write_text(launcher_content)
        launcher_file.chmod(0o755)  # 设置可执行权限
        
        print(f"   ✅ 创建统一启动器: launch.py")
    
    def update_import_paths(self):
        """更新导入路径"""
        print("\n🔧 更新导入路径...")
        
        # 这里应该实现更新各个文件中的import路径
        # 由于这个操作比较复杂，这里先提供框架
        print("   ⚠️ 导入路径更新需要手动处理:")
        print("   1. 标准架构中的相对导入")
        print("   2. LangGraph架构中的相对导入") 
        print("   3. 共享组件的导入路径")
    
    def generate_migration_report(self):
        """生成迁移报告"""
        print("\n📊 生成迁移报告...")
        
        report = {
            "migration_time": "2025-06-17",
            "original_structure": "混合架构",
            "new_structure": "分离架构",
            "architectures": {
                "standard": {
                    "location": "architectures/standard/",
                    "entry_point": "run.py",
                    "status": "已迁移"
                },
                "langgraph_native": {
                    "location": "architectures/langgraph_native/",
                    "entry_point": "run.py", 
                    "status": "已迁移"
                }
            },
            "shared_components": {
                "location": "shared/",
                "components": ["config", "utils", "tools", "data"]
            },
            "backup_location": "original_backup/",
            "next_steps": [
                "测试各架构独立运行",
                "更新CI/CD配置",
                "更新文档",
                "验证导入路径"
            ]
        }
        
        report_file = self.project_root / "migration_report.json"
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2))
        
        print(f"   ✅ 迁移报告已保存: migration_report.json")
    
    def run_migration(self):
        """执行完整的迁移过程"""
        print("🔄 开始架构分离迁移...")
        print("=" * 60)
        
        # 执行迁移步骤
        self.backup_original_structure()
        self.create_directory_structure()
        self.move_standard_architecture_files()
        self.move_langgraph_native_files()
        self.move_shared_components()
        self.create_architecture_entry_points()
        self.create_architecture_configs()
        self.create_architecture_readme()
        self.create_unified_launcher()
        self.update_import_paths()
        self.generate_migration_report()
        
        print("\n" + "=" * 60)
        print("🎉 架构分离迁移完成!")
        print("\n📋 后续步骤:")
        print("1. 测试标准架构: python launch.py standard --mode api")
        print("2. 测试LangGraph架构: python launch.py langgraph --mode api")
        print("3. 测试双架构: python launch.py both")
        print("4. 更新导入路径 (需要手动处理)")
        print("5. 更新CI/CD配置")
        print("\n📁 新的项目结构:")
        print("├── architectures/")
        print("│   ├── standard/          # 标准xDAN架构")
        print("│   └── langgraph_native/  # LangGraph原生架构")
        print("├── shared/                # 共享组件")
        print("├── original_backup/       # 原始备份")
        print("└── launch.py             # 统一启动器")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='xDAN架构分离工具')
    parser.add_argument('--project-root', 
                       default='/Users/gump_m2/CascadeProjects/xDAN-Agentic-Search-Test',
                       help='项目根目录路径')
    parser.add_argument('--dry-run', action='store_true',
                       help='模拟运行，不实际移动文件')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🧪 模拟运行模式 - 不会实际移动文件")
    
    separator = ArchitectureSeparator(args.project_root)
    
    if not args.dry_run:
        separator.run_migration()
    else:
        print("📋 将要执行的操作:")
        print("1. 备份原始结构")
        print("2. 创建新目录结构")  
        print("3. 分离标准架构文件")
        print("4. 分离LangGraph文件")
        print("5. 移动共享组件")
        print("6. 创建启动器和配置")


if __name__ == "__main__":
    main()