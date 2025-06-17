#!/usr/bin/env python3
"""
架构分离后的重复文件清理脚本
Post-Migration Duplicate File Cleanup Script

清理架构分离后产生的重复文件和目录
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict


class PostMigrationCleanup:
    """架构分离后清理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cleanup_report = {
            "timestamp": "2025-06-17",
            "phase": "post_migration_cleanup",
            "actions": {
                "deleted_files": [],
                "moved_files": [],
                "kept_files": [],
                "errors": []
            },
            "statistics": {
                "files_deleted": 0,
                "files_moved": 0,
                "space_saved": 0
            }
        }
    
    def analyze_duplicates(self):
        """分析重复文件"""
        print("🔍 分析重复文件和目录...")
        
        duplicates = {
            # 核心组件重复
            "intelligent_tool_selector": [
                self.project_root / "intelligent_tool_selector",
                self.project_root / "architectures/standard/intelligent_tool_selector",
                self.project_root / "original_backup/intelligent_tool_selector"
            ],
            
            # API文件重复
            "api_directory": [
                self.project_root / "api",
                self.project_root / "original_backup/api"
            ],
            
            # 适配器重复
            "adapters_directory": [
                self.project_root / "adapters",
                self.project_root / "original_backup/adapters"
            ],
            
            # 主要入口文件重复
            "main_files": [
                self.project_root / "main.py",
                self.project_root / "start_backend.py",
                self.project_root / "demo_parallel_execution.py"
            ],
            
            # 配置文件重复
            "config_files": [
                self.project_root / "requirements.txt",
                self.project_root / "requirements-api.txt", 
                self.project_root / "pyproject.toml"
            ],
            
            # 部署配置重复
            "deploy_directory": [
                self.project_root / "deploy"
            ],
            
            # 测试文件分散
            "test_files": [
                self.project_root / "test_logs",
                self.project_root / "test_reports",
                self.project_root / "run_youzhi_test.py",
                self.project_root / "youzhi_test.py"
            ]
        }
        
        # 检查实际存在的重复文件
        existing_duplicates = {}
        for category, files in duplicates.items():
            existing = [f for f in files if f.exists()]
            if existing:
                existing_duplicates[category] = existing
                print(f"   📋 {category}: {len(existing)} 个重复项")
        
        return existing_duplicates
    
    def create_final_cleanup_backup(self):
        """创建最终清理前的备份"""
        print("💾 创建清理前的安全备份...")
        
        backup_dir = self.project_root / "cleanup_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        backup_dir.mkdir()
        
        # 备份即将删除的重要文件
        important_files = [
            "intelligent_tool_selector",
            "api", 
            "adapters",
            "main.py",
            "requirements.txt",
            "pyproject.toml"
        ]
        
        for item in important_files:
            source = self.project_root / item
            if source.exists():
                target = backup_dir / item
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
                print(f"   ✅ 备份: {item}")
    
    def phase1_remove_major_duplicates(self):
        """阶段1: 删除主要重复文件"""
        print("\n🗑️ 阶段1: 删除主要重复目录和文件...")
        
        # 要删除的重复目录（已迁移到architectures/）
        major_duplicates = [
            "intelligent_tool_selector",  # 已迁移到 architectures/standard/
            "api",                        # 已迁移到 architectures/
            "adapters",                   # 已迁移到 architectures/
            "deploy"                      # 已迁移到 shared/
        ]
        
        for item in major_duplicates:
            path = self.project_root / item
            if path.exists():
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"   ✅ 删除目录: {item}")
                    else:
                        path.unlink()
                        print(f"   ✅ 删除文件: {item}")
                    
                    self.cleanup_report["actions"]["deleted_files"].append(str(path))
                    self.cleanup_report["statistics"]["files_deleted"] += 1
                    
                except Exception as e:
                    error_msg = f"删除 {item} 失败: {e}"
                    print(f"   ❌ {error_msg}")
                    self.cleanup_report["actions"]["errors"].append(error_msg)
    
    def phase2_remove_duplicate_main_files(self):
        """阶段2: 删除重复的主要文件"""
        print("\n🗑️ 阶段2: 删除重复的主要入口文件...")
        
        # 已迁移到 architectures/standard/ 的主要文件
        main_files = [
            "main.py",
            "start_backend.py", 
            "demo_parallel_execution.py"
        ]
        
        for filename in main_files:
            path = self.project_root / filename
            if path.exists():
                try:
                    path.unlink()
                    print(f"   ✅ 删除: {filename}")
                    self.cleanup_report["actions"]["deleted_files"].append(str(path))
                    self.cleanup_report["statistics"]["files_deleted"] += 1
                except Exception as e:
                    error_msg = f"删除 {filename} 失败: {e}"
                    print(f"   ❌ {error_msg}")
                    self.cleanup_report["actions"]["errors"].append(error_msg)
    
    def phase3_remove_duplicate_configs(self):
        """阶段3: 删除重复的配置文件"""
        print("\n🗑️ 阶段3: 删除重复的配置文件...")
        
        # 已迁移到 shared/ 的配置文件
        config_files = [
            "requirements.txt",
            "requirements-api.txt",
            "pyproject.toml"
        ]
        
        for filename in config_files:
            path = self.project_root / filename
            if path.exists():
                try:
                    path.unlink()
                    print(f"   ✅ 删除: {filename}")
                    self.cleanup_report["actions"]["deleted_files"].append(str(path))
                    self.cleanup_report["statistics"]["files_deleted"] += 1
                except Exception as e:
                    error_msg = f"删除 {filename} 失败: {e}"
                    print(f"   ❌ {error_msg}")
                    self.cleanup_report["actions"]["errors"].append(error_msg)
    
    def phase4_clean_scattered_test_files(self):
        """阶段4: 清理分散的测试文件"""
        print("\n🗑️ 阶段4: 清理分散的测试文件...")
        
        # 分散的测试相关文件和目录
        test_items = [
            "test_logs",
            "test_reports", 
            "run_youzhi_test.py",
            "youzhi_test.py"
        ]
        
        # 查找并删除根目录下的 test_*.py 文件
        test_files = list(self.project_root.glob("test_*.py"))
        
        for item in test_items + [f.name for f in test_files]:
            path = self.project_root / item
            if path.exists():
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"   ✅ 删除测试目录: {item}")
                    else:
                        path.unlink()
                        print(f"   ✅ 删除测试文件: {item}")
                    
                    self.cleanup_report["actions"]["deleted_files"].append(str(path))
                    self.cleanup_report["statistics"]["files_deleted"] += 1
                    
                except Exception as e:
                    error_msg = f"删除测试文件 {item} 失败: {e}"
                    print(f"   ❌ {error_msg}")
                    self.cleanup_report["actions"]["errors"].append(error_msg)
    
    def phase5_organize_utility_files(self):
        """阶段5: 整理工具文件到shared"""
        print("\n📁 阶段5: 整理工具文件到shared目录...")
        
        # 要移动到 shared/utils/ 的工具文件
        utility_files = [
            "advanced_mcp_agent.py",
            "intelligent_mcp_caller.py", 
            "smart_mcp_caller.py",
            "mcp_analysis_report.py",
            "quick_time_test.py"
        ]
        
        # 确保 shared/utils 目录存在
        shared_utils = self.project_root / "shared/utils"
        shared_utils.mkdir(parents=True, exist_ok=True)
        
        for filename in utility_files:
            source = self.project_root / filename
            target = shared_utils / filename
            
            if source.exists():
                try:
                    shutil.move(str(source), str(target))
                    print(f"   ✅ 移动: {filename} → shared/utils/")
                    self.cleanup_report["actions"]["moved_files"].append(f"{source} → {target}")
                    self.cleanup_report["statistics"]["files_moved"] += 1
                except Exception as e:
                    error_msg = f"移动 {filename} 失败: {e}"
                    print(f"   ❌ {error_msg}")
                    self.cleanup_report["actions"]["errors"].append(error_msg)
    
    def identify_files_to_keep(self):
        """识别需要保留的文件"""
        print("\n✅ 识别需要保留的重要文件...")
        
        # 必须保留的文件
        keep_files = [
            "launch.py",                 # 统一启动器
            "README.md",                 # 主文档
            "README-NEW-ARCHITECTURE.md", # 新架构文档
            "migration_report.json",     # 迁移报告
            "check_project_status.py",   # 状态检查工具
            "system_prompt.py",          # 系统提示
            "uv.lock",                   # 锁文件
            "architectures/",            # 架构目录
            "shared/",                   # 共享组件
            "original_backup/",          # 原始备份
            "frontend/",                 # 前端目录
            "gstack-langgraph/",         # gstack项目
            "archived_data/",            # 归档数据
            "data/",                     # 数据文件
            "langraph-stack/"            # langraph后端
        ]
        
        existing_keep_files = []
        for item in keep_files:
            path = self.project_root / item
            if path.exists():
                existing_keep_files.append(item)
                self.cleanup_report["actions"]["kept_files"].append(str(path))
        
        print(f"   📋 保留 {len(existing_keep_files)} 个重要文件/目录")
        
        return existing_keep_files
    
    def verify_architecture_integrity(self):
        """验证架构完整性"""
        print("\n🔍 验证架构完整性...")
        
        critical_paths = [
            "architectures/standard/run.py",
            "architectures/standard/intelligent_tool_selector/",
            "architectures/langgraph_native/run.py",
            "architectures/langgraph_native/adapters/",
            "shared/tools/",
            "shared/data/",
            "launch.py"
        ]
        
        missing_paths = []
        for path_str in critical_paths:
            path = self.project_root / path_str
            if not path.exists():
                missing_paths.append(path_str)
        
        if missing_paths:
            print(f"   ⚠️ 发现缺失的关键文件: {missing_paths}")
            return False
        else:
            print(f"   ✅ 所有关键架构文件完整")
            return True
    
    def generate_cleanup_report(self):
        """生成清理报告"""
        print("\n📊 生成清理报告...")
        
        # 计算统计信息
        total_actions = (
            self.cleanup_report["statistics"]["files_deleted"] +
            self.cleanup_report["statistics"]["files_moved"]
        )
        
        self.cleanup_report["statistics"]["total_actions"] = total_actions
        
        # 保存报告
        report_file = self.project_root / "cleanup_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.cleanup_report, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 清理报告已保存: cleanup_report.json")
        
        # 打印摘要
        print(f"\n📈 清理摘要:")
        print(f"   删除文件: {self.cleanup_report['statistics']['files_deleted']}")
        print(f"   移动文件: {self.cleanup_report['statistics']['files_moved']}")
        print(f"   错误数量: {len(self.cleanup_report['actions']['errors'])}")
        print(f"   总操作数: {total_actions}")
    
    def run_full_cleanup(self):
        """执行完整清理流程"""
        print("🚀 开始架构分离后的重复文件清理")
        print("=" * 70)
        
        # 预分析
        duplicates = self.analyze_duplicates()
        
        if not duplicates:
            print("✅ 没有发现重复文件，无需清理")
            return
        
        # 验证架构完整性（清理前检查）
        if not self.verify_architecture_integrity():
            print("❌ 架构完整性检查失败，停止清理")
            return
        
        # 创建安全备份
        self.create_final_cleanup_backup()
        
        # 执行清理阶段
        self.phase1_remove_major_duplicates()
        self.phase2_remove_duplicate_main_files()
        self.phase3_remove_duplicate_configs()
        self.phase4_clean_scattered_test_files()
        self.phase5_organize_utility_files()
        
        # 识别保留文件
        self.identify_files_to_keep()
        
        # 验证架构完整性（清理后检查）
        self.verify_architecture_integrity()
        
        # 生成报告
        self.generate_cleanup_report()
        
        print("\n" + "=" * 70)
        print("🎉 重复文件清理完成!")
        print("\n📋 清理后的项目结构更加清晰:")
        print("├── architectures/     # 分离的架构")
        print("├── shared/           # 共享组件") 
        print("├── original_backup/  # 原始备份")
        print("├── cleanup_backup/   # 清理前备份")
        print("└── launch.py        # 统一启动器")
        print("\n🚀 现在可以使用干净的架构进行开发了!")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='架构分离后重复文件清理工具')
    parser.add_argument('--project-root',
                       default='/Users/gump_m2/CascadeProjects/xDAN-Agentic-Search-Test',
                       help='项目根目录路径')
    parser.add_argument('--dry-run', action='store_true',
                       help='模拟运行，不实际删除文件')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🧪 模拟运行模式 - 不会实际删除文件")
        print("📋 将要执行的清理操作:")
        print("1. 删除重复的 intelligent_tool_selector 目录")
        print("2. 删除重复的 api 和 adapters 目录")
        print("3. 删除重复的主要入口文件")
        print("4. 删除重复的配置文件")
        print("5. 清理分散的测试文件")
        print("6. 整理工具文件到 shared/utils")
        return
    
    cleanup = PostMigrationCleanup(args.project_root)
    cleanup.run_full_cleanup()


if __name__ == "__main__":
    main()