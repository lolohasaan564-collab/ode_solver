# ═══════════════════════════════════════════════════════
#  solver.py  —  الحل خطوة بخطوة
# ═══════════════════════════════════════════════════════
from sympy import *

x  = symbols('x')
y  = Function('y')
C1 = symbols('C1')
C2 = symbols('C2')

# ══════════════════════════════════════════════════════
#  دالة الحل الشاملة
# ══════════════════════════════════════════════════════

def solve_ode(ode_eq, ics: dict, hint: str = "best"):
    """
    يحل المعادلة ويُعيد (steps, solution_str, error)
    steps : قائمة من (رقم, عنوان, محتوى, تفصيل)
    """
    steps = []
    try:
        order = ode_order(ode_eq, y(x))
        hints = list(classify_ode(ode_eq, y(x)))
        best  = hints[0] if hints else "default"

        # ── اختيار خوارزمية الخطوات ──────────────────
        if best in ("separable",):
            steps = _steps_separable(ode_eq)
        elif best in ("1st_linear", "1st_linear_variable_coeff"):
            steps = _steps_linear_1st(ode_eq)
        elif best == "Bernoulli":
            steps = _steps_bernoulli(ode_eq)
        elif best == "1st_exact":
            steps = _steps_exact(ode_eq)
        elif best in ("1st_homogeneous_coeff_best",
                      "1st_homogeneous_coeff_subs_dep_expr",
                      "1st_homogeneous_coeff_subs_indep_div_dep"):
            steps = _steps_homogeneous(ode_eq)
        elif "nth_linear_constant_coeff" in best:
            steps = _steps_const_coeff(ode_eq)
        elif "euler" in best.lower():
            steps = _steps_cauchy_euler(ode_eq)
        else:
            steps = [{"num":1,"title":"التحليل التلقائي",
                      "work": f"النوع: {best}",
                      "detail":"يتم الحل بـ SymPy مباشرةً"}]

        # ── الحل النهائي ─────────────────────────────
        try:
            sol = dsolve(ode_eq, y(x), ics=ics if ics else None)
        except:
            sol = dsolve(ode_eq, y(x))

        # تنظيف الحل
        sol_rhs = sol.rhs if hasattr(sol, 'rhs') else sol

        steps.append({
            "num":    len(steps)+1,
            "title":  "✅ الحل النهائي",
            "work":   f"y(x) = {sol_rhs}",
            "detail": ""
        })

        # شرط ابتدائي
        if ics:
            steps.append({
                "num":    len(steps)+1,
                "title":  "🎯 تطبيق الشروط الابتدائية",
                "work":   f"y(x) = {sol_rhs}",
                "detail": f"الشروط: {ics}"
            })

        return steps, str(sol_rhs), None

    except Exception as e:
        return steps, "", str(e)


# ══════════════════════════════════════════════════════
#  خطوات كل طريقة
# ══════════════════════════════════════════════════════

def _steps_separable(eq):
    steps = []
    try:
        expr = eq.lhs - eq.rhs
        steps.append({"num":1,"title":"التعرف على الشكل",
            "work":"dy/dx = f(x) · g(y)",
            "detail":"نتحقق أن الطرف الأيمن يمكن فصله لضرب دالتين مستقلتين"})
        steps.append({"num":2,"title":"فصل المتغيرات",
            "work":"dy / g(y) = f(x) dx",
            "detail":"ننقل كل متغير لطرفه — تأكد g(y) ≠ 0"})
        steps.append({"num":3,"title":"التكامل من الطرفين",
            "work":"∫ dy/g(y) = ∫ f(x) dx + C",
            "detail":"نكامل كل طرف بشكل مستقل"})
        steps.append({"num":4,"title":"إيجاد الحل العام",
            "work":"نعبّر عن y صريحاً أو ضمنياً",
            "detail":"الحل يحتوي ثابت تعسفي C"})
    except:
        pass
    return steps

