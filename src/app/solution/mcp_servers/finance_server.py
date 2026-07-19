"""Finance department MCP server (stdio). Toggle it on/off in the app sidebar."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("finance")


@mcp.tool()
def expense_policy() -> str:
    """Company expense-reimbursement policy."""
    return "Expenses over $500 need manager approval. Reimbursement takes 5-7 business days."


@mcp.tool()
def budget(team: str) -> str:
    """Look up the remaining quarterly budget for a team."""
    data = {"billing": "$12,000 left", "platform": "$40,000 left", "data": "$8,500 left"}
    return data.get(team.lower().strip(), "No budget on record for that team.")


if __name__ == "__main__":
    mcp.run(transport="stdio")
