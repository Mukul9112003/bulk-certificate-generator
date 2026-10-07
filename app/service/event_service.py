from sqlalchemy.orm import Session

from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate


class EventService:

    def __init__(self, db: Session):
        self.repository = EventRepository(db)

    def create_event(self, event_data: EventCreate) -> Event:

        event = Event(
            name=event_data.name,
            description=event_data.description,
            event_date=event_data.event_date,
        )

        return self.repository.create(event)