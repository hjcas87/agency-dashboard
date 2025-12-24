"""
Dependencies para autenticación.
"""
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.features.users.models import User
from app.core.features.users.repository import UserRepository
from app.config import settings

security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency para obtener el usuario actual autenticado.
    
    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get(int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency para obtener usuario activo.
    
    Args:
        current_user: Usuario actual
        
    Returns:
        Usuario activo
    """
    return current_user


# Optional dependency para rutas que pueden ser públicas o privadas
def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    db: Session = Depends(get_db),
) -> User | None:
    """
    Dependency opcional para obtener usuario si está autenticado.
    
    Args:
        credentials: Credenciales HTTP Bearer (opcional)
        db: Sesión de base de datos
        
    Returns:
        Usuario si está autenticado, None si no
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

