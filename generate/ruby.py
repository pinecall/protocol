"""Emits the Ruby side: the frozen tables a validator walks, the registries, and the RBS types."""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from schema import MISSING, Bundle, Definition, Message, Property, Shape

HEAD = "# frozen_string_literal: true\n"

# Ruby has no compile step to lean on, so the generated half is data: one frozen table per thing a
# reader or a writer must agree about. The types live in RBS beside it, which is where a Ruby
# programme keeps them, and cost nothing at runtime.
HEADLINES = {
    "enums": "Generated from schema/: every closed list on the wire, as a frozen array.",
    "shapes": "Generated from schema/: every named shape, as the table Validate walks.",
    "registry": "Generated from schema/: every event and command by its wire type.",
}


def emit(bundle: Bundle, out_dir: Path, sig_dir: Path) -> list[Path]:
    """Write the generated Ruby and the generated RBS, and return every path written."""
    out_dir.mkdir(parents=True, exist_ok=True)
    sig_dir.mkdir(parents=True, exist_ok=True)
    return [
        _write(out_dir / "enums.rb", _enums_source(bundle)),
        _write(out_dir / "shapes.rb", _shapes_source(bundle)),
        _write(out_dir / "registry.rb", _registry_source(bundle)),
        _write(sig_dir / "generated.rbs", _rbs_source(bundle)),
    ]


def _write(path: Path, source: str) -> Path:
    path.write_text(source)
    return path


# ── the three Ruby modules ──────────────────────────────────────────────────────


def _enums_source(bundle: Bundle) -> str:
    body: list[str] = []
    names: list[str] = []
    for definition in _definitions(bundle, "enum"):
        constant = _constant(definition.ref.name)
        names.append(f'"{definition.ref.name}" => {constant}')
        body.append(_comment(definition.description, 6))
        body.append(f"      {constant} = {_words(definition.values)}.freeze\n")
    body.append("      # Every closed list by the name the schema gave it, for a validator to look up.\n")
    body.append(f"      ALL = {{\n{_rows(names, 8)}\n      }}.freeze\n")
    return _module("Enums", HEADLINES["enums"], "".join(body))


def _shapes_source(bundle: Bundle) -> str:
    rows: list[str] = []
    for definition in _definitions(bundle, "object"):
        fields = ",\n".join(
            f"          {prop.name}: {_descriptor(prop)}" for prop in definition.properties
        )
        opened = f"{{\n{fields}\n        }}" if fields else "{}"
        rows.append(f'        "{definition.ref.name}" => {opened}.freeze')
    unions = [
        f'        "{definition.ref.name}" => {{ on: :{definition.discriminator}, '
        f"members: {_words([member.name for member in definition.members])} }}.freeze"
        for definition in _definitions(bundle, "union")
    ]
    maps = [
        f'        "{definition.ref.name}" => {_value_descriptor(definition.value)}.freeze'
        for definition in _definitions(bundle, "map")
        if definition.value is not None
    ]
    body = (
        "      # Every object the wire carries: its fields, and what each field may be. A shape is\n"
        "      # closed — the schema says additionalProperties: false — so a key nobody declared is\n"
        "      # a message from a newer protocol and the reader is told so by name.\n"
        f"      SHAPES = {{\n{',\n'.join(rows)}\n      }}.freeze\n\n"
        "      # A union is told apart by one field, the way the schema's discriminator says.\n"
        f"      UNIONS = {{\n{',\n'.join(unions)}\n      }}.freeze\n\n"
        "      # A map is keyed by names the app chose; every value is the one shape given here.\n"
        f"      MAPS = {{\n{',\n'.join(maps)}\n      }}.freeze\n"
    )
    return _module("Shapes", HEADLINES["shapes"], body)


def _registry_source(bundle: Bundle) -> str:
    events = bundle.messages_of("event")
    commands = bundle.messages_of("command")
    body = "".join(
        [
            _table("EVENTS", "The shape each event's data is, by the event's wire type.", events),
            "\n",
            _table("COMMANDS", "The shape each command's data is, by the command's wire type.", commands),
            "\n",
            _list("EVENT_TYPES", "Every event this protocol declares, in the schema's own order.", events),
            "\n",
            _list("COMMAND_TYPES", "Every command an app may send.", commands),
            "\n",
            "      # Entries a store may drop and a slow reader may miss without harm: the entry's\n"
            "      # own ephemeral flag defaults to this.\n"
            f"      EPHEMERAL_EVENTS = {_words([m.type for m in events if m.ephemeral])}.to_set.freeze\n\n",
            "      # The one event that ends a call: after it nothing more is true and the log seals.\n"
            f'      TERMINAL_EVENT = "{bundle.terminal_event()}"\n\n',
            "      # Which events a command lands in the log as, so a caller knows what to wait for.\n"
            f"      PRODUCES = {{\n{_rows([f'"{m.type}" => {_words(m.produces)}' for m in commands], 8)}\n      }}.freeze\n",
        ]
    )
    return _module("Registry", HEADLINES["registry"], body, requires=["set"])


def _table(name: str, why: str, messages: list[Message]) -> str:
    rows = _rows([f'"{message.type}" => "{message.root.name}"' for message in messages], 8)
    return f"      # {why}\n      {name} = {{\n{rows}\n      }}.freeze\n"


def _list(name: str, why: str, messages: list[Message]) -> str:
    return f"      # {why}\n      {name} = {_words([m.type for m in messages])}.freeze\n"


