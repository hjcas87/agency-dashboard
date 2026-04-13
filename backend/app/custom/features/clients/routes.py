"""
Routes for the Client feature.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.custom.features.clients.service import ClientService
from app.custom.features.clients.schemas import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/clients", tags=["Custom: Clients"])


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    """Dependency to obtain the client service."""
    return ClientService(db)


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
