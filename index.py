"""
Vercel Serverless Entrypoint alias for app.py
"""

from app import app, application, handler

__all__ = ["app", "application", "handler"]
