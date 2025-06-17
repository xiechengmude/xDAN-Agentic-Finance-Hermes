# xDAN Agent Backend Makefile
# 提供便捷的开发和测试命令

.PHONY: help install dev test clean lint format check health_check full_test auto_test
.PHONY: unit_tests integration_tests all_tests test_coverage test_fast test_parallel
.PHONY: test_smoke test_security test_performance

# 默认目标
help:
	@echo "🚀 xDAN Agent Backend 开发工具"
	@echo ""
	@echo "📦 安装和环境:"
	@echo "  install       - 安装依赖"
	@echo "  dev          - 开发模式安装"
	@echo "  clean        - 清理缓存和临时文件"
	@echo ""
	@echo "🧪 测试命令:"
	@echo "  health_check     - 快速健康检查"
	@echo "  full_test        - 完整后端测试"
	@echo "  auto_test        - 自动化测试脚本"
	@echo ""
	@echo "🔬 单元测试:"
	@echo "  unit_tests       - 运行单元测试"
	@echo "  integration_tests - 运行集成测试"
	@echo "  all_tests        - 运行所有测试"
	@echo "  test_coverage    - 生成覆盖率报告"
	@echo "  test_fast        - 快速测试(无覆盖率)"
	@echo "  test_parallel    - 并行测试"
	@echo "  test_smoke       - 冒烟测试"
	@echo "  test_security    - 安全测试"
	@echo "  test_performance - 性能测试"
	@echo ""
	@echo "🔧 代码质量:"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  check        - 完整检查"
	@echo ""
	@echo "🚀 运行:"
	@echo "  run          - 启动应用"
	@echo "  dev_run      - 开发模式运行"

# 安装和环境管理
install:
	@echo "📦 安装依赖..."
	@uv sync

dev:
	@echo "🔧 开发模式安装..."
	@uv sync --dev
	@echo "✅ 开发环境已准备就绪"

clean:
	@echo "🧹 清理缓存和临时文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml test-results.xml
	@rm -rf test-report.json
	@echo "✅ 清理完成"

# 传统测试命令（保持兼容性）
health_check:
	@echo "🏥 执行快速健康检查..."
	@python quick_health_check.py

full_test:
	@echo "🧪 执行完整测试..."
	@python test_full_backend_pipeline.py

auto_test:
	@echo "🤖 执行自动化测试..."
	@chmod +x run_full_test.sh
	@./run_full_test.sh

# 单元测试命令
unit_tests:
	@echo "🧪 运行单元测试..."
	@python run_unit_tests.py --type unit

integration_tests:
	@echo "🔗 运行集成测试..."
	@python run_unit_tests.py --type integration

all_tests:
	@echo "🚀 运行所有测试..."
	@python run_unit_tests.py --type all

test_coverage:
	@echo "📊 生成测试覆盖率报告..."
	@python run_unit_tests.py --type all --format detailed
	@echo "📄 覆盖率报告: htmlcov/index.html"

test_fast:
	@echo "⚡ 快速测试 (无覆盖率)..."
	@python run_unit_tests.py --type unit --no-coverage --format simple

test_parallel:
	@echo "🔀 并行测试..."
	@python run_unit_tests.py --type all --parallel

test_smoke:
	@echo "💨 冒烟测试..."
	@python run_unit_tests.py --markers smoke --format simple

test_security:
	@echo "🔒 安全测试..."
	@python run_unit_tests.py --markers security

test_performance:
	@echo "⚡ 性能测试..."
	@python run_unit_tests.py --markers performance

# 代码质量
lint:
	@echo "🔍 运行代码检查..."
	@uv run ruff check src/ tests/ || echo "⚠️  请安装 ruff: uv add --dev ruff"

format:
	@echo "🎨 格式化代码..."
	@uv run ruff format src/ tests/ || echo "⚠️  请安装 ruff: uv add --dev ruff"
	@uv run ruff check --fix src/ tests/ || echo "⚠️  请安装 ruff: uv add --dev ruff"

check: lint test_fast
	@echo "✅ 代码检查完成"

# 运行应用
run:
	@echo "🚀 启动应用..."
	@uv run python -m agent.app

dev_run:
	@echo "🔧 开发模式运行..."
	@uv run uvicorn agent.app:app --reload --host 0.0.0.0 --port 8000

# 测试环境检查
test_env:
	@echo "🔧 检查测试环境..."
	@python -c "import pytest; print('✅ pytest 可用')" || echo "❌ pytest 未安装"
	@python -c "import coverage; print('✅ coverage 可用')" || echo "❌ coverage 未安装"
	@python -c "import pytest_asyncio; print('✅ pytest-asyncio 可用')" || echo "❌ pytest-asyncio 未安装"
	@echo "📁 测试目录结构:"
	@find tests -name "*.py" | head -10

# 生成测试报告
test_report:
	@echo "📊 生成完整测试报告..."
	@python run_unit_tests.py --type all --format json
	@echo "📄 报告文件: test-report.json"

# CI/CD 相关
ci_test:
	@echo "🤖 CI 测试流程..."
	@make clean
	@make test_env
	@make test_fast
	@make test_coverage

# 开发者工具
watch_tests:
	@echo "👀 监控测试..."
	@echo "⚠️  需要安装 pytest-watch: uv add --dev pytest-watch"
	@uv run ptw tests/ || echo "请先安装: uv add --dev pytest-watch"

debug_test:
	@echo "🐛 调试模式测试..."
	@python run_unit_tests.py --type unit --format detailed -v

# 文档生成
docs:
	@echo "📚 生成文档..."
	@echo "⚠️  文档生成功能待实现"

# 版本信息
version:
	@echo "📋 版本信息:"
	@python --version
	@uv --version
	@echo "🧪 测试框架:"
	@python -c "import pytest; print(f'pytest {pytest.__version__}')" 2>/dev/null || echo "pytest 未安装"
	@python -c "import coverage; print(f'coverage {coverage.__version__}')" 2>/dev/null || echo "coverage 未安装" 