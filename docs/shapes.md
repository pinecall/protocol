# The shapes

The two frames on the wire (`schema/envelope.json`) and the shapes that events, commands and the state share (`schema/defs.json`). Generated.

<!-- generated:begin -->
### `Entry`

One line of a call's log, or of an agent's log when call is null. seq is written before control returns, so two readers never disagree about order.

| field | type | required | meaning |
|---|---|---|---|
| `seq` | `integer` | yes | The entry's place in its log, starting at 1, never reused. The cursor a reader resumes from. |
| `ts` | `number` | yes | When the entry was written, unix seconds with fractions. |
| `call` | `string | null` | yes | The call this entry belongs to. Null for entries about the agent itself: registered, configured, pong, an error outside any call. |
| `agent` | `string` | yes | The agent's slug, as it registered: clinica-norte. |
| `type` | `string` | yes | Which event this is, dotted: call.started, turn.user, metrics.llm. The closed list is the events/ folder. |
| `ephemeral` | `boolean` | yes | True for entries a store may drop and a slow reader may miss without harm: interim transcripts, VAD health, replay markers. False for everything the truth is made of. |
| `data` | `object` | yes | The event's payload, whose shape is the event's own schema under events/<type>.json. |

### `Command`

One instruction from an app to the gateway over its WebSocket. The gateway answers with the events the command produces, or with an error naming the command's id.

| field | type | required | meaning |
|---|---|---|---|
| `type` | `string` | yes | Which command this is, dotted: state.set, call.dial, ping. The closed list is the commands/ folder. |
| `agent` | `string` | yes | The agent this command speaks for. A socket may serve several agents. |
| `call` | `string | null` | yes | The call the command is about, or null for commands about the agent: register, configure, dial, ping. |
| `id` | `string` | no | The app's own id for the command, echoed back on an error so the app knows which one failed. |
| `data` | `object` | yes | The command's payload, whose shape is the command's own schema under commands/<type>.json. |

### `Channel`

The door the public came through: a phone call over SIP, the browser widget over WebRTC, or WhatsApp text.

One of: `phone`, `web`, `whatsapp`.

### `Direction`

Inbound: the public reached the agent. Outbound: the agent reached out (a dial).

One of: `inbound`, `outbound`.

### `EndReason`

Why the call is over. Who hung up, what failed before anybody could, drained: the platform took the worker down (a deploy, a stop) with the call still on it, or app_detached: the app holding the agent closed its socket mid-call, so nothing was rendering the prompt or answering a tool — both are nobody's fault and neither is an error.

One of: `caller_hung_up`, `agent_hung_up`, `supervisor_ended`, `transferred`, `no_answer`, `busy`, `dial_failed`, `timeout`, `drained`, `app_detached`, `error`.

### `EndedBy`

Whose action ended the call. platform covers timeouts, errors and a drained worker.

One of: `caller`, `agent`, `supervisor`, `platform`.

### `ScoreVerdict`

What one judge answered about a finished call. Held: the rule held. Broken: it did not, and the reason names the evidence. Deferred: the judge was asked and could not settle it. Skipped: nobody asked it — no model was reachable inside the call's judging budget.

One of: `held`, `broken`, `deferred`, `skipped`.

### `TransferMode`

Cold: the caller is sent on and the agent leaves. Warm: the agent stays on the line until the other side answers, then leaves.

One of: `cold`, `warm`.

### `PromptRegion`

Which region of the prompt: the cached static prefix (instructions), or the dynamic view rendered from state at the end. The append-only history in between is never written by the app.

One of: `static`, `view`.

### `UserState`

What the platform believes the person on the line is doing right now. The states are the session's own.

One of: `listening`, `speaking`, `away`.

### `AgentState`

What the agent is doing right now, in the session's own words: warming up, waiting, hearing the caller, generating, or playing audio.

One of: `initializing`, `idle`, `listening`, `thinking`, `speaking`.

### `ParticipantKind`

Who a participant is to the call: the person the agent serves (over SIP or the widget), the agent itself, a supervisor who took a seat in the room, a listener who only hears, or a second SIP leg that room.invite brought in.

