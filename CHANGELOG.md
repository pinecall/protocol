# Changelog

The contract, version by version. A release is a `v*` tag: `release.yml` publishes the three
packages from it, and the notes of a GitHub release are the section below it.

## Unreleased

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
