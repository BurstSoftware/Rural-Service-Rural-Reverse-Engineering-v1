from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.geo import bbox, path_length_m
from src.places import apply_place_filters, combined_frame

st.title("Place reports")

df = combined_frame(st.session_state.get("assets", []))
if df.empty:
    st.warning("Upload data first.")
    st.stop()

filters = st.session_state.get("place_filters", {})
filtered = apply_place_filters(
    df,
    None if filters.get("state") in (None, "All") else filters.get("state"),
    None if filters.get("county") in (None, "All") else filters.get("county"),
    None if filters.get("city") in (None, "All") else filters.get("city"),
    None if filters.get("zip_code") in (None, "All") else filters.get("zip_code"),
    None if filters.get("road") in (None, "All") else filters.get("road"),
    None if filters.get("address") in (None, "All") else filters.get("address"),
)

mappable = filtered.dropna(subset=["lon", "lat"])
box = bbox(mappable)
length = path_length_m(mappable) if len(mappable) >= 2 else 0.0

st.subheader(f"Report — {date.today().isoformat()}")
st.json(filters or {"note": "Open Map viewer once to store filters; otherwise this is the full dataset."})

summary = pd.DataFrame(
    [
        {"metric": "rows", "value": len(filtered)},
        {"metric": "mapped_points", "value": len(mappable)},
        {"metric": "states", "value": filtered["state"].nunique(dropna=True)},
        {"metric": "counties", "value": filtered["county"].nunique(dropna=True)},
        {"metric": "cities", "value": filtered["city"].nunique(dropna=True)},
        {"metric": "zip_codes", "value": filtered["zip_code"].nunique(dropna=True)},
        {"metric": "roads", "value": filtered["road"].nunique(dropna=True)},
        {"metric": "addresses", "value": filtered["address"].nunique(dropna=True)},
        {"metric": "path_m", "value": round(length, 1)},
    ]
)
st.dataframe(summary, use_container_width=True)
if box:
    st.write("Bounding box", box)

lines = [
    f"# Place report — {date.today().isoformat()}",
    "",
    f"Filters: {filters}",
    f"Rows: {len(filtered)}",
    f"Mapped points: {len(mappable)}",
    f"Path (ordered points): {length:.1f} m",
    "",
    "## Counts",
]
for _, row in summary.iterrows():
    lines.append(f"- {row['metric']}: {row['value']}")
report = "\n".join(lines)

st.download_button("Download markdown report", report, file_name="place_report.md")
st.download_button(
    "Download filtered CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="place_report.csv",
    mime="text/csv",
)
