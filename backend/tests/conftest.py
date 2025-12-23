"""
Pytest configuration y fixtures compartidas.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.config import settings


# Database de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Crea una sesión de base de datos para tests.
    Crea las tablas antes de cada test y las elimina después.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Crea un cliente de test de FastAPI.
    Override de get_db para usar la sesión de test.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def user_factory(db_session: Session):
    """
    Fixture para UserFactory.
    """
    def _create_user(**kwargs):
        return UserFactory.create(db_session, **kwargs)
    
    def _create_batch(count: int, **kwargs):
        return UserFactory.create_batch(db_session, count, **kwargs)
    
    return type('UserFactoryFixture', (), {
        'create': _create_user,
        'create_batch': _create_batch,
    })()


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock de settings para tests."""
    test_settings = {
        "SECRET_KEY": "test-secret-key",
        "ENVIRONMENT": "test",
        "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
        "N8N_BASE_URL": "http://localhost:5678",
    }
    
    for key, value in test_settings.items():
        monkeypatch.setattr(f"app.config.settings.{key}", value)
    
    return test_settings

