from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.certificate_job import (CertificateListItem,CertificateListResponse,JobStatusResponse)
from app.database.dependencies import get_db
from app.schemas.certificate_job import JobStatusResponse
from app.service.certificate_job_service import CertificateJobService


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
):
    service = CertificateJobService(db)

    try:
        job = service.get_job_status(job_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    pending = (
        job.total_count
        - job.success_count
        - job.failed_count
    )

    return JobStatusResponse(
        job_id=job.id,
        event_id=job.event_id,
        status=job.status,
        total=job.total_count,
        successful=job.success_count,
        failed=job.failed_count,
        pending=pending,
    )
@router.get(
    "/{job_id}/certificates",
    response_model=CertificateListResponse,
)
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db),
):
    service = CertificateJobService(db)

    try:
        certificates = service.get_job_certificates(job_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    return CertificateListResponse(
        job_id=job_id,
        certificates=[
            CertificateListItem(
                certificate_id=certificate.id,
                user_id=certificate.user_id,
                status=certificate.status,
                s3_key=certificate.s3_key,
                error_message=certificate.error_message,
            )
            for certificate in certificates
        ],
    )