"""Loads protocol/schema into one bundle of definitions and messages that every emitter walks."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# One generated module per schema file, in dependency order: a module only refers to earlier ones.
MODULES = (
    "defs",
    "metrics",
    "room",
    "state",
    "verbs",
    "envelope",
    "events",
    "commands",
    "rest",
)

MISSING: Any = object()


@dataclass(frozen=True)
class Ref:
    """A definition's address: the module it is generated into and its name there."""

    module: str
    name: str


@dataclass
class Shape:
    """One type expression: a scalar, a list of shapes, a reference, an inline enum or a const."""

    kind: str
    nullable: bool = False
    items: Shape | None = None
    ref: Ref | None = None
    values: tuple[str, ...] = ()
    const: str | None = None


@dataclass
class Property:
    """One field of an object definition."""

    name: str
    shape: Shape
    required: bool
    description: str
    default: Any = MISSING
    unit: str | None = None


@dataclass
class Definition:
    """One named shape: an object with properties, a named enum, or a discriminated union."""

    ref: Ref
    description: str
    kind: str
    properties: list[Property] = field(default_factory=list)
    values: tuple[str, ...] = ()
    members: list[Ref] = field(default_factory=list)
    discriminator: str | None = None
    measured_by: str | None = None


@dataclass
class Message:
    """One event or command: its wire type and the definition its data is."""

    kind: str
    type: str
    root: Ref
    description: str
    scope: str
    ephemeral: bool = False
    terminal: bool = False
    produces: tuple[str, ...] = ()


@dataclass
class Bundle:
    """Everything the schema says, resolved, for the emitters."""

    definitions: dict[Ref, Definition] = field(default_factory=dict)
    messages: list[Message] = field(default_factory=list)

    def module(self, name: str) -> list[Definition]:
        """The module's definitions, dependencies first, so a reader and a compiler meet each once."""
        ordered: list[Definition] = []
        seen: set[Ref] = set()

        def visit(definition: Definition) -> None:
            if definition.ref in seen:
                return
            seen.add(definition.ref)
            for dependency in _local_dependencies(definition):
                visit(self.definitions[dependency])
            ordered.append(definition)

        for definition in self.definitions.values():
            if definition.ref.module == name:
                visit(definition)
        return ordered

    def imports_of(self, name: str) -> dict[str, list[str]]:
        """Which names the module needs from earlier modules, grouped by module."""
        needed: dict[str, set[str]] = {}
        for definition in self.module(name):
            for dependency in _dependencies(definition):
                if dependency.module != name:
                    needed.setdefault(dependency.module, set()).add(dependency.name)
        for message in self.messages:
            if f"{message.kind}s" == name and message.root.module != name:
                needed.setdefault(message.root.module, set()).add(message.root.name)
        return {module: _in_import_order(names) for module, names in sorted(needed.items())}

    def roots_of(self, kind: str) -> dict[str, list[str]]:
        """Which root models a registry needs, by module, for the messages of one kind."""
        needed: dict[str, set[str]] = {}
        for message in self.messages_of(kind):
            needed.setdefault(message.root.module, set()).add(message.root.name)
        return {module: _in_import_order(names) for module, names in sorted(needed.items())}

    def messages_of(self, kind: str) -> list[Message]:
        return sorted((m for m in self.messages if m.kind == kind), key=lambda m: m.type)

    def terminal_event(self) -> str:
        """The one event that ends a call: after it nothing more is true, and the log seals."""
        marked = [message.type for message in self.messages_of("event") if message.terminal]
        if len(marked) != 1:
            raise ValueError(f"exactly one event is terminal, not {marked}")
        return marked[0]


def load(schema_dir: Path) -> Bundle:
    """Read every schema file under the directory and resolve every $ref."""
    bundle = Bundle()
    schema_dir = schema_dir.resolve()
    for path in sorted(schema_dir.glob("*.json")) + sorted(schema_dir.glob("*/*.json")):
        _load_file(bundle, schema_dir, path)
    _refuse_a_name_in_two_modules(bundle)
    return bundle


# Both languages export every module from one index, so one name in two modules is ambiguous there
# however unambiguous it was in the schema. The generator says so instead of emitting it.
def _refuse_a_name_in_two_modules(bundle: Bundle) -> None:
    modules_of: dict[str, list[str]] = {}
    for ref in bundle.definitions:
        modules_of.setdefault(ref.name, []).append(ref.module)
    for name, modules in sorted(modules_of.items()):
        if len(modules) > 1:
            raise ValueError(f"{name} is defined in {sorted(modules)}: a name lives in one module")


def _load_file(bundle: Bundle, schema_dir: Path, path: Path) -> None:
    document = json.loads(path.read_text())
    module = _module_of(schema_dir, path)
    for name, raw in document.get("$defs", {}).items():
        ref = Ref(module, name)
        if ref in bundle.definitions:
            raise ValueError(f"{path}: {name} is already defined in module {module}")
        bundle.definitions[ref] = _definition(ref, raw, path)
    marker = document.get("x-pinecall")
    if marker is not None:
        bundle.messages.append(
            Message(
                kind=marker["kind"],
                type=marker["type"],
                root=_resolve(document["$ref"], path, schema_dir),
                description=document["description"],
                scope=marker["scope"],
                ephemeral=marker.get("ephemeral", False),
                terminal=marker.get("terminal", False),
                produces=tuple(marker.get("produces", ())),
            )
        )


