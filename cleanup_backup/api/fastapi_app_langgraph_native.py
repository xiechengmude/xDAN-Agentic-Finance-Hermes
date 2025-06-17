"""
FastAPI应用 - LangGraph原生MCP版本
FastAPI Application with Native LangGraph MCP Integration
"""

import asyncio
import json
import uuid
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from adapters.langgraph_native_mcp_adapter import LangGraphNativeMCPAdapter


# Pydantic 模型定义
class Message(BaseModel):
    type: str  # "human" or "ai"
    content: str
    id: Optional[str] = None

class RunRequest(BaseModel):
    messages: List[Message]
    initial_search_query_count: Optional[int] = 3
    max_research_loops: Optional[int] = 5
    reasoning_model: Optional[str] = None

class ThreadResponse(BaseModel):
    thread_id: str
    status: str
    created_at: str

class HealthResponse(BaseModel):
    status: str
    initialized: bool
    tools_available: int
    timestamp: str
    architecture: str


# 创建FastAPI应用
app = FastAPI(
    title="xDAN-LangGraph Native MCP Adapter API",
    description="原生LangGraph MCP集成的适配器API",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局适配器实例
adapter: Optional[LangGraphNativeMCPAdapter] = None
adapter_lock = asyncio.Lock()


async def get_adapter() -> LangGraphNativeMCPAdapter:
    """获取全局适配器实例"""
    global adapter
    async with adapter_lock:
        if adapter is None:
            print("🚀 初始化 LangGraph 原生 MCP 适配器...")
            adapter = LangGraphNativeMCPAdapter()
            success = await adapter.initialize()
            if not success:
                raise HTTPException(status_code=500, detail="适配器初始化失败")
            print("✅ LangGraph 原生 MCP 适配器初始化完成")
    return adapter


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("🚀 启动 xDAN-LangGraph 原生 MCP 适配器 API 服务...")
    await get_adapter()  # 预初始化适配器


# API 路由定义

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "xDAN-LangGraph Native MCP Adapter API",
        "version": "2.0.0",
        "status": "running",
        "architecture": "langgraph_native_mcp",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    try:
        adapter_instance = await get_adapter()
        health_info = await adapter_instance.health_check()
        return HealthResponse(**health_info)
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            initialized=False,
            tools_available=0,
            timestamp=datetime.now().isoformat(),
            architecture="langgraph_native_mcp"
        )


@app.post("/assistants/{assistant_id}/threads", response_model=ThreadResponse)
async def create_thread(assistant_id: str):
    """创建新线程"""
    adapter_instance = await get_adapter()
    thread_id = await adapter_instance.create_thread()
    
    return ThreadResponse(
        thread_id=thread_id,
        status="created",
        created_at=datetime.now().isoformat()
    )


