"""Generated from schema/events/: one model per event."""

from typing import Annotated, Any, Literal

from pydantic import Field

from pinecall_protocol._base import WireModel
from pinecall_protocol.defs import (
    AgentState,
    Channel,
    Contact,
    Cost,
    DevVerb,
    Direction,
    DocSource,
    EndedBy,
    EndReason,
    Env,
    MemoryOp,
    Route,
    ScoreVerdict,
    Supervisor,
    TransferMode,
    UserState,
)
from pinecall_protocol.metrics import AgentTurnMetrics, ModelUsage, UserTurnMetrics
from pinecall_protocol.state import State


# Live calls keep their session; the next call starts with the new config.
class AgentConfigured(WireModel):
    """The gateway applied an agent.configure."""

    changed: list[str]


class AgentDetached(WireModel):
    """One socket stopped holding the agent."""

    app: str
    env: Env
    left: bool


# The gateway accepted an agent.register: this socket now speaks for the agent and answers its
# routes. Many sockets may hold one agent at once — a new call takes the newest of them, unless the
# caller names one by its `app` id.
class AgentRegistered(WireModel):
    """The gateway accepted an agent.register."""

    routes: list[Route]
    app: str
    sdk: str | None = None
    env: Env | None = None


class AgentStateChanged(WireModel):
    """The agent's state changed, in the session's own words."""

    state: AgentState


# One delta of the reply the agent is giving, never the reply so far: in a voice call one word, as
# the voice plays it, with the seconds it was aligned to; in a written call one model token. The
# reply so far is every delta of the same speech_id since the last turn.agent, joined; turn.agent
# carries the whole reply and closes it. Interim entries are ephemeral.
class AgentTranscript(WireModel):
    """One delta of the reply the agent is giving, never the reply so far."""

    speech_id: str
    text: str
    final: bool
    start: float | None = None
    end: float | None = None


# An ask for a person settled: a supervisor took the line, or the wait ran out and the agent has the
# caller back.
class AttentionAnswered(WireModel):
    """An ask for a person settled."""

    ok: bool
    by: Supervisor | None
    error: str | None = None


# The agent asked for a person: the caller is on hold and waits for a supervisor to take the line.
# What a supervisor's console and phone are notified by.
class AttentionRequested(WireModel):
    """The agent asked for a person."""

    reason: str
    wait_s: float


# The first entry of an outbound call's log.
class CallDialing(WireModel):
    """The platform is placing an outbound call and the far end has not answered yet."""

    channel: Channel
    from_: str = Field(alias="from")
    to: str
    run: str | None = None
    caller: Contact | None
    external_id: str | None = None
    asked_by: str | None = None


# Nothing about the conversation follows; call.summary still does.
class CallEnded(WireModel):
    """The call is over."""

    reason: EndReason
    ended_by: EndedBy
    ended_at: float
    duration_s: float


# Both are stated so a reader never has to remember the other.
class CallLine(WireModel):
    """The line's hold and mute flags after one of them changed."""

    held: bool
    muted: bool


# The first entry of an inbound call's log.
class CallRinging(WireModel):
    """An inbound call is offered to this agent and has not been answered yet."""

    channel: Channel
    from_: str = Field(alias="from")
    to: str
    route: Route
    run: str | None = None
    caller: Contact | None
    external_id: str | None = None


# A reader who disagrees with a verdict opens the log at those lines.
class JudgmentEvidence(WireModel):
    """Where in the call's own log a judgment is about."""

    seqs: list[int]
    said: str | None = None


# One judge's answer about one call: the question it was asked, the word it answered and the
# sentence that says why.
class Judgment(WireModel):
    """One judge's answer about one call."""

    name: str
    verdict: ScoreVerdict
    criteria: str
    reason: str
    evidence: JudgmentEvidence


