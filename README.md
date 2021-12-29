# Paypal Subscription Receipt Generator

This generates receipts for paypal subscription payments with proper company information.

In order to run this code, you need to:

- Clone this repo
- Create your [virtual environment](https://docs.python.org/3/tutorial/venv.html)
  and activate it
- Run `pip install -r requirements.txt`
- Install `wkhtmltopdf` locally so that pdfkit will work. Check how to do this
  [here](https://wkhtmltopdf.org/downloads.html).
- Write your own `.env` file with all your info (See `.env.example`)

Read `/assets/README.md` for instructions on how to add your company's logo.

To customize your `HTML` template, edit `/templates/template.html`.
