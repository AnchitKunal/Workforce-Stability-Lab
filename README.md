**Workforce Stability Lab**
_Strategic Workforce Risk & Business Impact Simulation Engine_

_**🔗 Live App: https://workforce-stability-lab.streamlit.app**_

**Overview**
Workforce Stability Lab is an interactive decision-support simulation tool designed to model workforce attrition risk, hiring capacity constraints, and revenue impact under varying strategic scenarios.
The application enables HR leaders and business stakeholders to simulate:
**Workforce headcount dynamics
Attrition pressure relative to industry benchmarks
Revenue implications of hiring and engagement constraints
Reinforcing workforce decline loops**

This project demonstrates applied HR analytics, system dynamics modeling, and executive decision visualization using Python and Streamlit.

**Business Problem**
Organizations often react to attrition only after performance and revenue are affected.

This tool answers:
1. What happens if attrition rises above industry benchmarks?
2. What if hiring capacity cannot match exits?
3. How does compensation dissatisfaction influence long-term stability?
4. When does workforce pressure become structurally unsustainable?
_The simulation provides forward-looking risk visibility instead of retrospective reporting._

**Modeling Approach**
The engine incorporates:

Logistic attrition response function
Engagement-driven attrition sensitivity
Hiring capacity constraints
Productivity ramp curves for new hires
Industry-specific attrition benchmarks
Reinforcing system dynamics loops

**Key modeled mechanisms:** 

1. Attrition increases with engagement decline and compensation gap.
2. Hiring capacity limits replacement velocity.
3. Overload reduces engagement.
4. Reduced engagement further increases attrition.
5. Revenue is adjusted for productivity ramp of new hires.

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
