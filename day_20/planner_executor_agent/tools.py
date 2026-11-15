import ast
import operator
import re

from langchain_core.tools import tool

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg, ast.Mod: operator.mod}


def _eval(node):
    """Safely evaluate a math expression tree (numbers and + - * / ** % only)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and + - * / ** % are allowed")


@tool
def calculator(expression: str) -> str:
    """Calculate a math expression such as '3 * 2 + 4 * 5' or '(26 * 0.9)'. Numbers and + - * / only."""
    try:
        expr = expression.replace("$", "").replace(",", "").replace("%", "/100").strip()
        result = _eval(ast.parse(expr, mode="eval").body)
        return str(round(result, 4))
    except Exception as e:
        return f"Calculator error: {e}. Send a plain expression like 3*2+4*5."


UNITS = {("km", "miles"): 0.621371, ("miles", "km"): 1.60934, ("kg", "lb"): 2.20462,
         ("lb", "kg"): 0.453592, ("m", "ft"): 3.28084, ("ft", "m"): 0.3048}


@tool
def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a value between km/miles, kg/lb or m/ft. Example: value=10, from_unit='km', to_unit='miles'."""
    factor = UNITS.get((from_unit.lower().strip(), to_unit.lower().strip()))
    if factor is None:
        return "Unsupported conversion. Supported: km<->miles, kg<->lb, m<->ft."
    return f"{round(float(value) * factor, 3)} {to_unit}"


def parse_plan(text: str, max_steps: int = 4) -> list:
    """Turn a numbered list ('1. do this', '2. do that') into ['do this', 'do that']."""
    steps = [re.sub(r"^\s*\d+[.)]\s*", "", ln).strip() for ln in text.splitlines() if re.match(r"^\s*\d+[.)]", ln)]
    # Guard rail: a small model sometimes writes a RESULT as a step ("4. 108", "$40 - 30 = $10"). Drop those.
    steps = [s for s in steps if re.search(r"[A-Za-z]{3,}", s) and "=" not in s]
    return steps[:max_steps] or [text.strip()]
