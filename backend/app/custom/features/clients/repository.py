"""
Repository for Client data access.
"""
from sqlalchemy.orm import Session

from app.custom.features.clients.models import Client, ClientEmail
from app.custom.features.clients.schemas import ClientCreate, ClientEmailIn, ClientUpdate
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
        persisted automatically without re-listing the columns. The
        `additional_emails` list is materialised into ClientEmail rows
        through the ORM relationship (cascade-all-delete-orphan keeps
        them in sync with the parent).
        """
        payload = data.model_dump(exclude={"additional_emails"})
        db_client = Client(**payload)
        db_client.additional_emails = _materialize_emails(data.additional_emails)
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        return db_client

    def update(self, client: Client, data: ClientUpdate) -> Client:
        """Update an existing client. exclude_unset means fields the
        consumer didn't pass (vs. explicitly passed `None`) are kept
        as-is. `additional_emails` is treated as a full replacement
        when included; passing `None` (or omitting it) leaves the
        existing list untouched.
        """
        update_data = data.model_dump(exclude_unset=True, exclude={"additional_emails"})
        for field, value in update_data.items():
            setattr(client, field, value)

        # Replace strategy keeps the form simple — operator submits
        # the full final list; orphan-delete cleans up removed rows.
        if "additional_emails" in data.model_fields_set and data.additional_emails is not None:
            client.additional_emails = _materialize_emails(data.additional_emails)

        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client


def _materialize_emails(payloads: list[ClientEmailIn]) -> list[ClientEmail]:
    """Translate a list of inbound payloads into ORM rows. Empty
    payloads are dropped; whitespace-only labels collapse to None so
    the DB stays clean."""
    rows: list[ClientEmail] = []
    for payload in payloads:
        label = payload.label.strip() if payload.label else None
        rows.append(ClientEmail(email=str(payload.email), label=label or None))
    return rows
