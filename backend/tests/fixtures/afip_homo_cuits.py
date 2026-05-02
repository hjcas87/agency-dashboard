"""CUITs registered in the AFIP/ARCA *homologación* environment.

Homologación has its own universe of taxpayers — production CUITs do
not exist there and vice versa. These are the test CUITs ARCA exposes
for development, grouped by category so tests can pick whichever shape
matches the scenario under test (Monotributo / Persona Física /
Persona Jurídica).

Single source of truth: imported by integration tests *and* by the
homo smoke-test script (`backend/scripts/afip_homo_smoke_test.py`).
Update here only — never duplicate.
"""
from typing import Final

# CUIT categories present in homologación.
HOMO_CUITS_MONOTRIBUTO: Final[tuple[str, ...]] = (
    "20431203422",
    "20700538673",
    "27139277908",
    "24766312108",
    "20313369154",
)

HOMO_CUITS_PERSONA_FISICA: Final[tuple[str, ...]] = (
    "20907332064",
    "27242151459",
    "24952244155",
    "20020833042",
    "27828940541",
    "20483704276",
    "24491994602",
)

HOMO_CUITS_PERSONA_JURIDICA: Final[tuple[str, ...]] = (
    "33561767209",
    "30243719581",
    "30229554324",
    "30392474036",
    "30643411861",
)

# Convenience aggregate.
ALL_HOMO_CUITS: Final[tuple[str, ...]] = (
    *HOMO_CUITS_MONOTRIBUTO,
    *HOMO_CUITS_PERSONA_FISICA,
    *HOMO_CUITS_PERSONA_JURIDICA,
)


# One representative per category — useful for the smoke script when a
# single example is enough to prove connectivity.
SAMPLE_MONOTRIBUTO: Final[str] = HOMO_CUITS_MONOTRIBUTO[0]
SAMPLE_PERSONA_FISICA: Final[str] = HOMO_CUITS_PERSONA_FISICA[0]
SAMPLE_PERSONA_JURIDICA: Final[str] = HOMO_CUITS_PERSONA_JURIDICA[0]


__all__ = [
    "ALL_HOMO_CUITS",
    "HOMO_CUITS_MONOTRIBUTO",
    "HOMO_CUITS_PERSONA_FISICA",
    "HOMO_CUITS_PERSONA_JURIDICA",
    "SAMPLE_MONOTRIBUTO",
    "SAMPLE_PERSONA_FISICA",
    "SAMPLE_PERSONA_JURIDICA",
]
