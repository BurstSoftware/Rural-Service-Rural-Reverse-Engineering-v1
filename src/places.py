from __future__ import annotations

import pandas as pd

PLACE_FIELDS = ("state", "county", "city", "zip_code", "road", "address")


def combined_frame(assets: list) -> pd.DataFrame:
    frames = []
    for asset in assets:
        if asset.frame is None or asset.frame.empty:
            continue
        part = asset.frame.copy()
        part["_source"] = asset.name
        frames.append(part)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def unique_sorted(series: pd.Series) -> list[str]:
    values = (
        series.dropna()
        .astype(str)
        .str.strip()
        .replace({"": pd.NA, "<NA>": pd.NA, "nan": pd.NA})
        .dropna()
        .unique()
        .tolist()
    )
    return sorted(values, key=str.lower)


def apply_place_filters(
    df: pd.DataFrame,
    state: str | None = None,
    county: str | None = None,
    city: str | None = None,
    zip_code: str | None = None,
    road: str | None = None,
    address: str | None = None,
) -> pd.DataFrame:
    out = df.copy()
    mapping = {
        "state": state,
        "county": county,
        "city": city,
        "zip_code": zip_code,
        "road": road,
        "address": address,
    }
    for col, value in mapping.items():
        if value and value != "All" and col in out.columns:
            out = out[out[col].astype(str) == value]
    return out
