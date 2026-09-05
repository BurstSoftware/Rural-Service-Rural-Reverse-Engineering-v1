from __future__ import annotations

import pandas as pd
import pydeck as pdk
import plotly.express as px


def point_deck(df: pd.DataFrame, lon_col: str, lat_col: str, color=(61, 107, 79)) -> pdk.Deck:
    view = pdk.ViewState(
        latitude=float(df[lat_col].mean()),
        longitude=float(df[lon_col].mean()),
        zoom=13,
        pitch=40,
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=[lon_col, lat_col],
        get_color=list(color) + [180],
        get_radius=12,
        pickable=True,
    )
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={"text": "{index}"},
        map_style=None,
    )


def xyz_scatter(df: pd.DataFrame, x: str, y: str, z: str, color: str | None = None):
    return px.scatter_3d(df, x=x, y=y, z=z, color=color, opacity=0.7)
