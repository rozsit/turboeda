from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
from pathlib import Path
import webbrowser

from .io_loader import load_table
from .typerules import infer_types
from .analyzers.summary import analyze_summary
from .analyzers.numeric import analyze_numeric
from .analyzers.categorical import analyze_categorical
from .analyzers.datetime import analyze_datetime
from .analyzers.correlation import analyze_correlations
from .report.renderer import HTMLRenderer


@dataclass
class EDAReport:
    """Core facade to run the EDA pipeline and export an HTML report."""

    input_path: str
    sep: str = ","
    sheet: str | None = None
    sample_rows: int | None = 200_000

    # Correlation config
    max_corr_cols: int = 40

    # Plot quotas
    max_numeric_plots: int = 12
    max_categorical_plots: int = 12

    # Theming
    theme: str = "dark"  # 'dark' or 'light'

    # Auto open options (useful in Jupyter)
    auto_save_and_open: bool = False          # if True: run() will save HTML and open browser automatically
    out_path: str | None = None               # optional custom output path; if None -> <input>_report.html
    open_target: str = "tab"                  # 'tab' or 'window'

    profile: str = "standard"

    def run(self) -> Dict[str, Any]:
        df = load_table(self.input_path, sep=self.sep, sheet=self.sheet, sample_rows=self.sample_rows)
        roles = infer_types(df)
        summary = analyze_summary(df)
        numeric = analyze_numeric(df, roles)
        categorical = analyze_categorical(df, roles)
        dt = analyze_datetime(df, roles)
        corrs = analyze_correlations(df, roles, max_cols=self.max_corr_cols)

        self._df = df
        self._result = {
            "summary": summary,
            "roles": roles,
            "numeric": numeric,
            "categorical": categorical,
            "datetime": dt,
            "correlations": corrs,
        }

        # Optional: immediately save and open the report after analysis finishes
        if self.auto_save_and_open:
            default_out = Path(self.input_path).with_name(f"{Path(self.input_path).stem}_report.html")
            out_path = Path(self.out_path) if self.out_path else default_out
            # to_html also supports opening, but we call it with open flag to ensure timing
            self.to_html(out_path.as_posix(), open_in_browser=True, open_target=self.open_target)

        return self._result

    def to_html(self, out_path: str, open_in_browser: bool = False, open_target: str = "tab") -> None:
        """Write the HTML report. Optionally open in the user's default browser."""
        if not hasattr(self, "_result") or not hasattr(self, "_df"):
            raise RuntimeError("Call run() before to_html().")

        renderer = HTMLRenderer()
        html = renderer.render(
            result=self._result,
            df=self._df,
            max_numeric_plots=self.max_numeric_plots,
            max_categorical_plots=self.max_categorical_plots,
            theme=self.theme,
        )
        p = Path(out_path)
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)

        if open_in_browser:
            try:
                url = p.resolve().as_uri()
                if (open_target or "tab").lower() == "tab":
                    webbrowser.open_new_tab(url)
                else:
                    webbrowser.open_new(url)
                print(f"[turboeda] Opening report in default browser: {url}")
            except Exception as e:
                # Do not fail the export if browser opening is not available (e.g., headless env)
                print(f"[turboeda] Could not open browser automatically: {e}")
