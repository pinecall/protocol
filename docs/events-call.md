# Events: the call and the conversation

The call's life (`call.*`), the two voices as the session sees them (`user.*`, `agent.state`, `agent.transcript`), the finished turns with their metrics (`turn.*`) and the raw metric blocks (`metrics.*`, whose fields are in `metrics.md`). Generated; the index is `events.md`.

<!-- generated:begin -->
### `agent.state`

The agent's state changed, in the session's own words.

| field | type | required | meaning |
|---|---|---|---|
| `state` | `AgentState` | yes | What the agent is doing right now, in the session's own words: warming up, waiting, hearing the caller, generating, or playing audio. |

### `agent.transcript`

Words from the agent as they are played, synced to the audio. Interim while final is false; the whole reply becomes turn.agent. Interim entries are ephemeral.

| field | type | required | meaning |
|---|---|---|---|
| `speech_id` | `string` | yes | The reply these words belong to. |
| `text` | `string` | yes | The words played so far. |
| `final` | `boolean` | yes | True when the reply is fully played or was cut. |
| `start` | `number` | no | When these words start, in seconds from the start of the reply's audio, as the voice aligned them. Absent when the voice returned no word timings. |
| `end` | `number` | no | When these words end, in seconds from the start of the reply's audio, as the voice aligned them. Absent when the voice returned no word timings. |

### `call.dialing`

The platform is placing an outbound call and the far end has not answered yet. The first entry of an outbound call's log.

| field | type | required | meaning |
|---|---|---|---|
| `channel` | `Channel` | yes | The door the public came through: a phone call over SIP, the browser widget over WebRTC, or WhatsApp text. |
| `from` | `string` | yes | The number the call shows as coming from, E.164. |
| `to` | `string` | yes | The number being dialed, E.164. |
| `run` | `string | null` | no | The eval run that placed this call, when one did. Absent or null for a call the platform placed for a person. |
| `caller` | `Contact | null` | yes | Who is being called, when the app said. |
| `external_id` | `string` | no | The carrier or SIP call id, once assigned. |

### `call.ended`

The call is over. Nothing about the conversation follows; call.summary still does.

| field | type | required | meaning |
|---|---|---|---|
| `reason` | `EndReason` | yes | Why the call is over. |
| `ended_by` | `EndedBy` | yes | Whose action ended the call. |
| `ended_at` | `number` | yes | When it ended, unix seconds. |
| `duration_s` | `number` | yes | Seconds from call.started to now. 0 for a call that never started. |

### `call.line`

The line's hold and mute flags after one of them changed. Both are stated so a reader never has to remember the other.

| field | type | required | meaning |
|---|---|---|---|
| `held` | `boolean` | yes | True while the caller is on hold and hears nothing from the agent. |
| `muted` | `boolean` | yes | True while the agent produces no audio. |

### `call.ringing`

An inbound call is offered to this agent and has not been answered yet. The first entry of an inbound call's log.

| field | type | required | meaning |
|---|---|---|---|
| `channel` | `Channel` | yes | The door the public came through: a phone call over SIP, the browser widget over WebRTC, or WhatsApp text. |
| `from` | `string` | yes | The calling number in E.164 form, or the web visitor id. |
| `to` | `string` | yes | The number or route that was called. |
| `route` | `Route` | yes | One door to an agent: a channel and, for phone and WhatsApp, the number that answers. |
| `run` | `string | null` | no | The eval run that opened this call, when one did: such a call starts mid-conversation, in the golden's state. Absent or null for a person. |
| `caller` | `Contact | null` | yes | Who this seems to be, from the number alone. Null when nobody is known. |
| `external_id` | `string` | no | The carrier or SIP call id, for tracing outside Pinecall. |

### `call.score`

The last entry of a call: what the judges said about it at hang-up, one row per judge. Written after call.summary, and the entry the log seals on.

| field | type | required | meaning |
|---|---|---|---|
| `passed` | `boolean` | no | Whether no judge answered broken. A deferred or a skipped judge is an answer nobody gave, never a fault of the call. ABSENT when no judge answered at all, which is not the same as false: read not_judged for why nobody did. |
| `not_judged` | `string` | no | Why nothing judged this call, when nothing did: the judges are not installed on this box, or the judging itself failed. Absent on every call a judge answered. |
| `judges` | `Judgment[]` | yes | One row per judge that was run over this call, in the order they were declared. |
| `panel` | `string[]` | no | Every judge this call declared, whether or not it answered: a judge that raised is here and absent from judges. Empty when nothing was ever declared, and absent on entries written before this field existed. |
| `judge_calls` | `integer` | yes | How many questions judging this call actually put to a model. Zero is the happy path: a policy answers by code. |
| `judge_cost_eur` | `number` | no | What those questions cost in euros, priced from the judge model's own usage rows. Absent when no usage was reported, never zero. |

### `call.started`

Media is up: the caller and the agent can hear each other, or the text session is open. Everything the agent says and hears comes after this.

| field | type | required | meaning |
|---|---|---|---|
| `channel` | `Channel` | yes | The door the public came through: a phone call over SIP, the browser widget over WebRTC, or WhatsApp text. |
| `direction` | `Direction` | yes | Inbound: the public reached the agent. |
| `from` | `string` | yes | The calling side, E.164 or a visitor id. |
| `to` | `string` | yes | The called side. |
| `run` | `string | null` | no | The eval run that opened this call, when one did: such a call starts mid-conversation, in the golden's state. Absent or null for a person. |
| `caller` | `Contact | null` | yes | Who is on the line, as far as the platform knows now. |
| `started_at` | `number` | yes | When media came up, unix seconds. |

