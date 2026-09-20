"""Generated from schema/defs.json: the shapes shared across the wire."""

from typing import Any, Literal

from pydantic import Field

from pinecall_protocol._base import WireModel

# The door the public came through: a phone call over SIP, the browser widget over WebRTC, or
# WhatsApp text.
type Channel = Literal["phone", "web", "whatsapp"]


# Inbound: the public reached the agent. Outbound: the agent reached out (a dial).
type Direction = Literal["inbound", "outbound"]


# Which of the two worlds a key opens, and so which world an agent is held in and a call ran in. A
# key is issued into one; an agent registered on it and every call it takes carry that one; a door
# claimed in one is refused to a key of the other. `sandbox` is where things are written and
# `production` is what the public reaches — and whether a sandbox agent is one PERSON's copy or the
# team's shared one is not this field: it is whether the key that registered it names a person.
# Every key issued before the field existed is production.
type Env = Literal["production", "sandbox"]


# What a console may ask of the process standing in the agent's directory, relayed by the gateway: a
# written call to the class mounted there (chat), a simulated caller put on the class it holds, its
# goldens and a suite of them, its knowledge folder pushed or its golden asked, its memory goldens,
# a call promoted to a candidate file, the drift of the last two windows, and the reproductions a
# broken run left on that disk. Everything else a console needs is a door of the gateway.
type DevVerb = Literal[
    "chat.roster",
    "chat.start",
    "chat.say",
    "chat.end",
    "simulate.start",
    "goldens.roster",
    "goldens.run",
    "knowledge.roster",
    "knowledge.push",
    "knowledge.eval",
    "memory.roster",
    "memory.eval",
    "memory.extraction",
    "promote.roster",
    "promote.write",
    "drift.read",
    "reproductions.roster",
    "reproductions.read",
]


# Why the call is over. Who hung up, what failed before anybody could, drained: the platform took
# the worker down (a deploy, a stop) with the call still on it, or app_detached: the app holding the
# agent closed its socket mid-call, so nothing was rendering the prompt or answering a tool — both
# are nobody's fault and neither is an error.
type EndReason = Literal[
    "caller_hung_up",
    "agent_hung_up",
    "supervisor_ended",
    "transferred",
    "no_answer",
    "busy",
    "dial_failed",
    "timeout",
    "drained",
    "app_detached",
    "error",
]


# Whose action ended the call. platform covers timeouts, errors and a drained worker.
type EndedBy = Literal["caller", "agent", "supervisor", "platform"]


# What one judge answered about a finished call. Held: the rule held. Broken: it did not, and the
# reason names the evidence. Deferred: the judge was asked and could not settle it. Skipped: nobody
# asked it — no model was reachable inside the call's judging budget.
type ScoreVerdict = Literal["held", "broken", "deferred", "skipped"]


# Cold: the caller is sent on and the agent leaves. Warm: the agent stays on the line until the
# other side answers, then leaves.
type TransferMode = Literal["cold", "warm"]


# Which region of the prompt a block lives in: static, before the history, cached by the provider;
# or dynamic, after the history, replaced every turn. The append-only history in between is never
# written by the app.
type PromptRegion = Literal["static", "dynamic"]


# How the knowledge base reaches the model: retrieved, the platform runs search itself when the
# caller's turn ends; or tool, the model calls search when it decides to. Either way the chunks
# arrive as a tool result.
type DocsMode = Literal["retrieved", "tool"]


# The two tools the platform runs on the app's behalf: recall reads the contact's facts out of
# memory, search reads chunks out of the knowledge base. The app declares memory and docs and writes
# neither method; the platform runs the lookup, and the answer reaches the model as a tool result
# rather than as part of the prompt.
type PlatformTool = Literal["recall", "search"]


# The default layout, when an agent declares none, is identity, knowledge and tools (static), then
# the history, then view (dynamic). A block's text is written per call with prompt.set.
class PromptBlockSpec(WireModel):
    """One named block of the prompt and the region it lives in."""

    name: str = Field(pattern="^[a-z][a-z0-9_]*$")
    region: PromptRegion


