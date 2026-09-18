# pinecall-protocol

Ruby's side of the Pinecall wire. The same JSON Schema that writes the pydantic models and the zod
schemas writes the tables in `lib/pinecall/protocol/generated/`, so a field added to the wire lands
in three languages in one commit.

```ruby
require "pinecall/protocol"

log   = Pinecall::Protocol.decode_entries(File.read("call.json"))
state = Pinecall::Protocol.reduce(log)          # what a reader of the whole log knows
state[:turns].size                              # => 12
state[:cost][:eur]                              # => 0.022937

# One command, checked here — where the backtrace is still yours — before it goes anywhere.
say = Pinecall::Protocol.command(type: "agent.say", agent: "clinica-norte", call: "CA_1",
                                 data: { text: "Buenas tardes." })
socket.write(Pinecall::Protocol.encode(say))
```

## What is generated and what is not

| file | written by |
|---|---|
| `lib/pinecall/protocol/generated/enums.rb` | `protocol/generate/ruby.py` — every closed list |
| `lib/pinecall/protocol/generated/shapes.rb` | the same — every named shape, as the table the validator walks |
| `lib/pinecall/protocol/generated/registry.rb` | the same — every event and command by its wire type |
| `sig/pinecall/protocol/generated.rbs` | the same — the wire as RBS record types |
| `validate.rb` · `codec.rb` · `state.rb` · `reduce.rb` | by hand, and never about a field's name |

Run `protocol/scripts/generate` after editing `schema/`, and commit what it wrote. `scripts/check`
regenerates and diffs, so stale output fails CI rather than travelling.

## Three implementations of one fold

`reduce.rb` is the third implementation of the log reducer, beside `typescript/src/reduce.ts` and
the runtime's `pinecall/log/reduce.py`. `test/golden_log_test.rb` reads the same golden log the
other two read and asserts the same final state, field for field. That test is the whole reason
three implementations are allowed to exist.

## Ruby notes

- **No camelCase layer.** The wire is snake_case and so is Ruby, so the conversion the TypeScript
  client needs does not exist here: a field is called on both sides what the schema calls it.
- **Symbol keys.** `JSON.parse(..., symbolize_names: true)`, so a payload matches with
  `case data in { name: "identity", chars: }` and a `Data` frame deconstructs the same way.
- **No schema gem.** The generated table plus `Validate` is thirty lines and cannot drift from the
  other two languages; a third-party validator could.
- **Types in RBS**, which is where a Ruby programme keeps them. `rake rbs` runs `rbs validate`.

## Working on it

```bash
rake            # the tests, then the RBS
rake test
rake rbs
```

## License

[Apache-2.0](LICENSE), like the rest of Pinecall.
