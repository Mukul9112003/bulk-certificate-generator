from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path("generated_certificates")


class CertificateTemplate:

    def generate(
        self,
        certificate_id: int,
        recipient_name: str,
        event_name: str,
        event_date: str,
    ) -> str:
        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            OUTPUT_DIR
            / f"certificate_{certificate_id}.pdf"
        )

        page_width, page_height = landscape(A4)

        pdf = canvas.Canvas(
            str(file_path),
            pagesize=landscape(A4),
        )

        # Title
        pdf.setFont("Helvetica-Bold", 30)

        pdf.drawCentredString(
            page_width / 2,
            page_height - 120,
            "CERTIFICATE OF PARTICIPATION",
        )

        # Main text
        pdf.setFont("Helvetica", 16)

        pdf.drawCentredString(
            page_width / 2,
            page_height - 190,
            "This certificate is proudly presented to",
        )

        # Recipient
        pdf.setFont("Helvetica-Bold", 26)

        pdf.drawCentredString(
            page_width / 2,
            page_height - 250,
            recipient_name,
        )

        # Event
        pdf.setFont("Helvetica", 16)

        pdf.drawCentredString(
            page_width / 2,
            page_height - 310,
            f"for participating in {event_name}",
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 350,
            f"Date: {event_date}",
        )

        pdf.showPage()
        pdf.save()

        return str(file_path)