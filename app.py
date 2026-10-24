"""Vercel entrypoint for the Quiz Assessment Platform API.

Vercel discovers the top-level ``app`` variable and serves the existing FastAPI
application without changing its local development command.
"""

from backend.main import app
