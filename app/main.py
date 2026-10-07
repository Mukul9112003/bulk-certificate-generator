from fastapi import FastAPI
from app.routes.event import event_router
from app.database.connection import engine
from app.models import *


app = FastAPI(title="Bulk Certificate Generator")


Base.metadata.create_all(bind=engine)
app.include_router(event_router)


@app.get("/")
def root():
    return {"message": "Bulk Certificate Generator"}