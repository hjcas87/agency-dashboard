# Agent Starter — Debugging (Web Application)

You are working in the **Web Application Boilerplate** template repo.

## Always do first (MANDATORY)
1) Read:
   - `AGENTS.md`
   - `ARCHITECTURE.md`
2) Identify the issue:
   - Error messages (backend logs, frontend console)
   - API endpoint affected (if applicable)
   - Database issues (if applicable)
   - Frontend component/page (if applicable)
3) Check logs:
   - Backend logs: `docker-compose logs backend` or application logs
   - Frontend console: Browser DevTools
   - Database logs: `docker-compose logs postgres`

If no error information exists, STOP and ask for more details.

---

## Role selection (MANDATORY)
Use role based on issue type:
- Backend issues → `docs/agents/roles/backend_architect.md`
- Frontend issues → `docs/agents/roles/frontend_architect.md`
- General debugging → `docs/agents/roles/feature_developer.md`

Follow its priorities and constraints strictly.

---

## Skill triggers (MANDATORY)
Apply the Skills Protocol from `AGENTS.md`.

Use appropriate skills based on issue:
- Database model sync issues → `add_database_migration.md`
- API endpoint issues → `add_backend_feature.md` or `review_feature.md`
- Frontend component issues → `add_frontend_feature.md` or `review_feature.md`
- Integration issues → `add_integration.md`

---

## Debugging rules (STRICT)
- Reproduce the issue before fixing.
- Check error logs and stack traces.
- Verify database migrations are applied.
- Check environment variables are set correctly.
- Verify API endpoints are accessible.
- Check frontend/backend integration.

---

## What to produce (MANDATORY)
1) Root cause explanation (based on logs/errors).
2) Minimal fix applied.
3) Files changed.
4) Commands to verify fix:
   - `make test` (run tests)
   - `make dev` (restart services if needed)
   - `docker-compose logs <service>` (check logs)
5) Confirmation that issue is resolved.

If the issue cannot be fixed, explain why and propose next steps.
