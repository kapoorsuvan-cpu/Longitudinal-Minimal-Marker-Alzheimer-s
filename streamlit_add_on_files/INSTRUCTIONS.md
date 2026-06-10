# Streamlit add-on files

Add these files to the root of your existing GitHub repo.

Your current repo already has:

- `csvs/`
- `README.md`
- `longitudinal_minimal_marker_pipeline.ipynb`
- `Parse_R_Files_Longitudinal_Minimal_Markers.R`

This ZIP only adds what you need for the Streamlit app:

- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

The app uses embedded summary results from your notebook, so it will render even without reading the raw ADNI CSVs.

If you later want the app to read directly from output CSVs, replace the hardcoded dataframes in `load_results()` with `pd.read_csv(...)`.
