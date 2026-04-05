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
    
    # Values set to 0.0 for a clean start
    h2 = st.number_input("H2 (Hydrogen)", min_value=0.0, value=0.0, step=1.0)
    ch4 = st.number_input("CH4 (Methane)", min_value=0.0, value=0.0, step=1.0)
    c2h6 = st.number_input("C2H6 (Ethane)", min_value=0.0, value=0.0, step=1.0)
    c2h2 = st.number_input("C2H2 (Acetylene)", min_value=0.0, value=0.0, step=1.0)
    c2h4 = st.number_input("C2H4 (Ethylene)", min_value=0.0, value=0.0, step=1.0)

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
            add_tri_zone(fig, [0, 87, 64, 0], [100, 13, 13, 77], [0, 0, 23, 23], 'rgba(173,216,230,0.6)', 'D1')
            add_tri_zone(fig, [0, 64, 47, 31, 0], [77, 13, 13, 29, 29], [23, 23, 40, 40, 71], 'rgba(135,206,250,0.8)', 'D2')
            add_tri_zone(fig, [0, 31, 47, 87, 96, 46, 35, 0], [29, 29, 13, 13, 4, 4, 15, 15], [71, 40, 40, 0, 0, 50, 50, 85], 'rgba(224,255,255,0.8)', 'DT')
            
            pt_mark = dict(symbol='circle', color='red', size=7, line=dict(color='red', width=2))
            fig.add_trace(go.Scatterternary(a=[p_ch4], b=[p_c2h2], c=[p_c2h4], mode='markers', marker=pt_mark, name='Calculated Point'))
            
            t_layout = dict(sum=100, aaxis=dict(title='CH4 %', min=0), baxis=dict(title='C2H2 %', min=0), caxis=dict(title='C2H4 %', min=0))
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', ternary=t_layout, height=500)
            
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
        
        cBase = [(0, 40), (-38, 12.4), (-23.5, -32.4), (23.5, -32.4), (38, 12.4)]
        
        x = []
        y = []
        for i in range(5):
            x.append((p_ord[i]/100) * cBase[i][0])
            y.append((p_ord[i]/100) * cBase[i][1])
            
        x.append(x[0])
        y.append(y[0])

        A = 0
        for i in range(5):
            term1 = x[i] * y[i+1]
            term2 = x[i+1] * y[i]
            A += 0.5 * (term1 - term2)
            
        cx = 0
        cy = 0
        
        if A != 0:
            for i in range(5):
                t1 = x[i] * y[i+1]
                t2 = x[i+1] * y[i]
                factor = t1 - t2
                cx += (x[i] + x[i+1]) * factor
                cy += (y[i] + y[i+1]) * factor
            cx = cx / (6 * A)
            cy = cy / (6 * A)

        pdX = [0, -1, -1, 0]
        pdY = [33, 33, 24.5, 24.5]
        
        d1X = [0, 38, 32, 4, 0]
        d1Y = [40, 12, -6.1, 16, 1.5]
        
        d2X = [4, 32, 24.3, 0, 0]
        d2Y = [16, -6.1, -30, -3, 1.5]
        
        t3X = [0, 24.3, 23.5, 1, -6]
        t3Y = [-3, -30, -32.4, -32, -4]
        
        t2X = [-6, 1, -22.5]
        t2Y = [-4, -32.4, -32.4]
        
        t1X = [-6, -22.5, -23.5, -35, 0, 0]
        t1Y = [-4, -32.4, -32.4, 3, 1.5, -3]
        
        sX  = [0, -35, -38, 0, 0, -1, -1, 0]
        sY  = [1.5, 3.1, 12.4, 40, 33, 33, 24.5, 24.5]

        if in_polygon(cx, cy, pdX, pdY):
            pent_fault = "PD (Partial Discharge)"
        elif in_polygon(cx, cy, d1X, d1Y):
            pent_fault = "D1 (Low Energy Arcing)"
        elif in_polygon(cx, cy, d2X, d2Y):
            pent_fault = "D2 (High Energy Arcing)"
        elif in_polygon(cx, cy, t3X, t3Y):
            pent_fault = "T3 (Thermal > 700°C)"
        elif in_polygon(cx, cy, t2X, t2Y):
            pent_fault = "T2 (Thermal 300 - 700°C)"
        elif in_polygon(cx, cy, t1X, t1Y):
            pent_fault = "T1 (Thermal < 300°C)"
        elif in_polygon(cx, cy, sX, sY):
            pent_fault = "S (Stray Gassing)"
        else:
            pent_fault = "Unknown / Borderline"

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
            add_pent_zone(fig2, sX, sY, 'rgba(229,229,229,0.6)', 'S')  

            bound_line = dict(color='black', width=2)
            bound_text = dict(size=14, color="blue", weight="bold")
            
            fig2.add_trace(go.Scatter(
                x=[0, -38, -23.5, 23.5, 38, 0], y=[40, 12.4, -32.4, -32.4, 12.4, 40], 
                mode='lines+text', line=bound_line, text=['H2', 'C2H6', 'CH4', 'C2H4', 'C2H2', ''], 
                textposition="top center", textfont=bound_text, name='Boundary', hoverinfo='none'
            ))
            
            cent_marker = dict(symbol='circle', color='black', size=6, line=dict(color='black', width=1.5))
            fig2.add_trace(go.Scatter(x=[cx], y=[cy], mode='markers', marker=cent_marker, name='Centroid'))
            
            p_xaxis = dict(visible=False, range=[-45, 45])
            p_yaxis = dict(visible=False, range=[-40, 45])
            p_legend = dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            
            fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis=p_xaxis, yaxis=p_yaxis, height=600, showlegend=True, legend=p_legend)
            
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Please enter gas values greater than 0.")
