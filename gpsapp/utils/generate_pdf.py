import pdfkit
from django.template.loader import render_to_string
from django.conf import settings
import os


def build_pdf_report(context, template_name="report_template.html"):
    """
    Render HTML template + context naar PDF met WKHTMLTOPDF.
    """

    # HTML renderen vanuit Django template
    html_string = render_to_string(template_name, context)

    # Pad naar wkhtmltopdf executable
    WKHTMLTOPDF_CMD = getattr(
        settings,
        "WKHTMLTOPDF_CMD",
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",  # Standaard Windows locatie
    )

    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)

    # Opties voor PDF (A4, marges, DPI, geen achtergrond verloren)
    options = {
        "page-size": "A4",
        "margin-top": "10mm",
        "margin-bottom": "10mm",
        "margin-left": "10mm",
        "margin-right": "10mm",
        "dpi": 300,
        "enable-local-file-access": "",  # ⬅ belangrijk voor statische afbeeldingen
        "zoom": "0.80",  # kleinere rendering zodat niets buiten de pagina valt
    }

    # PDF genereren als bytes
    pdf_bytes = pdfkit.from_string(html_string, False, configuration=config, options=options)

    return pdf_bytes