def _module_of(schema_dir: Path, path: Path) -> str:
    relative = path.relative_to(schema_dir)
    return relative.parts[0] if len(relative.parts) > 1 else path.stem


def _definition(ref: Ref, raw: dict[str, Any], path: Path) -> Definition:
    schema_dir = _schema_dir_of(path)
    description = raw.get("description", "")
    if "oneOf" in raw:
        members = [_resolve(member["$ref"], path, schema_dir) for member in raw["oneOf"]]
        discriminator = raw["discriminator"]["propertyName"]
        return Definition(ref, description, "union", members=members, discriminator=discriminator)
    if "enum" in raw:
        return Definition(ref, description, "enum", values=tuple(raw["enum"]))
    if raw.get("additionalProperties") is not False:
        raise ValueError(f"{path}: {ref.name} must close with additionalProperties: false")
    required = set(raw.get("required", ()))
    properties = [
        Property(
            name=name,
            shape=_shape(prop, path, schema_dir),
            required=name in required,
            description=prop.get("description", ""),
            default=prop.get("default", MISSING),
            unit=prop.get("x-unit"),
        )
        for name, prop in raw.get("properties", {}).items()
    ]
    for prop, raw_prop in zip(properties, raw.get("properties", {}).values(), strict=True):
        if not prop.description and "$ref" not in raw_prop and "anyOf" not in raw_prop:
            raise ValueError(f"{path}: {ref.name}.{prop.name} has no description")
    return Definition(
        ref, description, "object", properties=properties, measured_by=raw.get("x-measured-by")
    )


def _shape(raw: dict[str, Any], path: Path, schema_dir: Path) -> Shape:
    if "$ref" in raw:
        return Shape("ref", ref=_resolve(raw["$ref"], path, schema_dir))
    if "anyOf" in raw:
        return _nullable_ref(raw["anyOf"], path, schema_dir)
    kinds = raw.get("type")
    if kinds is None:
        return Shape("any")
    if isinstance(kinds, list):
        nullable = "null" in kinds
        kinds = [kind for kind in kinds if kind != "null"]
        shape = _shape({**raw, "type": kinds[0]}, path, schema_dir)
        shape.nullable = nullable
        return shape
    if "const" in raw:
        return Shape("const", const=raw["const"])
    if "enum" in raw:
        return Shape("enum", values=tuple(raw["enum"]))
    if kinds == "array":
        return Shape("list", items=_shape(raw["items"], path, schema_dir))
    if kinds == "object":
        if raw.get("additionalProperties") is not True:
            raise ValueError(f"{path}: inline objects are not allowed; name it in $defs")
        return Shape("json")
    scalar = {"string": "str", "number": "float", "integer": "int", "boolean": "bool"}
    return Shape(scalar[kinds])


# The one anyOf we allow: a reference or null. It is how a nested object says "optional here".
def _nullable_ref(options: list[dict[str, Any]], path: Path, schema_dir: Path) -> Shape:
    refs = [option for option in options if "$ref" in option]
    nulls = [option for option in options if option.get("type") == "null"]
    if len(refs) != 1 or len(nulls) != 1 or len(options) != 2:
        raise ValueError(f"{path}: anyOf must be exactly [$ref, null]")
    return Shape("ref", nullable=True, ref=_resolve(refs[0]["$ref"], path, schema_dir))


def _resolve(reference: str, path: Path, schema_dir: Path) -> Ref:
    file_part, _, pointer = reference.partition("#")
    if not pointer.startswith("/$defs/"):
        raise ValueError(f"{path}: {reference} must point into $defs")
    target = path if not file_part else (path.parent / file_part).resolve()
    return Ref(_module_of(schema_dir, target), pointer.removeprefix("/$defs/"))


def _schema_dir_of(path: Path) -> Path:
    return path.parent.parent if path.parent.name in ("events", "commands") else path.parent


def _dependencies(definition: Definition) -> list[Ref]:
    found: list[Ref] = list(definition.members)
    for prop in definition.properties:
        shape: Shape | None = prop.shape
        while shape is not None:
            if shape.ref is not None:
                found.append(shape.ref)
            shape = shape.items
    return found


# Both languages lint their own generated files, and both linters sort imports case-insensitively:
# `EndedBy` comes before `EndReason` for them and after it for Python's `sorted`. The generator
# emits the order the linters want, so a name is never renamed to please a sort.
def _in_import_order(names: set[str]) -> list[str]:
    """The names of one import, in the order isort and eslint both put them."""
    return sorted(names, key=lambda name: (name.lower(), name))


def _local_dependencies(definition: Definition) -> list[Ref]:
    return [ref for ref in _dependencies(definition) if ref.module == definition.ref.module]
