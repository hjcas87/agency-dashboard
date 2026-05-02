"""WSAA authentication (LoginCms) and TA cache.

`AuthService` is the public entrypoint of this sub-package. The
implementation lives in `ticket.py`; CMS signing in `cms.py`; the
single-flight refresh lock in `locking.py`.
"""
from app.shared.afip.auth.ticket import AuthService

__all__ = ["AuthService"]
