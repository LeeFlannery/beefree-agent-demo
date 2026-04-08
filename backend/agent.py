"""
PydanticAI agent — email design assistant backed by Beefree MCP.

Model is selected from LLM_PROVIDER env var:
  anthropic → claude-sonnet-4-5
  openai    → gpt-4o
  gemini    → gemini-1.5-pro (google-gla)
"""

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

from config import settings

SYSTEM_PROMPT = """You are an expert email design assistant powered by the Beefree SDK.

You help users create, modify, and manage professional email templates using Beefree's
drag-and-drop builder format (BEE JSON). You have access to the following tools:

- create_email: Generate a new email template with a name, subject, and visual theme
- update_section: Modify a specific section or row within an existing template
- list_templates: Browse all available email templates
- get_template: Fetch the full BEE JSON for a specific template

When a user asks you to create or modify an email, always use the appropriate tool
and summarize what was done. If the user asks to see templates, use list_templates first,
then get_template for details if requested.

Keep responses concise and actionable. When referencing template IDs, quote them exactly.
"""


def build_agent() -> Agent:
    """Construct a PydanticAI agent wired to the Beefree MCP server."""
    match settings.LLM_PROVIDER:
        case "openai":
            model = "openai:gpt-4o"
        case "gemini":
            model = "google-gla:gemini-1.5-pro"
        case _:
            model = "anthropic:claude-sonnet-4-5"

    mcp_server = MCPServerStreamableHTTP(f"{settings.BEEFREE_MCP_URL}/mcp")

    return Agent(
        model,
        toolsets=[mcp_server],
        system_prompt=SYSTEM_PROMPT,
    )


# Module-level agent — instantiated once, reused across WebSocket connections.
# Re-call build_agent() if you need to hot-swap the provider at runtime.
agent = build_agent()
