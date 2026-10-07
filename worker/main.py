import time

from app.database.connection import SessionLocal
from app.database.redis import redis_client
from app.repositories.certificate_repository import CertificateRepository


QUEUE_NAME = "certificate_queue"


def process_certificate(certificate_id: int):

    db = SessionLocal()

    try:
        repository = CertificateRepository(db)

        certificate = repository.get_by_id(certificate_id)

        if certificate is None:
            print(
                f"Certificate {certificate_id} not found"
            )
            return

        print(
            f"Processing certificate {certificate.id}"
        )

        print(
            f"User ID: {certificate.user_id}"
        )

        print(
            f"Event ID: {certificate.event_id}"
        )

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