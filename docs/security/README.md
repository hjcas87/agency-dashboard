# Security Updates

> This document needs to be completed.

## Security Update Log

| Date | Package | Old Version | New Version | Reason |
|------|---------|-------------|-------------|--------|
| 2025-04-11 | psycopg2-binary | 2.9.9 | — | Replaced with psycopg[binary] v3 |
| 2025-04-11 | Python | 3.14 | 3.12 | Compatibility with package ecosystem |

## Dependencies

### Backend
- Managed via `uv` in `backend/pyproject.toml`
- Lock file: `backend/uv.lock`
- Update: `uv add <package>` then `uv lock`

### Frontend
- Managed via `npm` in `frontend/package.json`
- Lock file: `frontend/package-lock.json`
- Update: `npm install <package>`

## Audit

```bash
# Frontend security audit
cd frontend && npm audit

# Backend: check for outdated packages
cd backend && uv pip list --outdated
```
