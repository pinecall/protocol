"""Generated from schema/verbs.json: the supervise verbs."""

from typing import Annotated, Literal

from pydantic import Field

from pinecall_protocol._base import WireModel
from pinecall_protocol.defs import TransferMode


# Logged as supervisor.said.
class SayVerb(WireModel):
    """Make the agent say this, verbatim, to the caller."""

    verb: Literal["say"] = "say"
    text: str


# It reaches the agent as an instruction for its next reply; logged as supervisor.whispered.
class WhisperVerb(WireModel):
    """Tell the agent something the caller never hears."""

    verb: Literal["whisper"] = "whisper"
    text: str


# The supervisor takes the line: the agent goes quiet and the supervisor's audio replaces it. Logged
# as supervisor.took_over.
class TakeoverVerb(WireModel):
    """The supervisor takes the line."""

    verb: Literal["takeover"] = "takeover"


# Logged as supervisor.released.
class ReleaseVerb(WireModel):
    """The supervisor hands the line back to the agent, which resumes with the history intact."""

    verb: Literal["release"] = "release"


# Logged as supervisor.transferred, then call.transferred says whether it worked.
class TransferVerb(WireModel):
    """Send the caller to another number."""

    verb: Literal["transfer"] = "transfer"
    to: str
    mode: TransferMode | None = None


# Hang up on the caller's behalf, at once: a sentence playing and a reply still being written are
# cut, not finished. Logged as supervisor.ended, then call.ended with reason supervisor_ended.
class EndVerb(WireModel):
    """Hang up on the caller's behalf, at once."""

    verb: Literal["end"] = "end"
    reason: str | None = None


# One supervise verb, told apart by its verb field.
type Verb = Annotated[
    SayVerb | WhisperVerb | TakeoverVerb | ReleaseVerb | TransferVerb | EndVerb,
    Field(discriminator="verb"),
]
