# beefree-agent-demo

A PydanticAI agent that drives the [Beefree SDK](https://beefree.io/sdk/) via MCP, with a built-in mock server so you can run the full loop locally with no Beefree account and no beta access required.

**Model-agnostic by design.** Most agent demos are secretly OpenAI demos with a provider abstraction bolted on at the end. This one starts from `pydantic-ai`'s provider-neutral `Agent`, and switching between Anthropic, OpenAI, and Gemini is one env-var change. There is no OpenAI-shaped API call anywhere in the codebase.

## What it does

```
┌─────────────┐   WebSocket   ┌──────────────────┐   MCP/JSON-RPC   ┌──────────────────┐
│  Vite + React│ ←──────────→ │  FastAPI + Pydantic│ ←─────────────→ │  Beefree MCP     │
│  (port 5173) │              │  AI Agent          │                  │  (mock: 8001,    │
│              │              │  (port 8000)        │                  │   real: your URL)│
└─────────────┘               └──────────────────┘                   └──────────────────┘
```

- **Left panel** - chat with the agent
- **Right panel** - live JSON preview of the Beefree template the agent built or fetched
- **Agent tools** - `create_email`, `update_section`, `list_templates`, `get_template`

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Vite, React, TypeScript, TanStack Router, HeroUI, Tailwind v4, Zustand, Zod |
| Backend | FastAPI, PydanticAI, Python 3.13+ |
| Package managers | Bun (frontend), uv (backend) |
| MCP transport | Streamable HTTP (JSON-RPC 2.0) |

## Get started

See the [Quickstart](quickstart.md) for setup instructions, or jump to [Configuration](configuration.md) to understand all the knobs.
