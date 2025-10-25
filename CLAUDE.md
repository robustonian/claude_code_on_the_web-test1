# CLAUDE.md - Development Guide for URL Shortener

This document provides guidance for Claude Code and developers working on this project.

## Project Overview

A minimal URL shortening service built with FastAPI and SQLite, developed using **Test-Driven Development (TDD)**.

### Key Features

- **POST /shorten**: Create short URLs
- **GET /{code}**: Redirect to original URLs
- **GET /_stats/{code}**: View URL statistics (visits count)
- URL validation with proper scheme checking
- Visit tracking
- Duplicate URL detection (returns existing code)

## Architecture

```
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── models.py        # SQLModel database models
│   └── db.py            # Database connection and session management
├── tests/
│   ├── __init__.py
│   └── test_api.py      # Comprehensive test suite (TDD)
├── scripts/
│   └── install_pkgs.sh  # Dependency installation script
├── .claude/
│   └── settings.json    # Claude Code configuration (SessionStart hooks)
├── requirements.txt     # Python dependencies
├── Makefile             # Convenience commands
└── .env.example         # Environment variable template
```

## API Specification

### POST /shorten

Create a short URL.

**Request:**
```json
{
  "url": "https://example.com/very/long/url/path"
}
```

**Response (200 OK):**
```json
{
  "code": "abc123",
  "short_url": "http://localhost:8000/abc123"
}
```

**Validation:**
- URL must start with `http://` or `https://`
- URL cannot be empty or contain spaces
- Returns 422 for validation errors

**Behavior:**
- If URL already exists, returns existing short code (idempotent)
- Generates 6-character alphanumeric code
- Ensures code uniqueness

### GET /{code}

Redirect to the original URL.

**Response:**
- 307 Temporary Redirect to original URL
- 404 if code doesn't exist
- Increments visit counter

### GET /_stats/{code}

Get statistics for a short URL.

**Response (200 OK):**
```json
{
  "code": "abc123",
  "target": "https://example.com/very/long/url/path",
  "visits": 42
}
```

## Development Setup

### Environment Check

Use `check-tools` to verify available tools:

```bash
check-tools
```

**Available tools (as of this session):**
- Python 3.11.14
- pytest 8.4.2
- ruff 0.14.1
- uvicorn, fastapi, sqlmodel (via pip)

### Automated Dependency Installation

Dependencies are automatically installed via **SessionStart hooks** configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "bash scripts/install_pkgs.sh",
        "description": "Install Python dependencies automatically"
      }
    ]
  }
}
```

The `scripts/install_pkgs.sh` script:
- Checks for `$CLAUDE_CODE_REMOTE` environment variable
- Installs dependencies from `requirements.txt`
- Works in both local and remote (Claude Code on the web) environments

### Manual Installation

If needed, install dependencies manually:

```bash
python3 -m pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Variables:
- `BASE_URL`: Base URL for short links (default: `http://localhost:8000`)
- `DATABASE_URL`: SQLite database path (default: `sqlite:///./urlshortener.db`)

## Running the Application

### Using Makefile

```bash
make dev     # Start development server
make test    # Run tests
make clean   # Clean cache and database files
make lint    # Run ruff linter
```

### Manual Commands

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python3 -m pytest tests/ -v

# Run tests with coverage
python3 -m pytest tests/ --cov=app --cov-report=html

# Lint code
ruff check app/ tests/
```

## Testing

This project was built using **Test-Driven Development (TDD)**:

1. **Red**: Write failing tests first (`tests/test_api.py`)
2. **Green**: Implement code to make tests pass
3. **Refactor**: Clean up while keeping tests green

### Test Coverage

All 14 tests pass, covering:
- ✅ Valid URL shortening
- ✅ HTTP and HTTPS schemes
- ✅ URL validation (missing scheme, invalid format, empty)
- ✅ Redirects with visit tracking
- ✅ Statistics endpoint
- ✅ 404 for non-existent codes
- ✅ Code uniqueness
- ✅ Duplicate URL handling (idempotency)

### Running Tests

```bash
# All tests
make test

