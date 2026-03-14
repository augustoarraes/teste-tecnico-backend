from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from uuid import UUID

from client import repository as clients_repository
from proposal import repository as proposals_repository
from proposal.dto import ProposalSimulateInput, ProposalListOutput

from integration.bank_client import simulate_credit, submit_credit_proposal, get_credit_proposal_status, cancel_credit_proposal
from integration.sqs_client import send_message


"""def simulate_proposal(current_user, payload: ProposalSimulateInput):
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

    return proposal"""


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

    """try:
        bank_response = simulate_credit(
            cpf=client.cpf,
            amount=payload.amount,
            installments=payload.installments,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com o banco mock: {str(e)}",
        )

    protocol = bank_response.get("protocol")
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Banco mock não retornou protocolo.",
        )

    proposal = proposals_repository.set_proposal_processing(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal.id,
        external_protocol=protocol,
    )"""

    # SQS
    send_message(
        {
            "action": "simulate",
            "proposal_id": str(proposal.id),
            "tenant_id": str(current_user.tenant_id),
        }
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
    

"""def get_proposal_by_id(current_user, proposal_id: UUID,):
    proposal = proposals_repository.get_proposal_by_id(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal_id,
    )

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada.",
        )

    return proposal"""


def map_bank_status(bank_status: str) -> str:
    value = bank_status.lower()

    if value == "approved":
        return "approved"

    if value == "rejected":
        return "rejected"

    if value == "cancelled":
        return "cancelled"

    if value == "simulated":
        return "simulated"

    return "processing"

TRANSIENT_STATUS = {"pending", "processing", "submitted"}


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

    if (
        proposal.external_protocol
        and proposal.status in TRANSIENT_STATUS
    ):
        try:
            bank_response = get_credit_proposal_status(
                proposal.external_protocol
            )

            bank_status = bank_response.get("status")

            mapped_status = map_bank_status(bank_status)

            proposal = proposals_repository.update_proposal_bank_status(
                tenant_id=current_user.tenant_id,
                proposal_id=proposal.id,
                status=mapped_status,
                bank_response=bank_response,
            )

        except Exception:
            pass  # fallback silencioso

    return proposal

def _map_consult_status(bank_status: str) -> str:
    value = bank_status.lower()

    if value in ("approved", "aprovada"):
        return "approved"
    if value in ("rejected", "reprovada"):
        return "rejected"
    if value in ("cancelled", "cancelada"):
        return "cancelled"
    if value in ("processing", "processing_simulation", "processing_proposal"):
        return "processing"
    if value in ("simulated",):
        return "simulated"

    return "processing"

def sync_proposal_status(current_user, proposal_id: UUID,):
    proposal = proposals_repository.get_proposal_by_id(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal_id,
    )

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada.",
        )

    if not proposal.external_protocol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proposta sem protocolo externo.",
        )

    try:
        bank_response = get_credit_proposal_status(proposal.external_protocol)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao consultar banco mock: {str(e)}",
        )

    mapped_status = _map_consult_status(bank_response.get("status", "processing"))

    return proposals_repository.update_proposal_bank_status(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal.id,
        status=mapped_status,
        bank_response=bank_response,
    )


"""def submit_proposal(current_user, proposal_id: UUID,):
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
    )"""


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

    client = clients_repository.get_client_by_id(
        tenant_id=current_user.tenant_id,
        client_id=proposal.client_id,
    )

    """if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
        )

    if not proposal.external_protocol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A proposta não possui protocolo externo da simulação.",
        )

    client_data = {
        "name": client.name,
        "cpf": client.cpf,
        "birth_date": str(client.birth_date),
        "phone": client.phone,
    }

    try:
        bank_response = submit_credit_proposal(
            protocol=proposal.external_protocol,
            client_data=client_data,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com o banco mock: {str(e)}",
        )

    protocol = bank_response.get("protocol", proposal.external_protocol)

    updated_proposal = proposals_repository.mark_proposal_submitted(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal.id,
        external_protocol=protocol,
    )"""

    send_message(
        {
            "action": "submit",
            "proposal_id": str(proposal.id),
            "tenant_id": str(current_user.tenant_id),
        }
    )

    return proposal


def cancel_proposal(current_user, proposal_id: UUID,):
    proposal = proposals_repository.get_proposal_by_id(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal_id,
    )

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada.",
        )

    if not proposal.external_protocol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proposta sem protocolo externo.",
        )

    try:
        bank_response = cancel_credit_proposal(proposal.external_protocol)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao cancelar no banco mock: {str(e)}",
        )

    return proposals_repository.update_proposal_bank_status(
        tenant_id=current_user.tenant_id,
        proposal_id=proposal.id,
        status="cancelled",
        bank_response=bank_response,
    )
