# pinecall/protocol

The wire between whoever does the real time and the application that owns the agent. One
vocabulary, written once as JSON Schema 2020-12 under `schema/`, generated into both
languages and committed: a consumer installs a package and never runs a generator.

```
schema/         the source. defs · envelope · events/ · commands/ · verbs · metrics · state · rest · room
python/pinecall_protocol/fixtures/  the golden call log and the state it reduces to, shipped with BOTH packages
generate/       the emitters: schema in, python + typescript + docs out
python/         pinecall-protocol: pydantic v2 models, the registries, the codec
typescript/     @pinecall/protocol: zod schemas, the types, the reducer
docs/           the reference, one page per family, tables refilled by the generator
tests/          the Python side; typescript/test is the other
```

## Working on it

```
scripts/generate      rewrite everything generated from schema/
scripts/check         regenerate, diff, lint, test — what CI runs
cd python && uv sync  the Python side, with its tools
cd typescript && pnpm install && pnpm test
```

Edit the schema, run `scripts/generate`, commit what it wrote. Nothing under
`python/pinecall_protocol/`, `typescript/src/generated/` or between the generated markers in
`docs/` is ever edited by hand. `docs/README.md` explains the envelope and the one `seq`;
`docs/decision.md` is why the vocabulary is the way it is.
