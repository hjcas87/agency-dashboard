"""
Interfaces y contratos para servicios compartidos.
"""
from app.shared.interfaces.email_service import IEmailService
from app.shared.interfaces.external_service import IExternalService
from app.shared.interfaces.message_broker import IMessageBroker

__all__ = ["IEmailService", "IMessageBroker", "IExternalService"]

