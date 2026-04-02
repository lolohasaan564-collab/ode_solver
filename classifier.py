# ═══════════════════════════════════════════════════════
#  classifier.py  —  تصنيف المعادلة التفاضلية
# ═══════════════════════════════════════════════════════
from sympy import *

x = symbols('x')
y = Function('y')

# ── خريطة أنواع SymPy → وصف عربي ──────────────────────
SYMPY_TO_AR = {
    # رتبة أولى
    "separable":                  ("فصل المتغيرات",       "Separable",                    "الأولى"),
    "separable_reduced":          ("اختزال لفصل المتغيرات","Reduced to Separable",         "الأولى"),
    "1st_linear":                 ("خطية",                "Linear (1st order)",            "الأولى"),
    "Bernoulli":                  ("برنولي",              "Bernoulli",                     "الأولى"),
    "1st_homogeneous_coeff_subs_dep_expr":
                                  ("متجانسة",             "Homogeneous",                   "الأولى"),
    "1st_homogeneous_coeff_subs_indep_div_dep":
                                  ("متجانسة",             "Homogeneous",                   "الأولى"),
    "1st_homogeneous_coeff_best":("متجانسة",              "Homogeneous",                   "الأولى"),
    "1st_exact":                  ("تامة",                "Exact",                         "الأولى"),
    "almost_linear":              ("شبه خطية",            "Almost Linear",                 "الأولى"),
    "1st_rational_riccati":       ("ريكاتي",              "Riccati",                       "الأولى"),
    "1st_linear_variable_coeff":  ("خطية (معاملات متغيرة)","Linear Variable Coeff",        "الأولى"),
    "lie_group":                  ("مجموعة لي",           "Lie Group",                     "الأولى"),
    "1st_power_series":           ("متسلسلة قوى",         "Power Series",                  "الأولى"),
    # رتبة ثانية
    "nth_linear_constant_coeff_homogeneous":
                                  ("خطية متجانسة / معاملات ثابتة",
                                   "Linear Homogeneous – Const. Coeff.",                   "الثانية"),
    "nth_linear_constant_coeff_undetermined_coefficients":
                                  ("خطية غير متجانسة / معاملات غير محددة",
                                   "Linear Non-Hom. – Undetermined Coeff.",                "الثانية"),
    "nth_linear_constant_coeff_variation_of_parameters":
                                  ("خطية غير متجانسة / تغيير الثوابت",
                                   "Linear Non-Hom. – Variation of Params",               "الثانية"),
    "nth_linear_euler_eq_homogeneous":
                                  ("كوشي-أويلر المتجانسة","Cauchy-Euler Homogeneous",      "الثانية"),
    "nth_linear_euler_eq_nonhomogeneous_undetermined_coefficients":
                                  ("كوشي-أويلر غير متجانسة","Cauchy-Euler Non-Homogeneous","الثانية"),
    "2nd_power_series_ordinary":  ("متسلسلة قوى (نقطة عادية)","Power Series – Ordinary",  "الثانية"),
    "2nd_power_series_regular":   ("متسلسلة قوى (نقطة شاذة منتظمة)","Power Series – Regular Singular","الثانية"),
    "Liouville":                  ("ليوفيل",              "Liouville",                     "الثانية"),
    "2nd_hypergeometric":         ("هايبرجيومترية",       "Hypergeometric",                "الثانية"),
}

def _detect_special_2nd(ode_eq):
    """كشف الأشكال الخاصة للرتبة الثانية يدوياً"""
    try:
        expr = ode_eq.lhs - ode_eq.rhs
        y_f  = y(x)
        yp   = y_f.diff(x)
        ypp  = y_f.diff(x, 2)

        has_x_explicit = x in expr.free_symbols

        # Autonomous: لا يظهر x صريحاً
        if not has_x_explicit and ypp in expr.atoms(Derivative):
            return "autonomous", "ذاتية (Autonomous)", "Autonomous", "الثانية"

        # Reducible: إما y غائبة أو x غائبة
        if y_f not in expr.atoms(Function):
            return "reducible_missing_y", "قابلة للاختزال (y غائبة)", "Reducible – Missing y", "الثانية"

        if not has_x_explicit:
            return "reducible_missing_x", "قابلة للاختزال (x غائبة)", "Reducible – Missing x", "الثانية"

    except:
        pass
    return None, None, None, None


