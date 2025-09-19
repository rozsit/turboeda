# turboeda/analyzers/datetime.py
from __future__ import annotations
from typing import Dict, Any
import pandas as pd


def _parse_datetime_series(s: pd.Series) -> pd.Series:
    """Safely coerce a series to datetime without deprecated args.
    - If it's already a datetime dtype, return as-is.
    - Else parse with pd.to_datetime(errors='coerce') (no infer_datetime_format).
    """
    if pd.api.types.is_datetime64_any_dtype(s):
        return s
    return pd.to_datetime(s, errors="coerce")


def analyze_datetime(df: pd.DataFrame, roles: Dict[str, list[str]]) -> Dict[str, Any]:
    """Analyze datetime-like columns and return basic stats for the report.

    Returns dict with:
      {
        "n_cols": int,
        "columns": [
            {
              "name": str,
              "n_nonnull": int,
              "n_null": int,
              "pct_null": float,
              "min": str|None,  # ISO8601 if available
              "max": str|None,  # ISO8601 if available
              "examples": list[str],  # first few non-null examples
            },
            ...
        ]
      }
    """
    cols = roles.get("datetime", []) or []
    out_cols: list[Dict[str, Any]] = []

    for col in cols:
        raw = df[col]
        ser = _parse_datetime_series(raw)

        n_nonnull = int(ser.notna().sum())
        n_null = int(ser.isna().sum())
        pct_null = float(ser.isna().mean() * 100.0) if len(ser) else 0.0

        if n_nonnull > 0:
            min_val = ser.min()
            max_val = ser.max()
            min_iso = min_val.isoformat() if pd.notna(min_val) else None
            max_iso = max_val.isoformat() if pd.notna(max_val) else None
            examples = [str(x) for x in ser.dropna().astype(str).head(3).tolist()]
        else:
            min_iso = None
            max_iso = None
            examples = []

        out_cols.append(
            {
                "name": col,
                "n_nonnull": n_nonnull,
                "n_null": n_null,
                "pct_null": pct_null,
                "min": min_iso,
                "max": max_iso,
                "examples": examples,
            }
        )

    return {"n_cols": len(cols), "columns": out_cols}
