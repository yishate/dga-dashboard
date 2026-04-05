import streamlit as st
import plotly.graph_objects as go

# ==========================================
# 1. THE "BRAIN": MATHS & POLYGON LOGIC
# ==========================================
def in_polygon(x, y, px, py):
    inside = False
    n = len(px)
    j = n - 1
    for i in range(n):
        cond1 = (py[i] > y) != (py[j] > y)
        dx = px[j] - px[i]
        dy = py[j] - py[i]
        if dy != 0:
            intersect_x = (dx * (y - py[i]) / dy) + px[i]
            cond2 = x < intersect_x
            if cond1 and cond2:
                inside = not inside
        j = i
    return inside

def get_triangle_diagnosis(ch4, c2h4, c2h2):
    total = ch4 + c2h4 + c2h2
    if total == 0:
        return 0, 0, 0, "Normal"
    p_ch4 = (ch4 / total) * 100
    p_c2h4 = (c2h4 / total) * 100
    p_c2h2 = (c2h2 / total) * 100
    
    if p_ch4 >= 98: return p_ch4, p_c2h4, p_c2h2, "PD (Partial Discharge)"
    elif p_c2h2 >= 13 and p_ch4 < 98: return p_ch4, p_c2h4, p_c2h2, "D1 / D2 (Arcing)"
    elif 20 <= p_c2h4 < 50 and p_c2h2 < 4 and p_ch4 < 98: return p_ch4, p_c2h4, p_c2h2, "T2 (Thermal 300-700°C)"
    elif p_c2h4 >= 50 and p_c2h2 < 15 and p_ch4 < 98: return p_ch4, p_c2h4, p_c2h2, "T3 (Thermal >700°C)"
    else: return p_ch4, p_c2h4, p_c2h2, "T1 or DT (Mixed)"

def add_tri_zone(fig, a_vals, b_vals, c_vals, zone_color, name):
    # Flat variable assignment to prevent any bracket truncation
    trace_line = dict(color='black', width=1)
    trace = go.Scatterternary(a=a_vals, b=b_vals, c=c_vals, mode='lines', fill='toself', fillcolor=zone_color, line=trace_line, name=name)
    fig.add_trace(trace)

def add_pent_zone(fig, x_vals, y_vals, zone_color, name):
    x_closed = x_vals + [x_vals[0]]
    y_closed = y_vals + [y_vals[0]]
    trace_line = dict(color='black', width=1)
    trace = go.Scatter(x=x_closed, y=y_closed, mode='lines', fill='toself', fillcolor=zone_color, line=trace_line, name=name)
    fig.add_trace(trace)

# ==========================================
# 2. PAGE CONFIGURATION & SIDEBAR
# ==========================================
st.set_page_config(page_title="Smart DGA Dashboard", layout="wide")

with st.sidebar:
    st.title("Data Input")
    st.markdown("Enter gas concentrations (ppm)")
    oil_type = st.radio("Select Insulating Fluid:", ["Mineral Oil", "Natural Ester (NE)"])
    st.divider()
    h2 = st.number_input("H2", min_value=0.0, value=10.0, step=1.0)
    ch4 = st.number_input("CH4", min_value=0.0, value=50.0, step=1.0)
    c2h6 = st.number_input("C2H6", min_value=0.0, value=20.0, step=1.0)
    c2h2 = st.number_input("C2H2", min_value=0.0, value=5.0, step=1.0)
    c2h4 = st.number_input("C2H4", min_value=0.0, value=40.0, step=1.0)

# ==========================================
# 3. MAIN INTERFACE
# ==========================================
st.title("Smart DGA Dashboard")
tab1, tab2 = st.tabs(["Duval Triangle", "Duval Pentagon"])

# ------------------------------------------
# TAB 1: DUVAL TRIANGLE
# ------------------------------------------
with tab1:
    p_ch4, p_c2h4, p_c2h2, tri_fault = get_triangle_diagnosis(ch4, c2h4, c2h2)
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
            
            add_tri_zone(fig, [98, 100, 98], [2, 0, 0], [0, 0, 2], 'rgba(128,0,0,0.6)', 'PD')
            add_tri_zone(fig, [80, 76, 96, 98, 98], [0, 4, 4, 2, 0], [20, 20, 0, 0, 2], 'rgba(255,165,0,0.6)', 'T1')
            add_tri_zone(fig, [50, 46, 76, 80], [0, 4, 4, 0], [50, 50, 20, 20], 'rgba(255,200,150,0.8)', 'T2')
            add_tri_zone(fig, [0, 35, 50, 0], [15, 15, 0, 0], [85, 50, 50, 100], 'rgba(139,69,19,0.6)', 'T3')
            add_tri_zone(fig, [0, 87, 64, 0], [100, 13, 13, 77], [0, 0, 23, 23], 'rgba(173,
