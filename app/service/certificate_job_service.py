from sqlalchemy.orm import Session
from app.database.redis import redis_client
from app.models.certificate import Certificate
from app.models.job import Job
from app.models.user import User
from pydantic import TypeAdapter, EmailStr
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
        email_validator = TypeAdapter(EmailStr)
        for recipient in job_data.recipients:
            if not recipient.name or not recipient.name.strip():
                certificate = Certificate(job_id=job.id,event_id=event_id,user_id=None,status="failed",error_message="Recipient name is required",)
                certificates.append(certificate)
                continue

            try:
                email = email_validator.validate_python(recipient.email)
            except Exception as error :
                certificate = Certificate(job_id=job.id,event_id=event_id,user_id=None,status="failed",error_message=f"Invalid email address",)
                certificates.append(certificate)
                continue   
            user = self.user_repository.get_by_email(
                email
            )

            if user is None:
                user = User(
                    name=recipient.name,
                    email=recipient.email,
                )

                user = self.user_repository.create(user)
            existing_certificate = (self.certificate_repository.get_by_event_and_user(event_id=event_id,user_id=user.id,))

            if existing_certificate is not None:
                certificate = Certificate(job_id=job.id,event_id=event_id,user_id=user.id,status="failed",error_message="Certificate already exists for this event",)

                certificates.append(certificate)
                continue
            certificate = Certificate(job_id=job.id,event_id=event_id,user_id=user.id,status="pending",)

            certificates.append(certificate)
        # 4. Create certificate records
        self.certificate_repository.create_many(certificates)
        job.failed_count = sum(1 for certificate in certificates if certificate.status == "failed")

        self.job_repository.update(job)

        for certificate in certificates:
             if certificate.status == "pending":
                redis_client.rpush("certificate_queue",certificate.id,)

        return job
    def get_job_status(self, job_id: int) -> Job:
            job = self.job_repository.get_by_id(job_id)

            if job is None:
                raise ValueError("Job not found")

            return job
    def get_certificate(self, certificate_id: int) -> Certificate:
        certificate = self.certificate_repository.get_by_id(certificate_id)

        if certificate is None:
            raise ValueError("Certificate not found")

        return certificate
    def get_job_certificates(self, job_id: int) -> list[Certificate]:
        job = self.job_repository.get_by_id(job_id)

        if job is None:
            raise ValueError("Job not found")

        return self.certificate_repository.get_by_job_id(job_id)