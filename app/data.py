import os
from flask import Flask, request, Response, render_template_string
import pandas as pd


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


if __name__ == "__main__":
		# Run local dev server
		app.run(host="127.0.0.1", port=5000, debug=True)

