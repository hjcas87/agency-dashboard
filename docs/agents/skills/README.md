# Skills Convention

Skills are operational, repeatable procedures used by both developers and agents.

## Naming
- Prefix: `<verb>_<object>.md`
- Use snake_case.
- Example: `add_backend_feature.md`

## Required sections (in this order)
1. Title: `# Skill <Name>`
2. `## Goal`
3. `## When to use`
4. `## Preconditions`
5. `## Steps (MANDATORY ORDER)`
6. `## Validation`
7. `## Common mistakes (avoid)`
8. `## Troubleshooting`

## Tags (optional but recommended)
Add at the top of the file:
`Tags: [core] [custom] [backend] [frontend] [debug] [review] [deploy]`

## Style rules
- Steps must be deterministic and testable.
- Prefer explicit commands and file paths.
- Avoid vague language ("should", "maybe") unless unavoidable.