# Quickstart

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.13+ | [python.org](https://www.python.org/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Bun | latest | `curl -fsSL https://bun.sh/install \| bash` |
| API key | any one | Anthropic / OpenAI / Gemini |

You only need one API key. Pick your provider, fill in that one key, leave the others blank.

## Setup

```bash
git clone https://github.com/LeeFlannery/beefree-agent-demo
cd beefree-agent-demo
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in your API key:

```env
LLM_PROVIDER=anthropic        # or openai or gemini
ANTHROPIC_API_KEY=sk-ant-...  # fill in the one you're using
```

## Run

You need three terminals.

**Terminal A - mock Beefree MCP server**

```bash
cd backend
uv run python mcp_mock.py
```

```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Terminal B - agent + API**

```bash
cd backend
op run --env-file=.env.secrets -- uv run python main.py
```

The `op run` command injects your API key from 1Password at process start. It never lands on disk.

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal C - frontend**

```bash
cd frontend
bun install
bun dev
```

```
  VITE ready in 300ms
  Local: http://localhost:5173/
```

## Try it

Open [http://localhost:5173/chat](http://localhost:5173/chat).

Suggested prompts to exercise each tool:

```
List all available templates
```

```
Create a bold product launch email called "Summer Drop" with subject "Something big is coming"
```

```
Get template tpl_abc12345
```

```
Update section row_001 in template tpl_abc12345 with the text "New hero copy here"
```

The agent streams tokens into the chat panel as it runs. When a tool call completes, the JSON panel on the right updates with the full Beefree template.

## What `uv run` is doing

`uv run python main.py` creates an isolated virtualenv from `pyproject.toml`, installs dependencies, and runs the script - all in one command. No `pip install`, no `source .venv/bin/activate`. Subsequent runs skip the install step.
