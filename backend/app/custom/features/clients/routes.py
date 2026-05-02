"""
Routes for the Client feature.
"""
from collections.abc import Generator

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.custom.features.clients.schemas import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    CuitLookupResponse,
)
from app.custom.features.clients.service import ClientService
from app.database import get_db
from app.shared.afip import AfipService, get_afip_service

router = APIRouter(prefix="/clients", tags=["Custom: Clients"])


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    """Dependency to obtain the client service."""
    return ClientService(db)


def afip_dependency(db: Session = Depends(get_db)) -> Generator[AfipService, None, None]:
    """Wrap `get_afip_service` so FastAPI can inject the request-scoped
    AfipService into routes that need to query Padrón A5."""
    yield from get_afip_service(db)


@router.get("/", response_model=list[ClientResponse])
def list_clients(service: ClientService = Depends(get_client_service)) -> list[ClientResponse]:
    """Return all clients."""
    return service.list_clients()


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    """Return a single client by ID."""
    return service.get_client(client_id)


@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    data: ClientCreate,
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    """Create a new client."""
    return service.create_client(data)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    data: ClientUpdate,
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    """Update an existing client."""
    return service.update_client(client_id, data)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    service: ClientService = Depends(get_client_service),
) -> None:
    """Delete a client."""
    return service.delete_client(client_id)


@router.get("/lookup-cuit/{cuit}", response_model=CuitLookupResponse)
def lookup_cuit(
    cuit: str,
    service: ClientService = Depends(get_client_service),
    afip: AfipService = Depends(afip_dependency),
) -> CuitLookupResponse:
    """Query AFIP's Padrón A5 by CUIT and return a payload the client
    form can use to autocomplete (company / name / inferred IVA
    condition / fiscal address). Always optional: clients without a
    CUIT keep working unchanged."""
    return service.lookup_cuit_in_afip(cuit, afip)
