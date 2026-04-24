import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go


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
    max-width: 1100px;
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown("""
<style>

/* Page Width */
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}

/* Card UI */
.card{
background:white;
border:1px solid #E6EBF2;
border-radius:20px;
padding:24px 26px;
min-height:190px;              /* forces all KPI cards same height */
display:flex;
flex-direction:column;
justify-content:center;
box-shadow:0 4px 14px rgba(0,0,0,.04);
transition:.2s ease;
}

.card:hover{
transform:translateY(-2px);
box-shadow:0 8px 22px rgba(0,0,0,.06);
}

/* KPI titles */
.card .label{
font-size:1rem;
font-weight:500;
color:#667085;
margin-bottom:14px;
line-height:1.4;
}

/* Big KPI numbers */
.card .value{
font-size:1.95rem;
font-weight:700;
color:#1F2937;
line-height:1.1;
margin-bottom:10px;

white-space:nowrap;
overflow:hidden;
text-overflow:ellipsis;
letter-spacing:-0.02em;
}

/* Subtext */
.card .meta{
font-size:.9rem;
color:#8A94A6;
}


/* left accent cards */
.blue-card{
border-left:6px solid #2E86DE;
}

.amber-card{
border-left:6px solid #F39C12;
}

.red-card{
border-left:6px solid #E74C3C;
}


/* strategic interpretation */
.risk-box-red,
.risk-box-orange,
.risk-box-green{
border-radius:18px;
padding:28px 30px;
margin-top:20px;
box-shadow:0 4px 14px rgba(0,0,0,.04);
}

.risk-box-red{
background:#FFF5F5;
border-left:6px solid #DC2626;
}

.risk-box-orange{
background:#FFF8ED;
border-left:6px solid #F59E0B;
}

.risk-box-green{
background:#F0FDF4;
border-left:6px solid #16A34A;
}


/* section headers */
.section-header{
font-size:1.55rem;
font-weight:700;
margin-top:28px;
margin-bottom:18px;
color:#1F2937;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================


st.title("⚡ Workforce Stability Lab")
st.caption("Simulate workforce risk scenarios and business impact in real-time")
st.markdown('<div class="caption"> Developed by Anchit Kunal</div>', unsafe_allow_html=True)
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

col_ind, col_bench = st.columns([2,3], vertical_alignment="bottom")

with col_ind:
    industry = st.selectbox(
        "🏭 Industry Benchmark",
        list(industry_benchmarks.keys())
    )
# active benchmark values
bench_min = industry_benchmarks[industry]["min"]
bench_max = industry_benchmarks[industry]["max"]

with col_bench:
    st.markdown(f"""
    <div style="
        margin-top:28px;
        padding:18px 24px;
        border-radius:14px;
        background:#EEF5FF;
        border-left:6px solid #2E86DE;
        font-size:1.05rem;
        box-shadow:0 4px 12px rgba(0,0,0,0.04);
    ">
        <strong>{industry}</strong> Monthly attrition benchmark:
        <strong>{bench_min*100:.1f}%–{bench_max*100:.2f}%</strong>
        (≈{bench_min*12*100:.0f}%–{bench_max*12*100:.0f}% annually)
    </div>
    """, unsafe_allow_html=True)
# Active benchmark values (used across presets + simulation)

# ==========================================
# INDUSTRY PRESETS
# ==========================================

INDUSTRY_PRESETS = {

"IT / ITES": {
    "stable":{
        "attr_b":0.008,
        "max_attr_b":0.014,
        "hr_b":10,
        "engage_b":85,
        "comp_b":0.00
    },
    "moderate":{
        "attr_b":0.018,
        "max_attr_b":0.025,
        "hr_b":5,
        "engage_b":70,
        "comp_b":0.10
    },
    "high":{
        "attr_b":0.025,
        "max_attr_b":0.040,
        "hr_b":2,
        "engage_b":58,
        "comp_b":0.18
    }
},

"Manufacturing": {
    "stable":{
        "attr_b":0.006,
        "max_attr_b":0.009,
        "hr_b":6,
        "engage_b":82,
        "comp_b":0.02
    },
    "moderate":{
        "attr_b":0.010,
        "max_attr_b":0.014,
        "hr_b":4,
        "engage_b":68,
        "comp_b":0.08
    },
    "high":{
        "attr_b":0.018,
        "max_attr_b":0.035,
        "hr_b":2,
        "engage_b":55,
        "comp_b":0.15
    }
},

"Banking / Financial Services": {
    "stable":{
        "attr_b":0.008,
        "max_attr_b":0.011,
        "hr_b":7,
        "engage_b":80,
        "comp_b":0.03
    },
    "moderate":{
        "attr_b":0.013,
        "max_attr_b":0.018,
        "hr_b":4,
        "engage_b":67,
        "comp_b":0.09
    },
    "high":{
        "attr_b":0.022,
        "max_attr_b":0.030,
        "hr_b":2,
        "engage_b":52,
        "comp_b":0.16
    }
},

"Healthcare": {
    "stable":{
        "attr_b":0.009,
        "max_attr_b":0.013,
        "hr_b":8,
        "engage_b":81,
        "comp_b":0.03
    },
    "moderate":{
        "attr_b":0.015,
        "max_attr_b":0.021,
        "hr_b":5,
        "engage_b":66,
        "comp_b":0.09
    },
    "high":{
        "attr_b":0.024,
        "max_attr_b":0.04,
        "hr_b":2,
        "engage_b":50,
        "comp_b":0.17
    }
}

}

# ==========================================
# SHOCK SCENARIO LIBRARY
# ==========================================

SHOCK_SCENARIOS = {

"None": None,

"Hiring Freeze Shock":{
    "hr_b_mult":0.4,
    "attr_b_mult":1.15,
    "engage_delta":-8,
    "comp_gap_add":0.00
},

"Burnout Wave":{
    "hr_b_mult":0.8,
    "attr_b_mult":1.35,
    "engage_delta":-15,
    "comp_gap_add":0.00
},

"Compensation Compression":{
    "hr_b_mult":1.0,
    "attr_b_mult":1.25,
    "engage_delta":-6,
    "comp_gap_add":0.08
},

"Hypergrowth Attrition":{
    "hr_b_mult":0.6,
    "attr_b_mult":1.15,
    "engage_delta":-10,
    "comp_gap_add":0.05
}

}
# ============================================================
# SIMULATION ENGINE
# ============================================================

def simulate_workforce(
    initial_employees, base_attrition, max_attrition,
    hr_capacity, revenue_per_fte, engagement_start,
    comp_gap, avg_salary, months=12
):
    RAMP        = [0.4, 0.7, 1.0]
    replacement_multipliers = {
    "IT / ITES":2.2,
    "Manufacturing":1.4,
    "Banking / Financial Services":1.8,
    "Healthcare":2.0
    }
    
    REPLACE_MULT = replacement_multipliers.get(industry,1.7)          # industry standard replacement cost multiplier

    employees   = float(initial_employees)
    engagement  = float(engagement_start)
    attrition   = float(base_attrition)
    
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

        fill_rate = 0.72
        hires = min(hr_capacity, exits * fill_rate)

        fully_productive_from_ramp = bucket_3
        bucket_3 = bucket_2
        bucket_2 = bucket_1
        bucket_1 = hires

        experienced += fully_productive_from_ramp
        employees = max(0.0, experienced + bucket_1 + bucket_2 + bucket_3)

        overload = (0.4*exits + hires) / max(hr_capacity, exits,1) if hr_capacity > 0 else 2.0
        engagement_change = 1.2*(overload-1)
        engagement = max(0, min(100, engagement - engagement_change))

        engagement_gap = engagement_start - engagement
        z = -2.8 + (0.045 * engagement_gap) + (2.5 * comp_gap)
        logistic_component = 1 / (1 + np.exp(-z))
        attrition = base_attrition + (
            max_attrition-base_attrition
        ) * logistic_component
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
        productivity_loss=max( 0,
        (initial_employees*revenue_per_fte)-revenue
        ) if employees < initial_employees else 0.0

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

       
    return pd.DataFrame(results)

# ============================================================
# INPUT VALIDATION HELPER
# ============================================================

def validate_inputs(base, max_attr, hr_cap, emp):
    errors = []
    if base >= max_attr:
        errors.append("⚠️ Worst-case attrition must be **higher than** current attrition.")
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

# Reset state when preset changes
if "preset_last" not in st.session_state:
     st.session_state.preset_last = "Custom"

st.markdown("### Scenario Shock Library")

shock_choice = st.selectbox(
    "Apply Stress Event",
    list(SHOCK_SCENARIOS.keys())
)

st.markdown("<h3 style='margin-bottom:10px;'>Quick Scenarios</h3>", unsafe_allow_html=True)

col_p1, col_p2, col_p3 = st.columns(3)

preset_pack = INDUSTRY_PRESETS[industry]

with col_p1:
    if st.button("🟢 Stable", use_container_width=True):

        st.session_state.update(
            {"preset":"stable"} |
            preset_pack["stable"]
        )


with col_p2:
    if st.button("🟠 Moderate", use_container_width=True):

        st.session_state.update(
            {"preset":"moderate"} |
            preset_pack["moderate"]
        )


with col_p3:
    if st.button("🔴 High Risk", use_container_width=True):

        st.session_state.update(
            {"preset":"high"} |
            preset_pack["high"]
        )
preset = st.session_state.get("preset", "custom")

preset_desc = {
    "custom":"Input your own Custom scenario",
    "stable":f"{industry}: controlled workforce conditions",
    "moderate":f"{industry}: benchmark stress emerging",
    "high":f"{industry}: severe workforce instability"
}

st.caption(f"Scenario Logic: {preset_desc[preset]}")

# ============================================================
# SCENARIO INPUTS
# ============================================================

col1, col2 = st.columns(2, gap="large")

# ---------------- A ----------------
with col1:
    st.markdown("### 🟦 Scenario A — Base")

    emp_a = st.number_input("Employees (A)", 1, 10000, 300, key="emp_a")

    attr_a = st.number_input(
        "Current Attrition (%) (A)",
        value=st.session_state.get("attr_a", bench_min) * 100,
        key="attr_a"
    ) / 100

    max_attr_a = st.number_input(
        "Worst-Case Attrition (%) (A)",
        value=st.session_state.get("max_attr_a", bench_max) * 100,
        key="max_attr_a"
    ) / 100

    hr_a = st.number_input(
        "Hiring Capacity (A)",
        value=st.session_state.get("hr_a", 8),
        key="hr_a"
    )

    rev_a = st.number_input(
        "Revenue per FTE ₹ (A)",
        1000, 1000000, 80000,
        key="rev_a"
    )

    sal_a = st.number_input(
        "Avg Salary ₹ (A)",
        1000, 2000000, 600000,
        key="sal_a"
    )

    engage_a = st.slider(
        "Engagement (A)",
        0, 100,
        st.session_state.get("engage_a", 75),
        key="engage_a"
    )

    # FIXED % handling
    comp_a_val = st.session_state.get("comp_a", 0.0)
    if comp_a_val > 1:
        comp_a_val /= 100

    comp_a = st.number_input(
        "Market Pay Gap (%) (A)",
        0.0, 100.0,
        comp_a_val * 100,
        step=0.5,
        key="comp_a"
    ) / 100

# ---------------- B ----------------
with col2:
    st.markdown("### 🟥 Scenario B — Stress")

    emp_b = st.number_input("Employees (B)", 1, 10000, 300, key="emp_b")

    attr_b = st.number_input(
        "Current Attrition (%) (B)",
        value=st.session_state.get("attr_b", bench_max) * 100,
        key="attr_b"
    ) / 100

    max_attr_b = st.number_input(
        "Worst-Case Attrition (%) (B)",
        value=st.session_state.get("max_attr_b", bench_max * 1.5) * 100,
        key="max_attr_b"
    ) / 100

    hr_b = st.number_input(
        "Hiring Capacity (B)",
        value=st.session_state.get("hr_b", 5),
        key="hr_b"
    )

    rev_b = st.number_input(
        "Revenue per FTE ₹ (B)",
        1000, 1000000, 80000,
        key="rev_b"
    )

    sal_b = st.number_input(
        "Avg Salary ₹ (B)",
        1000, 2000000, 600000,
        key="sal_b"
    )

    engage_b = st.slider(
        "Engagement (B)",
        0, 100,
        st.session_state.get("engage_b", 65),
        key="engage_b"
    )

    # FIXED % handling
    comp_b_val = st.session_state.get("comp_b", 0.15)
    if comp_b_val > 1:
        comp_b_val /= 100

    comp_b = st.number_input(
        "Market Pay Gap (%) (B)",
        0.0, 100.0,
        comp_b_val * 100,
        step=0.5,
        key="comp_b"
    ) / 100
# ===============================
# SHOCK OVERLAY ENGINE (SAFE)
# ===============================

# preserve raw user inputs
sim_attr_b   = attr_b
sim_max_b    = max_attr_b
sim_hr_b     = hr_b
sim_engage_b = engage_b
sim_comp_b   = comp_b

if shock_choice != "None":

    shock = SHOCK_SCENARIOS[shock_choice]

    # apply shock ONLY to simulation copies
    sim_attr_b = attr_b * shock["attr_b_mult"]

    # keep logic valid automatically
    if sim_attr_b >= max_attr_b:
            sim_max_b = min(
    0.06,
    sim_attr_b*1.15
    )   # auto expand worst-case ceiling

    sim_hr_b = max(
        1,
        int(hr_b * shock["hr_b_mult"])
    )

    sim_engage_b = max(
        40,
        engage_b + shock["engage_delta"]
    )

    sim_comp_b = min(
        0.35,
        comp_b + shock["comp_gap_add"]
    )
# ============================================================
# TIME
# ============================================================

months = st.slider("📅 Projection Duration (Months)", 6, 36, 12)

# ============================================================
# RUN SIMULATION
# ============================================================

run = st.button("🚀 Run Simulation", use_container_width=True)
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
    errors_b = validate_inputs(
    sim_attr_b,
    sim_max_b,
    sim_hr_b,
    emp_b
)
    all_errors = [f"**Scenario A:** {e}" for e in errors_a] + \
                 [f"**Scenario B:** {e}" for e in errors_b]

    if all_errors:
        for err in all_errors:
            st.error(err)
        st.stop()

    # --- Simulate ---
    df_a = simulate_workforce(emp_a, attr_a, max_attr_a, hr_a, rev_a, engage_a, comp_a, sal_a, months)
    df_b = simulate_workforce(
    emp_b,
    sim_attr_b,
    sim_max_b,
    sim_hr_b,
    rev_b,
    sim_engage_b,
    sim_comp_b,
    sal_b,
    months
)

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

    k1, k2, k3 = st.columns(3)
    
    def kpi_card(title, value, delta=None):
        return f"""
        <div class="card">
            <div style="font-size:0.9rem; color:#666;">{title}</div>
            <div style="font-size:1.6rem; font-weight:600;">{value}</div>
            <div style="font-size:0.8rem; color:#888;">{delta if delta else ""}</div>
        </div>
        """

    k1.markdown(kpi_card("Headcount (Stress vs Base)", round(final_emp_b,1), "▼ Decline"), unsafe_allow_html=True)
    k2.markdown(kpi_card("Final Attrition (Stress)", f"{final_attr_b:.2f}%"), unsafe_allow_html=True)
    k3.markdown(kpi_card("Monthly Revenue (Stress)", f"₹{final_rev_b:,.0f}"), unsafe_allow_html=True)
        # k4.metric("Cumulative Replace Cost — Stress",
    #           f"₹{cum_cost_b:,.0f}", delta=f"₹{cost_diff:+,.0f} vs Base",
    #           delta_color="inverse")

    # REPLACEMENT COST CALLOUT
    st.markdown("<br>", unsafe_allow_html=True)
    
    cc1, cc2, cc3 = st.columns(3, gap="large")
    def short_money(n):
        if abs(n) >= 10000000:   # 1 crore
            return f"₹{n/10000000:.2f} Cr"
        elif abs(n) >= 100000:   # 1 lakh
            return f"₹{n/100000:.1f} L"
        else:
            return f"₹{n:,.0f}"
    
    with cc1:
        st.markdown(f"""
        <div class="card blue-card">
            <div class="label">Total Exits — Base Scenario</div>
            <div class="value">{total_exits_a:.0f} people</div>
            <div style="opacity:.75;font-size:0.85rem;margin-top:8px;">
            {short_money(cum_cost_a)} replacement cost
            <br>
            <span style="font-size:.72rem;">
            (₹{cum_cost_a:,.0f})
            </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cc2:
        st.markdown(f"""
        <div class="card amber-card">
            <div class="label">Total Exits — Stress Scenario</div>
            <div class="value">{total_exits_b:.0f} people</div>
            <div style="opacity:.75;font-size:0.85rem;margin-top:8px;">
            {short_money(cum_cost_b)} replacement cost
            <br>
            <span style="font-size:.72rem;">
            (₹{cum_cost_b:,.0f})
            </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    def short_money(x):
        if x >= 10000000:
            return f"₹{x/10000000:.2f} Cr"
        elif x >= 100000:
            return f"₹{x/100000:.1f} Lakh"
        else:
            return f"₹{x:,.0f}"
        
    with cc3:
        incremental = cum_cost_b - cum_cost_a
    
        label = "Incremental Cost of Stress"
        border_class = "red-card"
        
        if incremental >= 0:
            amount = short_money(incremental)
            meta = "Additional replacement cost vs base"
        else:
            amount = f"−{short_money(abs(incremental))}"
            meta = "Lower replacement cost vs base"
    
        st.markdown(f"""
        <div class="card {border_class}">
            <div class="label">{label}</div>
            <div class="value">{amount}</div>
            <div class="meta">{meta}</div>
        </div>
        """, unsafe_allow_html=True)
    # ============================================================
    # STRATEGIC INTERPRETATION (FINAL FIX)
    # ============================================================
    if cost_diff >= 0:
        cost_line = f"Incremental cost: ₹{cost_diff:,.0f}"
    else:
        cost_line = f"Savings vs base: ₹{abs(cost_diff):,.0f}"
        
    st.markdown('<div class="section-header">Strategic Interpretation</div>', unsafe_allow_html=True)

    preset = st.session_state.get("preset", "custom")

    # ==========================================================
    # DATA-DRIVEN RISK ENGINE (Replaces preset-driven logic)
    # ==========================================================
    
    final_attr_pct = final_attr_b / 100
    
    # Risk index (0-100)
    attrition_score = min(40,max(0,
        ((final_attr_pct - bench_min) /
        (max(bench_max-bench_min,0.0001))) * 40
        )
        )
    
    engagement_score = max(
        0,
        min(25, ((70 - df_b["Engagement"].iloc[-1]) / 30) * 25)
    )
    
    hiring_gap_ratio = max(
        0,
        1 - (sim_hr_b / max(hr_a,1))
    )
    
    hiring_score = min(
        20,
        hiring_gap_ratio * 20
    )
    
    cost_score = min(
        15,
        max(0,cost_diff/cum_cost_a)*15 if cum_cost_a>0 else 0
    )
    
    risk_index = (
        attrition_score +
        engagement_score +
        hiring_score +
        cost_score
    )
    
    # Risk Classification
    if risk_index >= 65:
        risk_cls = "risk-box-red"
        risk_icon = "🔴"
        risk_text = (
            f"high workforce instability "
            f"(Risk Index: {risk_index:.0f}/100)."
        )
    
    elif risk_index >= 40:
        risk_cls = "risk-box-orange"
        risk_icon = "🟠"
        risk_text = (
            f"moderate workforce risk pressure "
            f"(Risk Index: {risk_index:.0f}/100)."
        )
    
    else:
        risk_cls = "risk-box-green"
        risk_icon = "🟢"
        risk_text = (
            f"stable workforce outlook "
            f"(Risk Index: {risk_index:.0f}/100)."
        )

    # ALWAYS RENDER (THIS WAS THE BUG)
    st.markdown(f"""
    <div class="{risk_cls}">
    <strong>{risk_icon} Overall Assessment</strong><br><br>
    
    Under the stress scenario, the organization is experiencing
    <strong>{risk_text}</strong><br><br>
    
    <strong>Key deltas vs Base Scenario:</strong><br>
    • Workforce Risk Index: <strong>{risk_index:.0f}/100</strong><br>
    • Headcount change: <strong>{emp_diff:+.1f}</strong><br>
    • Revenue impact: <strong>₹{rev_diff:+,.0f}</strong><br>
    • Final attrition: <strong>{final_attr_b:.2f}%</strong>
    (Base: {final_attr_a:.2f}%)<br>
    • {cost_line}
    
    </div>
    """, unsafe_allow_html=True)
    

  
    # st.markdown(f"""
    # <div class="{risk_cls}">
    # <div class="risk-text">
    # <strong>{risk_icon} Overall Assessment</strong><br><br>
    # Under the stress scenario, the organization is experiencing <strong>{risk_text}</strong><br><br>
    # <strong>Key deltas vs Base Scenario:</strong><br>
    # • Headcount changes by <strong>{emp_diff:+.1f} employees</strong> at month {months}<br>
    # • Monthly revenue shifts by <strong>₹{rev_diff:+,.0f}</strong><br>
    # • Attrition stabilizes at <strong>{final_attr_b:.2f}%</strong> (Base: {final_attr_a:.2f}%)<br>
    # • Incremental replacement cost: <strong>₹{cost_diff:+,.0f}</strong> over {months} months
    # </div>
    # </div>
    # """, unsafe_allow_html=True)

    # ============================================================
    # PLOTLY CHARTS
    # ============================================================
    #st.markdown('<div class="section-header">Visual Analysis</div>', unsafe_allow_html=True)

    COLORS = {"A": "#1A56DB", "B": "#DC2626", "bench_min": "#16A34A", "bench_max": "#EA580C"}

    def style_fig(fig):
        fig.update_layout(
            font_family="DM Sans",
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=320,  # tighter
            margin=dict(l=20, r=20, t=40, b=20),  # tighter
            #title_x=0.05,
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
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    # --- Chart 1: Headcount ---
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_a["Month"], y=df_a["Employees"],
                              name="Scenario A — Base", line=dict(color=COLORS["A"], width=2.5)))
    fig1.add_trace(go.Scatter(x=df_b["Month"], y=df_b["Employees"],
                              name="Scenario B — Stress", line=dict(color=COLORS["B"], width=2.5, dash="dot")))
    
    fig1.add_hline(y=emp_a, line_dash="dash", line_color="#94a3b8",
                   annotation_text="Initial Headcount", annotation_position="right")
    fig1.update_layout(title="Headcount Projection", yaxis_title="Employees")
    #fig1.update_layout(title=0.05)
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
    fig4.update_layout(title="Monthly Replacement Cost (Industry-adjusted turnover cost)",
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