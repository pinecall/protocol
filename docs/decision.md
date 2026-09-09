# The protocol

Why the wire says what it says. The shapes are `schema/`; the reference is
`docs/protocol/README.md`; this is the argument. Nothing here was copied from Pinecall v1's
code: its vocabulary was recalled, and a name survived only when it was still the best name.

## One vocabulary, one seq

v1 had two: the in-process events an app subscribed to, and the `type` strings the call log
stored. They drifted. In v2 the envelope of the log **is** the event. What the gateway
streams to a subscriber and what the store keeps are the same bytes, with the same `seq`.
A reader that reconnects sends its last `seq`; the cursor is the whole replay protocol.
`ephemeral` is on the entry, not the type, because the same `user.transcript` is an interim
that may be dropped and a final that becomes a turn.

## The names, group by group

**`call.*`** is the call's life: `ringing` (offered, not answered), `dialing` (outbound,
not answered), `started` (media up), `ended`, `transferred`, `line` (hold and mute, both
flags stated), `summary` (usage and cost, written last). `call.forwarded` became
`call.transferred` because the supervise verb is `transfer` and one thing gets one word;
forwarding is a telco term for redirecting before answer, ours happens after. `call.routed`
went: the route rides on `call.ringing` and on `agent.registered`, and a number is a route,
never an agent, so there is no separate routing moment to narrate.

**`user.*` and `agent.*`** are the two voices, in the session's own vocabulary. livekit's
session has `user_state_changed` and `agent_state_changed` with a closed set of states; the
wire carries those states under `user.state` and `agent.state` instead of inventing
`speech.started`, `user.speaking`, `bot.speaking`, `bot.finished`, `eager.turn`,
`turn.pause`, `turn.resumed` and `turn.continued`, the v1 family that described a turn
model the platform no longer owns. `user.transcript` and `agent.transcript` are the words as
they arrive, interim or final; `bot.word` went with them. `bot` itself went: the thesis says
an agent is an object, and the thing that registers, speaks and is configured is one agent,
so `agent.registered`, `agent.configured`, `agent.state`, `agent.transcript` share a prefix
on purpose.

**`turn.user` and `turn.agent`** are the finished turns, and they carry livekit's
`ChatMessage` metrics report split by role. This is the heart of the card: every field the
library measures for a turn travels under the library's own name (`llm_node_ttft`,
`tts_node_ttfb`, `e2e_latency`, `transcription_delay`, `end_of_turn_delay`, …), nothing
summarised, nothing renamed. The first attempt at this card invented a `TurnLatency {vad,
asr, eou, llm_ttft, tts_ttfb, e2e}`; that is exactly what a test now forbids: the field list
is read from the library at test time and compared with the schema.

**`metrics.<block>`** is one event per typed block the session emits, its data the
library's model verbatim: `llm`, `stt`, `tts`, `vad`, `eou`, `eot`, `interruption`,
`realtime`, `avatar`. The card spec said `metrics.collected`; a block per type won because a
reader filters by `type` and a store indexes by it, and because the registry test can then
prove that every member of livekit's `AgentMetrics` union has an event. `avatar` is carried
although no Pinecall channel has an avatar: the test walks the whole union, and an honest
union has no exceptions. The join is `speech_id`: livekit gives the caller's finished turn,
its end-of-turn decision and the reply that follows the same id, so `turn.user`,
`metrics.eou`, `metrics.llm`, `metrics.tts` and `turn.agent` of one exchange share it.
`metrics.stt`, `metrics.vad`, `metrics.eot` and `metrics.interruption` have no `speech_id` in
the library, so they belong to the call and the reducer keeps them by kind. `metrics.vad`
defaults to ephemeral because it arrives about once a second and says nothing a summary
needs; the console sees it live.

**`metrics.json`** is a seventh schema file the card did not list. The blocks are one idea
(the library's measurements) and generate one module (`metrics.py`, `metrics.ts`); folding
twenty-one definitions into `defs.json` would have hidden the one file a reviewer most needs
to read next to `livekit/agents/metrics/base.py`.

**Required means what the library requires.** A metric field is `required` in the schema
exactly when the library's model has no default for it; everything else is optional and,
when absent, absent, never zero. A text session (chat, WhatsApp) measures what it can of
the same fields and leaves the rest out. The one exception is the `type` tag, which the
library defaults and always dumps and both unions are told apart by.

**`call.summary`** carries the session's `ModelUsage` rows verbatim (`llm_usage`,
`tts_usage`, `stt_usage`, `interruption_usage`, `eot_usage`, every field) and a `cost` in
euros with the exchange rate stated and every priced row listed; a row the price table does
not know goes to `unpriced`, never to zero, so a total is known to be incomplete.

**`tool.call` / `tool.result`** survived: the model calls, the app answers, and the log
keeps both. `tool.result` is the one name that is both a command (app → gateway) and an
event (in the log) and shares one shape on purpose: the log line is the answer, with a seq.

