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

def get_triangle_3_diagnosis(ch4, c2h4, c2h2):
    total = ch4 + c2h4 + c2h2
    if total == 0:
        return 0, 0, 0, "Normal"
    
    p_ch4 = (ch4 / total) * 100
    p_c2h4 = (c2h4 / total) * 100
    p_c2h2 = (c2h2 / total) * 100
    
    if p_ch4 >= 98:
        return p_ch4, p_c2h4, p_c2h2, "PD (Partial Discharge)"
    elif p_c2h2 >= 15 and p_ch4 < 98: 
        return p_ch4, p_c2h4, p_c2h2, "D1 / D2 (Arcing)"
    elif 21 <= p_c2h4 < 50 and p_c2h2 < 15 and p_ch4 < 98:
        return p_ch4, p_c2h4, p_c2h2, "T2 (Thermal 300-700°C)"
    elif p_c2h4 >= 50 and p_c2h2 < 15 and p_ch4 < 98:
        return p_ch4, p_c2h4, p_c2h2, "T3 (Thermal >700°C)"
    else:
        return p_ch4, p_c2h4, p_c2h2, "T1 or DT (Mixed)"

def add_tri_zone(fig, a_vals, b_vals, c_vals, colour, name):
    trace_line = dict(color='black', width=1)
    trace = go.Scatterternary(
        a=a_vals, b=b_vals, c=c_vals, mode='lines', 
        fill='toself', fillcolor=colour, line=trace_line, name=name
    )
    fig.add_trace(trace)

def add_pent_zone(fig, x_vals, y_vals, colour, name):
    x_closed = x_vals + [x_vals[0]]
    y_closed = y_vals + [y_vals[0]]
    trace_line = dict(color='black', width=1)
    trace = go.Scatter(
        x=x_closed, y=y_closed, mode='lines', 
        fill='toself', fillcolor=colour, line=trace_line, name=name
    )
    fig.add_trace(trace)

def get_bar_chart(val_h2, val_ch4, val_c2h6, val_c2h2, val_c2h4):
    x_labels = ['H2', 'CH4', 'C2H6', 'C2H2', 'C2H4']
    y_values = [val_h2, val_ch4, val_c2h6, val_c2h2, val_c2h4]
    
    bar_trace = go.Bar(
        x=x_labels, 
        y=y_values, 
        marker_color='#2ca02c', 
        text=y_values,
        textposition='auto'
    )
    
    fig = go.Figure(bar_trace)
    
    b_layout = dict(
        title="Gas Concentrations",
        xaxis=dict(title="Gas Type"),
        yaxis=dict(title="ppm"),
        height=350,
        margin=dict(t=40, b=10, l=10, r=10),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_layout(b_layout)
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='lightgray')
    
    return fig

# ==========================================
# 2. PAGE CONFIGURATION & SIDEBAR
# ==========================================
st.set_page_config(page_title="Smart DGA Dashboard for Natural Ester", layout="wide")

with st.sidebar:
    st.title("Data Input")
    st.markdown("**Fluid Profile: Natural Ester (POME)**")
    st.markdown("Enter gas concentrations (ppm)")
    
    st.divider()
    
    h2 = st.number_input("H2 (Hydrogen)", min_value=0, value=0, step=1)
    ch4 = st.number_input("CH4 (Methane)", min_value=0, value=0, step=1)
    c2h6 = st.number_input("C2H6 (Ethane)", min_value=0, value=0, step=1)
    c2h2 = st.number_input("C2H2 (Acetylene)", min_value=0, value=0, step=1)
    c2h4 = st.number_input("C2H4 (Ethylene)", min_value=0, value=0, step=1)

# ==========================================
# 3. MAIN INTERFACE
# ==========================================
st.title("Smart DGA Dashboard for Natural Ester")
tab1, tab2 = st.tabs(["Duval Triangle 3", "Duval Pentagon 3"])

# ------------------------------------------
# TAB 1: DUVAL TRIANGLE 3
# ------------------------------------------
with tab1:
    p_ch4, p_c2h4, p_c2h2, tri
