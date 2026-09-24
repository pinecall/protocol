# Projections

What leaves the platform is never the whole log. Before a state or an entry reaches a reader, the
gateway or the worker applies a **projection** at the sink — the SSE stream, the DataChannel, a
`GET` — and a client never applies one, because a client can be modified and a token cannot ask for
more than it was issued with. The two projections are the `Projection` enum in `shapes.md`; this
page is the contract every sink obeys, and the tests on both sides
(`runtime/tests/api/calls/test_state.py`, `typescript/test/projection.test.ts`) assert it over the
golden state.

## Who gets which

| token | projection | reads |
|---|---|---|
| `talk` | public | its own call, while connected |
| `chat` | public | its own call: the room's text streams, which it subscribes to. No microphone |
| `participate` | public | its own call: the snapshot on join, the stream, a replay; sends `pinecall.event` |
| `observe` | tenant | **no log at all**: a hidden, silent seat that hears the room and reads nothing |
| `supervise` | tenant | the one live call it was minted for, and the six verbs |
| the operator key (`/v1/ops/*`) | tenant | every agent of the runtime |

A projection is a property of the token, decided when the token is minted. Nothing a client sends
changes it.

## `public` — what a participant may see of its own call

The rule is a whitelist: a field not named here is absent from the projection, not null. What is
kept is what the person on the line already knows or is being asked, and nothing that names the
tenant's implementation (tools, prompts, memory, retrieval, cost) or another person.

| field | public keeps |
|---|---|
| `seq` | whole. The cursor a client resumes from |
| `status`, `user_state`, `agent_state` | whole. The orb renders them |
| `live` | whole: the interim words on screen |
| `turns` | each turn as `role`, `speech_id`, `text`; an agent turn also `interrupted` and, of its metrics, only `e2e_latency`. No `item_id`, no language, no confidence, no other metric |
| `app_state` | the fields the agent declared `public` in `state_fields`. Nothing else, not masked: absent |
| `room` | `name`, `sid`, `caller`, and each participant as `identity`, `kind`, `name`, `joined_at`, `speaking`. **Never `attributes`**: they carry the caller's number and the trunk's headers |
| `confirms` | each as `phrase` and `status`: the widget may show the pending yes. No tool, no call id, no audience |
| `transfer` | whole |
| `held` | whole |
| `events` | only the entries whose `source` is `participant` and whose `identity` is the viewer's own. An event from the app or from another participant is not theirs to see |

Everything else — `agent`, `call`, `channel`, `direction`, `from`, `to`, `caller`, `started_at`,
`ended_at`, `end_reason`, `outcome`, `metrics`, `tools`, `prompt`, `tools_visible`, `memory`,
`sources`, `handoff`, `muted`, `usage`, `cost`, `routes`, `gaps`, `errors`, `custom` — is absent.

The same rule projects a single entry for the public stream: an entry whose type has no place in the
table above is dropped whole (`tool.*`, `prompt.changed`, `tools.changed`, `memory.ops`,
`docs.sources`, `custom`, `supervisor.*`, `metrics.*`, `call.summary`, `error`, `agent.*` outside a
call); an entry that has one is kept with only the fields the table keeps for it (`state.changed`
with its public fields and no `cause`; `confirm.request` as `phrase` and `ttl_s`; `participant.joined`
without `attributes`; `call.started` and `call.ended` without `from`, `to`, `caller`;
`event.received` only when it is the viewer's own). `log.gap` travels with its `snapshot` projected.

## `tenant` — everything, with personal data masked

The tenant projection is the whole state and every entry, with one change: a field the agent
declared `pii` in `state_fields` is masked, in `app_state` and wherever `state.changed` or
`call.attached` carries it.
A tool argument the agent declared in `ToolSpec.pii` was masked when the entry was written and needs
nothing here. A field never declared is `tenant`: seen whole.

**Masked** means, everywhere on this platform, that the value is replaced by the string `***`. The
key stays, so a reader knows a value exists; the type is lost, so nothing leaks through its shape.

## What the agent declares

Both projections read the agent's `AgentConfig`, sent with `agent.configure` and held by the gateway
— never the log, which does not carry the config:

- `state_fields: [{name, visibility}]` — `public`, `tenant` or `pii` per field of the app's state.
  Absent means `tenant`.
- `events: [{name, from}]` — which outside events the agent accepts and from whom (`app`,
  `participant`, or both). An event nobody declared, or one from a sender not listed for it, is
  refused with `error` before it touches the log. Declaring is the whole permission model for the
  outside world: a browser can only ever hand the agent what the tenant said a browser may.

## The DataChannel topics

Named once, here. Every message is JSON; the worker is the room's authority and the browser is a
client of it.

| topic | direction | carries | projection |
|---|---|---|---|
| `pinecall.log` | worker → browser | one log entry per message, in `seq` order, after the snapshot | public |
| `pinecall.snapshot` | worker → browser, once, on join | `{state, last_seq}`: the state projected, and the `seq` it was reduced to, repeated outside the state so a client resumes without opening it | public |
| `pinecall.replay` | browser → worker | `{after}`: send me the entries after this `seq`; answered on `pinecall.log`, with `log.gap` and `log.caught_up` as over SSE | — |
| `pinecall.event` | browser → worker | `{name, data}`: a fact from this participant. Lands as `event.received` with `source: participant` and the sender's `identity`; refused unless declared with `participant` among its senders | — |
| `pinecall.ui` | tenant → browser, via `room.send` | whatever the tenant sent, whole; the log keeps `room.sent` with its size | none: the tenant chose what to send and to whom |

A participant only ever receives `pinecall.log`, `pinecall.snapshot` and what was addressed to it on
`pinecall.ui`. A tenant's own topics, sent with `room.send`, reach the tenant's own page code and are
the tenant's business.

## Where the code lives

`schema/defs.json` declares `Projection`, `Visibility`, `StateFieldSpec` and `EventSpec`.
The functions that project — `project_state`, `project_entry` in
`runtime/src/pinecall/log/projection.py` — follow this page; the tests name each row of the table.
There is no TypeScript projection: on that side the contract is held by
`typescript/test/projection.test.ts` alone, over the golden state.
