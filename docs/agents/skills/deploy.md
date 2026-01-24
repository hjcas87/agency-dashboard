# Skill — Deploy Application

Tags: [deploy] [production] [release]

## Goal
Prepare and deploy the application to production.

## When to use
- Deploying to production environment.
- Preparing a release.
- Updating production deployment.

## Preconditions
- All migrations are created and tested.
- Environment variables are configured.
- Docker images are built.
- Tests pass.

## Steps (MANDATORY ORDER)

### 1) Verify database migrations
- Ensure all migrations are applied in development.
- Review migration files for production compatibility.
- Plan migration order if multiple migrations exist.

### 2) Update environment variables
- Verify all required environment variables are set in production.
- Check secrets are properly configured.
- Verify API keys and tokens.

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
- Check all services are running.
- Verify API endpoints are accessible.
- Check application logs for errors.
- Test critical user flows.

### 7) Monitor
- Monitor application logs.
- Check error rates.
- Verify background tasks are executing.
- Monitor database connections.

## Validation
- All services are running.
- Database migrations applied successfully.
- API endpoints are accessible.
- Application logs show no critical errors.
- Critical user flows work.

## Common mistakes (avoid)
- Not running migrations before starting services.
- Missing environment variables.
- Not verifying deployment after start.
- Not monitoring logs and errors.

## Troubleshooting
- If services don't start → check Docker logs and environment variables.
- If migrations fail → check database connection and migration files.
- If API errors → check application logs and service health.