# Specific test file
python3 -m pytest tests/test_api.py -v

# Specific test
python3 -m pytest tests/test_api.py::TestShortenEndpoint::test_shorten_valid_url -v

# With output
python3 -m pytest tests/ -v -s
```

## Database

### Production Database

- **Type**: SQLite
- **File**: `urlshortener.db` (created automatically)
- **Schema**: See `app/models.py` (URLMapping model)

### Test Database

- **Type**: SQLite
- **File**: `test.db` (recreated for each test)
- **Isolation**: Each test gets a fresh database

### Schema

```python
class URLMapping:
    id: int (primary key)
    code: str (unique, indexed)
    target_url: str
    visits: int (default: 0)
```

## Code Quality

### Linting

```bash
make lint  # or
ruff check app/ tests/
```

### Formatting

```bash
ruff format app/ tests/
```

## Branch Strategy

- **Development Branch**: `claude/url-shortener-tdd-011CUTBhGQHvF7FVzW24cu1u`
- All development happens on this branch
- PRs are created against the main branch

## Common Tasks

### Adding a New Endpoint

1. Write tests first in `tests/test_api.py`
2. Run tests to see them fail (Red)
3. Implement endpoint in `app/main.py`
4. Run tests until they pass (Green)
5. Refactor if needed

### Adding New Dependencies

1. Add to `requirements.txt`
2. Run `pip install -r requirements.txt`
3. Commit `requirements.txt`
4. SessionStart hooks will auto-install for new sessions

### Debugging

```bash
# Run server with debug logging
uvicorn app.main:app --reload --log-level debug

# Run single test with output
python3 -m pytest tests/test_api.py::test_name -v -s
```

## Future Enhancements

Potential improvements for this project:

1. **TTL (Time-To-Live)**: Expire short URLs after a certain period
2. **Custom Codes**: Allow users to specify custom short codes
3. **Rate Limiting**: Prevent abuse with request throttling
4. **Analytics**: Track more detailed statistics (referrer, user agent, timestamps)
5. **Authentication**: Require API keys for creating short URLs
6. **Web UI**: Simple frontend for creating/managing short URLs
7. **Redis Cache**: Cache frequently accessed URLs
8. **PostgreSQL**: Production-ready database for scalability
9. **Docker**: Containerize the application
10. **CI/CD**: GitHub Actions for automated testing and deployment

## Claude Code Integration

### SessionStart Hooks

Dependencies are auto-installed when starting a new Claude Code session via hooks defined in `.claude/settings.json`.

### AGENTS.md Integration Example

While not implemented in this project, you can integrate with @AGENTS.md for more complex workflows:

```markdown
# Example @AGENTS.md usage
@agent code-reviewer: Review pull requests for security and best practices
@agent test-runner: Run full test suite and report coverage
```

### check-tools Usage

Always verify your environment before starting work:

```bash
check-tools
```

This helps Claude understand what tools are available (Python version, testing frameworks, linters, etc.).

## Troubleshooting

### Tests Failing

```bash
# Clean and re-run
make clean
make test
```

### Database Issues

```bash
# Remove databases and restart
rm -f *.db
uvicorn app.main:app --reload
```

### Dependencies Not Installing

```bash
# Manual install
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Contributing

1. Ensure all tests pass: `make test`
2. Lint your code: `make lint`
3. Write tests for new features (TDD approach)
4. Update this CLAUDE.md if adding new functionality
5. Commit with descriptive messages
6. Push to your branch
7. Create a pull request

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **pytest Documentation**: https://docs.pytest.org/
- **Claude Code Documentation**: https://docs.claude.com/claude-code/

---

**Last Updated**: 2025-10-25
**Claude Code Version**: Sonnet 4.5 (claude-sonnet-4-5-20250929)
**Python Version**: 3.11.14
