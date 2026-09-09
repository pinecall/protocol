"""Generated from schema/envelope.json: the log entry and the command frame."""

from typing import Any

from pinecall_protocol._base import WireModel


# seq is written before control returns, so two readers never disagree about order.
class Entry(WireModel):
    """One line of a call's log, or of an agent's log when call is null."""

    seq: int
    ts: float
    call: str | None
    agent: str
    type: str
    ephemeral: bool
    data: dict[str, Any]


# The gateway answers with the events the command produces, or with an error naming the command's
# id.
class Command(WireModel):
    """One instruction from an app to the gateway over its WebSocket."""

    type: str
    agent: str
    call: str | None
    id: str | None = None
    data: dict[str, Any]
