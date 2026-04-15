import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
import io
import base64
import datetime

def clean_text(text):
    return str(text).encode("latin-1", "ignore").decode("latin-1")

st.set_page_config(
    page_title="Workforce Stability Lab",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)
st.markdown("""
<style>
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 1rem;
}

.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: #0D1B2A;
    border-bottom: 1px solid #E5EAF2;
    padding-bottom: 4px;
    margin-top: 18px;
    margin-bottom: 10px;
}

hr {
    margin-top: 10px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .main-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2.6rem;
        color: #0D1B2A;
        letter-spacing: -0.5px;
        margin-bottom: 0;
    }
    .sub-caption {
        color: #5C6E82;
        font-size: 0.95rem;
        margin-top: 0.2rem;
    }
    .kpi-card {
        background: #F5F8FF;
        border-left: 4px solid #1A56DB;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .kpi-label { font-size: 0.78rem; color: #5C6E82; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
    .kpi-value { font-size: 1.7rem; font-weight: 700; color: #0D1B2A; font-family: 'DM Serif Display', serif; }
    .kpi-delta-pos { color: #0e7f4e; font-size: 0.85rem; font-weight: 600; }
    .kpi-delta-neg { color: #c0392b; font-size: 0.85rem; font-weight: 600; }
    .risk-box-red    { background:#FEF2F2; border-left:4px solid #DC2626; border-radius:8px; padding:16px 20px; }
    .risk-box-orange { background:#FFF7ED; border-left:4px solid #EA580C; border-radius:8px; padding:16px 20px; }
    .risk-box-green  { background:#F0FDF4; border-left:4px solid #16A34A; border-radius:8px; padding:16px 20px; }
    .risk-text { font-size: 0.95rem; color: #1e293b; line-height:1.7; }
    .section-header {
        font-family: 'DM Serif Display', serif;
        font-size: 1.35rem;
        color: #0D1B2A;
        border-bottom: 2px solid #E5EAF2;
        padding-bottom: 6px;
        margin-top: 28px;
        margin-bottom: 14px;
    }
    .stButton>button {
        background: #1A56DB;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        padding: 12px 40px;
        width: 100%;
        cursor: pointer;
        transition: background 0.2s;
    }
    .stButton>button:hover { background: #1341B3; }
    .footer-text { color: #8899aa; font-size: 0.78rem; text-align: center; margin-top: 32px; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    .cost-highlight {
        background: linear-gradient(135deg, #0D1B2A 0%, #1A56DB 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
    }
    .cost-highlight .label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.7; }
    .cost-highlight .value { font-size: 2rem; font-weight: 700; font-family: 'DM Serif Display', serif; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown('<div class="main-title">⚡ Workforce Stability Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-caption">Strategic simulation engine for workforce risk & business impact modeling &nbsp;|&nbsp; Developed by Anchit Kunal</div>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================
# INDUSTRY BENCHMARK TABLE (Monthly)
# ============================================================

industry_benchmarks = {
    "IT / ITES":                     {"min": 0.008,  "max": 0.021},
    "Manufacturing":                 {"min": 0.007,  "max": 0.010},
    "Banking / Financial Services":  {"min": 0.007,  "max": 0.0125},
    "Healthcare":                    {"min": 0.008,  "max": 0.017},
}

col_ind, col_bench = st.columns([2, 3])
with col_ind:
    industry = st.selectbox("🏭 Industry Benchmark", list(industry_benchmarks.keys()))

bench_min = industry_benchmarks[industry]["min"]
bench_max = industry_benchmarks[industry]["max"]

with col_bench:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        f"**{industry}** — Monthly attrition benchmark: "
        f"**{bench_min*100:.1f}% – {bench_max*100:.1f}%** "
        f"(≈ **{bench_min*12*100:.0f}% – {bench_max*12*100:.0f}%** annually)"
    )

# ============================================================
# SIMULATION ENGINE
# ============================================================

def simulate_workforce(
    initial_employees, base_attrition, max_attrition,
    hr_capacity, revenue_per_fte, engagement_start,
    comp_gap, avg_salary, months=12
):
    RAMP        = [0.4, 0.7, 1.0]
    REPLACE_MULT = 1.5          # industry standard replacement cost multiplier

    employees   = float(initial_employees)
    engagement  = float(engagement_start)
    attrition   = float(base_attrition)
    prev_exits  = 0.0

    bucket_1 = bucket_2 = bucket_3 = 0.0
    experienced = employees
    results = []
    cumulative_cost = 0.0

    for month in range(1, months + 1):

        exits = employees * attrition
        exit_ratio = exits / employees if employees > 0 else 0

        experienced *= (1 - exit_ratio)
        bucket_1    *= (1 - exit_ratio)
        bucket_2    *= (1 - exit_ratio)
        bucket_3    *= (1 - exit_ratio)

        hires = min(hr_capacity, max(0.0, prev_exits))

        fully_productive_from_ramp = bucket_3
        bucket_3 = bucket_2
        bucket_2 = bucket_1
        bucket_1 = hires

        experienced += fully_productive_from_ramp
        employees = max(0.0, experienced + bucket_1 + bucket_2 + bucket_3)

        overload = (exits + hires) / hr_capacity if hr_capacity > 0 else 2.0
        engagement_change = 0.5 * (overload - 1)
        engagement = max(0, min(100, engagement - engagement_change))

        engagement_gap = engagement_start - engagement
        z = (0.02 * engagement_gap) + (1.0 * comp_gap)
        logistic_component = 1 / (1 + np.exp(-z))
        attrition = base_attrition + (max_attrition - base_attrition) * (
            (logistic_component - 0.5) * 2
        )
        attrition = max(0.0, min(max_attrition, attrition))

        revenue = (
            experienced  * revenue_per_fte
            + bucket_1   * RAMP[0] * revenue_per_fte
            + bucket_2   * RAMP[1] * revenue_per_fte
            + bucket_3   * RAMP[2] * revenue_per_fte
        )

        # Replacement cost this month
        monthly_replace_cost = exits * avg_salary * REPLACE_MULT
        cumulative_cost += monthly_replace_cost

        # Productivity loss (experienced gap vs full bench)
        productivity_loss = (initial_employees - employees) * revenue_per_fte if employees < initial_employees else 0.0

        results.append({
            "Month":                    month,
            "Employees":                employees,
            "Experienced":              experienced,
            "Attrition (%)":            attrition * 100,
            "Revenue":                  revenue,
            "Monthly Exits":            exits,
            "Monthly Replace Cost":     monthly_replace_cost,
            "Cumulative Replace Cost":  cumulative_cost,
            "Productivity Loss":        productivity_loss,
            "Engagement":               engagement,
        })

        prev_exits = exits

    return pd.DataFrame(results)

# ============================================================
# INPUT VALIDATION HELPER
# ============================================================

def validate_inputs(base, max_attr, hr_cap, emp):
    errors = []
    if base >= max_attr:
        errors.append("⚠️ Base Attrition must be **less than** Max Attrition.")
    if hr_cap <= 0:
        errors.append("⚠️ HR Capacity must be **greater than 0**.")
    if emp <= 0:
        errors.append("⚠️ Employee count must be **greater than 0**.")
    if base < 0 or max_attr < 0:
        errors.append("⚠️ Attrition rates cannot be **negative**.")
    return errors

# ============================================================
# SCENARIO INPUTS
# ============================================================

st.markdown('<div class="section-header">Scenario Configuration</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("#### 🟦 Scenario A — Base")
    emp_a      = st.number_input("Employees (A)", min_value=1, value=300, step=10)
    attr_a     = st.number_input("Base Attrition % (A)", min_value=0.0, max_value=99.0,
                                  value=round(bench_min * 100, 2), step=0.1) / 100
    max_attr_a = st.number_input("Max Attrition % (A)", min_value=0.0, max_value=99.0,
                                  value=round(bench_max * 100, 2), step=0.1) / 100
    hr_a       = st.number_input("HR Hiring Capacity / Month (A)", min_value=1, value=8, step=1)
    rev_a      = st.number_input("Revenue per FTE ₹ (A)", min_value=1000, value=80000, step=5000)
    sal_a      = st.number_input("Avg Annual Salary ₹ (A)", min_value=1000, value=600000, step=10000)
    engage_a   = st.slider("Engagement Score (A)", 0, 100, 75)
    comp_a     = st.number_input("Compensation Gap % (A)", min_value=0.0, max_value=100.0,
                                  value=0.0, step=0.5) / 100

with col2:
    st.markdown("#### 🟥 Scenario B — Stress")
    emp_b      = st.number_input("Employees (B)", min_value=1, value=300, step=10)
    attr_b     = st.number_input("Base Attrition % (B)", min_value=0.0, max_value=99.0,
                                  value=round(bench_max * 100, 2), step=0.1) / 100
    max_attr_b = st.number_input("Max Attrition % (B)", min_value=0.0, max_value=99.0,
                                  value=round(bench_max * 1.5 * 100, 2), step=0.1) / 100
    hr_b       = st.number_input("HR Hiring Capacity / Month (B)", min_value=1, value=5, step=1)
    rev_b      = st.number_input("Revenue per FTE ₹ (B)", min_value=1000, value=80000, step=5000)
    sal_b      = st.number_input("Avg Annual Salary ₹ (B)", min_value=1000, value=600000, step=10000)
    engage_b   = st.slider("Engagement Score (B)", 0, 100, 65)
    comp_b     = st.number_input("Compensation Gap % (B)", min_value=0.0, max_value=100.0,
                                  value=15.0, step=0.5) / 100

months = st.slider("📅 Projection Horizon (Months)", 6, 36, 12)

# ============================================================
# RUN SIMULATION
# ============================================================

run_col, _ = st.columns([1, 3])
with run_col:
    run = st.button("▶ Run Simulation")
def generate_pdf(
    df_a, df_b, industry, bench_min, bench_max, months,
    final_emp_a, final_emp_b, emp_diff,
    final_attr_a, final_attr_b, attr_diff,
    final_rev_a, final_rev_b, rev_diff,
    risk_icon, risk_text
):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_text("Workforce Stability Lab Report"), ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, clean_text("Strategic Workforce Simulation Output"), ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_text("Executive Summary"), ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, clean_text(f"Headcount Impact: {emp_diff:.1f}"), ln=True)
    pdf.cell(0, 6, clean_text(f"Attrition Change: {attr_diff:.2f}%"), ln=True)
    pdf.cell(0, 6, clean_text(f"Revenue Impact: Rs {rev_diff:,.0f}"), ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_text("Risk Assessment"), ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, clean_text(f"{risk_icon} {risk_text}"))

    # 🔥 IMPORTANT — THESE MUST BE INSIDE FUNCTION
    pdf_output = pdf.output(dest="S")
    pdf_output = pdf_output.replace("–", "-").replace("₹", "Rs")

    return pdf_output.encode("latin-1", "ignore")
if run:
    
    # --- Validate ---
    errors_a = validate_inputs(attr_a, max_attr_a, hr_a, emp_a)
    errors_b = validate_inputs(attr_b, max_attr_b, hr_b, emp_b)
    all_errors = [f"**Scenario A:** {e}" for e in errors_a] + \
                 [f"**Scenario B:** {e}" for e in errors_b]

    if all_errors:
        for err in all_errors:
            st.error(err)
        st.stop()

    # --- Simulate ---
    df_a = simulate_workforce(emp_a, attr_a, max_attr_a, hr_a, rev_a, engage_a, comp_a, sal_a, months)
    df_b = simulate_workforce(emp_b, attr_b, max_attr_b, hr_b, rev_b, engage_b, comp_b, sal_b, months)

    # ============================================================
    # KPI SUMMARY
    # ============================================================
    st.markdown('<div class="section-header">Executive KPI Summary</div>', unsafe_allow_html=True)

    final_emp_a    = df_a["Employees"].iloc[-1]
    final_emp_b    = df_b["Employees"].iloc[-1]
    final_attr_a   = df_a["Attrition (%)"].iloc[-1]
    final_attr_b   = df_b["Attrition (%)"].iloc[-1]
    final_rev_a    = df_a["Revenue"].iloc[-1]
    final_rev_b    = df_b["Revenue"].iloc[-1]
    cum_cost_a     = df_a["Cumulative Replace Cost"].iloc[-1]
    cum_cost_b     = df_b["Cumulative Replace Cost"].iloc[-1]
    total_exits_a  = df_a["Monthly Exits"].sum()
    total_exits_b  = df_b["Monthly Exits"].sum()

    emp_diff  = final_emp_b  - final_emp_a
    rev_diff  = final_rev_b  - final_rev_a
    attr_diff = final_attr_b - final_attr_a
    cost_diff = cum_cost_b   - cum_cost_a

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Headcount — Stress vs Base",
              f"{final_emp_b:.0f}", delta=f"{emp_diff:+.0f} employees",
              delta_color="inverse")
    k2.metric("Final Attrition % — Stress",
              f"{final_attr_b:.2f}%", delta=f"{attr_diff:+.2f}%",
              delta_color="inverse")
    k3.metric("Monthly Revenue — Stress",
              f"₹{final_rev_b:,.0f}", delta=f"₹{rev_diff:+,.0f}",
              delta_color="normal")
    k4.metric("Cumulative Replace Cost — Stress",
              f"₹{cum_cost_b:,.0f}", delta=f"₹{cost_diff:+,.0f} vs Base",
              delta_color="inverse")

    # REPLACEMENT COST CALLOUT
    st.markdown("<br>", unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.markdown(f"""
        <div class="cost-highlight">
            <div class="label">Total Exits — Base Scenario</div>
            <div class="value">{total_exits_a:.0f} people</div>
            <div style="opacity:0.75;font-size:0.82rem;margin-top:4px;">₹{cum_cost_a:,.0f} replacement cost</div>
        </div>""", unsafe_allow_html=True)
    with cc2:
        st.markdown(f"""
        <div class="cost-highlight">
            <div class="label">Total Exits — Stress Scenario</div>
            <div class="value">{total_exits_b:.0f} people</div>
            <div style="opacity:0.75;font-size:0.82rem;margin-top:4px;">₹{cum_cost_b:,.0f} replacement cost</div>
        </div>""", unsafe_allow_html=True)
    with cc3:
        incremental = cum_cost_b - cum_cost_a
        st.markdown(f"""
        <div class="cost-highlight" style="background:linear-gradient(135deg,#7f1d1d 0%,#DC2626 100%);">
            <div class="label">Incremental Cost of Stress</div>
            <div class="value">₹{incremental:,.0f}</div>
            <div style="opacity:0.75;font-size:0.82rem;margin-top:4px;">Based on 1.5× avg salary × exits</div>
        </div>""", unsafe_allow_html=True)

    # ============================================================
    # STRATEGIC INTERPRETATION
    # ============================================================
    st.markdown('<div class="section-header">Strategic Interpretation</div>', unsafe_allow_html=True)

    final_attr_pct = final_attr_b / 100
    if final_attr_pct > bench_max:
        risk_cls  = "risk-box-red"
        risk_icon = "🔴"
        risk_text = "high workforce instability — significantly above industry benchmarks. Immediate intervention recommended: review compensation banding, HR capacity, and engagement programs."
    elif final_attr_pct > bench_min:
        risk_cls  = "risk-box-orange"
        risk_icon = "🟠"
        risk_text = "moderate attrition pressure, tracking within the upper industry range. Monitor leading indicators — engagement scores and comp gaps — before conditions worsen."
    else:
        risk_cls  = "risk-box-green"
        risk_icon = "🟢"
        risk_text = "stable workforce dynamics, operating below the benchmark range. Maintain current retention levers and use the cost headroom for proactive talent investment."

    st.markdown(f"""
    <div class="{risk_cls}">
    <div class="risk-text">
    <strong>{risk_icon} Overall Assessment</strong><br><br>
    Under the stress scenario, the organization is experiencing <strong>{risk_text}</strong><br><br>
    <strong>Key deltas vs Base Scenario:</strong><br>
    • Headcount changes by <strong>{emp_diff:+.1f} employees</strong> at month {months}<br>
    • Monthly revenue shifts by <strong>₹{rev_diff:+,.0f}</strong><br>
    • Attrition stabilizes at <strong>{final_attr_b:.2f}%</strong> (Base: {final_attr_a:.2f}%)<br>
    • Incremental replacement cost: <strong>₹{cost_diff:+,.0f}</strong> over {months} months
    </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # PLOTLY CHARTS
    # ============================================================
    #st.markdown('<div class="section-header">Visual Analysis</div>', unsafe_allow_html=True)

    COLORS = {"A": "#1A56DB", "B": "#DC2626", "bench_min": "#16A34A", "bench_max": "#EA580C"}

    def style_fig(fig):
        fig.update_layout(
            font_family="DM Sans",
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=320,  # tighter
            margin=dict(l=10, r=10, t=35, b=10),  # tighter
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="left",
                x=0
                ),
                hovermode="x unified",
        )
        fig.update_xaxes(showgrid=True, gridcolor="#E5EAF2", title="")
        fig.update_yaxes(showgrid=True, gridcolor="#E5EAF2")
        return fig

    # --- Chart 1: Headcount ---
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_a["Month"], y=df_a["Employees"],
                              name="Scenario A — Base", line=dict(color=COLORS["A"], width=2.5)))
    fig1.add_trace(go.Scatter(x=df_b["Month"], y=df_b["Employees"],
                              name="Scenario B — Stress", line=dict(color=COLORS["B"], width=2.5, dash="dot")))
    
    fig1.add_hline(y=emp_a, line_dash="dash", line_color="#94a3b8",
                   annotation_text="Initial Headcount", annotation_position="right")
    fig1.update_layout(title="Headcount Projection", yaxis_title="Employees")
    style_fig(fig1)

    # --- Chart 2: Attrition ---
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_a["Month"], y=df_a["Attrition (%)"],
                              name="Scenario A — Base", line=dict(color=COLORS["A"], width=2.5)))
    fig2.add_trace(go.Scatter(x=df_b["Month"], y=df_b["Attrition (%)"],
                              name="Scenario B — Stress", line=dict(color=COLORS["B"], width=2.5, dash="dot")))
    fig2.add_hrect(y0=bench_min * 100, y1=bench_max * 100,
                   fillcolor="#16A34A", opacity=0.08,
                   annotation_text=f"{industry} Benchmark", annotation_position="top left")
    fig2.update_layout(title="Monthly Attrition Rate (%)", yaxis_title="Attrition %")
    style_fig(fig2)

    # --- Chart 3: Revenue ---
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df_a["Month"], y=df_a["Revenue"],
                              name="Scenario A — Base", line=dict(color=COLORS["A"], width=2.5),
                              fill="tozeroy", fillcolor="rgba(26,86,219,0.07)"))
    fig3.add_trace(go.Scatter(x=df_b["Month"], y=df_b["Revenue"],
                              name="Scenario B — Stress", line=dict(color=COLORS["B"], width=2.5, dash="dot"),
                              fill="tozeroy", fillcolor="rgba(220,38,38,0.05)"))
    fig3.update_layout(title="Monthly Revenue Projection (₹)", yaxis_title="Revenue (₹)")
    style_fig(fig3)

    # --- Chart 4: Cumulative Replacement Cost ---
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=df_a["Month"], y=df_a["Monthly Replace Cost"],
                          name="Scenario A — Base", marker_color=COLORS["A"], opacity=0.8))
    fig4.add_trace(go.Bar(x=df_b["Month"], y=df_b["Monthly Replace Cost"],
                          name="Scenario B — Stress", marker_color=COLORS["B"], opacity=0.8))
    fig4.update_layout(title="Monthly Replacement Cost (₹) [1.5× Avg Salary × Exits]",
                       yaxis_title="₹", barmode="group")
    style_fig(fig4)

    # --- Chart 5: Engagement Decay ---
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=df_a["Month"], y=df_a["Engagement"],
                              name="Scenario A — Base", line=dict(color=COLORS["A"], width=2.5)))
    fig5.add_trace(go.Scatter(x=df_b["Month"], y=df_b["Engagement"],
                              name="Scenario B — Stress", line=dict(color=COLORS["B"], width=2.5, dash="dot")))
    fig5.add_hline(y=60, line_dash="dash", line_color="#EA580C",
                   annotation_text="Engagement Risk Threshold (60)", annotation_position="right")
    fig5.update_layout(title="Employee Engagement Score Over Time", yaxis_title="Engagement (0–100)")
    style_fig(fig5)

    # --- Chart 6: Cumulative Replace Cost Line ---
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(x=df_a["Month"], y=df_a["Cumulative Replace Cost"],
                              name="Scenario A — Base", line=dict(color=COLORS["A"], width=2.5)))
    fig6.add_trace(go.Scatter(x=df_b["Month"], y=df_b["Cumulative Replace Cost"],
                              name="Scenario B — Stress", line=dict(color=COLORS["B"], width=2.5, dash="dot")))
    fig6.update_layout(title="Cumulative Replacement Cost (₹)", yaxis_title="₹")
    style_fig(fig6)

    st.markdown('<div class="section-header">Visual Analysis</div>', unsafe_allow_html=True)
    
    row1 = st.columns(2)
    row1[0].plotly_chart(fig1, use_container_width=True)
    row1[1].plotly_chart(fig2, use_container_width=True)
    
    row2 = st.columns(2)
    row2[0].plotly_chart(fig3, use_container_width=True)
    row2[1].plotly_chart(fig4, use_container_width=True)
    
    row3 = st.columns(2)
    row3[0].plotly_chart(fig5, use_container_width=True)
    row3[1].plotly_chart(fig6, use_container_width=True)

    # ============================================================
    # DATA TABLE
    # ============================================================
    st.markdown('<div class="section-header">Raw Simulation Data</div>', unsafe_allow_html=True)
    tab_a, tab_b = st.tabs(["Scenario A — Base", "Scenario B — Stress"])
    with tab_a:
        fmt_a = df_a.copy()
        for c in ["Revenue", "Monthly Replace Cost", "Cumulative Replace Cost", "Productivity Loss"]:
            fmt_a[c] = fmt_a[c].apply(lambda x: f"₹{x:,.0f}")
        fmt_a["Employees"]    = fmt_a["Employees"].apply(lambda x: f"{x:.1f}")
        fmt_a["Attrition (%)"]= fmt_a["Attrition (%)"].apply(lambda x: f"{x:.3f}%")
        fmt_a["Engagement"]   = fmt_a["Engagement"].apply(lambda x: f"{x:.1f}")
        st.dataframe(fmt_a, use_container_width=True, hide_index=True)

    with tab_b:
        fmt_b = df_b.copy()
        for c in ["Revenue", "Monthly Replace Cost", "Cumulative Replace Cost", "Productivity Loss"]:
            fmt_b[c] = fmt_b[c].apply(lambda x: f"₹{x:,.0f}")
        fmt_b["Employees"]    = fmt_b["Employees"].apply(lambda x: f"{x:.1f}")
        fmt_b["Attrition (%)"]= fmt_b["Attrition (%)"].apply(lambda x: f"{x:.3f}%")
        fmt_b["Engagement"]   = fmt_b["Engagement"].apply(lambda x: f"{x:.1f}")
        st.dataframe(fmt_b, use_container_width=True, hide_index=True)

    # ============================================================
    # PDF EXPORT
    # ============================================================
   
          
        # =========================
        # EXPORT (FINAL FIX)
        # =========================
    
    st.markdown('<div class="section-header">Export</div>', unsafe_allow_html=True)
    
    try:
        pdf_bytes = generate_pdf(
            df_a, df_b, industry, bench_min, bench_max, months,
            final_emp_a, final_emp_b, emp_diff,
            final_attr_a, final_attr_b, attr_diff,
            final_rev_a, final_rev_b, rev_diff,
            risk_icon, risk_text
        )
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.download_button(
                "📄 Download PDF",
                pdf_bytes,
                file_name="workforce_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            csv = pd.concat([df_a, df_b])
            st.download_button(
                "📊 Download CSV",
                csv.to_csv(index=False).encode(),
                file_name="data.csv",
                mime="text/csv",
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"Export failed: {e}")
                
        # ============================================================
        # FOOTER
        # ============================================================
        st.markdown("---")
        st.markdown(
            '<div class="footer-text">Workforce Stability Lab &nbsp;|&nbsp; '
            'Developed by <strong>Anchit Kunal</strong> &nbsp;|&nbsp; '
            'MBA — HR Analytics &nbsp;|&nbsp; Educational Simulation Tool</div>',
            unsafe_allow_html=True
        )