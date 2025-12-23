"""
Factory para crear usuarios de test.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.features.users.models import User
from app.core.features.users.repository import UserRepository


class UserFactory:
    """Factory para crear usuarios de test."""

    @staticmethod
    def create(
        db: Session,
        email: Optional[str] = None,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        **kwargs: Any,
    ) -> User:
        """
        Crea un usuario de test.
        
        Args:
            db: Sesión de base de datos
            email: Email del usuario (generado si no se proporciona)
            name: Nombre del usuario (generado si no se proporciona)
            is_active: Si el usuario está activo
            **kwargs: Otros campos del usuario
            
        Returns:
            Usuario creado
        """
        import random
        import string

        # Generar datos por defecto si no se proporcionan
        if email is None:
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            email = f"test_{random_suffix}@example.com"
        
        if name is None:
            name = f"Test User {random.randint(1000, 9999)}"
        
        if is_active is None:
            is_active = True

        # Crear usuario
        user_data = {
            "email": email,
            "name": name,
            "is_active": is_active,
            **kwargs,
        }

        repository = UserRepository(db)
        return repository.create(user_data)

    @staticmethod
    def create_batch(
        db: Session,
        count: int,
        **kwargs: Any,
    ) -> list[User]:
        """
        Crea múltiples usuarios de test.
        
        Args:
            db: Sesión de base de datos
            count: Número de usuarios a crear
            **kwargs: Campos comunes para todos los usuarios
            
        Returns:
            Lista de usuarios creados
        """
        users = []
        for i in range(count):
            user = UserFactory.create(
                db,
                email=f"test_user_{i}@example.com",
                name=f"Test User {i}",
                **kwargs,
            )
            users.append(user)
        return users

