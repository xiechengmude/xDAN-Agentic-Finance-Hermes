# xDAN Agent 单元测试指南

## 📋 概述

本文档提供 xDAN Agent 后端系统完整的单元测试框架使用指南。我们的测试框架覆盖了配置系统、MCP工具、FastAPI应用以及完整的集成测试。

## 🏗️ 测试架构

### 测试目录结构
```
tests/
├── __init__.py                     # 测试包初始化
├── conftest.py                     # pytest全局配置
├── pytest.ini                     # pytest配置文件
├── fixtures/                      # 测试数据和fixtures
│   ├── __init__.py
│   └── test_data.py               # 模拟数据和fixtures
├── unit/                          # 单元测试
│   ├── __init__.py
│   ├── test_configuration.py      # 配置系统测试
│   ├── test_mcp_tools.py          # MCP工具测试
│   ├── test_fastapi_app.py        # FastAPI应用测试
│   └── test_testing_scripts.py    # 测试脚本测试
└── integration/                   # 集成测试
    ├── __init__.py
    └── test_full_integration.py   # 完整集成测试
```

### 测试分类

#### 🔬 单元测试 (Unit Tests)
- **配置系统测试**: 环境变量处理、配置验证、默认值设置
- **MCP工具测试**: 工具管理器、连接处理、工具调用
- **FastAPI应用测试**: API端点、错误处理、CORS配置
- **测试脚本测试**: 健康检查、全链路测试脚本

#### 🔗 集成测试 (Integration Tests)
- **系统集成**: 组件间交互测试
- **性能测试**: 并发处理、内存使用
- **安全测试**: 输入验证、URL验证
- **可靠性测试**: 超时处理、错误恢复

## 🚀 快速开始

### 1. 安装依赖
```bash
# 安装测试依赖
make dev
# 或者直接使用uv
uv add --dev pytest pytest-asyncio pytest-cov pytest-xdist coverage
```

### 2. 运行测试
```bash
# 查看所有可用命令
make help

# 快速单元测试
make test_fast

# 完整测试覆盖率
make test_coverage

# 运行特定类型测试
make unit_tests           # 只运行单元测试
make integration_tests    # 只运行集成测试
make all_tests           # 运行所有测试
```

### 3. 查看结果
```bash
# 查看覆盖率报告
open htmlcov/index.html

# 查看测试结果XML
cat test-results.xml

# 查看JSON报告
cat test-report.json
```

## 📊 测试命令详解

### 基础测试命令

| 命令 | 功能 | 用途 |
|------|------|------|
| `make unit_tests` | 运行单元测试 | 开发过程中快速验证 |
| `make integration_tests` | 运行集成测试 | 验证组件集成 |
| `make all_tests` | 运行所有测试 | 完整测试验证 |
| `make test_fast` | 快速测试(无覆盖率) | 快速反馈 |
| `make test_coverage` | 生成覆盖率报告 | 代码质量评估 |

### 高级测试命令

| 命令 | 功能 | 用途 |
|------|------|------|
| `make test_parallel` | 并行测试 | 提高测试速度 |
| `make test_smoke` | 冒烟测试 | 基本功能验证 |
| `make test_security` | 安全测试 | 安全漏洞检测 |
| `make test_performance` | 性能测试 | 性能基准测试 |
| `make ci_test` | CI测试流程 | 持续集成 |

### 开发者工具

| 命令 | 功能 | 用途 |
|------|------|------|
| `make debug_test` | 调试模式测试 | 问题排查 |
| `make test_env` | 检查测试环境 | 环境验证 |
| `make watch_tests` | 监控测试 | 实时测试反馈 |
| `make test_report` | 生成JSON报告 | 详细测试分析 |

## 🧪 使用pytest直接运行

### 基本用法
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_configuration.py

# 运行特定测试类
pytest tests/unit/test_configuration.py::TestMCPConfiguration

# 运行特定测试方法
pytest tests/unit/test_configuration.py::TestMCPConfiguration::test_from_runnable_config_with_valid_env

# 详细输出
pytest -v

# 显示最慢的10个测试
pytest --durations=10
```

### 使用标记过滤
```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"

# 只运行异步测试
pytest -m async_test

# 组合标记
pytest -m "unit and not slow"
```

### 覆盖率相关
```bash
# 生成覆盖率报告
pytest --cov=src/agent --cov-report=html

# 只显示缺失覆盖的行
pytest --cov=src/agent --cov-report=term-missing

# 设置覆盖率阈值
pytest --cov=src/agent --cov-fail-under=80
```

### 并行运行
```bash
# 自动检测CPU核心数并行运行
pytest -n auto

# 指定进程数
pytest -n 4
```

## 📝 编写测试

### 测试文件命名规范
- 单元测试: `test_<module_name>.py`
- 集成测试: `test_<feature>_integration.py`
- 测试类: `Test<ClassName>`
- 测试方法: `test_<functionality>`

### 基本测试结构
```python
"""
模块测试
Module Tests
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from agent.your_module import YourClass
from tests.fixtures.test_data import TEST_DATA


class TestYourClass:
    """YourClass 的单元测试"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        # Arrange
        instance = YourClass()
        
        # Act
        result = instance.method()
        
        # Assert
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """测试异步功能"""
        with patch('agent.your_module.external_dependency') as mock_dep:
            mock_dep.return_value = "mocked_result"
            
            instance = YourClass()
            result = await instance.async_method()
            
            assert result == "mocked_result"
    
    def test_error_handling(self):
        """测试错误处理"""
        instance = YourClass()
        
        with pytest.raises(ValueError):
            instance.method_that_should_raise()
    
    @pytest.mark.parametrize("input_value,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
        ("input3", "output3"),
    ])
    def test_parametrized(self, input_value, expected):
        """参数化测试"""
        instance = YourClass()
        result = instance.process(input_value)
        assert result == expected