@app.get("/assistants/{assistant_id}/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(assistant_id: str, thread_id: str):
    """获取线程信息"""
    adapter_instance = await get_adapter()
    thread_info = await adapter_instance.get_thread_status(thread_id)
    
    return ThreadResponse(
        thread_id=thread_id,
        status=thread_info.get("status", "active"),
        created_at=thread_info.get("created_at", datetime.now().isoformat())
    )


@app.post("/assistants/{assistant_id}/threads/{thread_id}/runs/stream")
async def stream_run(assistant_id: str, thread_id: str, request: dict):
    """流式执行接口（LangGraph原生MCP版本）"""
    try:
        adapter_instance = await get_adapter()
        
        # 处理LangGraph SDK格式的请求
        input_data = request.get("input", {})
        messages = input_data.get("messages", [])
        config = {
            "initial_search_query_count": input_data.get("initial_search_query_count", 3),
            "max_research_loops": input_data.get("max_research_loops", 3),
            "reasoning_model": input_data.get("reasoning_model", "xDAN-Agent-Medium-v2-step300-0525")
        }
        
        print(f"📡 开始LangGraph原生流式执行 - Thread: {thread_id}, Assistant: {assistant_id}")
        
        async def event_generator():
            """SSE事件生成器"""
            try:
                # 发送开始事件
                yield f"data: {json.dumps({'type': 'start', 'timestamp': datetime.now().isoformat(), 'architecture': 'langgraph_native_mcp'})}\n\n"
                
                # 流式执行并发送事件
                async for event in adapter_instance.stream_execution(messages, config):
                    event_data = {
                        "type": "update",
                        "data": event,
                        "timestamp": datetime.now().isoformat(),
                        "architecture": "langgraph_native_mcp"
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                    
                    # 控制发送速度
                    await asyncio.sleep(0.1)
                
                # 发送结束事件
                yield f"data: {json.dumps({'type': 'end', 'timestamp': datetime.now().isoformat(), 'architecture': 'langgraph_native_mcp'})}\n\n"
                
            except Exception as e:
                error_event = {
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "architecture": "langgraph_native_mcp"
                }
                yield f"data: {json.dumps(error_event)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        print(f"❌ LangGraph原生流式执行错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assistants/{assistant_id}/threads/{thread_id}/history")
async def get_thread_history(assistant_id: str, thread_id: str, request: dict):
    """获取线程历史记录（LangGraph原生MCP版本）"""
    try:
        adapter_instance = await get_adapter()
        
        # For now, return an empty history since our current implementation
        # doesn't maintain detailed state history like LangGraph Studio
        # In a full implementation, this would return the actual thread history
        history = []
        
        print(f"📜 获取线程历史 (原生MCP) - Thread: {thread_id}, Assistant: {assistant_id}")
        return history
        
    except Exception as e:
        print(f"❌ 获取线程历史错误 (原生MCP): {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/assistants/{assistant_id}/threads/{thread_id}/state")
async def get_thread_state(assistant_id: str, thread_id: str):
    """获取线程状态（LangGraph原生MCP版本）"""
    try:
        adapter_instance = await get_adapter()
        thread_info = await adapter_instance.get_thread_status(thread_id)
        
        # Return a minimal state structure that LangGraph SDK expects
        state = {
            "values": thread_info.get("values", {}),
            "checkpoint": {
                "checkpoint_id": thread_id,
                "thread_id": thread_id
            },
            "created_at": thread_info.get("created_at", datetime.now().isoformat()),
            "metadata": thread_info.get("metadata", {}),
            "architecture": "langgraph_native_mcp"
        }
        
        print(f"📊 获取线程状态 (原生MCP) - Thread: {thread_id}, Assistant: {assistant_id}")
        return state
        
    except Exception as e:
        print(f"❌ 获取线程状态错误 (原生MCP): {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket流式接口"""
    await websocket.accept()
    print("🔌 WebSocket 连接已建立 (LangGraph Native MCP)")
    
    try:
        adapter_instance = await get_adapter()
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            print(f"📨 收到WebSocket消息: {data.get('type', 'unknown')}")
            
            if data.get("type") == "run":
                messages = data.get("messages", [])
                config = data.get("config", {})
                
                # 发送开始事件
                await websocket.send_json({
                    "type": "start",
                    "timestamp": datetime.now().isoformat(),
                    "architecture": "langgraph_native_mcp"
                })
                
                # 流式执行并发送事件
                try:
                    async for event in adapter_instance.stream_execution(messages, config):
                        await websocket.send_json({
                            "type": "update",
                            "data": event,
                            "timestamp": datetime.now().isoformat(),
                            "architecture": "langgraph_native_mcp"
                        })
                        await asyncio.sleep(0.1)
                    
                    # 发送完成事件
                    await websocket.send_json({
                        "type": "complete",
                        "timestamp": datetime.now().isoformat(),
                        "architecture": "langgraph_native_mcp"
                    })
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                        "architecture": "langgraph_native_mcp"
                    })
            
    except WebSocketDisconnect:
        print("🔌 WebSocket 连接已断开")
    except Exception as e:
        print(f"❌ WebSocket 错误: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })


@app.get("/tools/count")
async def get_tools_count():
    """获取可用工具数量"""
    try:
        adapter_instance = await get_adapter()
        count = adapter_instance.get_available_tools_count()
        return {"tools_count": count, "architecture": "langgraph_native_mcp"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools/list")
async def list_tools():
    """列出所有可用工具"""
    try:
        adapter_instance = await get_adapter()
        if adapter_instance.is_initialized:
            tools_info = list(adapter_instance.available_tools.keys())
            return {
                "tools": tools_info, 
                "total": len(tools_info),
                "architecture": "langgraph_native_mcp"
            }
        else:
            return {"tools": [], "total": 0, "architecture": "langgraph_native_mcp"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 静态文件服务（如果需要服务前端文件）
import os
from pathlib import Path

frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"📁 静态文件服务已启用: {frontend_path}")


def create_app() -> FastAPI:
    """创建应用实例"""
    return app


if __name__ == "__main__":
    print("🚀 启动 xDAN-LangGraph 原生 MCP 适配器服务器...")
    print("📡 API 文档: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    print("🏗️ 架构: LangGraph Native MCP")
    
    uvicorn.run(
        "fastapi_app_langgraph_native:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )