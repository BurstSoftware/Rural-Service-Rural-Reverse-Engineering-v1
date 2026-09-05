from __future__ import annotations

import streamlit as st
import pandas as pd

from src.places import combined_frame

st.set_page_config(page_title="Rural dispatch", page_icon="📦", layout="wide")

if "assets" not in st.session_state:
    st.session_state.assets = []


def _col(df: pd.DataFrame, names: list[str]) -> str | None:
    lower = {c.lower().strip(): c for c in df.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def _num(series: pd.Series) -> float:
    return float(pd.to_numeric(series, errors="coerce").fillna(0).sum())


def kpis(df: pd.DataFrame) -> dict[str, float | int]:
    empty = {
        "cycle_1_packages": 0,
        "same_day_packages": 0,
        "non_conveyor_packages": 0,
        "trucks_this_week": 0,
        "total_volume": 0.0,
        "routes_by_dsp": 0,
        "totes": 0,
    }
    if df is None or df.empty:
        return empty

    pkg_col = _col(df, ["packages", "package_count", "pkg_count", "parcel_count"])
    cycle_col = _col(df, ["cycle", "cycle_name", "sort_cycle", "wave"])
    same_day_col = _col(df, ["same_day", "is_same_day", "sameday"])
    conveyor_col = _col(df, ["conveyor", "is_conveyor", "non_conveyor", "induct_type"])
    truck_col = _col(df, ["trucks", "truck_count", "trailer_count", "truck_id"])
    week_col = _col(df, ["week", "week_of", "service_week"])
    volume_col = _col(df, ["volume", "total_volume", "cube", "cuft", "volume_m3"])
    route_col = _col(df, ["route", "route_id", "delivery_route", "routes"])
    dsp_col = _col(df, ["dsp", "provider", "delivery_service_provider", "carrier"])
    tote_col = _col(df, ["totes", "tote_count", "tote_id"])

    out = dict(empty)

    if cycle_col is not None:
        cycle = df[cycle_col].astype(str).str.lower()
        mask = cycle.str.contains(r"\bcycle\s*1\b|^1$|c1", regex=True)
        out["cycle_1_packages"] = int(_num(df.loc[mask, pkg_col])) if pkg_col else int(mask.sum())

    if same_day_col is not None:
        raw = df[same_day_col]
        if raw.dtype == bool or set(raw.dropna().astype(str).str.lower().unique()) <= {"true", "false", "1", "0", "yes", "no", "y", "n"}:
            flag = raw.astype(str).str.lower().isin({"true", "1", "yes", "y"})
            out["same_day_packages"] = int(_num(df.loc[flag, pkg_col])) if pkg_col else int(flag.sum())
        else:
            flag = raw.astype(str).str.lower().str.contains("same")
            out["same_day_packages"] = int(_num(df.loc[flag, pkg_col])) if pkg_col else int(flag.sum())
    elif cycle_col is not None:
        flag = df[cycle_col].astype(str).str.lower().str.contains("same")
        out["same_day_packages"] = int(_num(df.loc[flag, pkg_col])) if pkg_col else int(flag.sum())

    if conveyor_col is not None:
        text = df[conveyor_col].astype(str).str.lower()
        if "non_conveyor" in conveyor_col.lower() or text.str.contains("non").any():
            flag = text.str.contains("non") | text.isin({"1", "true", "yes"})
            if conveyor_col.lower() in {"conveyor", "is_conveyor"}:
                flag = text.isin({"0", "false", "no", "n", "non", "non-conveyor", "non_conveyor", "manual"})
            out["non_conveyor_packages"] = int(_num(df.loc[flag, pkg_col])) if pkg_col else int(flag.sum())
        else:
            flag = text.isin({"0", "false", "no", "n", "manual", "off-conveyor", "off_conveyor"})
            out["non_conveyor_packages"] = int(_num(df.loc[flag, pkg_col])) if pkg_col else int(flag.sum())

    if truck_col is not None:
        if truck_col.lower() in {"truck_id"}:
            work = df
            if week_col is not None:
                work = df  # current file is treated as this week
            out["trucks_this_week"] = int(work[truck_col].nunique(dropna=True))
        else:
            out["trucks_this_week"] = int(_num(df[truck_col]))

    if volume_col is not None:
        out["total_volume"] = round(_num(df[volume_col]), 1)

    if route_col is not None:
        if dsp_col is not None:
            out["routes_by_dsp"] = int(df.dropna(subset=[route_col]).groupby(dsp_col)[route_col].nunique().sum())
        else:
            out["routes_by_dsp"] = int(df[route_col].nunique(dropna=True))

    if tote_col is not None:
        if tote_col.lower() in {"tote_id"}:
            out["totes"] = int(df[tote_col].nunique(dropna=True))
        else:
            out["totes"] = int(_num(df[tote_col]))

    return out


df = combined_frame(st.session_state.assets)
metrics = kpis(df)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.4rem;}
      div[data-testid="stMetric"] {
        background: #e8efe8;
        border: 1px solid #c5d4c7;
        border-radius: 14px;
        padding: 12px 16px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

r1c1, r1c2, r1c3, r1c4 = st.columns(4)
r1c1.metric("Cycle 1 packages", f"{metrics['cycle_1_packages']:,}")
r1c2.metric("Same-day packages", f"{metrics['same_day_packages']:,}")
r1c3.metric("Non-conveyor packages", f"{metrics['non_conveyor_packages']:,}")
r1c4.metric("Trucks this week", f"{metrics['trucks_this_week']:,}")

r2c1, r2c2, r2c3 = st.columns(3)
r2c1.metric("Total volume", f"{metrics['total_volume']:,}")
r2c2.metric("Delivery routes by DSP", f"{metrics['routes_by_dsp']:,}")
r2c3.metric("Totes", f"{metrics['totes']:,}")

if df.empty:
    st.caption("Upload a file with package columns to populate these counts.")
