from __future__ import annotations
import pandas as pd

def analyze_numeric(df: pd.DataFrame, roles: dict) -> dict:
    """Numeric distributions and outlier summary (IQR)."""
    out: dict[str, dict] = {}
    for col in roles.get("numeric", []):
        s = pd.to_numeric(df[col], errors="coerce")
        desc = s.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).to_dict()
        q1, q3 = desc.get("25%"), desc.get("75%")
        iqr = (q3 - q1) if q1 is not None and q3 is not None else None
        if iqr is not None:
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = int(((s < lower) | (s > upper)).sum())
        else:
            outliers = 0
        out[col] = {
            "describe": {k: (float(v) if pd.notna(v) else None) for k, v in desc.items()},
            "iqr_outliers": outliers,
            "n_missing": int(s.isna().sum()),
        }
    return out
