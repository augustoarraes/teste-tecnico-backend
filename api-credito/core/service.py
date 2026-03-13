# Lógica de negócio

from sqlalchemy import text
from core.repository import session


def check_database():
    db = session
    try:
        version = db.execute(text("SELECT version()")).scalar()
        return {
            "database": "connected",
            "postgres_version": version
        }
    except Exception as e:
        return {
            "database": "error",
            "detail": str(e)
        }
    finally:
        db.close()
