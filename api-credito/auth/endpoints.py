from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dto import LoginInput, TokenOutput
from auth.service import login


app = APIRouter(prefix="/api/auth", tags=["Auth"])


@app.post("/login", response_model=TokenOutput, tags=['Auth'])
def login_endpoint(payload: LoginInput):
    return login(payload.email, payload.password)