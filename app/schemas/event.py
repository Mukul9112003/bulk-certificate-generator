from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    event_date: date
class EventResponse(BaseModel):
    id: int
    name: str
    description: str | None
    event_date: date

    model_config = ConfigDict(from_attributes=True)
    '''Why from_attributes=True?

Because SQLAlchemy gives us an Event object, while FastAPI needs to convert it into our Pydantic response model.'''