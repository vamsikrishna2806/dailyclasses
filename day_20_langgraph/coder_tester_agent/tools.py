import os
import re
import subprocess
import sys
import tempfile


def strip_code_fences(text: str) -> str:
    """Models wrap code in ```python ... ``` — keep only the code inside."""
    m = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


def code_blocks(text: str) -> list:
    """Return EVERY ```python ... ``` block found in the text (in order)."""
    return [b.strip() for b in re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)]


HARNESS = '''
import sys
_failures = []
for _t in __TESTS__.splitlines():
    _t = _t.strip()
    if not _t.startswith("assert"):
        continue
    try:
        exec(_t)
    except AssertionError:
        _msg = _t
        if " == " in _t:                       # show what the function REALLY returned
            _left = _t[len("assert"):].split(" == ", 1)[0]
            try:
                _msg += "    -> but it returned " + repr(eval(_left))
            except Exception as _e:
                _msg += "    -> error: " + str(_e)
        _failures.append(_msg)
    except Exception as _e:
        _failures.append(_t + "    -> " + type(_e).__name__ + ": " + str(_e))
if _failures:
    print("FAILED:")
    print("\\n".join(_failures))
    sys.exit(1)
print("ALL TESTS PASSED")
'''


def build_test_program(code: str, tests: str) -> str:
    """Code + a small harness that runs each assert and reports WHAT went wrong (like a mini pytest)."""
    return code + "\n\n" + HARNESS.replace("__TESTS__", repr(tests))


def run_python(code: str, timeout: int = 5) -> dict:
    """
    Run Python code in a SEPARATE process (with a time limit) and report what happened.
    Returns {"ok": bool, "output": str}.
    ⚠️ Only run code you are comfortable running — this is a classroom demo, not a sandbox.
    """
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "snippet.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            p = subprocess.run([sys.executable, path], capture_output=True, text=True,
                               timeout=timeout, cwd=folder)
        except subprocess.TimeoutExpired:
            return {"ok": False, "output": f"Timed out after {timeout}s (infinite loop?)"}
    output = (p.stdout + p.stderr).strip()
    # keep only the last lines of a traceback — that is where the useful error is
    output = "\n".join(output.splitlines()[-12:])
    return {"ok": p.returncode == 0, "output": output}
