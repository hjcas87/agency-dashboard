"""
Routes para el feature de Users.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.features.users.repository import UserRepository
from app.core.features.users.schemas import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.core.features.users.service import UserService
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Core: Users"])


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency para obtener el repository de usuarios."""
    return UserRepository(db)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Dependency para obtener el service de usuarios."""
    return UserService(user_repository)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """
    Crea un nuevo usuario.
    """
    user = service.create_user(user_data)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    """
    Obtiene un usuario por ID.
    """
    user = service.get_user(user_id)
    return user


@router.get("", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    active_only: bool = Query(False, description="Solo usuarios activos"),
    search: Optional[str] = Query(None, description="Búsqueda por nombre o email"),
    service: UserService = Depends(get_user_service),
):
    """
    Obtiene lista de usuarios con paginación.
    """
    users, total = service.get_users(
        skip=skip,
        limit=limit,
        active_only=active_only,
        search=search,
    )

    return UserListResponse(
        items=users,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    """
    Actualiza un usuario.
    """
    user = service.update_user(user_id, user_data)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    """
    Elimina un usuario.
    """
    service.delete_user(user_id)
    return None
