from __future__ import annotations

import streamlit as st

from src.io_loaders import guess_xy_columns
from src.viz import point_deck, xyz_scatter

st.title("Viewer")

assets = st.session_state.get("assets", [])
named = {a.name: a for a in assets if a.frame is not None}
if not named:
    st.warning("Upload a CSV or GeoJSON with coordinates first.")
    st.stop()

choice = st.selectbox("Asset", list(named))
df = named[choice].frame
st.dataframe(df.head(20), use_container_width=True)

lon_col, lat_col = guess_xy_columns(df)
cols = list(df.columns)

c1, c2, c3 = st.columns(3)
lon_col = c1.selectbox("Lon / X", cols, index=cols.index(lon_col) if lon_col in cols else 0)
lat_col = c2.selectbox("Lat / Y", cols, index=cols.index(lat_col) if lat_col in cols else min(1, len(cols) - 1))
z_candidates = [c for c in cols if c.lower() in {"z", "elev", "elevation", "height"}]
z_col = c3.selectbox("Z (optional)", ["—"] + cols, index=(cols.index(z_candidates[0]) + 1) if z_candidates else 0)

tab_map, tab_3d = st.tabs(["Map", "3D scatter"])
with tab_map:
    try:
        st.pydeck_chart(point_deck(df.dropna(subset=[lon_col, lat_col]), lon_col, lat_col))
    except Exception as exc:
        st.error(f"Map failed: {exc}")

with tab_3d:
    if z_col != "—":
        st.plotly_chart(xyz_scatter(df, lon_col, lat_col, z_col), use_container_width=True)
    else:
        st.info("Pick a Z column for a 3D preview.")
