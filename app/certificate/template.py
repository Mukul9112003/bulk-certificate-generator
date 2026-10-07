from dataclasses import dataclass


@dataclass
class CertificateTemplate:
    title: str
    recipient_name: str
    event_name: str
    event_date: str

    def render(self) -> str:
        return f"""
        ==============================
              CERTIFICATE
        ==============================

        {self.title}

        This certificate is proudly
        presented to

        {self.recipient_name}

        for participating in

        {self.event_name}

        Date: {self.event_date}

        ==============================
        """