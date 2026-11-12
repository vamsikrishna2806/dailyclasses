from langchain_core.tools import tool


@tool
def solve_math(expression: str) -> str:
    """
    Solve or evaluate any mathematical expression, equation, derivative, or integral.
    Examples:
      '2 + 2'            → arithmetic
      'sqrt(144)'        → functions
      'solve x^2 - 9'    → find roots
      'diff x^3 + 2*x'   → derivative
      'integrate sin(x)' → integral
    Uses SymPy — runs locally, no internet needed.
    """
    import sympy as sp

    x, y, z = sp.symbols("x y z")
    expr = expression.strip()
    lower = expr.lower()

    try:
        if lower.startswith("solve"):
            eq_str = lower.replace("solve", "", 1).strip()
            if "=" in eq_str:
                lhs, rhs = eq_str.split("=", 1)
                eq = sp.sympify(lhs) - sp.sympify(rhs)
            else:
                eq = sp.sympify(eq_str)
            solutions = sp.solve(eq, x)
            return f"Equation : {expr}\nSolutions: x = {solutions}"

        elif lower.startswith(("diff", "derivative")):
            expr_str = lower.replace("derivative", "").replace("diff", "", 1).strip()
            result = sp.diff(sp.sympify(expr_str), x)
            simplified = sp.simplify(result)
            return f"d/dx [ {expr_str} ] = {simplified}"

        elif lower.startswith(("integrate", "integral")):
            expr_str = lower.replace("integral", "").replace("integrate", "", 1).strip()
            result = sp.integrate(sp.sympify(expr_str), x)
            return f"∫ {expr_str} dx = {result} + C"

        else:
            parsed = sp.sympify(expr)
            evaluated = parsed.evalf()
            simplified = sp.simplify(parsed)
            return (
                f"Expression : {expr}\n"
                f"Result     : {evaluated}\n"
                f"Simplified : {simplified}"
            )

    except Exception as e:
        return f"Could not evaluate '{expr}': {str(e)}\nTry rewording, e.g. 'solve x^2 - 4'"
