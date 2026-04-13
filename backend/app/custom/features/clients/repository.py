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
        """Create a new client from schema."""
        db_client = Client(
            name=data.name,
            company=data.company,
            email=data.email,
            phone=data.phone,
        )
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        return db_client

    def update(self, client: Client, data: ClientUpdate) -> Client:
        """Update an existing client."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client
