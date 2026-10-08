from datetime import datetime, timezone

from app.certificate.template import CertificateTemplate
from app.database.connection import SessionLocal
from app.database.redis import redis_client
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.event_repository import EventRepository
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository

QUEUE_NAME = "certificate_queue"


def process_certificate(certificate_id: int):

    db = SessionLocal()
    certificate_repository = CertificateRepository(db)
    user_repository = UserRepository(db)
    event_repository = EventRepository(db)
    job_repository = JobRepository(db)
    try:
        
        certificate = certificate_repository.get_by_id(certificate_id)

        if certificate is None:
            print(
                f"Certificate {certificate_id} not found"
            )
            return
         # 2. Get job
        job = job_repository.get_by_id(
            certificate.job_id
        )

        if job is None:
            raise ValueError(
                f"Job {certificate.job_id} not found"
            )
         # Mark certificate as processing
        certificate.status = "processing"

        certificate_repository.update(certificate)
        # Get user
        user = user_repository.get_by_id(certificate.user_id)

        if user is None:
            raise ValueError(f"User {certificate.user_id} not found")

        # Get event
        event = event_repository.get_by_id(
            certificate.event_id
        )

        if event is None:
            raise ValueError(f"Event {certificate.event_id} not found")

        template = CertificateTemplate()

        file_path = template.generate(
            certificate_id=certificate.id,
            recipient_name=user.name,
            event_name=event.name,
            event_date=str(event.event_date),
        )

       # 6. Mark completed
        certificate.status = "completed"
        certificate.s3_key = file_path
        certificate.completed_at = datetime.now(timezone.utc)

        certificate_repository.update(certificate)
        job = job_repository.increment_success_count(certificate.job_id)

        processed = (job.success_count+ job.failed_count)

        if processed == job.total_count:
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
        else:
            job.status = "processing"

        job_repository.update(job)
        print(
            f"Certificate {certificate.id} completed"
        )
    except Exception as error:

            print(f"Certificate {certificate_id} failed: {error}")

            # Try to mark certificate as failed
            try:
                certificate = certificate_repository.get_by_id(
                    certificate_id
                )

                if certificate is not None:
                    certificate.status = "failed"
                    certificate.error_message = str(error)

                    certificate_repository.update(certificate)
                    job = job_repository.get_by_id(certificate.job_id)
                    if job is not None:

                        job = job_repository.increment_failed_count(certificate.job_id)

                        processed = (job.success_count+ job.failed_count)

                        if processed == job.total_count:
                            job.status = "completed"
                            job.completed_at = datetime.now(timezone.utc)
                        else:
                            job.status = "processing"

                        job_repository.update(job)
            except Exception as update_error:
                print(f"Could not update failed certificate: "f"{update_error}")
    finally:
        db.close()

def main():
    print("Certificate worker started")

    while True:
        result = redis_client.blpop(QUEUE_NAME)

        if result is None:
            continue

        _, certificate_id = result

        process_certificate(int(certificate_id))


if __name__ == "__main__":
    main()