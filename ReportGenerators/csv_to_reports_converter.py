import csv
import os
from collections import defaultdict
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import pdfkit


class PayoutReportGenerator:
    def __init__(self, csv_path, template_path, template_name):
        self.csv_path = csv_path
        self.template_path = template_path
        self.template_name = template_name
        self.env = Environment(loader=FileSystemLoader(self.template_path))
        self.template = self.env.get_template(self.template_name)

        self.output_html_dir = '../receipts/HTML'
        self.output_pdf_dir = '../receipts/PDF'

    def read_csv(self):
        payouts_by_date = defaultdict(float)
        with open(self.csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                payout_date = row['Payout Date']
                partner_share = float(row['Partner Share'])
                payouts_by_date[payout_date] += partner_share
        return payouts_by_date

    def create_reports(self, payouts_by_date):
        for payout_date, transactions in payouts_by_date.items():
            date_obj = datetime.strptime(payout_date, '%Y-%m-%d %H:%M:%S UTC')
            html_file_name = f"payout_report_{date_obj.strftime('%Y-%m-%d')}.html"
            self.create_html_report(html_file_name, date_obj, transactions)
            self.create_pdf_report(html_file_name)

    def create_html_report(self, file_name, date_obj, transactions):
        file_path = os.path.join(self.output_html_dir, file_name)
        html_content = self.template.render(
            payout_date=date_obj.strftime('%b %d, %Y'),
            bill_amount=transactions,
            serial_number_date=date_obj.strftime('%Y%b%d').upper()
        )
        with open(file_path , 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML file successfully created: '{file_name}'")

    def create_pdf_report(self, html_file_name):
        html_file_path = os.path.join(self.output_html_dir, html_file_name)
        pdf_file_path = os.path.join(self.output_pdf_dir, html_file_name.replace('.html', '.pdf'))
        pdfkit.from_file(html_file_path, pdf_file_path)
        print(f"Successfully transformed into PDF: '{html_file_name}'")

# Usage
if __name__ == "__main__":
    load_dotenv()
    csv_file_path = input("Enter the path of the file :")
    report_generator = PayoutReportGenerator(csv_file_path, '../templates', 'shopify_payout_template.html')
    payouts_by_date = report_generator.read_csv()
    report_generator.create_reports(payouts_by_date)
