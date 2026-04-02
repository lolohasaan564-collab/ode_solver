# ═══════════════════════════════════════════════════════
#  app.py  —  واجهة Streamlit
#  تشغيل: streamlit run app.py
# ═══════════════════════════════════════════════════════
import streamlit as st
from sympy import *
from parser   import parse_equation, build_ics
from classifier import classify
from solver    import solve_ode

# ── إعداد الصفحة ────────────────────────────────────────
st.set_page_config(
    page_title="ODE Solver — حل المعادلات التفاضلية",
    page_icon="📐",
    layout="wide",
)

# ── CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', sans-serif !important; }

.stApp { background: linear-gradient(135deg,#07071a 0%,#0b0b22 100%); direction:rtl; }

/* عناوين */
h1,h2,h3 { color: #00d4ff !important; }

/* بطاقة التصنيف */
.classify-box {
    background: rgba(0,212,255,0.07);
    border: 1.5px solid rgba(0,212,255,0.3);
    border-radius: 14px;
    padding: 18px 22px;
    margin: 12px 0;
}
.classify-title { color:#00d4ff; font-weight:900; font-size:16px; margin-bottom:6px; }
.classify-en    { color:rgba(255,255,255,0.45); font-size:13px; }
.classify-desc  { color:rgba(255,255,255,0.7); font-size:13px; margin-top:8px; line-height:1.8; }
.order-badge    {
    display:inline-block;
    background: linear-gradient(135deg,#00d4ff22,#b44fff22);
    border: 1px solid #b44fff55;
    border-radius:20px; padding:3px 14px;
    color:#b44fff; font-size:12px; font-weight:700;
    margin-bottom:8px;
}

/* خطوات الحل */
.step-wrap {
    border-right: 3px solid #00d4ff44;
    margin: 8px 0 8px 0;
    padding-right: 16px;
}
.step-header {
    display:flex; align-items:center; gap:10px; margin-bottom:6px;
}
.step-num {
    background: linear-gradient(135deg,#00d4ff,#b44fff);
    color:#000; font-weight:900;
    width:28px; height:28px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:13px; flex-shrink:0;
}
.step-title { color:white; font-weight:700; font-size:15px; }
.step-work  {
    background:rgba(0,0,0,0.4); border:1px solid rgba(0,212,255,0.15);
    border-radius:8px; padding:9px 14px;
    font-family:monospace; color:#00d4ff;
    direction:ltr; text-align:left; font-size:14px;
    margin: 6px 0;
}
.step-detail { color:rgba(255,255,255,0.45); font-size:12px; margin-top:4px; }

/* الحل النهائي */
.final-box {
    background: rgba(0,255,136,0.07);
    border: 2px solid rgba(0,255,136,0.35);
    border-radius:14px; padding:20px 24px; margin:20px 0;
    text-align:center;
}
.final-label { color:#00ff88; font-weight:900; font-size:15px; margin-bottom:10px; text-align:right; }
.final-sol   { color:#00ff88; font-family:monospace; font-size:18px; direction:ltr; }

/* حقول الإدخال */
div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label { color:rgba(255,255,255,0.8)!important; }

.stTextInput>div>div>input, .stSelectbox>div>div {
    background:rgba(255,255,255,0.05)!important;
    border:1px solid rgba(255,255,255,0.15)!important;
    color:white!important; border-radius:10px!important;
}

/* زر الحل */
.stButton>button {
    background:linear-gradient(135deg,#00d4ff,#b44fff)!important;
    color:#000!important; font-weight:900!important;
    border:none!important; border-radius:12px!important;
    padding:12px 30px!important; font-size:16px!important;
    width:100%!important;
}

/* تنبيه */
.warn-box {
    background:rgba(255,71,87,0.08); border:1px solid rgba(255,71,87,0.3);
    border-radius:10px; padding:12px 16px; color:#ff6b7a; font-size:13px;
    margin:10px 0;
}
.tip-box {
    background:rgba(255,215,0,0.07); border:1px solid rgba(255,215,0,0.25);
    border-radius:10px; padding:12px 16px; color:#ffd700;
    font-size:13px; line-height:1.8; margin:12px 0;
}
hr { border-color:rgba(255,255,255,0.08)!important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; padding:10px 0 4px">
  <h1 style="font-size:2.6rem; font-weight:900; margin:0;
      background:linear-gradient(135deg,#00d4ff,#b44fff,#ff6b9d);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
      📐 حل المعادلات التفاضلية
  </h1>
  <p style="color:rgba(255,255,255,0.4); font-size:14px; margin-top:6px;">
      أدخل معادلتك بالشكل العادي · تصنيف تلقائي · خطوة بخطوة
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")


# ══════════════════════════════════════════════════════════
#  الخطوة 1 — إدخال المعادلة
# ══════════════════════════════════════════════════════════
st.markdown("## الخطوة 1 — أدخل المعادلة")

col_input, col_guide = st.columns([3, 2])

with col_input:
    eq_input = st.text_input(
        "المعادلة التفاضلية",
        value="y' + 2y = 4x",
        placeholder="مثال: y'' - 3y' + 2y = 0",
        help="يمكنك كتابة y', dy/dx, y'', d²y/dx²"
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        x0_input = st.number_input("x₀", value=0.0, help="نقطة الشرط الابتدائي")
    with col_b:
        y0_input = st.text_input("y(x₀) =", value="", placeholder="مثال: 1")
    with col_c:
        dy0_input = st.text_input("y'(x₀) =", value="", placeholder="للرتبة الثانية")

    solve_btn = st.button("⚡  احسب الحل", use_container_width=True)

with col_guide:
    st.markdown("""
    <div class="tip-box">
    <b>📖 طريقة الكتابة:</b><br>
    <code style="color:#00d4ff">y'</code> &nbsp; أو &nbsp; <code style="color:#00d4ff">dy/dx</code> &nbsp; → المشتق الأول<br>
    <code style="color:#00d4ff">y''</code> &nbsp; أو &nbsp; <code style="color:#00d4ff">d²y/dx²</code> &nbsp; → المشتق الثاني<br>
    <code style="color:#00d4ff">exp(x)</code> &nbsp; → eˣ &nbsp;|&nbsp;
    <code style="color:#00d4ff">sin(x)</code>, <code style="color:#00d4ff">cos(x)</code><br>
    <code style="color:#00d4ff">x**2</code> &nbsp; أو &nbsp; <code style="color:#00d4ff">x^2</code> &nbsp; → x²
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**أمثلة سريعة:**")
    EXAMPLES = [
        ("y' + 2y = 4x",           "خطية رتبة أولى"),
        ("y' = x*y",               "فصل متغيرات"),
        ("y' - y = x*y^3",         "برنولي"),
        ("y'' - 3y' + 2y = 0",     "معاملات ثابتة"),
        ("y'' + 4y = sin(x)",      "غير متجانسة"),
        ("x^2*y'' - 3*x*y' + 4*y = 0", "كوشي-أويلر"),
    ]
    for eq_ex, label in EXAMPLES:
        if st.button(f"  {eq_ex}  —  {label}", use_container_width=True, key=eq_ex):
            st.session_state['eq_example'] = eq_ex
            st.rerun()

if 'eq_example' in st.session_state:
    st.info(f"✅ انسخ هذه المعادلة في الخانة: `{st.session_state['eq_example']}`")


# ══════════════════════════════════════════════════════════
#  التنفيذ عند الضغط
# ══════════════════════════════════════════════════════════
if solve_btn and eq_input.strip():
    st.markdown("---")

    # ── الخطوة 2: التصنيف ───────────────────────────────
    st.markdown("## الخطوة 2 — التصنيف التلقائي")

    parse_ok   = True
    ode_eq     = None
    parse_error = ""

    try:
        ode_eq = parse_equation(eq_input)
    except Exception as e:
        parse_ok    = False
        parse_error = str(e)

    if not parse_ok:
        st.markdown(f'<div class="warn-box">⚠️ خطأ في قراءة المعادلة: {parse_error}<br>'
                    'تأكد من الصيغة — مثال: <code>y\' + 2*y = 4*x</code></div>',
                    unsafe_allow_html=True)
        st.stop()

    order, type_ar, type_en, order_str, hints, desc = classify(ode_eq)

    st.markdown(f"""
    <div class="classify-box">
        <div class="order-badge">رتبة {order_str}</div>
        <div class="classify-title">🔖 {type_ar}</div>
        <div class="classify-en">{type_en}</div>
        {"<div class='classify-desc'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)

    if order is None:
        st.markdown('<div class="warn-box">⚠️ تعذّر التصنيف — تأكد من صياغة المعادلة</div>',
                    unsafe_allow_html=True)
        st.stop()


    # ── الخطوة 3: الحل ──────────────────────────────────
    st.markdown("---")
    st.markdown("## الخطوة 3 — الحل خطوة بخطوة")

    ics = build_ics(x0_input, y0_input, dy0_input)

    with st.spinner("⏳ جاري الحل..."):
        steps, sol_str, error = solve_ode(ode_eq, ics)

    if error and not steps:
        st.markdown(f'<div class="warn-box">⚠️ لم يتمكن من الحل: {error}</div>',
                    unsafe_allow_html=True)
        st.stop()

    # عرض الخطوات
    for step in steps:
        is_final = "✅" in step['title'] or "🎯" in step['title']
        border_color = "#00ff88" if is_final else "#00d4ff"

        st.markdown(f"""
        <div class="step-wrap" style="border-right-color:{border_color}44">
            <div class="step-header">
                <div class="step-num" style="{'background:#00ff88' if is_final else ''}">{step['num']}</div>
                <div class="step-title">{step['title']}</div>
            </div>
            <div class="step-work" style="{'color:#00ff88;border-color:rgba(0,255,136,0.2)' if is_final else ''}">
                {step['work']}
            </div>
            {"<div class='step-detail'>"+step['detail']+"</div>" if step.get('detail') else ""}
        </div>
        """, unsafe_allow_html=True)

    # الحل النهائي بارز
    if sol_str:
        st.markdown(f"""
        <div class="final-box">
            <div class="final-label">✅ الحل العام</div>
            <div class="final-sol">y(x) = {sol_str}</div>
        </div>
        """, unsafe_allow_html=True)

    if error:
        st.markdown(f'<div class="warn-box">⚠️ ملاحظة: {error}</div>',
                    unsafe_allow_html=True)

    # نصيحة للتحقق
    st.markdown("""
    <div class="tip-box">
    💡 <b>للتحقق من الحل:</b> عوّض y(x) في المعادلة الأصلية — يجب أن تتحقق المعادلة بشكل متطابق.
    </div>
    """, unsafe_allow_html=True)


elif solve_btn:
    st.warning("⚠️ من فضلك أدخل معادلة أولاً")


# ══════════════════════════════════════════════════════════
#  جدول أنواع المعادلات
# ══════════════════════════════════════════════════════════
with st.expander("📚 جدول أنواع المعادلات التفاضلية"):
    st.markdown("""
    <div style="direction:rtl">

    ### الرتبة الأولى
    | النوع | الشكل | طريقة الحل |
    |-------|-------|------------|
    | فصل المتغيرات | dy/dx = f(x)·g(y) | نفصل dy و dx |
    | اختزال لفصل المتغيرات | dy/dx = f(ax+by) | v = ax+by |
    | خطية | y' + P(x)y = Q(x) | عامل التكامل μ |
    | برنولي | y' + Py = Qyⁿ | v = y^(1-n) |
    | متجانسة | dy/dx = f(y/x) | y = vx |
    | غير متجانسة | dy/dx = f(ax+by+c)/g(...) | تحويل المحاور |
    | تامة | M dx + N dy = 0، ∂M/∂y = ∂N/∂x | F(x,y) = C |
    | غير تامة | ∂M/∂y ≠ ∂N/∂x | عامل تكامل μ(x) أو μ(y) |

    ### الرتبة الثانية
    | النوع | الشكل | طريقة الحل |
    |-------|-------|------------|
    | خطية متجانسة / معاملات ثابتة | ay''+by'+cy=0 | المعادلة المميزة r² |
    | خطية غير متجانسة | ay''+by'+cy=R(x) | yₕ + yₚ |
    | كوشي-أويلر | ax²y''+bxy'+cy=0 | y = xᵐ |
    | ذاتية (Autonomous) | y''=f(y,y') بدون x | p=y'، dp/dx=p·dp/dy |
    | قابلة للاختزال (y غائبة) | y''=f(x,y') | p=y' |
    | قابلة للاختزال (x غائبة) | y''=f(y,y') | p=y' كدالة في y |

    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:rgba(255,255,255,0.18);font-size:11px;padding:8px">
    ODE Solver &nbsp;·&nbsp; Python + SymPy + Streamlit
</div>
""", unsafe_allow_html=True)