One of: `caller`, `agent`, `supervisor`, `listener`, `sip`.

### `TrackKind`

What a track carries: a microphone's audio, a camera's video, or a screen share.

One of: `audio`, `video`, `screen`.

### `TrackSource`

Where a track comes from, as livekit's TrackSource names it, in lower case.

One of: `microphone`, `camera`, `screen_share`, `screen_share_audio`, `unknown`.

### `EventSource`

Where an outside fact came from: the tenant's backend over the app socket (app), or a participant's browser over the DataChannel (participant).

One of: `app`, `participant`.

### `Visibility`

Who may see a field of the app's state: everyone in the call (public), the tenant's own readers (tenant, the default for a field never declared), or nobody without masking (pii).

One of: `public`, `tenant`, `pii`.

### `Projection`

Which projection a sink applies before a state or an entry leaves the platform: public for a participant reading its own call, tenant for the tenant's readers. The contract is docs/protocol/projections.md; a client never applies one.

One of: `public`, `tenant`.

### `Contact`

Who is on the line, as far as the platform knows. Everything is optional: a web visitor may be nobody yet.

| field | type | required | meaning |
|---|---|---|---|
| `id` | `string` | no | The platform's own id for this contact, stable across channels and calls. |
| `phone` | `string` | no | The caller's number in E.164 form (+34 600 000 000 written as +34600000000). |
| `name` | `string` | no | The name the contact is known by, when memory or the app supplied one. |
| `email` | `string` | no | An e-mail address, when the web widget or the app supplied one. |
| `external_id` | `string` | no | The id the tenant's own system uses for this person, when the app told the platform. |

### `Route`

One door to an agent: a channel and, for phone and WhatsApp, the number that answers. A number is a route, never an agent.

| field | type | required | meaning |
|---|---|---|---|
| `channel` | `Channel` | yes | The door the public came through: a phone call over SIP, the browser widget over WebRTC, or WhatsApp text. |
| `number` | `string | null` | yes | The number in E.164 form for phone and WhatsApp; null for the web widget, which needs none. |
| `label` | `string` | no | A human name for the door, for the console: 'main line', 'after hours'. |

### `Supervisor`

The human who sent a supervise verb, as the token that let them in names them.

| field | type | required | meaning |
|---|---|---|---|
| `id` | `string` | yes | The supervisor's id, from their token. |
| `name` | `string` | no | Their display name, when the token carried one. |

### `ToolSpec`

What the app declares about one tool: the contract the model sees and the rules the platform enforces before running it.

| field | type | required | meaning |
|---|---|---|---|
| `name` | `string` | yes | The name the model calls, unique within the agent: find_patient, book_slot. |
| `description` | `string` | yes | What the tool does, as the model reads it. In the app this is the method's docstring. |
| `parameters` | `object` | yes | The arguments, as a JSON Schema object the model must satisfy. |
| `side_effect` | `"read" | "write" | "irreversible"` | no | read looks at the world; write changes it and can be undone; irreversible changes it for good, so the platform asks the caller first. Absent means read. |
| `confirm` | `string` | no | The read-back the agent says before the tool runs, with {argument} placeholders filled from the call: 'Le reservo con la doctora {doctor} el {at}. ¿Confirmo?'. Absent means no confirmation. |
| `pii` | `string[]` | no | Argument names that carry personal data, masked in the log by declaration. |
| `timeout_s` | `number` | no | How long the platform waits for the app's result before reporting an error to the model, in seconds. |

### `ToolResult`

What came back from running a tool in the app's process. Either an output or an error, never both.

| field | type | required | meaning |
|---|---|---|---|
| `call_id` | `string` | yes | The id the tool.call carried, so the result finds its call. |
| `name` | `string` | yes | The tool's name, repeated so a log line stands on its own. |
| `output` | `any` | no | Whatever the method returned, as JSON. Absent when the tool failed. |
| `error` | `string` | no | What went wrong, in words the model may read. Absent when the tool succeeded. |
| `summary` | `string` | no | A one-line version of the output for the console and for memory, when the app wrote one. |
| `duration_s` | `number` | no | How long the app's method took, in seconds. |

