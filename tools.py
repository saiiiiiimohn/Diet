"""
Tools for the Daily Meal & Diet Planner.

Per the capstone guidance: tools must always return strings and never raise
exceptions — errors are returned as strings so the answer_node can see them.
"""

from __future__ import annotations

import ast
import operator
import re
from datetime import datetime
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------
# Calculator — safe arithmetic for macro / calorie math
# ---------------------------------------------------------------------------

_ALLOWED_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}

_ALLOWED_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"unsupported literal: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_BIN_OPS:
            raise ValueError(f"operator not allowed: {op_type.__name__}")
        return _ALLOWED_BIN_OPS[op_type](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARY_OPS:
            raise ValueError(f"unary op not allowed: {op_type.__name__}")
        return _ALLOWED_UNARY_OPS[op_type](_safe_eval(node.operand))
    raise ValueError(f"unsupported expression node: {type(node).__name__}")


def calculator(expression: str) -> str:
    """
    Evaluate a plain arithmetic expression and return the result as a string.

    Supports + - * / % ** // and parentheses on numbers only. Refuses any
    identifiers, function calls, or attribute access — so a model cannot
    smuggle code through here.
    """
    expr = (expression or "").strip()
    if not expr:
        return "Calculator error: empty expression."
    if len(expr) > 200:
        return "Calculator error: expression too long (max 200 chars)."
    if not re.fullmatch(r"[0-9+\-*/%.()\s]+", expr):
        return (
            "Calculator error: only numbers and + - * / % ( ) are allowed. "
            "Pass a plain arithmetic expression such as '2*100 + 3*40'."
        )
    try:
        tree = ast.parse(expr, mode="eval")
        value = _safe_eval(tree)
    except ZeroDivisionError:
        return "Calculator error: division by zero."
    except Exception as exc:  # noqa: BLE001 — tool must never raise
        return f"Calculator error: {exc}"
    if value == int(value):
        return f"{expr} = {int(value)}"
    return f"{expr} = {round(value, 2)}"


# ---------------------------------------------------------------------------
# Datetime — for "it's 9 pm, should I still eat dinner?" style questions
# ---------------------------------------------------------------------------

_IST = ZoneInfo("Asia/Kolkata")


def current_datetime() -> str:
    """
    Return the current local time (IST) as a readable string plus meal-window
    context the answer_node can reason over.
    """
    now = datetime.now(_IST)
    hour = now.hour
    if 5 <= hour < 10:
        window = "breakfast window"
    elif 10 <= hour < 12:
        window = "mid-morning snack window"
    elif 12 <= hour < 15:
        window = "lunch window"
    elif 15 <= hour < 18:
        window = "evening snack window"
    elif 18 <= hour < 21:
        window = "dinner window"
    elif 21 <= hour < 23:
        window = "late — prefer a light option, not a full dinner"
    else:
        window = "very late / overnight — water or buttermilk only is safest"
    return (
        f"Current time (IST): {now.strftime('%Y-%m-%d %H:%M')} "
        f"({now.strftime('%A')}). Meal window: {window}."
    )


# ---------------------------------------------------------------------------
# Dispatcher used by the tool_node in agent.py
# ---------------------------------------------------------------------------

def run_tool(name: str, argument: str = "") -> str:
    name = (name or "").strip().lower()
    if name == "calculator":
        return calculator(argument)
    if name in {"datetime", "time", "now"}:
        return current_datetime()
    return (
        f"Tool error: unknown tool '{name}'. "
        "Available tools: calculator(expression), datetime()."
    )
