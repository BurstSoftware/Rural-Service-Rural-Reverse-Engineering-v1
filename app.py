from __future__ import annotations

import streamlit as st

from src.places import combined_frame

st.set_page_config(page_title="Rural places", page_icon="🌾", layout="wide")

if "assets" not in st.session_state:
    st.session_state.assets = []

st.title("Rural places map")
st.caption("CSV · JSON · GeoJSON  ·  filter by state, county, city, zip, road, address")

frame = combined_frame(st.session_state.assets)
n = len(st.session_state.assets)
mappable = int(frame[["lon", "lat"]].dropna().shape[0]) if not frame.empty else 0

c1, c2, c3 = st.columns(3)
c1.metric("Files", n)
c2.metric("Rows", len(frame))
c3.metric("Mapped points", mappable)

st.markdown(
    """
1. **Upload** — `.csv`, `.json`, `.geojson`  
2. **Map viewer** — place filters + map  
3. **Place directory** — table for the current filters  
4. **Place reports** — export a filtered summary

Expected columns (aliases accepted): `state`, `county`, `city`, `address`, `road`, `zip` / `zip_code`, `lon`, `lat`.
"""
)
