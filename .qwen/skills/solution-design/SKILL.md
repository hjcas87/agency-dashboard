---
name: solution-design
description: Produce functional solution documentation agreed with the client. Use when defining solution scope, requirements, user stories, or creating solution design documents. All output MUST be in Spanish.
---

# Solution Design (Functional Definition)

## When to use
- Defining a new automation solution with a client
- Clarifying scope, requirements, or flows before development
- Updating the agreed solution after an explicit scope change

## Rules (STRICT)
- **Functional level only** — no technical architecture decisions, no implementation details
- **All documents MUST be written in Spanish** — for client review and discussion
- Changes require explicit agreement

## Outputs (all in Spanish)
- `docs/solution_design/system_requirements.md`
- `docs/solution_design/scope.md`
- `docs/solution_design/assumptions_and_constraints.md`
- `docs/solution_design/diagrams/*.excalidraw`
- `docs/solution_design/user_stories/*.md`

## Steps

### 1) Read PROJECT_BRIEF
- Read `docs/PROJECT_BRIEF.md` to understand client needs

### 2) Define system requirements
- Capture non-negotiable technical constraints
- Use binary language (must / must not)
- No implementation details

### 3) Define scope
- Explicitly list: In Scope / Out of Scope
- Include acceptance criteria

### 4) Define assumptions and constraints
- Document expectations about data quality, performance, execution conditions

### 5) Create process diagrams
- Use Excalidraw format (`.excalidraw`) — must remain editable
- Separate happy path and error paths

### 6) Create user stories
- One user story per file, maps to a single feature
- Define preconditions and acceptance criteria
- Avoid technical language

### 7) Review for completeness
- No technical implementation details
- No missing error paths

## Validation
- Stakeholder can review without reading code
- Developers can map user stories to features
- Documents suitable for client sign-off

## Common mistakes
- Mixing functional design with technical decisions
- Writing user stories that span multiple processes
- Using diagrams as screenshots instead of editable files
- Leaving assumptions undocumented
