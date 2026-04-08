"""
Beefree MCP Mock Server — port 8001

Implements the MCP Streamable HTTP transport (JSON-RPC 2.0) so that
pydantic-ai's MCPServerStreamableHTTP client can connect without modification.

Swap seam: point BEEFREE_MCP_URL at a real Beefree MCP server and delete this file.
"""

import json
import uuid
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Beefree MCP Mock", version="0.1.0")


# ---------------------------------------------------------------------------
# Beefree BEE JSON helpers
# ---------------------------------------------------------------------------

def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_text_module(html: str, padding: str = "10px 20px") -> dict:
    return {
        "type": "mailup-bee-newsletter-modules-text",
        "descriptor": {
            "text": {"html": html},
            "style": {"padding": padding},
        },
    }


def _make_image_module(src: str, alt: str = "", href: str = "") -> dict:
    return {
        "type": "mailup-bee-newsletter-modules-image",
        "descriptor": {
            "image": {"src": src, "alt": alt, "href": href, "width": "100%"},
            "style": {"padding": "0px"},
        },
    }


def _make_button_module(text: str, href: str = "#", color: str = "#4f46e5") -> dict:
    return {
        "type": "mailup-bee-newsletter-modules-button",
        "descriptor": {
            "button": {
                "label": text,
                "href": href,
                "style": {
                    "backgroundColor": color,
                    "color": "#ffffff",
                    "borderRadius": "6px",
                    "padding": "12px 24px",
                    "fontWeight": "600",
                },
            },
        },
    }


def _make_row(modules: list[dict], bg_color: str = "#ffffff") -> dict:
    return {
        "id": f"row_{uuid.uuid4().hex[:8]}",
        "cells": [1],
        "columns": [
            {
                "id": f"col_{uuid.uuid4().hex[:8]}",
                "modules": modules,
                "style": {"backgroundColor": bg_color, "padding": "0px"},
            }
        ],
        "style": {"backgroundColor": bg_color},
    }


def _full_template(name: str, subject: str, theme: str = "minimal") -> dict:
    accent = {"minimal": "#4f46e5", "bold": "#e11d48", "corporate": "#0369a1"}.get(
        theme, "#4f46e5"
    )
    tpl_id = f"tpl_{uuid.uuid4().hex[:8]}"
    return {
        "id": tpl_id,
        "name": name,
        "subject": subject,
        "theme": theme,
        "createdAt": _timestamp(),
        "updatedAt": _timestamp(),
        "tags": [theme, "email", "beefree"],
        "page": {
            "body": {
                "backgroundColor": "#f4f4f5",
                "contentWidth": "600px",
                "rows": [
                    _make_row(
                        [
                            _make_image_module(
                                "https://via.placeholder.com/600x120/4f46e5/ffffff?text=Beefree+Demo",
                                alt="Header",
                            )
                        ],
                        bg_color=accent,
                    ),
                    _make_row(
                        [
                            _make_text_module(
                                f"<h1 style='color:#111827;font-size:24px;margin:0 0 8px'>{name}</h1>"
                                f"<p style='color:#6b7280;font-size:16px;line-height:1.6'>"
                                f"This is your email generated via the Beefree SDK. "
                                f"Customize sections, swap images, and publish when ready.</p>"
                            ),
                            _make_button_module("Get Started", href="#", color=accent),
                        ]
                    ),
                    _make_row(
                        [
                            _make_text_module(
                                "<p style='color:#9ca3af;font-size:12px;text-align:center'>"
                                "You received this because you're awesome. "
                                "<a href='#' style='color:#9ca3af'>Unsubscribe</a></p>",
                                padding="16px 20px",
                            )
                        ],
                        bg_color="#f9fafb",
                    ),
                ],
            },
            "template": {
                "name": "template-base",
                "version": "2.0.0",
                "pluginVersion": "5.14.0",
            },
        },
    }


def _template_stub(tpl_id: str, name: str, theme: str = "minimal") -> dict:
    return {
        "id": tpl_id,
        "name": name,
        "theme": theme,
        "createdAt": _timestamp(),
        "tags": [theme, "email"],
        "thumbnailUrl": f"https://via.placeholder.com/300x200/e5e7eb/374151?text={name.replace(' ', '+')}",
    }


STUB_TEMPLATES = [
    _template_stub("tpl_abc12345", "Welcome Series — Week 1", "minimal"),
    _template_stub("tpl_def67890", "Product Launch Announcement", "bold"),
    _template_stub("tpl_ghi11223", "Monthly Newsletter", "corporate"),
]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

