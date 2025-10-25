"""
Database models for URL shortener using SQLModel.
"""
from typing import Optional
from sqlmodel import SQLModel, Field


class URLMapping(SQLModel, table=True):
    """Model representing a URL shortening mapping."""

    __tablename__ = "url_mappings"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True, max_length=10)
    target_url: str = Field(max_length=2048)
    visits: int = Field(default=0)

    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "code": "abc123",
                "target_url": "https://example.com/long/url",
                "visits": 0
            }
        }
