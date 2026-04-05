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
    
    if p_ch4 >= 98: 
        return p_ch4, p_c2h4, p_c2h2, "PD (Partial Discharge)"
    elif p_c2h2 >= 13 and p_ch4 < 98: 
        return p_ch4, p_c2h4, p_c2h2, "D1 / D2 (Arcing)"
    elif 20 <= p_c2h4 < 50 and p_c2h2 < 4 and p_ch4 < 98: 
        return p_ch4, p_c2h4, p_c2h2, "T2 (Thermal 300-700°C)"
    elif p_c2h4 >= 50 and p_c2h2 < 15 and p_ch4 < 98: 
        return p_ch4, p_c2h4, p_c2h2, "T3 (Thermal >700°C)"
    else: 
        return p_ch4, p_c2h4, p_c2h2, "T1 or DT (Mixed)"

def add_tri_zone(fig, a_vals, b_vals, c_vals, colour, name):
    trace_line = dict(color='black', width=1)
    trace = go.Scatterternary(
        a=a_vals, 
        b=b_vals, 
        c=c_vals, 
        mode='lines', 
        fill='toself', 
        fillcolor=colour, 
        line=trace_line, 
        name=name
    )
    fig.add_trace(trace)

def add_pent_zone(fig, x_vals, y_vals, colour, name):
    x_closed = x_vals + [x_vals[0]]
    y_closed = y_vals + [y_vals[0]]
    trace_line = dict(color='black', width=1)
    trace = go.Scatter(
        x=x_closed, 
        y=y_closed, 
        mode='lines', 
        fill='toself', 
        fillcolor=colour, 
        line=trace_line, 
        name=name
    )
    fig.add_trace(trace)

# ==========================================
# 2. PAGE CONFIGURATION & SIDEBAR
# ==========================================
st.set_page_config(page_title="Smart DGA Dashboard", layout="wide")

with st.sidebar:
    st.title("Data Input")
    st.markdown("Enter gas concentrations (ppm)")
    
    oil_type = st.radio(
        "Select Insulating Fluid:", 
        ["Mineral Oil", "Natural Ester (NE)"]
    )
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
            
            # PD Zone
            add_tri_zone(
                fig, 
                a_vals=[98, 100, 98], 
                b_vals=[2, 0, 0], 
                c_vals=[0, 0, 2], 
                colour='rgba(128,0,0,0.6)', 
                name='PD'
            )
            # T1 Zone
            add_tri_zone(
                fig, 
                a_vals=[80, 76, 96, 98, 98], 
                b_vals=[0, 4, 4, 2, 0], 
                c_vals=[20, 20, 0, 0, 2], 
                colour='rgba(255,165,0,0.6)', 
                name='T1'
            )
            # T2 Zone
            add_tri_zone(
                fig, 
                a_vals=[50, 46, 76, 80], 
                b_vals=[0, 4, 4, 0], 
                c_vals=[50, 50, 20, 20], 
                colour='rgba(255,200,150,0.8)', 
                name='T2'
            )
            # T3 Zone
            add_tri_zone(
                fig, 
                a_vals=[0, 35, 50, 0], 
                b_vals=[15, 15, 0, 0], 
                c_vals=[85, 50, 50, 100], 
                colour='rgba(139,69,19,0.6)', 
                name='T3'
            )
            # D1 Zone
            add_tri_zone(
                fig, 
                a_vals=[0, 87, 64, 0], 
                b_vals=[100, 13, 13, 77], 
                c_vals=[0, 0, 23, 23], 
                colour='rgba(173,216,230,0.6)', 
                name='D1'
            )
            # D2 Zone
            add_tri_zone(
                fig, 
                a_vals=[0, 64, 47, 31, 0], 
                b_vals=[77, 13, 13, 29, 29], 
                c_vals=[23, 23, 40, 40, 71], 
                colour='rgba(135,206,250,0.8)', 
                name='D2'
            )
            # DT Zone
            add_tri_zone(
                fig, 
                a_vals=[0, 31, 47, 87, 96, 46, 35, 0], 
                b_vals=[29, 29, 13, 13, 4, 4, 15, 15], 
                c_vals=[71, 40, 40, 0, 0, 50, 50, 85], 
                colour='rgba(224,255,255,0.8)', 
                name='DT'
            )
            
            pt_marker = dict(
                symbol='circle', 
                color='black', 
                size=14, 
                line=dict(color='white', width=2)
            )
            
            pt_trace = go.Scatterternary(
                a=[p_ch4], 
                b=[p_c2h2], 
                c=[p_c2h4], 
                mode='markers', 
                marker=pt_marker, 
                name='Calculated Point'
            )
            fig.add_trace(pt_trace)
            
            t_layout = dict(
                sum=100, 
                aaxis=dict(title='CH4 %', min=0), 
                baxis=dict(title='C2H2 %', min=0), 
                caxis=dict(title='C2H4 %', min=0)
            )
            
            fig.update_layout(
                plot_bgcolor='white', 
                paper_bgcolor='white', 
                ternary=t_layout, 
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please enter gas values greater than 0.")

# ------------------------------------------
# TAB 2: DUVAL PENTAGON
# ------------------------------------------
with tab2:
    col_pent_chart, col_pent_results = st.columns([7, 3])
    total_5 = h2 + ch4 + c2h6 + c2h4 + c2h2
    
    if total_5 > 0:
        p_H2 = (h2 / total_5) * 100
        p_C2H6 = (c2h6 / total_5) * 100
        p_CH4 = (ch4 / total_5) * 100
        p_C2H4 = (c2h4 / total_5) * 100
        p_C2H2 = (c2h2 / total_5) * 100
        
        p_ord = [p_H2, p_C2H6, p_CH4, p_C2H4, p_C2H2]
        
        cBase = [
            (0, 40), 
            (-38, 12.4), 
            (-23.5, -32.4), 
            (23.5, -32.4), 
            (38, 12.4)
        ]
        
        x = [(p_ord[i]/100) * cBase[i][0] for i in range(5)]
        y = [(p_ord[i]/100) * cBase[i][1] for i in range(5)]
        x.append(x[0])
        y.append(y[0])

        A = sum(0.5 * (x[i] * y[i+1] - x[i+1] * y[i]) for i in range(5))
        cx = 0
        cy = 0
        
        if A != 0:
            for i in range(5):
                factor = (x[i]
