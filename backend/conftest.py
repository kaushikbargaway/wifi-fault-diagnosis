"""Pytest configuration — ensures the backend root is on sys.path."""
import sys
from pathlib import Path

# Allow `from app.xxx import ...` in tests without installing the package
sys.path.insert(0, str(Path(__file__).parent))
