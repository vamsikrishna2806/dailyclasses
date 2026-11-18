"""
math_server.py  -  Your FIRST MCP server (stdio transport)
Try it:  mcp dev servers/math_server.py     (opens the MCP Inspector)
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")              # the name clients will see


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the product."""
    return a * b


@mcp.tool()
def div(a: float, b: float) -> float:
    """div of two numbers"""
    return a / b

@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return base ** exponent

@mcp.resource("math://constants")
def constants() -> str:
    """Useful math constants (read-only data)."""
    return "pi = 3.14159\ne = 2.71828\ngolden_ratio = 1.61803"


@mcp.prompt()
def explain_step_by_step(problem: str) -> str:
    """Template: solve a math problem step by step."""
    return f"Solve step by step. Use the math tools for EVERY calculation:\n{problem}"


if __name__ == "__main__":
    # stdio: talk JSON-RPC over stdin/stdout. NEVER print() in a stdio server!
    mcp.run(transport="stdio")
