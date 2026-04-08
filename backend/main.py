"""
FastAPI main — WebSocket chat endpoint + CORS for Vite dev server.

WebSocket message protocol (JSON):
  Client → server:  {"message": "...user text..."}
  Server → client:  {"type": "token",       "content": "...delta..."}
                    {"type": "tool_result",  "tool_name": "...", "content": {...}}
                    {"type": "done"}
                    {"type": "error",        "content": "...message..."}
"""

import json

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic_ai import Agent
from pydantic_ai.messages import (
    FunctionToolResultEvent,
    PartDeltaEvent,
    TextPartDelta,
)

from agent import agent
from config import settings

app = FastAPI(title="Beefree Agent Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            message: str = data.get("message", "").strip()
            if not message:
                continue

            try:
                async with agent.iter(message) as run:
                    async for node in run:
                        if Agent.is_model_request_node(node):
                            async with node.stream(run.ctx) as stream:
                                async for event in stream:
                                    if (
                                        isinstance(event, PartDeltaEvent)
                                        and isinstance(event.delta, TextPartDelta)
                                        and event.delta.content_delta
                                    ):
                                        await websocket.send_json(
                                            {
                                                "type": "token",
                                                "content": event.delta.content_delta,
                                            }
                                        )

                        elif Agent.is_call_tools_node(node):
                            async with node.stream(run.ctx) as stream:
                                async for event in stream:
                                    if isinstance(event, FunctionToolResultEvent):
                                        _maybe_send_tool_result(
                                            websocket, event
                                        )

                await websocket.send_json({"type": "done"})

            except Exception as exc:  # noqa: BLE001
                await websocket.send_json({"type": "error", "content": str(exc)})

    except WebSocketDisconnect:
        pass


async def _maybe_send_tool_result(
    websocket: WebSocket,
    event: FunctionToolResultEvent,
) -> None:
    """Parse MCP tool result content and forward as a tool_result message."""
    content = event.result.content

    # MCP results arrive as a list of content parts or a raw string
    raw: str | None = None
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                raw = part.get("text")
                break
            if isinstance(part, str):
                raw = part
                break
    elif isinstance(content, str):
        raw = content

    if raw is None:
        return

    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return

    tool_name: str = getattr(event, "tool_name", "") or ""
    await websocket.send_json(
        {"type": "tool_result", "tool_name": tool_name, "content": parsed}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info",
    )
