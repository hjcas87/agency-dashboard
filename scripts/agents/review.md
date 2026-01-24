# Agent Starter — Review (Code Quality Gate)

You are reviewing changes in the **Web Application Boilerplate** template repo.

## Always do first (MANDATORY)
1) Read:
   - `AGENTS.md`
   - `ARCHITECTURE.md`
2) Identify:
   - scope of changes
   - affected features (backend/frontend)
   - affected core/custom boundaries
   - database migrations (if any)

---

## Role selection (MANDATORY)
Use role:
- `docs/agents/roles/code_reviewer.md`

Follow its authority and constraints strictly.

---

## Skill triggers (MANDATORY)
Apply the Skills Protocol from `AGENTS.md`.

Always use:
- `docs/agents/skills/review_feature.md`

Additionally, if applicable:
- Deployment changes → `deploy.md`
- Database migrations → `add_database_migration.md`
- New client fork → `setup_new_client_fork.md`

---

## Review rules (STRICT)
- No new features during review.
- No architecture drift.
- Block any violation of:
  - boundaries (core / custom / shared)
  - Python 3.11+ typing rules
  - TypeScript strict mode rules
  - uv/npm dependency rules
  - Database synchronization rules

---

## What to produce (MANDATORY)
1) Review verdict:
   - Approve
   - Approve with minor notes
   - Request changes
2) Categorized findings:
   - Blocker
   - Major
   - Minor
3) Concrete, actionable fix suggestions.

Do NOT merge or approve if any blocker exists.
