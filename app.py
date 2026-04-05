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
        fill='toself', fillcolor=
