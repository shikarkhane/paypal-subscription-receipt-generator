from jinja2 import Environment, FileSystemLoader
import pdfkit
import os
import json
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv


def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')


def get_formatted_date(unformatted_date):
    dt = unformatted_date.split('T')[0].split('-')
    date_string = datetime(int(dt[0]), int(dt[1]), int(dt[2])).strftime('%b {S}, %Y')
    # Return date with right format and day suffix (1st, 2nd, 21st...)
    return date_string.replace('{S}', str(int(dt[2])) + suffix(int(dt[2])))

currency_dict = {'USD': '$', 'EUR': '€'}

# Loading env variables...
load_dotenv()
CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
SECRET = os.environ.get('PAYPAL_SECRET')
BASE_URL = os.environ.get('BASE_URL')
PAYEE_COMPANY_NAME = os.environ.get('PAYEE_COMPANY_NAME')
PAYEE_ADDRESS = os.environ.get('PAYEE_ADDRESS')
PAYEE_TAX_ID = os.environ.get('PAYEE_TAX_ID')
PAYEE_WEBSITE = os.environ.get('PAYEE_WEBSITE')
PAYEE_EMAIL = os.environ.get('PAYEE_EMAIL')
ITEM_DESCRIPTION = os.environ.get('ITEM_DESCRIPTION')


# Grab access token
access_token_headers = {
    'Accept': 'application/json',
    'Accept-Language': 'en_US',
}

data = {
  'grant_type': 'client_credentials'
}

auth = (CLIENT_ID, SECRET)

response = requests.post(f'{BASE_URL}/oauth2/token',
                         headers=access_token_headers, data=data, auth=auth)

access_token = response.json()['access_token']

# Now use access token to grab data from the API
transaction_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}',
}
start_date = input('Enter start date (format: YYYY-MM-DD): ')
end_date = input('Enter end date (format: YYYY-MM-DD)): ')

res = requests.get(f'{BASE_URL}/reporting/transactions?start_date={start_date}T00:00:00-0700&end_date={end_date}T23:59:59-0700&fields=all&page_size=100&page=1&transaction_type=T0002',
             headers=transaction_headers)

transactions_array = res.json()['transaction_details']

# Do the html converting stuff
root = os.path.dirname(os.path.abspath(__file__))

logo_filename = os.path.join(root, 'assets', 'logo.png')

def get_image_file_as_base64_data():
    with open(logo_filename, 'rb') as image_file:
        return base64.b64encode(image_file.read())


templates_dir = os.path.join(root, 'templates')
env = Environment( loader = FileSystemLoader(templates_dir) )
template = env.get_template('template.html')


print(f'Found {len(transactions_array)} recepits in that range')

for index, transaction in enumerate(transactions_array):
    print(f'Printing now receipt # {index+1}')
    transaction_info = transaction['transaction_info']

    try:
        with open('transaction_details.json') as json_file:
            payer_info_from_api = json.load(json_file)['transaction_details'][index]['payer_info']
            payer_email_address = payer_info_from_api['email_address']
    except Exception as e:
        payer_email_address = transaction['payer_info']['email_address']

    # We need to load payers info because payer info from api is often
    # incomplete
    with open('payers_information.json') as payer_file:
        payer_info_from_file = json.load(payer_file)


    paypal_reference_id =  transaction_info['paypal_reference_id']
    transaction_id = transaction_info['transaction_id']
    invoice_date = get_formatted_date(transaction_info['transaction_initiation_date'])
    payment_date = get_formatted_date(transaction_info['transaction_updated_date'])

    payer_dict = payer_info_from_file[payer_email_address]

    payer_name = payer_dict['company_name']
    payer_address = payer_dict['street_address']
    payer_reference_name = payer_dict['reference_name']
    payer_reference_email = payer_email_address
    payment_amount = transaction_info['transaction_amount']['value']
    payer_postal_code = payer_dict['postal_code']
    payer_city = payer_dict['city']
    payer_country = payer_dict['country']
    currency_symbol = currency_dict[transaction_info['transaction_amount']['currency_code']]

    filename = os.path.join(root, 'receipts/HTML', f'{paypal_reference_id}.html') 

    with open(filename, 'w') as fh:
        fh.write(template.render(
            payee_company_name = PAYEE_COMPANY_NAME,
            payee_address = PAYEE_ADDRESS,
            payee_tax_id = PAYEE_TAX_ID,
            payee_website = PAYEE_WEBSITE,
            payee_email = PAYEE_EMAIL,
            item_description=ITEM_DESCRIPTION,
            image_base64 = get_image_file_as_base64_data().decode(),
            title = f"Receipt {payer_name}",
            paypal_reference = paypal_reference_id,
            transaction_id = transaction_id,
            invoice_date = invoice_date,
            payment_date = payment_date,
            status = "PAID",
            balance_due = f'{currency_symbol} 0.00',
            payer_name = payer_name,
            payer_address_line1 = payer_address,
            payer_address_line2 = f"{payer_postal_code} {payer_city}",
            payer_country = payer_country,
            total_price = f"{currency_symbol} {payment_amount}",
            ammount_paid = f"{currency_symbol} {payment_amount}",
            reference_name = payer_reference_name,
            reference_email = payer_reference_email,
        ))

    pdf_filename = os.path.join(root, 'receipts/PDF', f'{paypal_reference_id}.pdf') 

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

    pdfkit.from_file(filename, pdf_filename, options=options) 
