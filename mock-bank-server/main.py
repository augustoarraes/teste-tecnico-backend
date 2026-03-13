"""
Mock Bank Server — Simula a API de um banco para o teste técnico.

Este servidor NÃO deve ser modificado pelo candidato.
Ele simula comportamentos reais: delays, webhooks e erros aleatórios.
"""

import asyncio
import uuid
import random
import logging
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────

import os

WEBHOOK_CALLBACK_URL = os.getenv("WEBHOOK_CALLBACK_URL", "http://host.docker.internal:8000/api/webhooks/bank-callback")
PROCESSING_DELAY_MIN = int(os.getenv("PROCESSING_DELAY_MIN", "2"))
PROCESSING_DELAY_MAX = int(os.getenv("PROCESSING_DELAY_MAX", "5"))
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.1"))  # 10% de erro

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-bank")

# ──────────────────────────────────────────────
# In-memory storage
# ──────────────────────────────────────────────

proposals_db: dict[str, dict] = {}

# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────

class SimulationRequest(BaseModel):
    cpf: str
    amount: float
    installments: int
    webhook_url: str | None = None  # override opcional


class InclusionRequest(BaseModel):
    protocol: str
    client_name: str
    client_cpf: str
    client_birth_date: str
    amount: float
    installments: int
    webhook_url: str | None = None


class CancelRequest(BaseModel):
    reason: str | None = "Cancelado pelo operador"


class ProtocolResponse(BaseModel):
    protocol: str
    message: str
    received_at: str


class StatusResponse(BaseModel):
    protocol: str
    status: str
    type: str
    data: dict
    created_at: str
    updated_at: str


# ──────────────────────────────────────────────
# Background processing
# ──────────────────────────────────────────────

