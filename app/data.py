import os
from flask import Flask, request, Response, render_template_string
import pandas as pd

# plotting imports
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(BASE_DIR, "qcom.us.txt")


def load_data(path=DATA_FILE):
		"""Load the CSV into a pandas DataFrame. Returns None on error."""
		if not os.path.exists(path):
				return None
		try:
				df = pd.read_csv(path, parse_dates=["Date"])
				# Optional: sort by date ascending
				if "Date" in df.columns:
						df = df.sort_values("Date", ascending=False).reset_index(drop=True)
				return df
		except Exception:
				return None


# Load once at import (fast for this dataset). If the file changes often, replace with lazy loading.
DF = load_data()

# Preprocess: drop unused column and split into three period-based DataFrames
df_1991_1999 = None
df_2000_2009 = None
df_2010_2017 = None
if DF is not None:
	# Drop OpenInt if present (dataset contains zeros/unneeded column)
	if "OpenInt" in DF.columns:
		DF = DF.drop(columns=["OpenInt"])

	# Ensure Date is datetime
	if "Date" in DF.columns:
		DF["Date"] = pd.to_datetime(DF["Date"]) 

		# Define ranges (inclusive)
		df_1991_1999 = DF[(DF["Date"] >= "1991-12-16") & (DF["Date"] <= "1999-12-31")].copy().reset_index(drop=True)
		df_2000_2009 = DF[(DF["Date"] >= "2000-01-01") & (DF["Date"] <= "2009-12-31")].copy().reset_index(drop=True)
		df_2010_2017 = DF[(DF["Date"] >= "2010-01-01") & (DF["Date"] <= "2017-11-10")].copy().reset_index(drop=True)

	# Keep DF as the full, cleaned DataFrame for existing endpoints
	DF = DF.reset_index(drop=True)

app = Flask(__name__)


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>QCOM data</title>
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
	</head>
	<body class="p-4">
		<div class="container">
			<h1>QCOM Data (showing top {{ rows }})</h1>
			<div class="mb-2">
				<form method="get" class="row g-2">
					<div class="col-auto">
						<label class="visually-hidden" for="rows">Rows</label>
						<input id="rows" name="rows" type="number" min="1" value="{{ rows }}" class="form-control" />
					</div>
					<div class="col-auto">
						<button class="btn btn-primary">Refresh</button>
					</div>
				</form>
			</div>
			<div class="table-responsive">{{ table|safe }}</div>
		</div>
	</body>
</html>
"""


@app.route("/")
def index():
		if DF is None:
				return Response("Data file not found or failed to load. Expected: {}".format(DATA_FILE), status=500)

		# rows query parameter
		try:
				rows = int(request.args.get("rows", 50))
		except Exception:
				rows = 50

		table = DF.head(rows).to_html(classes="table table-striped table-sm", index=False, border=0)
		return render_template_string(HTML_TEMPLATE, table=table, rows=rows)


@app.route("/full")
def full_table():
		if DF is None:
				return Response("Data file not found or failed to load.", status=500)
		table = DF.to_html(classes="table table-striped table-sm", index=False, border=0)
		return render_template_string(HTML_TEMPLATE, table=table, rows=len(DF))


@app.route("/api")
def api():
		if DF is None:
				return Response("Data file not found or failed to load.", status=500)
		try:
				rows = int(request.args.get("rows", 50))
		except Exception:
				rows = 50
		return DF.head(rows).to_json(orient="records", date_format="iso")


@app.route("/viz/monthly-volume")
def viz_monthly_volume():
	"""Generate a PNG plot of average monthly Volume for each of the three period DataFrames.
	Returns an HTML page with the embedded image.
	"""
	if DF is None:
		return Response("Data file not found or failed to load.", status=500)

	series_list = []
	labels = []
	# helper to compute monthly mean
	def monthly_mean(df):
		if df is None or df.empty:
			return None
		s = df.set_index("Date")["Volume"].resample('M').mean()
		return s

	s1 = monthly_mean(df_1991_1999)
	s2 = monthly_mean(df_2000_2009)
	s3 = monthly_mean(df_2010_2017)

	if s1 is not None:
		series_list.append(s1)
		labels.append('1991-1999')
	if s2 is not None:
		series_list.append(s2)
		labels.append('2000-2009')
	if s3 is not None:
		series_list.append(s3)
		labels.append('2010-2017')

	if not series_list:
		return Response("No period data available to plot.", status=500)

	# create figure
	fig, ax = plt.subplots(figsize=(10, 4))
	for s, lbl in zip(series_list, labels):
		ax.plot(s.index, s.values, marker='.', label=lbl)

	ax.set_title('Average Monthly Volume by Period')
	ax.set_xlabel('Date')
	ax.set_ylabel('Average Volume')
	ax.legend()
	fig.autofmt_xdate()

	buf = io.BytesIO()
	fig.savefig(buf, format='png', bbox_inches='tight')
	plt.close(fig)
	buf.seek(0)
	img_b64 = base64.b64encode(buf.read()).decode('ascii')

	html = f"""
	<html><head><title>Monthly Volume</title></head>
	<body>
	  <h1>Average Monthly Volume (period splits)</h1>
	  <p>Lines show monthly average Volume for each period.</p>
	  <img src="data:image/png;base64,{img_b64}" alt="monthly-volume" />
	</body></html>
	"""
	return html


if __name__ == "__main__":
		# Run local dev server
		app.run(host="127.0.0.1", port=5000, debug=True)

