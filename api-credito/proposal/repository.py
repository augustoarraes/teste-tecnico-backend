from uuid import UUID
from sqlalchemy.orm import Session

from models.proposal import Proposal
from core.repository import session


def create_simulation_proposal(*, tenant_id: UUID, client_id: UUID, amount, installments: int, created_by: UUID,) -> Proposal:
    proposal = Proposal(
        tenant_id=tenant_id,
        client_id=client_id,
        type="simulacao",
        amount=amount,
        installments=installments,
        status="pending",
        created_by=created_by,
    )
    session.add(proposal)
    session.commit()
    session.refresh(proposal)
    return proposal


def list_proposals(*, tenant_id: UUID, status: str | None = None, proposal_type: str | None = None,
    client_id: UUID | None = None, skip: int = 0, limit: int = 10,):
    query = session.query(Proposal).filter(Proposal.tenant_id == tenant_id)

    if status:
        query = query.filter(Proposal.status == status)

    if proposal_type:
        query = query.filter(Proposal.type == proposal_type)

    if client_id:
        query = query.filter(Proposal.client_id == client_id)

    total = query.count()

    items = (
        query.order_by(Proposal.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total


def get_proposal_by_id(*, tenant_id: UUID, proposal_id: UUID,) -> Proposal | None:
    return (
        session.query(Proposal)
        .filter(
            Proposal.id == proposal_id,
            Proposal.tenant_id == tenant_id,
        )
        .first()
    )


def submit_proposal(*, tenant_id: UUID, proposal_id: UUID,) -> Proposal | None:
    proposal = (
        session.query(Proposal)
        .filter(
            Proposal.id == proposal_id,
            Proposal.tenant_id == tenant_id,
        )
        .first()
    )

    if not proposal:
        return None

    proposal.type = "proposta"
    proposal.status = "submitted"

    session.commit()
    session.refresh(proposal)
    return proposal
