from __future__ import annotations
import pandas as pd

def analyze_correlations(df: pd.DataFrame, roles: dict, max_cols: int = 40) -> dict:
    """Pearson and Spearman correlations for numeric columns (capped to max_cols)."""
    numeric_cols = roles.get("numeric", [])[:max_cols]
    if len(numeric_cols) < 2:
        return {"pearson": None, "spearman": None, "columns": numeric_cols}
    sub = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    pearson = sub.corr(method="pearson")
    spearman = sub.corr(method="spearman")
    return {
        "pearson": pearson.round(3).to_dict(),
        "spearman": spearman.round(3).to_dict(),
        "columns": numeric_cols,
    }
