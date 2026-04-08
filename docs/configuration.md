# Configuration

All configuration lives in `backend/.env`. Copy the example file to get started:

```bash
cp backend/.env.example backend/.env
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `anthropic` | Which LLM to use: `anthropic`, `openai`, or `gemini` |
| `ANTHROPIC_API_KEY` | | Required when `LLM_PROVIDER=anthropic` |
| `OPENAI_API_KEY` | | Required when `LLM_PROVIDER=openai` |
| `GEMINI_API_KEY` | | Required when `LLM_PROVIDER=gemini` |
| `BEEFREE_MCP_URL` | `http://localhost:8001` | Base URL of the Beefree MCP server |
| `BEEFREE_CLIENT_ID` | | Your Beefree client ID (not used by mock) |
| `BEEFREE_CLIENT_SECRET` | | Your Beefree client secret (not used by mock) |
| `HOST` | `0.0.0.0` | FastAPI bind address |
| `PORT` | `8000` | FastAPI port |

## Switching LLM provider

Edit `LLM_PROVIDER` and fill in the corresponding key. Restart `main.py`.

=== "Anthropic"

    ```env
    LLM_PROVIDER=anthropic
    ANTHROPIC_API_KEY=sk-ant-...
    ```

    Model: `claude-sonnet-4-5`

=== "OpenAI"

    ```env
    LLM_PROVIDER=openai
    OPENAI_API_KEY=sk-...
    ```

    Model: `gpt-4o`

=== "Gemini"

    ```env
    LLM_PROVIDER=gemini
    GEMINI_API_KEY=AIza...
    ```

    Model: `gemini-1.5-pro`

Nothing else changes. The agent, WebSocket, and frontend are all provider-blind.

## Swapping to the real Beefree MCP

When you have Beefree SDK credentials:

```env
BEEFREE_MCP_URL=https://your-beefree-mcp.example.com
BEEFREE_CLIENT_ID=your-client-id
BEEFREE_CLIENT_SECRET=your-client-secret
```

Shut down `mcp_mock.py` and restart `main.py`. The agent connects via `MCPServerStreamableHTTP(BEEFREE_MCP_URL + "/mcp")` - the same MCP Streamable HTTP transport the mock speaks, so the swap is seamless.
