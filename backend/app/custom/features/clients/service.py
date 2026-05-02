"""
Service layer for the Client feature.
"""
import logging
from collections.abc import Callable

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.custom.features.clients.messages import (
    ERR_AFIP_LOOKUP_FAILED,
    ERR_AFIP_LOOKUP_NOT_FOUND,
    ERR_AFIP_NOT_CONFIGURED,
    ERR_DUPLICATE_EMAIL,
    ERR_NOT_FOUND,
)
from app.custom.features.clients.repository import ClientRepository
from app.custom.features.clients.schemas import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    CuitLookupResponse,
)
from app.shared.afip import (
    AfipConfigurationError,
    AfipException,
    AfipService,
    AfipTaxId,
    IvaCondition,
    TaxpayerInfo,
    TaxpayerRequest,
    TaxpayerTax,
    TaxStatus,
)

logger = logging.getLogger(__name__)


def _matches_tax(tax: TaxpayerTax, tax_id: AfipTaxId, expected: TaxStatus) -> bool:
    """Compare a `TaxpayerTax` row against a known (id, status) pair.
    Defensive about types — Padrón A5 ships ids as text."""
    if tax.tax_id is None or tax.status is None:
        return False
    try:
        return int(tax.tax_id) == int(tax_id) and tax.status == expected.value
    except (TypeError, ValueError):
        return False


def _is_active_monotributo(info: TaxpayerInfo) -> bool:
    """Active monotributo entry (id 20, status AC) in `monotributo.taxes`."""
    return any(
        _matches_tax(t, AfipTaxId.MONOTRIBUTO, TaxStatus.ACTIVE) for t in info.monotributo.taxes
    )


def _is_active_iva(info: TaxpayerInfo) -> bool:
    """IVA (id 30) status AC in the general regime — Responsable Inscripto."""
    return any(_matches_tax(t, AfipTaxId.IVA, TaxStatus.ACTIVE) for t in info.general_regime.taxes)


def _is_exempt_iva(info: TaxpayerInfo) -> bool:
    """IVA (id 30) status EX in the general regime — Exento."""
    return any(_matches_tax(t, AfipTaxId.IVA, TaxStatus.EXEMPT) for t in info.general_regime.taxes)


def _is_iva_not_reached(info: TaxpayerInfo) -> bool:
    """IVA NO ALCANZADO regime (id 34) status AC — No Alcanzado."""
    return any(
        _matches_tax(t, AfipTaxId.IVA_NOT_REACHED, TaxStatus.ACTIVE)
        for t in info.general_regime.taxes
    )


# Inference order matters: monotributo wins over IVA-active because a
# monotributista is monotributista regardless of any historical IVA
# entry. After that, the discriminating-vs-non-discriminating split
# follows the IvaCondition codes from app.shared.afip.enums. First
# matching predicate wins; if none match, the result is None and the
# operator picks manually in the UI.
_IVA_INFERENCE_RULES: tuple[tuple[Callable[[TaxpayerInfo], bool], IvaCondition], ...] = (
    (_is_active_monotributo, IvaCondition.MT),
    (_is_active_iva, IvaCondition.RI),
    (_is_exempt_iva, IvaCondition.EX),
    (_is_iva_not_reached, IvaCondition.NA),
)


def _infer_iva_condition(info: TaxpayerInfo) -> IvaCondition | None:
    """Run the inference rules in order; return the first matching
    `IvaCondition`. None means we could not decide."""
    for predicate, condition in _IVA_INFERENCE_RULES:
        if predicate(info):
            return condition
    return None


class ClientService:
    """Service for client business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ClientRepository(db)

    # ── CRUD ──────────────────────────────────────────────────────

    def list_clients(self) -> list[ClientResponse]:
        """Return all clients."""
        clients = self.repository.get_all()
        return [ClientResponse.model_validate(c) for c in clients]

    def get_client(self, client_id: int) -> ClientResponse:
        """Return a single client by ID."""
        client = self.repository.get(client_id)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
        return ClientResponse.model_validate(client)

    def create_client(self, data: ClientCreate) -> ClientResponse:
        """Create a new client."""
        existing = self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ERR_DUPLICATE_EMAIL)
        client = self.repository.create(data)
        return ClientResponse.model_validate(client)

    def update_client(self, client_id: int, data: ClientUpdate) -> ClientResponse:
        """Update an existing client."""
        client = self.repository.get(client_id)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
        if data.email:
            existing = self.repository.get_by_email(data.email)
            if existing and existing.id != client_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=ERR_DUPLICATE_EMAIL
                )
        updated = self.repository.update(client, data)
        return ClientResponse.model_validate(updated)

    def delete_client(self, client_id: int) -> None:
        """Delete a client by ID."""
        client = self.repository.get(client_id)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
        self.repository.delete(client_id)

    # ── AFIP lookup ───────────────────────────────────────────────

    def lookup_cuit_in_afip(self, cuit: str, afip: AfipService) -> CuitLookupResponse:
        """Query Padrón A5 by CUIT and shape the result for the client
        form's "Buscar en AFIP" button. Inference of `iva_condition` is
        conservative: only well-known (tax_id, status) pairs translate
        to a condition. Anything else returns None and lets the
        operator pick manually."""
        try:
            info = afip.get_taxpayer(TaxpayerRequest(cuit=cuit))
        except AfipConfigurationError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ERR_AFIP_NOT_CONFIGURED,
            ) from exc
        except AfipException as exc:
            message = str(exc)
            # ARCA's Padrón signals "unknown CUIT" with a SOAP fault
            # carrying "No existe persona con ese Id". Translate to a
            # 404 so the frontend can show a precise message.
            if "No existe persona" in message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ERR_AFIP_LOOKUP_NOT_FOUND,
                ) from exc
            logger.warning("AFIP lookup failed for CUIT %s: %s", cuit, message)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=ERR_AFIP_LOOKUP_FAILED.format(error=message),
            ) from exc

        return CuitLookupResponse(
            cuit=cuit,
            status=info.status,
            person_type=info.person_type,
            company_name=info.company_name,
            first_name=info.first_name,
            last_name=info.last_name,
            iva_condition=_infer_iva_condition(info),
            fiscal_address=info.fiscal_domicile.address,
            fiscal_locality=info.fiscal_domicile.locality,
            fiscal_province=info.fiscal_domicile.province,
            fiscal_postal_code=info.fiscal_domicile.postal_code,
        )
