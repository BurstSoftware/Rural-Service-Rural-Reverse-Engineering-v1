from __future__ import annotations

import streamlit as st

from src.geo import bbox, path_length_m
from src.io_loaders import guess_xy_columns

st.title("Measure")

assets = [a for a in st.session_state.get("assets", []) if a.frame is not None]
if not assets:
    st.warning("No tabular geometry loaded.")
    st.stop()

asset = st.selectbox("Asset", assets, format_func=lambda a: a.name)
df = asset.frame
lon_col, lat_col = guess_xy_columns(df)
cols = list(df.columns)

c1, c2 = st.columns(2)
lon_col = c1.selectbox("Lon", cols, index=cols.index(lon_col) if lon_col in cols else 0)
lat_col = c2.selectbox("Lat", cols, index=cols.index(lat_col) if lat_col in cols else min(1, len(cols) - 1))

work = df.dropna(subset=[lon_col, lat_col]).copy()
if work.empty:
    st.error("No valid coordinate rows.")
    st.stop()

length = path_length_m(work, lat_col, lon_col)
box = bbox(work, lon_col, lat_col)

k1, k2, k3 = st.columns(3)
k1.metric("Points", len(work))
k2.metric("Path length", f"{length:,.1f} m")
k3.metric("Path length", f"{length / 1000:,.3f} km")

st.json(box)
st.caption("Length assumes rows are ordered along the feature (road centerline, traverse, etc.).")
