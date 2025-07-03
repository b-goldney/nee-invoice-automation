import os
import io
import zipfile
import tempfile
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename

import pandas as pd
from flask import (
    Flask,
    request,
    render_template,
    send_file,
    redirect,
    url_for,
    flash,
    jsonify,
)

from weasyprint import HTML

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this to a secure secret key
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_csv_columns(df):
    """Validate that the CSV has required columns"""
    required_columns = [
        "Split Order Number",
        "Invoice #",
        "Order Item Quantity (# of units ordered)",
        "SKU ID (Vendor SKU ID)",
        "Gross Placed: Total Wholesale $",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    return True, ""


def generate_invoice_pdf(row, temp_dir):
    """Generate a single invoice PDF and return the file path"""
    today = datetime.today().strftime("%B %-d, %Y")

    purchase_order = row["Split Order Number"]
    invoice_number = row["Invoice #"]
    quantity = row["Order Item Quantity (# of units ordered)"]
    sku = row["SKU ID (Vendor SKU ID)"]
    unit_price = f"{row['Gross Placed: Total Wholesale $']:,.2f}"

    # Render the HTML template
    template = render_template(
        "invoice.html",
        date=today,
        quantity=quantity,
        purchase_order=purchase_order,
        invoice_number=invoice_number,
        sku=sku,
        unit_price=unit_price,
    )

    # Generate PDF
    html = HTML(string=template, base_url=request.url_root)
    pdf_path = os.path.join(temp_dir, f"{invoice_number}.pdf")
    html.write_pdf(pdf_path)

    return pdf_path


@app.route("/")
def index():
    """Landing page with upload option"""
    return render_template("upload.html")


@app.route("/uploads", methods=["GET", "POST"])
def upload_file():
    """Handle file upload and process invoices"""
    if request.method == "GET":
        return render_template("upload.html")

    if request.method == "POST":
        # Check if file was uploaded
        if "file" not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                # Read CSV directly from upload
                df = pd.read_csv(file)
                print(f"Loaded CSV with shape: {df.shape}")

                # Validate CSV columns
                is_valid, error_message = validate_csv_columns(df)
                if not is_valid:
                    flash(f"Invalid CSV format: {error_message}")
                    return redirect(request.url)

                # Create temporary directory for PDFs
                with tempfile.TemporaryDirectory() as temp_dir:
                    pdf_files = []

                    # Generate PDFs for each row
                    for index, row in df.iterrows():
                        try:
                            pdf_path = generate_invoice_pdf(row, temp_dir)
                            pdf_files.append(pdf_path)
                            print(
                                f"Generated PDF {index + 1}/{len(df)}: {os.path.basename(pdf_path)}"
                            )
                        except Exception as e:
                            print(f"Error generating PDF for row {index}: {str(e)}")
                            continue

                    if not pdf_files:
                        flash("No PDFs were generated. Please check your CSV format.")
                        return redirect(request.url)

                    # Create ZIP file in memory
                    zip_buffer = io.BytesIO()

                    with zipfile.ZipFile(
                        zip_buffer, "w", zipfile.ZIP_DEFLATED
                    ) as zip_file:
                        for pdf_path in pdf_files:
                            if os.path.exists(pdf_path):
                                zip_file.write(pdf_path, os.path.basename(pdf_path))

                    zip_buffer.seek(0)

                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    zip_filename = f"invoices_{timestamp}.zip"

                    return send_file(
                        zip_buffer,
                        as_attachment=True,
                        download_name=zip_filename,
                        mimetype="application/zip",
                    )

            except pd.errors.EmptyDataError:
                flash("The uploaded file is empty or invalid")
                return redirect(request.url)
            except pd.errors.ParserError:
                flash("Unable to parse the CSV file. Please check the format.")
                return redirect(request.url)
            except Exception as e:
                flash(f"An error occurred while processing the file: {str(e)}")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload a CSV file.")
            return redirect(request.url)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """API endpoint for programmatic uploads"""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        df = pd.read_csv(file)

        # Validate CSV
        is_valid, error_message = validate_csv_columns(df)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        # Generate PDFs and ZIP (same logic as above)
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_files = []

            for index, row in df.iterrows():
                try:
                    pdf_path = generate_invoice_pdf(row, temp_dir)
                    pdf_files.append(pdf_path)
                except Exception as e:
                    continue

            if not pdf_files:
                return jsonify({"error": "No PDFs were generated"}), 400

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for pdf_path in pdf_files:
                    if os.path.exists(pdf_path):
                        zip_file.write(pdf_path, os.path.basename(pdf_path))

            zip_buffer.seek(0)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name=f"invoices_{timestamp}.zip",
                mimetype="application/zip",
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Keep the original route for backward compatibility
@app.route("/generate")
def generate_original():
    """Original functionality with hardcoded CSV"""
    MONTH = "june"

    try:
        df = pd.read_csv(f"../data/inputs/{MONTH}.csv")
        today_date = datetime.today().strftime("%Y%m%d")
        output_path = f"../data/outputs/{today_date}"
        os.makedirs(output_path, exist_ok=True)

        today = datetime.today().strftime("%B %-d, %Y")

        for _, row in df.iterrows():
            purchase_order = row["Split Order Number"]
            invoice_number = row["Invoice #"]
            quantity = row["Order Item Quantity (# of units ordered)"]
            sku = row["SKU ID (Vendor SKU ID)"]
            unit_price = f"{row['Gross Placed: Total Wholesale $']:,.2f}"

            template = render_template(
                "invoice.html",
                date=today,
                quantity=quantity,
                purchase_order=purchase_order,
                invoice_number=invoice_number,
                sku=sku,
                unit_price=unit_price,
            )

            html = HTML(string=template, base_url=request.url_root)
            html.write_pdf(f"{output_path}/{invoice_number}.pdf")

        return f"Generated {len(df)} invoices in {output_path}"

    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50002, debug=True)
