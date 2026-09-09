"""Generated from schema/rest.json: the envelopes the read doors answer in."""

from pydantic import Field

from pinecall_protocol._base import WireModel
from pinecall_protocol.defs import (
    Channel,
    Contact,
    Cost,
    Direction,
    EndReason,
    KnowledgeFile,
    MarkerName,
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


class SessionLine(WireModel):
    """One call as a list draws it: which call, how far the log got, and the state's own fields."""

    call: str
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


class SessionList(WireModel):
    """GET /v1/agents/{slug}/sessions: which calls that agent handled, newest first."""

    calls: list[SessionLine]


class HeldAgent(WireModel):
    """One agent, as somebody choosing which to open needs to see it: its name and its channels."""

    slug: str
    channels: list[Channel]


class AgentList(WireModel):
    """GET /v1/agents: every agent this fleet is holding right now, as the front page lists them."""

    agents: list[HeldAgent]


# The base is replaced, never merged.
class KnowledgePush(WireModel):
    """PUT /v1/knowledge/{base}, the body: the tenant's folder as of now, sent whole."""

    files: list[KnowledgeFile]


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


# The view wrote it and never resolves it.
class FillMarker(WireModel):
    """One marker the worker found in a dynamic block, as the gateway is asked to fill it."""

    name: MarkerName
    payload: str


# POST /v1/calls/{call}/fill, the body: what the caller just said and the markers to fill before the
# model is asked. Worker-only; the gateway writes memory.ops and docs.sources on the call's log
# itself.
class FillRequest(WireModel):
    """POST /v1/calls/{call}/fill, the body."""

    query: str
    markers: list[FillMarker]
    speech_id: str | None = None


class Fill(WireModel):
    """One marker filled: the marker as it was asked, and the text that takes its line."""

    name: MarkerName
    payload: str
    text: str


# POST /v1/calls/{call}/fill, the answer: every marker filled, and how long the whole fill took.
class Fills(WireModel):
    """POST /v1/calls/{call}/fill, the answer."""

    fills: list[Fill]
    took_ms: float


# POST /v1/calls/{call}/remember, the answer: what the call taught about the contact, counted.
# Worker-only; the body is empty, the gateway reads the turns off its own log and writes memory.ops
# itself.
class Remembered(WireModel):
    """POST /v1/calls/{call}/remember, the answer."""

    ops: int
    took_ms: float
