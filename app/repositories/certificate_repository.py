from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.certificate import Certificate


class CertificateRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, certificate: Certificate) -> Certificate:
        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)

        return certificate

    def create_many(
        self,
        certificates: list[Certificate],
    ) -> list[Certificate]:

        self.db.add_all(certificates)
        self.db.commit()

        for certificate in certificates:
            self.db.refresh(certificate)

        return certificates
    def get_by_id(self,certificate_id: int,) -> Certificate | None:

        statement = select(Certificate).where(Certificate.id == certificate_id)

        result = self.db.execute(statement)

        return result.scalar_one_or_none()
    def update(self, certificate: Certificate) -> Certificate:
        self.db.commit()
        self.db.refresh(certificate)

        return certificate