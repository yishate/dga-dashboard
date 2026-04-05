import streamlit as st
import plotly.graph_objects as go

# ==========================================
# 1. THE "BRAIN": CALCULATION FUNCTION
# ==========================================
def get_duval_diagnosis(ch4, c2h4, c2h2):
    total = ch4 + c2h4 + c2h2
    
    # Safety check: Prevent 0 division. Return early if no gases.
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
    
    # The moment you change these, the charts will update instantly!
    h2 = st.number_input("Hydrogen (H2)", min_value=0.0, value=10.0, step=1.0)
    ch4 = st.number_input("Methane (CH4)", min_value=0.0, value=50.0, step=1.0)
    c2h6 = st.number_input("Ethane (C2H6)", min_value=0.0, value=20.0, step=1.0)
    c2h2 = st.number_input("Acetylene (C2H2)", min_value=0.0, value=5.0, step=1.0)
    c2h4 = st.number_input("Ethylene (C2H4)", min_value=0.0, value=40.0, step=1.0)

# ==========================================
# 3. MAIN INTERFACE & VISUALIZATION
# ==========================================
st.title("Smart DGA Dashboard")

# Run math immediately based on current sidebar inputs
p_ch4, p_c2h4, p_c2h2, fault_type, report = get_duval_diagnosis(ch4, c2h4, c2h2)

tab1, tab2 = st.tabs(["Duval Triangle", "Duval Pentagon"])

with tab1:
    col_chart, col_results = st.columns([7, 3])
    
    with col_results:
        st.subheader("Diagnosis")
        if fault_type == "Normal":
            st.success("🟢 **Status:** Normal")
        else:
            st.error("🚨 **Alert:** Fault detected.")
            st.markdown(f"**Fault Type:** {fault_type}")
            st.write(f"**Oil Type Selected:** {oil_type}")

    with col_chart:
        st.subheader("Interactive Fault Map")
        
        # Only draw if the sum > 0
        if (ch4 + c2h4 + c2h2) > 0:
            fig = go.Figure(go.Scatterternary({
                'mode': 'markers',
                'a': [p_ch4],   # Top
                'b': [p_c2h2],  # Bottom Left
                'c': [p_c2h4],  # Bottom Right
                'marker': {'symbol': 'circle', 'color': 'red', 'size': 14},
                'name': 'Fault Point'
            }))
            
            fig.update_layout({
                'ternary': {
                    'sum': 100,
                    'aaxis': {'title': 'CH4 %', 'min': 0, 'linewidth': 2, 'ticks': 'outside'},
                    'baxis': {'title': 'C2H2 %', 'min': 0, 'linewidth': 2, 'ticks': 'outside'},
                    'caxis': {'title': 'C2H4 %', 'min': 0, 'linewidth': 2, 'ticks': 'outside'}
                }
            })
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please enter values greater than 0 for CH4, C2H4, or C2H2 to see the plot.")

with tab2:
    st.subheader("Duval Pentagon (Center of Gravity Analysis)")
    st.write("Calculates the precise (X, Y) fault coordinate based on the relative weight of all 5 gases.")
    
    total_5 = h2 + c2h6 + ch4 + c2h4 + c2h2
    
    if total_5 > 0:
        # 1. Calculate relative percentages (from 0.0 to 1.0)
        p_h2 = h2 / total_5
        p_c2h6 = c2h6 / total_5
        p_ch4 = ch4 / total_5
        p_c2h4 = c2h4 / total_5
        p_c2h2 = c2h2 / total_5
        
        # 2. Define the fixed (X, Y) coordinates for the 5 corners of the Pentagon
        # H2 (Top), C2H6 (Top Right), CH4 (Bottom Right), C2H4 (Bottom Left), C2H2 (Top Left)
        x_corners = [0, 0.951, 0.588, -0.588, -0.951]
        y_corners = [1, 0.309, -0.809, -0.809, 0.309]
        
        # 3. Calculate the Center of Gravity (The Fault Point)
        point_x = (p_h2 * x_corners[0]) + (p_c2h6 * x_corners[1]) + (p_ch4 * x_corners[2]) + (p_c2h4 * x_corners[3]) + (p_c2h2 * x_corners[4])
        point_y = (p_h2 * y_corners[0]) + (p_c2h6 * y_corners[1]) + (p_ch4 * y_corners[2]) + (p_c2h4 * y_corners[3]) + (p_c2h2 * y_corners[4])
        
        # 4. Draw the actual Pentagon shape using Plotly Scatter
        # We repeat the first coordinate at the end to close the shape's outline
        x_pentagon = [0, 0.951, 0.588, -0.588, -0.951, 0]
        y_pentagon = [1, 0.309, -0.809, -0.809, 0.309, 1]
        
        fig2 = go.Figure()
        
        # Draw the Pentagon Outline
        fig2.add_trace(go.Scatter(
            x=x_pentagon, y=y_pentagon, 
            mode='lines+text', 
            line=dict(color='black', width=2),
            text=['H2', 'C2H6', 'CH4', 'C2H4', 'C2H2', ''], # Labels for the corners
            textposition="top center",
            textfont=dict(size=14, color="blue", weight="bold"),
            name='Duval Pentagon Boundary'
        ))
        
        # Plot the calculated Fault Point inside it
        fig2.add_trace(go.Scatter(
            x=[point_x], y=[point_y], 
            mode='markers', 
            marker=dict(symbol='circle', color='red', size=14),
            name='Calculated Fault Point'
        ))
        
        # Clean up the graph background so it looks like an engineering diagram
        fig2.update_layout(
            xaxis=dict(visible=False, range=[-1.5, 1.5]),
            yaxis=dict(visible=False, range=[-1.5, 1.5]),
            height=500,
            template="plotly_white",
            showlegend=False
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Enter gas values greater than 0 to generate the Pentagon analysis.")
