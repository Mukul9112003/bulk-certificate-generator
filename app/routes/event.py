from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.event import EventCreate, EventResponse
from app.service.event_service import EventService

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