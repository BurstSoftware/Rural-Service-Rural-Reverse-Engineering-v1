from __future__ import annotations

import streamlit as st

from src.geo import path_length_m
from src.places import apply_place_filters, combined_frame, unique_sorted

st.title("Place directory")

df = combined_frame(st.session_state.get("assets", []))
if df.empty:
    st.warning("Upload data first.")
    st.stop()

filters = st.session_state.get("place_filters", {})
st.caption("Filters follow Map viewer when set; you can also change them here.")

c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)

state = c1.selectbox("State", ["All"] + unique_sorted(df["state"]), index=0)
county = c2.selectbox("County", ["All"] + unique_sorted(df["county"]), index=0)
city = c3.selectbox("City", ["All"] + unique_sorted(df["city"]), index=0)
zip_code = c4.selectbox("Zip code", ["All"] + unique_sorted(df["zip_code"]), index=0)
road = c5.selectbox("Road", ["All"] + unique_sorted(df["road"]), index=0)
address = c6.selectbox("Address", ["All"] + unique_sorted(df["address"]), index=0)

filtered = apply_place_filters(
    df,
    None if state == "All" else state,
    None if county == "All" else county,
    None if city == "All" else city,
    None if zip_code == "All" else zip_code,
    None if road == "All" else road,
    None if address == "All" else address,
)

mappable = filtered.dropna(subset=["lon", "lat"])
length = path_length_m(mappable) if len(mappable) >= 2 else 0.0

k1, k2, k3 = st.columns(3)
k1.metric("Places", len(filtered))
k2.metric("Mapped", len(mappable))
k3.metric("Ordered path", f"{length:,.1f} m")
st.caption("Path length only means something if rows are vertices along one road, in order.")

cols = [c for c in ("state", "county", "city", "zip_code", "road", "address", "lon", "lat", "z") if c in filtered.columns]
st.dataframe(filtered[cols], use_container_width=True)
st.download_button(
    "Download filtered CSV",
    filtered[cols].to_csv(index=False).encode("utf-8"),
    file_name="place_directory.csv",
    mime="text/csv",
)
