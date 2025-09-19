import typer
from pathlib import Path
from typing import Optional
from .eda_report import EDAReport

app = typer.Typer(help="Generate EDA HTML reports from CSV/XLSX files.")

@app.command()
def report(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="Path to CSV/XLSX file."),
    out: Optional[Path] = typer.Option(
        None,
        "--out",
        "-o",
        help="Output HTML report path. Default: <input_basename>_report.html next to the input file.",
    ),
    sep: str = typer.Option(",", help="CSV delimiter (if CSV)."),
    sheet: str | None = typer.Option(
        None,
        help="Excel sheet name. If not provided for XLSX/XLSM/XLS, the FIRST sheet is used by default.",
    ),
    sample_rows: int | None = typer.Option(200_000, help="Sample size for large files (None for full)."),
    max_corr_cols: int = typer.Option(40, help="Max number of columns to include in correlation matrix."),
    max_numeric_plots: int = typer.Option(12, help="Max numeric columns to plot histograms for."),
    max_categorical_plots: int = typer.Option(12, help="Max categorical columns to plot bar charts for."),
    theme: str = typer.Option("dark", "--theme", help="Report theme: 'dark' or 'light'.", show_default=True),
    open_browser: bool = typer.Option(False, "--open/--no-open", help="Open the report in the default browser after writing."),
    profile: str = typer.Option("standard", help="Profile: quick|standard|deep (affects analyses)."),
):
    """Read INPUT_PATH and write an interactive HTML EDA report."""
    theme = theme.lower().strip()
    if theme not in {"dark", "light"}:
        raise typer.BadParameter("theme must be 'dark' or 'light'")

    typer.echo("[turboeda] Loading data…")
    eda = EDAReport(
        input_path=str(input_path),
        sep=sep,
        sheet=sheet,
        sample_rows=sample_rows,
        max_corr_cols=max_corr_cols,
        max_numeric_plots=max_numeric_plots,
        max_categorical_plots=max_categorical_plots,
        theme=theme,
    )

    res = eda.run()
    typer.echo(f"[turboeda] Analysis done. Rows={res['summary']['n_rows']}, Cols={res['summary']['n_cols']}")

    # Default output: <input_basename>_report.html next to input
    if out is None:
        out = input_path.with_name(f"{input_path.stem}_report.html")

    eda.to_html(str(out), open_in_browser=open_browser, open_target="tab")
    typer.echo(f"[turboeda] HTML written to: {out}")
    if open_browser:
        typer.echo("[turboeda] Opening default browser…")

if __name__ == "__main__":
    app()
