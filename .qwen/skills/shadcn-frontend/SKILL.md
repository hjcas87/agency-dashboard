---
name: shadcn-frontend
description: Build UI components using shadcn/ui for the frontend. Triggers when adding components, fixing styling, creating forms, building dashboards, or working with any UI element. Use this skill for all frontend work involving components, layouts, forms, charts, or navigation. Keywords: shadcn, ui, component, form, button, card, dialog, sidebar, chart, table, input, select, badge, avatar, toast, dropdown, dialog, sheet, drawer, tabs, accordion, popover, tooltip, hovercard, context-menu, command, calendar, date-picker, skeleton, progress, toggle, breadcrumb, navigation, pagination, empty state, alert, separator, scroll-area, resizable, collapsible, menubar, slider, switch, checkbox, radio, input-otp, textarea, combobox, sonner.
---

# shadcn/ui — Frontend Component System

## When to use
- Adding or creating any UI component (button, card, form, table, chart, sidebar, etc.)
- Fixing styling, layout, or component composition issues
- Building dashboards, settings pages, navigation
- Working with shadcn CLI (`npx shadcn@latest add ...`)
- Debugging component rendering or styling issues

## Preconditions
- Project has `components.json` at `frontend/components.json`
- UI components live in `frontend/components/core/ui/`
- Dashboard components live in `frontend/components/core/features/dashboard/`
- Use `npx` for shadcn CLI commands (project uses npm)

## Critical Rules (always enforced)

### 1. Use existing components first
- Run `npx shadcn@latest search` before writing custom UI
- Compose from existing components — don't reinvent
- Settings page = Tabs + Card + form controls
- Dashboard = Sidebar + Card + Chart + Table

### 2. Styling rules
- **`className` for layout only** — never override colors or typography via className
- **No `space-x-*` or `space-y-*`** — use `flex` with `gap-*`
- **Use `size-*` for equal dimensions** — `size-10` not `w-10 h-10`
- **Semantic colors only** — `bg-background`, `text-muted-foreground`, `bg-primary` — never raw `bg-blue-500`
- **No manual `dark:` color overrides**
- **Use `cn()` for conditional classes**
- **No manual `z-index` on overlays** — Dialog, Sheet, Popover handle their own stacking

### 3. Forms
- **Use `FieldGroup` + `Field`** — never raw `div` with `space-y-*`
- **Field validation uses `data-invalid` + `aria-invalid`**
- **Option sets (2–7 choices) use `ToggleGroup`**
- **`FieldSet` + `FieldLegend` for grouping checkboxes/radios**

### 4. Component composition
- **Items inside their Group** — `SelectItem` → `SelectGroup`, `DropdownMenuItem` → `DropdownMenuGroup`
- **Dialog, Sheet, Drawer always need a Title** — use `className="sr-only"` if visually hidden
- **Use full Card composition** — `CardHeader`/`CardTitle`/`CardDescription`/`CardContent`/`CardFooter`
- **Button has no `isPending`/`isLoading`** — compose with Spinner + disabled
- **`TabsTrigger` must be inside `TabsList`**
- **`Avatar` always needs `AvatarFallback`**

### 5. Icons
- **Icons in `Button` use `data-icon`** — `data-icon="inline-start"` or `data-icon="inline-end"`
- **No sizing classes on icons inside components** — components handle sizing via CSS
- **Pass icons as objects, not string keys** — `icon={CheckIcon}`, not `"CheckIcon"`

### 6. Use components, not custom markup
- Callouts → `Alert` (not custom styled divs)
- Empty states → `Empty` (not custom markup)
- Toast → `sonner` / `toast()` 
- Separators → `Separator` (not `<hr>` or `<div className="border-t">`)
- Loading placeholders → `Skeleton` (not custom `animate-pulse` divs)
- Status indicators → `Badge` (not custom styled spans)

## Steps

### 1. Check project context
```bash
cd frontend && npx shadcn@latest info
```
This returns: installed components, aliases, base (radix vs base), icon library, Tailwind version, package manager.

### 2. Find component if not installed
```bash
npx shadcn@latest search button
```

### 3. Get docs before implementing
```bash
npx shadcn@latest docs button dialog select
```
Fetch the returned URLs to get correct API and usage patterns.

### 4. Add component
```bash
npx shadcn@latest add button card dialog
```

### 5. Fix imports
After adding, verify imports match the project's `components.json` aliases. Components should import from `@/components/core/ui/` in this project.

### 6. Verify composition
Read the added files and check for:
- Missing sub-components (e.g., `SelectItem` without `SelectGroup`)
- Missing imports
- Incorrect composition
- Icon library mismatches (project may use different icon library than default)

## Key Patterns

```tsx
// Form layout: FieldGroup + Field
<FieldGroup>
  <Field>
    <FieldLabel htmlFor="email">Email</FieldLabel>
    <Input id="email" />
  </Field>
</FieldGroup>

// Icons in buttons
<Button>
  <SearchIcon data-icon="inline-start" />
  Search
</Button>

// Spacing
<div className="flex flex-col gap-4">  // correct
<div className="space-y-4">           // wrong

// Equal dimensions
<Avatar className="size-10">   // correct
<Avatar className="w-10 h-10"> // wrong

// Status colors
<Badge variant="secondary">+20.1%</Badge>         // correct
<span className="text-emerald-600">+20.1%</span> // wrong
```

## Component Selection Guide

| Need | Use |
|------|-----|
| Button/action | `Button` with variant |
| Form inputs | `Input`, `Select`, `Combobox`, `Switch`, `Checkbox`, `RadioGroup`, `Textarea` |
| Toggle 2–5 options | `ToggleGroup` |
| Data display | `Table`, `Card`, `Badge`, `Avatar` |
| Navigation | `Sidebar`, `Breadcrumb`, `Tabs`, `Pagination` |
| Overlays | `Dialog` (modal), `Sheet` (side), `Drawer` (bottom), `AlertDialog` (confirm) |
| Feedback | `sonner` (toast), `Alert`, `Progress`, `Skeleton` |
| Charts | `Chart` (wraps Recharts) |
| Layout | `Card`, `Separator`, `ScrollArea`, `Accordion`, `Collapsible` |
| Empty states | `Empty` |
| Menus | `DropdownMenu`, `ContextMenu` |
| Tooltips | `Tooltip`, `HoverCard`, `Popover` |

## Validation
- Component added without errors
- TypeScript compiles without errors
- No styling rule violations
- Component uses project's icon library
- Component follows composition rules (groups, titles, fallbacks)

## Common mistakes
- Writing custom markup when a component exists
- Using raw colors instead of semantic tokens
- Missing `AvatarFallback`, `DialogTitle`, `SheetTitle`
- Using `space-y-*` instead of `flex flex-col gap-*`
- Using `w-* h-*` instead of `size-*`
- Overriding component colors via className
- Manual `z-index` on overlays
- Missing `asChild`/`render` for custom triggers
