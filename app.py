from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Rural RE / Services",
    page_icon="🌾",
    layout="wide",
)

if "assets" not in st.session_state:
    st.session_state.assets = []
if "site_name" not in st.session_state:
    st.session_state.site_name = "Unassigned"

st.title("Rural reverse engineering & services")
st.caption("Scan-to-model workspace for rural roads, settlements, and service assets")

st.session_state.site_name = st.sidebar.text_input("Site name", st.session_state.site_name)
st.sidebar.selectbox("Focus", ["Road corridor", "Settlement", "Building", "Service point"])

n = len(st.session_state.assets)
c1, c2, c3 = st.columns(3)
c1.metric("Loaded files", n)
c2.metric("Site", st.session_state.site_name)
c3.metric("Next step", "Upload" if n == 0 else "Viewer / Measure")

st.markdown(
    """
Use the pages in order:

1. **Upload** — CSV surveys, GeoJSON, later LAS/PLY  
2. **Viewer** — map and 3D preview  
3. **Measure** — lengths, bbox, simple chainage  
4. **Reports** — export a field summary
"""
)
