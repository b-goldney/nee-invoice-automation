#!/usr/bin/env python3
import shutil
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Template
from weasyprint import HTML


def load_template():
    """Load the HTML template"""
    template_path = Path(__file__).parent / "templates" / "invoice.html"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found at {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    return Template(template_content)


def process_invoices(csv_path, output_dir, logo_path=None):
    """Process CSV file and generate invoice PDFs"""
    print(csv_path, "<<< csv_path")

    file_extension = csv_path.split(".")[-1]
    # Load CSV
    try:
        if file_extension == "csv":
            df = pd.read_csv(csv_path)
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(csv_path)
    except Exception as e:
        raise Exception(f"Failed to read CSV file: {str(e)}")

    print(f"Processing {len(df)} invoices...")

    # Create output directory for PDFs
    pdf_dir = os.path.join(output_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)

    # Handle logo file
    logo_filename = None
    if logo_path and os.path.exists(logo_path):
        # Create static/images directory in temp dir
        static_dir = os.path.join(output_dir, "static", "images")
        os.makedirs(static_dir, exist_ok=True)

        # Copy logo to static directory
        logo_extension = os.path.splitext(logo_path)[1]
        logo_filename = f"company-logo{logo_extension}"
        logo_dest = os.path.join(static_dir, logo_filename)
        shutil.copy2(logo_path, logo_dest)

    # Load template
    template = load_template()

    # Get today's date
    today = datetime.today().strftime("%B %-d, %Y")

    pdf_files = []

    for index, row in df.iterrows():
        try:
            # Extract data from row
            vendor_name = str(row.get("vendor_name"))
            vendor_routing_number = str(row.get("vendor_routing_number"))
            vendor_account_number = str(row.get("vendor_account_number"))
            bill_to_name = str(row.get("bill_to_name", ""))
            bill_to_address_line_1 = str(row.get("bill_to_address_line_1", ""))
            bill_to_address_line_2 = str(row.get("bill_to_address_line_2", ""))
            bill_to_address_line_3 = str(row.get("bill_to_address_line_3", ""))
            purchase_order = str(row.get("split_order_number", ""))
            invoice_number = str(row.get("invoice_number", ""))
            quantity = row.get("order_item_quantity", 0)
            sku = str(row.get("sku_id", ""))

            # Format unit price
            gross_placed = row.get("Gross Placed: Total Wholesale $", 0)
            try:
                unit_price = f"{float(gross_placed):,.2f}"
            except (ValueError, TypeError):
                unit_price = "0.00"

            # Render template
            html_content = template.render(
                date=today,
                vendor_name=vendor_name,
                vendor_routing_number=vendor_routing_number,
                vendor_account_number=vendor_account_number,
                logo_filename=logo_filename,
                bill_to_name=bill_to_name,
                bill_to_address_line_1=bill_to_address_line_1,
                bill_to_address_line_2=bill_to_address_line_2,
                bill_to_address_line_3=bill_to_address_line_3,
                quantity=quantity,
                purchase_order=purchase_order,
                invoice_number=invoice_number,
                sku=sku,
                unit_price=unit_price,
            )

            # Generate PDF
            pdf_filename = f"{invoice_number}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)

            html_doc = HTML(string=html_content, base_url=str(Path(output_dir)))
            # html_doc = HTML(string=html_content, base_url=str(Path(__file__).parent))
            html_doc.write_pdf(pdf_path)

            pdf_files.append(pdf_path)
            print(f"Generated PDF {index + 1}/{len(df)}: {pdf_filename}")

        except Exception as e:
            print(f"Error processing row {index + 1}: {str(e)}", file=sys.stderr)
            continue

    if not pdf_files:
        raise Exception("No PDFs were generated successfully")

    # Create zip file
    zip_path = os.path.join(
        output_dir, f"invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    )

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for pdf_path in pdf_files:
            # Add file to zip with just the filename (not full path)
            zipf.write(pdf_path, os.path.basename(pdf_path))

    print(f"Created zip file with {len(pdf_files)} PDFs: {zip_path}")
    return zip_path


def main():
    if not (3 <= len(sys.argv) <= 4):
        print(
            "Usage: python process_invoices.py <csv_path> <output_dir> [optional_logo_path]"
        )
        sys.exit(1)

    csv_path = sys.argv[1]
    output_dir = sys.argv[2]
    logo_path = sys.argv[3] if len(sys.argv) > 3 else None
    print("---------------- csv_path ---------------------- ", flush=True)
    print(logo_path, "<<< logo_path", flush=True)

    try:
        zip_path = process_invoices(csv_path, output_dir, logo_path)
        # Print zip path as the last line for the Node.js script to read
        print(zip_path)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