```

### 使用Fixtures
```python
@pytest.fixture
def mock_config():
    """模拟配置对象"""
    config = Mock()
    config.api_key = "test-key"
    config.base_url = "http://test.example.com"
    return config

def test_with_fixture(mock_config):
    """使用fixture的测试"""
    instance = YourClass(mock_config)
    assert instance.config.api_key == "test-key"
```

### 异步测试
```python
@pytest.mark.asyncio
async def test_async_operation():
    """异步操作测试"""
    async with AsyncClient() as client:
        response = await client.get("/api/endpoint")
        assert response.status_code == 200
```

## 🔧 配置和自定义

### pytest.ini 配置
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --tb=short --cov=src/agent
markers =
    unit: 单元测试
    integration: 集成测试
    slow: 慢速测试
    network: 需要网络的测试
```

### conftest.py 全局配置
- 全局fixtures
- 测试环境设置
- 自动标记
- 自定义断言

## 📈 覆盖率分析

### 覆盖率目标
- **总体覆盖率**: ≥ 80%
- **单元测试覆盖率**: ≥ 90%
- **关键模块覆盖率**: ≥ 95%

### 覆盖率报告
```bash
# 生成HTML报告
make test_coverage
open htmlcov/index.html

# 命令行报告
pytest --cov=src/agent --cov-report=term-missing

# XML报告(用于CI)
pytest --cov=src/agent --cov-report=xml
```

### 排除覆盖率检查
```python
def debug_function():  # pragma: no cover
    """调试函数，不计入覆盖率"""
    pass
```

## 🚨 常见问题和解决方案

### 1. 导入错误
**问题**: `ModuleNotFoundError: No module named 'agent'`

**解决方案**:
```bash
# 确保在项目根目录
cd langraph-stack/backend

# 检查PYTHONPATH
export PYTHONPATH=$PWD/src:$PYTHONPATH

# 或使用uv运行
uv run pytest
```

### 2. 异步测试失败
**问题**: `RuntimeError: asyncio.run() cannot be called from a running event loop`

**解决方案**:
```python
# 使用 pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### 3. Mock不生效
**问题**: Mock对象没有被正确使用

**解决方案**:
```python
# 确保patch路径正确
with patch('tests.unit.test_module.external_function') as mock_func:
    # 而不是
    # with patch('external_module.external_function') as mock_func:
    pass
```

### 4. 环境变量问题
**问题**: 测试中环境变量冲突

**解决方案**:
```python
def test_with_env(monkeypatch):
    monkeypatch.setenv("TEST_VAR", "test_value")
    # 测试代码
```

### 5. 数据库连接问题
**问题**: 测试中需要数据库连接

**解决方案**:
```python
@pytest.fixture
def mock_db():
    with patch('agent.database.get_connection') as mock_conn:
        mock_conn.return_value = Mock()
        yield mock_conn
```

## 🔄 CI/CD 集成

### GitHub Actions 示例
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install uv
      run: pip install uv
    
    - name: Install dependencies
      run: uv sync --dev
    
    - name: Run tests
      run: make ci_test
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 本地CI测试
```bash
# 模拟CI环境测试
make ci_test

# 清理并完整测试
make clean && make test_coverage
```

## 📚 最佳实践

### 1. 测试命名
- 使用描述性名称
- 遵循 `test_<what>_<when>_<expected>` 模式
- 中文注释说明测试目的

### 2. 测试结构
- 使用 Arrange-Act-Assert 模式
- 每个测试只验证一个行为
- 保持测试简单和独立

### 3. Mock使用
- 只mock外部依赖
- 使用有意义的mock返回值
- 验证mock的调用

### 4. 异步测试
- 使用 `@pytest.mark.asyncio`
- 正确处理异步上下文
- 避免阻塞操作

### 5. 数据管理
- 使用fixtures提供测试数据
- 避免硬编码测试数据
- 清理测试产生的数据

## 🎯 性能优化

### 测试速度优化
```bash
# 并行运行
make test_parallel

# 只运行失败的测试
pytest --lf

# 跳过慢速测试
pytest -m "not slow"

# 使用缓存
pytest --cache-clear  # 清理缓存
```

### 内存优化
- 使用轻量级mock
- 及时清理大对象
- 避免内存泄漏

## 📊 报告和分析

### 测试报告类型
1. **简单报告**: 快速查看测试状态
2. **详细报告**: 包含执行时间和覆盖率
3. **JSON报告**: 机器可读的详细数据
4. **HTML覆盖率报告**: 可视化覆盖率分析

### 分析工具
- pytest-html: HTML测试报告
- pytest-cov: 覆盖率分析
- pytest-benchmark: 性能基准测试
- pytest-xdist: 并行测试

## 🔮 进阶功能

### 自定义标记
```python
# 添加自定义标记
@pytest.mark.api_test
def test_api_endpoint():
    pass

# 运行自定义标记的测试
pytest -m api_test
```

### 参数化测试
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4), 
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

### 测试依赖
```python
@pytest.mark.dependency()
def test_setup():
    pass

@pytest.mark.dependency(depends=["test_setup"])
def test_main():
    pass
```

## 📞 获取帮助

### 命令帮助
```bash
# Makefile帮助
make help

# pytest帮助
pytest --help

# 测试运行器帮助
python run_unit_tests.py --help
```

### 调试技巧
```bash
# 进入调试模式
pytest --pdb

# 详细输出
pytest -vv

# 显示本地变量
pytest --tb=long

# 只运行最后失败的测试
pytest --lf
```

---

**📝 注意**: 本指南会随着项目发展持续更新。如有问题或建议，请提交 Issue 或 Pull Request。 