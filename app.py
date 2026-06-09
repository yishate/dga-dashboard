import streamlit as st
import plotly.graph_objects as go
import math


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
    x_labels = ['H<sub>2</sub>', 'CH<sub>4</sub>', 'C<sub>2</sub>H<sub>6</sub>', 'C<sub>2</sub>H<sub>4</sub>', 'C<sub>2</sub>H<sub>2</sub>']
    y_values = [val_h2, val_ch4, val_c2h6, val_c2h4, val_c2h2] 
    
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


st.set_page_config(page_title="Smart DGA Dashboard for Natural Ester", layout="wide")

with st.sidebar:
    st.title("Data Input")
  
    st.markdown("Enter gas concentrations (ppm)")
    
    st.divider()
    
    h2 = st.number_input("$H_2$ (Hydrogen)", min_value=0.0, value=0.00, step=0.01, format="%.2f")
    ch4 = st.number_input("$CH_4$ (Methane)", min_value=0.0, value=0.00, step=0.01, format="%.2f")
    c2h6 = st.number_input("$C_2H_6$ (Ethane)", min_value=0.0, value=0.00, step=0.01, format="%.2f")
    c2h4 = st.number_input("$C_2H_4$ (Ethylene)", min_value=0.0, value=0.00, step=0.01, format="%.2f")
    c2h2 = st.number_input("$C_2H_2$ (Acetylene)", min_value=0.0, value=0.00, step=0.01, format="%.2f")


st.title("Duval Pentagon 3 Dashboard for Natural Ester")
st.markdown("---")

col_pent_chart, col_pent_results = st.columns([7, 3])
total_5 = h2 + ch4 + c2h6 + c2h4 + c2h2
 
if total_5 > 0:
    p_H2 = (h2 / total_5) * 100
    p_C2H6 = (c2h6 / total_5) * 100
    p_CH4 = (ch4 / total_5) * 100
    p_C2H4 = (c2h4 / total_5) * 100
    p_C2H2 = (c2h2 / total_5) * 100
     
    p_ord = [p_H2, p_C2H6, p_CH4, p_C2H4, p_C2H2]
     

    angles = [90, 162, 234, 306, 18]
     
    x = []
    y = []
    for i in range(5):
        rad = math.radians(angles[i])
        x.append(p_ord[i] * math.cos(rad))
        y.append(p_ord[i] * math.sin(rad))
         
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
    else:
        # Fallback if area is perfectly 0 (pure gas). Centroid drops to 1/3 radius.
        cx = sum(x[:-1]) / 3.0
        cy = sum(y[:-1]) / 3.0


    pdX = [0, -1.8, -1.8, 0]
    pdY = [33, 33, 24, 24]
     
    d1X = [0, 38, 30.5, 6, 0]
    d1Y = [40, 12.4, -10.5, 12.5, 1.5]
     
    d2X = [0, 6, 30.5, 23.5, 0]
    d2Y = [1.5, 12.5, -10.5, -32.4, -3.29]
     
    t3X = [0, 23.5, 0]
    t3Y = [-3.29, -32.4, -32.4]
     
    t2X = [0, 0, -23.5, -9.91]
    t2Y = [1.5, -32.4, -32.4, 2.89]
     
    t1X = [0, -9.91, -23.5, -38, -9.7]
    t1Y = [1.5, 2.89, -32.4, 12.4, 5.8]
     
    sX  = [0, -9.7, -38, 0, 0, -1.8, -1.8, 0]
    sY  = [1.5, 5.8, 12.4, 40, 33, 33, 24, 24]

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
        st.subheader("Pentagon 3 Diagnosis")
        st.markdown(f"**Calculated Centroid:**\nX: {cx:.2f}, Y: {cy:.2f}")
        st.error("🚨 **Alert:** Fault detected.")
        st.markdown(f"**Fault Type:** {pent_fault}")
         
        st.divider()
        bc_fig2 = get_bar_chart(h2, ch4, c2h6, c2h2, c2h4)
        st.plotly_chart(bc_fig2, use_container_width=True, key="bar2")

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
            x=[0, -38, -23.5, 23.5, 38, 0], 
            y=[40, 12.4, -32.4, -32.4, 12.4, 40], 
            mode='lines+text', 
            line=bound_line, 
            text=['H<sub>2</sub>', 'C<sub>2</sub>H<sub>6</sub>', 'CH<sub>4</sub>', 'C<sub>2</sub>H<sub>4</sub>', 'C<sub>2</sub>H<sub>2</sub>', ''], 
            textposition="middle center", 
            textfont=bound_text, 
            name='Boundary', 
            hoverinfo='none'
        ))
         
        cent_marker = dict(symbol='circle', color='red', size=6, line=dict(color='red', width=1))
        fig2.add_trace(go.Scatter(x=[cx], y=[cy], mode='markers', marker=cent_marker, name='Centroid'))
         
        p_xaxis = dict(visible=False, range=[-45, 45])
        p_yaxis = dict(visible=False, range=[-45, 45], scaleanchor="x", scaleratio=1) 
        p_legend = dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
         
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis=p_xaxis, yaxis=p_yaxis, height=600, showlegend=True, legend=p_legend)
         
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Please enter gas values greater than 0.")
