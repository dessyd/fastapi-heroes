# Troubleshooting Guide

Common issues and solutions for FastAPI Heroes development and deployment.

## Development Issues

### ModuleNotFoundError

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**

1. Ensure virtual environment is activated:

   ```bash
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Verify installation:

   ```bash
   python -c "import fastapi; print(fastapi.__version__)"
   ```

### Database is Locked

**Problem:** `database.db` locked, cannot write to database

**Solution:**

```bash
# 1. Stop the server (Ctrl+C)
# 2. Remove the locked database
rm database.db

# 3. Restart the server - it will recreate the database
uvicorn app.main:app --reload
```

**Prevention:** Use only one server instance per `database.db`

### Port 8000 Already in Use

**Problem:** `Port 8000 is already in use`

**Solution:**

```bash
# Use a different port
uvicorn app.main:app --port 8001 --reload

# Or kill the process using port 8000
# Linux/Mac:
lsof -i :8000
kill -9 <PID>

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### ImportError in Tests

**Problem:** `ImportError: cannot import name 'Hero' from 'app.main'`

**Solution:**

Ensure test imports are correct:

```python
# ✅ Correct
from app.classes import Hero
from app.database import get_session

# ❌ Wrong
from app.main import Hero
```

## API Issues

### 404 Not Found Errors

**Problem:** Endpoint returns 404 even though it exists

**Causes and Solutions:**

1. **Wrong URL path:**

   ```bash
   # ✅ Correct
   curl http://localhost:8000/heroes/

   # ❌ Wrong (missing trailing slash)
   curl http://localhost:8000/heroes
   ```

2. **Wrong HTTP method:**

   ```bash
   # ✅ Correct - POST to create
   curl -X POST http://localhost:8000/heroes/

   # ❌ Wrong - GET won't work
   curl -X GET http://localhost:8000/heroes/
   ```

3. **Server not running:**

   ```bash
   # Check if server is running
   curl http://localhost:8000/docs
   ```

### 422 Unprocessable Entity

**Problem:** Request returns 422 with validation error

**Solution:**

Check request payload matches schema:

```bash
# ✅ Correct - has required fields
curl -X POST http://localhost:8000/heroes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Spider-Man", "secret_name": "Peter Parker"}'

# ❌ Wrong - missing secret_name
curl -X POST http://localhost:8000/heroes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Spider-Man"}'
```

**Check error details in response:**

```bash
curl -X POST http://localhost:8000/heroes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Spider-Man"}' | python -m json.tool
```

### 500 Internal Server Error

**Problem:** Endpoint returns 500 error

**Solution:**

1. **Check server logs:**

   ```bash
   # Terminal where server is running - look at error output
   # Or use:
   uvicorn app.main:app --reload --log-level debug
   ```

2. **Check database connection:**

   ```bash
   # Verify database.db exists and is readable
   ls -la database.db
   ```

3. **Check for syntax errors:**

   ```bash
   # Run Python syntax check
   python -m py_compile app/main.py
   python -m py_compile app/routers/heroes.py
   ```

## Testing Issues

### Tests Fail Unexpectedly

**Problem:** Tests pass locally but fail in CI/CD

**Solution:**

1. **Ensure clean database state:**

   ```bash
   # Clear any existing data
   rm database.db

   # Run tests
   python -m pytest app/test_main.py -v
   ```

2. **Check test isolation:**

   - Each test should use fresh in-memory SQLite
   - Check `test_main.py` fixtures use `StaticPool`

3. **Verify dependencies versions:**

   ```bash
   pip install -r requirements.txt --upgrade
   python -m pytest app/test_main.py -v
   ```

### Coverage Report Issues

**Problem:** Coverage report shows low coverage

**Solution:**

```bash
# Generate detailed coverage report
python -m pytest app/test_main.py --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Code Quality Issues

### Flake8 Violations

**Problem:** `E501 line too long`

**Solution:**

```bash
# Check violations
python -m flake8 app/ --max-line-length=79

# Fix line breaks in long lines
# Split long function definitions:
def my_function(
    param1: str,
    param2: int,
    param3: bool,
):
    pass

# Split long imports:
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
```

### Type Checking Errors

**Problem:** Type hints cause issues

**Solution:**

```bash
# Check types with mypy
python -m mypy app/

# Common fixes:
# 1. Use modern syntax: X | None instead of Optional[X]
# 2. Use list[X] instead of List[X]
# 3. Add return type hints to functions
```

## Deployment Issues

### Docker Build Fails

**Problem:** Docker image won't build

**Solution:**

```bash
# Check Dockerfile syntax
docker build --no-cache -t fastapi-heroes:latest .

