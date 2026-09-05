from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.geo import path_length_m
from src.io_loaders import guess_xy_columns

st.title("Reports")

site = st.session_state.get("site_name", "Unassigned")
assets = st.session_state.get("assets", [])

rows = []
for a in assets:
    rec = {"file": a.name, "kind": a.kind, "rows": None, "path_m": None}
    if a.frame is not None:
        rec["rows"] = len(a.frame)
        lon_col, lat_col = guess_xy_columns(a.frame)
        if lon_col and lat_col:
            rec["path_m"] = round(path_length_m(a.frame.dropna(subset=[lon_col, lat_col]), lat_col, lon_col), 1)
    rows.append(rec)

summary = pd.DataFrame(rows)
st.subheader(f"{site} — {date.today().isoformat()}")
st.dataframe(summary, use_container_width=True)

md = [f"# Rural RE report — {site}", f"Date: {date.today().isoformat()}", ""]
for rec in rows:
    md.append(f"- **{rec['file']}** ({rec['kind']}) rows={rec['rows']} path_m={rec['path_m']}")
report = "\n".join(md)
st.download_button("Download markdown report", report, file_name=f"{site.replace(' ', '_')}_report.md")
