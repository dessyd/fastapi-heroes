# Contributing Guide

Thank you for your interest in contributing to FastAPI Heroes! This guide will help you get started with development.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip (Python package manager)

### Initial Setup

1. **Fork the repository** (optional, for external contributors)

2. **Clone the repository:**

   ```bash
   git clone https://github.com/dessyd/fastapi-heroes.git
   cd fastapi-heroes
   ```

3. **Create a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Verify setup:**

   ```bash
   # Run tests to ensure everything works
   python -m pytest app/test_main.py -v

   # Check linting
   python -m flake8 app/ --max-line-length=79
   ```

## Development Workflow

### Before Starting Work

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Keep main up to date:**

   ```bash
   git fetch origin
   git rebase origin/main
   ```

### Making Changes

#### Code Style

The project follows strict PEP 8 standards:

- **Line length:** Maximum 79 characters (enforced)
- **Type hints:** Required for all functions (Python 3.10+ syntax)
- **Imports:** Alphabetically sorted, organized in groups

#### Example of Good Code

```python
# ✅ Good: Type hints, proper line length, clear logic
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from .. import classes
from ..database import get_session

router = APIRouter(prefix="/heroes", tags=["Heroes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_hero(
    *,
    session: Session = Depends(get_session),
    hero: classes.HeroCreate,
):
    """Create a new hero."""
    db_hero = classes.Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

#### Example of Poor Code

```python
# ❌ Bad: No type hints, line too long, unclear logic
def create_hero(session, hero):
    db_hero = classes.Hero(**hero.dict()); session.add(db_hero); session.commit(); session.refresh(db_hero); return db_hero
```

### Writing Tests

Every feature or bug fix should include tests. Use the existing test structure:

```python
def test_your_feature(client: TestClient):
    """Test description here."""
    # Arrange
    test_data = {"name": "Test", "secret_name": "Secret"}

    # Act
    response = client.post("/heroes/", json=test_data)
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["name"] == "Test"
```

**Test Guidelines:**

- Use the AAA pattern: Arrange, Act, Assert
- Test both success and failure cases
- Use descriptive test names
- Keep tests isolated (no shared state)

### Running Quality Checks

Before committing, run all checks:

```bash
# Run tests
python -m pytest app/test_main.py -v

# Check code style
python -m flake8 app/ --max-line-length=79

# Check type hints (optional, but recommended)
python -m mypy app/ --strict

# Check test coverage
python -m pytest app/test_main.py --cov=app --cov-report=term-missing
```

## Commit Guidelines

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring (no feature change)
- `test`: Test additions or modifications
- `docs`: Documentation updates
- `style`: Code style changes (formatting, etc.)
- `chore`: Build process, dependency updates

**Examples:**

```bash
git commit -m "feat(heroes): add hero filtering by team"
git commit -m "fix(database): resolve connection pool issue"
git commit -m "test(heroes): add test for hero deletion"
git commit -m "docs: update configuration guide"
```

### Making a Commit

1. **Stage changes:**

   ```bash
   git add app/routers/heroes.py
   git add app/test_main.py
   ```

2. **Commit:**

   ```bash
   git commit -m "feat(heroes): add bulk hero creation endpoint"
   ```

3. **Push to your branch:**

   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Process

### Before Submitting PR

**Checklist:**

- [ ] Tests pass: `python -m pytest app/test_main.py -v`
- [ ] Code style passes: `python -m flake8 app/ --max-line-length=79`
- [ ] Type hints complete: `python -m mypy app/ --strict`
- [ ] Documentation updated (if applicable)
- [ ] No hardcoded secrets or credentials
- [ ] Branch is up to date with main: `git rebase origin/main`

### Creating a Pull Request

1. **Push your branch:**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub:**

   - Title: Clear, descriptive title
   - Description: Explain changes and why they're needed

3. **PR Description Template:**

   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing Done
   Describe test cases

   ## Checklist
   - [ ] Tests pass
   - [ ] Code style passes
   - [ ] Documentation updated
   - [ ] No hardcoded secrets
   ```

### Code Review

- Address reviewer feedback promptly
- Push additional commits to the same branch
- Don't force push (unless instructed)
- Keep discussions professional and focused

## Adding New Features

### Adding a New Endpoint

