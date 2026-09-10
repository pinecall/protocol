"""Emits the zod schemas and their inferred types: one module per schema file, registries, the codec."""

from __future__ import annotations

import textwrap
from pathlib import Path

from schema import MODULES, Bundle, Definition, Message, Property, Shape, dependencies

HEADLINES = {
    "defs": "the shapes shared across the wire",
    "metrics": "every livekit-agents 1.8 metric, verbatim",
    "room": "the room's facts and the outside world's",
    "state": "what a log reduces to",
    "verbs": "the supervise verbs",
    "envelope": "the log entry and the command frame",
    "events": "one schema per event",
    "commands": "one schema per command",
    "rest": "the envelopes the read doors answer in",
}


def emit(bundle: Bundle, out_dir: Path) -> list[Path]:
    """Write every module and return the paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for module in MODULES:
        written.append(_write(out_dir / f"{module}.ts", _module_source(bundle, module)))
    written.append(_write(out_dir / "registry.ts", _registry_module_source(bundle)))
    written.append(_write(out_dir / "units.ts", _units_module_source(bundle)))
    written.append(_write(out_dir / "codec.ts", _codec_source(bundle)))
    written.append(_write(out_dir / "index.ts", INDEX_SOURCE))
    return written


def _write(path: Path, source: str) -> Path:
    path.write_text(source)
    return path


def _module_source(bundle: Bundle, module: str) -> str:
    source_file = f"{module}/" if module in ("events", "commands") else f"{module}.json"
    header = f"// Generated from schema/{source_file}: {HEADLINES[module]}. Never edited by hand."
    imports = ['import { z } from "zod";']
    for other, names in _field_imports(bundle, module).items():
        imports.append(_import_line(names, other))
    blocks = [_definition_source(definition) for definition in bundle.module(module)]
    return header + "\n\n" + "\n".join(imports) + "\n\n" + "\n\n".join(blocks) + "\n"


def _registry_module_source(bundle: Bundle) -> str:
    header = "// Generated from schema: every event and command by its wire type. Never edited by hand."
    needed: dict[str, set[str]] = {}
    for kind in ("event", "command"):
        for other, names in bundle.roots_of(kind).items():
            needed.setdefault(other, set()).update(names)
    imports = [_import_line(sorted(names), other) for other, names in sorted(needed.items())]
    events = bundle.messages_of("event")
    commands = bundle.messages_of("command")
    blocks = [
        _registry_source("EVENT_SCHEMAS", "EventType", events),
        _ephemeral_source(events),
        _terminal_source(bundle),
        _registry_source("COMMAND_SCHEMAS", "CommandType", commands),
        _produces_source(commands),
    ]
    return header + "\n\n" + "\n".join(imports) + "\n\n" + "\n\n".join(blocks) + "\n"


# The schema measures a field with `x-unit` and the models cannot carry it: a zod schema describes
# a shape, not what the number means. So the units leave as their own table, by field name — every
# definition that names a field names the same unit for it, and a disagreement stops generation
# rather than picking one. It is what lets a reader of a metrics block see "s" beside a duration.
def _units_module_source(bundle: Bundle) -> str:
    header = "// Generated from schema: the unit each measured field is written in. Never edited by hand."
    units = _units(bundle)
    rows = "\n".join(f'  {_key(field)}: "{unit}",' for field, unit in sorted(units.items()))
    return (
        f"{header}\n\n"
        "/** What one field is measured in, by the name the wire uses: `UNITS.ttft` is `\"s\"`. */\n"
        f"export const UNITS: Readonly<Record<string, string>> = {{\n{rows}\n}};\n"
    )


def _units(bundle: Bundle) -> dict[str, str]:
    """Every field the schema gives a unit, by name. Two units for one name is a schema bug."""
    found: dict[str, str] = {}
    for definition in bundle.definitions.values():
        for prop in definition.properties:
            if prop.unit is None:
                continue
            said = found.get(prop.name)
            if said is not None and said != prop.unit:
                raise ValueError(
                    f"{definition.ref.name}.{prop.name}: unit {prop.unit!r} "
                    f"disagrees with {said!r} declared elsewhere"
                )
            found[prop.name] = prop.unit
    return found


def _key(field: str) -> str:
    return field if field.isidentifier() else f'"{field}"'


# A message whose data is a shape from another module needs no import in the models module.
def _field_imports(bundle: Bundle, module: str) -> dict[str, list[str]]:
    used = {ref.name for definition in bundle.module(module) for ref in dependencies(definition)}
    return {
        other: [name for name in names if name in used]
        for other, names in bundle.imports_of(module).items()
        if any(name in used for name in names)
    }


def _import_line(names: list[str], other: str) -> str:
    schemas = [f"{name}Schema" for name in names]
    if len(", ".join(schemas)) < 70:
        return f'import {{ {", ".join(schemas)} }} from "./{other}.js";'
    listed = "\n".join(f"  {schema}," for schema in schemas)
    return f'import {{\n{listed}\n}} from "./{other}.js";'


def _definition_source(definition: Definition) -> str:
    name = definition.ref.name
    comment = _doc_comment(definition.description)
    if definition.kind == "enum":
        schema = f"z.enum([{_strings(definition.values)}])"
    elif definition.kind == "union":
        members = ", ".join(f"{member.name}Schema" for member in definition.members)
        schema = f'z.discriminatedUnion("{definition.discriminator}", [{members}])'
    elif definition.kind == "map":
        assert definition.value is not None
        schema = f"z.record(z.string(), {_schema(definition.value)})"
    elif not definition.properties:
        schema = "z.strictObject({})"
    else:
        fields = "\n".join(f"  {_field_source(prop)}," for prop in definition.properties)
        schema = f"z.strictObject({{\n{fields}\n}})"
    return (
        f"{comment}export const {name}Schema = {schema};\n"
        f"export type {name} = z.infer<typeof {name}Schema>;"
    )


# A field the schema does not require is `T | None = None` in Python, which accepts a null as
# readily as an absence — and pydantic writes that null back out whenever a producer set it
# explicitly. `.nullish()` is zod's word for the same two, so what one language may write the other
# may always read. `.optional()` alone refused a `"email": null` a real gateway had just sent.
def _field_source(prop: Property) -> str:
    key = prop.name if prop.name.isidentifier() else f'"{prop.name}"'
    schema = _schema(prop.shape)
    if prop.pattern is not None:
        schema += f".regex(/{prop.pattern}/)"
    if not prop.required:
        schema += ".nullish()"
    return f"{key}: {schema}"


def _schema(shape: Shape) -> str:
    rendered = _bare_schema(shape)
    return f"{rendered}.nullable()" if shape.nullable else rendered


def _bare_schema(shape: Shape) -> str:
    match shape.kind:
        case "str":
            return "z.string()"
        case "float":
            return "z.number()"
        case "int":
            return "z.int()"
        case "bool":
            return "z.boolean()"
        case "any":
            return "z.unknown()"
        case "json":
            return "z.record(z.string(), z.unknown())"
        case "list":
            assert shape.items is not None
            return f"z.array({_schema(shape.items)})"
        case "map":
            assert shape.items is not None
            return f"z.record(z.string(), {_schema(shape.items)})"
        case "tuple":
            return f"z.tuple([{', '.join(_schema(one) for one in shape.members)}])"
        case "ref":
            assert shape.ref is not None
            return f"{shape.ref.name}Schema"
        case "enum":
            return f"z.enum([{_strings(shape.values)}])"
        case "const":
            return f'z.literal("{shape.const}")'
    raise ValueError(f"unknown shape kind {shape.kind}")


def _strings(values: tuple[str, ...]) -> str:
    return ", ".join(f'"{value}"' for value in values)


def _registry_source(name: str, alias: str, messages: list[Message]) -> str:
    rows = "\n".join(f'  "{message.type}": {message.root.name}Schema,' for message in messages)
    return (
        f"/** Every {alias.removesuffix('Type').lower()} by its wire type; the codec looks the schema up here. */\n"
        f"export const {name} = {{\n{rows}\n}} as const;\n"
        f"export type {alias} = keyof typeof {name};"
    )


def _ephemeral_source(messages: list[Message]) -> str:
    names = ", ".join(f'"{message.type}"' for message in messages if message.ephemeral)
    return (
        "/** Events a store may drop and a slow reader may miss: the entry's ephemeral flag defaults to this. */\n"
        f"export const EPHEMERAL_EVENTS: ReadonlySet<EventType> = new Set<EventType>([{names}]);"
    )


def _terminal_source(bundle: Bundle) -> str:
    return (
        "/** The one event that ends a call: after it nothing more is true and the log is sealed. */\n"
        f'export const TERMINAL_EVENT: EventType = "{bundle.terminal_event()}";'
    )


def _produces_source(messages: list[Message]) -> str:
    rows = "\n".join(
        f'  "{message.type}": [{_strings(message.produces)}],' for message in messages
    )
    return (
        "/** Which events a command lands in the log as, so a caller knows what to wait for. */\n"
        f"export const PRODUCES: Readonly<Record<CommandType, readonly string[]>> = {{\n{rows}\n}};"
    )


def _doc_comment(text: str) -> str:
    if not text:
        return ""
    lines = textwrap.wrap(text, width=96)
    if len(lines) == 1:
        return f"/** {lines[0]} */\n"
    return "/**\n" + "\n".join(f" * {line}" for line in lines) + "\n */\n"


# The keys whose values are the app's own JSON, or a map keyed by names the app chose: the codec
# never renames anything under them.
def _codec_source(bundle: Bundle) -> str:
    opaque = sorted(
        {
            prop.name
            for definition in bundle.definitions.values()
            for prop in definition.properties
            if _keyed_by_the_app(bundle, prop.shape)
        }
    )
    quoted = tuple(opaque)
    return CODEC_TEMPLATE.replace("__OPAQUE__", _strings(quoted)).replace(
        "__OPAQUE_TYPE__", " | ".join(f'"{key}"' for key in quoted)
    )


def _keyed_by_the_app(bundle: Bundle, shape: Shape) -> bool:
    if shape.kind in ("json", "any", "map"):
        return True
    return shape.ref is not None and bundle.definitions[shape.ref].kind == "map"


CODEC_TEMPLATE = '''// The wire, decoded and typed. The only file that touches a key name: snake_case on the wire,
// camelCase for whoever wants it. Never edited by hand.

import { z } from "zod";
import { CommandSchema, EntrySchema, type Command, type Entry } from "./envelope.js";
import { COMMAND_SCHEMAS, EVENT_SCHEMAS, type CommandType, type EventType } from "./registry.js";

export class ProtocolError extends Error {
  override readonly name = "ProtocolError";
}

/** The data shape of one event type. */
export type EventData<K extends EventType> = z.infer<(typeof EVENT_SCHEMAS)[K]>;

/** One event, typed by its type: switch on `type` and `data` narrows with it. */
export type Event = { [K in EventType]: { type: K; data: EventData<K> } }[EventType];

/** The data shape of one command type. */
export type CommandData<K extends CommandType> = z.infer<(typeof COMMAND_SCHEMAS)[K]>;

/** One command, typed by its type. */
export type AnyCommand = { [K in CommandType]: { type: K; data: CommandData<K> } }[CommandType];

/** One log line from decoded JSON. A bad shape throws. */
export function decodeEntry(raw: unknown): Entry {
  return EntrySchema.parse(raw);
}

/** A whole log from a JSON array text, in the order it came. */
export function decodeEntries(text: string): Entry[] {
  return z.array(EntrySchema).parse(JSON.parse(text));
}

/** The entry's data as the shape its type names. An unknown type or a bad shape throws. */
export function eventOf(entry: Entry): Event {
  if (!isEventType(entry.type)) {
    throw new ProtocolError(`unknown event type: ${entry.type}`);
  }
  const data: unknown = EVENT_SCHEMAS[entry.type].parse(entry.data);
  return { type: entry.type, data } as Event;
}

/** The command's data as the shape its type names. An unknown type or a bad shape throws. */
export function commandOf(command: Command): AnyCommand {
  if (!isCommandType(command.type)) {
    throw new ProtocolError(`unknown command type: ${command.type}`);
  }
  const data: unknown = COMMAND_SCHEMAS[command.type].parse(command.data);
  return { type: command.type, data } as AnyCommand;
}

export function isEventType(type: string): type is EventType {
  return Object.hasOwn(EVENT_SCHEMAS, type);
}

export function isCommandType(type: string): type is CommandType {
  return Object.hasOwn(COMMAND_SCHEMAS, type);
}

// ── key names ──────────────────────────────────────────────────────────────────

/** "llm_node_ttft" as a type becomes "llmNodeTtft". */
export type CamelCase<S extends string> = S extends `${infer Head}_${infer Tail}`
  ? `${Head}${Capitalize<CamelCase<Tail>>}`
  : S;

/** "llmNodeTtft" as a type becomes "llm_node_ttft". */
export type SnakeCase<S extends string> = S extends `${infer Head}${infer Tail}`
  ? Head extends Lowercase<Head>
    ? `${Head}${SnakeCase<Tail>}`
    : `_${Lowercase<Head>}${SnakeCase<Tail>}`
  : S;

/** A wire shape with every key camelCased, deep, except under the opaque keys. */
export type Camel<T> = T extends readonly (infer Item)[]
  ? Camel<Item>[]
  : T extends object
    ? { [K in keyof T as K extends string ? CamelCase<K> : K]: K extends OpaqueKey ? T[K] : Camel<T[K]> }
    : T;

/** A camelCased shape back to the wire's keys, deep, except under the opaque keys. */
export type Snake<T> = T extends readonly (infer Item)[]
  ? Snake<Item>[]
  : T extends object
    ? { [K in keyof T as K extends string ? SnakeCase<K> : K]: K extends OpaqueKey ? T[K] : Snake<T[K]> }
    : T;

/** The keys whose values belong to the app (its state, a tool's arguments, a map it named): never renamed below them. */
export const OPAQUE_KEYS = new Set<string>([__OPAQUE__]);
export type OpaqueKey = __OPAQUE_TYPE__;

/** Rename every key from snake_case to camelCase, deep. Values are never touched. */
export function toCamel<T>(value: T): Camel<T> {
  return renameKeys(value, camelCase) as Camel<T>;
}

/** Rename every key from camelCase to snake_case, deep. Values are never touched. */
export function toSnake<T>(value: T): Snake<T> {
  return renameKeys(value, snakeCase) as Snake<T>;
}

function renameKeys(value: unknown, rename: (key: string) => string): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => renameKeys(item, rename));
  }
  if (value === null || typeof value !== "object") {
    return value;
  }
  const renamed: Record<string, unknown> = {};
  for (const [key, inner] of Object.entries(value)) {
    renamed[rename(key)] = OPAQUE_KEYS.has(key) ? inner : renameKeys(inner, rename);
  }
  return renamed;
}

function camelCase(key: string): string {
  return key.replace(/_([a-z0-9])/g, (_, letter: string) => letter.toUpperCase());
}

function snakeCase(key: string): string {
  return key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}
'''

INDEX_SOURCE = """// Generated: everything the wire defines, from one door. Never edited by hand.

export * from "./codec.js";
export * from "./commands.js";
export * from "./defs.js";
export * from "./envelope.js";
export * from "./events.js";
export * from "./metrics.js";
export * from "./registry.js";
export * from "./rest.js";
export * from "./units.js";
export * from "./room.js";
export * from "./state.js";
export * from "./verbs.js";
"""
