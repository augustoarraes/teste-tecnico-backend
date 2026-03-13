from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ClientCreateInput(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    cpf: str = Field(..., min_length=11, max_length=11)
    birth_date: date
    phone: str | None = Field(default=None, max_length=20)


class ClientOutput(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    cpf: str
    birth_date: date
    phone: str | None
    created_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True


class ClientUpdateInput(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    cpf: str = Field(..., min_length=11, max_length=11)
    birth_date: date
    phone: str | None = Field(default=None, max_length=20)
