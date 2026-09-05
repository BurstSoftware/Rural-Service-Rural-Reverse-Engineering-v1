from __future__ import annotations

import streamlit as st

from src.io_loaders import LoadedAsset, load_uploaded

st.title("Upload")

files = st.file_uploader(
    "Survey / scan files",
    type=["csv", "geojson", "json", "ply", "pcd", "las", "laz", "tif", "tiff"],
    accept_multiple_files=True,
)

if files:
    for f in files:
        asset = load_uploaded(f.name, f.getvalue())
        existing = [a.name for a in st.session_state.get("assets", [])]
        if asset.name not in existing:
            st.session_state.setdefault("assets", []).append(asset)
        st.success(f"Loaded {asset.name} ({asset.kind})")
        st.json(asset.meta)
        if asset.frame is not None:
            st.dataframe(asset.frame.head(50), use_container_width=True)

assets: list[LoadedAsset] = st.session_state.get("assets", [])
if assets:
    st.subheader("Session assets")
    st.table({"file": [a.name for a in assets], "kind": [a.kind for a in assets]})
