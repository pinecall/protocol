# Changelog

The contract, version by version. A release is a `v*` tag: `release.yml` publishes the three
packages from it, and the notes of a GitHub release are the section below it.

## Unreleased

## 0.6.6 — The box's floor

### Added
- **`BoxEvent`**, the frame of the operator's `GET /v1/ops/events`: `{org, entry}`, an entry of
  some org's floor and the id of the org it is. The envelope itself is untouched.

## 0.6.5 — Asking for a person, a call back, and a transfer the runtime shapes

### Added
- **`call.attention`, `attention.requested`, `attention.answered`, `State.attention`,
  `SessionLine.attention`.** The agent asks for a person without sending the caller anywhere: the
  call waits on hold until a supervisor takes the line or `wait_s` runs out. `wait_s` has no
  default; the app chooses it.
- **`call.callback`, and `callback.requested` with `via: "agent"`, `when` and `note`.** A caller who
  asks to be called back, written down from inside the call.

### Changed
- **`mode` is optional wherever a transfer is named.** `call.transfer` and `TransferVerb` take
  none: absent, the runtime picks — cold for a caller on a SIP leg, warm (the number dialled into
  the call's own room) for one in a browser. `supervisor.transferred` carries the one it picked;
  `call.transferred` and `TransferState.mode` are null when nothing was attempted at all, which is
  what a written conversation answers. `TransferMode`'s warm now says what it does: the agent
  falls silent once the far side answers, and the call ends when either human hangs up.
- **`ToolSpec.confirm` and `EndVerb` say what the runtime does.** `confirm` is a receipt read out
  once the tool has run and before the model replies, with `{{name}}` and `{{result.name}}`
  placeholders — the old text described a question asked before the tool, in `{name}` braces that
  nothing fills. `end` hangs up at once: a sentence playing and a reply being written are cut.
  Descriptions only; no shape changed.

## 0.6.4 — A persona's model, voice and verdict; how sure a turn is; whether a call keeps its audio

### Added
- **`Persona.llm` · `tts` · `voice` · `accepts_when` · `declines_when`, and the same on
  `PersonaPut`.** How a synthetic caller is played, in the agent's own three words, and its own
  rule for a call. `CallStarted` carries `accepts_when` · `declines_when` too, so the judge at
  hang-up reads the rule a call was made under.
- **`TurnConfig.eot_threshold` and `eot_threshold`'s eager half.** A recogniser that decides the
  end of the turn itself — Deepgram Flux — does it on a confidence, and how sure it has to be was
  the one thing about a turn the wire could not carry: an agent could say how long a silence is,
  never how certain. Deepgram measures a fifth of the turns ending before the caller has finished
  at its own default, so it is the knob that decides whether an agent answers half a sentence.
  `eager_eot_threshold` is the lower bar at which it says the turn MIGHT be over, which is what
  lets a model start on an answer early without the turn being committed on a guess.
- **`TuningBody.record` and `AgentConfig.record`.** Whether an agent's calls keep their audio, as
  a setting of the agent rather than a switch on the machine: one org may record and another may
  not, and neither needs a deploy to change its mind. Unset, they are recorded.

## 0.6.3 — Which base answered, and the panel an agent draws

### Added
- **`AgentConfig.view` and the `view.render` dev verb**: the panel an agent draws beside a
  conversation. The declaration is one name, so a console knows the agent has a panel before it
  asks for one and draws its own about the contact when it has not; what the panel CONTAINS is
  asked for a conversation at a time, through the verb, and never travels in the declaration.
- **`DocSource.base`**: which knowledge base a retrieved chunk came from. An agent reads every
  base its world attached to it and a turn searches them together, so `docs.sources` was the one
  place that could say which collection answered a question — and it did not. Optional, because a
  log written before a turn could read more than one base carries no such field.

### Fixed
- **Three optional fields say they may be null, because the wire sends null.** `HeldAgent.holder`,
  `TheLine.holding` and `ThreadMessage.answered` were typed as a bare `$ref` and a bare `boolean`
  and described as "absent" when unset — and the gateway sends `null` for all three (`GET /v1/agents`
  for the org's own corner, an unheld agent's line, every written message of a thread). The
  generated clients already accepted it, because the generator makes every optional field nullish;
  the SCHEMA was the one document that disagreed with the box, and a stricter client validating
  against it would have refused a correct answer.

## 0.6.2 — A persona is the org's, and a call says who is playing it

### Changed
- **`Persona` is the ORG's, and its doors say so.** The family loses nothing, but the paths do:
  `GET /v1/personas` and `PUT`·`DELETE /v1/personas/{name}` in place of the per-agent ones. Who a
  caller is does not depend on which of the org's agents answers them.

### Added
- **`PersonaRun` and `PersonaRunList`.** What a caller has done: `GET /v1/personas/{name}/runs`
  answers every simulation it has run, newest first — the call, the agent, when, the caller's
  turns, how it ended, its outcome, what it cost and how the judges answered — with the sessions
  list's own `total`/`next` paging.
- **`call.started.persona`.** The name of the synthetic caller a model is playing on this call,
  beside `run`, absent or null for a person. It is the one place the fact lives; a gateway
  projects it from here.

## 0.6.1 — The personas an agent's simulations play

### Added
- **`Persona`, `PersonaList` and `PersonaPut`.** A synthetic caller — a goal, a manner and the
  facts they may state about themselves — used to be a file of a project, so only the terminal
  standing in that directory could read one. It is the gateway's now, beside the agent's
  settings, which makes its shape a contract and not one repository's type: the console, the CLI
  and the runtime all read the same caller.

### Removed
- **The dev verbs `simulate.roster`, `personas.write` and `personas.drop`.** A console asks the
  gateway for an agent's callers now, not the process standing in its directory, so nothing is
  relayed for them any more.
