"""Emits the pydantic v2 models: one module per schema file, a registry per message kind, the codec."""

from __future__ import annotations

import keyword
import re
import textwrap
from pathlib import Path

from schema import MISSING, MODULES, Bundle, Definition, Message, Property, Shape

PACKAGE = "pinecall_protocol"

HEADLINES = {
    "defs": "Generated from schema/defs.json: the shapes shared across the wire.",
    "metrics": "Generated from schema/metrics.json: every livekit-agents 1.8 metric, verbatim.",
    "room": "Generated from schema/room.json: the room's facts and the outside world's.",
    "state": "Generated from schema/state.json: what a log reduces to.",
    "verbs": "Generated from schema/verbs.json: the supervise verbs.",
    "envelope": "Generated from schema/envelope.json: the log entry and the command frame.",
    "events": "Generated from schema/events/: one model per event.",
    "commands": "Generated from schema/commands/: one model per command.",
    "rest": "Generated from schema/rest.json: the envelopes the read doors answer in.",
    "registry": "Generated from schema: every event and command by its wire type.",
}


def emit(bundle: Bundle, out_dir: Path) -> list[Path]:
    """Write every module and return the paths, so the caller can format them."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for module in MODULES:
        written.append(_write(out_dir / f"{module}.py", _module_source(bundle, module)))
    written.append(_write(out_dir / "registry.py", _registry_module_source(bundle)))
    written.append(_write(out_dir / "_base.py", BASE_SOURCE))
    written.append(_write(out_dir / "codec.py", CODEC_SOURCE))
    written.append(_write(out_dir / "__init__.py", INIT_SOURCE))
    return written


def _write(path: Path, source: str) -> Path:
    path.write_text(source)
    return path


def _module_source(bundle: Bundle, module: str) -> str:
    blocks = [_definition_source(definition) for definition in bundle.module(module)]
    body = "\n\n\n".join(blocks)
    imports = _imports_source(body, _model_imports(bundle, module))
    return f'"""{HEADLINES[module]}"""\n\n{imports}\n\n{body}\n'


def _registry_module_source(bundle: Bundle) -> str:
    events = bundle.messages_of("event")
    commands = bundle.messages_of("command")
    blocks = [
        _registry_source("EVENTS", "EventType", events),
        _ephemeral_source(events),
        _terminal_source(bundle),
        _registry_source("COMMANDS", "CommandType", commands),
        _produces_source(commands),
    ]
    body = "\n\n\n".join(blocks)
    needed: dict[str, list[str]] = {}
    for kind in ("event", "command"):
        for other, names in bundle.roots_of(kind).items():
            needed[other] = sorted(set(needed.get(other, [])) | set(names))
    imports = _imports_source(body, dict(sorted(needed.items())))
    return f'"""{HEADLINES["registry"]}"""\n\n{imports}\n\n{body}\n'


def _model_imports(bundle: Bundle, module: str) -> dict[str, list[str]]:
    return {
        other: [name for name in names if name not in _root_only(bundle, module)]
        for other, names in bundle.imports_of(module).items()
    }


# A message whose data is a shape from another module (metrics.llm is LLMMetrics) needs no import
# in the models module; the registry imports it instead.
def _root_only(bundle: Bundle, module: str) -> set[str]:
    used_by_fields: set[str] = set()
    for definition in bundle.module(module):
        for prop in definition.properties:
            shape: Shape | None = prop.shape
            while shape is not None:
                if shape.ref is not None:
                    used_by_fields.add(shape.ref.name)
                shape = shape.items
        used_by_fields.update(member.name for member in definition.members)
    roots = {message.root.name for message in bundle.messages if f"{message.kind}s" == module}
    return roots - used_by_fields


def _imports_source(body: str, needed: dict[str, list[str]]) -> str:
    typing_names = [name for name in ("Annotated", "Any", "Literal") if re.search(rf"\b{name}\b", body)]
    lines: list[str] = []
    if typing_names:
        lines.append(f"from typing import {', '.join(typing_names)}")
    if "Field(" in body:
        lines.append("\nfrom pydantic import Field")
    lines.append(f"\nfrom {PACKAGE}._base import WireModel")
    for other, names in needed.items():
        if names:
            lines.append(f"from {PACKAGE}.{other} import {', '.join(names)}")
    return "\n".join(lines)


def _definition_source(definition: Definition) -> str:
    name = definition.ref.name
    if definition.kind == "enum":
        return _commented(definition.description) + f"type {name} = Literal[{_literals(definition.values)}]"
    if definition.kind == "union":
        members = " | ".join(member.name for member in definition.members)
        tag = definition.discriminator
        return _commented(definition.description) + (
            f'type {name} = Annotated[{members}, Field(discriminator="{tag}")]'
        )
    docstring, comment = _docstring_and_comment(definition.description, name)
    lines = [f"class {name}(WireModel):", f'    """{docstring}"""']
    if definition.properties:
        lines.append("")
        lines.extend(f"    {_field_source(prop)}" for prop in definition.properties)
    return comment + "\n".join(lines)


def _field_source(prop: Property) -> str:
    annotation = _annotation(prop.shape)
    if _absent_means_none(prop) and not prop.shape.nullable:
        annotation = "Any" if prop.shape.kind == "any" else f"{annotation} | None"
    name = prop.name
    alias = ""
    if keyword.iskeyword(name):
        name = f"{name}_"
        alias = f'alias="{prop.name}"'
    default = _default_source(prop, alias)
    return f"{name}: {annotation}{default}"


# A required field has no default, except a const, which is its own only value. An optional field
# is None when absent: the codec drops unset fields, so None never reaches the wire uninvited.
def _default_source(prop: Property, alias: str) -> str:
    shape = prop.shape
    if prop.default is not MISSING:
        return _explicit_default(prop.default, alias)
    if shape.kind == "const":
        return _field_call(repr(shape.const), alias)
    if prop.required:
        return f" = Field({alias})" if alias else ""
    return _field_call("None", alias)


def _absent_means_none(prop: Property) -> bool:
    return not prop.required and prop.default is MISSING and prop.shape.kind != "const"


def _explicit_default(default: object, alias: str) -> str:
    if default == [] or default == {}:
        factory = "list" if default == [] else "dict"
        parts = [f"default_factory={factory}"] + ([alias] if alias else [])
        return f" = Field({', '.join(parts)})"
    return _field_call(repr(default), alias)


def _field_call(value: str, alias: str) -> str:
    return f" = Field({value}, {alias})" if alias else f" = {value}"


def _annotation(shape: Shape) -> str:
    rendered = _bare_annotation(shape)
    if shape.nullable:
        return f"{rendered} | None"
    return rendered


def _bare_annotation(shape: Shape) -> str:
    match shape.kind:
        case "str" | "float" | "int" | "bool":
            return shape.kind
        case "any":
            return "Any"
        case "json":
            return "dict[str, Any]"
        case "list":
            assert shape.items is not None
            return f"list[{_annotation(shape.items)}]"
        case "ref":
            assert shape.ref is not None
            return shape.ref.name
        case "enum":
            return f"Literal[{_literals(shape.values)}]"
        case "const":
            return f"Literal[{shape.const!r}]"
    raise ValueError(f"unknown shape kind {shape.kind}")


def _literals(values: tuple[str, ...]) -> str:
    return ", ".join(repr(value) for value in values)


def _registry_source(name: str, alias: str, messages: list[Message]) -> str:
    rows = "\n".join(f'    "{message.type}": {message.root.name},' for message in messages)
    types = ",\n".join(f'    "{message.type}"' for message in messages)
    return (
        f"# Every {alias.removesuffix('Type').lower()} by its wire type; codec looks the model up here.\n"
        f"{name}: dict[str, type[WireModel]] = {{\n{rows}\n}}\n\n"
        f"type {alias} = Literal[\n{types},\n]"
    )


def _ephemeral_source(messages: list[Message]) -> str:
    names = ", ".join(f'"{message.type}"' for message in messages if message.ephemeral)
    return (
        "# Events a store may drop and a slow reader may miss: the entry's ephemeral flag defaults\n"
        "# to this.\n"
        f"EPHEMERAL_EVENTS: frozenset[str] = frozenset({{{names}}})"
    )


def _terminal_source(bundle: Bundle) -> str:
    return (
        "# The one event that ends a call: after it nothing more is true and the log is sealed.\n"
        f'TERMINAL_EVENT: str = "{bundle.terminal_event()}"'
    )


def _produces_source(messages: list[Message]) -> str:
    rows = "\n".join(
        f'    "{message.type}": ({", ".join(repr(t) for t in message.produces)}{"," if len(message.produces) == 1 else ""}),'
        for message in messages
    )
    return (
        "# Which events a command lands in the log as, so a caller knows what to wait for.\n"
        f"PRODUCES: dict[str, tuple[str, ...]] = {{\n{rows}\n}}"
    )


# The first sentence is the docstring when it fits on one line; the rest, or the whole description
# when it does not, becomes a comment above, wrapped to the line limit.
def _docstring_and_comment(description: str, name: str) -> tuple[str, str]:
    first, _, rest = description.partition(". ")
    if not rest:
        first, rest = description, ""
    elif not first.endswith("."):
        first += "."
    if len(first) <= 90:
        return first, _commented(rest)
    head, colon, _ = first.partition(": ")
    if colon and len(head) <= 89:
        return f"{head}.", _commented(description)
    return f"{name}, as protocol/schema declares it.", _commented(description)


def _commented(text: str) -> str:
    if not text:
        return ""
    return "\n".join(f"# {line}" for line in textwrap.wrap(text, width=98)) + "\n"


BASE_SOURCE = '''"""The base every wire model shares: unknown keys are refused; a field builds by name or alias."""

from pydantic import BaseModel, ConfigDict


class WireModel(BaseModel):
    """A shape on the wire. extra=forbid is the schema's additionalProperties: false."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True, validate_by_alias=True)


class ProtocolError(ValueError):
    """A message did not match the protocol: unknown type, bad shape, a seq out of order."""
'''

CODEC_SOURCE = '''"""JSON in, models out, and back. The only file that touches a key name: aliases, by_alias."""

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
'''

INIT_SOURCE = '''"""Generated from schema/ by `python generate`. Never edited by hand."""

from pinecall_protocol._base import ProtocolError, WireModel
from pinecall_protocol.codec import (
    command_of,
    decode_entries,
    decode_entry,
    encode,
    event_of,
)
from pinecall_protocol.envelope import Command, Entry
from pinecall_protocol.registry import (
    COMMANDS,
    EPHEMERAL_EVENTS,
    EVENTS,
    PRODUCES,
    TERMINAL_EVENT,
    CommandType,
    EventType,
)
from pinecall_protocol.state import State

__all__ = [
    "COMMANDS",
    "EPHEMERAL_EVENTS",
    "EVENTS",
    "PRODUCES",
    "TERMINAL_EVENT",
    "Command",
    "CommandType",
    "Entry",
    "EventType",
    "ProtocolError",
    "State",
    "WireModel",
    "command_of",
    "decode_entries",
    "decode_entry",
    "encode",
    "event_of",
]
'''
