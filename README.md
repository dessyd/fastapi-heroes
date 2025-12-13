# FastAPI Heroes API

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.117+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready REST API demonstrating **FastAPI** and **SQLModel** best practices with async database operations, type-safe models, and comprehensive testing.

## Quick Start

Get your first hero API running in **60 seconds**:

```bash
# Clone and setup
git clone https://github.com/dessyd/fastapi-heroes.git
cd fastapi-heroes
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

Expected output: `Uvicorn running on http://127.0.0.1:8000`

**Verify it works:**

```bash
curl http://localhost:8000/heroes
# Output: []
```

**Create your first hero:** Open [http://localhost:8000/docs](http://localhost:8000/docs) → POST /heroes → Try it out

### Docker Setup (Development)

```bash
# Build and start the container
docker compose up

# API will be available at http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### Docker Production Deployment

```bash
# Set database password
export DB_PASSWORD=your_secure_password_here

# Start with PostgreSQL and nginx
docker compose -f compose.prod.yml up -d

# View logs
docker compose -f compose.prod.yml logs -f api
```

See [Production Deployment](docs/PRODUCTION_DEPLOYMENT.md) for detailed setup.

## Features

✨ **Core Features:**

- Create, read, update, and delete (CRUD) heroes
- Manage superhero teams with team-hero relationships
- Paginated list endpoints
- Comprehensive input validation
- Proper HTTP status codes

🔒 **Code Quality:**

- Type-safe models with Python 3.10+ syntax
- Pydantic v2 validation
- FastAPI lifespan context managers
- Clean separation of concerns
- Full test coverage (7/7 tests passing)
- PEP 8 compliant (line length < 79 characters)
- Production-ready deployment guides

## Documentation

Complete documentation is organized in the `docs/` directory:

| Document | Purpose |
|----------|---------|
| [📋 Configuration Guide](docs/CONFIGURATION.md) | Environment variables, database setup, and environment-specific settings |
| [🚀 Usage Examples](docs/USAGE_EXAMPLES.md) | Real-world scenarios, integration patterns, and code examples |
| [🏗️ Architecture Guide](docs/ARCHITECTURE.md) | System design, component breakdown, data flow, and performance |
| [🌐 Production Deployment](docs/PRODUCTION_DEPLOYMENT.md) | Deployment options (traditional, Docker, Kubernetes), scaling, and security |

### Quick Navigation

- **Just getting started?** → Follow [Quick Start](#quick-start) above
- **Setting up environment variables?** → See [Configuration Guide](docs/CONFIGURATION.md)
- **Want code examples and integration patterns?** → Check [Usage Examples](docs/USAGE_EXAMPLES.md)
- **Understanding system design and architecture?** → Read [Architecture Guide](docs/ARCHITECTURE.md)
- **Ready to deploy to production?** → Follow [Production Deployment](docs/PRODUCTION_DEPLOYMENT.md)

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.117.1 | Web framework |
| **SQLModel** | 0.0.25 | ORM + validation |
| **Pydantic** | 2.11.9 | Data validation |
| **Uvicorn** | 0.38.0 | ASGI server |
| **SQLite** | Built-in | Development database |
| **pytest** | 8.2.2 | Testing framework |
| **Python** | 3.14.2 | Runtime |

## Project Structure

```
fastapi-heroes/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── classes.py           # SQLModel data models & schemas
│   ├── database.py          # Database configuration & session
│   ├── test_main.py         # Comprehensive test suite
│   └── routers/
│       ├── heroes.py        # Hero CRUD endpoints
│       └── teams.py         # Team CRUD endpoints
├── docs/
│   ├── CONFIGURATION.md     # Environment and settings
│   ├── USAGE_EXAMPLES.md    # Real-world scenarios
│   ├── ARCHITECTURE.md      # System design and diagrams
│   └── PRODUCTION_DEPLOYMENT.md  # Deployment guides
├── requirements.txt         # Pinned dependencies
├── .pre-commit-config.yaml  # Pre-commit hooks
├── database.db             # SQLite database (generated)
└── README.md               # This file
```

## API Endpoints

The API provides two main resources:

### Heroes (`/heroes`)

- **POST** `/heroes/` - Create a new hero
- **GET** `/heroes/` - List all heroes (paginated)
- **GET** `/heroes/{hero_id}` - Get single hero with team info
- **PATCH** `/heroes/{hero_id}` - Update hero (partial)
- **DELETE** `/heroes/{hero_id}` - Delete hero

### Teams (`/teams`)

- **POST** `/teams/` - Create a new team
- **GET** `/teams/` - List all teams (paginated)
- **GET** `/teams/{team_id}` - Get team with related heroes
- **PATCH** `/teams/{team_id}` - Update team (partial)
- **DELETE** `/teams/{team_id}` - Delete team

**Full API documentation:** Interactive API docs available at `/docs` (Swagger UI) or `/redoc` (ReDoc)

## Testing

Run tests with pytest:

```bash
# All tests
python -m pytest app/test_main.py -v

# With coverage report
python -m pytest app/test_main.py --cov=app

# Specific test
python -m pytest app/test_main.py::test_create_hero -v
```

**Test coverage:** All 7 tests passing ✅

- Hero CRUD operations (create, read, list, update, delete)
- Input validation (incomplete and invalid requests)
- Team relationships

## Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/new-endpoint`
2. Make changes and test: `pytest app/test_main.py -v`
3. Check code style: `flake8 app/`
4. Commit: `git commit -m "feat: add new endpoint"`
5. Push and create PR

### Code Review Checklist

- Tests pass and new tests added
- Code style: flake8, black
- Type hints present
- Documentation updated
- No hardcoded secrets

## License

MIT License - See [LICENSE](LICENSE) file for details

## Authors

Created as a modern example of FastAPI and SQLModel best practices.

---

**Last Updated**: 2025-12-13
**Python Version**: 3.14.2
**FastAPI Version**: 0.117.1
**SQLModel Version**: 0.0.25
