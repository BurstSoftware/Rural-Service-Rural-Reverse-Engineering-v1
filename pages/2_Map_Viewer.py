from __future__ import annotations

import streamlit as st

from src.places import apply_place_filters, combined_frame, unique_sorted
from src.viz import point_deck, xyz_scatter

st.title("Map viewer")

df = combined_frame(st.session_state.get("assets", []))
if df.empty:
    st.warning("Upload a CSV, JSON, or GeoJSON file first.")
    st.stop()

st.sidebar.header("Place filters")

state_opts = ["All"] + unique_sorted(df["state"])
state = st.sidebar.selectbox("State", state_opts)
scoped = apply_place_filters(df, state=None if state == "All" else state)

county_opts = ["All"] + unique_sorted(scoped["county"])
county = st.sidebar.selectbox("County", county_opts)
scoped = apply_place_filters(scoped, county=None if county == "All" else county)

city_opts = ["All"] + unique_sorted(scoped["city"])
city = st.sidebar.selectbox("City", city_opts)
scoped = apply_place_filters(scoped, city=None if city == "All" else city)

zip_opts = ["All"] + unique_sorted(scoped["zip_code"])
zip_code = st.sidebar.selectbox("Zip code", zip_opts)
scoped = apply_place_filters(scoped, zip_code=None if zip_code == "All" else zip_code)

road_opts = ["All"] + unique_sorted(scoped["road"])
road = st.sidebar.selectbox("Road", road_opts)
scoped = apply_place_filters(scoped, road=None if road == "All" else road)

address_opts = ["All"] + unique_sorted(scoped["address"])
address = st.sidebar.selectbox("Address", address_opts)
filtered = apply_place_filters(scoped, address=None if address == "All" else address)

st.session_state.place_filters = {
    "state": state,
    "county": county,
    "city": city,
    "zip_code": zip_code,
    "road": road,
    "address": address,
}
st.session_state.filtered = filtered

mappable = filtered.dropna(subset=["lon", "lat"])
c1, c2, c3 = st.columns(3)
c1.metric("Filtered rows", len(filtered))
c2.metric("On map", len(mappable))
c3.metric("Roads", mappable["road"].nunique(dropna=True) if not mappable.empty else 0)

tab_map, tab_3d, tab_table = st.tabs(["Map", "3D", "Table"])

with tab_map:
    if mappable.empty:
        st.info("No rows with lon/lat for this filter.")
    else:
        try:
            st.pydeck_chart(point_deck(mappable))
        except Exception as exc:
            st.error(f"Map failed: {exc}")

with tab_3d:
    if mappable["z"].notna().sum() >= 2:
        st.plotly_chart(xyz_scatter(mappable, color="city"), use_container_width=True)
    else:
        st.info("Need a numeric z / elevation column for 3D.")

with tab_table:
    show = [
        c
        for c in ("state", "county", "city", "zip_code", "road", "address", "lon", "lat", "z", "_source")
        if c in filtered.columns
    ]
    st.dataframe(filtered[show], use_container_width=True)
