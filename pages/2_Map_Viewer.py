with tab_map:
    if mappable.empty:
        st.info("No rows with lon/lat for this filter.")
    else:
        try:
            st.pydeck_chart(point_deck(mappable, lon_col="lon", lat_col="lat"))
        except Exception as exc:
            st.error(f"Map failed: {exc}")

with tab_3d:
    if "z" in mappable.columns and mappable["z"].notna().sum() >= 2:
        try:
            st.plotly_chart(
                xyz_scatter(mappable, x="lon", y="lat", z="z", color="city"),
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"3D failed: {exc}")
    else:
        st.info("Need a numeric z / elevation column for 3D.")
