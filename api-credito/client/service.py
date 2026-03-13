from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from uuid import UUID

from client import repository
from client.dto import ClientCreateInput, ClientUpdateInput


def create_client(current_user, payload: ClientCreateInput):
    existing = repository.get_client_by_cpf(current_user.tenant_id, payload.cpf)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe cliente com este CPF neste tenant.",
        )

    return repository.create_client(
        tenant_id=current_user.tenant_id,
        created_by=current_user.user_id,
        name=payload.name,
        cpf=payload.cpf,
        birth_date=payload.birth_date,
        phone=payload.phone,
    )


def list_clients(current_user, skip: int = 0, limit: int = 10):
    return repository.list_clients(tenant_id=current_user.tenant_id, skip=skip, limit=limit,)


def get_client_by_id(current_user, client_id: UUID):
    client = repository.get_client_by_id(tenant_id=current_user.tenant_id, client_id=client_id,)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
        )
    return client


def update_client(current_user, client_id: UUID, payload: ClientUpdateInput):
    duplicated = repository.get_client_by_cpf_excluding_id(
        tenant_id=current_user.tenant_id,
        cpf=payload.cpf,
        client_id=client_id,
    )

    if duplicated:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe outro cliente com este CPF neste tenant.",
        )

    client = repository.update_client(
        tenant_id=current_user.tenant_id,
        client_id=client_id,
        name=payload.name,
        cpf=payload.cpf,
        birth_date=payload.birth_date,
        phone=payload.phone,
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
        )

    return client