from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def validate_csv(file_path):
    df = pd.read_csv(file_path)

    errors = []

    # Missing values
    if df.isnull().sum().sum() > 0:
        errors.append("Missing values found in file")

    # Duplicate rows
    if df.duplicated().sum() > 0:
        errors.append("Duplicate rows detected")

    # Email validation
    if "email" in df.columns:
        invalid_email = df[~df["email"].astype(str).str.contains("@", na=False)]
        if len(invalid_email) > 0:
            errors.append("Invalid email format found")

    # Numeric check
    if "age" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["age"]):
            errors.append("Age column must be numeric")

    return errors


@app.route("/", methods=["GET", "POST"])
def index():
    errors = []
    table = None

    if request.method == "POST":
        file = request.files["file"]

        if file:
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            errors = validate_csv(path)

            df = pd.read_csv(path)
            table = df.head().to_html(classes="table table-striped")

    return render_template("index.html", errors=errors, table=table)


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)