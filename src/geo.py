from __future__ import annotations

import math

import pandas as pd
from pyproj import Transformer


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def path_length_m(df: pd.DataFrame, lat_col: str, lon_col: str) -> float:
    if len(df) < 2:
        return 0.0
    total = 0.0
    prev = df.iloc[0]
    for _, row in df.iloc[1:].iterrows():
        total += haversine_m(prev[lat_col], prev[lon_col], row[lat_col], row[lon_col])
        prev = row
    return total


def reproject_xy(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    src_epsg: int,
    dst_epsg: int = 4326,
) -> pd.DataFrame:
    out = df.copy()
    transformer = Transformer.from_crs(src_epsg, dst_epsg, always_xy=True)
    lon, lat = transformer.transform(out[x_col].to_numpy(), out[y_col].to_numpy())
    out["lon"] = lon
    out["lat"] = lat
    return out


def bbox(df: pd.DataFrame, lon_col: str, lat_col: str) -> dict[str, float]:
    return {
        "min_lon": float(df[lon_col].min()),
        "max_lon": float(df[lon_col].max()),
        "min_lat": float(df[lat_col].min()),
        "max_lat": float(df[lat_col].max()),
    }
