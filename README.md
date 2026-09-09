# pinecall/protocol

The wire between whoever does the real time and the application that owns the agent. One
vocabulary, written once as JSON Schema 2020-12 under `schema/`, generated into three
languages and committed: a consumer installs a package and never runs a generator.

```
schema/         the source. defs · envelope · events/ · commands/ · verbs · metrics · state · rest · room
python/pinecall_protocol/fixtures/  the golden call log and the state it reduces to, read by all three
generate/       the emitters: schema in, python + typescript + ruby + docs out
python/         pinecall-protocol: pydantic v2 models, the registries, the codec
typescript/     @pinecall/protocol: zod schemas, the types, the reducer
ruby/           pinecall-protocol: the frozen tables, the validator, the codec, the reducer, RBS
docs/           the reference, one page per family, tables refilled by the generator
tests/          the Python side; typescript/test and ruby/test are the others
```

## Working on it

```
scripts/generate      rewrite everything generated from schema/
scripts/check         regenerate, diff, lint, test — what CI runs
cd python && uv sync  the Python side, with its tools
cd typescript && pnpm install && pnpm test    (its exports point at src/; publishConfig swaps in dist/)
cd ruby && rake                               the tests, then `rbs validate`
```

Edit the schema, run `scripts/generate`, commit what it wrote. Nothing under
`python/pinecall_protocol/`, `typescript/src/generated/`, `ruby/lib/pinecall/protocol/generated/`,
`ruby/sig/pinecall/protocol/generated.rbs` or between the generated markers in `docs/` is ever
edited by hand. `docs/README.md` explains the envelope and the one `seq`;
`docs/decision.md` is why the vocabulary is the way it is.

## License

[Apache-2.0](LICENSE). Use it, change it, run it in production, sell what you build with it —
commercially or not, on your own box or somebody else's. The licence carries an explicit patent
grant, which is why it is the one this stack uses (LiveKit's is the same). There is no NOTICE
file, so nothing has to be reproduced downstream beyond the licence itself, and there is no CLA:
a patch is yours and stays under the same terms.

Every package carries a copy of it: `pinecall-protocol` on PyPI, `@pinecall/protocol` on npm,
`pinecall-protocol` on RubyGems.
