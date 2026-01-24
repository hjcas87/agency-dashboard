# Skill — Solution Design (Functional Definition)

Tags: [solution] [design]

## Goal
Produce and maintain functional solution documentation that is agreed with the client
and used as the basis for development.

## When to use
- Defining a new automation solution with a client.
- Clarifying scope, requirements, or flows before development.
- Updating the agreed solution after an explicit scope change.

## Scope
This skill applies to all content under:
`docs/solution_design/`

## Rules (STRICT)
- This skill operates at **functional level only**.
- No technical architecture decisions.
- No implementation details.
- No code changes.
- Changes require explicit agreement (scope change).

## Outputs
- system_requirements.md
- scope.md
- assumptions_and_constraints.md
- diagrams/*.excalidraw
- user_stories/*.md

## Steps (MANDATORY ORDER)

### 1) Read PROJECT_BRIEF
- Read `docs/PROJECT_BRIEF.md` to understand client needs.
- Identify key requirements, scope, and constraints.

### 2) Define system requirements
- Capture non-negotiable technical constraints.
- Use binary language (must / must not).
- No implementation details.

### 2) Define scope
- Explicitly list:
  - In Scope
  - Out of Scope
- Avoid ambiguous phrasing.
- Include acceptance criteria at solution level.

### 3) Define assumptions and constraints
- Document expectations about:
  - data quality
  - performance
  - UI stability
  - execution conditions

### 4) Create process diagrams
- Start with a high-level flow.
- Separate happy path and error paths.
- Use Excalidraw format (`.excalidraw`).
- Diagrams must remain editable.

### 5) Create user stories
- One user story per file.
- Each user story must map to a single feature (backend + frontend if needed).
- Define preconditions and acceptance criteria.
- Avoid technical language where possible.

### 6) Review for completeness
- No technical implementation details.
- No missing error paths.
- No implicit assumptions.

## Validation
- A stakeholder can review and understand the solution without reading code.
- Developers can map user stories to features (backend + frontend).
- Scope boundaries are explicit and enforceable.
- Documents are suitable for client sign-off.
- Solution design is based on PROJECT_BRIEF.

## Common mistakes (avoid)
- Mixing functional design with technical decisions.
- Writing user stories that span multiple processes.
- Using diagrams as screenshots instead of editable files.
- Leaving assumptions undocumented.
- Making changes without recording a scope update.

## Troubleshooting
- If scope is unclear → refine `scope.md`.
- If stories are too technical → simplify language.
- If diagrams grow too complex → split them.