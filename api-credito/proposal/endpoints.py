from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from core.repository import session
from auth.dependencies import get_current_user
from auth.dto import AuthenticatedUser
from proposal.dto import ProposalSimulateInput, ProposalOutput, ProposalListOutput
from proposal.service import simulate_proposal, list_proposals, get_proposal_by_id, submit_proposal, cancel_proposal


app = APIRouter(prefix="/api/proposals", tags=["Proposals"])


@app.post("/simulate", response_model=ProposalOutput, status_code=status.HTTP_202_ACCEPTED)
def simulate_proposal_endpoint(payload: ProposalSimulateInput, current_user: AuthenticatedUser = Depends(get_current_user),):
    return simulate_proposal(current_user, payload)


@app.get("", response_model=ProposalListOutput)
def list_proposals_endpoint(
    status: str | None = Query(default=None),
    type: str | None = Query(default=None),
    client_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return list_proposals(
        current_user=current_user,
        status=status,
        proposal_type=type,
        client_id=client_id,
        skip=skip,
        limit=limit,
    )


@app.get("/{proposal_id}", response_model=ProposalOutput)
def get_proposal_by_id_endpoint(
    proposal_id: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return get_proposal_by_id(
        current_user=current_user,
        proposal_id=proposal_id,
    )


@app.post("/{proposal_id}/submit", response_model=ProposalOutput, status_code=status.HTTP_200_OK,)
def submit_proposal_endpoint(proposal_id: UUID, current_user: AuthenticatedUser = Depends(get_current_user),):
    return submit_proposal(current_user=current_user, proposal_id=proposal_id,)


@app.post( "/{proposal_id}/cancel", response_model=ProposalOutput, status_code=status.HTTP_200_OK,)
def cancel_proposal_endpoint(proposal_id: UUID, current_user: AuthenticatedUser = Depends(get_current_user),):
    return cancel_proposal(current_user=current_user, proposal_id=proposal_id,)
