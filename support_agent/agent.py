"""E-commerce support agent from the MCP video, built on Google ADK
(Agent Development Kit) with a free-tier Gemini model.
"""

import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# Only needed for the Streamable HTTP example in build_toolsets() below.
# from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams

ROOT = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

INSTRUCTION = """You are a support agent for an online store.

Rules:
- For order or product questions, always use this store's own
  order/product tools. Never guess an order status, product detail,
  or policy from your own general knowledge.

- For policy questions (refunds, shipping), use the filesystem tools
  to read the policy files directly: refund_policy.md for refunds,
  shipping_policy.md for shipping. List the directory first if you
  need to find them.

- Never use the web search tool for anything about this store (orders,
  products, refunds, shipping, policies) -- even if a general answer
  is easy to find online, it is not this store's actual policy.

- For questions clearly unrelated to this store (general knowledge,
  current events, "what is X"), use the web search tool if it's
  available.

 If no tool is available to answer a question, say so plainly
  (e.g. "I don't have access to that right now") instead of guessing.
- Keep answers short and friendly.
"""


def build_toolsets() -> list[McpToolset]:
    private_ecommerce = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(ROOT / "ecommerce_mcp_server" / "server.py")],
            ),
        ),
    )

    # Example: a Streamable HTTP MCP server instead of STDIO.
    #public_streamable_http_example = McpToolset(
    #     connection_params=StreamableHTTPConnectionParams(
    #         url="http://127.0.0.1:8010/mcp",
    #     ),
    # )

    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    public_filesystem = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=npx_cmd,
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    str(ROOT / "docs"),
                ],
            ),
        ),
    )

    public_web_search = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="uvx",
                args=["duckduckgo-mcp-server"],
            ),
        ),
    )

    # Example: a Streamable HTTP MCP server instead of STDIO.
    #
    # All three servers above are STDIO -- we launch them ourselves as
    # subprocesses on this same machine. A Streamable HTTP server is
    # different: it's already running somewhere else, as its own
    # always-on web address, and you just give it a URL, the same way a
    # browser hits a website. No `command` / `args` to launch anything --
    # StreamableHTTPConnectionParams takes a `url` instead of a
    # StdioServerParameters.
    #
    # To try this for real: run our DuckDuckGo server in Streamable HTTP
    # mode, in its own terminal, BEFORE starting the agent:
    #
    #   uvx duckduckgo-mcp-server --transport streamable-http --port 8964
    #
    # ...then point this toolset at it:
    #
    # public_streamable_http_example = McpToolset(
    #     connection_params=StreamableHTTPConnectionParams(
    #         url="http://127.0.0.1:8964/mcp",
    #     ),
    # )
    # # add it to the list below, e.g.:
    # # return [private_ecommerce, public_filesystem, public_streamable_http_example]
    #
    # Note this is now a SEPARATE process you have to start and stop
    # yourself -- unlike STDIO, ADK doesn't launch or manage it for you.
    
    return [private_ecommerce, public_filesystem, public_web_search]

root_agent = Agent(
    name="support_agent",
    model=MODEL,
    description="Support agent for an online store.",
    instruction=INSTRUCTION,
    tools=build_toolsets(),
)