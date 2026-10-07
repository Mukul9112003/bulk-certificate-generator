import time

from app.database.connection import SessionLocal
from app.database.redis import redis_client
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository

QUEUE_NAME = "certificate_queue"


def process_certificate(certificate_id: int):

    db = SessionLocal()

    try:
        repository = CertificateRepository(db)
        user_repository = UserRepository(db)
        event_repository = EventRepository(db)
        certificate = repository.get_by_id(certificate_id)

        if certificate is None:
            print(
                f"Certificate {certificate_id} not found"
            )
            return
         # Mark certificate as processing
        certificate.status = "processing"

        repository.update(certificate)
        # Get user
        user = user_repository.get_by_id(certificate.user_id)

        if user is None:
            print(
                f"User {certificate.user_id} not found"
            )
            return

        # Get event
        event = event_repository.get_by_id(
            certificate.event_id
        )

        if event is None:
            print(
                f"Event {certificate.event_id} not found"
            )
            return

        print("------ Certificate Data ------")
        print(f"Certificate ID: {certificate.id}")
        print(f"User: {user.name}")
        print(f"Email: {user.email}")
        print(f"Event: {event.name}")
        print(f"Event Date: {event.event_date}")
        print("------------------------------")
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