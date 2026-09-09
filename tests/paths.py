"""Where the repo keeps the things a test reads: the schema, the fixtures, the pages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
FIXTURES = ROOT / "fixtures"
DOCS = ROOT / "docs"
