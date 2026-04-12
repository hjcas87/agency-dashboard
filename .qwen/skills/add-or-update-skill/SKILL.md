---
name: add-or-update-skill
description: Create or modify an agent skill following the standard convention. Use when adding new skills, updating existing skill procedures, or changing agent behavior conventions.
---

# Add or Update a Skill

## When to use
- Adding a new skill file
- Updating an existing skill's procedure or convention
- Creating or updating triggers and mappings

## Preconditions
- The change is generic (not client-specific)
- The skill represents a repeatable process

## Steps

### 1) Choose a clear skill name
- Use **snake_case**, **verb + object**
- Examples: `add_backend_feature`, `solution_design`, `deploy`

### 2) Place the file
- Create or update under `.qwen/skills/<skill-name>/SKILL.md`

### 3) Follow the required template
Include sections in this exact order:
1. Goal
2. When to use
3. Preconditions (optional)
4. Rules (optional, if strict constraints)
5. Steps
6. Validation
7. Common mistakes (avoid)
8. Troubleshooting

### 4) Add frontmatter
```yaml
---
name: skill-name
description: Clear description with trigger keywords.
---
```

### 5) Register triggers in `AGENTS.md`
- Add trigger line under appropriate category
- Update the Skill Trigger Map
- Ensure trigger language is strict and unambiguous

### 6) Update role references (only if required)
- Add skill to role's mandatory skills ONLY if always applicable

### 7) Validate consistency
- Skill file exists with correct name
- Filename matches references in `AGENTS.md`
- Trigger exists and is unambiguous
- Steps are concrete and enforceable

## Validation
- Skill follows convention
- `AGENTS.md` includes trigger(s) and map entry
- No duplicate or ambiguous skill names

## Common mistakes
- Creating skills without triggers
- Writing vague steps
- Embedding client-specific behavior in a generic skill
