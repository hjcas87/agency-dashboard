"""
Centralized constants for user-facing messages, status values, and protocol strings.
User-facing messages are in Spanish. Internal/developer messages and protocol values in English.
No magic strings allowed — all values must come from this module.
"""

# ── Auth error messages (user-facing, Spanish) ─────────────────
AUTH_ERRORS = {
    "invalid_credentials": "El email o la contraseña son incorrectos",
    "invalid_token": "El token es inválido o ha expirado",
    "incorrect_password": "La contraseña actual es incorrecta",
    "email_already_exists": "El email ya está registrado",
    "user_not_found": "Usuario no encontrado",
    "inactive_user": "El usuario está inactivo",
    "user_exists_detail": "Ya existe un usuario con el email {email}",
    "user_not_found_detail": "No se encontró el usuario con ID {user_id}",
}

# ── Auth success messages (user-facing, Spanish) ───────────────
AUTH_SUCCESS = {
    "logged_out": "Sesión cerrada correctamente",
    "password_reset_sent": "Si el email existe, se envió un enlace de restablecimiento",
    "password_reset_done": "La contraseña fue restablecida correctamente",
    "password_changed": "La contraseña fue actualizada correctamente",
}

# ── N8N messages (internal, English) ───────────────────────────
N8N_MESSAGES = {
    "queued": "Workflow trigger queued successfully",
    "pending_desc": "Task is waiting to be processed",
    "unknown_error": "Unknown error",
}

# ── Status values (internal, English) ──────────────────────────
TASK_STATE = {
    "PENDING": "PENDING",
    "STARTED": "STARTED",
    "SUCCESS": "SUCCESS",
    "FAILURE": "FAILURE",
    "RETRY": "RETRY",
    "REVOKED": "REVOKED",
}

N8N_STATUS = {
    "SUCCESS": "success",
    "QUEUED": "queued",
}

HEALTH_STATUS = {
    "HEALTHY": "healthy",
    "DEGRADED": "degraded",
}

# ── Environment values (internal, English) ─────────────────────
ENVIRONMENT = {
    "DEVELOPMENT": "DEVELOPMENT",
    "PRODUCTION": "PRODUCTION",
}

# ── Email provider values (internal, English) ──────────────────
EMAIL_PROVIDER = {
    "SMTP": "smtp",
    "API": "api",
}

# ── Auth protocol strings (internal, English) ──────────────────
AUTH_SCHEME = "Bearer"
AUTHENTICATE_HEADER = "WWW-Authenticate"
TOKEN_TYPE = "bearer"

# ── JWT claim keys (internal, English) ─────────────────────────
JWT_CLAIM_SUB = "sub"

# ── Task result dict keys (internal, English) ──────────────────
TASK_RESULT_SUCCESS = "success"
TASK_RESULT_ERROR = "error"

# ── HTTP header keys (internal, English) ───────────────────────
HEADER_CONTENT_TYPE = "Content-Type"
CONTENT_TYPE_JSON = "application/json"
