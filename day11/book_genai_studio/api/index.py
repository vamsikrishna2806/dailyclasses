"""Vercel entry point. Vercel runs this file as a serverless function and gives it every request
(see the rewrite in vercel.json). It just imports the normal FastAPI app."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402,F401
