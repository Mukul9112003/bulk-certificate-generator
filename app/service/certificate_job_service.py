from sqlalchemy.orm import Session
from app.database.redis import redis_client
from app.models.certificate import Certificate
from app.models.job import Job
from app.models.user import User

from app.repositories.certificate_repository import CertificateRepository
from app.repositories.event_repository import EventRepository
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository

from app.schemas.certificate_job import CertificateJobCreate


class CertificateJobService:

    def __init__(self, db: Session):
        self.event_repository = EventRepository(db)
        self.user_repository = UserRepository(db)
        self.job_repository = JobRepository(db)
        self.certificate_repository = CertificateRepository(db)

    def create_job(
        self,
        event_id: int,
        job_data: CertificateJobCreate,
    ) -> Job:

        # 1. Check event
        event = self.event_repository.get_by_id(event_id)

        if event is None:
            raise ValueError("Event not found")

        # 2. Create job
        job = Job(
            event_id=event_id,
            status="queued",
            total_count=len(job_data.recipients),
            success_count=0,
            failed_count=0,
        )

        job = self.job_repository.create(job)

        # 3. Resolve users
        certificates = []

        for recipient in job_data.recipients:

            user = self.user_repository.get_by_email(
                recipient.email
            )

            if user is None:
                user = User(
                    name=recipient.name,
                    email=recipient.email,
                )

                user = self.user_repository.create(user)

            certificate = Certificate(
                job_id=job.id,
                event_id=event_id,
                user_id=user.id,
                status="pending",
            )

            certificates.append(certificate)

        # 4. Create certificate records
        self.certificate_repository.create_many(certificates)
        for certificate in certificates:
            redis_client.rpush("certificate_queue",certificate.id,)

        return job