from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from ..viz.plots import (
    numeric_histograms,
    categorical_bars,
    correlation_heatmap,
)

@dataclass
class HTMLRenderer:
    """Render the EDA result dictionary to a single HTML string using Jinja2 templates."""

    def _get_template_dir(self) -> Path:
        pkg_root = Path(__file__).parent
        return pkg_root / "templates"

    def render(
        self,
        result: Dict[str, Any],
        df,
        max_numeric_plots: int = 12,
        max_categorical_plots: int = 12,
        theme: str = "dark",
    ) -> str:
        tdir = self._get_template_dir()
        env = Environment(
            loader=FileSystemLoader(str(tdir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        base = env.get_template("base.html")
        summary_t = env.get_template("sections/summary.html")
        vars_t = env.get_template("sections/variables.html")
        corr_t = env.get_template("sections/correlations.html")

        roles = result["roles"]

        # Generate figures (capped by limits)
        numeric_cols = roles.get("numeric", [])[:max_numeric_plots]
        categorical_cols = roles.get("categorical", [])[:max_categorical_plots]

        numeric_figs = numeric_histograms(df, numeric_cols, theme=theme) if numeric_cols else []
        categorical_figs = categorical_bars(df, categorical_cols, theme=theme) if categorical_cols else []

        # Correlation figures
        pearson_div = correlation_heatmap(result["correlations"]["pearson"], "Pearson correlation", theme=theme)
        spearman_div = correlation_heatmap(result["correlations"]["spearman"], "Spearman correlation", theme=theme)

        html = base.render(
            theme=theme,
            summary_section=summary_t.render(summary=result["summary"], roles=roles),
            variables_section=vars_t.render(
                numeric=result["numeric"],
                categorical=result["categorical"],
                dt=result["datetime"],
                numeric_figs=numeric_figs,
                categorical_figs=categorical_figs,
            ),
            correlations_section=corr_t.render(
                pearson_div=pearson_div,
                spearman_div=spearman_div,
                cols=result["correlations"]["columns"],
            ),
        )
        return html
