from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.io as pio

def fig_to_html_div(fig) -> str:
    """Render a Plotly fig to a standalone <div> (no full HTML)."""
    return pio.to_html(fig, include_plotlyjs="cdn", full_html=False)

def _apply_plotly_theme(fig, theme: str) -> None:
    """Apply a consistent plotly theme to the figure."""
    theme = (theme or "dark").lower()
    if theme == "dark":
        # Match base.html .theme-dark palette
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#141821",  # page background
            plot_bgcolor="#1a1f2a",   # card background
        )
        # Softer gridlines on dark
        fig.update_xaxes(gridcolor="#2a3140", zeroline=False)
        fig.update_yaxes(gridcolor="#2a3140", zeroline=False)
    else:
        fig.update_layout(
            template="plotly",
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

def numeric_histograms(df: pd.DataFrame, cols: list[str], theme: str = "dark") -> list[dict]:
    """Create histogram per numeric column. Returns list of {col, div}."""
    out = []
    for c in cols:
        s = pd.to_numeric(df[c], errors="coerce")
        fig = px.histogram(x=s, nbins=50, title=f"Distribution – {c}")
        _apply_plotly_theme(fig, theme)
        div = fig_to_html_div(fig)
        out.append({"col": c, "div": div})
    return out

def categorical_bars(df: pd.DataFrame, cols: list[str], theme: str = "dark") -> list[dict]:
    """Create bar charts for top categories. Returns list of {col, div}."""
    out = []
    for c in cols:
        vc = df[c].astype("string").value_counts(dropna=True).head(30)
        fig = px.bar(x=vc.index.to_list(), y=vc.values.tolist(), title=f"Top categories – {c}")
        fig.update_layout(xaxis_title=c, yaxis_title="count")
        _apply_plotly_theme(fig, theme)
        div = fig_to_html_div(fig)
        out.append({"col": c, "div": div})
    return out

def correlation_heatmap(
    corr_input: dict | pd.DataFrame | None,
    title: str,
    theme: str = "dark",
    colorscale: str = "RdBu_r",  # blue→white→red (seaborn 'coolwarm'-like)
) -> str | None:
    """
    Create a correlation heatmap that *only* shows numeric columns.
    Accepts:
      - a dict (e.g. DataFrame.to_dict()) or
      - a pandas DataFrame
    Returns a Plotly <div> string or None if nothing numeric remains.
    """
    if corr_input is None:
        return None

    # Normalize input to DataFrame
    if isinstance(corr_input, dict):
        df = pd.DataFrame(corr_input)
    elif isinstance(corr_input, pd.DataFrame):
        df = corr_input.copy()
    else:
        return None

    # Coerce everything to numeric (non-numeric → NaN), then keep numeric-only columns
    df = df.apply(pd.to_numeric, errors="coerce")

    # Drop columns/rows that are entirely NaN (non-numeric or empty after coercion)
    keep = df.columns[df.notna().any(axis=0)]
    df = df.loc[keep, keep]

    # Final guard: need at least 2 numeric columns to make a meaningful heatmap
    if df.shape[1] < 2:
        return None

    fig = px.imshow(
        df,
        text_auto=True,
        aspect="auto",
        title=title,
        zmin=-1,
        zmax=1,
        color_continuous_scale=colorscale,
    )
    fig.update_layout(coloraxis_colorbar_title="corr")
    _apply_plotly_theme(fig, theme)
    return fig_to_html_div(fig)
