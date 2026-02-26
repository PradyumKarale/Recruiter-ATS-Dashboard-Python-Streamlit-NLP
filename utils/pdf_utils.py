import pdfplumber
from pdf2image import convert_from_path


def is_scanned_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:2]:
            if page.extract_text():
                return False
    return True


def pdf_to_images(pdf_path, dpi=200):
    return convert_from_path(pdf_path, dpi=dpi)
