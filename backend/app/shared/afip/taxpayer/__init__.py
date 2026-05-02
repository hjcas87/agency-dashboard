"""Padrón A5 (`ws_sr_padron_a5`) wrapper.

`TaxpayerService.get` is the public entrypoint. It returns a
`TaxpayerInfo` dataclass — the consumer never sees raw XML or AFIP
response shapes. Implementation lives in `service.py`."""
from app.shared.afip.taxpayer.service import TaxpayerService

__all__ = ["TaxpayerService"]
