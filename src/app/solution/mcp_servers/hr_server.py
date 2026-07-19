"""HR department MCP server. Run standalone or launched by the app via stdio.

This is what "a department hands you their MCP" looks like — a small server
exposing that team's tools. The app connects to it and the agent gains its tools.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hr")


@mcp.tool()
def pto_policy() -> str:
    """Company paid-time-off (PTO) policy."""
    return "Full-time employees get 28 days of PTO per year, plus public holidays."


@mcp.tool()
def benefits(topic: str) -> str:
    """Look up an HR benefit by topic (e.g. 'health', 'pension', 'remote')."""
    data = {
        "health": "Private health cover for employee + dependents.",
        "pension": "6% employer pension match.",
        "remote": "Remote work up to 3 days/week.",
    }
    return data.get(topic.lower().strip(), "No benefit found for that topic.")


if __name__ == "__main__":
    mcp.run(transport="stdio")
