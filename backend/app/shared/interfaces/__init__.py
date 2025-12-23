"""
Interfaces y contratos para servicios compartidos.
"""
from app.shared.interfaces.message_broker import IMessageBroker
from app.shared.interfaces.external_service import IExternalService

__all__ = ["IMessageBroker", "IExternalService"]

