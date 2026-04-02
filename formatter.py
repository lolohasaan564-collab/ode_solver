# ═══════════════════════════════════════════════════════
#  formatter.py  —  تحويل الحل لشكل مقروء وجميل
# ═══════════════════════════════════════════════════════
from sympy import *
import re

x = symbols('x')
y = Function('y')

def format_solution(sol_raw) -> str:
    """
    يحوّل أي شكل من أشكال الحل لنص مقروء.
    يتعامل مع: Eq, list, str, Expr
    """
    # ── حالة 1: قائمة من Eq (مثل حلول متعددة) ──────────
    if isinstance(sol_raw, (list, tuple)):
        parts = []
        for item in sol_raw:
            parts.append(_format_single(item))
        # لو حلان متماثلان بعلامتين → ± 
        if len(parts) == 2:
            p0 = parts[0].replace('-', '').strip()
            p1 = parts[1].replace('-', '').strip()
            if p0 == p1 or parts[0].replace('-','') == parts[1].replace('-',''):
                # اجعلها ± شكل
                return f"±({parts[1]})"
        return "  أو  ".join(parts)

    return _format_single(sol_raw)


def _format_single(sol) -> str:
    """يعالج حل واحد"""
    # استخرج الطرف الأيمن إذا كان Eq
    if isinstance(sol, Eq):
        expr = sol.rhs
    elif isinstance(sol, str):
        # لو string فيه Eq(...)
        if sol.startswith('[') or 'Eq(' in sol:
            return _parse_ugly_str(sol)
        expr = sympify(sol) if _is_sympifiable(sol) else sol
    else:
        expr = sol

    return _expr_to_pretty(expr)


def _parse_ugly_str(s: str) -> str:
    """يعالج النص القبيح مثل [Eq(y(x), ...), Eq(y(x), ...)]"""
    # استخرج كل محتويات Eq(y(x), ...)
    matches = re.findall(r'Eq\(y\(x\),\s*(.+?)\)(?:,|\]|$)', s)
    if not matches:
        # جرّب تحليل بـ sympy
        try:
            obj = sympify(s)
            return format_solution(obj)
        except:
            return _sympy_to_human(s)

    parts = [_expr_to_pretty(m.strip()) for m in matches]

    # تحقق من ± 
    if len(parts) == 2:
        neg = parts[0].startswith('-')
        pos_part = parts[0].lstrip('-').strip()
        if f"-{pos_part}" == parts[0] and pos_part == parts[1]:
            return f"±{pos_part}"
        # لو واحدة سالبة والتانية موجبة لنفس التعبير
        try:
            e0 = sympify(matches[0])
            e1 = sympify(matches[1])
            if simplify(e0 + e1) == 0:
                return f"±({parts[1]})"
        except:
            pass

    return "  أو  ".join(parts)


def _expr_to_pretty(expr) -> str:
    """يحوّل SymPy expression لنص جميل"""
    if isinstance(expr, str):
        try:
            expr = sympify(expr)
        except:
            return _sympy_to_human(expr)

    s = str(expr)
    return _sympy_to_human(s)


def _sympy_to_human(s: str) -> str:
    """يحوّل نص SymPy لشكل رياضي مقروء"""
    s = str(s).strip()

    # إزالة y(x) من الطرف الأيسر لو موجود
    s = re.sub(r'^y\(x\)\s*=\s*', '', s)

    # sqrt(...) → √(...)
    s = re.sub(r'sqrt\(([^)]+)\)', r'√(\1)', s)

    # exp(x) → eˣ  (بسيط)
    s = re.sub(r'exp\(x\)', 'eˣ', s)
    s = re.sub(r'exp\((-?\w+)\*x\)', r'e^(\1x)', s)
    s = re.sub(r'exp\((.+?)\)', r'e^(\1)', s)

    # log(x) → ln(x)
    s = re.sub(r'\blog\b\(', 'ln(', s)

    # x**2 → x²  وهكذا
    superscripts = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴',
                    '5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    def replace_power(m):
        base = m.group(1)
        exp  = m.group(2)
        if len(exp) == 1 and exp in superscripts:
            return f"{base}{superscripts[exp]}"
        return f"{base}^({exp})"

    s = re.sub(r'(\w+)\*\*(\d+)', replace_power, s)

    # C1 → C₁ , C2 → C₂
    subscripts = {'1':'₁','2':'₂','3':'₃'}
    for d, sub in subscripts.items():
        s = s.replace(f'C{d}', f'C{sub}')

    # ضرب ضمني: 2*x → 2x
    s = re.sub(r'(\d)\*([a-zA-Z])', r'\1\2', s)
    s = re.sub(r'([a-zA-Z])\*([a-zA-Z])', r'\1·\2', s)

    # تنظيف مسافات
    s = re.sub(r'\s+', ' ', s).strip()

    return s


def _is_sympifiable(s):
    try:
        sympify(s)
        return True
    except:
        return False
