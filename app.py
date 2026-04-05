import streamlit as st
import plotly.graph_objects as go

# ==========================================
# 1. THE "BRAIN": MATHS & POLYGON LOGIC
# ==========================================
def in_polygon(x, y, px, py):
    """Pure Python ray-casting algorithm to replace MATLAB's inpolygon"""
    inside = False
    n = len(px)
    j = n - 1
    for i in range(n):
        if ((py[i] > y) != (py[j] > y)) and \
           (x < (px[j] - px[i]) * (y - py[i]) / (py[j] - py[i]) + px[i]):
            inside = not inside
        j = i
    return inside

def get_triangle_diagnosis(ch4, c2h4, c2h2):
    """Original Duval Triangle Logic"""
    total = ch4 + c2h4 + c2h2
    if total == 0:
        return 0, 0, 0, "Normal", "Enter gas values to see diagnosis."
    
    p_ch4 = (ch4 / total) * 100
    p_c2h4 = (c2h4 / total) * 100
    p_c2h2 = (c2h2 / total) * 100
    
    if p_ch4 >= 98:
        fault_type = "PD (Partial Discharge)"
    elif p_c2h2 >= 13 and p_ch4 < 98:
        fault_type = "D1 / D2 (Arcing)"
    elif 20 <= p_c2h4 < 50 and p_c2h2 < 4 and p_ch4 < 98:
        fault_type = "T2 (Thermal 300-700°C)"
    elif p_c2h4 >= 50 and p_c2h2 < 15 and p_ch4 < 98:
        fault_type = "T3 (Thermal >700°C)"
    else:
        fault_type = "T1 or DT (Low Thermal / Mixed)"

    return p_ch4, p_c2h4, p_c2h2, fault_type, "Calculated successfully."

# ==========================================
# 2. PAGE CONFIGURATION & SIDEBAR
# ==========================================
st.set_page_config(page_title="Smart DGA Dashboard", layout="wide")

with st.sidebar:
    st.title("Data Input")
    st.markdown("Enter gas concentrations (ppm)")
    
    oil_type = st.radio("Select Insulating Fluid:", ["Mineral Oil", "Natural Ester (NE)"])
    st.divider()
    
    h2 = st.number_input("Hydrogen (H2)", min_value=0.0, value=10.0, step=1.0)
    ch4 = st.number_input("Methane (CH4)", min_value=0.0, value=50.0, step=1.0)
    c2h6 = st.number_input("Ethane (C2H6)", min_value=0.0, value=20.0, step=1.0)
    c2h2 = st.number_input("Acetylene (C2H2)", min_value=0.0, value=5.0, step=1.0)
    c2h4 = st.number_input("Ethylene (C2H4)", min_value=0.0, value=40.0, step=1.0)

# ==========================================
# 3. MAIN INTERFACE
# ==========================================
st.title("Smart DGA Dashboard")

tab1, tab2 = st.tabs(["Duval Triangle", "Duval Pentagon"])

# ------------------------------------------
# TAB 1: DUVAL TRIANGLE
# ------------------------------------------
with tab1:
    p_ch4, p_c2h4, p_c2h2, tri_fault, report = get_triangle_diagnosis(ch4, c2h4, c2h2)
    col_chart, col_results = st.columns([7, 3])
    
    with col_results:
        st.subheader("Triangle Diagnosis")
        if tri_fault == "Normal":
            st.success("🟢 **Status:** Normal")
        else:
            st.error("🚨 **Alert:** Fault detected.")
            st.markdown(f"**Fault Type:** {tri_fault}")

    with col_chart:
        if (ch4 + c2h4 + c2h2) > 0:
            fig = go.Figure()
            # Triangle Zones
            fig.add_trace(go.Scatterternary(a=[98, 100, 98], b=[0, 0, 2], c=[2, 0, 0], mode='lines', fill='toself', fillcolor='rgba(128, 0, 0, 0.6)', line=dict(color='black', width=1), name='PD'))
            fig.add_trace(go.Scatterternary(a=[98, 98, 76, 80], b=[0, 2, 4, 0], c=[2, 0, 20, 20], mode='lines', fill='toself', fillcolor='rgba(255, 165, 0, 0.6)', line=dict(color='black', width=1), name='T1'))
            fig.add_trace(go.Scatterternary(a=[80, 76, 46, 50], b=[0, 4, 4, 0], c=[20, 20, 50, 50], mode='lines', fill='toself', fillcolor='rgba(255, 200, 150, 0.8)', line=dict(color='black', width=1), name='T2'))
            fig.add_trace(go.Scatterternary(a=[50, 46, 31, 0, 0], b=[0, 4, 15, 15, 0], c=[50, 50, 54, 85, 100], mode='lines', fill='toself', fillcolor='rgba(139, 69, 19, 0.6)', line=dict(color='black', width=1), name='T3'))
            fig.
