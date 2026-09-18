"""
Vercel / WSGI entrypoint forwarding to main.app
"""
from main import app, application, handler

__all__ = ["app", "application", "handler"]
