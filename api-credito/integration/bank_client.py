import httpx

from core.config import settings


def simulate_credit(*, cpf: str, amount, installments: int) -> dict:
    url = f"{settings.MOCK_BANK_BASE_URL}/api/simular"

    payload = {
        "cpf": cpf,
        "amount": float(amount),
        "installments": installments,
        "webhook_url": settings.WEBHOOK_CALLBACK_URL,
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    

def submit_credit_proposal(*, protocol: str, client_data: dict,) -> dict:
    url = f"{settings.MOCK_BANK_BASE_URL}/api/incluir"

    payload = {
        "protocol": protocol,
        "client_data": client_data,
        "webhook_url": settings.WEBHOOK_CALLBACK_URL,
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    

def get_credit_proposal_status(protocol: str) -> dict:
    url = f"{settings.MOCK_BANK_BASE_URL}/api/consultar/{protocol}"

    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()


def cancel_credit_proposal(protocol: str) -> dict:
    url = f"{settings.MOCK_BANK_BASE_URL}/api/cancelar/{protocol}"

    with httpx.Client(timeout=10.0) as client:
        response = client.post(url)
        response.raise_for_status()
        return response.json()