def _steps_linear_1st(eq):
    steps = []
    try:
        # كتابة بالشكل القياسي y' + P(x)y = Q(x)
        expr  = eq.lhs - eq.rhs
        coeff = expr.coeff(y(x).diff(x))
        rest  = simplify(expr - coeff * y(x).diff(x))
        P_sym = simplify(rest.coeff(y(x)) / coeff)
        Q_sym = simplify(-(rest - P_sym*coeff*y(x)) / coeff)

        mu_int = integrate(P_sym, x)
        mu     = simplify(exp(mu_int))

        steps.append({"num":1,"title":"الشكل القياسي",
            "work":f"dy/dx + ({P_sym})·y = {Q_sym}",
            "detail":"نرتب المعادلة بحيث معامل dy/dx = 1"})
        steps.append({"num":2,"title":"عامل التكامل μ(x)",
            "work":f"μ = e^(∫{P_sym} dx) = e^({mu_int}) = {mu}",
            "detail":"نحسب ∫P(x)dx ثم نرفع e"})
        steps.append({"num":3,"title":"الضرب في μ",
            "work":f"d/dx [μ·y] = μ·Q = {simplify(mu*Q_sym)}",
            "detail":"الطرف الأيسر أصبح مشتقاً كاملاً"})
        steps.append({"num":4,"title":"التكامل",
            "work":f"μ·y = ∫({simplify(mu*Q_sym)}) dx + C",
            "detail":"نكامل الطرف الأيمن"})
        steps.append({"num":5,"title":"الحل العام",
            "work":"y = [∫(μQ)dx + C] / μ",
            "detail":""})
    except:
        steps = [{"num":1,"title":"الحل التلقائي","work":"يتم الحل بـ SymPy","detail":""}]
    return steps

def _steps_bernoulli(eq):
    steps = []
    try:
        expr = eq.lhs - eq.rhs
        steps.append({"num":1,"title":"التعرف على معادلة برنولي",
            "work":"الشكل: dy/dx + P(x)·y = Q(x)·yⁿ",
            "detail":"نحدد قيمة n (يجب أن تكون n ≠ 0 و n ≠ 1)"})
        steps.append({"num":2,"title":"القسمة على yⁿ",
            "work":"y⁻ⁿ dy/dx + P(x)·y^(1-n) = Q(x)",
            "detail":"نحضّر للتعويض"})
        steps.append({"num":3,"title":"التعويض v = y^(1-n)",
            "work":"dv/dx = (1-n)·y^(-n)·dy/dx",
            "detail":"نعبّر عن المعادلة بدلالة v"})
        steps.append({"num":4,"title":"المعادلة الخطية في v",
            "work":"dv/dx + (1-n)·P(x)·v = (1-n)·Q(x)",
            "detail":"نطبق طريقة المعادلة الخطية"})
        steps.append({"num":5,"title":"الرجوع: y = v^(1/(1-n))",
            "work":"نستخرج y من الحل v(x)",
            "detail":"⚠️ y = 0 هي أيضاً حل ثابت"})
    except:
        pass
    return steps

def _steps_exact(eq):
    steps = []
    try:
        y_s = symbols('y')
        # استخراج M و N
        lhs  = eq.lhs - eq.rhs
        M    = lhs.coeff(symbols('dx')) if symbols('dx') in lhs.free_symbols else None
        # نستخدم SymPy مباشرة للتحليل
        steps.append({"num":1,"title":"التحقق من التمامة",
            "work":"نحسب ∂M/∂y و ∂N/∂x ونتأكد تساويهما",
            "detail":"إذا ∂M/∂y = ∂N/∂x → المعادلة تامة ✅"})
        steps.append({"num":2,"title":"إيجاد F(x,y)",
            "work":"F = ∫M dx + g(y)",
            "detail":"نكامل M بالنسبة لـ x مع ترك g(y) مجهولة"})
        steps.append({"num":3,"title":"إيجاد g(y)",
            "work":"∂F/∂y = N  →  نحل لـ g'(y) ثم نكامل",
            "detail":""})
        steps.append({"num":4,"title":"الحل: F(x,y) = C",
            "work":"نكتب الدالة الكاملة F وتساويها بثابت",
            "detail":""})
    except:
        pass
    return steps

def _steps_homogeneous(eq):
    steps = []
    steps.append({"num":1,"title":"التحقق من التجانس",
        "work":"M(tx,ty) = tⁿ·M(x,y) و N(tx,ty) = tⁿ·N(x,y)",
        "detail":"نعوّض tx, ty ونتأكد أن الدرجة تتلغى"})
    steps.append({"num":2,"title":"التعويض y = v·x",
        "work":"dy/dx = v + x·dv/dx",
        "detail":"نعوّض في المعادلة الأصلية"})
    steps.append({"num":3,"title":"فصل المتغيرات",
        "work":"نعزل dv وdx في طرفين منفصلين",
        "detail":""})
    steps.append({"num":4,"title":"التكامل",
        "work":"∫ dv/f(v) = ∫ dx/x + C",
        "detail":""})
    steps.append({"num":5,"title":"الرجوع: v = y/x",
        "work":"نعوّض v = y/x في الحل النهائي",
        "detail":""})
    return steps