# View build logs
docker build -t fastapi-heroes:latest . 2>&1 | head -50

# Common issues:
# - Requirements.txt not found
# - Wrong base image Python version
# - Missing system dependencies
```

### Database Connection Errors

**Problem:** Cannot connect to PostgreSQL in production

**Solution:**

1. **Check DATABASE_URL format:**

   ```bash
   # ✅ Correct
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/heroesdb

   # ❌ Wrong
   DATABASE_URL=postgres://user:password@localhost:5432/heroesdb  # Old driver
   ```

2. **Verify database is running:**

   ```bash
   # Test connection
   psql -U username -d database_name -h localhost -c "SELECT version();"
   ```

3. **Check firewall rules:**

   ```bash
   # Ensure database port 5432 is accessible
   nc -zv localhost 5432
   ```

4. **Check environment variables:**

   ```bash
   # Verify DATABASE_URL is set
   echo $DATABASE_URL

   # If not set, load .env file
   export $(cat .env | xargs)
   ```

### Health Check Failures

**Problem:** Docker health check fails

**Solution:**

```bash
# Debug health check endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-12-13T..."}

# Check health check configuration in docker-compose.yml
# Increase timeout if endpoint is slow:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s  # Increase if needed
  retries: 3
```

## Performance Issues

### Slow API Response

**Problem:** Endpoints respond slowly

**Solution:**

1. **Check database queries:**

   ```python
   # Enable SQL logging to see queries
   import logging
   logging.basicConfig()
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

2. **Add database indexes:**

   ```python
   # In classes.py
   class Hero(SQLModel, table=True):
       id: int | None = Field(default=None, primary_key=True)
       name: str = Field(index=True)  # Add index for fast lookups
   ```

3. **Use pagination:**

   ```bash
   # Always use limits
   curl "http://localhost:8000/heroes/?limit=10&offset=0"

   # Don't fetch all records at once
   # ❌ BAD
   curl "http://localhost:8000/heroes/"

   # ✅ GOOD
   curl "http://localhost:8000/heroes/?limit=100"
   ```

4. **Check resource usage:**

   ```bash
   # Monitor CPU and memory
   ps aux | grep uvicorn
   top -p <PID>  # macOS/Linux
   tasklist /v | findstr uvicorn  # Windows
   ```

### High Memory Usage

**Problem:** Application uses excessive memory

**Solution:**

1. **Reduce worker count:**

   ```bash
   # Use fewer workers
   gunicorn --workers 2 app.main:app
   ```

2. **Clear caches:**

   ```bash
   # Restart application to clear in-memory caches
   systemctl restart fastapi-heroes
   ```

3. **Monitor connections:**

   ```python
   # Check database connection pool settings in production
   # In database.py, adjust pool size:
   engine = create_engine(
       DATABASE_URL,
       echo=False,
       pool_size=5,        # Reduce if high memory
       max_overflow=10,
   )
   ```

## Getting Help

If you can't resolve an issue:

1. **Check logs carefully:**

   ```bash
   # Full error traceback helps debugging
   tail -50 /var/log/fastapi-heroes.log
   ```

2. **Reproduce with minimal example:**

   ```python
   # Create simple test case to isolate problem
   ```

3. **Check official documentation:**

   - [FastAPI Docs](https://fastapi.tiangolo.com/)
   - [SQLModel Docs](https://sqlmodel.tiangolo.com/)
   - [Pydantic Docs](https://docs.pydantic.dev/)

4. **Search existing issues:**

   - GitHub repository issues
   - Stack Overflow tagged with `fastapi` and `sqlmodel`

5. **Enable debug logging:**

   ```bash
   # Run with full debug output
   uvicorn app.main:app --reload --log-level debug
   ```

---

## Quick Reference

| Issue | Quick Fix |
| ------- | ----------- |
| Module not found | `source .venv/bin/activate && pip install -r requirements.txt` |
| Database locked | `rm database.db && restart server` |
| Port in use | `uvicorn app.main:app --port 8001` |
| 404 error | Check URL path and HTTP method |
| 422 validation error | Check JSON payload matches schema |
| Test failures | `rm database.db && python -m pytest app/test_main.py -v` |
| Slow response | Enable SQL logging, add indexes, use pagination |
| Flake8 errors | `python -m flake8 app/` then fix line breaks |
