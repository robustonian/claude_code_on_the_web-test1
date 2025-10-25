"""
FastAPI URL Shortener Service.

A minimal URL shortening service with:
- POST /shorten: Create short URLs
- GET /{code}: Redirect to original URL
- GET /_stats/{code}: View statistics
"""
import os
import secrets
import string
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl, field_validator
from sqlmodel import Session, select
from app.db import get_session, create_db_and_tables
from app.models import URLMapping

# Environment configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

app = FastAPI(
    title="URL Shortener",
    description="A minimal URL shortening service",
    version="1.0.0"
)


# Pydantic models for request/response
class ShortenRequest(BaseModel):
    """Request model for creating a short URL."""
    url: str

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL has a proper scheme."""
        if not v:
            raise ValueError("URL cannot be empty")
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        # Additional basic validation
        if ' ' in v:
            raise ValueError("URL cannot contain spaces")
        return v


class ShortenResponse(BaseModel):
    """Response model for created short URL."""
    code: str
    short_url: str


class StatsResponse(BaseModel):
    """Response model for URL statistics."""
    code: str
    target: str
    visits: int


def generate_code(length: int = 6) -> str:
    """
    Generate a random short code.

    Args:
        length: Length of the code (default: 6)

    Returns:
        Random alphanumeric code
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_db():
    """Database dependency - can be overridden in tests."""
    yield from get_session()


@app.on_event("startup")
def on_startup():
    """Create database tables on startup (skip if using test database)."""
    # Skip if dependency overrides are active (test mode)
    if not app.dependency_overrides:
        create_db_and_tables()


@app.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_200_OK)
def shorten_url(
    request: ShortenRequest,
    db: Annotated[Session, Depends(get_db)]
) -> ShortenResponse:
    """
    Create a short URL for the given target URL.

    If the URL has already been shortened, returns the existing code.
    Otherwise, generates a new unique code.
    """
    # Check if URL already exists
    statement = select(URLMapping).where(URLMapping.target_url == request.url)
    existing = db.exec(statement).first()

    if existing:
        # Return existing short code
        return ShortenResponse(
            code=existing.code,
            short_url=f"{BASE_URL}/{existing.code}"
        )

    # Generate unique code
    max_attempts = 10
    for _ in range(max_attempts):
        code = generate_code()
        # Check if code already exists
        statement = select(URLMapping).where(URLMapping.code == code)
        if not db.exec(statement).first():
            break
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique code"
        )

    # Create new mapping
    mapping = URLMapping(
        code=code,
        target_url=request.url,
        visits=0
    )
    db.add(mapping)
    db.commit()

    return ShortenResponse(
        code=code,
        short_url=f"{BASE_URL}/{code}"
    )


@app.get("/_stats/{code}", response_model=StatsResponse)
def get_stats(
    code: str,
    db: Annotated[Session, Depends(get_db)]
) -> StatsResponse:
    """
    Get statistics for a short URL.

    Returns the target URL and visit count.
    """
    statement = select(URLMapping).where(URLMapping.code == code)
    mapping = db.exec(statement).first()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    return StatsResponse(
        code=mapping.code,
        target=mapping.target_url,
        visits=mapping.visits
    )


@app.get("/{code}")
def redirect_to_url(
    code: str,
    db: Annotated[Session, Depends(get_db)]
) -> RedirectResponse:
    """
    Redirect to the original URL for the given short code.

    Also increments the visit counter.
    """
    statement = select(URLMapping).where(URLMapping.code == code)
    mapping = db.exec(statement).first()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    # Increment visit count
    mapping.visits += 1
    db.add(mapping)
    db.commit()

    return RedirectResponse(
        url=mapping.target_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