**`state.changed`, `prompt.changed`, `tools.changed`** are the app's declarations landing:
`state.set`, `prompt.set`, `tools.set` survived as commands because the thesis is that
fields are state, the prompt is `render(state)` and tools are the only thing that changes
state; `prompt.changed` carries a hash and a length, never the text. `prompt.set` names a
region (`static` or `view`) because the prompt has three regions in a fixed order and the
app writes two of them.

**`confirm.request` / `granted` / `declined`** are new: the confirmation gate for
irreversible tools. The `audience` is `sha256(tool + arguments)`, what the one-shot token is
bound to; the token itself never enters the log.

**`memory.ops` and `docs.sources`** survived from the design: what memory did (recall,
remember, forget) and what retrieval put in front of the model, so an answer is traceable.

**`supervisor.*`, one per verb**: `said`, `whispered`, `took_over`, `released`,
`transferred`, `ended`. v1's `handoff.requested` / `active` / `released` collapsed into
`took_over` / `released`: there is no requested state, a takeover is immediate. The event
names are the verbs in the past tense so a reader hears who did what.

**`log.gap` / `log.caught_up`** survived unchanged: they are still the best names for the
replay markers. A gap may carry a `snapshot` (the reduced State) so a reader catches up in
one step; a marker stands at the seq of the last entry it speaks for.

**`error`, `custom`, `pong`** survived. `error` is one event for both scopes (in a call, or
about a refused command) rather than v1's `error` plus `call.error` plus `line.error`.

## The amendment: the room, the outside world, participate, projections

ms-1 extended the wire in four directions. Each was a choice with a plausible alternative.

**Room facts, not room objects.** LiveKit has a `Room` with participants, tracks and attributes,
and the obvious design gives the agent class a `room` object to call methods on. The wire carries
facts instead — `room.opened`, `participant.joined`, `participant.left`, `participant.speaking`,
`track.published`, `track.unpublished` — and the agent acts through commands that land as more
facts (`room.invite`, `participant.mute`, `participant.remove`, `room.send`). Two reasons. The
invariant says a tenant never imports LiveKit, and an object with LiveKit's methods on it is LiveKit
by another name; a fact in the log is not. And a fact reduces: `State.room` is what the facts fold
to, so the console, a replay and a test see the same room the agent saw, with no live handle to
lose. The attributes travel verbatim, `sip.*` keys included, for the same reason the metrics do:
the caller's number as the trunk reported it is a fact of the room, and a field we invented for it
would be a copy that drifts. `participant.mute` lands as `track.unpublished` because that is the
fact the room has for it — the leg's audio is gone for everyone — and there is no unmute: a leg
that must speak again is invited again, which is a fact too.

**One `event.received`, not a name per source.** The tenant's backend hands the agent a fact with
`call.event`; a browser hands it one with `pinecall.event`. Both land as `event.received`, told apart
by `source` and, for a participant, `identity`. A name per source (`app.event`, `participant.event`)
would have made the app's handler care where a fact came from before it could read it, and made a
reader filter two types for one idea. The permission is not in the name but in the declaration:
`AgentConfig.events` lists which names the agent accepts and from whom, and the gateway refuses
anything else before it touches the log. `state.changed.cause` became a union so a state change
says which kind of thing moved it — a tool or an outside fact — without a second field.

**The projection is server-side.** A widget is code in somebody else's browser. If it applied the
projection itself, a modified widget would ask for the whole state and get it; the token's scope
would be a suggestion. So the gateway or the worker projects at the sink — SSE, the DataChannel, a
`GET` — and a client only ever receives what its token's projection keeps. `public` is a whitelist
(`docs/protocol/projections.md`) and everything not on it is absent, not null: a field that is not
there cannot be asked for. `tenant` is everything with `pii` fields masked to the string `***`, so
the key survives and the value does not. Visibility is declared per field by the app
(`state_fields`), never guessed by the platform, because only the app knows what a field holds.

**`participate` is its own scope.** `talk` lets a browser connect once and speak; `observe` lets a
console read a set of agents' logs. A caller reading its own call is neither: it must read exactly
one call, the one it is in, through the public projection, and it must be able to hand the agent a
fact from its browser. Folding that into `talk` would give every widget a reader it does not need;
folding it into `observe` would need a per-call filter on a scope designed for sets. A scope that
says "this call, public, and `pinecall.event`" is smaller than either and refuses more.

**Two shapes the spec drew differently.** The spec wrote the declarations as maps —
`state_fields: {<field>: {visibility}}`, `events: {<name>: {from}}` — and they landed as lists of
named specs, `StateFieldSpec[]` and `EventSpec[]`, the way `tools: ToolSpec[]` already is. The
generator's dialect has no typed map (an inline object must be opaque JSON), and a map keyed by the
app's own field names would sit under the codec's camelCase rename, which never touches the app's
keys under `state` or `arguments` and would have had to learn two more opaque keys; a `name` is a
value and is never renamed. The room's shapes live in their own schema file, `room.json`, generating
`room.py` and `room.ts`, as `metrics.json` does: `events.py` was already near the line ceiling, and
the room is one idea a reader wants in one file.

## What did not come along, and why

