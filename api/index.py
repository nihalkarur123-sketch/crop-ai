"""
Vercel serverless entry point for PlantCare AI.
All app code lives inside api/ so Vercel's Python builder bundles everything correctly.
"""
import os
import sys

# Put api/ itself on the path so imports like "from services.x import y" resolve
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from app import create_app

app = create_app()
