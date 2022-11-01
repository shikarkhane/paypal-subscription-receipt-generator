from dotenv import load_dotenv
from utility import PdfWriter
import pdfkit

# Loading env variables...
load_dotenv()

file_name = input("Enter html file name : ")

pdf_writer = PdfWriter(pdfkit)
pdf_writer.html_to_pdf(file_name)
