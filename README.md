# TRG Week 48

## $QCOM (Qualcomm Incorporated Exchange)

- A NASDAQ-listed semiconductor and telecommunications company based in San Diego, California (founded 1985). It designs Snapdragon SoCs, cellular modems, RF components and licenses wireless technologies (3G/4G/5G), serving mobile, automotive, IoT and infrastructure markets.

- https://www.kaggle.com/borismarjanovic/datasets

### 1st Commit

- Added a short Qualcomm (QCOM) summary to the README (ticker, HQ, core business and markets).
- Added a small Flask API script at `app/data.py` that loads `qcom.us.txt` into a pandas DataFrame and serves it as an HTML table (`/`), a full view (`/full`) and a JSON endpoint (`/api`).
- Included usage notes and a quick syntax check; dependencies: `flask`, `pandas`.

### 2nd Commit

- Kept the Flask code unchanged but preprocessed the loaded CSV `qcom.us.txt`:
	- Dropped the `OpenInt` column (it contains only zeros for this dataset and isn't needed for typical OHLC/volume analysis).
	- Split the full data into three DataFrames by date to simplify period-based analysis and reduce per-table size when exploring historical changes:
		- `df_1991_1999`: 1991-12-16 through 1999-12-31 — captures the early company and pre-dot-com/expansion period.
		- `df_2000_2009`: 2000-01-01 through 2009-12-31 — covers the dot-com aftermath and the 2008 financial crisis era (useful for stress/regime analysis).
		- `df_2010_2017`: 2010-01-01 through 2017-11-10 — covers the smartphone/5G ramp-up and more recent structural changes in Qualcomm's business.
	- Each smaller DataFrame is easier to render (avoid huge HTML tables), quicker to compute summaries on, and makes it straightforward to compare pre/post major market/regime events.

	Reasoning: splitting by intuitive market/regime boundaries (late-90s, 2000s, 2010s) helps when doing exploratory analysis, plotting, or training models that should be aware of structural breaks (e.g., dot-com era vs post-2008 vs smartphone era). Dropping `OpenInt` removes an unused column and reduces memory/visual clutter.

### 3rd Commit

### 4th Commit

### 5th Commit