import os
import requests
from utility import get_formatted_date, CURRENCY_DICT


class Transaction:
    def __init__(self, json: dict):
        info = json['transaction_info']
        self.payer_email_address = json['payer_info']['email_address']
        self.paypal_reference_id = info['paypal_reference_id']
        self.transaction_id = info['transaction_id']
        self.invoice_date = get_formatted_date(info['transaction_initiation_date'])
        self.payment_date = get_formatted_date(info['transaction_updated_date'])
        self.payment_amount = info['transaction_amount']['value']
        self.currency_symbol = CURRENCY_DICT[info['transaction_amount']['currency_code']]

    def repr_json(self):
        return dict(payer_email_address=self.payer_email_address, paypal_reference_id=self.paypal_reference_id,
                    transaction_id=self.transaction_id, invoice_date=self.invoice_date,
                    payment_date=self.payment_date, payment_amount=self.payment_amount,
                    currency_symbol=self.currency_symbol)


class Gateway:
    def __init__(self):
        client_id = os.environ.get('PAYPAL_CLIENT_ID')
        secret = os.environ.get('PAYPAL_SECRET')
        self.base_url = os.environ.get('BASE_URL')

        # Grab access token
        access_token_headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = {
            'grant_type': 'client_credentials'
        }
        auth = (client_id, secret)
        response = requests.post(f'{self.base_url}/oauth2/token',
                                 headers=access_token_headers, data=data, auth=auth)
        self.access_token = response.json()['access_token']

    def get_invoices(self, start_date, end_date):
        # Now use access token to grab data from the API
        transaction_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
        }

        res = requests.get(
            f'{self.base_url}/reporting/transactions'
            f'?start_date={start_date}T00:00:00-0700&end_date={end_date}T23:59:59-0700'
            f'&fields=all&page_size=100&page=1&transaction_type=T0002',
            headers=transaction_headers)

        return [Transaction(i) for i in res.json()['transaction_details']]