async def _tool_create_email(args: dict) -> dict:
    name = args.get("name", "New Campaign")
    subject = args.get("subject", "Hello from Beefree")
    theme = args.get("theme", "minimal")
    return _full_template(name, subject, theme)


async def _tool_update_section(args: dict) -> dict:
    template_id = args.get("template_id", "tpl_unknown")
    section_id = args.get("section_id", f"row_{uuid.uuid4().hex[:8]}")
    content = args.get("content", {})
    html = content.get("html", "<p>Updated content</p>")
    return {
        "templateId": template_id,
        "section": {
            "id": section_id,
            "updatedAt": _timestamp(),
            "column": {
                "id": f"col_{uuid.uuid4().hex[:8]}",
                "modules": [_make_text_module(html)],
            },
        },
        "success": True,
    }


async def _tool_list_templates(args: dict) -> dict:  # noqa: ARG001
    return {"templates": STUB_TEMPLATES, "total": len(STUB_TEMPLATES)}


async def _tool_get_template(args: dict) -> dict:
    template_id = args.get("template_id", "tpl_abc12345")
    match template_id:
        case "tpl_abc12345":
            return _full_template("Welcome Series — Week 1", "Welcome!", "minimal")
        case "tpl_def67890":
            return _full_template("Product Launch Announcement", "Big news 🚀", "bold")
        case "tpl_ghi11223":
            return _full_template("Monthly Newsletter", "This month in review", "corporate")
        case _:
            return _full_template("Custom Template", "Hello", "minimal")


TOOL_HANDLERS = {
    "create_email": _tool_create_email,
    "update_section": _tool_update_section,
    "list_templates": _tool_list_templates,
    "get_template": _tool_get_template,
}

# ---------------------------------------------------------------------------
# MCP tool schemas (JSON Schema for each tool's inputSchema)
# ---------------------------------------------------------------------------

MCP_TOOLS = [
    {
        "name": "create_email",
        "description": "Create a new Beefree email template. Returns full BEE JSON.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Template display name"},
                "subject": {"type": "string", "description": "Email subject line"},
                "theme": {
                    "type": "string",
                    "enum": ["minimal", "bold", "corporate"],
                    "description": "Visual theme",
                },
            },
        },
    },
    {
        "name": "update_section",
        "description": "Update a specific section/row in an existing Beefree template.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_id": {"type": "string", "description": "Template ID to update"},
                "section_id": {"type": "string", "description": "Row/section ID to replace"},
                "content": {
                    "type": "object",
                    "properties": {
                        "html": {"type": "string", "description": "New HTML content for the section"},
                    },
                    "description": "New content for the section",
                },
            },
            "required": ["template_id", "section_id"],
        },
    },
    {
        "name": "list_templates",
        "description": "List all available Beefree email templates (stubs, no full BEE JSON).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_template",
        "description": "Fetch the full BEE JSON for a specific Beefree template by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_id": {"type": "string", "description": "Template ID to fetch"},
            },
            "required": ["template_id"],
        },
    },
]


# ---------------------------------------------------------------------------
# MCP Streamable HTTP endpoint — JSON-RPC 2.0
# ---------------------------------------------------------------------------

def _ok(req_id, result) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})


def _err(req_id, code: int, message: str) -> JSONResponse:
    return JSONResponse(
        {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    )


@app.post("/mcp")
async def mcp_handler(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except Exception:
        return _err(None, -32700, "Parse error")

    method: str = body.get("method", "")
    req_id = body.get("id")
    params: dict = body.get("params", {})

    match method:
        case "initialize":
            return _ok(
                req_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "Beefree MCP Mock", "version": "0.1.0"},
                },
            )

        case "notifications/initialized":
            # Client notification — no response body needed
            return _ok(req_id, None)

        case "tools/list":
            return _ok(req_id, {"tools": MCP_TOOLS})

        case "tools/call":
            tool_name: str = params.get("name", "")
            arguments: dict = params.get("arguments", {})
            handler = TOOL_HANDLERS.get(tool_name)
            if handler is None:
                return _err(req_id, -32601, f"Unknown tool: {tool_name}")
            result_data = await handler(arguments)
            return _ok(
                req_id,
                {
                    "content": [
                        {"type": "text", "text": json.dumps(result_data, indent=2)}
                    ],
                    "isError": False,
                },
            )

        case _:
            return _err(req_id, -32601, f"Method not found: {method}")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.post("/health")
async def health() -> dict:
    return {"status": "ok", "service": "beefree-mcp-mock", "version": "0.1.0"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
