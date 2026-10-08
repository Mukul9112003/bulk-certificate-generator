from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.service.certificate_job_service import CertificateJobService

router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"],
)


@router.get("/{certificate_id}")
def get_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
):
    service = CertificateJobService(db)

    try:
        certificate = service.get_certificate(certificate_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    if certificate.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Certificate is not available. Current status: {certificate.status}",
        )

    if not certificate.s3_key:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found",
        )

    file_path = Path(certificate.s3_key)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Certificate file does not exist",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf",
    )