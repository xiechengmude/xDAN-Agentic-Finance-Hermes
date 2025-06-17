"""
测试数据和Fixtures
Test Data and Fixtures
"""

from typing import Dict, Any, List
import pytest
from unittest.mock import Mock, AsyncMock


# 测试配置数据
TEST_CONFIG_DATA = {
    "model_name": "test-model",
    "model_url": "http://test.example.com/v1",
    "model_api_key": "test-key",
    "mcp_server_url": "http://test-mcp.example.com",
    "temperature": 0.7,
    "max_tokens": 2048,
    "max_iterations": 3
}

# 测试环境变量
TEST_ENV_VARS = {
    "OPENAI_API_KEY": "test-key",
    "OPENAI_BASE_URL": "http://test.example.com/v1",
    "MODEL_BASE_URL": "http://test.example.com/v1",
    "MODEL_NAME": "test-model",
    "MODEL_API_KEY": "test-key",
    "MCP_SERVER_URL": "http://test-mcp.example.com",
    "DEFAULT_TEMPERATURE": "0.7",
    "MAX_TOKENS": "2048",
    "MAX_ITERATIONS": "3"
}

# 模拟MCP工具响应
MOCK_MCP_TOOLS = [
    {
        "name": "test_tool_1",
        "description": "Test tool 1",
        "inputSchema": {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            }
        }
    },
    {
        "name": "test_tool_2", 
        "description": "Test tool 2",
        "inputSchema": {
            "type": "object",
            "properties": {
                "param2": {"type": "number"}
            }
        }
    }
]

# 模拟MCP工具调用响应
MOCK_TOOL_RESPONSE = {
    "success": True,
    "data": {"result": "test result"},
    "message": "Tool executed successfully"
}

# 模拟LLM响应
MOCK_LLM_RESPONSE = {
    "content": "This is a test response from the LLM",
    "additional_kwargs": {},
    "response_metadata": {}
}

# 模拟股票数据
MOCK_STOCK_DATA = {
    "ts_code": "000001.SZ",
    "symbol": "000001",
    "name": "平安银行",
    "area": "深圳",
    "industry": "银行",
    "market": "主板",
    "list_date": "19910403"
}

# 模拟交易日历数据
MOCK_TRADE_CAL_DATA = [
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
    }
]


@pytest.fixture
def mock_env_vars(monkeypatch):
    """模拟环境变量fixture"""
    for key, value in TEST_ENV_VARS.items():
        monkeypatch.setenv(key, value)
    return TEST_ENV_VARS


@pytest.fixture
def mock_config():
    """模拟配置对象fixture"""
    mock = Mock()
    mock.model_name = TEST_CONFIG_DATA["model_name"]
    mock.model_url = TEST_CONFIG_DATA["model_url"]
    mock.model_api_key = TEST_CONFIG_DATA["model_api_key"]
    mock.mcp_server_url = TEST_CONFIG_DATA["mcp_server_url"]
    mock.temperature = TEST_CONFIG_DATA["temperature"]
    mock.max_tokens = TEST_CONFIG_DATA["max_tokens"]
    mock.max_iterations = TEST_CONFIG_DATA["max_iterations"]
    return mock


@pytest.fixture
def mock_mcp_manager():
    """模拟MCP管理器fixture"""
    mock = AsyncMock()
    mock.initialize.return_value = True
    mock.get_tools_count.return_value = len(MOCK_MCP_TOOLS)
    mock.get_all_tools_info.return_value = MOCK_MCP_TOOLS
    mock.call_tool.return_value = (True, MOCK_TOOL_RESPONSE["data"], MOCK_TOOL_RESPONSE["message"])
    return mock


@pytest.fixture
def mock_llm():
    """模拟LLM fixture"""
    mock = AsyncMock()
    mock_response = Mock()
    mock_response.content = MOCK_LLM_RESPONSE["content"]
    mock_response.additional_kwargs = MOCK_LLM_RESPONSE["additional_kwargs"]
    mock_response.response_metadata = MOCK_LLM_RESPONSE["response_metadata"]
    mock.ainvoke.return_value = mock_response
    mock.invoke.return_value = mock_response
    return mock


@pytest.fixture
def sample_messages():
    """示例消息fixture"""
    from langchain_core.messages import HumanMessage, AIMessage
    
    return [
        HumanMessage(content="查询平安银行的基本信息"),
        AIMessage(content="我来帮您查询平安银行的基本信息")
    ]


@pytest.fixture
def mock_agent_state(mock_mcp_manager, sample_messages):
    """模拟Agent状态fixture"""
    from agent.state import MCPAgentState
    
    return MCPAgentState(
        messages=sample_messages,
        mcp_manager=mock_mcp_manager,
        enable_parallel=False
    )


@pytest.fixture
def mock_fastapi_client():
    """模拟FastAPI客户端fixture"""
    from fastapi.testclient import TestClient
    from agent.app import app
    
    return TestClient(app)


# 测试用例数据
TEST_CASES = {
    "configuration": [
        {
            "name": "valid_config",
            "env_vars": TEST_ENV_VARS,
            "expected": TEST_CONFIG_DATA
        },
        {
            "name": "missing_api_key",
            "env_vars": {k: v for k, v in TEST_ENV_VARS.items() if k != "OPENAI_API_KEY"},
            "expected_error": "Missing API key"
        }
    ],
    "mcp_tools": [
        {
            "name": "successful_tool_call",
            "tool_name": "test_tool_1",
            "params": {"param1": "test_value"},
            "expected_response": MOCK_TOOL_RESPONSE
        },
        {
            "name": "invalid_tool_call",
            "tool_name": "invalid_tool",
            "params": {},
            "expected_error": "Tool not found"
        }
    ],
    "llm_responses": [
        {
            "name": "simple_query",
            "input": "Hello",
            "expected_output": MOCK_LLM_RESPONSE["content"]
        },
        {
            "name": "chinese_query", 
            "input": "你好",
            "expected_output": "你好！我是xDAN智能助手"
        }
    ]
}


def create_mock_response(status_code: int = 200, json_data: Dict[str, Any] = None):
    """创建模拟HTTP响应"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    mock_response.text = str(json_data) if json_data else ""
    return mock_response


def create_mock_async_response(status_code: int = 200, json_data: Dict[str, Any] = None):
    """创建模拟异步HTTP响应"""
    mock_response = AsyncMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    mock_response.text = str(json_data) if json_data else ""
    return mock_response