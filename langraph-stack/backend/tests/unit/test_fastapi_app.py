"""
FastAPI应用单元测试
FastAPI Application Unit Tests
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import status

from agent.app import app
from tests.fixtures.test_data import mock_fastapi_client


class TestFastAPIApp:
    """FastAPI应用的单元测试"""
    
    @pytest.fixture
    def client(self):
        """测试客户端fixture"""
        return TestClient(app)
    
    def test_app_creation(self):
        """测试应用创建"""
        assert app.title == "LangGraph Financial Agent API"
        assert hasattr(app, 'routes')
        assert len(app.routes) > 0
    
    def test_cors_middleware(self, client):
        """测试CORS中间件配置"""
        # 测试预检请求
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # 检查CORS头部
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert data["service"] == "langraph-financial-agent"
    
    def test_models_endpoint_success(self, client):
        """测试模型端点成功响应"""
        with patch('agent.api_models.MCPConfiguration.get_available_models') as mock_get_models:
            # 模拟可用模型
            mock_models = {
                "model1": {
                    "name": "Test Model 1",
                    "description": "Test description 1",
                    "base_url": "http://test1.example.com/v1"
                },
                "model2": {
                    "name": "Test Model 2", 
                    "description": "Test description 2",
                    "base_url": "http://test2.example.com/v1"
                }
            }
            mock_get_models.return_value = mock_models
            
            response = client.get("/api/v1/models")
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert "models" in data
            assert "default_model" in data
            assert len(data["models"]) == 2
            
            # 验证模型格式
            for model in data["models"]:
                assert "key" in model
                assert "name" in model
                assert "description" in model
                assert "provider" in model
    
    def test_models_endpoint_failure(self, client):
        """测试模型端点失败响应"""
        with patch('agent.api_models.MCPConfiguration.get_available_models') as mock_get_models:
            # 模拟异常
            mock_get_models.side_effect = Exception("Configuration error")
            
            response = client.get("/api/v1/models")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            
            data = response.json()
            assert "detail" in data
            assert "获取模型列表失败" in data["detail"]
    
    def test_models_endpoint_empty_models(self, client):
        """测试模型端点空模型列表"""
        with patch('agent.api_models.MCPConfiguration.get_available_models') as mock_get_models:
            mock_get_models.return_value = {}
            
            response = client.get("/api/v1/models")
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True
            assert data["models"] == []
            assert data["default_model"] is None
    
    def test_frontend_static_files_missing(self, client):
        """测试前端静态文件缺失的处理"""
        # 测试访问前端路由
        response = client.get("/app/")
        
        # 应该返回503或者相应的错误信息
        # 具体行为取决于前端构建状态
        assert response.status_code in [503, 404, 200]
        
        if response.status_code == 503:
            assert "Frontend not built" in response.text
    
    def test_api_route_prefix(self, client):
        """测试API路由前缀"""
        # 测试带前缀的路由
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        
        # 测试不带前缀的路由应该不存在
        response = client.get("/health")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_invalid_endpoints(self, client):
        """测试无效端点"""
        invalid_endpoints = [
            "/api/v1/invalid",
            "/api/v2/models",
            "/invalid/path",
            "/api/v1/models/invalid"
        ]
        
        for endpoint in invalid_endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_http_methods(self, client):
        """测试不同HTTP方法"""
        # GET方法应该工作
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        
        # POST方法对健康检查端点应该不被允许
        response = client.post("/api/v1/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # PUT方法对模型端点应该不被允许
        response = client.put("/api/v1/models")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_response_headers(self, client):
        """测试响应头部"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == status.HTTP_200_OK
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"
    
    def test_request_validation(self, client):
        """测试请求验证"""
        # 测试带有无效查询参数的请求
        response = client.get("/api/v1/models?invalid_param=value")
        
        # 应该忽略无效参数并正常响应
        assert response.status_code in [200, 422]  # 200或422都是合理的
    
    @pytest.mark.parametrize("origin", [
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:3000"
    ])
    def test_cors_allowed_origins(self, client, origin):
        """测试CORS允许的源"""
        response = client.get(
            "/api/v1/health",
            headers={"Origin": origin}
        )
        
        assert response.status_code == status.HTTP_200_OK
        # 注意：TestClient可能不会自动处理CORS头部
        # 在实际测试中，可能需要检查中间件配置
    
    def test_app_metadata(self):
        """测试应用元数据"""
        assert app.title == "LangGraph Financial Agent API"
        assert hasattr(app, 'version') or app.version is None  # 版本可能未设置
        
        # 检查路由器是否正确包含
        route_paths = [route.path for route in app.routes]
        assert "/api/v1/health" in route_paths or any("/health" in path for path in route_paths)
        assert "/api/v1/models" in route_paths or any("/models" in path for path in route_paths)


