from jinja2 import Environment, FileSystemLoader
import pdfkit
import os
import base64

# TODO => Call call api authentication endpoint
# TODO => Grab token and call transactions endpoint

# TODO => Grab Json and pull information for filling up temmplate file
root = os.path.dirname(os.path.abspath(__file__))

logo_filename = os.path.join(root, 'assets', 'yayloh-logo.png')

def get_image_file_as_base64_data():
    with open(logo_filename, 'rb') as image_file:
        return base64.b64encode(image_file.read())


templates_dir = os.path.join(root, 'templates')
env = Environment( loader = FileSystemLoader(templates_dir) )
template = env.get_template('template.html')

# receipts.html is a temporary name!
# Should be called --transaction-id--.html (or something...)
filename = os.path.join(root, 'receipts/HTML', 'receipts.html') 

address_line2 = ""
postal_code = 75003
city_and_country = "Paris, FR"
VAT = 12030103010
with open(filename, 'w') as fh:
    fh.write(template.render(
        image_base64 = get_image_file_as_base64_data().decode(),
        title = "Receipt Company A",
        transaction_id = "192349194919",
        reference_id = "9034199-4912",
        date_paid = "November 12th, 2021",
        payer_name = "Company A",
        address_line1 = "Rue les bleu 21",
        address_line2 = address_line2 if address_line2 != "" else False,
        postal_code = postal_code,
        city_and_country = city_and_country,
        VAT = VAT
    ))
pdf_filename = os.path.join(root, 'receipts/PDF', 'receipts.pdf') 

pdfkit.from_file(filename,pdf_filename) 
