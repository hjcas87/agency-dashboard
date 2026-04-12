---
name: deploy
description: Prepare and deploy the application to production using Docker Compose with Traefik. Use when deploying to production, preparing releases, or updating production environment.
---

# Deploy Application

## When to use
- Deploying to production environment
- Preparing a release
- Updating production deployment

## Preconditions
- All migrations created and tested
- Environment variables configured
- Tests pass

## Steps

### 1) Verify database migrations
- Ensure all migrations applied in development
- Review migration files for production compatibility

### 2) Update environment variables
- Verify all required env vars set in production
- Check secrets are properly configured
- Verify API keys and tokens

### 3) Build Docker images
```bash
docker-compose -f docker-compose.prod.yml build
```

### 4) Run database migrations
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 5) Start services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 6) Verify deployment
- Check all services are running
- Verify API endpoints accessible
- Check application logs for errors
- Test critical user flows

### 7) Monitor
- Monitor application logs
- Check error rates
- Verify background tasks executing

## Validation
- All services running
- Database migrations applied
- API endpoints accessible
- No critical errors in logs

## Common mistakes
- Not running migrations before starting services
- Missing environment variables
- Not verifying deployment after start
