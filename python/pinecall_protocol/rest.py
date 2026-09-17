"""Generated from schema/rest.json: the envelopes the read doors answer in."""

from typing import Any, Literal

from pydantic import Field

from pinecall_protocol._base import WireModel
from pinecall_protocol.defs import (
    Channel,
    Contact,
    Cost,
    Direction,
    EndReason,
    Env,
    KnowledgeFile,
    PlatformTool,
)
from pinecall_protocol.envelope import Entry
from pinecall_protocol.state import CallStatus, State


class CallState(WireModel):
    """GET /v1/calls/{call}/state: the whole log folded, and the seq a stream resumes from."""

    state: State
    last_seq: int
    live: bool


class LogPage(WireModel):
    """One page of a log: what this reader may see, whether the log is open, and where to resume."""

    entries: list[Entry]
    live: bool
    next: int | None


# One call's call.score as a list draws it: how many judges held of how many answered, and why the
# first one that broke did.
class SessionScore(WireModel):
    """One call's call.score as a list draws it."""

    held: int
    judged: int
    passed: bool
    reason: str | None


# escalated: a person took part — a transfer, a supervisor taking the line, saying something, or
# ending the call. low_score: a judge answered broken. promise: the promises judge found the agent
# committing the business to something no tool call records.
type SessionFlag = Literal["escalated", "low_score", "promise"]


class SessionLine(WireModel):
    """One call as a list draws it: which call, how far the log got, and the state's own fields."""

    call: str
    agent: str
    live: bool
    last_seq: int
    status: CallStatus
    channel: Channel | None
    direction: Direction | None
    from_: str | None = Field(alias="from")
    to: str | None
    caller: Contact | None
    started_at: float | None
    ended_at: float | None
    end_reason: EndReason | None
    outcome: str | None
    cost: Cost | None
    score: SessionScore | None = None
    flags: list[SessionFlag] | None = None


# GET /v1/agents/{slug}/sessions and GET /v1/sessions: the calls that match, newest first, a page at
# a time.
class SessionList(WireModel):
    """GET /v1/agents/{slug}/sessions and GET /v1/sessions."""

    calls: list[SessionLine]
    total: int | None = None
    next: str | None = None


class InsightsConversations(WireModel):
    """How many calls started on the day, and on the day before it."""

    today: int
    yesterday: int


class InsightsChannels(WireModel):
    """The day's calls by the door they came in by."""

    phone: int
    web: int
    whatsapp: int


class InsightsAgent(WireModel):
    """One agent's day."""

    slug: str
    today: int
    score: float | None


class InsightsBudget(WireModel):
    """What the org may spend in a month and what it has spent so far, both worlds together."""

    limit_eur: float | None
    spent_eur_month: float


# GET /v1/insights: one day of the key's world and corner at a glance, counted off the call index
# and never off a log.
class Insights(WireModel):
    """GET /v1/insights."""

    day: str
    timezone: str
    conversations: InsightsConversations
    resolved_rate: float | None
    median_e2e_s: float | None
    spend_eur: float
    channels: InsightsChannels
    sessions_total: int
    live: int
    agents: list[InsightsAgent]
    budget: InsightsBudget


# GET and PUT /v1/org/judging: whether the org's calls are judged at hang-up, and what judging one
# may spend on a model.
class Judging(WireModel):
    """GET and PUT /v1/org/judging."""

    on: bool
    ceiling_eur: float | None


class JudgingWanted(WireModel):
    """PUT /v1/org/judging, the body."""

    on: bool


# in: the contact wrote it. out: the agent, or a person as the agent, did. call: a spoken call,
# drawn as one pill.
type ThreadKind = Literal["in", "out", "call"]


class ThreadLast(WireModel):
    """The newest thing on a contact's thread."""

    text: str | None
    at: float
    kind: ThreadKind


class ThreadLine(WireModel):
    """One contact of an agent's inbox: every call of theirs, folded into one line."""

    contact: str
    name: str | None
    channel_last: Channel
    last: ThreadLast
    unread: int
    calls: int


class ThreadList(WireModel):
    """GET /v1/agents/{slug}/threads: the agent's contacts, the newest thread first."""

    threads: list[ThreadLine]
    next: str | None


class ThreadMessage(WireModel):
    """One message of a thread, or one spoken call drawn as a pill."""

    kind: ThreadKind
    text: str | None
    at: float
    call: str
    channel: Channel
    duration_s: float | None = None
    answered: bool | None = None


class Thread(WireModel):
    """GET /v1/agents/{slug}/threads/{contact}: every call of one contact, merged, oldest first."""

    contact: str
    name: str | None
    messages: list[ThreadMessage]


class ThreadSay(WireModel):
    """POST /v1/agents/{slug}/threads/{contact}/messages, the body."""

    text: str


# The turn.agent it lands as is on that call's log.
class ThreadSaid(WireModel):
    """POST /v1/agents/{slug}/threads/{contact}/messages, the answer: the call it was said on."""

    contact: str
    call: str


class AgentFact(WireModel):
    """One current fact memory holds, across the contacts an agent's calls taught."""

    id: str
    contact: str
    text: str
    category: str | None
    written_at: float


