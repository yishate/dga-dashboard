import streamlit as st
import plotly.graph_objects as go

# ==========================================
# 1. THE "BRAIN": CALCULATION FUNCTION
# ==========================================
def get_duval_diagnosis(ch4, c2h4, c2h2):
    total = ch4 + c2h4 + c2h2
    
    # Safety check: Prevent 0 division
    if total == 0:
        return 0, 0, 0, "Normal", "Enter gas values to see diagnosis."
        
    p_ch4 = (ch4 / total) * 100
    p_c2h4 = (c2h4 / total) * 100
    p_c2h2 = (c2h2 / total) * 100
    
    # Standard Duval Triangle 1 Logic
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
    
    # The moment you change these, the charts will update instantly
    h2 = st.number_input("Hydrogen (H2)", min_value=0.0, value=10.0, step=1.0)
    ch4 = st.number_input("Methane (CH4)", min_value=0.0, value=50.0, step=1.0)
    c2h6 = st.number_input("Ethane (C2H6)", min_value=0.0, value=20.0, step=1.0)
    c2h2 = st.number_input("Acetylene (C2H2)", min_value=0.0, value=5.0, step=1.0)
    c2h4 = st.number_input("Ethylene (C2H4)", min_value=0.0, value=40.0, step=1.0)

# ==========================================
# 3. MAIN INTERFACE & VISUALISATION
# ==========================================
st.title("Smart DGA Dashboard")

# Run math immediately based on current sidebar inputs
p_ch4, p_c2h4, p_c2h2, fault_type, report = get_duval_diagnosis(ch4, c2h4, c2h2)

tab1, tab2 = st.tabs(["Duval Triangle", "Duval Pentagon"])

# ------------------------------------------
# TAB 1: DUVAL TRIANGLE WITH COLOURED ZONES
# ------------------------------------------
with tab1:
    col_chart, col_results = st.columns([7, 3])
    
    with col_results:
        st.subheader("Triangle Diagnosis")
        if fault_type == "Normal":
            st.success("🟢 **Status:** Normal")
        else:
            st.error("🚨 **Alert:** Fault detected.")
            st.markdown(f"**Fault Type:** {fault_type}")
            st.write(f"**Oil Type Selected:** {oil_type}")

    with col_chart:
        st.subheader("Interactive Fault Map (Triangle 1)")
        
        if (ch4 + c2h4 + c2h2) > 0:
            fig = go.Figure()
            
            # --- BASE LAYERS: DRAWING THE COLOURED FAULT ZONES ---
            fig.add_trace(go.Scatterternary(a=[98, 100, 98], b=[0, 0, 2], c=[2, 0, 0], mode='lines', fill='toself', fillcolor='rgba(128, 0, 0, 0.6)', line=dict(color='black', width=1), name='PD', hoverinfo='name'))
            fig.add_trace(go.Scatterternary(a=[98, 98, 76, 80], b=[0, 2, 4, 0], c=[2, 0, 20, 20], mode='lines', fill='toself', fillcolor='rgba(255, 165, 0, 0.6)', line=dict(color='black', width=1), name='T1', hoverinfo='name'))
            fig.add_trace(go.Scatterternary(a=[80, 76, 46, 50], b=[0, 4, 4, 0], c=[20, 20, 50, 50], mode='lines', fill='toself', fillcolor='rgba(255, 200, 150, 0.8)', line=dict(color='black', width=1), name='T2', hoverinfo='name'))
            fig.add_trace(go.Scatterternary(a=[50, 46, 31, 0, 0], b=[0, 4, 15, 15, 0], c=[50, 50, 54, 85, 100], mode='lines', fill='toself', fillcolor='rgba(139, 69, 19, 0.6)', line=dict(color='black', width=1), name='T3', hoverinfo='name'))
            fig.add_trace(go.Scatterternary(a=[98, 87, 64, 76], b=[2, 13, 13, 4], c=[0, 0, 23, 20], mode='lines', fill='toself', fillcolor='rgba(173, 216, 230, 0.6)', line=dict(color='black', width=1), name='D1', hoverinfo='name'))
            fig.add_trace(go.Scatterternary(a=[87, 0, 0, 31, 46, 64], b=[13, 100, 71, 15, 4, 13], c=[0, 0, 29, 54, 50, 23], mode='lines', fill='toself', fillcolor='rgba(135, 206, 250, 0.8)', line=dict(color='black', width=1), name='D2', hoverinfo='name'))
            fig.add_trace(go.Scatterternary(a=[64, 46, 31, 0, 0], b=[13, 4, 15, 71, 15], c=[23, 50, 54, 29, 85], mode='lines', fill='toself', fillcolor='rgba(224, 255, 255, 0.8)', line=dict(color='black', width=1), name='DT', hoverinfo='name'))

            # --- TOP LAYER: THE CALCULATED FAULT POINT ---
            fig.add_trace(go.Scatterternary(
                a=[p_ch4], b=[p_c2h2], c=[p_c2h4],
                mode='markers',
                marker=dict(symbol='circle', color='black', size=14, line=dict(color='white', width=2)),
                name='Calculated Point',
                text=[f"Fault: {fault_type}"],
                hoverinfo='text'
            ))
            
            # Clean layout with white background
            fig.update_layout({
                'plot_bgcolor': 'white',
                'paper_bgcolor': 'white',
                'ternary': {
                    'sum': 100,
                    'aaxis': {'title': 'CH4 %', 'min': 0, 'linewidth': 2, 'ticks': 'outside'},
                    'baxis': {'title': 'C2H2 %', 'min': 0, 'linewidth': 2, 'ticks': 'outside'},
                    'caxis': {'title': 'C2H4 %', 'min': 0, 'linewidth': 2, 'ticks': 'outside'}
                },
                'height': 500
            })
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please enter values greater than 0 for CH4, C2H4, or C2H2 to see the plot.")

# ------------------------------------------
# TAB 2: DUVAL PENTAGON (CENTRE OF GRAVITY)
# ------------------------------------------
with tab2:
    st.subheader("Interactive Fault Map (Pentagon 1)")
    
    total_5 = h2 + c2h6 + ch4 + c2h4 + c2h2
    
    if total_5 > 0:
        # 1. Calculate relative percentages (from 0.0 to 1.0)
        p_h2 = h2 / total_5
        p_c2h6 = c2h6 / total_5
        p_ch4 = ch4 / total_5
        p_c2h4 = c2h4 / total_5
        p_c2h2 = c2h2 / total_5
        
        # 2. Fixed (X, Y) coordinates for the 5 corners of the Pentagon
        # Order: H2(Top), C2H6(Top Left), CH4(Bottom Left), C2H4(Bottom Right), C2H2(Top Right)
        x_corners = [0, -0.951, -0.588, 0.588, 0.951]
        y_corners = [1, 0.309, -0.809, -0.809, 0.309]
        
        # 3. Calculate the Centre of Gravity (The Fault Point)
        point_x = sum([p * x for p, x in zip([p_h2, p_c2h6, p_ch4, p_c2h4, p_c2h2], x_corners)])
        point_y = sum([p * y for p, y in zip([p_h2, p_c2h6, p_ch4, p_c2h4, p_c2h2], y_corners)])
        
        fig2 = go.Figure()

        # --- BASE LAYERS: DRAWING THE COLOURED PENTAGON ZONES ---
        # S (Stray Gassing) Zone
        fig2.add_trace(go.Scatter(x=[0, -0.951, -0.8, -0.2, 0, 0], y=[1, 0.309, -0.1, -0.1, 0.1, 1], mode='lines', fill='toself', fillcolor='rgba(255, 255, 204, 0.6)', line
