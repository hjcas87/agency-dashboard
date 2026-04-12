---
name: add-n8n-workflow
description: Create and integrate an N8N workflow for automation. Use when adding workflow automation, connecting N8N to backend features, or creating webhook-based automations.
---

# Add N8N Workflow

## When to use
- Adding automation workflows via N8N
- Integrating N8N workflows with backend features

## Preconditions
- N8N is running and accessible (http://localhost:5678)
- Workflow requirements are understood

## Steps

### 1) Design workflow in N8N
- Create workflow in N8N UI
- Define nodes, connections, and logic
- Test workflow in N8N

### 2) Export workflow
- Export workflow JSON from N8N
- Save to `automation/workflows/<workflow_name>.json`

### 3) Add backend integration (if needed)
- To trigger workflow: use `N8NService` from `shared/services/`
- To receive webhook: create endpoint in `backend/app/custom/features/<feature>/routes.py`

### 4) Add Celery task (if async)
- Create Celery task in feature `tasks.py`
- Use `N8NService` to trigger workflow

### 5) Document workflow
- Document in feature `README.md`: purpose, trigger method, payload, workflow file location

### 6) Test integration
- Test workflow trigger from backend
- Test webhook endpoint (if applicable)

## Validation
- Workflow is exported and saved
- Backend integration works (if applicable)
- Workflow can be triggered and executed

## Common mistakes
- Not exporting workflow JSON
- Hardcoding workflow IDs
- Not handling workflow failures
- Not documenting workflow purpose
