from pydantic import BaseModel, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    email: str | None = None

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
class CertificateListItem(BaseModel):
    certificate_id: int
    user_id: int | None
    status: str
    s3_key: str | None
    error_message: str | None


class CertificateListResponse(BaseModel):
    job_id: int
    certificates: list[CertificateListItem]