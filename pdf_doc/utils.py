from django.template.loader import render_to_string
from django.conf import settings
import pdfkit
import os

def generate_pdf(document):
    """
    Generate PDF using wkhtmltopdf through pdfkit
    """
    # Render HTML template
    html_content = render_to_string('pdf/pdf_template.html', {
        'document': document,
        'base_url': settings.BASE_URL,
    })

    # PDF options
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': None,
    }

    # Generate PDF
    pdf = pdfkit.from_string(html_content, False, options=options)
    return pdf