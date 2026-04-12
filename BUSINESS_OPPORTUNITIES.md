# Business Opportunities Analysis — Tiendanube Integration

> This document catalogs potential products and features built on top of Tiendanube's API.
> Use it as a starting point for defining the PROJECT_BRIEF with the client.

---

## 📦 Inventory of Existing Resources

The `resources/` folder contains **two separate product ideas** from a previous project:

### Product A: NexusB2B — B2B Wholesale Portal
- Custom pricing per customer/customer group
- Read-only catalog synced from Tiendanube
- Multi-tenant SaaS architecture
- Order creation via Tiendanube API
- Password reset + email system (documented)

### Product B: Mendri Growth Suite — Loyalty & Retention
- **Loyalty Points**: Spend-based earning, VIP tiers (Bronze/Silver/Gold)
- **Rewards**: Discount redemption, coupon generation
- **Gamification**: Badges/achievements (5-purchase streak, big spender, etc.)
- **Referrals**: Unique codes, point bonuses for referrer and referee
- **Abandoned Cart Recovery**: Email with bonus points incentive

---

## 🔌 Tiendanube API — Complete Capability Map

### 🛒 Core Commerce (33 Resources)

| Category | Resources | What it enables |
|----------|-----------|-----------------|
| **Catalog** | Products, Variants, Categories, Images, Custom Fields | Full catalog sync, search, display |
| **Customers** | Customers, Custom Fields | CRM, segmentation, personalized experiences |
| **Orders** | Orders, Draft Orders, Fulfillment Orders, Transactions | Order management, fulfillment tracking |
| **Carts** | Carts, Cart line items, Coupons | Cart management, abandoned cart recovery |
| **Checkout** | Checkout, Checkout SDK, Business Rules | Checkout customization, payment flows |
| **Payments** | Payment Providers, Payment Options, Transactions | Payment method management, transaction tracking |
| **Shipping** | Shipping Carriers, Locations, Fulfillment | Multi-location inventory, shipping rate calculation |
| **Discounts** | Discounts, Coupons | Promotional campaigns, loyalty rewards |
| **Store** | Store, Pages, Blog | Storefront customization |
| **Customization** | Scripts, Metafields, Email Templates | App injection, data storage, email branding |
| **Automation** | Webhooks | Real-time event notifications |
| **Billing** | Billing (Plans, Subscriptions, Charges) | SaaS billing management |

### 🎯 Key Webhook Events

| Event | Trigger | Use Case |
|-------|---------|----------|
| `order/paid` | Customer completes purchase | Loyalty points, referral bonuses, notifications |
| `checkouts/created` | Customer starts checkout | Abandoned cart detection |
| `product/updated` | Product modified | Catalog sync |
| `customer/updated` | Customer data changed | Profile updates, segmentation |

---

## 💡 Product Opportunities (Ranked by Impact/Complexity)

### 1. 🏆 Abandoned Cart Recovery — HIGH IMPACT, MEDIUM COMPLEXITY
**What**: Detect incomplete checkouts and automatically re-engage customers
**How**: Webhook `checkouts/created` → N8N workflow → Email/SMS with incentive
**Revenue driver**: Direct revenue recovery (5-15% of abandoned carts recoverable)
**Tiendanube resources**: Abandoned Checkouts API, Webhooks, Email Templates, Coupons
**Status**: Partially documented in `resources/` — needs implementation

### 2. 🏆 Loyalty Program — HIGH IMPACT, HIGH COMPLEXITY
**What**: Points system with VIP tiers, earning rules, and reward redemption
**How**: Webhook `order/paid` → Points engine → Metafields storage → Storefront widget
**Revenue driver**: Customer retention, increased LTV, repeat purchases
**Tiendanube resources**: Metafields, Business Rules (for $0 checkouts), Webhooks, Scripts
**Status**: Fully documented in `resources/` — ready for implementation

### 3. 🎯 B2B Wholesale Portal — MEDIUM IMPACT, HIGH COMPLEXITY
**What**: Separate storefront for wholesale buyers with custom pricing
**How**: Catalog sync + pricing engine + order injection
**Revenue driver**: Opens B2B channel, automates wholesale operations
**Tiendanube resources**: Products, Orders, Custom Fields, Webhooks
**Status**: Well-documented in `resources/` — ready for implementation

### 4. 🎯 Referral System — MEDIUM IMPACT, LOW COMPLEXITY
**What**: Customers share codes, both referrer and referee get discounts
**How**: Webhook `order/paid` → Referral matching → Coupon generation
**Revenue driver**: New customer acquisition at low cost
**Tiendanube resources**: Customers, Coupons, Webhooks, Metafields
**Status**: Documented — simple to implement

### 5. 📊 Customer Analytics Dashboard — MEDIUM IMPACT, LOW COMPLEXITY
**What**: RFM analysis, cohort tracking, customer lifetime value
**How**: Orders + Customers API → Local aggregation → Dashboard
**Revenue driver**: Data-driven decisions, merchant insights
**Tiendanube resources**: Orders, Customers, Webhooks
**Status**: Not documented — easy to add

### 6. 🎯 Email + WhatsApp Marketing Automation — HIGH IMPACT, LOW COMPLEXITY
**What**: Triggered sequences based on customer behavior across email and WhatsApp
**How**: Webhooks → N8N workflows → Email Templates + WhatsApp Business API
**Revenue driver**: Re-engagement, upselling, win-back campaigns
**Tiendanube resources**: Webhooks, Email Templates, Customers
**N8N channels**: Email, WhatsApp, SMS (future)
**Status**: Email infrastructure documented — ready to extend with WhatsApp via N8N

### 7. 📱 Storefront Widget (Scripts API) — MEDIUM IMPACT, MEDIUM COMPLEXITY
**What**: Loyalty balance, referral codes, gamification badges on storefront
**How**: Scripts API injects Preact/JS widget into storefront
**Revenue driver**: Customer engagement, visibility of loyalty program
**Tiendanube resources**: Scripts, Metafields, Store
**Status**: Partially documented — needs UI work

---

## ⚠️ Architecture Alignment Notes

### What aligns with this repo's architecture:
- ✅ All products fit the `custom/features/` pattern perfectly
- ✅ N8N integration is already in `core/features/n8n/`
- ✅ Auth, users, and email infrastructure exist in core
- ✅ Celery tasks fit the background job pattern
- ✅ Multi-tenancy can be implemented as a custom feature

### What needs careful attention:
- ⚠️ **Multi-tenancy**: The existing docs describe it, but this repo doesn't have it built-in. Must be implemented as a custom feature with `tenant_id` on all models.
- ⚠️ **Catalog sync**: The "Pull on Demand" strategy from `resources/` is good but needs rate limiting (Tiendanube: 40 burst, 2 req/sec).
- ⚠️ **Metafields storage**: Tiendanube Metafields are namespaced key-value pairs — useful for loyalty balance but requires API calls on every storefront render.
- ⚠️ **Business Rules API**: Has an 800ms callback timeout — must be responsive.

### What to AVOID or reconsider:
- ❌ **Don't build a full B2B portal as MVP** — too complex, start with one feature
- ❌ **Don't over-engineer the loyalty engine** — start with simple spend→points ratio
- ❌ **Don't build multi-tenancy from day 1** — single tenant first, add later

---

## 🎯 Recommended Starting Point

For a new client project, the recommended approach is:

1. **Start with ONE product** — either Loyalty OR Abandoned Cart Recovery (not both)
2. **Single tenant first** — no multi-tenancy in MVP
3. **Use N8N for email flows** — no custom email service needed initially
4. **Skip gamification** — add after core loyalty is working
5. **Build the referral system** — it's low complexity, high perceived value

**MVP Scope Recommendation**:
```
Abandoned Cart Recovery (email + WhatsApp) + Simple Loyalty (points per purchase)
```

This combination gives immediate revenue impact (cart recovery via dual channels) AND long-term retention (loyalty) with manageable complexity. WhatsApp is handled via N8N workflows, not custom backend code.

---

## 📋 Next Steps

1. Meet with client to understand their store, customer base, and priorities
2. Fill out `docs/PROJECT_BRIEF.md` based on the meeting
3. Generate `docs/solution_design/` from the brief
4. Choose the MVP scope and implement in `custom/features/`
