# Configuration Guide

## Environment Variables

FastAPI Heroes uses environment variables for configuration. Create a `.env` file in the project root with the following settings:

### Development Environment

```bash
# Database configuration (default: SQLite)
DATABASE_URL=sqlite:///./heroes.db

# Logging level
LOG_LEVEL=debug

# Debug mode
DEBUG=true

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# API settings
API_V1_PREFIX=/api/v1
```

### Production Example

```bash
# PostgreSQL database (recommended for production)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/heroesdb

# Logging level
LOG_LEVEL=info

# Debug mode OFF
DEBUG=false

# CORS origins (restrict to your domain)
CORS_ORIGINS=https://example.com,https://www.example.com

# Security headers
ALLOWED_HOSTS=example.com,www.example.com
SECRET_KEY=your-secret-key-here-change-in-production
```

## Database Configuration

### SQLite (Development)

Default configuration uses SQLite, which requires no setup:

```python
# app/database.py
sqlite_file_name = "heroes.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)
```

**Pros:**

- Zero setup
- No external dependencies
- Perfect for development and testing

**Cons:**

- Single-threaded writes
- Not suitable for high concurrency

### PostgreSQL (Production)

For production, use PostgreSQL with async driver:

```bash
# 1. Install PostgreSQL driver
pip install asyncpg

# 2. Set environment variable
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/heroesdb

# 3. Create database
createdb heroesdb

# 4. Run application
uvicorn app.main:app
```

**Connection string format:**

```python
postgresql+asyncpg://username:password@host:port/database
```

**Example with environment variable:**

```bash
export DATABASE_URL="postgresql+asyncpg://heroesadmin:securepass@db.example.com:5432/heroes_prod"
uvicorn app.main:app
```

### MySQL (Alternative)

```bash
# Install MySQL driver
pip install aiomysql

# Connection string
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/heroesdb
```

## Docker Configuration

### Environment Variables in Docker

Create `.env.docker`:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/heroesdb
LOG_LEVEL=info
DEBUG=false
```

Use in docker-compose:

```yaml
services:
  api:
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/heroesdb
      - LOG_LEVEL=info
```

Or load from file:

```yaml
services:
  api:
    env_file:
      - .env.docker
```

## Application Settings

### Logging Configuration

```python
# app/config.py
import logging
from os import getenv

LOG_LEVEL = getenv("LOG_LEVEL", "info").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### CORS Settings

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Configuration Examples

### Local Development

```bash
# .env (local development)
DATABASE_URL=sqlite:///./heroes_dev.db
LOG_LEVEL=debug
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Docker Development

```bash
# docker-compose.yml
services:
  api:
    environment:
      - DATABASE_URL=sqlite:///./heroes_docker.db
      - LOG_LEVEL=debug
      - DEBUG=true
```

### Staging Environment

```bash
# .env.staging
DATABASE_URL=postgresql+asyncpg://user:password@staging-db.example.com/heroes
LOG_LEVEL=info
DEBUG=false
CORS_ORIGINS=https://staging.example.com
```

### Production Environment

```bash
# .env.production (never commit!)
DATABASE_URL=postgresql+asyncpg://prod_user:$(pass show prod/db_password)@prod-db.example.com/heroes_prod
LOG_LEVEL=info
DEBUG=false
CORS_ORIGINS=https://example.com,https://www.example.com
SECRET_KEY=$(openssl rand -hex 32)
```

## Best Practices

1. **Never commit `.env` files**

   ```bash
   echo ".env*" >> .gitignore
   ```

2. **Use `.env.example` for documentation**

   ```bash
   # .env.example
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/heroesdb
   LOG_LEVEL=info
   DEBUG=false
   ```

3. **Use strong database passwords in production**

   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

4. **Restrict database access**
   - Create separate database users for different environments
   - Use read-only users for read operations where possible
   - Limit connection from specific IPs

5. **Use secrets management for production**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Google Cloud Secret Manager
   - Azure Key Vault

## Troubleshooting Configuration

### Connection String Issues

**Error:** `could not translate host name "localhost" to address`

- **Cause:** Database host not reachable
- **Solution:** Check database is running and host is correct

**Error:** `permission denied for schema public`

- **Cause:** User doesn't have permissions
- **Solution:** Grant permissions to user on database

### Environment Variable Not Read

**Error:** Variable not set despite being in `.env`

- **Solution:** Ensure `.env` file is in project root
- **Solution:** Restart application after changing `.env`

See [Troubleshooting Guide](TROUBLESHOOTING.md) for more issues.