# Written after call.summary, and the entry the log seals on.
class CallScore(WireModel):
    """The last entry of a call: what the judges said about it at hang-up, one row per judge."""

    passed: bool | None = None
    not_judged: str | None = None
    judges: list[Judgment]
    panel: list[str] | None = None
    judge_calls: int
    judge_cost_eur: float | None = None


# Everything the agent says and hears comes after this.
class CallStarted(WireModel):
    """Media is up: the caller and the agent can hear each other, or the text session is open."""

    channel: Channel
    direction: Direction
    from_: str = Field(alias="from")
    to: str
    run: str | None = None
    persona: str | None = None
    accepts_when: str | None = None
    declines_when: str | None = None
    caller: Contact | None
    started_at: float
    env: Env | None = None


# Written after call.ended, once memory and pricing are done; call.score follows it and seals the
# log.
class CallSummary(WireModel):
    """What the call was about, how it went, what it consumed and what that cost."""

    reason: EndReason
    outcome: str
    duration_s: float
    turns: int
    usage: list[ModelUsage]
    cost: Cost
    recording: str | None = None


class CallTransferred(WireModel):
    """A transfer asked for by the agent or a supervisor finished, one way or the other."""

    to: str
    mode: TransferMode
    ok: bool
    error: str | None = None


# Somebody asked to be called back: a phone caller the overflow agent answered, a web visitor who
# left a number at the widget, or a caller who asked the agent for one (call.callback). Written into
# the agent's own log; the tenant's app reads it and places the call.
class CallbackRequested(WireModel):
    """Somebody asked to be called back."""

    channel: Channel
    number: str
    via: Literal["overflow", "widget", "agent"]
    call: str | None
    when: str | None = None
    note: str | None = None
    contact: Contact | None


# The tool does not run; the model is told.
class ConfirmDeclined(WireModel):
    """The caller did not say yes, or the request lapsed."""

    tool: str
    call_id: str
    audience: str
    said: str | None = None
    reason: Literal["no", "timeout", "changed", "cancelled"]


# The platform minted a one-shot token bound to the audience and the tool now runs. The token itself
# never enters the log.
class ConfirmGranted(WireModel):
    """The caller said yes."""

    tool: str
    call_id: str
    audience: str
    said: str
    ttl_s: int


# The agent reads the phrase; nothing runs until confirm.granted.
class ConfirmRequest(WireModel):
    """A tool with confirm set is about to run and the platform is asking the caller."""

    tool: str
    call_id: str
    arguments: dict[str, Any]
    audience: str
    phrase: str
    ttl_s: int


# Written into the agent's own log, which is the org's, before the door says no.
class CreditsExhausted(WireModel):
    """The gateway refused a call or a register because one of the org's quotas ran out."""

    org: str
    quota: Literal[
        "minutes",
        "messages",
        "agents",
        "concurrent_calls",
        "memory_facts",
        "knowledge_chunks",
        "numbers",
        "seats",
    ]
    used: float
    limit: int


# The platform never reads it; the console shows it and evals may.
class Custom(WireModel):
    """A line the app wrote into the log with call.log."""

    name: str
    data: dict[str, Any]


class DevRequest(WireModel):
    """One ask of the process in the agent's directory, on a console's behalf."""

    id: str
    verb: DevVerb
    data: dict[str, Any]


# An answer can be traced back to its chunks.
class DocsSources(WireModel):
    """What retrieval put in front of the model for this turn."""

    query: str
    sources: list[DocSource]
    took_ms: float
    speech_id: str | None = None


# Inside a call it says what failed; outside a call it says which command the gateway refused.
class ErrorEvent(WireModel):
    """Something went wrong."""

    code: str
    message: str
    command: str | None = None
    id: str | None = None
    recoverable: bool


# Written into the agent's own log, which is the org's, before the door says no — the caller was
# offered a call back instead of a room.
class FleetFull(WireModel):
    """The gateway refused to open a call because every worker of the fleet was full."""

    channel: Channel
    workers: int
    active: int


# Never stored; sent to the reader.
class LogCaughtUp(WireModel):
    """The replay is done: everything up to seq has been sent and what follows is live."""

    seq: int


