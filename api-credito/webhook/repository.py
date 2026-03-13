from sqlalchemy.orm import Session

from models.proposal import Proposal
from core.repository import session


def get_proposal_by_protocol(protocol: str) -> Proposal | None:
    return (
        session.query(Proposal)
        .filter(Proposal.external_protocol == protocol)
        .first()
    )


def save_bank_callback(*, proposal: Proposal, status: str, bank_response: dict,
    interest_rate=None, installment_value=None,):
    proposal.status = status
    proposal.bank_response = bank_response

    if interest_rate is not None:
        proposal.interest_rate = interest_rate

    if installment_value is not None:
        proposal.installment_value = installment_value

    session.commit()
    session.refresh(proposal)
    return proposal