1. **Define models in `app/classes.py`:**

   ```python
   class PowerBase(SQLModel):
       name: str
       description: str

   class PowerCreate(PowerBase):
       pass

   class Power(PowerBase, table=True):
       id: int | None = Field(default=None, primary_key=True)
   ```

2. **Create router in `app/routers/powers.py`:**

   ```python
   from fastapi import APIRouter, Depends, HTTPException, status
   from sqlmodel import Session, select

   from .. import classes
   from ..database import get_session

   router = APIRouter(prefix="/powers", tags=["Powers"])

   @router.post("/", status_code=status.HTTP_201_CREATED)
   def create_power(
       *,
       session: Session = Depends(get_session),
       power: classes.PowerCreate,
   ):
       db_power = classes.Power.model_validate(power)
       session.add(db_power)
       session.commit()
       session.refresh(db_power)
       return db_power
   ```

3. **Register router in `app/main.py`:**

   ```python
   from app.routers import heroes, teams, powers

   app.include_router(heroes.router)
   app.include_router(teams.router)
   app.include_router(powers.router)  # Add this
   ```

4. **Write tests in `app/test_main.py`:**

   ```python
   def test_create_power(client: TestClient):
       response = client.post(
           "/powers/",
           json={"name": "Flight", "description": "Ability to fly"}
       )
       assert response.status_code == 201
       assert response.json()["name"] == "Flight"
   ```

5. **Update documentation:**

   - Update `docs/USAGE_EXAMPLES.md` with example requests
   - Update `docs/ARCHITECTURE.md` if schema changed

### Updating Dependencies

**Requirements:**

- Dependencies must be pinned to specific versions
- Use compatible release operator: `~=`
- Update `requirements.txt` and document changes

**Example:**

```bash
# Update a package
pip install --upgrade fastapi

# Check new version
pip show fastapi

# Update requirements.txt
pip freeze | grep fastapi > requirements.txt
```

## Database Changes

### Adding a New Table

1. **Define model in `app/classes.py` with `table=True`**

2. **The database schema updates automatically** on app startup (see `main.py` lifespan)

3. **For production migrations**, consider using Alembic (optional):

   ```bash
   pip install alembic
   alembic init migrations
   alembic revision --autogenerate -m "add new table"
   alembic upgrade head
   ```

## Performance Considerations

When adding features:

- Use database indexes for frequently queried fields
- Implement pagination for list endpoints
- Use async/await for I/O operations
- Avoid N+1 queries (eager load relationships)

## Documentation

### Update Documentation For:

- **New features** → Update `docs/USAGE_EXAMPLES.md`
- **Configuration changes** → Update `docs/CONFIGURATION.md`
- **Architecture changes** → Update `docs/ARCHITECTURE.md`
- **Deployment changes** → Update `docs/PRODUCTION_DEPLOYMENT.md`

## Security Guidelines

### Never Commit:

- `.env` files with secrets
- API keys, tokens, or credentials
- Database passwords in code
- Private configuration

### Always Use:

- Environment variables for secrets
- `.env.example` template for configuration
- Validation for user inputs
- Proper error handling

## Getting Help

- **Questions about setup?** → Check [CONFIGURATION.md](CONFIGURATION.md)
- **Not sure how something works?** → Check [ARCHITECTURE.md](ARCHITECTURE.md)
- **Stuck on an issue?** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Need examples?** → Check [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)

## Code Review Checklist

As a reviewer, ensure:

- [ ] Code follows PEP 8 (79 character lines)
- [ ] Type hints present on all functions
- [ ] Tests added/updated
- [ ] No hardcoded secrets
- [ ] Database migrations handled (if needed)
- [ ] Documentation updated
- [ ] No breaking changes to API (or documented)
- [ ] Performance acceptable (no N+1 queries)
- [ ] Error handling appropriate

## Project Philosophy

This project follows these principles:

1. **Type Safety** - All code is type-hinted using Python 3.10+ syntax
2. **Modern Patterns** - Uses latest FastAPI/SQLModel/Pydantic v2 features
3. **Testing** - High test coverage and comprehensive test suite
4. **Documentation** - Clear, modular documentation for all aspects
5. **Performance** - Async by default, proper indexing, pagination
6. **Security** - Secure by default, environment-based configuration

## Questions or Suggestions?

- Open an issue on GitHub
- Check existing issues and discussions
- Follow the contribution guidelines above

Happy coding! 🚀
