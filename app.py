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
    st.subheader("Duval Pentagon (Radar Analysis)")
    st.write("Visualizing all 5 gases to detect stray gassing characteristics.")
    
    # A Radar chart acts as a perfect visual substitute for the Pentagon
    total_5 = h2 + ch4 + c2h6 + c2h4 + c2h2
    if total_5 > 0:
        fig2 = go.Figure(data=go.Scatterpolar(
          r=[(h2/total_5)*100, (c2h6/total_5)*100, (ch4/total_5)*100, (c2h4/total_5)*100, (c2h2/total_5)*100],
          theta=['H2','C2H6','CH4','C2H4','C2H2'],
          fill='toself',
          line_color='blue'
        ))
        fig2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Enter gas values to generate Pentagon analysis.")