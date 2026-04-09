# beefree-agent-demo

A PydanticAI agent that drives the [Beefree SDK](https://beefree.io/sdk/) via MCP, with a built-in mock server so you can run the full loop locally with no Beefree account and no beta access required.

**Model-agnostic by design.** Most agent demos are secretly OpenAI demos with a provider abstraction bolted on at the end. This one starts from `pydantic-ai`'s provider-neutral `Agent`, and switching between Anthropic, OpenAI, and Gemini is one env-var change. There is no OpenAI-shaped API call anywhere in the codebase.

[Docs + Quickstart](https://leeflannery.github.io/beefree-agent-demo/)

---

## What this is

```
┌─────────────┐   WebSocket   ┌──────────────────┐   MCP/JSON-RPC   ┌──────────────────┐
│  Vite + React│ ←──────────→ │  FastAPI + Pydantic│ ←─────────────→ │  Beefree MCP     │
│  (port 5173) │              │  AI Agent          │                  │  (mock: 8001,    │
│              │              │  (port 8000)        │                  │   real: your URL)│
└─────────────┘               └──────────────────┘                   └──────────────────┘
```

- Left panel: chat with the agent
- Right panel: live JSON preview of the Beefree template the agent built or fetched
- Agent tools: `create_email`, `update_section`, `list_templates`, `get_template`

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.13+ | [python.org](https://www.python.org/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Bun | latest | `curl -fsSL https://bun.sh/install \| bash` |
| API key | any one | Anthropic / OpenAI / Gemini |

---

## Quickstart

```bash
# 1. Clone and configure
git clone https://github.com/LeeFlannery/beefree-agent-demo
cd beefree-agent-demo
cp backend/.env.example backend/.env
# Edit backend/.env - fill in the key for your chosen provider (see below)

# 2. Terminal A - mock Beefree MCP server
cd backend
uv run python mcp_mock.py
# listening on http://localhost:8001

# 3. Terminal B - agent + API (key injected from 1Password, never hits disk)
cd backend
op run --env-file=.env.secrets -- uv run python main.py
# listening on http://localhost:8000

# 4. Terminal C - frontend
cd frontend
bun install
bun dev
# http://localhost:5173
```

Open [http://localhost:5173/chat](http://localhost:5173/chat) and try:

> "Create a bold product launch email called Summer Drop with subject 'Something big is coming'"

The agent will call `create_email` via MCP, stream its reply token-by-token, and the JSON panel will populate with the full BEE template.

---

## Switching LLM provider

Edit `backend/.env`:

```env
# anthropic (default) - requires ANTHROPIC_API_KEY
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# openai - requires OPENAI_API_KEY
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# gemini - requires GEMINI_API_KEY
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

Restart `main.py`. Nothing else changes.

Model mapping: `anthropic -> claude-sonnet-4-5`, `openai -> gpt-4o`, `gemini -> gemini-1.5-pro`.

---

## Swapping to the real Beefree MCP

When you have Beefree SDK credentials and a running Beefree MCP server:

```env
BEEFREE_MCP_URL=https://your-beefree-mcp.example.com
BEEFREE_CLIENT_ID=your-client-id
BEEFREE_CLIENT_SECRET=your-client-secret
```

That's it. The agent uses `MCPServerStreamableHTTP(BEEFREE_MCP_URL + "/mcp")`, the same MCP Streamable HTTP transport the mock speaks. Shut down `mcp_mock.py` and restart `main.py`.

---

## Project structure

```
beefree-agent-demo/
├── backend/
│   ├── pyproject.toml     # uv project - Python 3.13+
│   ├── config.py          # pydantic-settings - all env vars
│   ├── mcp_mock.py        # Mock Beefree MCP server (port 8001)
│   ├── agent.py           # PydanticAI agent - model selection + MCP wiring
│   ├── main.py            # FastAPI - WebSocket /ws/chat
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── routes/        # TanStack Router - / to /chat
    │   ├── components/    # ChatPanel, JsonPreviewPanel, Layout
    │   ├── store/         # Zustand - messages, emailJson, isStreaming
    │   └── api/           # useChat (WebSocket hook), Zod schemas
    └── ...
```

---

## Development notes

- The mock MCP server implements the [MCP Streamable HTTP transport](https://spec.modelcontextprotocol.io/) (JSON-RPC 2.0 over POST `/mcp`). No extra dependencies - plain FastAPI.
- Zod schemas in `frontend/src/api/schemas.ts` match the mock's BEE JSON output exactly. They'll need updating if you add fields to a real Beefree MCP response.
- `uv run` handles the virtualenv automatically - no `source .venv/bin/activate` needed.
