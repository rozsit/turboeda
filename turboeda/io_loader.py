from __future__ import annotations
from typing import Optional
from pathlib import Path
import pandas as pd
import chardet

def _detect_encoding(file_path: str, nbytes: int = 20000) -> str:
    # Detect CSV encoding from the first n bytes
    with open(file_path, "rb") as f:
        raw = f.read(nbytes)
    enc = chardet.detect(raw).get("encoding") or "utf-8"
    return enc

def _read_excel_first_sheet(path: str) -> pd.DataFrame:
    # Open workbook once, pick the first sheet name explicitly
    xls = pd.ExcelFile(path)  # uses openpyxl for .xlsx/.xlsm
    if not xls.sheet_names:
        raise ValueError("Excel file contains no sheets.")
    first = xls.sheet_names[0]
    return pd.read_excel(xls, sheet_name=first)

def load_table(
    input_path: str,
    sep: str = ",",
    sheet: Optional[str] = None,
    sample_rows: Optional[int] = 200_000,
) -> pd.DataFrame:
    """
    Load CSV or Excel into a DataFrame with optional sampling and basic dtype optimization.

    Behavior:
    - CSV/TXT: encoding auto-detected.
    - XLSX/XLSM: if `sheet` is None -> uses the FIRST worksheet by default.
    - XLS: tries engine='xlrd' (requires xlrd<2.0); if unavailable, raises a clear error.
    """
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    suffix = p.suffix.lower()

    if suffix in (".csv", ".txt"):
        enc = _detect_encoding(input_path)
        df = pd.read_csv(input_path, sep=sep, encoding=enc, low_memory=False)

    elif suffix in (".xlsx", ".xlsm"):
        if sheet is None:
            df = _read_excel_first_sheet(input_path)
        else:
            df = pd.read_excel(input_path, sheet_name=sheet)

    elif suffix == ".xls":
        # Legacy Excel format; needs xlrd<2.0
        try:
            # If sheet is None, pass 0 to mean "first sheet"
            sheet_arg = 0 if sheet is None else sheet
            df = pd.read_excel(input_path, sheet_name=sheet_arg, engine="xlrd")
        except ImportError as e:
            raise ImportError(
                "Reading .xls requires 'xlrd<2.0'. Install via: pip install 'xlrd<2.0'"
            ) from e

    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    # Optional sample for speed
    if sample_rows is not None and len(df) > sample_rows:
        df = df.sample(n=sample_rows, random_state=42).reset_index(drop=True)

    # Basic dtype optimization: downcast numerics
    for col in df.select_dtypes(include=["int", "int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["float", "float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")

    return df
