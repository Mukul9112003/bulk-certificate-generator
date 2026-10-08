from sqlalchemy import select
from sqlalchemy.orm import Session

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
    def get_by_job_id(self, job_id: int) -> list[Certificate]:
        statement = (
            select(Certificate)
            .where(Certificate.job_id == job_id)
            .order_by(Certificate.id)
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())
    def get_by_event_and_user(self,event_id: int,user_id: int,) -> Certificate | None:
        statement = (
            select(Certificate)
            .where(
                Certificate.event_id == event_id,
                Certificate.user_id == user_id,
            ).limit(1)
        )

        result = self.db.execute(statement)

        return result.scalars().first()