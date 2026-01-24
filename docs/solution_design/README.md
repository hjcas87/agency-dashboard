# Solution Design — Documentation Convention

This folder contains the agreed functional definition of the web application solution.

## General rules
- These documents are discussed and approved with the client.
- They are the single source of truth for development.
- Changes require explicit agreement and versioning.
- No implementation or technical decisions belong here.

## Versioning
- Versioning is tracked at the folder level.
- The current version must be stated in this file.
- Changes are also reflected in git history.

Current version: **v1.0 — Initial agreed solution**

Version history:
- v1.0 — Initial agreed solution (YYYY-MM-DD)
  - [Project description]
  - Based on PROJECT_BRIEF dated YYYY-MM-DD

## Templates
This folder provides templates for all solution design documents.

Templates MUST be used when creating new documents to ensure:
- consistency
- completeness
- clear review with the client

Available templates:
- `system_requirements.template.md`
- `scope.template.md`
- `assumptions_and_constraints.template.md`
- `user_stories/template.md`
- `diagrams/template.excalidraw`

Do not create solution documents from scratch; always start from the template.

## File ownership
- Only the **Solution Designer** role may create or modify files in this folder.
- Other roles may read but MUST NOT edit these documents.
- Developers must not change these files during implementation.

## Language
- Use clear, business-oriented language.
- Avoid technical jargon unless unavoidable.
- Prefer contractual wording:
  - must / must not
  - will / will not

## Mapping to development
- Each user story maps to:
  - exactly one feature (backend + frontend if needed)
  - one test suite
- Diagrams describe behavior and decisions,
  not UI layout or technical implementation.

## Workflow

1. **Analyst creates PROJECT_BRIEF** → `docs/PROJECT_BRIEF.md` (in client fork)
2. **Cursor generates solution_design/** → Based on PROJECT_BRIEF (in Spanish)
3. **Refine with client** → Iterate until approved
4. **Cursor generates code** → Based on approved solution design