class AgentMemory(WireModel):
    """GET /v1/agents/{slug}/memory: the current facts the agent's calls taught, newest first."""

    facts: list[AgentFact]
    next: str | None


# GET and PUT /v1/agents/{slug}/widget: how the widget presents this agent, kept per org, world and
# agent. PUT takes the whole set.
class WidgetSettings(WireModel):
    """GET and PUT /v1/agents/{slug}/widget."""

    title: str | None
    tagline: str | None
    greeting: str | None
    accent: str | None
    autostart: bool


# GET and PUT /v1/org/sso: the OpenID Connect provider this org's people sign in at, and never the
# client secret it was wired with.
class OrgSso(WireModel):
    """GET and PUT /v1/org/sso."""

    configured: bool
    issuer: str | None
    client_id: str | None
    domains: list[str]
    role: str | None
    required: bool
    redirect_uri: str


# The configuration is replaced whole, the client secret included: it is write-only, so a change of
# anything else carries it again.
class OrgSsoWanted(WireModel):
    """PUT /v1/org/sso, the body."""

    issuer: str
    client_id: str
    client_secret: str
    domains: list[str]
    role: str | None = None
    required: bool | None = None


# One org a sign-in page may send somebody to, named — and nothing about whether anybody answers to
# the address that asked.
class SsoOrg(WireModel):
    """SsoOrg, as protocol/schema declares it."""

    org: str
    slug: str
    name: str


# POST /v1/login/sso/discover: the orgs whose domains match an address's and that wired a provider.
# Empty is the answer for a domain nobody wired, and for a box that keeps no provider at all.
class SsoDiscovery(WireModel):
    """POST /v1/login/sso/discover."""

    orgs: list[SsoOrg]


# One corner of a world holding an agent: the member whose it is, named so a person can read it.
class LineHolder(WireModel):
    """One corner of a world holding an agent."""

    holder: str | None
    name: str | None


class HeldAgent(WireModel):
    """One agent, as somebody choosing which to open needs to see it: its name and its channels."""

    slug: str
    channels: list[Channel]
    holder: LineHolder | None = None


class AgentList(WireModel):
    """GET /v1/agents: every agent this fleet is holding right now, as the front page lists them."""

    agents: list[HeldAgent]


# GET /v1/agents/{slug}/line: whose terminal a call that RINGS at this agent's doors lands in. An
# org shares one sandbox number, so it rings in one place and which one is claimed.
class TheLine(WireModel):
    """GET /v1/agents/{slug}/line."""

    agent: str
    env: Env
    held: bool
    holding: LineHolder | None = None
    yours: bool
    waiting: list[LineHolder]
    calling: list[str]


# The base is replaced, never merged.
class KnowledgePush(WireModel):
    """PUT /v1/knowledge/{base}, the body: the tenant's folder as of now, sent whole."""

    files: list[KnowledgeFile]


# A chunk answers when its file and heading path start with `expects`, so naming a file alone
# accepts any chunk of it and naming a heading accepts that section.
class GoldenQuestion(WireModel):
    """One question of a base's golden: what somebody asks, and the chunk that should answer it."""

    asks: str
    expects: str


# A golden is fixed and the index is the variable; a question is never softened so a change can
# pass.
class KnowledgeGolden(WireModel):
    """POST /v1/knowledge/{base}/eval, the body: the questions a base is held to."""

    questions: list[GoldenQuestion]
    k: int | None = None


# One question whose expected chunk was not among the k returned, and what came back instead.
class GoldenMiss(WireModel):
    """GoldenMiss, as protocol/schema declares it."""

    asks: str
    expects: str
    found: list[str]


# Both figures are computed by code, with no model, so two runs of the same golden over the same
# base answer the same numbers.
class KnowledgeScore(WireModel):
    """POST /v1/knowledge/{base}/eval, the answer: how the index did on its own golden."""

    base: str
    model: str
    questions: int
    k: int
    recall_at_k: float
    ndcg_at_10: float
    took_ms: float
    misses: list[GoldenMiss]


# PUT /v1/knowledge/{base}, the answer: which base, how many chunks it became, and how long that
# took.
class KnowledgePushed(WireModel):
    """PUT /v1/knowledge/{base}, the answer."""

    base: str
    chunks: int
    took_ms: float


class KnowledgeBase(WireModel):
    """One knowledge base as the list draws it: its name, its size, and when it was last pushed."""

    base: str
    chunks: int
    model: str
    pushed_at: float


class KnowledgeList(WireModel):
    """GET /v1/knowledge: every base this org has pushed."""

    bases: list[KnowledgeBase]


# A fact is never deleted, only superseded, so the history keeps every version.
class ContactFact(WireModel):
    """One fact of a contact's history: a MemoryFact with the two dates that bound it."""

    id: str | None = None
    text: str
    category: str | None = None
    source: str | None = None
    valid_from: float
    invalidated_at: float | None


# GET /v1/contacts/{contact}/memory: everything memory ever kept about one contact, current facts
# first.
class ContactMemory(WireModel):
    """GET /v1/contacts/{contact}/memory."""

    facts: list[ContactFact]


