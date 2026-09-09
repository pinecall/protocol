"""The schema in; pydantic models, zod schemas, Ruby tables and the reference pages out. Idempotent."""

from __future__ import annotations

import sys
from pathlib import Path

import docs
import python
import ruby
import schema
import typescript

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
PYTHON_OUT = ROOT / "python" / "pinecall_protocol"
TYPESCRIPT_OUT = ROOT / "typescript" / "src" / "generated"
RUBY_OUT = ROOT / "ruby" / "lib" / "pinecall" / "protocol" / "generated"
RUBY_SIG_OUT = ROOT / "ruby" / "sig" / "pinecall" / "protocol"
DOCS_OUT = ROOT / "docs"


def main() -> int:
    bundle = schema.load(SCHEMA)
    written = python.emit(bundle, PYTHON_OUT)
    written += typescript.emit(bundle, TYPESCRIPT_OUT)
    written += ruby.emit(bundle, RUBY_OUT, RUBY_SIG_OUT)
    written += docs.emit(bundle, DOCS_OUT)
    sys.stdout.write(
        f"generate: {len(bundle.definitions)} shapes, {len(bundle.messages_of('event'))} events, "
        f"{len(bundle.messages_of('command'))} commands -> {len(written)} files\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
