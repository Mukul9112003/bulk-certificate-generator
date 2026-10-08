from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.schemas.certificate_job import (CertificateJobCreate,CertificateJobResponse,JobStatusResponse,)
from app.database.dependencies import get_db
from app.schemas.certificate_job import (CertificateJobCreate,CertificateJobResponse,CertificateListItem,CertificateListResponse,JobStatusResponse)
from app.service.certificate_job_service import CertificateJobService


router = APIRouter(
    prefix="/events",
    tags=["Certificate Jobs"],
)


@router.post(
    "/{event_id}/certificate-jobs",
    response_model=CertificateJobResponse,
)
def create_certificate_job(
    event_id: int,
    job_data: CertificateJobCreate,
    db: Session = Depends(get_db),
):
    service = CertificateJobService(db)

    job = service.create_job(
        event_id=event_id,
        job_data=job_data,
    )

    return CertificateJobResponse(
        job_id=job.id,
        event_id=job.event_id,
        status=job.status,
        total=job.total_count,
    )