| v1 | v2 | why |
|---|---|---|
| `add_phone`, `remove_phone`, `phone.added`, `phone.removed`, `channel.add`, `channel.remove` | `agent.register {routes}` → `agent.registered` | doors are declared once, at registration; a number is a route, and routes are the gateway's table, not a stream of edits |
| `update_config`, `update_session_config`, `config.updated` | `agent.configure` → `agent.configured`; `session.configure` | snake_case cruft, and two names for one idea; dotted verbs like everything else |
| `registered` | `agent.registered` | every event has a domain prefix |
| `bot.say`, `bot.reply`, `bot.reply_stream`, `bot.reply.stream`, `bot.cancel`, `bot.clear` | `agent.say` | the LLM runs in the platform now; the app never streams a reply token by token. One verb remains for a verbatim phrase (a greeting, a legal notice), on livekit's `session.say` |
| `session.pause`, `session.resume`, `session.send` | the supervise verbs | a human takes over through `/v1/attach` with a supervise token, not through the app's socket |
| `line.create`, `line.destroy`, `line.created`, `line.error` | nothing | SIP trunks are infrastructure (livekit-sip), not something an app narrates |
| `call.route` | nothing | routes are configuration |
| `speech.*`, `user.speaking`, `user.message`, `eager.turn`, `turn.*` (pause, end, resumed, continued), `bot.speaking`, `bot.word`, `bot.finished`, `bot.interrupted`, `barge_in` | `user.state`, `agent.state`, `user.transcript`, `agent.transcript`, `turn.user`, `turn.agent`, `metrics.interruption` | the session owns the turn model; the wire carries its states and its finished turns with their metrics |
| `call.forwarded`, `call.forward` | `call.transferred`, `call.transfer` | one word for one thing, and it is the supervise verb |
| `handoff.requested`, `handoff.active`, `handoff.released` | `supervisor.took_over`, `supervisor.released` | a takeover is immediate |
| `metrics.collected` (the card's first name) | `metrics.<block>` | one event per typed block: filterable, indexable, testable against the library's union |

## What the generator decides

- The generator is `protocol/generate/`, stdlib Python, four files: the loader, the two
  emitters, the docs emitter. Not `datamodel-code-generator`: its output names things
  `Model1`, puts every definition in one file, and cannot keep a file under 400 lines or a
  docstring on one line. Our emitter writes the modules a person would.
- `scripts/generate` runs it, then `ruff format` on the Python it wrote. Formatting
  is part of generation, so idempotence is `ruff`'s promise plus ours; CI regenerates and
  diffs.
- Every JSON object on the wire is closed (`additionalProperties: false`), inline objects
  are refused (name it in `$defs`), and the one `anyOf` allowed is `[$ref, null]`. A small
  schema dialect keeps the generator small and the names good.
- Python fields carry no `description`: the class docstring is the definition's first
  sentence, the rest is a comment above it, and the field meanings live in the schema and
  the reference. A `Field(description=…)` per field would have doubled every module and put
  `events.py` over the line limit.
- `from` is a Python keyword: the one alias, `from_`, and the codec serialises `by_alias`.
  That is why the codec is the only file that touches a key name.
- An optional field is `T | None = None` in Python and the codec encodes with
  `exclude_unset`: what the wire did not carry, the wire does not get back. The reducers
  build turns and tool runs from the encoded event data, so both sides keep exactly the
  fields the entry had, and the golden state compares equal.
- TypeScript gets the wire's snake_case in its zod schemas and inferred types, and `Camel<T>`
  / `toCamel` / `toSnake` in the codec for the SDK, which never rename under the app's own
  JSON (`OPAQUE_KEYS`: `state`, `arguments`, `output`, `data`, `parameters`, `metadata`,
  `app_state`).
- `schema/rest.json` is the wire the READ DOORS answer in — `CallState`, `LogPage`,
  `SessionLine`, `SessionList`, `HeldAgent`, `AgentList`. The wire is not only what a socket
  carries: a REST envelope hand-read in one console file is a schema nobody generates. ms-5.
- A definition name lives in ONE module. Both languages export every module from one index, so a
  name in two of them is ambiguous there however clear it was in the schema, and the loader refuses
  it by name before an emitter runs.
- `x-unit` reaches TypeScript as `units.ts`: one `UNITS` map, field name to unit, and two
  definitions that disagree about a field stop generation instead of one of them winning. Python
  does not need it — the reference tables already carry it — and a TypeScript client does.
- `"terminal": true` on `call.summary` generates `TERMINAL_EVENT` into both registries. The name
  that ends a call is one name, and the four places that used to spell it read it from there.
- The registries (`EVENTS`, `COMMANDS`, `EPHEMERAL_EVENTS`, `PRODUCES`) are their own
  module on both sides, `registry.py` / `registry.ts`, so the model modules stay under 400
  lines and the closed set of types has one home.
- The reducer is written by hand twice, in Python and in TypeScript, and both must reduce
  `protocol/fixtures/call-log-golden.json` to `call-log-golden.state.json`. The fixture is
  written by hand from this schema, one entry per line so a log reads as a log.
