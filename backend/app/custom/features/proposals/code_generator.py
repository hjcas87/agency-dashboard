"""
Proposal reference-code generator.

Codes follow a fixed `LLDDLL` pattern (two letters, two digits, two
letters — e.g. ``TY48YY``). Search space is 26**4 * 10**2 ≈ 45.7M,
which is plenty for a per-proposal counter; collisions are handled
by retrying against the database before insert.
"""
import secrets
import string

from sqlalchemy.orm import Session

from app.custom.features.proposals.models import Proposal

_LETTERS = string.ascii_uppercase
_DIGITS = string.digits

_MAX_ATTEMPTS = 16


def generate_code() -> str:
    """Return a random `LLDDLL` code (without the leading `#`)."""
    return (
        secrets.choice(_LETTERS)
        + secrets.choice(_LETTERS)
        + secrets.choice(_DIGITS)
        + secrets.choice(_DIGITS)
        + secrets.choice(_LETTERS)
        + secrets.choice(_LETTERS)
    )


def generate_unique_code(db: Session) -> str:
    """Generate a code that is not already taken in the proposals table.

    Raises:
        RuntimeError: if a unique value can't be found within
            ``_MAX_ATTEMPTS`` tries — extremely unlikely given the
            size of the search space.
    """
    for _ in range(_MAX_ATTEMPTS):
        candidate = generate_code()
        exists = db.query(Proposal.id).filter(Proposal.code == candidate).first()
        if exists is None:
            return candidate
    raise RuntimeError(
        "could not generate a unique proposal code after retries — investigate "
        "code-space exhaustion or a bug in the generator"
    )
