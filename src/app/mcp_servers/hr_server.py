"""HR department MCP server — 📝 YOU BUILD THIS.

This is what "a department hands you their MCP" looks like: a small server that
exposes that team's tools. The app connects to it (see load_mcp_tools) and the
agent gains its tools. Finance is already written (finance_server.py) as an example.

Fill in the TODOs, then it's launched automatically when you toggle "HR" in the app.
Run standalone to sanity-check:  uv run python app/mcp_servers/hr_server.py
"""
from mcp.server.fastmcp import FastMCP

# TODO: create the server — mcp = FastMCP("hr")
mcp = ...


# TODO: expose a tool with the @mcp.tool() decorator. A tool is just a documented
#       function — the docstring is what the agent reads to decide when to call it.
#
#   @mcp.tool()
#   def pto_policy() -> str:
#       """Company paid-time-off (PTO) policy."""
#       return "Full-time employees get 28 days of PTO per year, plus public holidays."
#
# Add at least one tool (a second, e.g. benefits(topic), is a nice extra).


if __name__ == "__main__":
    # TODO: mcp.run(transport="stdio")
    ...
