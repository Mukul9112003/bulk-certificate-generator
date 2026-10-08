from fastapi import FastAPI
from app.routes.event import event_router
from app.database.connection import engine
from app.models import *
from app.routes.certificate import router as certificate_router
from app.routes.certificate_job import router as certificate_job_router
from app.routes.job import router as job_router
app = FastAPI(title="Bulk Certificate Generator")


Base.metadata.create_all(bind=engine)
app.include_router(event_router)
app.include_router(certificate_job_router)
app.include_router(job_router)
app.include_router(certificate_router)
@app.get("/")
def root():
    return {"message": "Bulk Certificate Generator"}