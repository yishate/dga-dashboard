import streamlit as st
import plotly.graph_objects as go

# ==========================================
# 1. THE "BRAIN": MATHS & POLYGON LOGIC
# ==========================================
def in_polygon(x, y, px, py):
    """Pure Python ray-casting algorithm for fault zones"""
    inside = False
    n = len(px)
    j = n - 1
    for i in range(n):
        if ((py[i] > y) != (py[j] > y)) and (x < (px[j] - px[i]) * (y - py[i]) / (py[j] - py[i]) + px[i]):
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
    else: return p_ch4, p_c2h4, p_c2h2, "T1 or DT (Low Thermal / Mixed)"

# Helper functions for ultra-safe plotting (Prevents copy-paste errors)
def add_tri_zone(fig, a_vals, b_vals, c_vals, colour, name):
    fig.add_trace(go.Scatterternary(a=a_vals, b=b_vals, c=c_vals, mode='lines', fill='toself', fillcolor=colour, line=dict(color='black', width=1), name=name))

def add_pent_zone(fig, x_vals, y_vals, colour, name):
    fig.add_trace(go.Scatter(x=x_vals + [x_vals[0]], y=y_vals + [y_vals[0]], mode='lines', fill='toself', fillcolor=colour, line=dict(color='black', width=1), name=name))


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
    p_ch4, p_c2h4, p_c2h2, tri_fault = get_triangle_diagnosis(ch4, c2h4, c2h2)
    col_chart, col_results = st.columns([7, 3])
    
    with col_results:
        st.subheader("Triangle Diagnosis")
        if tri_fault == "Normal": st.success("🟢 **Status:** Normal")
        else: 
            st.error("🚨 **Alert:** Fault detected.")
            st.markdown(f"**Fault Type:** {tri_fault}")

    with col_chart:
        if (ch4 + c2h4 + c2h2) > 0:
            fig = go.Figure()
            
            # Draw Triangle Zones safely
            add_tri_zone(fig, [98, 100, 98], [0, 0, 2], [2, 0, 0], 'rgba(128,0,0,0.6)', 'PD')
            add_tri_zone(fig, [98, 98, 76, 80], [0, 2, 4, 0], [2, 0, 20, 20], 'rgba(255,165,0,0.6)', 'T1')
            add_tri_zone(fig, [80, 76, 46, 50], [0, 4, 4, 0], [20, 20, 50, 50], 'rgba(255,200,150,0.8)', 'T2')
            add_tri_zone(fig, [50, 46, 31, 0, 0], [0, 4, 15, 15, 0], [50, 50, 54, 85, 100], 'rgba(139,69,19,0.6)', 'T3')
            add_tri_zone(fig, [98, 87, 64, 76], [2, 13, 13, 4], [0, 0, 23, 20], 'rgba(173,216,230,0.6)', 'D1')
            add_tri_zone(fig, [87, 0, 0, 31, 46, 64], [13, 100, 71, 15, 4, 13], [0, 0, 29, 54, 50, 23], 'rgba(135,206,250,0.8)', 'D2')
            add_tri_zone(fig, [64, 46, 31, 0, 0], [13, 4, 15, 71, 15], [23, 50, 54, 29, 85], 'rgba(224,255,255,0.8)', 'DT')
            
            fig.add_trace(go.Scatterternary(a=[p_ch4], b=[p_c2h2], c=[p_c2h4], mode='markers', marker=dict(symbol='circle', color='black', size=14, line=dict(color='white', width=2)), name='Calculated Point'))
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', ternary=dict(sum=100, aaxis=dict(title='CH4 %', min=0), baxis=dict(title='C2H2 %', min=0), caxis=dict(title='C2H4 %', min=0)), height=500)
            st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# TAB 2: DUVAL PENTAGON
# ------------------------------------------
with tab2:
    col_pent_chart, col_pent_results = st.columns([7, 3])
    total_5 = h2 + ch4 + c2h6 + c2h4 + c2h2
    
    if total_5 > 0:
        p_H2, p_C2H6, p_CH4, p_C2H4, p_C2H2 = (h2/total_5)*100, (c