def _steps_const_coeff(eq):
    steps = []
    try:
        r   = symbols('r')
        lhs = eq.lhs - eq.rhs
        # استخراج المعاملات
        a = lhs.coeff(y(x).diff(x, 2))
        b = lhs.coeff(y(x).diff(x))
        c = lhs.coeff(y(x))
        rhs_expr = simplify(-(lhs - a*y(x).diff(x,2) - b*y(x).diff(x) - c*y(x)))

        char = a*r**2 + b*r + c
        roots = solve(char, r)
        delta = b**2 - 4*a*c

        steps.append({"num":1,"title":"الشكل القياسي",
            "work":f"{a}y'' + {b}y' + {c}y = {rhs_expr}",
            "detail":"نتأكد أن المعاملات ثابتة"})
        steps.append({"num":2,"title":"المعادلة المميزة",
            "work":f"{a}r² + {b}r + {c} = 0",
            "detail":"نفترض y = eʳˣ ونعوّض"})
        steps.append({"num":3,"title":f"حل المعادلة المميزة (Δ = {delta})",
            "work":f"الجذور: r = {roots}",
            "detail":"Δ>0: جذران حقيقيان | Δ=0: جذر مكرر | Δ<0: جذران مركبان"})

        if delta > 0:
            r1, r2 = roots
            yh = f"C₁·e^({r1}x) + C₂·e^({r2}x)"
            case = "جذران حقيقيان مختلفان"
        elif delta == 0:
            r1 = roots[0]
            yh = f"(C₁ + C₂·x)·e^({r1}x)"
            case = "جذر مكرر"
        else:
            r1 = roots[0]
            alp, bet = re(r1), im(r1)
            yh = f"e^({alp}x)·[C₁·cos({bet}x) + C₂·sin({bet}x)]"
            case = "جذران مركبان"

        steps.append({"num":4,"title":f"الحالة: {case}",
            "work":f"yₕ = {yh}",
            "detail":""})

        if rhs_expr != 0:
            steps.append({"num":5,"title":"الحل الخاص yₚ",
                "work":"نطبق طريقة المعاملات غير المحددة أو تغيير الثوابت",
                "detail":"الحل العام = yₕ + yₚ"})
    except:
        steps = [{"num":1,"title":"الحل التلقائي","work":"يتم الحل بـ SymPy","detail":""}]
    return steps

def _steps_cauchy_euler(eq):
    steps = []
    try:
        m   = symbols('m')
        lhs = eq.lhs - eq.rhs
        a   = lhs.coeff(x**2 * y(x).diff(x,2))
        b   = lhs.coeff(x * y(x).diff(x))
        c   = lhs.coeff(y(x))

        indicial = a*m*(m-1) + b*m + c
        roots    = solve(indicial, m)

        steps.append({"num":1,"title":"التعرف على كوشي-أويلر",
            "work":f"{a}x²y'' + {b}xy' + {c}y = 0",
            "detail":"المعاملات: ax², bx, c (درجة متزايدة)"})
        steps.append({"num":2,"title":"التعويض y = xᵐ",
            "work":"y' = m·x^(m-1),  y'' = m(m-1)·x^(m-2)",
            "detail":"نعوّض في المعادلة"})
        steps.append({"num":3,"title":"المعادلة الإندائية",
            "work":f"{a}m(m-1) + {b}m + {c} = 0  →  m = {roots}",
            "detail":"نحل لإيجاد الجذور"})

        if len(roots) == 2 and roots[0] != roots[1]:
            if im(roots[0]) == 0:
                yh = f"C₁·x^({roots[0]}) + C₂·x^({roots[1]})"
                case = "جذران حقيقيان مختلفان"
            else:
                alp = re(roots[0]); bet = im(roots[0])
                yh  = f"x^({alp})·[C₁·cos({bet}·ln x) + C₂·sin({bet}·ln x)]"
                case = "جذران مركبان"
        else:
            m1   = roots[0]
            yh   = f"x^({m1})·(C₁ + C₂·ln x)"
            case = "جذر مكرر"

        steps.append({"num":4,"title":f"الحالة: {case}",
            "work":f"y = {yh}","detail":""})
    except:
        steps = [{"num":1,"title":"الحل التلقائي","work":"يتم الحل بـ SymPy","detail":""}]
    return steps
