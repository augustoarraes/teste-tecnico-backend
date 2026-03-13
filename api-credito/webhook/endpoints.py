from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.repository import session
from webhook.dto import BankCallbackInput
from webhook.service import process_bank_callback


app = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@app.post("/bank-callback", status_code=status.HTTP_200_OK)
def bank_callback_endpoint(payload: BankCallbackInput,):
    proposal = process_bank_callback(payload)

    return {
        "message": "Webhook processado com sucesso.",
        "proposal_id": str(proposal.id),
        "status": proposal.status,
    }
