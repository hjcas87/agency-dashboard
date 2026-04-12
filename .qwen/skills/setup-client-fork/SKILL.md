---
name: setup-client-fork
description: Create a new client fork with proper structure, PROJECT_BRIEF, and initial configuration. Use when starting a new client project from the boilerplate.
---

# Setup New Client Fork

## When to use
- Starting a new client project
- Setting up a new fork from the boilerplate

## Preconditions
- `docs/PROJECT_BRIEF.md` has been created by the analyst

## Steps

### 1) Create client branch
```bash
git checkout -b <client-name>
```

### 2) Create PROJECT_BRIEF
- Copy `docs/PROJECT_BRIEF.template.md` to `docs/PROJECT_BRIEF.md`
- Fill with client information from analyst meeting

### 3) Customize home page (optional)
- Override `frontend/app/(private)/page.tsx` with client-specific dashboard

### 4) Create custom directories (if needed)
- `frontend/app/(private)/(custom)/` — custom pages
- `frontend/components/custom/features/` — custom components
- `backend/app/custom/features/` — custom backend features

### 5) Configure environment variables
- Copy `.env.example` to `.env`
- Configure client-specific settings
- Never commit `.env` files

### 6) Initialize solution design
- Run `solution-design` skill to generate `docs/solution_design/` from PROJECT_BRIEF

### 7) Verify structure
- Ensure core/custom separation is clear
- Verify `.gitattributes` rules are in place

## Validation
- Branch created and up to date with `main`
- PROJECT_BRIEF exists and is filled
- Custom directories are ready
- Environment variables configured (not committed)

## Common mistakes
- Modifying `core/` files directly
- Committing `.env` files
- Creating features before solution design is approved
