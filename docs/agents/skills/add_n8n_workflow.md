# Skill — Add N8N Workflow

Tags: [automation] [n8n] [workflow]

## Goal
Create and integrate an N8N workflow for automation.

## When to use
- Adding automation workflows via N8N.
- Integrating N8N workflows with backend features.

## Preconditions
- N8N is running and accessible.
- Workflow requirements are understood.
- Webhook endpoints are identified (if needed).

## Steps (MANDATORY ORDER)

### 1) Design workflow in N8N
- Create workflow in N8N UI.
- Define nodes, connections, and logic.
- Test workflow in N8N.

### 2) Export workflow
- Export workflow JSON from N8N.
- Save to `automation/workflows/<workflow_name>.json`.

### 3) Add backend integration (if needed)
- If backend needs to trigger workflow:
  - Use `N8NService` from `shared/services/`.
  - Call `trigger_workflow_async()` with workflow ID and payload.
- If workflow needs to call backend:
  - Create webhook endpoint in `backend/app/custom/features/<feature>/routes.py`.
  - Handle webhook payload.

### 4) Add Celery task (if async)
- If workflow execution is async:
  - Create Celery task in feature `tasks.py`.
  - Use `N8NService` to trigger workflow.
  - Handle task status and results.

### 5) Document workflow
- Document in feature `README.md`:
  - Workflow purpose
  - How to trigger (API endpoint or Celery task)
  - Expected payload
  - Workflow file location

### 6) Test integration
- Test workflow trigger from backend.
- Test webhook endpoint (if applicable).
- Verify workflow execution and results.

## Validation
- Workflow is exported and saved.
- Backend integration works (if applicable).
- Workflow can be triggered and executed.
- Documentation is complete.

## Common mistakes (avoid)
- Not exporting workflow JSON.
- Hardcoding workflow IDs.
- Not handling workflow failures.
- Not documenting workflow purpose.

## Troubleshooting
- If workflow fails → check N8N logs and workflow configuration.
- If integration fails → verify N8N service configuration and workflow ID.
- If webhook fails → check endpoint URL and payload format.
