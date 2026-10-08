from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job


class JobRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, job: Job) -> Job:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def get_by_id(self, job_id: int) -> Job | None:
        statement = select(Job).where(Job.id == job_id)

        result = self.db.execute(statement)

        return result.scalar_one_or_none()
    def update(self, job: Job) -> Job:
        self.db.commit()
        self.db.refresh(job)

        return job