"""
Test suite for URL shortener API using TDD approach.

These tests define the expected behavior before implementation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel
from app.main import app, get_db
from app.db import test_engine


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Ensure clean state - drop and recreate tables
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)

    # Create session that will be shared across all requests in this test
    session = Session(test_engine, expire_on_commit=False)

    yield session

    # Cleanup - close session but don't drop tables yet
    # (they'll be dropped at the start of the next test)
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def get_test_db_override():
        # Return the same session for all requests in this test
        yield db_session

    app.dependency_overrides[get_db] = get_test_db_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


class TestShortenEndpoint:
    """Tests for POST /shorten endpoint."""

    def test_shorten_valid_url(self, client):
        """Test creating a short URL with a valid URL."""
        response = client.post(
            "/shorten",
            json={"url": "https://example.com/very/long/url/path"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "short_url" in data
        assert len(data["code"]) == 6  # Default code length
        assert data["short_url"].endswith(data["code"])

    def test_shorten_url_with_http(self, client):
        """Test creating a short URL with http scheme."""
        response = client.post(
            "/shorten",
            json={"url": "http://example.com/path"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "short_url" in data

    def test_shorten_invalid_url_no_scheme(self, client):
        """Test that URL without scheme returns 422 (validation error)."""
        response = client.post(
            "/shorten",
            json={"url": "example.com"}
        )
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_shorten_invalid_url_format(self, client):
        """Test that invalid URL format returns 422 (validation error)."""
        response = client.post(
            "/shorten",
            json={"url": "not-a-url"}
        )
        assert response.status_code == 422

    def test_shorten_empty_url(self, client):
        """Test that empty URL returns 422 (validation error)."""
        response = client.post(
            "/shorten",
            json={"url": ""}
        )
        assert response.status_code == 422

    def test_shorten_missing_url_field(self, client):
        """Test that missing URL field returns 422."""
        response = client.post(
            "/shorten",
            json={}
        )
        assert response.status_code == 422


class TestRedirectEndpoint:
    """Tests for GET /{code} endpoint."""

    def test_redirect_existing_code(self, client):
        """Test that valid code redirects to original URL."""
        # First create a short URL
        create_response = client.post(
            "/shorten",
            json={"url": "https://example.com/target"}
        )
        code = create_response.json()["code"]

        # Then try to access it
        response = client.get(f"/{code}", follow_redirects=False)
        assert response.status_code in [307, 308]  # Temporary or permanent redirect
        assert response.headers["location"] == "https://example.com/target"

    def test_redirect_nonexistent_code(self, client):
        """Test that nonexistent code returns 404."""
        response = client.get("/nonexistent123")
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_redirect_increments_visit_count(self, client):
        """Test that accessing a short URL increments visit count."""
        # Create short URL
        create_response = client.post(
            "/shorten",
            json={"url": "https://example.com/counted"}
        )
        code = create_response.json()["code"]

        # Access it multiple times
        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)

        # Check stats
        stats_response = client.get(f"/_stats/{code}")
        assert stats_response.status_code == 200
        assert stats_response.json()["visits"] == 3


class TestStatsEndpoint:
    """Tests for GET /_stats/{code} endpoint."""

    def test_stats_existing_code(self, client):
        """Test getting stats for existing code."""
        # Create short URL
        create_response = client.post(
            "/shorten",
            json={"url": "https://example.com/stats-test"}
        )
        code = create_response.json()["code"]

        # Get stats
        response = client.get(f"/_stats/{code}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == code
        assert data["target"] == "https://example.com/stats-test"
        assert data["visits"] == 0  # No visits yet

    def test_stats_after_visits(self, client):
        """Test that stats correctly track visit count."""
        # Create and visit
        create_response = client.post(
            "/shorten",
            json={"url": "https://example.com/visit-test"}
        )
        code = create_response.json()["code"]

        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)

        # Check stats
        response = client.get(f"/_stats/{code}")
        assert response.status_code == 200
        assert response.json()["visits"] == 2

    def test_stats_nonexistent_code(self, client):
        """Test that stats for nonexistent code returns 404."""
        response = client.get("/_stats/nonexistent123")
        assert response.status_code == 404


class TestCodeUniqueness:
    """Tests for code generation and uniqueness."""

    def test_different_urls_get_different_codes(self, client):
        """Test that different URLs get different short codes."""
        response1 = client.post(
            "/shorten",
            json={"url": "https://example.com/url1"}
        )
        response2 = client.post(
            "/shorten",
            json={"url": "https://example.com/url2"}
        )

        code1 = response1.json()["code"]
        code2 = response2.json()["code"]
        assert code1 != code2

    def test_same_url_returns_existing_code(self, client):
        """Test that the same URL returns the existing short code."""
        url = "https://example.com/duplicate"

        response1 = client.post("/shorten", json={"url": url})
        response2 = client.post("/shorten", json={"url": url})

        code1 = response1.json()["code"]
        code2 = response2.json()["code"]
        assert code1 == code2  # Should return same code for same URL
