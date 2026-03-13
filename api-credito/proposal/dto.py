from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProposalSimulateInput(BaseModel):
    client_id: UUID
    amount: Decimal = Field(..., gt=0)
    installments: int = Field(..., gt=0)


class ProposalOutput(BaseModel):
    id: UUID
    tenant_id: UUID
    client_id: UUID
    external_protocol: str | None
    type: str
    amount: Decimal
    installments: int
    interest_rate: Decimal | None
    installment_value: Decimal | None
    status: str
    bank_response: dict | None
    created_at: datetime
    updated_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True


class ProposalListOutput(BaseModel):
    items: list[ProposalOutput]
    total: int
    skip: int
    limit: int
