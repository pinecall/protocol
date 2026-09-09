"""Generated from schema/room.json: the room's facts and the outside world's."""

from typing import Any

from pinecall_protocol._base import WireModel
from pinecall_protocol.defs import Channel, EventSource, ParticipantKind, TrackKind, TrackSource


# Phone and web calls have one; a text session has no room and never logs this.
class RoomOpened(WireModel):
    """The LiveKit room exists and the call lives in it."""

    name: str
    sid: str
    channel: Channel


# Somebody joined the room: the caller over SIP or the widget, the agent, a supervisor, a listener,
# or a second SIP leg. Their attributes travel verbatim: the caller's number is a fact of the room,
# not a field we invent.
class ParticipantJoined(WireModel):
    """Somebody joined the room."""

    identity: str
    kind: ParticipantKind
    name: str | None = None
    attributes: dict[str, Any]


# When it is the caller, call.ended follows.
class ParticipantLeft(WireModel):
    """Somebody left the room."""

    identity: str
    reason: str


# Ephemeral: it is a light for the console, and the turns say who spoke.
class ParticipantSpeaking(WireModel):
    """The room's own voice activity for one participant flipped."""

    identity: str
    speaking: bool


class TrackPublished(WireModel):
    """A participant put a track on the room: their microphone, their camera, a screen."""

    identity: str
    kind: TrackKind
    source: TrackSource


# A participant's track left the room: they stopped sharing, or a participant.mute took their audio
# away.
class TrackUnpublished(WireModel):
    """A participant's track left the room."""

    identity: str
    kind: TrackKind
    source: TrackSource


# A fact arrived from outside the conversation: the tenant's backend sent call.event, or a
# participant's browser sent pinecall.event. One event for both, told apart by source. It reached
# the log only because the agent declared the name in its events, from that source; anything else
# was refused before this.
class EventReceived(WireModel):
    """A fact arrived from outside the conversation."""

    name: str
    data: dict[str, Any]
    source: EventSource
    identity: str | None = None


# Ephemeral, and the payload stays out of the log: the tenant chose what to send and to whom.
class RoomSent(WireModel):
    """The agent pushed a payload to a browser in the room, on the tenant's room.send."""

    topic: str
    to: str | None = None
    bytes: int
