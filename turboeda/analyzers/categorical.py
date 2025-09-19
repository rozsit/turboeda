from __future__ import annotations
import pandas as pd

def analyze_categorical(df: pd.DataFrame, roles: dict) -> dict:
    """Top categories and rarity flags."""
    out: dict[str, dict] = {}
    for col in roles.get("categorical", []):
        s = df[col].astype("string")
        vc = s.value_counts(dropna=True)
        top = vc.head(20)
        rarity_threshold = max(2, int(0.01 * len(s)))  # 1% or at least 2 rows
        rare_count = int((vc < rarity_threshold).sum())
        out[col] = {
            "top_values": {str(k): int(v) for k, v in top.items()},
            "n_unique": int(vc.shape[0]),
            "rare_below_threshold": rare_count,
            "n_missing": int(s.isna().sum()),
        }
    return out
