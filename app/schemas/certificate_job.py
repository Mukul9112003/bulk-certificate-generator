from pydantic import BaseModel, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr

class CertificateJobCreate(BaseModel):
    recipients: list[RecipientCreate] = Field(
        min_length=1,
        max_length=10000,
    )

class CertificateJobResponse(BaseModel):
    job_id: int
    event_id: int
    status: str
    total: int


class JobStatusResponse(BaseModel):
    job_id: int
    event_id: int
    status: str
    total: int
    successful: int
    failed: int
    pending: int