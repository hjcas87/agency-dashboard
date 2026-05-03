"""
Client-facing text formats for a proposal — filename, recipient label,
and the email subject + body templates that go out when the quote is
shared.

All strings live here so the wording stays consistent across the PDF,
the download filename, and the email-send feature.
"""
from xml.sax.saxutils import escape

from app.custom.features.clients.models import Client
from app.custom.features.proposals.models import Proposal

# Always copied on outbound proposal emails. Hard-coded for now —
# per-tenant customization can move this behind settings the day a
# second fork needs different addresses.
PROPOSAL_EMAIL_CC: tuple[str, ...] = (
    "hernan.mendrisoftware@gmail.com",
    "leandro.carriego@mendrisoftware.com",
)


_CODE_REFERENCE_PREFIX = "Código de referencia:"


def format_recipient_label(client: Client | None) -> str | None:
    """Build the line printed under "PREPARADO PARA:" on the cover.

    Returns None when there's no client to address — the caller decides
    whether to render the recipient block at all.
    """
    if client is None:
        return None

    name = (client.name or "").strip()
    company = (client.company or "").strip()
    if name and company:
        return f"{name} - {company}"
    return name or company or None


def _company_or_name_for_filename(client: Client | None) -> str:
    """Pick the human-readable identifier the filename uses to refer
    to the client. Prefers the company name (matches how the team
    files quotes), falls back to the contact name, then to a generic
    "CLIENTE" placeholder so the slot is always populated.
    """
    if client is None:
        return "CLIENTE"
    return (client.company or client.name or "CLIENTE").strip().upper() or "CLIENTE"


FILENAME_SUFFIX = "COTIZACION - DESARROLLO DE SOFTWARE"


def format_filename(proposal: Proposal, client: Client | None) -> str:
    """Canonical filename for a quote PDF — also used as the email
    subject prefix in `format_email_subject`.

    Pattern: ``dd-mm-yy - EMPRESA #CODE - COTIZACION - DESARROLLO DE SOFTWARE``
    """
    date_str = proposal.issue_date.strftime("%d-%m-%y")
    company = _company_or_name_for_filename(client)
    return f"{date_str} - {company} #{proposal.code} - {FILENAME_SUFFIX}"


def format_email_subject(proposal: Proposal, client: Client | None) -> str:
    """Email subject pattern: ``EMPRESA - COTIZACION #CODE``."""
    company = _company_or_name_for_filename(client)
    return f"{company} - COTIZACION #{proposal.code}"


_EMAIL_BODY_TEMPLATE = """\
Hola {greeting_name},

Te escribo para enviarte la cotización correspondiente al desarrollo solicitado.

Código de referencia: #{code}

Agradezco de antemano la confirmación de recepción y estoy a disposición ante cualquier duda que tengas.

¡Muchas gracias!
Saludos"""


def format_email_body(proposal: Proposal, client: Client | None) -> str:
    """Email body pattern. The greeting uses the contact's first name
    when available; otherwise it falls back to the company name and,
    if there's no client at all, to a neutral "equipo" salutation."""
    greeting_name = "equipo"
    if client is not None:
        if client.name:
            greeting_name = client.name.strip().split()[0]
        elif client.company:
            greeting_name = client.company.strip()
    return _EMAIL_BODY_TEMPLATE.format(greeting_name=greeting_name, code=proposal.code)


def format_email_html_body(plain_body: str) -> str:
    """Build an HTML version of the plain body so the line that
    references the proposal code lands in **bold** in the recipient's
    inbox. Everything else is escaped and `\\n` becomes `<br>` so the
    layout matches what the operator sees in the textarea.
    """
    rendered_lines: list[str] = []
    for line in plain_body.split("\n"):
        escaped = escape(line)
        if line.lstrip().startswith(_CODE_REFERENCE_PREFIX):
            rendered_lines.append(f"<strong>{escaped}</strong>")
        else:
            rendered_lines.append(escaped)
    body_html = "<br>".join(rendered_lines)
    return f"<html><body>{body_html}</body></html>"