def classify(ode_eq):
    """
    يصنّف المعادلة ويُعيد:
      order      : 1 أو 2
      type_ar    : الاسم بالعربي
      type_en    : الاسم بالإنجليزي
      order_str  : 'الأولى' | 'الثانية'
      sympy_hints: قائمة تلميحات SymPy
      description: شرح مختصر
    """
    try:
        order      = ode_order(ode_eq, y(x))
        hints      = list(classify_ode(ode_eq, y(x)))
        best_hint  = hints[0] if hints else ""

        # ابحث في الخريطة
        for hint in hints:
            if hint in SYMPY_TO_AR:
                ar, en, ord_s = SYMPY_TO_AR[hint]
                return order, ar, en, ord_s, hints, _description(hint)

        # كشف خاص للرتبة الثانية
        if order == 2:
            sid, ar, en, ord_s = _detect_special_2nd(ode_eq)
            if sid:
                return order, ar, en, ord_s, hints, _description(sid)

        # افتراضي
        if order == 1:
            return order, "رتبة أولى (نوع غير محدد)", "1st-Order (unclassified)", "الأولى", hints, ""
        else:
            return order, "رتبة ثانية (نوع غير محدد)", "2nd-Order (unclassified)", "الثانية", hints, ""

    except Exception as e:
        return None, "فشل التصنيف", str(e), "-", [], ""


def _description(hint):
    DESC = {
        "separable":
            "المعادلة يمكن كتابتها كـ dy/dx = f(x)·g(y)، نفصل المتغيرات ونكامل كلاً على حدة.",
        "separable_reduced":
            "المعادلة من الشكل dy/dx = f(ax+by)، نستخدم التعويض v=ax+by لاختزالها لمعادلة قابلة للفصل.",
        "1st_linear":
            "المعادلة خطية من الرتبة الأولى dy/dx + P(x)y = Q(x)، نحلها بعامل التكامل μ=e^(∫P dx).",
        "Bernoulli":
            "المعادلة من شكل برنولي dy/dx + P(x)y = Q(x)yⁿ، نستخدم التعويض v=y^(1-n) لاختزالها لخطية.",
        "1st_exact":
            "المعادلة تامة M dx + N dy = 0 حيث ∂M/∂y = ∂N/∂x، نجد دالة F بحيث dF = M dx + N dy.",
        "1st_homogeneous_coeff_best":
            "المعادلة متجانسة dy/dx = f(y/x)، نستخدم التعويض y=vx.",
        "nth_linear_constant_coeff_homogeneous":
            "معادلة خطية متجانسة بمعاملات ثابتة، نحل المعادلة المميزة ar²+br+c=0.",
        "nth_linear_constant_coeff_undetermined_coefficients":
            "معادلة خطية غير متجانسة، الحل = الحل المتجانس yₕ + الحل الخاص yₚ (طريقة المعاملات غير المحددة).",
        "nth_linear_euler_eq_homogeneous":
            "معادلة كوشي-أويلر ax²y''+bxy'+cy=0، نستخدم التعويض y=xᵐ.",
        "autonomous":
            "معادلة ذاتية y''=f(y,y') لا يظهر فيها x صريحاً، نستخدم p=y' و dp/dx=p dp/dy.",
        "reducible_missing_y":
            "y غائبة صريحاً، نضع p=y' فتصبح المعادلة من الرتبة الأولى في p(x).",
        "reducible_missing_x":
            "x غائبة صريحاً (معادلة ذاتية)، نضع p=y' كدالة في y.",
    }
    return DESC.get(hint, "")
