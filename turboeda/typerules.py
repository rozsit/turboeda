from __future__ import annotations
import re
from typing import Iterable, Tuple
import pandas as pd

# Common datetime formats to try quickly
_COMMON_DT_FORMATS: tuple[str, ...] = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y.%m.%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%Y.%m.%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%d/%m/%Y",
    "%d/%m/%Y %H:%M:%S",
    "%d.%m.%Y",
    "%d.%m.%Y %H:%M:%S",
    "%m/%d/%Y",
    "%m/%d/%Y %H:%M:%S",
)

# Lightweight hint that a string looks like a date/datetime
# - YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
# - DD/MM/YYYY, DD.MM.YYYY, MM/DD/YYYY
# - ISO-like timestamps with 'T' and time
_DATE_HINT_RE = re.compile(
    r"""(?xi)
    (?:\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b)      # 2024-09-14, 2024/09/14, 2024.09.14
    |
    (?:\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b)    # 14/09/2024, 09/14/2024, 14.09.2024
    |
    (?:\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})  # 2024-09-14T12:34:56 (optionally with ms/zone)
    """,
)

def _best_datetime_format(sample: pd.Series, formats: Iterable[str]) -> Tuple[str | None, float]:
    """Try a set of datetime formats and return (best_format, success_ratio)."""
    if sample.empty:
        return None, 0.0
    best_fmt: str | None = None
    best_ratio: float = 0.0
    s = sample.astype(str)

    for fmt in formats:
        parsed = pd.to_datetime(s, format=fmt, errors="coerce")
        ratio = float(parsed.notna().mean()) if len(parsed) else 0.0
        if ratio > best_ratio:
            best_ratio = ratio
            best_fmt = fmt

    return best_fmt, best_ratio

def _date_hint_ratio(sample: pd.Series) -> float:
    """Share of values that look date-like according to a simple regex."""
    if sample.empty:
        return 0.0
    s = sample.astype(str)
    hits = s.str.contains(_DATE_HINT_RE, na=False)
    return float(hits.mean())

def _looks_like_datetime(sample: pd.Series, threshold: float = 0.8) -> bool:
    """Heuristic: detect if a string-like column is datetime-like.

    1) Try common explicit formats (fast, no warnings).
    2) If none reach threshold, only then consider a general parse
       IF enough values look like dates by regex hint.
    """
    if sample.empty:
        return False

    # 1) Fast formatted attempts
    fmt, ratio = _best_datetime_format(sample, _COMMON_DT_FORMATS)
    if ratio >= threshold:
        return True

    # 2) Skip noisy general parsing if almost nothing looks like date
    hint_ratio = _date_hint_ratio(sample)
    if hint_ratio < 0.2:  # if <20% look date-like, we assume NOT datetime
        return False

    # 3) Final broad attempt WITHOUT infer_datetime_format (deprecated)
    #    Suppress only the specific "Could not infer format..." warning.
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Could not infer format, so each element will be parsed individually",
            category=UserWarning,
        )
        parsed_general = pd.to_datetime(sample.astype(str), errors="coerce")
    ratio_general = float(parsed_general.notna().mean()) if len(parsed_general) else 0.0
    return ratio_general >= threshold

def infer_types(df: pd.DataFrame) -> dict:
    """Infer logical roles for variables: numeric, categorical, datetime, text."""
    roles: dict[str, list[str]] = {"numeric": [], "categorical": [], "datetime": [], "text": []}
    n = len(df)

    for col in df.columns:
        s = df[col]

        # Numeric early exit
        if pd.api.types.is_numeric_dtype(s):
            roles["numeric"].append(col)
            continue

        # Already datetime dtype
        if pd.api.types.is_datetime64_any_dtype(s):
            roles["datetime"].append(col)
            continue

        # Object/string-like → decide among datetime/categorical/text
        if s.dtype == "O" or pd.api.types.is_string_dtype(s):
            sample = s.dropna().head(500)
            if not sample.empty and _looks_like_datetime(sample):
                roles["datetime"].append(col)
                continue

            nunique = s.nunique(dropna=True)
            if nunique <= min(100, max(10, int(0.2 * n))):
                roles["categorical"].append(col)
            else:
                roles["text"].append(col)
            continue

        # Fallback
        roles["text"].append(col)

    return roles
