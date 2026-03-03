import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Workforce Stability Lab", layout="wide")

st.title("Workforce Stability Lab")
st.caption("A strategic simulation engine for workforce risk and business impact modeling.")

# ============================================================
# INDUSTRY BENCHMARK TABLE (Monthly)
# Derived from public HR reports (annual ÷ 12 approximation)
# ============================================================

industry_benchmarks = {
    "IT / ITES": {"min": 0.008, "max": 0.021},
    "Manufacturing": {"min": 0.007, "max": 0.010},
    "Banking / Financial Services": {"min": 0.007, "max": 0.0125},
    "Healthcare": {"min": 0.008, "max": 0.017}
}

industry = st.selectbox("Select Industry Benchmark", list(industry_benchmarks.keys()))

bench_min = industry_benchmarks[industry]["min"]
bench_max = industry_benchmarks[industry]["max"]

st.info(
    f"Industry Monthly Attrition Benchmark: "
    f"{bench_min*100:.1f}% – {bench_max*100:.1f}% "
    f"(≈ {bench_min*100*12:.0f}% – {bench_max*100*12:.0f}% annually)"
)

# ============================================================
# SIMULATION ENGINE
# ============================================================

def simulate_workforce(
    initial_employees,
    base_attrition,
    max_attrition,
    hr_capacity,
    revenue_per_fte,
    engagement_start,
    comp_gap,
    months=12
):

    RAMP = [0.4, 0.7, 1.0]

    employees = float(initial_employees)
    engagement = float(engagement_start)
    attrition = float(base_attrition)
    prev_exits = 0.0

    bucket_1 = bucket_2 = bucket_3 = 0.0
    experienced = employees
    results = []

    for month in range(1, months + 1):

        exits = employees * attrition
        exit_ratio = exits / employees if employees > 0 else 0

        experienced *= (1 - exit_ratio)
        bucket_1 *= (1 - exit_ratio)
        bucket_2 *= (1 - exit_ratio)
        bucket_3 *= (1 - exit_ratio)

        hires = min(hr_capacity, prev_exits)

        fully_productive_from_ramp = bucket_3
        bucket_3 = bucket_2
        bucket_2 = bucket_1
        bucket_1 = hires

        experienced += fully_productive_from_ramp
        employees = experienced + bucket_1 + bucket_2 + bucket_3

        overload = (exits + hires) / hr_capacity

        engagement_change = 0.5 * (overload - 1)
        engagement -= engagement_change
        engagement = max(0, min(100, engagement))

        engagement_gap = engagement_start - engagement
        z = (0.02 * engagement_gap) + (1 * comp_gap)

        logistic_component = 1 / (1 + np.exp(-z))

        attrition = base_attrition + (max_attrition - base_attrition) * (
            (logistic_component - 0.5) * 2
        )

        attrition = max(0, min(max_attrition, attrition))

        revenue = (
            experienced * revenue_per_fte
            + bucket_1 * RAMP[0] * revenue_per_fte
            + bucket_2 * RAMP[1] * revenue_per_fte
            + bucket_3 * RAMP[2] * revenue_per_fte
        )

        results.append({
            "Month": month,
            "Employees": employees,
            "Attrition (%)": attrition * 100,
            "Revenue": revenue
        })

        prev_exits = exits

    return pd.DataFrame(results)

# ============================================================
# SCENARIO INPUTS
# ============================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Scenario A — Base")

    emp_a = st.number_input("Employees (A)", value=300)
    attr_a = st.number_input("Base Attrition % (A)", value=bench_min*100) / 100
    max_attr_a = st.number_input("Max Attrition % (A)", value=bench_max*100) / 100
    hr_a = st.number_input("HR Capacity (A)", value=8)
    rev_a = st.number_input("Revenue per FTE (A)", value=80000)
    engage_a = st.slider("Engagement Start (A)", 0, 100, 75)
    comp_a = st.number_input("Comp Gap % (A)", value=0.0) / 100