### `MemoryFact`

One thing remembered about a contact: a sentence, where it came from, and how well it matched when recalled.

| field | type | required | meaning |
|---|---|---|---|
| `id` | `string` | no | The fact's id in the memory store. |
| `text` | `string` | yes | The fact itself, as one sentence: 'prefers mornings', 'allergic to penicillin'. |
| `score` | `number` | no | How well it matched the recall query, 0 to 1. Absent when remembering, which has no query. |
| `source` | `string` | no | The call this fact was extracted from, when known. |

### `MemoryOp`

One operation against the contact's memory: a recall during the turn, a remember at hangup, or a forget on request.

| field | type | required | meaning |
|---|---|---|---|
| `op` | `"recall" | "remember" | "forget"` | yes | recall reads facts for the turn; remember writes facts extracted at hangup; forget erases on the contact's request. |
| `contact` | `string` | no | The contact id the memory belongs to. |
| `query` | `string` | no | What was asked of memory, for a recall. |
| `facts` | `MemoryFact[]` | yes | The facts read, written or erased. |
| `took_ms` | `number` | yes | How long the operation took, in milliseconds. A recall in the turn must stay under 150. |

### `DocSource`

One chunk of the knowledge base that retrieval put in front of the model for this turn.

| field | type | required | meaning |
|---|---|---|---|
| `id` | `string` | yes | The chunk's id in the knowledge store. |
| `path` | `string` | yes | The document the chunk came from, as the tenant pushed it: 'faq/horarios.md'. |
| `heading` | `string` | no | The heading the chunk sits under, since chunks are cut by heading. |
| `score` | `number` | yes | The fused rank score (vector and BM25 through RRF), higher is better. |
| `excerpt` | `string` | no | The first line or so of the chunk, for the console. |

### `CostRate`

The exchange rate the cost was computed with, stated so the number can be reproduced.

| field | type | required | meaning |
|---|---|---|---|
| `currency` | `"EUR"` | yes | Costs are always stated in euros. |
| `usd_to_eur` | `number` | yes | How many euros one US dollar bought, since providers price in dollars. |
| `as_of` | `string` | yes | The day the rate is from, as YYYY-MM-DD. |

### `CostRow`

One priced line: a model, what was counted, how much, and what it came to.

| field | type | required | meaning |
|---|---|---|---|
| `provider` | `string` | yes | The provider, as the usage row names it: anthropic, elevenlabs, soniox. |
| `model` | `string` | yes | The model, as the usage row names it. |
| `unit` | `"input_tokens" | "cached_input_tokens" | "cache_creation_tokens" | "output_tokens" | "characters" | "audio_seconds" | "requests" | "session_seconds"` | yes | What the provider bills by for this line. |
| `quantity` | `number` | yes | How many of that unit the call used. |
| `unit_price_usd` | `number` | yes | The provider's list price per unit, in US dollars, from the price table. |
| `eur` | `number` | yes | quantity times unit_price_usd times the rate, in euros. |

### `UnpricedRow`

A usage row the price table does not know. It is listed, never priced at zero.

| field | type | required | meaning |
|---|---|---|---|
| `provider` | `string` | yes | The provider of the row nobody could price. |
| `model` | `string` | yes | The model of the row nobody could price. |

### `Cost`

What the call cost in provider fees, informational, in euros. The runtime never prices commercially; this is the provider's bill as best we know it.

| field | type | required | meaning |
|---|---|---|---|
| `eur` | `number` | yes | The sum of every priced row, in euros. |
| `rate` | `CostRate` | yes | The exchange rate the cost was computed with, stated so the number can be reproduced. |
| `rows` | `CostRow[]` | yes | Every usage row that had a price, one line per unit billed. |
| `unpriced` | `UnpricedRow[]` | yes | The usage rows the price table did not know, so the total is known to be incomplete. |

### `VoiceConfig`

Which voice speaks for the agent: the name it was asked for, or the id the provider knows it by.