async def process_simulation(protocol: str, request: SimulationRequest):
    """Simula o processamento do banco com delay e callback via webhook."""
    delay = random.uniform(PROCESSING_DELAY_MIN, PROCESSING_DELAY_MAX)
    logger.info(f"[{protocol}] Processando simulação... (delay: {delay:.1f}s)")
    await asyncio.sleep(delay)

    # Simular erro aleatório
    if random.random() < ERROR_RATE:
        logger.warning(f"[{protocol}] Simulação falhou (erro simulado)")
        callback_payload = {
            "protocol": protocol,
            "event": "simulation_completed",
            "status": "rejected",
            "data": {
                "reason": "Score insuficiente para aprovação",
                "score": random.randint(100, 350),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        proposals_db[protocol]["status"] = "rejected"
    else:
        interest_rate = round(random.uniform(1.2, 2.8), 2)
        installment_value = round(
            (request.amount * (1 + interest_rate / 100 * request.installments))
            / request.installments,
            2,
        )
        total_amount = round(installment_value * request.installments, 2)

        callback_payload = {
            "protocol": protocol,
            "event": "simulation_completed",
            "status": "approved",
            "data": {
                "interest_rate": interest_rate,
                "installment_value": installment_value,
                "total_amount": total_amount,
                "approved_amount": request.amount,
                "installments": request.installments,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        proposals_db[protocol]["status"] = "approved"
        proposals_db[protocol]["data"] = callback_payload["data"]

    proposals_db[protocol]["updated_at"] = datetime.utcnow().isoformat()

    # Enviar webhook callback
    webhook_url = request.webhook_url or WEBHOOK_CALLBACK_URL
    await send_webhook(webhook_url, callback_payload, protocol)


async def process_inclusion(protocol: str, request: InclusionRequest):
    """Simula a inclusão da proposta no banco."""
    delay = random.uniform(PROCESSING_DELAY_MIN, PROCESSING_DELAY_MAX)
    logger.info(f"[{protocol}] Processando inclusão... (delay: {delay:.1f}s)")
    await asyncio.sleep(delay)

    if random.random() < ERROR_RATE:
        logger.warning(f"[{protocol}] Inclusão falhou (erro simulado)")
        callback_payload = {
            "protocol": protocol,
            "event": "inclusion_completed",
            "status": "rejected",
            "data": {
                "reason": "Documentação pendente ou dados inconsistentes",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        proposals_db[protocol]["status"] = "rejected"
    else:
        contract_number = f"CTR-{random.randint(100000, 999999)}"
        callback_payload = {
            "protocol": protocol,
            "event": "inclusion_completed",
            "status": "approved",
            "data": {
                "contract_number": contract_number,
                "client_name": request.client_name,
                "amount": request.amount,
                "installments": request.installments,
                "first_due_date": "2025-02-15",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        proposals_db[protocol]["status"] = "approved"
        proposals_db[protocol]["data"] = callback_payload["data"]

    proposals_db[protocol]["updated_at"] = datetime.utcnow().isoformat()

    webhook_url = request.webhook_url or WEBHOOK_CALLBACK_URL
    await send_webhook(webhook_url, callback_payload, protocol)


async def send_webhook(url: str, payload: dict, protocol: str):
    """Envia o callback via HTTP POST com retry simples."""
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload)
                if response.status_code < 300:
                    logger.info(
                        f"[{protocol}] Webhook enviado com sucesso para {url} "
                        f"(status: {response.status_code})"
                    )
                    return
                logger.warning(
                    f"[{protocol}] Webhook retornou {response.status_code}, "
                    f"tentativa {attempt + 1}/3"
                )
        except Exception as e:
            logger.error(
                f"[{protocol}] Erro ao enviar webhook (tentativa {attempt + 1}/3): {e}"
            )
        await asyncio.sleep(2)

    logger.error(f"[{protocol}] Falha ao enviar webhook após 3 tentativas")


# ──────────────────────────────────────────────
# App
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Mock Bank Server iniciado")
    logger.info(f"Webhook callback URL: {WEBHOOK_CALLBACK_URL}")
    logger.info(f"Delay: {PROCESSING_DELAY_MIN}-{PROCESSING_DELAY_MAX}s")
    logger.info(f"Taxa de erro: {ERROR_RATE * 100}%")
    yield
    logger.info("Mock Bank Server encerrado")


app = FastAPI(
    title="Mock Bank Server",
    description="Servidor que simula a API de um banco para testes técnicos. NÃO MODIFIQUE.",
    version="1.0.0",
    lifespan=lifespan,
)


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "mock-bank-server",
        "proposals_in_memory": len(proposals_db),
    }


@app.post("/api/simular", response_model=ProtocolResponse, status_code=202)
async def simular(request: SimulationRequest):
    """
    Recebe pedido de simulação e processa de forma assíncrona.
    Retorna imediatamente com um protocolo.
    O resultado será enviado via webhook após o processamento.
    """
    protocol = f"MOCK-SIM-{uuid.uuid4().hex[:8].upper()}"

    proposals_db[protocol] = {
        "protocol": protocol,
        "type": "simulacao",
        "status": "processing",
        "cpf": request.cpf,
        "amount": request.amount,
        "installments": request.installments,
        "data": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    # Processar em background
    asyncio.create_task(process_simulation(protocol, request))

    logger.info(f"[{protocol}] Simulação recebida — CPF: {request.cpf}, Valor: R${request.amount}")

    return ProtocolResponse(
        protocol=protocol,
        message="Simulação recebida. O resultado será enviado via webhook.",
        received_at=datetime.utcnow().isoformat(),
    )


@app.post("/api/incluir", response_model=ProtocolResponse, status_code=202)
async def incluir(request: InclusionRequest):
    """
    Recebe pedido de inclusão de proposta e processa de forma assíncrona.
    O protocolo informado deve ser de uma simulação previamente aprovada.
    """
    if request.protocol not in proposals_db:
        raise HTTPException(
            status_code=404,
            detail=f"Protocolo {request.protocol} não encontrado",
        )

    original = proposals_db[request.protocol]
    if original["status"] != "approved":
        raise HTTPException(
            status_code=422,
            detail=f"Protocolo {request.protocol} não está aprovado (status: {original['status']})",
        )

    new_protocol = f"MOCK-INC-{uuid.uuid4().hex[:8].upper()}"

    proposals_db[new_protocol] = {
        "protocol": new_protocol,
        "type": "proposta",
        "status": "processing",
        "original_protocol": request.protocol,
        "client_name": request.client_name,
        "client_cpf": request.client_cpf,
        "amount": request.amount,
        "installments": request.installments,
        "data": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    asyncio.create_task(process_inclusion(new_protocol, request))

    logger.info(f"[{new_protocol}] Inclusão recebida — Cliente: {request.client_name}")

    return ProtocolResponse(
        protocol=new_protocol,
        message="Inclusão recebida. O resultado será enviado via webhook.",
        received_at=datetime.utcnow().isoformat(),
    )


@app.get("/api/consultar/{protocol}", response_model=StatusResponse)
async def consultar(protocol: str):
    """Consulta o status atual de um protocolo."""
    if protocol not in proposals_db:
        raise HTTPException(
            status_code=404,
            detail=f"Protocolo {protocol} não encontrado",
        )

    proposal = proposals_db[protocol]

    return StatusResponse(
        protocol=proposal["protocol"],
        status=proposal["status"],
        type=proposal["type"],
        data=proposal.get("data", {}),
        created_at=proposal["created_at"],
        updated_at=proposal["updated_at"],
    )


@app.post("/api/cancelar/{protocol}")
async def cancelar(protocol: str, request: CancelRequest):
    """Cancela uma proposta/simulação."""
    if protocol not in proposals_db:
        raise HTTPException(
            status_code=404,
            detail=f"Protocolo {protocol} não encontrado",
        )

    proposal = proposals_db[protocol]

    if proposal["status"] in ("cancelled", "rejected"):
        raise HTTPException(
            status_code=422,
            detail=f"Protocolo {protocol} já está {proposal['status']}",
        )

    proposals_db[protocol]["status"] = "cancelled"
    proposals_db[protocol]["updated_at"] = datetime.utcnow().isoformat()

    logger.info(f"[{protocol}] Cancelado — Motivo: {request.reason}")

    return {
        "protocol": protocol,
        "status": "cancelled",
        "message": "Proposta cancelada com sucesso",
    }