with col2:
    st.subheader("Scenario B — Stress")

    emp_b = st.number_input("Employees (B)", value=300)
    attr_b = st.number_input("Base Attrition % (B)", value=bench_max*100) / 100
    max_attr_b = st.number_input("Max Attrition % (B)", value=(bench_max*1.5)*100) / 100
    hr_b = st.number_input("HR Capacity (B)", value=5)
    rev_b = st.number_input("Revenue per FTE (B)", value=80000)
    engage_b = st.slider("Engagement Start (B)", 0, 100, 75)
    comp_b = st.number_input("Comp Gap % (B)", value=15.0) / 100

months = st.slider("Projection Months", 6, 36, 12)

# ============================================================
# RUN SIMULATION
# ============================================================

if st.button("Run Simulation"):

    df_a = simulate_workforce(emp_a, attr_a, max_attr_a, hr_a,
                               rev_a, engage_a, comp_a, months)

    df_b = simulate_workforce(emp_b, attr_b, max_attr_b, hr_b,
                               rev_b, engage_b, comp_b, months)

    # ===============================
    # EXECUTIVE KPI SUMMARY
    # ===============================

    st.subheader("Executive Summary")

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

    final_emp_a = df_a["Employees"].iloc[-1]
    final_emp_b = df_b["Employees"].iloc[-1]
    emp_diff = final_emp_b - final_emp_a

    final_attr_a = df_a["Attrition (%)"].iloc[-1]
    final_attr_b = df_b["Attrition (%)"].iloc[-1]
    attr_diff = final_attr_b - final_attr_a

    final_rev_a = df_a["Revenue"].iloc[-1]
    final_rev_b = df_b["Revenue"].iloc[-1]
    rev_diff = final_rev_b - final_rev_a

    col_kpi1.metric("Headcount (Stress)", f"{final_emp_b:.0f}", delta=f"{emp_diff:.1f}")
    col_kpi2.metric("Final Attrition %", f"{final_attr_b:.2f}%", delta=f"{attr_diff:.2f}%")
    col_kpi3.metric("Revenue (Stress)", f"₹{final_rev_b:,.0f}", delta=f"₹{rev_diff:,.0f}")

    # ===============================
    # STRATEGIC INTERPRETATION
    # ===============================

    st.subheader("Strategic Interpretation")

    final_attr = final_attr_b / 100

    if final_attr > bench_max:
        risk_text = "high workforce instability relative to industry benchmarks."
        risk_icon = "🔴"
    elif final_attr > bench_min:
        risk_text = "moderate attrition pressure within the upper industry range."
        risk_icon = "🟠"
    else:
        risk_text = "stable workforce dynamics below benchmark range."
        risk_icon = "🟢"

    st.markdown(
        f"""
### {risk_icon} Overall Assessment

Under the defined stress scenario, the organization is experiencing **{risk_text}**

Compared to Scenario A:
- Headcount changes by **{emp_diff:.1f} employees**
- Revenue shifts by **₹{rev_diff:,.0f}**
- Attrition stabilizes at **{final_attr_b:.2f}%**

This reflects whether current hiring capacity and compensation positioning are structurally sustainable.
"""
    )
    st.markdown("---")
    st.caption("Developed by Anchit Kunal | Workforce Stability Lab | Educational Simulation Tool")
    # ===============================
    # VISUAL ANALYSIS
    # ===============================

    st.subheader("Headcount Projection")
    fig1, ax1 = plt.subplots()
    ax1.plot(df_a["Month"], df_a["Employees"], label="Scenario A")
    ax1.plot(df_b["Month"], df_b["Employees"], label="Scenario B")
    ax1.legend()
    st.pyplot(fig1)

    st.subheader("Attrition Projection (%)")
    fig2, ax2 = plt.subplots()
    ax2.plot(df_a["Month"], df_a["Attrition (%)"], label="Scenario A")
    ax2.plot(df_b["Month"], df_b["Attrition (%)"], label="Scenario B")
    ax2.legend()
    st.pyplot(fig2)

    st.subheader("Revenue Projection")
    fig3, ax3 = plt.subplots()
    ax3.plot(df_a["Month"], df_a["Revenue"], label="Scenario A")
    ax3.plot(df_b["Month"], df_b["Revenue"], label="Scenario B")
    ax3.legend()
    st.pyplot(fig3)