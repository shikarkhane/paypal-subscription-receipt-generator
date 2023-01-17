import csv
import datetime
import copy
import pdfkit
import os

path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
if not os.path.isdir("shopify_invoices"):
    os.makedirs("shopify_invoices")
with open('shopify_earning.csv', newline='') as csv_file:
    shopify_earnings = csv.reader(csv_file, delimiter=',', quotechar='"')
    with open("templates\shopify_payout_template.html") as html_file:
        html_file_content = html_file.read()
        shopify_earnings.__next__()
        for index, row_data in enumerate(shopify_earnings):
            invoice_html = copy.deepcopy(html_file_content)
            bill_amount = row_data[7]
            payout_date = datetime.datetime.strptime(row_data[1], '%Y-%m-%d %H:%M:%S UTC').date()
            invoice_html = invoice_html.replace("{{bill_amount}}", str(bill_amount))
            invoice_html = invoice_html.replace("{{payout_date}}", payout_date.strftime("%b %d, %Y"))
            invoice_html = invoice_html.replace("{{serial_number_date}}", payout_date.strftime("%Y%b%d").upper())
            store_name = row_data[2].split(".")[0]
            pdfkit.from_string(invoice_html,f"shopify_invoices\{index}-{store_name}-invoice.pdf",configuration=config)
            print(f"finish for {index}-{store_name}")
print("finish for all")
