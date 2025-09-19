from __future__ import annotations
import pandas as pd

def analyze_summary(df: pd.DataFrame) -> dict:
    """Basic dataset-level metrics."""
    n_rows, n_cols = df.shape
    missing_by_col = df.isna().sum().to_dict()
    missing_ratio_by_col = {k: float(v) / n_rows for k, v in missing_by_col.items()} if n_rows else {k: 0.0 for k in df.columns}
    dtypes = df.dtypes.astype(str).to_dict()
    mem_mb = float(df.memory_usage(deep=True).sum()) / (1024 ** 2)

    dup_rows = int(df.duplicated().sum())

    return {
        "n_rows": int(n_rows),
        "n_cols": int(n_cols),
        "memory_mb": round(mem_mb, 3),
        "dtypes": dtypes,
        "missing_count": missing_by_col,
        "missing_ratio": {k: round(v, 4) for k, v in missing_ratio_by_col.items()},
        "duplicate_rows": dup_rows,
    }
