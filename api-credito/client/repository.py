from sqlalchemy.orm import Session

from uuid import UUID

from models.client import Client
from core.repository import session


def get_client_by_cpf(tenant_id, cpf: str) -> Client | None:
    db = session
    return (
        db.query(Client)
        .filter(Client.tenant_id == tenant_id, Client.cpf == cpf)
        .first()
    )


def create_client(*, tenant_id, created_by, name: str, cpf: str, birth_date, phone: str | None,) -> Client:
    db = session
    client = Client(tenant_id=tenant_id, created_by=created_by, name=name, cpf=cpf, birth_date=birth_date, phone=phone,)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def list_clients(tenant_id, skip: int = 0, limit: int = 10):
    db = session
    return (
        db.query(Client)
        .filter(Client.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_client_by_id(tenant_id: UUID, client_id: UUID) -> Client | None:
    return (
        session.query(Client)
        .filter(
            Client.id == client_id,
            Client.tenant_id == tenant_id,
        )
        .first()
    )


def update_client(tenant_id: UUID, client_id: UUID, *, name: str, cpf: str, birth_date, phone: str | None,) -> Client | None:
    client = (
        session.query(Client)
        .filter(
            Client.id == client_id,
            Client.tenant_id == tenant_id,
        )
        .first()
    )

    if not client:
        return None

    client.name = name
    client.cpf = cpf
    client.birth_date = birth_date
    client.phone = phone

    session.commit()
    session.refresh(client)
    return client


def get_client_by_cpf_excluding_id(tenant_id: UUID, cpf: str, client_id: UUID,) -> Client | None:
    return (
        session.query(Client)
        .filter(
            Client.tenant_id == tenant_id,
            Client.cpf == cpf,
            Client.id != client_id,
        )
        .first()
    )
