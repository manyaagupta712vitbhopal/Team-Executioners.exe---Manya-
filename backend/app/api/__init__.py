"""
API router package.

This package contains all API route modules used by the application.
"""

from . import auth
from . import documents
from . import folders
from . import mentor
from . import users

__all__ = [
    "auth",
    "documents",
    "folders",
    "mentor",
    "users",
]
