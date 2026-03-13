from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from uuid import UUID

from client import repository as clients_repository
from proposal import repository as proposals_repository
from proposal.dto import ProposalSimulateInput, ProposalListOutput


def simulate_proposal(current_user, payload: ProposalSimulateInput):
    client = clients_repository.get_client_by_id(
        tenant_id=current_user.tenant_id,
        client_id=payload.client_id,
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
        )

    proposal = proposals_repository.create_simulation_proposal(
        tenant_id=current_user.tenant_id,
        client_id=payload.client_id,
        amount=payload.amount,
        installments=payload.installments,
        created_by=current_user.user_id,
    )

    return proposal


def list_proposals(current_user, *, status: str | None = None, proposal_type: str | None = None,
    client_id: UUID | None = None, skip: int = 0, limit: int = 10,) -> ProposalListOutput:
    items, total = proposals_repository.list_proposals(
        tenant_id=current_user.tenant_id,
        status=status,
        proposal_type=proposal_type,
        client_id=client_id,
        skip=skip,
        limit=limit,
    )

    return ProposalListOutput(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
    

def get_proposal_by_id(current_user, proposal_id: UUID,):
    proposal = proposals_repository.get_proposal_by_id(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal_id,
    )

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada.",
        )

    return proposal


def submit_proposal(current_user, proposal_id: UUID,):
    proposal = proposals_repository.get_proposal_by_id(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal_id,
    )

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada.",
        )

    if proposal.status != "simulated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A proposta precisa estar com status 'simulated' para ser enviada.",
        )

    return proposals_repository.submit_proposal(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal_id,
    )
