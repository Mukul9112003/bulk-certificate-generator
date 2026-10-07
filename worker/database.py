from app.database.connection import SessionLocal


def get_db():
    db = SessionLocal()

    try:
        return db
    except Exception:
        db.close()
        raise