# DELETE /v1/contacts/{contact}/memory, the answer: how many facts the right to be forgotten erased.
class Forgotten(WireModel):
    """DELETE /v1/contacts/{contact}/memory, the answer."""

    forgotten: int


# One question of a memory golden: what memory holds about the contact who asks it, the words they
# just said, and the fact or facts that should come back. The facts are the question's own, so a
# golden needs no contact in any table.
class MemoryQuestion(WireModel):
    """One question of a memory golden."""

    holds: list[str]
    asks: str
    expects: list[str]


# Each question brings its own facts, which are written to a scratch contact of this org, asked, and
# deleted. A golden is fixed and the ranking is the variable; a question is never softened so a
# change can pass.
class MemoryGolden(WireModel):
    """POST /v1/contacts/memory/eval, the body: the questions memory is held to."""

    questions: list[MemoryQuestion]
    k: int | None = None


# One question memory did not answer whole: what it wanted and did not get, and what came back
# instead. GoldenMiss is the knowledge base's and names the one chunk that should have won; a memory
# question may expect several facts and miss some of them.
class MemoryMiss(WireModel):
    """One question memory did not answer whole."""

    asks: str
    missing: list[str]
    found: list[str]


# POST /v1/contacts/memory/eval, the answer: how memory ranked the facts its own golden asked for.
# Both figures are computed by code, with no model in the loop, so two runs of one golden answer the
# same numbers.
class MemoryScore(WireModel):
    """POST /v1/contacts/memory/eval, the answer."""

    model: str
    questions: int
    k: int
    recall_at_k: float
    ndcg_at_10: float
    took_ms: float
    misses: list[MemoryMiss]


# What must come of one call's hang-up: each field is one of the four ways a hang-up costs a
# business. Nothing here compares one sentence to another — a category is the class's own word, a
# value is a literal the caller said out loud, and a supersession is an id — because two ways of
# writing one fact are one fact.
class ExtractionExpected(WireModel):
    """What must come of one call's hang-up."""

    writes: list[str] = Field(default_factory=list[str])
    never: list[str] = Field(default_factory=list[str])
    never_says: list[str] = Field(default_factory=list[str])
    invalidates: list[str] = Field(default_factory=list[str])


# One call written down and what memory must make of it: the write side of the table, judged by
# code. The read side is MemoryGolden and neither answers for the other — a call may extract the
# perfect fact and never see it again, because six is what a turn is handed and the seventh is cut.
class ExtractionGolden(WireModel):
    """One call written down and what memory must make of it."""

    name: str
    said: list[tuple[str, str]]
    holds: list[str] = Field(default_factory=list[str])
    plants: list[str] = Field(default_factory=list[str])
    channel: Channel = "phone"
    expect: ExtractionExpected = Field(default_factory=ExtractionExpected)


# POST /v1/agents/{slug}/memory/extraction, the body: the goldens whole, as the tenant wrote them
# down. Each costs ONE model call — the very one a hang-up makes — run on the org's own model and
# keys against the class the caller is holding.
class ExtractionCases(WireModel):
    """POST /v1/agents/{slug}/memory/extraction, the body."""

    cases: list[ExtractionGolden]


# One thing that did not hold about a case: which of the questions, and the evidence in a sentence a
# person can act on.
class ExtractionBroke(WireModel):
    """One thing that did not hold about a case."""

    check: str
    detail: str


class ExtractionJudged(WireModel):
    """One case, run: what memory would have kept, what admission refused, and what did not hold."""

    name: str
    held: bool
    wrote: list[str] = Field(default_factory=list[str])
    refused: list[str] = Field(default_factory=list[str])
    broke: list[ExtractionBroke] = Field(default_factory=list[ExtractionBroke])


# POST /v1/agents/{slug}/memory/extraction, the answer: which model answered, how many cases held,
# and every one of them. A verb prints this and a pipeline exits on it.
class ExtractionRun(WireModel):
    """POST /v1/agents/{slug}/memory/extraction, the answer."""

    agent: str
    model: str
    cases: int
    held: int
    took_ms: float
    results: list[ExtractionJudged]


# POST /v1/calls/{call}/lookup, the body: which platform tool to run for this turn, and what to run
# it with. Worker-only; the gateway runs it against its own stores and writes memory.ops or
# docs.sources on the call's log itself.
class LookupRequest(WireModel):
    """POST /v1/calls/{call}/lookup, the body."""

    tool: PlatformTool
    input: dict[str, Any]
    speech_id: str | None = None


# POST /v1/calls/{call}/lookup, the answer: what the tool found, and how long finding it took. The
# output is JSON-encoded into a tool_result block, which is where everything from outside the
# conversation goes and the only place it goes.
class LookupResult(WireModel):
    """POST /v1/calls/{call}/lookup, the answer."""

    output: dict[str, Any]
    took_ms: float


# POST /v1/calls/{call}/remember, the answer: what the call taught about the contact, counted.
# Worker-only; the body is empty, the gateway reads the turns off its own log and writes memory.ops
# itself.
class Remembered(WireModel):
    """POST /v1/calls/{call}/remember, the answer."""

    ops: int
    took_ms: float
