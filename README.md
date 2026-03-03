**Workforce Stability Lab**
_Strategic Workforce Risk & Business Impact Simulation Engine_

_**🔗 Live App: https://workforce-stability-lab.streamlit.app**_

**Overview**
Workforce Stability Lab is a forward-looking workforce simulation engine designed to model:
1. Attrition risk
2. Hiring capacity constraints
3. Engagement pressure
4. Revenue impact under stress scenarios

Unlike traditional HR dashboards that describe historical data, this tool simulates structural workforce instability before it manifests operationally. 
It demonstrates applied system dynamics modeling in HR analytics using Python and Streamlit.

**Business Problem**
Organizations often respond to attrition only after performance and revenue have already been affected.

This engine addresses critical strategic questions:

**1. What happens if attrition rises above industry benchmarks?
2. What if hiring capacity cannot replace exits?
3. How does compensation dissatisfaction influence long-term stability?
4. When does workforce pressure become structurally unsustainable?**

The simulation provides forward-looking risk visibility instead of retrospective reporting.

**System Dynamics Logic**

The model captures a reinforcing workforce loop:

Headcount ↓
→ Workload ↑
→ Engagement ↓
→ Attrition ↑
→ Further Headcount ↓

A balancing mechanism exists:

Attrition ↑
→ Hiring Demand ↑
→ HR Capacity Constraint
→ Replacement Lag
→ Revenue Impact
System behavior depends on which force dominates.

**Modeling Framework**

The engine incorporates:
1. Logistic attrition response function
2. Engagement-driven attrition sensitivity
3. Compensation gap multiplier
4. Hiring capacity constraints
5. 3-month productivity ramp curve

**Industry-relative attrition benchmarks**

1. Attrition bounding via maximum cap
2. Core Mechanisms
3. Attrition increases as engagement declines and compensation gap widens.
4. Hiring capacity limits workforce replacement velocity.
5. Overload reduces engagement.
6. Reduced engagement further increases attrition.
7. Revenue adjusts for productivity ramp stages.


**Industry Benchmark Integration**
Includes reference bands for: _IT / ITES, Manufacturing, Banking / Financial Services, Healthcare_
Benchmarks are derived from publicly available HR industry reports (annual rates converted to monthly approximation).

**Features**

1. Dual scenario comparison (Base vs Stress)
2. Executive KPI dashboard
3. Industry-relative risk classification
4. Strategic interpretation narrative
5. Workforce headcount projection
6. Attrition projection
7. Revenue impact modeling

_**Tech Stack: Python, Streamlit, NumPy, Pandas, Matplotlib**_

_Disclaimer: This is an educational simulation model designed to demonstrate strategic workforce analytics concepts. It is not intended for financial forecasting or regulatory reporting._