### `call.summary`

What the call was about, how it went, what it consumed and what that cost. Written after call.ended, once memory and pricing are done; call.score follows it and seals the log.

| field | type | required | meaning |
|---|---|---|---|
| `reason` | `EndReason` | yes | Why the call is over. |
| `outcome` | `string` | yes | One line on how it went, in the agent's words: booked, no slot, wrong number. |
| `duration_s` | `number` | yes | Seconds of conversation. |
| `turns` | `integer` | yes | How many turns, both sides together. |
| `usage` | `ModelUsage[]` | yes | One row per model used, as the session summed them. |
| `cost` | `Cost` | yes | What the call cost in provider fees, informational, in euros. |
| `recording` | `string` | no | Where the recording is, when one was made. |

### `call.transferred`

A transfer asked for by the agent or a supervisor finished, one way or the other.

| field | type | required | meaning |
|---|---|---|---|
| `to` | `string` | yes | Where the caller was sent. |
| `mode` | `TransferMode` | yes | Cold: the caller is sent on and the agent leaves. |
| `ok` | `boolean` | yes | True when the far end took the call. |
| `error` | `string` | no | Why it failed, when it did. |

### `metrics.avatar`

One avatar timing report: livekit's AvatarMetrics, every field. No Pinecall channel has an avatar today.

Data: `AvatarMetrics`, in [metrics.md](metrics.md).

### `metrics.eot`

One end-of-turn prediction: livekit's EOTInferenceMetrics, every field. Has no speech_id; it belongs to the call.

Data: `EOTInferenceMetrics`, in [metrics.md](metrics.md).

### `metrics.eou`

How long closing the caller's turn took: livekit's EOUMetrics, every field. Joined to the turn by speech_id.

Data: `EOUMetrics`, in [metrics.md](metrics.md).

### `metrics.interruption`

The interruption detector's latest inference and running counts: livekit's InterruptionMetrics, every field.

Data: `InterruptionMetrics`, in [metrics.md](metrics.md).

### `metrics.llm`

One LLM request as the session measured it: livekit's LLMMetrics, every field. Joined to the turn by speech_id.

Data: `LLMMetrics`, in [metrics.md](metrics.md).

### `metrics.realtime`

One speech-to-speech response: livekit's RealtimeModelMetrics, every field, its token details nested as the library nests them.

Data: `RealtimeModelMetrics`, in [metrics.md](metrics.md).

### `metrics.stt`

One STT request or stream segment as the session measured it: livekit's STTMetrics, every field. Has no speech_id; it belongs to the call.

Data: `STTMetrics`, in [metrics.md](metrics.md).

### `metrics.tts`

One TTS request as the session measured it: livekit's TTSMetrics, every field. Joined to the turn by speech_id; several per reply, one per segment.

Data: `TTSMetrics`, in [metrics.md](metrics.md).

### `metrics.vad`

The VAD's health for the last second or so: livekit's VADMetrics, every field. About one a second, so ephemeral by default: the console sees it live, the store need not keep it.

Data: `VADMetrics`, in [metrics.md](metrics.md).

### `turn.agent`

The agent's reply is over and this is what was said. With it, everything the session measured about the reply.

| field | type | required | meaning |
|---|---|---|---|
| `speech_id` | `string` | yes | The reply's id, shared with the caller's turn and with the metrics blocks. |
| `item_id` | `string` | no | The session's id for this message in the chat history. |
| `text` | `string` | yes | What was said. When interrupted, only what was actually played. |
| `interrupted` | `boolean` | yes | True when the caller cut the reply short. |
| `metrics` | `AgentTurnMetrics` | yes | What the session measured about the agent's reply. |

### `turn.user`

The caller's turn is over and this is what they said. With it, everything the session measured about the turn.

| field | type | required | meaning |
|---|---|---|---|
| `speech_id` | `string` | yes | The id of the reply this turn triggers; turn.agent and its llm, tts and eou blocks carry the same id. That is the join. |
| `item_id` | `string` | no | The session's id for this message in the chat history. |
| `text` | `string` | yes | The final transcript, or the message as typed. |
| `language` | `string` | no | The language heard, as a BCP 47 tag. |
| `transcript_confidence` | `number` | no | The recognizer's confidence, 0 to 1, when it reports one. |
| `metrics` | `UserTurnMetrics` | yes | What the session measured about the caller's turn. |

### `user.state`

The caller's state changed, in the session's own words.

| field | type | required | meaning |
|---|---|---|---|
| `state` | `UserState` | yes | What the platform believes the person on the line is doing right now. |

### `user.transcript`

Words from the caller as the recognizer hears them. Interim while final is false; the final one becomes turn.user. Interim entries are ephemeral.

| field | type | required | meaning |
|---|---|---|---|
| `text` | `string` | yes | The transcript so far, or the final one. |
| `final` | `boolean` | yes | True when the recognizer will not revise this. |
| `language` | `string` | no | The language heard, as a BCP 47 tag. |
| `confidence` | `number` | no | The recognizer's confidence, 0 to 1, when it reports one. |

<!-- generated:end -->
