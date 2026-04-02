# ═══════════════════════════════════════════════════════
#  parser.py  —  تحويل المعادلة من الشكل العادي لـ SymPy
# ═══════════════════════════════════════════════════════
import re as _re          # ← نستخدم alias عشان لا يتعارض مع sympy.re
from sympy import *

x = symbols('x')
y = Function('y')

def parse_equation(eq_str: str):
    """
    يحوّل المعادلة من الشكل العادي إلى SymPy Eq.
    يقبل: y', dy/dx, y'', d²y/dx², y^2, x^3 ...
    """
    s = eq_str.strip()

    # ── الخطوة 1: توحيد رموز المشتق الثاني ──────────────
    s = _re.sub(r"d\^2\s*y\s*/\s*dx\^2",   "__YPP__", s)
    s = _re.sub(r"d²y\s*/\s*dx²",           "__YPP__", s)
    s = _re.sub(r"d\*\*2\s*y\s*/\s*dx\*\*2","__YPP__", s)
    s = _re.sub(r"y''|y″",                  "__YPP__", s)

    # ── الخطوة 2: توحيد رموز المشتق الأول ───────────────
    s = _re.sub(r"dy\s*/\s*dx",             "__YP__",  s)
    s = _re.sub(r"y'|y′",                   "__YP__",  s)

    # ── الخطوة 3: توحيد y المجهول ───────────────────────
    # نستبدل y المنفردة (ليست جزء من exp, sin, ... إلخ)
    s = _re.sub(r"(?<![a-zA-Z])y(?![a-zA-Z_(])", "__YF__", s)

    # ── الخطوة 4: استبدال بـ SymPy ──────────────────────
    s = s.replace("__YPP__", "y(x).diff(x,2)")
    s = s.replace("__YP__",  "y(x).diff(x)")
    s = s.replace("__YF__",  "y(x)")

    # ── الخطوة 5: تحويل ^ لـ ** ─────────────────────────
    s = _re.sub(r"\^", "**", s)

    # ── الخطوة 6: تحويل لـ Eq ───────────────────────────
    local_ns = {
        'x': x, 'y': y,
        'sin': sin, 'cos': cos, 'tan': tan,
        'exp': exp, 'ln': ln, 'log': log,
        'sqrt': sqrt, 'pi': pi, 'E': E,
        'sinh': sinh, 'cosh': cosh, 'tanh': tanh,
    }

    if '=' in s:
        left, right = s.split('=', 1)
        lhs = sympify(left.strip(),  locals=local_ns)
        rhs = sympify(right.strip(), locals=local_ns)
        return Eq(lhs, rhs)
    else:
        return Eq(sympify(s, locals=local_ns), 0)


def build_ics(x0, y0_str, dy0_str):
    """يبني dict الشروط الابتدائية"""
    ics = {}
    try:
        x0v = float(x0)
        if str(y0_str).strip():
            ics[y(x0v)] = sympify(str(y0_str).strip())
        if str(dy0_str).strip():
            ics[y(x).diff(x).subs(x, x0v)] = sympify(str(dy0_str).strip())
    except:
        pass
    return ics
