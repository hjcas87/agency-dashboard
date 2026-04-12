# Testing Strategy

> This document needs to be completed.

## Test Types

### Unit Tests
- **Location**: `backend/tests/unit/`
- **Scope**: Pure logic — services, utilities, helpers
- **Speed**: Fast, no external dependencies
- **Run**: `make test-unit`

### Integration Tests
- **Location**: `backend/tests/integration/`
- **Scope**: API endpoints, database operations, external services (mocked)
- **Run**: `make test-integration`

### E2E Tests
- **Location**: `backend/tests/e2e/`
- **Scope**: Complete user flows with all services running
- **Run**: `make test` (all tests)

## Coverage Target

- Minimum: 80%
- Enforced via `--cov-fail-under=80` in pytest config

## Running Tests

```bash
make test           # All tests
make test-unit      # Unit tests only
make test-cov       # Tests with coverage report
```

## Test Conventions

- **Naming**: `test_<what>_<condition>_<expected_result>`
- **Pattern**: Arrange → Act → Assert
- **Fixtures**: Use `conftest.py` for shared fixtures
- **Mocks**: Use `pytest-mock` for external services
