from __future__ import annotations

import pandas as pd
import pydeck as pdk
import plotly.express as px


def point_deck(df: pd.DataFrame, lon_col: str = "lon", lat_col: str = "lat") -> pdk.Deck:
    work = df.dropna(subset=[lon_col, lat_col]).copy()
    if work.empty:
        raise ValueError("No mappable lon/lat rows")
    view = pdk.ViewState(
        latitude=float(work[lat_col].mean()),
        longitude=float(work[lon_col].mean()),
        zoom=12,
        pitch=35,
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=work,
        get_position=[lon_col, lat_col],
        get_color=[61, 107, 79, 190],
        get_radius=18,
        pickable=True,
        radius_min_pixels=4,
    )
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={
            "html": "<b>{address}</b><br/>{road}<br/>{city}, {state} {zip_code}",
            "style": {"backgroundColor": "#1c241e", "color": "#f6f3ec"},
        },
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    )


def xyz_scatter(df: pd.DataFrame, color: str | None = "city"):
    work = df.dropna(subset=["lon", "lat", "z"])
    color_col = color if color and color in work.columns else None
    return px.scatter_3d(work, x="lon", y="lat", z="z", color=color_col, hover_data=["address", "road", "zip_code"])
