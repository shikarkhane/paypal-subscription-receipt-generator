import os
import json
from dotenv import load_dotenv
from utility import PdfWriter
from provider import paypal
import pdfkit

# Loading env variables...
load_dotenv()

# We need to load payers info because payer info from api is often
# incomplete
with open('payers_information.json') as payer_file:
    PAYER_INFO_FROM_FILE = json.load(payer_file)


class Payee:
    def __init__(self):
        self.payee_company_name = os.environ.get('PAYEE_COMPANY_NAME')
        self.payee_address = os.environ.get('PAYEE_ADDRESS')
        self.payee_tax_id = os.environ.get('PAYEE_TAX_ID')
        self.payee_website = os.environ.get('PAYEE_WEBSITE')
        self.payee_email = os.environ.get('PAYEE_EMAIL')
        self.item_description = os.environ.get('ITEM_DESCRIPTION')


class Payer:
    def __init__(self, payer_dict, payer_email_address):
        self.payer_name = payer_dict['company_name']
        self.payer_address = payer_dict['street_address']
        self.payer_reference_name = payer_dict['reference_name']
        self.payer_reference_email = payer_email_address
        self.payer_postal_code = payer_dict['postal_code']
        self.payer_city = payer_dict['city']
        self.payer_country = payer_dict['country']


start_date = input('Enter start date (format: YYYY-MM-DD): ')
end_date = input('Enter end date (format: YYYY-MM-DD)): ')

payee = Payee()
transactions = paypal.Gateway().get_invoices(start_date, end_date)

print(f'Found {len(transactions)} recepits in that range')

pdf_writer = PdfWriter(pdfkit)

for index, transaction in enumerate(transactions):
    print(f'Printing now receipt # {index+1}')
    payer_info = PAYER_INFO_FROM_FILE.get(transaction.payer_email_address)
    if not payer_info:
        print(f'Payers information missing entry for email: {transaction.payer_email_address}')
        continue

    payer = Payer(payer_info, transaction.payer_email_address)

    pdf_writer.write_to_pdf(payee, payer, transaction)
