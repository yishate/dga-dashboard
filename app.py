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
        condition1 = (py[i] > y) != (py[j] > y)
        dx = px[j] - px[i]
        dy = py[j] - py[i]
        
        # Prevent division by zero if line is perfectly horizontal
        if dy != 0:
            intersect_x = (dx * (y - py[i]) / dy) + px[i]
            condition2 = x < intersect_x
            if condition1 and condition2:
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

# Helper functions for ultra-safe plotting
def add_tri_zone(fig, a_vals, b_vals, c_vals, colour, name):
    fig.add_trace(go.Scatterternary(
        a=a_vals, b=b_vals, c=c_vals, mode='lines', 
        fill='toself', fillcolor=colour, 
        line=dict(color='black', width=1), name=name
    ))

def add_pent_zone(fig, x_vals, y_vals, colour, name):
    x_closed = x_vals + [x_vals[0]]
    y_closed = y_vals + [y_vals[0]]
    fig.add_trace(go.Scatter(
        x=x_closed, y=y_closed, mode='lines', 
        fill='toself', fillcolor=colour, 
        line=dict(color='black', width=1), name=name
    ))

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
            
            add_tri_zone(fig, [98, 100, 98], [0, 0, 2], [2, 0, 0], 'rgba(128,0,0,0.6)', 'PD')
            add_tri_zone(fig, [98, 98, 76, 80], [0, 2, 4, 0], [2, 0, 20, 20], 'rgba(255,165,0,0.6)', 'T1')
            add_tri_zone(fig, [80, 76, 46, 50], [0, 4, 4, 0], [20, 20, 50, 50], 'rgba(255,200,150,0.8)', 'T2')
            add_tri_zone(fig, [50, 46, 31, 0, 0], [0, 4, 15, 15, 0], [50, 50, 54, 85, 100], 'rgba(139,69,19,0.6)', 'T3')
            add_tri_zone(fig, [98, 87, 64, 76], [2, 13, 13, 4], [0, 0, 23, 20], 'rgba(173,216,230,0.6)', 'D1')
            add_tri_zone(fig, [87, 0, 0, 31, 46, 64], [13, 100, 71, 15, 4, 13], [0, 0, 29, 54, 50, 23], 'rgba(135,206,250,0.8)', 'D2')
            add_tri_zone(fig, [64, 46, 31, 0, 0], [13, 4, 15, 71, 15], [23, 50, 54, 29, 85], 'rgba(224,255,255,0.8)', 'DT')
            
            fig.add_trace(go.Scatterternary(
                a=[p_ch4], b=[p_c2h2], c=[p_c2h4], mode='markers', 
                marker=dict(symbol='circle', color='black', size=14, line=dict(color='white', width=2)), 
                name='Calculated Point'
            ))
            
            fig.update_layout(
                plot_bgcolor='white', paper_bgcolor='white', 
                ternary=dict(
                    sum=100, aaxis=dict(title='CH4 %', min=0), 
                    baxis=dict(title='C2H2 %', min=0), caxis=dict(title='C2H4 %', min=0)
                ), height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please enter gas values greater than 0 to generate the Triangle.")

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
        cBase = [(0, 40), (-38, 12.4), (-23.5, -32.4), (23.5, -32.4), (38, 12.4)]
        
        x = [(p_ord[i]/100) * cBase[i][0] for i in range(5)]
        y = [(p_ord[i]/100) * cBase[i][1] for i in range(5)]
        x.append(x[0])
        y.append(y[0])

        A = sum(0.5 * (x[i] * y[i+1] - x[i+1] * y[i]) for i in range(5))
        cx, cy = 0, 0
        
        if A != 0:
            for i in range(5):
                factor = (x[i] * y[i+1] - x[i+1] * y[i])
                cx += (x[i] + x[i+1]) * factor
                cy += (y[i] + y[i+1]) * factor
            cx = cx / (6 * A)
            cy = cy / (6 * A)

        pdX, pdY = [0, -1, -1, 0], [33, 33, 24.5, 24.5]
        d1X, d1Y = [0, 38, 32, 4, 0], [40, 12, -6.1, 16, 1.5]
        d2X, d2Y = [4, 32, 24.3, 0, 0], [16, -6.1, -30, -3, 1.5]
        t3X, t3Y = [0, 24.3, 23.5, 1, -6], [-3, -30, -32.4, -32, -4]
        t2X, t2Y = [-6, 1, -22.5], [-4, -32.4, -32.4]
        t1X, t1Y = [-6, -22.5, -23.5, -35, 0, 0], [-4, -32.4, -32.4, 3, 1.5, -3]
        sX,  sY  = [0, -35, -38, 0, 0, -1, -1, 0], [1.5, 3.1, 12.4, 40, 33, 33, 24.5, 24.5]

        if in_polygon(cx, cy, pdX, pdY): pent_fault = "PD (Partial Discharge)"
        elif in_polygon(cx, cy, d1X, d1Y): pent_fault = "D1 (Low Energy Arcing)"
        elif in_polygon(cx, cy, d2X, d2Y): pent_fault = "D2 (High Energy Arcing)"
        elif in_polygon(cx, cy, t3X, t3Y): pent_fault = "T3 (Thermal > 700°C)"
        elif in_polygon(cx, cy, t2X, t2Y): pent_fault = "T2 (Thermal 300 - 700°C)"
        elif in_polygon(cx, cy, t1X, t1Y): pent_fault = "T1 (Thermal < 300°C)"
        elif in_polygon(cx, cy, sX, sY): pent_fault = "S (Stray Gassing)"
        else: pent_fault = "Unknown / Borderline"

        with col_pent_results:
            st.subheader("Pentagon Diagnosis")
            st.markdown(f"**Calculated Centroid:**\nX: {cx:.2f}, Y: {cy:.2f}")
            st.error("🚨 **Alert:** Fault detected.")
            st.markdown(f"**Fault Type:** {pent_fault}")

        with col_pent_chart:
            fig2 = go.Figure()
            
            add_pent_zone(fig2, pdX, pdY, 'rgba(204,204,255,0.6)', 'PD') 
            add_pent_zone(fig2, d1X, d1Y, 'rgba(255,204,204,0.6)', 'D1') 
            add_pent_zone(fig2, d2X, d2Y, 'rgba(255,153,153,0.6)', 'D2') 
            add_pent_zone(fig2, t3X, t3Y, 'rgba(255,229,153,0.6)', 'T3') 
            add_pent_zone(fig2, t2X, t2Y, 'rgba(255,255,153,0.6)', 'T2') 
            add_pent_zone(fig2, t1X, t1Y, 'rgba(204,255,204,0.6)', 'T1') 
            add_pent_zone(fig2, sX,  sY,  'rgba(229,229,229,0.6)', 'S')  

            fig2.add_trace(go.Scatter(
                x=[0, -38, -23.5, 23.5, 38, 0], y=[40, 12.4, -32.4, -32.4, 12.4, 40], 
                mode='lines+text', line=dict(color='black', width=2), 
                text=['H2', 'C2H6', 'CH4', 'C2H4', 'C2H2', ''], textposition="top center", 
                textfont=dict(size=14, color="blue", weight="bold"), name='Boundary', hoverinfo='none'
            ))
            
            fig2.add_trace(go.Scatter(
                x=[cx], y=[cy], mode='markers', 
                marker=dict(symbol='circle', color='blue', size=12, line=dict(color='black', width=1.5)), 
                name='Centroid'
            ))
            
            fig2.update_layout(
                plot_bgcolor='white', paper_bgcolor='white', 
                xaxis=dict(visible=False, range=[-45, 45]), yaxis=dict(visible=False, range=[-40, 45]), 
                height=600, showlegend=True, 
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Please enter gas values greater than 0 to generate the Pentagon.")
