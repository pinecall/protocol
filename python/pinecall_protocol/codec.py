"""JSON in, models out, and back. The only file that touches a key name: aliases, by_alias."""

from typing import Any

from pydantic import TypeAdapter, ValidationError

from pinecall_protocol._base import ProtocolError, WireModel
from pinecall_protocol.envelope import Command, Entry
from pinecall_protocol.registry import COMMANDS, EVENTS

_LOG: TypeAdapter[list[Entry]] = TypeAdapter(list[Entry])


def decode_entry(raw: dict[str, Any]) -> Entry:
    """One log line from decoded JSON. A bad shape is a ProtocolError."""
    return _validate(Entry, raw, "entry")


def decode_entries(text: str) -> list[Entry]:
    """A whole log from a JSON array text, in the order it came."""
    try:
        return _LOG.validate_json(text)
    except ValidationError as error:
        raise ProtocolError(f"log: {error}") from error


def event_of(entry: Entry) -> WireModel:
    """The entry's data as the model its type names. Unknown type or bad shape: ProtocolError."""
    model = EVENTS.get(entry.type)
    if model is None:
        raise ProtocolError(f"unknown event type: {entry.type}")
    return _validate(model, entry.data, entry.type)


def command_of(command: Command) -> WireModel:
    """The command's data as the model its type names. Unknown type or bad shape: ProtocolError."""
    model = COMMANDS.get(command.type)
    if model is None:
        raise ProtocolError(f"unknown command type: {command.type}")
    return _validate(model, command.data, command.type)


def encode(model: WireModel) -> dict[str, Any]:
    """A model as it goes on the wire: wire key names, absent fields absent, JSON-ready values."""
    return model.model_dump(mode="json", by_alias=True, exclude_unset=True)


def _validate[T: WireModel](model: type[T], raw: dict[str, Any], what: str) -> T:
    try:
        return model.model_validate(raw)
    except ValidationError as error:
        raise ProtocolError(f"{what}: {error}") from error
