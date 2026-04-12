# Tiendanube API Reference

Reference documentation for building integrations with Tiendanube/Nuvemshop.

## Files

| File | Description |
|------|-------------|
| `api-reference.md` | Complete API analysis: auth, rate limiting, resource schemas, webhook events |
| `endpoint-reference.md` | Quick reference of all 33 API resources with methods |
| `api-examples/` | Sample JSON responses (products, variants, categories) |

## Key Details

- **Base URL**: `https://api.tiendanube.com/2025-03/{store_id}` (Argentina/LatAm)
- **Auth**: OAuth 2.0 with Bearer token + `User-Agent` header
- **Rate limiting**: Leaky Bucket (40 burst capacity, 2 req/sec drain)
- **Webhooks**: `order/paid`, `checkouts/created`, `product/updated`, `customer/updated`

## Official Docs

- API Documentation: https://tiendanube.github.io/api-documentation/
- Resources: https://tiendanube.github.io/api-documentation/resources