# This reader missed a stretch: it reconnected too late for the store, or fell behind and the fanout
# dropped ephemeral entries. When the platform has a snapshot, it is here so the reader can catch up
# in one step. Never stored; sent to the reader.
class LogGap(WireModel):
    """This reader missed a stretch."""

    from_seq: int
    to_seq: int
    snapshot: State | None


# What memory did for this turn or at hangup: a recall before the reply, a remember after the call,
# a forget on request.
class MemoryOps(WireModel):
    """What memory did for this turn or at hangup."""

    ops: list[MemoryOp]
    speech_id: str | None = None


# Ephemeral: it proves the socket is alive and says nothing else.
class Pong(WireModel):
    """The answer to ping."""

    ts: float


# The text stays out of the log; its hash and length let two states be compared.
class PromptChanged(WireModel):
    """A block of the prompt was rewritten."""

    name: str
    hash: str
    chars: int


class StateCauseTool(WireModel):
    """A tool call's result changed the state."""

    kind: Literal["tool"] = "tool"
    tool: str
    call_id: str


# A fact from outside changed the state: the app's handler for an event.received moved a field.
class StateCauseEvent(WireModel):
    """A fact from outside changed the state."""

    kind: Literal["event"] = "event"
    name: str
    seq: int


# What changed the state: a tool's result, or a fact from outside. Told apart by kind.
type StateCause = Annotated[StateCauseTool | StateCauseEvent, Field(discriminator="kind")]


# A tool's result or an outside fact caused it, and the cause says which; the whole state travels so
# a reader never needs the previous entry.
class StateChanged(WireModel):
    """The app's declared state changed."""

    state: dict[str, Any]
    changed: list[str]
    cause: StateCause | None = None


# call.ended follows with reason supervisor_ended.
class SupervisorEnded(WireModel):
    """A supervisor hung up the call."""

    by: Supervisor
    reason: str | None = None


class SupervisorReleased(WireModel):
    """The supervisor gave the line back; the agent resumes with the history intact."""

    by: Supervisor


class SupervisorSaid(WireModel):
    """A supervisor made the agent say this to the caller."""

    by: Supervisor
    text: str


class SupervisorTookOver(WireModel):
    """A supervisor took the line; the agent is quiet until supervisor.released."""

    by: Supervisor


# call.transferred says how it went.
class SupervisorTransferred(WireModel):
    """A supervisor asked for a transfer."""

    by: Supervisor
    to: str
    mode: TransferMode


class SupervisorWhispered(WireModel):
    """A supervisor told the agent something the caller never heard."""

    by: Supervisor
    text: str


# The platform sends this to the app and the app's method runs in the app's own process; tool.result
# closes it.
class ToolCall(WireModel):
    """The model called a tool."""

    call_id: str
    name: str
    arguments: dict[str, Any]
    speech_id: str | None = None


# The app's state moved and each tool's when was recomputed.
class ToolsChanged(WireModel):
    """The tools the model can see changed."""

    visible: list[str]


# With it, everything the session measured about the reply.
class AgentTurnEnded(WireModel):
    """The agent's reply is over and this is what was said."""

    speech_id: str
    item_id: str | None = None
    text: str
    interrupted: bool
    metrics: AgentTurnMetrics


# With it, everything the session measured about the turn.
class UserTurnEnded(WireModel):
    """The caller's turn is over and this is what they said."""

    speech_id: str
    item_id: str | None = None
    text: str
    language: str | None = None
    transcript_confidence: float | None = None
    metrics: UserTurnMetrics


class UserStateChanged(WireModel):
    """The caller's state changed, in the session's own words."""

    state: UserState


# Interim while final is false; the final one becomes turn.user. Interim entries are ephemeral.
class UserTranscript(WireModel):
    """Words from the caller as the recognizer hears them."""

    text: str
    final: bool
    language: str | None = None
    confidence: float | None = None
