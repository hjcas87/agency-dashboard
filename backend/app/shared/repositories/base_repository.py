"""
Repositorio base con operaciones CRUD comunes.
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repositorio base con operaciones CRUD comunes."""

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Inicializa el repositorio.
        
        Args:
            model: Clase del modelo SQLAlchemy
            db: Sesión de base de datos
        """
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        """Obtiene un registro por ID."""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error getting {self.model.__name__}: {str(e)}")

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> List[ModelType]:
        """Obtiene múltiples registros con paginación."""
        try:
            query = self.db.query(self.model)

            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)

            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error getting all {self.model.__name__}: {str(e)}")

    def create(self, obj_in: dict) -> ModelType:
        """Crea un nuevo registro."""
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error creating {self.model.__name__}: {str(e)}")

    def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        """Actualiza un registro."""
        try:
            db_obj = self.get(id)
            if not db_obj:
                return None

            for key, value in obj_in.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)

            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error updating {self.model.__name__}: {str(e)}")

    def delete(self, id: int) -> bool:
        """Elimina un registro."""
        try:
            db_obj = self.get(id)
            if not db_obj:
                return False

            self.db.delete(db_obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error deleting {self.model.__name__}: {str(e)}")

    def count(self, filters: Optional[dict] = None) -> int:
        """Cuenta registros."""
        try:
            query = self.db.query(self.model)

            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)

            return query.count()
        except SQLAlchemyError as e:
            raise Exception(f"Error counting {self.model.__name__}: {str(e)}")

