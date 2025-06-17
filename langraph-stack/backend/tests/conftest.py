"""
Pytest配置文件
Global test configuration and fixtures
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """自动设置测试环境"""
    # 设置测试环境变量
    test_env_vars = {
        "OPENAI_API_KEY": "test-key-123",
        "OPENAI_BASE_URL": "http://test.example.com/v1",
        "MODEL_BASE_URL": "http://test.example.com/v1",
        "MODEL_NAME": "test-model",
        "MODEL_API_KEY": "test-key-123",
        "MCP_SERVER_URL": "http://test-mcp.example.com:7223/sse",
        "DEFAULT_TEMPERATURE": "0.1",
        "MAX_TOKENS": "2048",
        "MAX_ITERATIONS": "3"
    }
    
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def temp_env_file(tmp_path):
    """创建临时环境文件"""
    env_file = tmp_path / ".env"
    env_content = """
# 测试环境配置
OPENAI_API_KEY=test-key-123
OPENAI_BASE_URL=http://test.example.com/v1
MODEL_BASE_URL=http://test.example.com/v1
MODEL_NAME=test-model
MODEL_API_KEY=test-key-123
MCP_SERVER_URL=http://test-mcp.example.com:7223/sse
DEFAULT_TEMPERATURE=0.1
MAX_TOKENS=2048
MAX_ITERATIONS=3
"""
    env_file.write_text(env_content.strip())
    return env_file


@pytest.fixture
def mock_http_client():
    """模拟HTTP客户端"""
    client = Mock()
    
    # 模拟成功响应
    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = {"status": "success"}
    success_response.text = '{"status": "success"}'
    
    client.get.return_value = success_response
    client.post.return_value = success_response
    
    return client


@pytest.fixture
def mock_async_http_client():
    """模拟异步HTTP客户端"""
    client = AsyncMock()
    
    # 模拟成功响应
    success_response = AsyncMock()
    success_response.status_code = 200
    success_response.json.return_value = {"status": "success"}
    success_response.text = '{"status": "success"}'
    
    client.get.return_value = success_response
    client.post.return_value = success_response
    
    return client


@pytest.fixture
def sample_stock_data():
    """示例股票数据"""
    return {
        "ts_code": "000001.SZ",
        "symbol": "000001",
        "name": "平安银行",
        "area": "深圳",
        "industry": "银行",
        "market": "主板",
        "list_date": "19910403",
        "curr_type": "CNY",
        "list_status": "L"
    }


@pytest.fixture
def sample_trade_calendar():
    """示例交易日历数据"""
    return [
        {
            "exchange": "SSE",
            "cal_date": "20240101",
            "is_open": 0,
            "pretrade_date": "20231229"
        },
        {
            "exchange": "SSE",
            "cal_date": "20240102", 
            "is_open": 1,
            "pretrade_date": "20240101"
        },
        {
            "exchange": "SZSE",
            "cal_date": "20240102",
            "is_open": 1,
            "pretrade_date": "20240101"
        }
    ]


@pytest.fixture
def mock_logger():
    """模拟日志记录器"""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


# 测试标记定义
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 标记单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 标记慢速测试"
    )
    config.addinivalue_line(
        "markers", "network: 标记需要网络的测试"
    )
    config.addinivalue_line(
        "markers", "async_test: 标记异步测试"
    )


# 测试收集配置
def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    for item in items:
        # 自动为异步测试添加标记
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.async_test)
        
        # 为集成测试添加慢速标记
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # 为需要网络的测试添加标记
        if any(keyword in item.name.lower() for keyword in ["http", "client", "request", "api"]):
            item.add_marker(pytest.mark.network)


# 跳过条件
def pytest_runtest_setup(item):
    """测试运行前设置"""
    # 如果没有网络连接，跳过网络测试
    if "network" in [mark.name for mark in item.iter_markers()]:
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=1)
        except OSError:
            pytest.skip("网络连接不可用")


# 自定义断言
def pytest_assertrepr_compare(op, left, right):
    """自定义断言错误消息"""
    if isinstance(left, dict) and isinstance(right, dict) and op == "==":
        return [
            "字典比较失败:",
            f"左侧: {left}",
            f"右侧: {right}",
            "差异:",
            *[f"  {key}: {left.get(key)} != {right.get(key)}" 
              for key in set(left.keys()) | set(right.keys())
              if left.get(key) != right.get(key)]
        ] 