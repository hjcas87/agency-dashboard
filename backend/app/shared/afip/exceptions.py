"""Exception hierarchy for the AFIP/ARCA integration.

Consumers catch `AfipException` to handle every failure mode uniformly,
or one of the subclasses for narrower handling. The hierarchy is
deliberately flat — only the distinctions a caller can act on are
modeled.
"""


class AfipException(Exception):
    """Root of the integration's exception hierarchy."""


class AfipConfigurationError(AfipException):
    """Settings are missing or invalid (cert/key not readable, CUIT
    malformed, etc.). Raised at construction time of services that need
    the configuration to be complete."""


class AfipAuthenticationError(AfipException):
    """The WSAA login flow failed: CMS signing, certificate, or response
    parsing. Always means we couldn't get a usable Token+Sign pair."""


class AfipNetworkError(AfipException):
    """Transport-level failure: timeout, connection error, HTTP non-200,
    SOAP fault. Retried by the SoapClient up to MAX_RETRIES; if it
    surfaces here, the retries already exhausted."""


class AfipServiceError(AfipException):
    """ARCA returned a structured error inside a syntactically valid
    response. The `errors` attribute carries the list of `(code, message)`
    pairs. May be retryable depending on the code."""

    def __init__(self, message: str, errors: list[tuple[int, str]] | None = None) -> None:
        super().__init__(message)
        self.errors: list[tuple[int, str]] = errors or []


class AfipValidationError(AfipException):
    """Pre-AFIP local validation rejected the request. The payload never
    reached ARCA. The `errors` attribute carries the list of
    `(code_or_none, friendly_message)` pairs from the validation
    pipeline."""

    def __init__(
        self,
        message: str,
        errors: list[tuple[int | None, str]] | None = None,
    ) -> None:
        super().__init__(message)
        self.errors: list[tuple[int | None, str]] = errors or []


__all__ = [
    "AfipAuthenticationError",
    "AfipConfigurationError",
    "AfipException",
    "AfipNetworkError",
    "AfipServiceError",
    "AfipValidationError",
]
