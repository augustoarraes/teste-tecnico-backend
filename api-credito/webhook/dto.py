from decimal import Decimal
from pydantic import BaseModel


class BankCallbackDataInput(BaseModel):
    interest_rate: Decimal | None = None
    installment_value: Decimal | None = None
    total_amount: Decimal | None = None
    approved_amount: Decimal | None = None


class BankCallbackInput(BaseModel):
    protocol: str
    event: str
    status: str
    data: BankCallbackDataInput | None = None