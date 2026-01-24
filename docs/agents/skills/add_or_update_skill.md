# Skill — Add or Update a Skill (Skill Authoring)

Tags: [core] [review]

## Goal
Create or modify a skill so it is consistent, discoverable, and enforceable
by agents across the repository.

## When to use
- Adding a new skill file.
- Updating an existing skill’s procedure or convention.
- Changing how agents are expected to behave (rules, standards, workflows).
- Creating or updating triggers and mappings.

## Preconditions
- The change is generic (not client-specific).
- You understand the existing agent roles, triggers, and conventions.
- The skill represents a repeatable process, not an ad-hoc instruction.

## Steps (MANDATORY ORDER)

### 1) Choose a clear skill name
- Use **snake_case**.
- Use **verb + object**.
- Do NOT use numeric prefixes.

Examples:
- `add_backend_feature.md`
- `add_frontend_feature.md`
- `solution_design.md`
- `deploy.md`

The filename is the skill identifier.

---

### 2) Place the file
- Create or update the file under:
  - `docs/agents/skills/`

---

### 3) Follow the required template order
Include sections in this exact order:
- Goal
- When to use
- Preconditions (optional if obvious)
- Rules (optional, if strict constraints exist)
- Steps (MANDATORY ORDER)
- Validation
- Common mistakes (avoid)
- Troubleshooting

Do NOT reorder sections.

---

### 4) Add tags
- Add `Tags: [...]` at the top (optional but recommended).
- Use:
  - one primary tag (e.g. `[release]`, `[debug]`, `[review]`)
  - up to two secondary tags
- Tags are descriptive only; they do not replace triggers.

---

### 5) Register triggers in `AGENTS.md`
- Add an explicit trigger line under the appropriate trigger category.
- Update the **Skill Trigger Map** using the skill name.
- Ensure the trigger language is strict and unambiguous.

If no trigger exists, the skill is considered incomplete.

---

### 6) Update role references (only if required)
- Add the skill to a role’s **Mandatory skills** ONLY if:
  - the role must always apply it
- Otherwise, rely on triggers.

Do not over-assign skills to roles.

---

### 7) Review and validate consistency
Perform a consistency check:
- skill file exists
- filename matches references in `AGENTS.md`
- trigger exists
- trigger map includes the skill
- no duplicate or ambiguous skill names
- steps are concrete and enforceable

If the skill affects execution or quality gates,
ensure the **Validation** section is explicit.

---

## Validation
- Skill follows the convention in `docs/agents/skills/README.md`.
- `AGENTS.md` includes trigger(s) and map entry.
- No numeric identifiers are used.
- Agents can unambiguously determine when to apply the skill.

## Common mistakes (avoid)
- Creating skills without triggers.
- Using numeric prefixes or implicit ordering.
- Writing vague steps (“handle errors”, “ensure stability”).
- Embedding client-specific behavior in a generic skill.

## Troubleshooting
- If agents ignore the skill:
  - verify a strict trigger exists in `AGENTS.md`
- If multiple skills seem applicable:
  - rely on trigger priority and role context
- If naming is unclear:
  - rename the skill to better reflect its intent