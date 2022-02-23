from datetime import datetime
import os
import base64
from jinja2 import Environment, FileSystemLoader


CURRENCY_DICT = {'USD': '$', 'EUR': '€'}


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def get_formatted_date(unformatted_date):
    dt = unformatted_date.split('T')[0].split('-')
    date_string = datetime(int(dt[0]), int(dt[1]), int(dt[2])).strftime('%b {S}, %Y')
    # Return date with right format and day suffix (1st, 2nd, 21st...)
    return date_string.replace('{S}', str(int(dt[2])) + suffix(int(dt[2])))


# Do the html converting stuff
root = os.path.dirname(os.path.abspath(__file__))

logo_filename = os.path.join(root, 'assets', 'logo.png')


def get_image_file_as_base64_data():
    with open(logo_filename, 'rb') as image_file:
        return base64.b64encode(image_file.read())


def get_html_template():
    templates_dir = os.path.join(root, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    return env.get_template('template.html')


class PdfWriter:
    def __init__(self, pdf_kit):
        self.pdf_kit = pdf_kit

    def write_to_pdf(self, payee, payer, transaction):

        filename = os.path.join(root, 'receipts/HTML', f'{transaction.paypal_reference_id}.html')

        with open(filename, 'w') as fh:
            fh.write(get_html_template().render(
                payee_company_name=payee.payee_company_name,
                payee_address=payee.payee_address,
                payee_tax_id=payee.payee_tax_id,
                payee_website=payee.payee_website,
                payee_email=payee.payee_email,
                item_description=payee.item_description,
                image_base64=get_image_file_as_base64_data().decode(),
                title=f"Receipt {payer.payer_name}",
                paypal_reference=transaction.paypal_reference_id,
                transaction_id=transaction.transaction_id,
                invoice_date=transaction.invoice_date,
                payment_date=transaction.payment_date,
                status="PAID",
                balance_due=f'{transaction.currency_symbol} 0.00',
                payer_name=payer.payer_name,
                payer_address_line1=payer.payer_address,
                payer_address_line2=f"{payer.payer_postal_code} {payer.payer_city}",
                payer_country=payer.payer_country,
                total_price=f"{transaction.currency_symbol} {transaction.payment_amount}",
                amount_paid=f"{transaction.currency_symbol} {transaction.payment_amount}",
                reference_name=payer.payer_reference_name,
                reference_email=payer.payer_reference_email,
            ))

        pdf_filename = os.path.join(root, 'receipts/PDF', f'{transaction.paypal_reference_id}.pdf')

        options = {
            'page-size': 'Letter',
            'margin-top': '0.25in',
            'margin-right': '0.3in',
            'margin-bottom': '0.25in',
            'margin-left': '0.5in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'no-outline': None
        }

        self.pdf_kit.from_file(filename, pdf_filename, options=options)