# ── one field, as the table describes it ────────────────────────────────────────


def _descriptor(prop: Property) -> str:
    parts = [f"kind: :{_kind(prop.shape)}"]
    parts.extend(_shape_parts(prop.shape))
    if prop.required:
        parts.append("required: true")
    if prop.default is not MISSING:
        parts.append(f"default: {_literal(prop.default)}")
    if prop.pattern is not None:
        parts.append(f"pattern: {_literal(prop.pattern)}")
    return "{ " + ", ".join(parts) + " }"


# What a list holds, or what every value of a map is: a shape with no field around it.
def _value_descriptor(shape: Shape) -> str:
    return "{ " + ", ".join([f"kind: :{_kind(shape)}", *_shape_parts(shape)]) + " }"


def _shape_parts(shape: Shape) -> list[str]:
    parts: list[str] = []
    if shape.nullable:
        parts.append("null: true")
    if shape.ref is not None:
        parts.append(f'ref: "{shape.ref.name}"')
    if shape.values:
        parts.append(f"values: {_words(shape.values)}")
    if shape.const is not None:
        parts.append(f'const: "{shape.const}"')
    if shape.items is not None:
        parts.append(f"items: {_value_descriptor(shape.items)}")
    return parts


# str, float, int, bool, any, json, list, map, ref, enum and const are the eleven kinds the schema
# loader resolves everything to; the validator has one branch per kind and no twelfth.
def _kind(shape: Shape) -> str:
    return shape.kind


# ── RBS: the same shapes, where a Ruby programme keeps its types ────────────────


def _rbs_source(bundle: Bundle) -> str:
    lines = [
        "# Generated from schema/: the wire as RBS record types. `rbs validate` reads this file.",
        "#",
        "# A payload is a Hash with symbol keys, so its type is a record: what Steep checks and what",
        "# `case data in {...}` matches on. Nothing here is loaded at runtime.",
        "module Pinecall",
        "  module Protocol",
        "    module Types",
    ]
    for definition in bundle.definitions.values():
        lines.append(f"      # {_one_line(definition.description)}")
        lines.append(f"      type {_snake(definition.ref.name)} = {_rbs_definition(definition)}")
    lines.extend(["    end", "  end", "end", ""])
    return "\n".join(lines)


def _rbs_definition(definition: Definition) -> str:
    if definition.kind == "enum":
        return " | ".join(f'"{value}"' for value in definition.values)
    if definition.kind == "union":
        return " | ".join(_snake(member.name) for member in definition.members)
    if definition.kind == "map":
        assert definition.value is not None
        return f"Hash[Symbol, {_rbs_type(definition.value)}]"
    if not definition.properties:
        return "{ }"
    fields = ", ".join(_rbs_field(prop) for prop in definition.properties)
    return "{ " + fields + " }"


def _rbs_field(prop: Property) -> str:
    optional = "" if prop.required else "?"
    return f"{optional}{prop.name}: {_rbs_type(prop.shape)}"


def _rbs_type(shape: Shape) -> str:
    rendered = _rbs_bare(shape)
    return f"{rendered}?" if shape.nullable else rendered


def _rbs_bare(shape: Shape) -> str:
    match shape.kind:
        case "str":
            return "String"
        case "float":
            return "Float"
        case "int":
            return "Integer"
        case "bool":
            return "bool"
        case "any":
            return "untyped"
        case "json":
            return "Hash[Symbol, untyped]"
        case "list":
            assert shape.items is not None
            return f"Array[{_rbs_type(shape.items)}]"
        case "map":
            assert shape.items is not None
            return f"Hash[Symbol, {_rbs_type(shape.items)}]"
        case "ref":
            assert shape.ref is not None
            return _snake(shape.ref.name)
        case "enum":
            return " | ".join(f'"{value}"' for value in shape.values)
        case "const":
            return f'"{shape.const}"'
    raise ValueError(f"unknown shape kind {shape.kind}")


# ── the small stuff every emitter needs ─────────────────────────────────────────


def _module(name: str, headline: str, body: str, requires: list[str] | None = None) -> str:
    required = "".join(f'require "{one}"\n' for one in requires or [])
    prelude = f"\n{required}" if required else ""
    return (
        f"{HEAD}\n"
        f"# {headline}\n"
        "# Written by protocol/generate; never edited by hand.\n"
        f"{prelude}\n"
        "module Pinecall\n"
        "  module Protocol\n"
        f"    module {name}\n"
        f"{body}"
        "    end\n"
        "  end\n"
        "end\n"
    )


def _definitions(bundle: Bundle, kind: str) -> list[Definition]:
    return [definition for definition in bundle.definitions.values() if definition.kind == kind]


def _rows(rows: list[str], indent: int) -> str:
    pad = " " * indent
    return ",\n".join(f"{pad}{row}" for row in rows)


def _words(values: "list[str] | tuple[str, ...]") -> str:
    return f"%w[{' '.join(values)}]" if values else "[]"


def _literal(value: object) -> str:
    return json.dumps(value)


def _comment(text: str, indent: int) -> str:
    if not text:
        return ""
    pad = " " * indent
    wrapped = textwrap.wrap(text, width=96 - indent)
    return "".join(f"{pad}# {line}\n" for line in wrapped)


def _one_line(text: str) -> str:
    first, _, _ = text.partition(". ")
    return first if first.endswith(".") or not text else f"{first}."


def _constant(name: str) -> str:
    return _snake(name).upper()


def _snake(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()
