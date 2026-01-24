# Skill — Add External Service Integration

Tags: [integration] [external] [service]

## Goal
Integrate an external service (API, webhook, etc.) in a fork-friendly way.

## When to use
- Adding integration with external APIs.
- Adding webhook endpoints.
- Integrating third-party services.

## Preconditions
- External service API documentation is available.
- Authentication/authorization requirements are understood.
- Rate limits and error handling are understood.

## Steps (MANDATORY ORDER)

### 1) Create interface (if needed)
- If the integration should be swappable, create interface in `backend/app/shared/interfaces/`.
- Define methods and contracts.

### 2) Create service wrapper
- Create service in `backend/app/shared/services/` or `backend/app/custom/features/<feature>/service.py`.
- Implement interface (if created) or create standalone service.
- Handle authentication, rate limiting, error handling.

### 3) Add configuration
- Add environment variables for:
  - API keys/tokens
  - Base URLs
  - Timeouts
- Never hardcode credentials.

### 4) Add error handling
- Handle network errors.
- Handle API errors (4xx, 5xx).
- Provide meaningful error messages.

### 5) Add tests
- Mock external service in tests.
- Test error cases.
- Test authentication failures.

### 6) Document integration
- Document in feature `README.md`:
  - How to configure
  - How to use
  - Error handling
  - Rate limits

## Validation
- Service can be instantiated and used.
- Error handling works correctly.
- Tests pass (with mocked external service).
- Configuration is externalized (no hardcoded values).
- Documentation is complete.

## Common mistakes (avoid)
- Hardcoding API keys or URLs.
- Not handling errors properly.
- Not mocking external services in tests.
- Not documenting configuration requirements.

## Troubleshooting
- If authentication fails → check environment variables and credentials.
- If rate limits hit → implement retry logic with exponential backoff.
- If tests fail → ensure external service is properly mocked.
