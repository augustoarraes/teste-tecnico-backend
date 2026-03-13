from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from webhook import repository
from webhook.dto import BankCallbackInput


def map_bank_callback_status(event: str, bank_status: str) -> str:
    bank_status = bank_status.lower()
    event = event.lower()

    if event == "simulation_completed":
        if bank_status == "approved":
            return "simulated"
        return "simulation_failed"

    if event == "proposal_completed":
        if bank_status == "approved":
            return "approved"
        if bank_status == "rejected":
            return "rejected"

    if event == "proposal_cancelled":
        return "cancelled"

    return "processing"


def process_bank_callback(payload: BankCallbackInput):
    proposal = repository.get_proposal_by_protocol(payload.protocol)

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada para o protocolo informado.",
        )

    mapped_status = map_bank_callback_status(payload.event, payload.status)

    interest_rate = payload.data.interest_rate if payload.data else None
    installment_value = payload.data.installment_value if payload.data else None

    return repository.save_bank_callback(
        proposal=proposal,
        status=mapped_status,
        bank_response=payload.model_dump(),
        interest_rate=interest_rate,
        installment_value=installment_value,
    )
