import os
import io
from datetime import datetime

import pandas as pd
from flask import Flask, request, render_template, send_file
from weasyprint import HTML


MONTH = "june"

app = Flask(__name__)

# create folder and load data
today_date = datetime.today().strftime("%Y%m%d")
output_path = f"../data/outputs/{today_date}"
df = pd.read_csv(f"../data/inputs/{MONTH}.csv")
os.makedirs(output_path, exist_ok=True)
print(df.shape, "<<< df.shape")
print(df.head(2))


@app.route("/")
def hello_world():
    today = datetime.today().strftime("%B %-d, %Y")
    for _, row in df.iterrows():
        print(row, "<<< row")
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
        # save pdf
        html = HTML(
            string=template,
            base_url="/Users/brandongoldney/Documents/projects/pappy/nee-invoice-automation/flask",
        )
        rendered_pdf = html.write_pdf(f"{output_path}/{invoice_number}.pdf")
    return template
    # return send_file(template, attachment_filename="invoice.pdf")
    # return send_file(template)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50002, debug=True)
