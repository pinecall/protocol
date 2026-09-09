"""Where the repo keeps the things a test reads: the schema, the fixtures, the pages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"

DOCS = ROOT / "docs"
FIXTURES = ROOT / "python" / "pinecall_protocol" / "fixtures"