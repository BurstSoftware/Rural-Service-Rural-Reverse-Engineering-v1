from __future__ import annotations

import streamlit as st
import pandas as pd

from src.places import combined_frame

st.set_page_config(page_title="Rural dispatch", page_icon="📦", layout="wide")

if "assets" not in st.session_state:
    st.session_state.assets = []


def _col(df: pd.DataFrame, names: list[str]) -> str | None:
    lower = {str(c).lower().strip(): c for c in df.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def _num(series: pd.Series) -> float:
    return float(pd.to_numeric(series, errors="coerce").fillna(0).sum())


def _truthy(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip().str.lower()
    return text.isin({"true", "1", "yes", "y", "t"})


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
    cycle_col = _col(df, ["cycle", "sort_cycle", "cycle_name", "wave"])
    same_day_col = _col(df, ["same_day", "is_same_day", "sameday"])
    conveyor_col = _col(df, ["induct_type", "non_conveyor", "conveyor", "is_conveyor"])
    truck_col = _col(df, ["truck_id", "trucks", "truck_count", "trailer_count"])
    volume_col = _col(df, ["volume", "total_volume", "cube", "cuft", "volume_m3"])
    route_col = _col(df, ["route_id", "route", "delivery_route", "routes"])
    dsp_col = _col(df, ["dsp", "delivery_service_provider", "provider", "carrier"])
    tote_col = _col(df, ["tote_id", "totes", "tote_count"])

    out = dict(empty)

    def pkg_sum(mask: pd.Series) -> int:
        if pkg_col:
            return int(_num(df.loc[mask, pkg_col]))
        return int(mask.sum())

    if cycle_col is not None:
        cycle = df[cycle_col].astype(str).str.strip().str.lower()
        mask = cycle.isin({"1", "1.0", "c1", "cycle 1", "cycle1"})
        out["cycle_1_packages"] = pkg_sum(mask)

    if same_day_col is not None:
        flag = _truthy(df[same_day_col]) | df[same_day_col].astype(str).str.lower().str.contains("same", na=False)
        out["same_day_packages"] = pkg_sum(flag)
    elif cycle_col is not None:
        flag = df[cycle_col].astype(str).str.lower().str.contains("same", na=False)
        out["same_day_packages"] = pkg_sum(flag)

    if conveyor_col is not None:
        text = df[conveyor_col].astype(str).str.strip().str.lower()
        if conveyor_col.lower() in {"conveyor", "is_conveyor"}:
            flag = ~_truthy(df[conveyor_col]) | text.isin({"false", "0", "no", "n", "manual", "non", "non_conveyor", "non-conveyor"})
        else:
            flag = text.str.contains("non", na=False) | text.isin({"manual", "off", "off_conveyor"})
        out["non_conveyor_packages"] = pkg_sum(flag)

    if truck_col is not None:
        if truck_col.lower().endswith("_id") or truck_col.lower() == "truck_id":
            out["trucks_this_week"] = int(df[truck_col].dropna().astype(str).nunique())
        else:
            out["trucks_this_week"] = int(_num(df[truck_col]))

    if volume_col is not None:
        out["total_volume"] = round(_num(df[volume_col]), 1)

    if route_col is not None:
        if dsp_col is not None:
            out["routes_by_dsp"] = int(
                df.dropna(subset=[route_col]).groupby(df[dsp_col].astype(str))[route_col].nunique().sum()
            )
        else:
            out["routes_by_dsp"] = int(df[route_col].nunique(dropna=True))

    if tote_col is not None:
        if tote_col.lower() in {"tote_id"}:
            out["totes"] = int(df[tote_col].dropna().astype(str).nunique())
        else:
            out["totes"] = int(_num(df[tote_col]))

    return out


df = combined_frame(st.session_state.assets)
metrics = kpis(df)

st.markdown(
    """
    <style>
      [data-testid="stHeader"] {background: transparent;}
      .block-container {padding-top: 1rem;}
      h1.dispatch-title {font-size: 1.6rem; margin: 0 0 .25rem 0;}
      p.dispatch-sub {color: #5b675e; margin: 0 0 1rem 0;}
      div[data-testid="stMetric"] {
        background: #e8efe8;
        border: 1px solid #c5d4c7;
        border-radius: 14px;
        padding: 12px 16px;
      }
    </style>
    <h1 class="dispatch-title">Rural dispatch</h1>
    <p class="dispatch-sub">Cycle 1 · same-day · non-conveyor · trucks · volume · DSP routes · totes</p>
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