# What the platform believes the person on the line is doing right now. The states are the session's
# own.
type UserState = Literal["listening", "speaking", "away"]


# What the agent is doing right now, in the session's own words: warming up, waiting, hearing the
# caller, generating, or playing audio.
type AgentState = Literal["initializing", "idle", "listening", "thinking", "speaking"]


# Who a participant is to the call: the person the agent serves (over SIP or the widget), the agent
# itself, a supervisor who took a seat in the room, a listener who only hears, or a second SIP leg
# that room.invite brought in.
type ParticipantKind = Literal["caller", "agent", "supervisor", "listener", "sip"]


# What a track carries: a microphone's audio, a camera's video, or a screen share.
type TrackKind = Literal["audio", "video", "screen"]


# Where a track comes from, as livekit's TrackSource names it, in lower case.
type TrackSource = Literal["microphone", "camera", "screen_share", "screen_share_audio", "unknown"]


# Where an outside fact came from: the tenant's backend over the app socket (app), or a
# participant's browser over the DataChannel (participant).
type EventSource = Literal["app", "participant"]


# Who may see a field of the app's state: everyone in the call (public), the tenant's own readers
# (tenant, the default for a field never declared), or nobody without masking (pii).
type Visibility = Literal["public", "tenant", "pii"]


# Which projection a sink applies before a state or an entry leaves the platform: public for a
# participant reading its own call, tenant for the tenant's readers. The contract is
# docs/protocol/projections.md; a client never applies one.
type Projection = Literal["public", "tenant"]


# Everything is optional: a web visitor may be nobody yet.
class Contact(WireModel):
    """Who is on the line, as far as the platform knows."""

    id: str | None = None
    phone: str | None = None
    name: str | None = None
    email: str | None = None
    external_id: str | None = None


# A number is a route, never an agent.
class Route(WireModel):
    """One door to an agent: a channel and, for phone and WhatsApp, the number that answers."""

    channel: Channel
    number: str | None
    label: str | None = None


class Supervisor(WireModel):
    """The human who sent a supervise verb, as the token that let them in names them."""

    id: str
    name: str | None = None


# What the app declares about one tool: the contract the model sees and the rules the platform
# enforces before running it.
class ToolSpec(WireModel):
    """What the app declares about one tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    side_effect: Literal["read", "write", "irreversible"] = "read"
    confirm: str | None = None
    pii: list[str] | None = None
    timeout_s: float | None = None


# Either an output or an error, never both.
class ToolResult(WireModel):
    """What came back from running a tool in the app's process."""

    call_id: str
    name: str
    output: Any = None
    error: str | None = None
    summary: str | None = None
    duration_s: float | None = None


# One thing remembered about a contact: a sentence, where it came from, and how well it matched when
# recalled.
class MemoryFact(WireModel):
    """One thing remembered about a contact."""

    id: str | None = None
    text: str
    category: str | None = None
    score: float | None = None
    source: str | None = None


# One operation against the contact's memory: a recall during the turn, a remember at hangup, or a
# forget on request.
class MemoryOp(WireModel):
    """One operation against the contact's memory."""

    op: Literal["recall", "remember", "forget"]
    contact: str | None = None
    query: str | None = None
    facts: list[MemoryFact]
    took_ms: float


class DocSource(WireModel):
    """One chunk of the knowledge base that retrieval put in front of the model for this turn."""

    id: str
    path: str
    heading: str | None = None
    score: float
    excerpt: str | None = None


class CostRate(WireModel):
    """The exchange rate the cost was computed with, stated so the number can be reproduced."""

    currency: Literal["EUR"] = "EUR"
    usd_to_eur: float
    as_of: str


class CostRow(WireModel):
    """One priced line: a model, what was counted, how much, and what it came to."""

    provider: str
    model: str
    unit: Literal[
        "input_tokens",
        "cached_input_tokens",
        "cache_creation_tokens",
        "output_tokens",
        "characters",
        "audio_seconds",
        "requests",
        "session_seconds",
    ]
    quantity: float
    unit_price_usd: float
    eur: float


# It is listed, never priced at zero.
class UnpricedRow(WireModel):
    """A usage row the price table does not know."""

    provider: str
    model: str


