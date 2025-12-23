"""
Repository para el feature de Users.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.shared.repositories.base_repository import BaseRepository
from app.core.features.users.models import User


class UserRepository(BaseRepository[User]):
    """Repository para operaciones de User."""

    def __init__(self, db: Session):
        """Inicializa el repository."""
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por email.
        
        Args:
            email: Email del usuario
            
        Returns:
            User si existe, None si no
        """
        return self.db.query(self.model).filter(self.model.email == email).first()

    def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Obtiene usuarios activos.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de usuarios activos
        """
        return (
            self.db.query(self.model)
            .filter(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Busca usuarios por nombre o email.
        
        Args:
            query: Término de búsqueda
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de usuarios que coinciden
        """
        search_filter = or_(
            self.model.name.ilike(f"%{query}%"),
            self.model.email.ilike(f"%{query}%"),
        )
        return (
            self.db.query(self.model)
            .filter(search_filter)
            .offset(skip)
            .limit(limit)
            .all()
        )

