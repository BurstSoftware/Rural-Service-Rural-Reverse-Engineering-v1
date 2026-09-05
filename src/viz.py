from __future__ import annotations

import pandas as pd
import pydeck as pdk
import plotly.express as px


def point_deck(
    df: pd.DataFrame,
    lon_col: str = "lon",
    lat_col: str = "lat",
    color=(61, 107, 79),
) -> pdk.Deck:
    work = df.dropna(subset=[lon_col, lat_col]).copy()
    if work.empty:
        raise ValueError("No mappable lon/lat rows")

    view = pdk.ViewState(
        latitude=float(work[lat_col].mean()),
        longitude=float(work[lon_col].mean()),
        zoom=12,
        pitch=35,
    )
    r, g, b = color[:3]
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=work,
        get_position=[lon_col, lat_col],
        get_color=[r, g, b, 190],
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


def xyz_scatter(
    df: pd.DataFrame,
    x: str = "lon",
    y: str = "lat",
    z: str = "z",
    color: str | None = "city",
):
    needed = [c for c in (x, y, z) if c in df.columns]
    work = df.dropna(subset=[c for c in (x, y, z) if c in df.columns])
    if work.empty or z not in work.columns:
        raise ValueError("Need lon, lat, and z columns for 3D")
    color_col = color if color and color in work.columns else None
    hover = [c for c in ("address", "road", "zip_code", "city", "state") if c in work.columns]
    return px.scatter_3d(work, x=x, y=y, z=z, color=color_col, hover_data=hover)
