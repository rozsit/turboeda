
# turboeda

**turboeda** is a one-command Exploratory Data Analysis (EDA) report generator.  
Give it a CSV or XLSX file — it automatically analyzes the data and creates a polished, interactive HTML report with Plotly charts.

---

## 📦 Installation

### From PyPI
```bash
pip install turboeda
```

### From local source (development mode)
```bash
# in the project root folder (where pyproject.toml is)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -e .
```

> CSV files are read with pandas' default engine. Excel is handled by `openpyxl`.  
> CSV encoding is auto-detected via `chardet` (installed as a dependency).

---

## 🚀 Usage (CLI)

**Short form (recommended):**
```bash
turboeda "data.csv" -o "report.html" --open
# Excel (auto-uses the FIRST sheet if --sheet is omitted):
turboeda "data.xlsx" --sheet "Sheet1" -o "report.html" --open
```

**Long form (also supported, legacy-friendly):**
```bash
turboeda report "data.csv" -o "report.html" --open
turboeda report "data.xlsx" --sheet "Sheet1" -o "report.html" --open
```

**Default naming rule:**  
If `-o/--out` is not provided, the HTML is saved as **`<input_basename>_report.html`** in the **same folder** as the input file.  
Examples:
- `C:\data\Iris.csv` → `C:\data\Iris_report.html`
- `/Users/me/data/sales.xlsx` → `/Users/me/data/sales_report.html`

**Common options:**
- `--sheet "Sheet1"`: select Excel sheet if using `.xlsx` (if omitted, **first** sheet is used)
- `--sep ";"` : custom CSV delimiter
- `--sample-rows 100000` : sample large files for faster analysis (**default: 200000**)
- `--max-corr-cols 40` : cap number of columns in correlation matrices
- `--max-numeric-plots 12` / `--max-categorical-plots 12` : limit per-variable charts
- `--theme dark|light` : choose dark or light theme (**default: dark**)
- `--open` : open the generated HTML in your default browser

---

## 📓 Usage in Jupyter Notebook / Python scripts

```python
from turboeda import EDAReport
from pathlib import Path

# Create and run analysis
report = EDAReport(
    input_path="data.csv",
    theme="dark",           # or "light"
    sample_rows=None,       # use all rows; or set an int to sample large datasets
    max_corr_cols=40,
    max_numeric_plots=12,
    max_categorical_plots=12,
    # Optional UX:
    auto_save_and_open=False,  # if True, saves & opens after run()
    out_path=None,             # custom output name; otherwise uses <input>_report.html
    open_target="tab",         # "tab" or "window" for auto-open
)

results = report.run()

# Export to HTML (default name rule: <input_basename>_report.html)
inp = Path("data.csv")
out = inp.with_name(f"{inp.stem}_report.html")
report.to_html(out.as_posix(), open_in_browser=True)  # set open_in_browser=False if you don't want auto-open
```

**Inline preview in notebook:**
```python
from IPython.display import IFrame
IFrame("data_report.html", width="100%", height=800)
```

---

## 🎨 Theme

The report supports **dark** and **light** themes.  
Charts adopt the chosen theme as well (Plotly `plotly_dark` vs `plotly`).

- Dark (default):
  ```bash
  turboeda "data.csv" --theme dark
  ```
- Light:
  ```bash
  turboeda "data.csv" --theme light
  ```

---

## 🧠 Notes & Tips

- CSV encoding is auto-detected with `chardet`; Excel uses the selected sheet (or **first** if omitted).
- For very large files, consider `--sample-rows` to speed up initial EDA.
- Datetime detection is heuristic-based and avoids deprecated parsing flags; specify formats upstream if needed.
- On Windows PowerShell, if script activation is blocked, run:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```

---

## ⚡ Requirements

- Python 3.9+
- Packages: `pandas`, `numpy`, `plotly`, `jinja2`, `typer`, `chardet`, `openpyxl`  
  (installed automatically when you `pip install -e .`)

---

## 📄 License

MIT License — see [LICENSE](LICENSE).
