"""
Service layer for the Client feature.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.custom.features.clients.repository import ClientRepository
from app.custom.features.clients.schemas import ClientCreate, ClientUpdate, ClientResponse


class ClientService:
    """Service for client business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ClientRepository(db)

    def list_clients(self) -> list[ClientResponse]:
        """Return all clients."""
        clients = self.repository.get_all()
        return [ClientResponse.model_validate(c) for c in clients]

    def get_client(self, client_id: int) -> ClientResponse:
        """Return a single client by ID."""
        client = self.repository.get(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        return ClientResponse.model_validate(client)

    def create_client(self, data: ClientCreate) -> ClientResponse:
        """Create a new client."""
        existing = self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un cliente con ese email",
            )
        client = self.repository.create(data)
        return ClientResponse.model_validate(client)

    def update_client(self, client_id: int, data: ClientUpdate) -> ClientResponse:
        """Update an existing client."""
        client = self.repository.get(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        if data.email:
            existing = self.repository.get_by_email(data.email)
            if existing and existing.id != client_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un cliente con ese email",
                )
        updated = self.repository.update(client, data)
        return ClientResponse.model_validate(updated)

    def delete_client(self, client_id: int) -> None:
        """Delete a client by ID."""
        client = self.repository.get(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        self.repository.delete(client_id)