| field | type | required | meaning |
|---|---|---|---|
| `name` | `string` | no | The voice as the app wrote it: one of the platform's curated names, or a provider's own id. Resolved to a provider and an id when the app declares itself, so an unknown name is refused there and never at the first utterance. |
| `provider` | `string` | no | The TTS provider: elevenlabs. Absent when the curated name decides it. |
| `model` | `string` | no | The provider's model, when the default is not wanted. |
| `voice_id` | `string` | no | The provider's id for the voice. |

### `ModelConfig`

Which model does a job (the LLM, or the STT), and the one or two knobs worth turning.

| field | type | required | meaning |
|---|---|---|---|
| `provider` | `string` | yes | The provider: anthropic, openai, soniox, deepgram. |
| `model` | `string` | yes | The provider's model name. |
| `temperature` | `number` | no | Sampling temperature, for an LLM. Absent means the provider's default. |

### `TurnConfig`

How the session decides that the caller has finished, and when the caller may interrupt.

| field | type | required | meaning |
|---|---|---|---|
| `min_interruption_words` | `integer` | no | How many words the caller must say before the agent stops talking. Guards against 'mm-hm'. |
| `endpointing_ms` | `integer` | no | How long a silence, in milliseconds, before the turn detector is asked whether the caller is done. |

### `Pronunciation`

How the voice says one word it would otherwise get wrong: a proper name, a brand, a street.

| field | type | required | meaning |
|---|---|---|---|
| `word` | `string` | yes | The word as the model writes it: Vidal. |
| `spoken` | `string` | yes | What the voice is given instead: bidál. Applied to the reply before it is spoken, never to the log. |

### `StateFieldSpec`

What the app declares about one field of its state: who may see it. A field never declared is tenant.

| field | type | required | meaning |
|---|---|---|---|
| `name` | `string` | yes | The field's name in the app's state, as state.set sends it: patient, slots. |
| `visibility` | `Visibility` | yes | Who may see a field of the app's state: everyone in the call (public), the tenant's own readers (tenant, the default for a field never declared), or nobody without masking (pii). |

### `EventSpec`

One outside event the agent accepts, and from whom. An event nobody declared is refused before it touches the log.

| field | type | required | meaning |
|---|---|---|---|
| `name` | `string` | yes | The event's name, dotted, as call.event or pinecall.event will send it: slot.released, form.submitted. |
| `from` | `EventSource[]` | yes | Who may send it: the tenant's backend, a participant's browser, or both. |

### `AgentConfig`

What an app declares about its agent: the voice, the models, the language, the greeting, the tools, and who may see and send what. Every field is optional so a configure can change one thing.

| field | type | required | meaning |
|---|---|---|---|
| `instructions` | `string` | no | The static prefix of the prompt: who the agent is and how it behaves. Cached by the provider. |
| `language` | `string` | no | The language the agent speaks and expects, as a BCP 47 tag: es-ES, es-UY. |
| `greeting` | `string` | no | What the agent says first, verbatim, when a call starts. |
| `voice` | `VoiceConfig` | no | Which voice speaks for the agent: the name it was asked for, or the id the provider knows it by. |
| `llm` | `ModelConfig` | no | Which model does a job (the LLM, or the STT), and the one or two knobs worth turning. |
| `stt` | `ModelConfig` | no | Which model does a job (the LLM, or the STT), and the one or two knobs worth turning. |
| `turn` | `TurnConfig` | no | How the session decides that the caller has finished, and when the caller may interrupt. |
| `says` | `Pronunciation[]` | no | How the voice says the words it would otherwise get wrong. Applied to the reply on its way to the TTS. |
| `hears` | `string[]` | no | The words the ears must know: the agent's own name, the doctors', the streets. Given to the STT as keyterms. |
| `tools` | `ToolSpec[]` | no | Every tool the agent may ever see. Which ones are visible now is tools.set. |
| `state_fields` | `StateFieldSpec[]` | no | Who may see each field of the app's state. A field not listed is tenant: seen by the tenant's readers, never by the public. |
| `events` | `EventSpec[]` | no | The outside events this agent accepts and from whom. Anything else is refused before it touches the log. |

<!-- generated:end -->
