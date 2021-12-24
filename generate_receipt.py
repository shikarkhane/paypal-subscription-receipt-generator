from jinja2 import Environment, FileSystemLoader
import pdfkit
import os
import base64

# TODO => Call call api authentication endpoint
# TODO => Grab token and call transactions endpoint

# TODO => Grab Json and pull information for filling up temmplate file
root = os.path.dirname(os.path.abspath(__file__))

logo_filename = os.path.join(root, 'assets', 'yayloh-small.png')

def get_image_file_as_base64_data():
    with open(logo_filename, 'rb') as image_file:
        return base64.b64encode(image_file.read())


templates_dir = os.path.join(root, 'templates')
env = Environment( loader = FileSystemLoader(templates_dir) )
template = env.get_template('template.html')

# receipts.html is a temporary name!
# Should be called --transaction-id--.html (or something...)
filename = os.path.join(root, 'receipts/HTML', 'receipts.html') 


payer_address_line2 = ""
payer_postal_code = 75003
payer_city = "Paris"
payer_country = "France"
with open(filename, 'w') as fh:
    fh.write(template.render(
        image_base64 = get_image_file_as_base64_data().decode(),
        title = "Receipt Company A",
        paypal_reference = "I-G2349194919",
        transaction_id = "9034199-4912",
        invoice_date = "Nov 12th, 21",
        payment_date = "Nov 12th, 21",
        status = "PAID",
        balance_due ="€0.00",
        payer_name = "Company A",
        payer_address_line1 = "Rue les bleu 21",
        payer_address_line2 = f"{payer_postal_code} {payer_city}",
        payer_country = payer_country,
        total_price = "€297.00",
        ammount_paid = "€297.00",
        reference_name = "Julie Liot",
        reference_email = "julie@smoon-lingerie.com",
    ))
pdf_filename = os.path.join(root, 'receipts/PDF', 'receipts.pdf') 

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

pdfkit.from_file(filename,pdf_filename, options=options) 
