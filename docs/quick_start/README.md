# Quick Start Guide

> This document needs to be completed.

## Prerequisites

- Docker & Docker Compose (or Colima on macOS)
- Node.js 18+
- Python 3.12+ (managed by uv)

## First-time setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd automation-warehouse

# 2. Copy environment file
cp .env.example backend/.env

# 3. Start infrastructure
make dev

# 4. Install and run backend
cd backend && uv sync
uv run uvicorn app.main:app --reload

# 5. Install and run frontend (in another terminal)
cd frontend && npm install
npm run dev
```

## Services available

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| N8N | http://localhost:5678 |
| RabbitMQ Management | http://localhost:15672 |
| Flower (Celery) | http://localhost:5555 |

## Useful commands

See `Makefile` for all available commands.

```bash
make help    # Show all commands
make dev     # Start infrastructure
make down    # Stop infrastructure
make test    # Run backend tests
make logs    # View service logs
```
