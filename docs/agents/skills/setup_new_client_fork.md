# Skill — Setup New Client Fork

Tags: [setup] [client] [fork]

## Goal
Create a new client fork with proper structure and initial configuration.

## When to use
- Starting a new client project
- Setting up a new fork from the boilerplate

## Preconditions
- `docs/PROJECT_BRIEF.md` has been created by the analyst.
- Client name is agreed (used for branch name and references).

## Steps (MANDATORY ORDER)

### 1) Create client branch
- Create branch from `main`: `git checkout -b <client-name>`
- Ensure branch is up to date with `main`.

### 2) Create PROJECT_BRIEF
- Copy `docs/PROJECT_BRIEF.template.md` to `docs/PROJECT_BRIEF.md`.
- Fill with client information from analyst meeting.

### 3) Customize home page (optional)
- Override `frontend/app/(private)/page.tsx` with client-specific dashboard.
- This file has `merge=ours` in `.gitattributes`, so customizations are preserved.

### 4) Create custom directories (if needed)
- `frontend/app/(private)/(custom)/` - for custom pages
- `frontend/components/custom/features/` - for custom components
- `backend/app/custom/features/` - for custom backend features

### 5) Configure environment variables
- Copy `.env.example` to `.env` (if exists).
- Configure client-specific settings.
- Never commit `.env` files.

### 6) Initialize solution design
- Run `solution_design` skill to generate `docs/solution_design/` from PROJECT_BRIEF.

### 7) Verify structure
- Ensure core/custom separation is clear.
- Verify `.gitattributes` rules are in place.
- Test that fork can be updated from `main` without conflicts.

## Validation
- Branch created and up to date with `main`.
- PROJECT_BRIEF exists and is filled.
- Custom directories are ready.
- Environment variables configured (not committed).
- Solution design can be generated.

## Common mistakes (avoid)
- Modifying `core/` files directly (use `custom/` instead).
- Committing `.env` files.
- Not keeping branch up to date with `main`.
- Creating features before solution design is approved.

## Troubleshooting
- If merge conflicts occur → check `.gitattributes` rules.
- If core files need changes → commit to `main` first, then merge to client branch.
