# Architecture

## Overview

```
beefree-agent-demo/
├── backend/
│   ├── config.py        # pydantic-settings - typed env vars
│   ├── mcp_mock.py      # Mock MCP server (port 8001)
│   ├── agent.py         # PydanticAI agent - model selection + toolsets
│   ├── main.py          # FastAPI - WebSocket /ws/chat
│   └── pyproject.toml   # uv project - Python 3.13+
└── frontend/
    └── src/
        ├── routes/      # TanStack Router - / to /chat
        ├── components/  # ChatPanel, JsonPreviewPanel, Layout
        ├── store/       # Zustand - messages, emailJson, isStreaming
        └── api/         # useChat (WebSocket hook), Zod schemas
```

## WebSocket message protocol

All messages are JSON.

**Client to server:**

```json
{ "message": "Create a welcome email for new users" }
```

**Server to client:**

```json
{ "type": "token", "content": "Sure" }
{ "type": "token", "content": ", I'll create" }
{ "type": "tool_result", "tool_name": "create_email", "content": { ... } }
{ "type": "done" }
{ "type": "error", "content": "..." }
```

The frontend appends `token` deltas into the current message bubble, and pipes `tool_result` content directly into the JSON preview panel.

## MCP mock server

`mcp_mock.py` implements the [MCP Streamable HTTP transport](https://spec.modelcontextprotocol.io/) manually - a single `POST /mcp` endpoint that handles JSON-RPC 2.0 methods:

| Method | Description |
|--------|-------------|
| `initialize` | Handshake - returns server capabilities |
| `notifications/initialized` | Client acknowledgement - no-op |
| `tools/list` | Returns the four tool schemas |
| `tools/call` | Dispatches to the appropriate handler |

Tool results are returned as MCP content parts:

```json
{
  "content": [{ "type": "text", "text": "{ ...BEE JSON... }" }],
  "isError": false
}
```

The `text` value is JSON-stringified BEE format. The frontend's Zod schemas validate this after parsing.

## Agent wiring

`agent.py` builds a `pydantic_ai.Agent` with `MCPServerStreamableHTTP` as its toolset:

```python
mcp_server = MCPServerStreamableHTTP(f"{settings.BEEFREE_MCP_URL}/mcp")
agent = Agent(model, toolsets=[mcp_server], system_prompt=SYSTEM_PROMPT)
```

PydanticAI handles the MCP `initialize` + `tools/list` handshake transparently on the first run. Tool calls made by the LLM are routed through PydanticAI to the MCP server and back.

## Provider selection

```python
match settings.LLM_PROVIDER:
    case "openai":  model = "openai:gpt-4o"
    case "gemini":  model = "google-gla:gemini-1.5-pro"
    case _:         model = "anthropic:claude-sonnet-4-5"
```

PydanticAI's model string format handles credential lookup from the environment automatically for each provider.
