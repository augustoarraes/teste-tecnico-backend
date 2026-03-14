import json
import time
from uuid import UUID

from core.repository import session

from integration.bank_client import simulate_credit, submit_credit_proposal
from integration.sqs_client import get_queue_url, get_sqs_client
from client import repository as clients_repository
from proposal import repository as proposals_repository


def process_simulate(tenant_id: UUID, proposal_id: UUID):
    proposal = proposals_repository.get_proposal_by_id(
        tenant_id=tenant_id,
        proposal_id=proposal_id,
    )
    if not proposal:
        return

    client = clients_repository.get_client_by_id(
        tenant_id=tenant_id,
        client_id=proposal.client_id,
    )
    if not client:
        raise ValueError("Cliente não encontrado para proposal")

    proposals_repository.mark_proposal_processing(
        tenant_id=tenant_id,
        proposal_id=proposal_id,
    )

    bank_response = simulate_credit(
        cpf=client.cpf,
        amount=proposal.amount,
        installments=proposal.installments,
    )

    protocol = bank_response.get("protocol")
    if not protocol:
        raise ValueError("Banco mock não retornou protocolo")

    proposals_repository.set_external_protocol(
        tenant_id=tenant_id,
        proposal_id=proposal_id,
        external_protocol=protocol,
    )


def process_submit(tenant_id: UUID, proposal_id: UUID):
    proposal = proposals_repository.get_proposal_by_id(
        tenant_id=tenant_id,
        proposal_id=proposal_id,
    )
    if not proposal:
        return

    client = clients_repository.get_client_by_id(
        tenant_id=tenant_id,
        client_id=proposal.client_id,
    )
    if not client:
        raise ValueError("Cliente não encontrado para proposal")

    if not proposal.external_protocol:
        raise ValueError("Proposal sem external_protocol")

    proposals_repository.mark_proposal_submitted(
        tenant_id=tenant_id,
        proposal_id=proposal_id,
        external_protocol=proposal.external_protocol,
    )

    submit_credit_proposal(
        protocol=proposal.external_protocol,
        client_data={
            "name": client.name,
            "cpf": client.cpf,
            "birth_date": str(client.birth_date),
            "phone": client.phone,
        },
    )


def handle_message(message_body: dict):
    action = message_body["action"]
    proposal_id = UUID(message_body["proposal_id"])
    tenant_id = UUID(message_body["tenant_id"])

    try:
        if action == "simulate":
            process_simulate(tenant_id, proposal_id)
        elif action == "submit":
            process_submit( tenant_id, proposal_id)
        else:
            raise ValueError(f"Ação inválida: {action}")
    finally:
        session.close()


def run():
    client = get_sqs_client()
    queue_url = get_queue_url()

    print(f"[SQS WORKER] started successfully - queue: {queue_url}")

    while True:
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            VisibilityTimeout=30,
        )

        messages = response.get("Messages", [])
        if not messages:
            time.sleep(1)
            continue

        for message in messages:
            receipt_handle = message["ReceiptHandle"]
            body = json.loads(message["Body"])

            try:
                handle_message(body)

                client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle,
                )
            except Exception as exc:
                print(f"Erro ao processar mensagem: {exc}")
                # não deleta: SQS vai reenviar depois
                continue


if __name__ == "__main__":
    run()