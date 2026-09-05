from __future__ import annotations

import streamlit as st

from src.io_loaders import LoadedAsset, load_uploaded

st.title("Upload")
st.caption("Accepted types: CSV, JSON, GeoJSON")

files = st.file_uploader(
    "Place files",
    type=["csv", "json", "geojson"],
    accept_multiple_files=True,
)

if files:
    for f in files:
        asset = load_uploaded(f.name, f.getvalue())
        names = [a.name for a in st.session_state.get("assets", [])]
        if asset.name not in names:
            st.session_state.setdefault("assets", []).append(asset)
        if asset.frame is None:
            st.error(f"{asset.name}: {asset.meta}")
        else:
            st.success(f"Loaded {asset.name} ({asset.kind}, {len(asset.frame)} rows)")
            st.json(asset.meta)
            preview_cols = [
                c
                for c in ("state", "county", "city", "zip_code", "road", "address", "lon", "lat")
                if c in asset.frame.columns
            ]
            st.dataframe(asset.frame[preview_cols].head(50), use_container_width=True)

assets: list[LoadedAsset] = st.session_state.get("assets", [])
if assets:
    st.subheader("Session files")
    st.table({"file": [a.name for a in assets], "kind": [a.kind for a in assets], "rows": [0 if a.frame is None else len(a.frame) for a in assets]})
    if st.button("Clear uploaded files"):
        st.session_state.assets = []
        st.rerun()
