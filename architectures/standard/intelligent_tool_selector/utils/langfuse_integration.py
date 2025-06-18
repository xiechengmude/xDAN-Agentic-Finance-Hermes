"""
Langfuse集成模块
提供观测、追踪和监控功能
"""

import os
import functools
from typing import Any, Callable, Optional, Dict
from datetime import datetime
import asyncio

try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("⚠️ Langfuse未安装，观测功能将被禁用")

class LangfuseIntegration:
    """Langfuse集成管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.enabled = False
            self.client = None
            self._initialize()
            self.__class__._initialized = True
    
    def _initialize(self):
        """初始化Langfuse客户端"""
        if not LANGFUSE_AVAILABLE:
            return
        
        # 从环境变量读取配置
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        # 调试输出
        print(f"🔍 Langfuse配置:")
        print(f"  - Host: {host}")
        print(f"  - Public Key: {public_key[:10]}..." if public_key else "  - Public Key: None")
        print(f"  - Secret Key: {secret_key[:10]}..." if secret_key else "  - Secret Key: None")
        
        if public_key and secret_key and public_key != "your_public_key_here":
            try:
                # 首先尝试正常连接
                try:
                    self.client = Langfuse(
                        public_key=public_key,
                        secret_key=secret_key,
                        host=host
                    )
                    self.client.auth_check()
                    self.enabled = True
                    print("✅ Langfuse集成已启用")
                except Exception as ssl_error:
                    if "SSL" in str(ssl_error) or "certificate" in str(ssl_error).lower():
                        print(f"⚠️ SSL错误，尝试禁用SSL验证: {ssl_error}")
                        # 尝试禁用SSL验证
                        self.client = Langfuse(
                            public_key=public_key,
                            secret_key=secret_key,
                            host=host,
                            httpx_client_kwargs={"verify": False}
                        )
                        self.client.auth_check()
                        self.enabled = True
                        print("✅ Langfuse集成已启用（已禁用SSL验证）")
                    else:
                        raise
            except Exception as e:
                print(f"⚠️ Langfuse初始化失败: {e}")
                self.enabled = False
        else:
            print("ℹ️ Langfuse配置未设置，观测功能已禁用")
    
    def trace_async(self, name: str = None, metadata: Dict[str, Any] = None):
        """异步函数装饰器"""
        def decorator(func: Callable):
            if not self.enabled:
                return func
            
            @functools.wraps(func)
            @observe(name=name or func.__name__)
            async def wrapper(*args, **kwargs):
                # 更新trace元数据
                if metadata:
                    langfuse_context.update_current_trace(
                        metadata=metadata,
                        tags=metadata.get("tags", [])
                    )
                
                # 记录函数开始
                start_time = datetime.now()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # 记录成功
                    langfuse_context.update_current_observation(
                        metadata={
                            "status": "success",
                            "duration": (datetime.now() - start_time).total_seconds()
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    # 记录错误
                    langfuse_context.update_current_observation(
                        metadata={
                            "status": "error",
                            "error": str(e),
                            "duration": (datetime.now() - start_time).total_seconds()
                        }
                    )
                    raise
            
            return wrapper
        return decorator
    
    def trace_sync(self, name: str = None, metadata: Dict[str, Any] = None):
        """同步函数装饰器"""
        def decorator(func: Callable):
            if not self.enabled:
                return func
            
            @functools.wraps(func)
            @observe(name=name or func.__name__)
            def wrapper(*args, **kwargs):
                # 更新trace元数据
                if metadata:
                    langfuse_context.update_current_trace(
                        metadata=metadata,
                        tags=metadata.get("tags", [])
                    )
                
                # 记录函数开始
                start_time = datetime.now()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # 记录成功
                    langfuse_context.update_current_observation(
                        metadata={
                            "status": "success",
                            "duration": (datetime.now() - start_time).total_seconds()
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    # 记录错误
                    langfuse_context.update_current_observation(
                        metadata={
                            "status": "error",
                            "error": str(e),
                            "duration": (datetime.now() - start_time).total_seconds()
                        }
                    )
                    raise
            
            return wrapper
        return decorator
    
    def log_generation(self, 
                      input_text: str,
                      output_text: str,
                      model_name: str,
                      metadata: Optional[Dict[str, Any]] = None):
        """记录LLM生成"""
        if not self.enabled:
            return
        
        try:
            generation = self.client.generation(
                name="llm_generation",
                input=input_text,
                output=output_text,
                model=model_name,
                metadata=metadata or {},
                completion_start_time=datetime.now()
            )
            return generation
        except Exception as e:
            print(f"⚠️ Langfuse记录失败: {e}")
    
    def log_tool_call(self,
                     tool_name: str,
                     parameters: Dict[str, Any],
                     result: Any,
                     success: bool,
                     duration: float):
        """记录工具调用"""
        if not self.enabled:
            return
        
        try:
            if hasattr(langfuse_context, 'update_current_observation'):
                langfuse_context.update_current_observation(
                    name=f"tool_call_{tool_name}",
                    metadata={
                        "tool_name": tool_name,
                        "parameters": parameters,
                        "success": success,
                        "duration": duration,
                        "result_preview": str(result)[:200] if result else None
                    }
                )
        except Exception as e:
            print(f"⚠️ Langfuse工具调用记录失败: {e}")
    
    def create_score(self,
                    name: str,
                    value: float,
                    trace_id: Optional[str] = None,
                    comment: Optional[str] = None):
        """创建评分"""
        if not self.enabled or not self.client:
            return
        
        try:
            self.client.score(
                name=name,
                value=value,
                trace_id=trace_id,
                comment=comment
            )
        except Exception as e:
            print(f"⚠️ Langfuse评分创建失败: {e}")
    
    def flush(self):
        """刷新待发送的事件"""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except:
                pass

# 创建全局实例
langfuse_integration = LangfuseIntegration()

# 导出装饰器和函数
trace_async = langfuse_integration.trace_async
trace_sync = langfuse_integration.trace_sync
log_generation = langfuse_integration.log_generation
log_tool_call = langfuse_integration.log_tool_call
create_score = langfuse_integration.create_score