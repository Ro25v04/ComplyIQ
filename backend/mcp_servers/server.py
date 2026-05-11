"""
ComplyAU MCP Server — exposes Australian legislation fetching as MCP tools.

Run standalone:  python backend/mcp_servers/server.py
The ReAct agent connects to this server via stdio and calls tools over the MCP protocol.
"""
import sys
import os

# Ensure project root is on the path when run as a subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from mcp.server.fastmcp import FastMCP
from backend.mcp_servers.legislation_au import fetch_legislation
from backend.mcp_servers.oaic import fetch_oaic

mcp = FastMCP("complyau-legislation")


@mcp.tool()
def fetch_legislation_tool(act_name: str) -> str:
    """Fetch live text for an Australian Act or regulation from government sources.
    Use when the user asks about a specific piece of Australian legislation.
    Examples: 'Privacy Act 1988', 'Fair Work Act 2009', 'Australian Consumer Law',
    'Work Health and Safety Act 2011', 'Spam Act 2003'"""
    return fetch_legislation(act_name)


@mcp.tool()
def fetch_oaic_guidance(topic: str) -> str:
    """Fetch official guidance from the Office of the Australian Information Commissioner (OAIC).
    Use when the question is specifically about privacy regulation, data breaches,
    or the Australian Privacy Principles.
    Examples: 'data breach', 'Australian Privacy Principles', 'privacy impact assessment',
    'credit reporting'"""
    return fetch_oaic(topic)


if __name__ == "__main__":
    mcp.run()