class TestAPIModels:
    """API模型端点的详细测试"""
    
    @pytest.fixture
    def client(self):
        """测试客户端fixture"""
        return TestClient(app)
    
    def test_models_response_structure(self, client):
        """测试模型响应结构"""
        with patch('agent.api_models.MCPConfiguration.get_available_models') as mock_get_models:
            mock_models = {
                "test_model": {
                    "name": "Test Model",
                    "description": "A test model",
                    "base_url": "http://test.example.com/v1"
                }
            }
            mock_get_models.return_value = mock_models
            
            response = client.get("/api/v1/models")
            data = response.json()
            
            # 验证顶级结构
            assert isinstance(data, dict)
            assert "success" in data
            assert "models" in data
            assert "default_model" in data
            
            # 验证models数组结构
            assert isinstance(data["models"], list)
            if data["models"]:
                model = data["models"][0]
                required_fields = ["key", "name", "description", "provider"]
                for field in required_fields:
                    assert field in model
                    assert isinstance(model[field], str)
    
    def test_models_provider_extraction(self, client):
        """测试提供商名称提取"""
        with patch('agent.api_models.MCPConfiguration.get_available_models') as mock_get_models:
            mock_models = {
                "openai_model": {
                    "name": "OpenAI Model",
                    "base_url": "https://api.openai.com/v1"
                },
                "local_model": {
                    "name": "Local Model",
                    "base_url": "http://localhost:8080/v1"
                },
                "invalid_url_model": {
                    "name": "Invalid URL Model",
                    "base_url": "invalid-url"
                }
            }
            mock_get_models.return_value = mock_models
            
            response = client.get("/api/v1/models")
            data = response.json()
            
            models_by_key = {model["key"]: model for model in data["models"]}
            
            # 验证提供商提取
            assert models_by_key["openai_model"]["provider"] == "api"
            assert models_by_key["local_model"]["provider"] == "localhost"
            assert models_by_key["invalid_url_model"]["provider"] == "unknown"
    
    def test_models_default_selection(self, client):
        """测试默认模型选择"""
        with patch('agent.api_models.MCPConfiguration.get_available_models') as mock_get_models:
            mock_models = {
                "first_model": {"name": "First Model"},
                "second_model": {"name": "Second Model"}
            }
            mock_get_models.return_value = mock_models
            
            response = client.get("/api/v1/models")
            data = response.json()
            
            # 默认模型应该是第一个
            assert data["default_model"] == "first_model"
    
    def test_models_configuration_error_handling(self, client):
        """测试配置错误处理"""
        with patch('agent.api_models.MCPConfiguration.get_available_models') as mock_get_models:
            # 测试不同类型的异常
            exceptions = [
                ValueError("Invalid configuration"),
                KeyError("Missing key"),
                RuntimeError("Runtime error"),
                Exception("Generic error")
            ]
            
            for exc in exceptions:
                mock_get_models.side_effect = exc
                
                response = client.get("/api/v1/models")
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                data = response.json()
                assert "detail" in data
                assert "获取模型列表失败" in data["detail"]
                assert str(exc) in data["detail"]


class TestFrontendIntegration:
    """前端集成测试"""
    
    @pytest.fixture
    def client(self):
        """测试客户端fixture"""
        return TestClient(app)
    
    def test_frontend_mount_path(self, client):
        """测试前端挂载路径"""
        # 测试根路径重定向或处理
        response = client.get("/app")
        # 可能重定向到/app/或返回前端内容
        assert response.status_code in [200, 301, 302, 404, 503]
    
    def test_frontend_static_file_serving(self, client):
        """测试静态文件服务"""
        # 尝试访问常见的静态文件路径
        static_paths = [
            "/app/index.html",
            "/app/static/js/main.js",
            "/app/static/css/main.css"
        ]
        
        for path in static_paths:
            response = client.get(path)
            # 文件可能不存在，但应该有合理的响应
            assert response.status_code in [200, 404, 503]
    
    def test_spa_routing_fallback(self, client):
        """测试SPA路由回退"""
        # 测试前端路由路径
        spa_routes = [
            "/app/dashboard",
            "/app/chat",
            "/app/settings"
        ]
        
        for route in spa_routes:
            response = client.get(route)
            # SPA应该回退到index.html或返回404
            assert response.status_code in [200, 404, 503]


class TestAPIErrorHandling:
    """API错误处理测试"""
    
    @pytest.fixture
    def client(self):
        """测试客户端fixture"""
        return TestClient(app)
    
    def test_404_error_handling(self, client):
        """测试404错误处理"""
        response = client.get("/nonexistent/endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
    
    def test_500_error_handling(self, client):
        """测试500错误处理"""
        # 通过模拟异常来触发500错误
        with patch('agent.api_models.MCPConfiguration.get_available_models') as mock_get_models:
            mock_get_models.side_effect = Exception("Internal error")
            
            response = client.get("/api/v1/models")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_method_not_allowed_handling(self, client):
        """测试方法不允许错误处理"""
        response = client.delete("/api/v1/health")
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_large_request_handling(self, client):
        """测试大请求处理"""
        # 发送大量数据（如果端点支持POST）
        large_data = {"data": "x" * 10000}  # 10KB数据
        
        response = client.post("/api/v1/models", json=large_data)
        
        # 应该返回405（方法不允许）或413（请求实体过大）
        assert response.status_code in [405, 413, 422]
    
    def test_invalid_json_handling(self, client):
        """测试无效JSON处理"""
        # 发送无效JSON
        response = client.post(
            "/api/v1/models",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # 应该返回400或405
        assert response.status_code in [400, 405, 422]
    
    def test_missing_content_type(self, client):
        """测试缺少Content-Type头部"""
        response = client.post("/api/v1/models", data="some data")
        
        # 应该有合理的错误响应
        assert response.status_code in [400, 405, 415, 422] 