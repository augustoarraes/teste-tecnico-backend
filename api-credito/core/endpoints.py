# Rotas FastAPI

from fastapi import APIRouter, status, HTTPException, Depends

from sqlalchemy.orm import Session

from core.service import check_database


app = APIRouter(prefix="/api", tags=["Default"])


@app.get("/db-check")
def db_check():
    return check_database()


@app.get("/ping")
def ping_pong():
    return {"ping": "pong"}

