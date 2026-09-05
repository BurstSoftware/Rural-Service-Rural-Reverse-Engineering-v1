from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


SUPPORTED = {
    "csv": "tabular survey",
    "geojson": "vector features",
    "json": "geojson or records",
    "ply": "point cloud (preview later)",
    "pcd": "point cloud (preview later)",
    "las": "LiDAR (preview later)",
    "laz": "LiDAR (preview later)",
    "tif": "raster DTM (preview later)",
    "tiff": "raster DTM (preview later)",
}


@dataclass
class LoadedAsset:
    name: str
    kind: str
    frame: pd.DataFrame | None
    meta: dict[str, Any]


def suffix(name: str) -> str:
    return Path(name).suffix.lower().lstrip(".")


def load_uploaded(name: str, raw: bytes) -> LoadedAsset:
    ext = suffix(name)
    kind = SUPPORTED.get(ext, "unknown")

    if ext == "csv":
        from io import BytesIO

        df = pd.read_csv(BytesIO(raw))
        return LoadedAsset(name, kind, df, {"rows": len(df), "cols": list(df.columns)})

    if ext in {"geojson", "json"}:
        import json
        from io import BytesIO

        payload = json.loads(raw.decode("utf-8"))
        features = payload.get("features", [])
        rows = []
        for feat in features:
            props = feat.get("properties") or {}
            geom = feat.get("geometry") or {}
            coords = geom.get("coordinates")
            row = dict(props)
            row["_geom_type"] = geom.get("type")
            if geom.get("type") == "Point" and isinstance(coords, list) and len(coords) >= 2:
                row["lon"], row["lat"] = coords[0], coords[1]
                if len(coords) > 2:
                    row["z"] = coords[2]
            rows.append(row)
        df = pd.DataFrame(rows) if rows else pd.DataFrame()
        return LoadedAsset(name, kind, df, {"feature_count": len(features)})

    return LoadedAsset(
        name,
        kind,
        None,
        {"bytes": len(raw), "note": "Stored; specialized parser not wired yet."},
    )


def guess_xy_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    lower = {c.lower(): c for c in df.columns}
    for lon_key, lat_key in (
        ("lon", "lat"),
        ("longitude", "latitude"),
        ("x", "y"),
        ("easting", "northing"),
    ):
        if lon_key in lower and lat_key in lower:
            return lower[lon_key], lower[lat_key]
    return None, None
