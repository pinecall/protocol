# Changelog

The contract, version by version. A release is a `v*` tag: `release.yml` publishes the three
packages from it, and the notes of a GitHub release are the section below it.

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
