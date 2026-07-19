from mcp.server.fastmcp import FastMCP

mcp = FastMCP("company-ops")

@mcp.tool()
def get_headcount(department: str) -> str:
    """Return the headcount for a company department."""
    data = {"billing": 12, "platform": 30, "data": 8}
    return f"{department}: {data.get(department.lower(), 'unknown')} people"

@mcp.tool()
def get_office(city: str) -> str:
    """Return the office address for a city."""
    offices = {"bengaluru": "The Leela, Bengaluru", "milan": "Via Roma 1, Milan"}
    return offices.get(city.lower(), "no office there")

if __name__ == "__main__":
    mcp.run(transport="stdio")
