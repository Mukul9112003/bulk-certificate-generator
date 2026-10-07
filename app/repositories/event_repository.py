from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event: Event) -> Event:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def get_by_id(self, event_id: int) -> Event | None:
        statement = select(Event).where(Event.id == event_id)

        result = self.db.execute(statement)

        return result.scalar_one_or_none()