# The runtime never prices commercially; this is the provider's bill as best we know it.
class Cost(WireModel):
    """What the call cost in provider fees, informational, in euros."""

    eur: float
    rate: CostRate
    rows: list[CostRow]
    unpriced: list[UnpricedRow]


# Which voice speaks for the agent: the name it was asked for, or the id the provider knows it by.
class VoiceConfig(WireModel):
    """Which voice speaks for the agent."""

    name: str | None = None
    provider: str | None = None
    model: str | None = None
    voice_id: str | None = None


class ModelConfig(WireModel):
    """Which model does a job (the LLM, or the STT), and the one or two knobs worth turning."""

    provider: str
    model: str
    temperature: float | None = None


class TurnConfig(WireModel):
    """How the session decides that the caller has finished, and when the caller may interrupt."""

    min_interruption_words: int | None = None
    endpointing_ms: int | None = None


# How the voice says one word it would otherwise get wrong: a proper name, a brand, a street.
class Pronunciation(WireModel):
    """How the voice says one word it would otherwise get wrong."""

    word: str
    spoken: str


# A field never declared is tenant.
class StateFieldSpec(WireModel):
    """What the app declares about one field of its state: who may see it."""

    name: str
    visibility: Visibility


# An event nobody declared is refused before it touches the log.
class EventSpec(WireModel):
    """One outside event the agent accepts, and from whom."""

    name: str
    from_: list[EventSource] = Field(alias="from")


class KnowledgeFile(WireModel):
    """One file of a base, as a push sends it: its path as the tenant keeps it, and its text."""

    path: str
    text: str


# It is named by the base it was pushed under, with PUT /v1/knowledge/{base}.
class DocsConfig(WireModel):
    """The knowledge base the agent answers from, and how its chunks reach the model."""

    base: str
    mode: DocsMode = "retrieved"
    k: int = 8
    min_score: float | None = None


# Exactly one of the two, because there are only two ways to open one: `say` are the words
# themselves and `reply` is what the model is told before it finds its own. They are agent.say and
# agent.reply declared instead of called, so a class that opens every call the same way needs no
# onCall hook to do it, and an operator can turn the opening at the pipeline door without a deploy.
# Absent: nobody speaks until the caller does.
class GreetingConfig(WireModel):
    """How the agent opens a call, before the caller has said anything."""

    say: str | None = None
    reply: str | None = None
    allow_interruptions: bool | None = None


# Declaring this is what puts livekit's own end_call tool in front of the model; a class that says
# nothing here cannot hang up, and the call ends when the caller does or when a supervisor says so.
# The tool is hidden while the agent is greeting, because a model that can hang up on its first turn
# eventually does.
class HangupConfig(WireModel):
    """Whether the model may end the call itself."""

    when: str = ""


# Both lists are in the tenant's own words.
class MemoryConfig(WireModel):
    """What memory keeps about a contact across calls, and what it must never keep."""

    remember: list[str] = Field(default_factory=list[str])
    forget: list[str] = Field(default_factory=list[str])


# What an app declares about its agent: the prompt's layout, the language, the tools, whether it
# searches its bases itself, and who may see and send what. Every field is optional so a configure
# can change one thing. The environment — voice, models, greeting, hangup, turn, says, hears,
# knowledge, docs, memory — is the world's, set in the agent's settings, and no longer read off this
# declaration.
class AgentConfig(WireModel):
    """What an app declares about its agent."""

    prompt: list[PromptBlockSpec] | None = None
    language: str | None = None
    greeting: GreetingConfig | None = None
    voice: VoiceConfig | None = None
    llm: ModelConfig | None = None
    stt: ModelConfig | None = None
    turn: TurnConfig | None = None
    says: list[Pronunciation] | None = None
    hears: list[str] | None = None
    knowledge: KnowledgeFile | None = None
    docs: DocsConfig | None = None
    memory: MemoryConfig | None = None
    hangup: HangupConfig | None = None
    tools: list[ToolSpec] | None = None
    uses_knowledge: bool = False
    state_fields: list[StateFieldSpec] | None = None
    events: list[EventSpec] | None = None
