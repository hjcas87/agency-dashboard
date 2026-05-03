"""
Service layer para el feature de Users.
"""
from typing import Optional

from fastapi import HTTPException, status

from app.core.features.users.models import User
from app.core.features.users.repository import UserRepository
from app.core.features.users.schemas import UserCreate, UserUpdate


class UserService:
    """Service para manejar lógica de negocio de Users."""

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa el service.

        Args:
            user_repository: Instancia del repository de usuarios
        """
        self.user_repository = user_repository

    def create_user(self, user_data: UserCreate) -> User:
        """
        Crea un nuevo usuario.

        Args:
            user_data: Datos del usuario a crear

        Returns:
            Usuario creado

        Raises:
            HTTPException: Si el email ya existe
        """
        # Verificar si el email ya existe
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {user_data.email} already exists",
            )

        # Crear usuario
        user_dict = user_data.model_dump()
        return self.user_repository.create(user_dict)

    def get_user(self, user_id: int) -> User:
        """
        Obtiene un usuario por ID.

        Args:
            user_id: ID del usuario

        Returns:
            Usuario encontrado

        Raises:
            HTTPException: Si el usuario no existe
        """
        user = self.user_repository.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return user

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        search: Optional[str] = None,
    ) -> tuple[list[User], int]:
        """
        Obtiene lista de usuarios.

        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            active_only: Si solo devolver usuarios activos
            search: Término de búsqueda opcional

        Returns:
            Tupla con (lista de usuarios, total)
        """
        if search:
            users = self.user_repository.search(query=search, skip=skip, limit=limit)
            total = self.user_repository.count(filters={"name": search})  # Aproximado
        elif active_only:
            users = self.user_repository.get_active_users(skip=skip, limit=limit)
            total = self.user_repository.count(filters={"is_active": True})
        else:
            users = self.user_repository.get_all(skip=skip, limit=limit)
            total = self.user_repository.count()

        return users, total

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Actualiza un usuario.

        Args:
            user_id: ID del usuario
            user_data: Datos a actualizar

        Returns:
            Usuario actualizado

        Raises:
            HTTPException: Si el usuario no existe o el email ya está en uso
        """
        # Verificar que el usuario existe
        user = self.get_user(user_id)

        # Verificar si el email está siendo actualizado y ya existe
        if user_data.email and user_data.email != user.email:
            existing_user = self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email {user_data.email} already exists",
                )

        # Actualizar
        update_dict = user_data.model_dump(exclude_unset=True)
        return self.user_repository.update(user_id, update_dict)

    def delete_user(self, user_id: int) -> bool:
        """
        Elimina un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            True si se eliminó exitosamente

        Raises:
            HTTPException: Si el usuario no existe
        """
        # Verificar que el usuario existe
        self.get_user(user_id)

        # Eliminar
        return self.user_repository.delete(user_id)
