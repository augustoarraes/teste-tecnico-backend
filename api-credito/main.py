from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.endpoints import app as core_router
from auth.endpoints import app as auth_routet
from client.endpoints import app as clients_router
from proposal.endpoints import app as proposals_router
from webhook.endpoints import app as webhooks_router

app = FastAPI(title='API Crédito', description='Gerenciamento de Propostas de Crédito, develop by Augusto Arraes')

# Configurações de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lista de origens específicas: ["https://meusite.com"]
    allow_credentials=True,
    allow_methods=["*"],  # ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"], 
)

Instrumentator().instrument(app).expose(app, endpoint="/api/metrics", tags=["Default"]) # prometheus

app.include_router(core_router)
app.include_router(auth_routet)
app.include_router(clients_router)
app.include_router(proposals_router)
app.include_router(webhooks_router)

# http://127.0.0.1:8000/
# http://127.0.0.1:8000/docs