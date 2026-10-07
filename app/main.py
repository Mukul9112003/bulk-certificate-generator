from fastapi import FastAPI

from app.database.connection import engine
from app.models.base import Base

from app import models


app = FastAPI(title="Bulk Certificate Generator")


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Bulk Certificate Generator"}