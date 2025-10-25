# URL Shortener

A minimal, production-ready URL shortening service built with **FastAPI** and **SQLite**, developed using **Test-Driven Development (TDD)**.

## Features

- **Create Short URLs**: Convert long URLs into short, shareable links
- **Redirect**: Automatically redirect short URLs to their original destinations
- **Analytics**: Track visit counts for each short URL
- **Validation**: Robust URL validation and error handling
- **Idempotent**: Same URL always returns the same short code
- **100% Test Coverage**: All features tested with pytest

## Quick Start

### Installation

Dependencies are automatically installed via Claude Code SessionStart hooks. To install manually:

```bash
pip install -r requirements.txt
```

### Run the Server

```bash
# Using Make
make dev

# Or directly
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Run Tests

```bash
# Using Make
make test

# Or directly
python3 -m pytest tests/ -v
```

## API Usage

### Create a Short URL

```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url/path"}'
```

Response:
```json
{
  "code": "abc123",
  "short_url": "http://localhost:8000/abc123"
}
```

### Use the Short URL

```bash
curl -L "http://localhost:8000/abc123"
```

Redirects to `https://example.com/very/long/url/path`

### View Statistics

```bash
curl "http://localhost:8000/_stats/abc123"
```

Response:
```json
{
  "code": "abc123",
  "target": "https://example.com/very/long/url/path",
  "visits": 42
}
```

## Project Structure

```
├── app/
│   ├── main.py          # FastAPI application and endpoints
│   ├── models.py        # Database models (SQLModel)
│   └── db.py            # Database connection management
├── tests/
│   └── test_api.py      # Comprehensive test suite
├── scripts/
│   └── install_pkgs.sh  # Dependency installation
├── .claude/
│   └── settings.json    # Claude Code configuration
├── requirements.txt     # Python dependencies
├── Makefile             # Convenience commands
└── CLAUDE.md            # Detailed development guide
```

## Technology Stack

- **FastAPI**: Modern, fast web framework
- **SQLModel**: SQL databases with Python type hints
- **SQLite**: Lightweight, serverless database
- **pytest**: Testing framework
- **Ruff**: Fast Python linter
- **Uvicorn**: ASGI server

## Development

This project follows **Test-Driven Development (TDD)**:

1. ✅ Write failing tests
2. ✅ Implement features to pass tests
3. ✅ Refactor and improve

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

### Available Commands

```bash
make dev     # Start development server
make test    # Run test suite
make lint    # Lint code with ruff
make clean   # Clean cache and database files
```

## Testing

All 14 tests pass, covering:

- URL shortening (valid, invalid, edge cases)
- Redirects with visit tracking
- Statistics endpoint
- Error handling (404, 422)
- Code uniqueness and idempotency

```bash
python3 -m pytest tests/ -v
# ======================== 14 passed in 1.62s ========================
```

## Configuration

Environment variables (create `.env` from `.env.example`):

- `BASE_URL`: Base URL for short links (default: `http://localhost:8000`)
- `DATABASE_URL`: SQLite database path (default: `sqlite:///./urlshortener.db`)

## Future Enhancements

- ⏱️ TTL (Time-To-Live) for URLs
- 🎨 Custom short codes
- 🚦 Rate limiting
- 📊 Advanced analytics (referrer, timestamps)
- 🔐 API authentication
- 🌐 Web UI
- 🐳 Docker deployment
- ⚡ Redis caching

## License

MIT

## Contributing

1. Ensure tests pass: `make test`
2. Lint your code: `make lint`
3. Follow TDD approach for new features
4. Update documentation

---

**Built with Claude Code** | [Documentation](CLAUDE.md)
