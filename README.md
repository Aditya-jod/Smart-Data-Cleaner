# 🧹 Smart Data Cleaner

**Interactive Streamlit app to analyze, clean, and visualize CSV datasets.**

---

## Project Overview

Automates common data cleaning tasks so you can focus on analysis and modeling. Upload a CSV and:
- Generate a data quality summary.
- Detect and handle missing values, duplicates, and outliers.
- Visualize distributions, boxplots, countplots, and missing-value summaries.
- Download the cleaned CSV.

## What's new in this version

- Robust input validation and defensive error handling across the codebase.
- Centralized logging for easier debugging.
- DataCleaner improvements:
  - Safe missing-value strategies: drop / mean / median / mode.
  - Outlier handling (IQR) with safe clipping for integer-like dtypes.
  - Type conversion using pandas' convert_dtypes and safer numeric conversion.
  - get_summary returns captured info, description, missing counts, duplicate count.
- Visualizer improvements:
  - Functions return Optional[matplotlib.figure.Figure].
  - Input validation and safe styling; errors are logged and handled.
  - Consistent dark theme and centralized color constants.
- App improvements:
  - Defensive Streamlit UI (explicit None checks for DataFrames).
  - Safe CSV download, spinners, and better error messages.
  - Replaced deprecated Streamlit param use_container_width -> width='stretch'.
- Dev tooling (recommended and scaffolded):
  - requirements-dev.txt (pytest, flake8, black, isort, pre-commit, mypy).
  - CI workflow (GitHub Actions) to run tests and lint.
  - Pre-commit hooks (black/isort/flake8) recommended.

## Folder structure

```
smart_data_cleaner/
├── .streamlit/
├── app.py
├── utils/
│   ├── data_cleaner.py
│   └── visualizer.py
├── requirements.txt
├── requirements-dev.txt   # dev/test tools (recommended)
├── tests/                 # suggested: pytest tests
└── README.md
```

## Install & run (local)

1. Create and activate venv (Windows)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install runtime dependencies
```powershell
pip install -r requirements.txt
```

3. (Optional) Install dev deps for tests & linting
```powershell
pip install -r requirements-dev.txt
```

4. Run the app
```powershell
streamlit run app.py
```
Open: http://localhost:8501

## Tests & CI

- Run tests locally:
```powershell
pytest -q
```

- CI (GitHub Actions): add `.github/workflows/ci.yml` to run pytest and flake8 on push / PR.

## Code style & pre-commit

Recommended pre-commit config (black, isort, flake8). Install locally:
```powershell
pre-commit install
pre-commit run --all-files
```

## Notes & caveats

- DataFrame truth checks were replaced with explicit None/empty checks to avoid pandas' ambiguous truth-value errors.
- Outlier capping uses integer-safe bounds for pandas nullable integer dtypes (Int64). If you prefer fractional caps, convert the column to float before capping (can be added).
- Some pandas styling operations can produce warnings when columns are constant or NaN-only; the app now falls back to plain rendering when styling fails.
- If you encounter warnings about future pandas behavior (e.g., pd.to_numeric errors parameter), update utils/data_cleaner.convert_data_types accordingly.

## Contributing

- Open an issue or PR.
- Run tests and linters locally before opening a PR.
- Follow the code style (black/isort/flake8).

## License

MIT
