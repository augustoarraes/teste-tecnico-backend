from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from auth.security import create_access_token, verify_password
from auth import repository

from core.repository import session


def login( email: str, password: str) -> dict:
    db = session
    user = repository.get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )

    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário sem tenant associado.",
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "role": user.role,
            "email": user.email,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }