from __future__ import annotations

import json
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

SUPPORTED = ("csv", "json", "geojson")

COLUMN_ALIASES = {
    "state": ["state", "st", "province", "region", "admin1"],
    "county": ["county", "parish", "borough", "admin2"],
    "city": ["city", "town", "village", "municipality", "place"],
    "address": ["address", "addr", "street_address", "full_address", "site_address"],
    "road": ["road", "street", "road_name", "street_name", "highway", "route"],
    "zip_code": ["zip_code", "zip", "postal", "postal_code", "postcode"],
    "lon": ["lon", "lng", "long", "longitude", "x"],
    "lat": ["lat", "latitude", "y"],
    "z": ["z", "elev", "elevation", "height", "alt"],
}


@dataclass
class LoadedAsset:
    name: str
    kind: str
    frame: pd.DataFrame | None
    meta: dict[str, Any] = field(default_factory=dict)


def suffix(name: str) -> str:
    return Path(name).suffix.lower().lstrip(".")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        for key in ("state", "county", "city", "address", "road", "zip_code", "lon", "lat", "z"):
            if key not in df.columns:
                df[key] = pd.NA
        return df

    lower_map = {c.lower().strip(): c for c in df.columns}
    out = df.copy()
    for canonical, aliases in COLUMN_ALIASES.items():
        if canonical in out.columns:
            continue
        for alias in aliases:
            if alias in lower_map:
                out[canonical] = out[lower_map[alias]]
                break
        else:
            out[canonical] = pd.NA

    out["lon"] = pd.to_numeric(out["lon"], errors="coerce")
    out["lat"] = pd.to_numeric(out["lat"], errors="coerce")
    out["z"] = pd.to_numeric(out["z"], errors="coerce")
    for text_col in ("state", "county", "city", "address", "road", "zip_code"):
        out[text_col] = out[text_col].astype("string").str.strip()
    return out


def _point_row(props: dict[str, Any], coords: list | None) -> dict[str, Any]:
    row = dict(props or {})
    if coords and len(coords) >= 2:
        row.setdefault("lon", coords[0])
        row.setdefault("lat", coords[1])
        if len(coords) > 2:
            row.setdefault("z", coords[2])
    return row


def _features_to_frame(payload: dict[str, Any]) -> pd.DataFrame:
    features = payload.get("features", [])
    rows: list[dict[str, Any]] = []
    for feat in features:
        props = feat.get("properties") or {}
        geom = feat.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates")
        if gtype == "Point":
            rows.append(_point_row(props, coords))
        elif gtype == "MultiPoint":
            for pt in coords or []:
                rows.append(_point_row(props, pt))
        elif gtype == "LineString":
            for i, pt in enumerate(coords or []):
                row = _point_row(props, pt)
                row["_vertex"] = i
                row["_geom_type"] = "LineString"
                rows.append(row)
        elif gtype == "MultiLineString":
            for line in coords or []:
                for i, pt in enumerate(line or []):
                    row = _point_row(props, pt)
                    row["_vertex"] = i
                    row["_geom_type"] = "MultiLineString"
                    rows.append(row)
        elif gtype in {"Polygon", "MultiPolygon"}:
            row = dict(props)
            ring = coords[0] if gtype == "Polygon" and coords else None
            if gtype == "MultiPolygon" and coords:
                ring = coords[0][0] if coords[0] else None
            if ring:
                xs = [p[0] for p in ring]
                ys = [p[1] for p in ring]
                row.setdefault("lon", sum(xs) / len(xs))
                row.setdefault("lat", sum(ys) / len(ys))
            row["_geom_type"] = gtype
            rows.append(row)
        else:
            row = dict(props)
            row["_geom_type"] = gtype
            rows.append(row)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def load_uploaded(name: str, raw: bytes) -> LoadedAsset:
    ext = suffix(name)
    if ext not in SUPPORTED:
        return LoadedAsset(name, "unsupported", None, {"error": f"Use csv, json, or geojson. Got .{ext}"})

    if ext == "csv":
        df = pd.read_csv(BytesIO(raw))
        df = _normalize_columns(df)
        return LoadedAsset(name, "csv", df, {"rows": len(df), "cols": list(df.columns)})

    payload = json.loads(raw.decode("utf-8"))
    if isinstance(payload, list):
        df = _normalize_columns(pd.DataFrame(payload))
        return LoadedAsset(name, "json", df, {"rows": len(df), "record_list": True})

    if isinstance(payload, dict) and payload.get("type") == "FeatureCollection":
        df = _normalize_columns(_features_to_frame(payload))
        return LoadedAsset(
            name,
            "geojson",
            df,
            {"rows": len(df), "feature_count": len(payload.get("features", []))},
        )

    if isinstance(payload, dict) and payload.get("type") == "Feature":
        df = _normalize_columns(_features_to_frame({"features": [payload]}))
        return LoadedAsset(name, "geojson", df, {"rows": len(df), "single_feature": True})

    if isinstance(payload, dict):
        records = payload.get("records") or payload.get("data") or payload.get("items")
        if isinstance(records, list):
            df = _normalize_columns(pd.DataFrame(records))
            return LoadedAsset(name, "json", df, {"rows": len(df)})
        df = _normalize_columns(pd.DataFrame([payload]))
        return LoadedAsset(name, "json", df, {"rows": 1, "object": True})

    return LoadedAsset(name, "json", None, {"error": "Unrecognized JSON structure"})
