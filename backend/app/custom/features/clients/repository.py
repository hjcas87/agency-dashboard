"""
Repository for Client data access.
"""
from sqlalchemy.orm import Session

from app.custom.features.clients.models import Client
from app.custom.features.clients.schemas import ClientCreate, ClientUpdate
from app.shared.repositories.base_repository import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Repository for Client CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(Client, db)

    def get_by_email(self, email: str) -> Client | None:
        """Get a client by email address."""
        return self.db.query(Client).filter(Client.email == email).first()

    def create(self, data: ClientCreate) -> Client:
        """Create a new client from a Pydantic schema. Uses model_dump
        so any new optional field (cuit / iva_condition / future) is
        persisted automatically without re-listing the columns."""
        db_client = Client(**data.model_dump())
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        return db_client

    def update(self, client: Client, data: ClientUpdate) -> Client:
        """Update an existing client. exclude_unset means fields that
        the consumer didn't pass (vs. explicitly passed `None`) are
        preserved as-is."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client
