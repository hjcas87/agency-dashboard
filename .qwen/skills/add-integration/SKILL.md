---
name: add-integration
description: Integrate an external service (API, webhook, third-party) into the project. Use when adding external API integrations, webhooks, or third-party service connections.
---

# Add External Service Integration

## When to use
- Adding integration with external APIs
- Adding webhook endpoints
- Integrating third-party services

## Preconditions
- External service API documentation is available
- Authentication/authorization requirements are understood
- Rate limits and error handling are understood

## Steps

### 1) Create interface (if needed)
- If the integration should be swappable, create interface in `backend/app/shared/interfaces/`
- Define methods and contracts

### 2) Create service wrapper
- Create service in `backend/app/shared/services/` or `backend/app/custom/features/<feature>/service.py`
- Implement interface or create standalone service
- Handle authentication, rate limiting, error handling

### 3) Add configuration
- Add environment variables for API keys, base URLs, timeouts
- Never hardcode credentials

### 4) Add error handling
- Handle network errors, API errors (4xx, 5xx)
- Provide meaningful error messages

### 5) Add tests
- Mock external service in tests
- Test error cases and authentication failures

### 6) Document integration
- Document in feature `README.md`: configuration, usage, error handling, rate limits

## Validation
- Service can be instantiated and used
- Error handling works correctly
- Tests pass (with mocked external service)
- Configuration is externalized (no hardcoded values)

## Common mistakes
- Hardcoding API keys or URLs
- Not handling errors properly
- Not mocking external services in tests
- Not documenting configuration requirements
