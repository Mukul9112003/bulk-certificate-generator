from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.service.event_service import EventService
from app.database.dependencies import get_db
from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, EventResponse


event_router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@event_router.post("", response_model=EventResponse)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
):
    service = EventService(db)

    return service.create_event(event_data)