"""Generated from schema/commands/: one model per command."""

from typing import Any, Literal

from pydantic import Field

from pinecall_protocol._base import WireModel
from pinecall_protocol.defs import AgentConfig, Contact, Route, Supervisor, ToolSpec, TransferMode
from pinecall_protocol.verbs import Verb


# Declare or change what the agent is: voice, models, language, greeting, the full tool list. Only
# the fields sent change.
class AgentConfigure(WireModel):
    """Declare or change what the agent is."""

    config: AgentConfig


class AgentDrain(WireModel):
    """This socket is leaving, and its calls go on without it."""


# The gateway answers agent.registered, or error.
class AgentRegister(WireModel):
    """The app's first message: this socket speaks for this agent and answers these doors."""

    routes: list[Route]
    sdk: str | None = None
    host: str | None = None
    takes_unclaimed: bool = True


# Make the model speak now, guided by an instruction it reads and the caller never hears: 'tell them
# a slot at 10:15 just opened'. On livekit's session.generate_reply; the sibling of agent.say, which
# speaks verbatim. The reply lands as turn.agent.
class AgentReply(WireModel):
    """Make the model speak now, guided by an instruction it reads and the caller never hears."""

    instructions: str
    allow_interruptions: bool | None = None


# Make the agent say this text now, verbatim, outside the model's turn: a greeting, a read-back, a
# system notice. The reply lands as turn.agent.
class AgentSay(WireModel):
    """Make the agent say this text now, verbatim, outside the model's turn."""

    text: str
    allow_interruptions: bool | None = None


# Ask for a person without sending the caller anywhere: the call waits on hold until a supervisor
# takes the line, or until wait_s passes with nobody taking it. attention.answered says which.
class CallAttention(WireModel):
    """Ask for a person without sending the caller anywhere."""

    reason: str
    wait_s: float


# Lands as callback.requested with via agent; placing the call is the app's.
class CallCallback(WireModel):
    """Write down that the caller wants to be called back."""

    number: str
    when: str | None = None
    note: str | None = None


class CallClaim(WireModel):
    """The code the caller said, to bind this call to the page that shows it."""

    code: str = Field(pattern="^[0-9]{4}$")


# The new call's log opens with call.dialing; call.started follows when the far end answers.
class CallDial(WireModel):
    """Place an outbound call as this agent."""

    to: str
    from_: str | None = Field(None, alias="from")
    caller: Contact | None = None
    metadata: dict[str, Any] | None = None


class CallDtmf(WireModel):
    """Send touch tones down the line, for an IVR on the far end."""

    digits: str


# Hand the agent a fact from the tenant's backend: a slot freed, an order shipped, a payment
# confirmed. Lands as event.received with source app. The agent must have declared the name in its
# events with app among the senders, or the gateway answers error and nothing touches the log.
class CallEvent(WireModel):
    """Hand the agent a fact from the tenant's backend."""

    name: str
    data: dict[str, Any]


# call.ended follows with reason agent_hung_up.
class CallHangup(WireModel):
    """End the call from the app's side."""

    reason: str | None = None


class CallHold(WireModel):
    """Put the caller on hold: they hear hold audio, the agent hears nothing."""


# It gets a seq like everything else and lands as custom.
class CallLog(WireModel):
    """Write a line of the app's own into the call's log."""

    name: str
    data: dict[str, Any]


class CallMute(WireModel):
    """Mute the agent: it keeps listening and thinking, produces no audio."""


# call.transferred says whether it worked, and which mode it was.
class CallTransfer(WireModel):
    """Send the caller to another number, or bring that number into the call."""

    to: str
    mode: TransferMode | None = None


class CallUnhold(WireModel):
    """Take the caller off hold."""


class CallUnmute(WireModel):
    """Unmute the agent."""


# Why the verb did not run, in the words the console shows: the status it travels under, and the
# sentence.
class DevRefusal(WireModel):
    """Why the verb did not run, in the words the console shows."""

    status: int
    detail: str


class DevAnswer(WireModel):
    """What came of one dev.request, named by its id."""

    id: str
    result: dict[str, Any] | None = None
    refused: DevRefusal | None = None


# Silence a participant for the rest of the call: their audio leaves the room, for everyone in it.
# Lands as track.unpublished for their microphone. There is no unmute; a leg that must speak again
# is invited again.
class ParticipantMute(WireModel):
    """Silence a participant for the rest of the call."""

    identity: str


# Lands as participant.left with reason participant_removed. Removing the caller ends the call.
class ParticipantRemove(WireModel):
    """Put a participant out of the room."""

    identity: str


class Ping(WireModel):
    """Is the socket alive? The gateway answers pong."""


# The name must be one of the agent's declared blocks, or one of the default four; anything else is
# refused with the name.
class PromptSet(WireModel):
    """Rewrite one block of the prompt, whole, by name."""

    name: str
    text: str


# A second SIP leg dialed to a number is the warm path: the agent stays on with the caller while the
# other side answers. Lands as participant.joined when they arrive, or error when they do not.
class RoomInvite(WireModel):
    """Bring somebody else into the call's room."""

    to: str
    kind: Literal["sip", "participant"]


# Push a payload to a browser in the room over the DataChannel: a card to render, a form to open.
# Lands as room.sent with the size, never the payload. The widget listens on pinecall.ui; a topic of
# the tenant's own reaches the tenant's own page code.
class RoomSend(WireModel):
    """Push a payload to a browser in the room over the DataChannel."""

    topic: str
    data: dict[str, Any]
    to: str | None = None


# Set up this one call before the first turn: the app's initial state, and any config that differs
# from the agent's defaults for this caller.
class SessionConfigure(WireModel):
    """Set up this one call before the first turn."""

    state: dict[str, Any] | None = None
    config: AgentConfig | None = None


# The platform logs state.changed and re-renders.
class StateSet(WireModel):
    """The app's state changed and this is all of it."""

    state: dict[str, Any]
    changed: list[str] | None = None


class SupervisorVerb(WireModel):
    """One supervise verb, from the human the door named."""

    by: Supervisor
    verb: Verb


# The full list was declared in agent.configure; this is the subset whose when allows them in this
# state.
class ToolsSet(WireModel):
    """The tools the model may see now."""

    tools: list[ToolSpec]
