from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from typing import List
from uuid import UUID

from core.repository import session
from auth.dependencies import get_current_user
from auth.dto import AuthenticatedUser
from client.dto import ClientCreateInput, ClientOutput, ClientUpdateInput
from client.service import create_client, list_clients, get_client_by_id, update_client


app = APIRouter(prefix="/api/clients", tags=["Clients"])


@app.post("", response_model=ClientOutput, status_code=201)
def create_client_endpoint(payload: ClientCreateInput, current_user: AuthenticatedUser = Depends(get_current_user),):
    return create_client(current_user, payload)


@app.get("", response_model=List[ClientOutput])
def list_clients_endpoint(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),):
    return list_clients(current_user, skip, limit)


@app.get("/{client_id}", response_model=ClientOutput)
def get_client_by_id_endpoint(client_id: UUID, current_user: AuthenticatedUser = Depends(get_current_user),):
    return get_client_by_id(current_user, client_id)


@app.put("/{client_id}", response_model=ClientOutput)
def update_client_endpoint(client_id: UUID, payload: ClientUpdateInput, current_user: AuthenticatedUser = Depends(get_current_user),):
    return update_client(current_user, client_id, payload)
