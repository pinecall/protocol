"""Emits the reference pages into docs/ between the generated markers; the prose stays."""

from __future__ import annotations

from pathlib import Path

from schema import Bundle, Definition, Message, Property, Shape

BEGIN = "<!-- generated:begin -->"
END = "<!-- generated:end -->"

# One page per group of events, so no page outgrows a reader. Every event must land on exactly
# one page: an event with a new prefix fails generation until somebody decides where it goes.
EVENT_PAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("events-call.md", ("call.", "user.", "agent.state", "agent.transcript", "turn.", "metrics.")),
    (
        "events-app.md",
        ("tool.", "state.", "prompt.", "tools.", "confirm.", "memory.", "docs.", "custom"),
    ),
    (
        "events-control.md",
        (
            "supervisor.",
            "attention.",
            "log.",
            "error",
            "pong",
            "agent.registered",
            "agent.configured",
            "agent.detached",
            "agent.draining",
            "credits.",
            "fleet.",
            "callback.",
            "message.",
            "dev.",
        ),
    ),
    ("events-room.md", ("room.", "participant.", "track.", "event.")),
)

# Where a shape's own table lives, by the module it is generated into.
PAGE_OF_MODULE = {"metrics": "metrics.md", "defs": "shapes.md", "envelope": "shapes.md", "state": "state.md"}


def emit(bundle: Bundle, docs_dir: Path) -> list[Path]:
    """Refill the generated region of every reference page. The prose around it is hand-written."""
    pages = {
        "events.md": _events_index(bundle),
        "commands.md": _commands_and_verbs(bundle),
        "metrics.md": _metrics_table(bundle),
        "state.md": _definitions(bundle, "state"),
        "shapes.md": _definitions(bundle, "envelope") + "\n" + _definitions(bundle, "defs"),
    }
    for page, _ in EVENT_PAGES:
        pages[page] = _event_sections(bundle, page)
    written: list[Path] = []
    for name, generated in pages.items():
        _refill(docs_dir / name, generated)
        written.append(docs_dir / name)
    return written


def _refill(path: Path, generated: str) -> None:
    if not path.exists():
        raise ValueError(f"{path}: write the page's prose and markers first; only the tables are generated")
    text = path.read_text()
    if BEGIN not in text or END not in text:
        raise ValueError(f"{path}: the generated markers are missing")
    head, _, tail = text.partition(BEGIN)
    _, _, tail = tail.partition(END)
    path.write_text(f"{head}{BEGIN}\n{generated}\n{END}{tail}")


# ── events ──────────────────────────────────────────────────────────────────────


def _events_index(bundle: Bundle) -> str:
    rows = ["| type | scope | ephemeral | page | what it says |", "|---|---|---|---|---|"]
    for message in bundle.messages_of("event"):
        page = _page_of(message.type)
        rows.append(
            f"| `{message.type}` | {message.scope} | {'yes' if message.ephemeral else 'no'} "
            f"| [{page}]({page}) | {_first_sentence(message.description)} |"
        )
    return "\n".join(rows)


def _event_sections(bundle: Bundle, page: str) -> str:
    sections = [
        _message_section(bundle, message)
        for message in bundle.messages_of("event")
        if _page_of(message.type) == page
    ]
    return "\n".join(sections)


def _page_of(event_type: str) -> str:
    pages = [page for page, prefixes in EVENT_PAGES if event_type.startswith(prefixes)]
    if len(pages) != 1:
        raise ValueError(f"{event_type} must land on exactly one events page, not {pages}")
    return pages[0]


# ── commands and verbs ──────────────────────────────────────────────────────────


def _commands_and_verbs(bundle: Bundle) -> str:
    rows = ["| type | scope | lands as | what it does |", "|---|---|---|---|"]
    for message in bundle.messages_of("command"):
        lands = ", ".join(f"`{t}`" for t in message.produces) or "nothing"
        rows.append(
            f"| `{message.type}` | {message.scope} | {lands} | {_first_sentence(message.description)} |"
        )
    parts = ["\n".join(rows), ""]
    parts += [_message_section(bundle, message) for message in bundle.messages_of("command")]
    parts += ["## Verbs", "", _definitions(bundle, "verbs")]
    return "\n".join(parts)


# ── shared pieces ───────────────────────────────────────────────────────────────


def _message_section(bundle: Bundle, message: Message) -> str:
    definition = bundle.definitions[message.root]
    lines = [f"### `{message.type}`", "", message.description, ""]
    if message.kind == "command" and message.produces:
        lines += [f"Lands in the log as: {', '.join(f'`{t}`' for t in message.produces)}.", ""]
    if definition.ref.module in PAGE_OF_MODULE:
        page = PAGE_OF_MODULE[definition.ref.module]
        lines += [f"Data: `{definition.ref.name}`, in [{page}]({page}).", ""]
    else:
        lines += [_fields_table(bundle, definition), ""]
    return "\n".join(lines)


def _definitions(bundle: Bundle, module: str) -> str:
    return "\n".join(
        _definition_section(bundle, definition) for definition in bundle.module(module)
    )


def _definition_section(bundle: Bundle, definition: Definition) -> str:
    lines = [f"### `{definition.ref.name}`", "", definition.description, ""]
    if definition.kind == "enum":
        lines += ["One of: " + ", ".join(f"`{value}`" for value in definition.values) + ".", ""]
    elif definition.kind == "union":
        members = ", ".join(f"`{member.name}`" for member in definition.members)
        lines += [f"One of {members}, told apart by `{definition.discriminator}`.", ""]
    elif definition.kind == "map":
        assert definition.value is not None
        lines += [f"A map by name: every value is a `{_type_name(definition.value)}`.", ""]
    else:
        lines += [_fields_table(bundle, definition), ""]
    return "\n".join(lines)


def _fields_table(bundle: Bundle, definition: Definition) -> str:
    if not definition.properties:
        return "No fields."
    rows = ["| field | type | required | meaning |", "|---|---|---|---|"]
    for prop in definition.properties:
        required = "yes" if prop.required else "no"
        rows.append(
            f"| `{prop.name}` | `{_type_name(prop.shape)}` | {required} | {_meaning(bundle, prop)} |"
        )
    return "\n".join(rows)


# A field that is a bare reference says nothing of its own; the shape it points at does.
def _meaning(bundle: Bundle, prop: Property) -> str:
    said = prop.description
    if not said and prop.shape.ref is not None:
        said = _first_sentence(bundle.definitions[prop.shape.ref].description)
    if prop.pattern is not None:
        said = f"{said} Matches `{prop.pattern}`."
    return said


def _metrics_table(bundle: Bundle) -> str:
    rows = [
        "| block | field | unit | required | measured by | meaning |",
        "|---|---|---|---|---|---|",
    ]
    for definition in bundle.module("metrics"):
        if definition.kind != "object":
            continue
        for prop in definition.properties:
            required = "yes" if prop.required else "no"
            rows.append(
                f"| `{definition.ref.name}` | `{prop.name}` | {prop.unit} | {required} "
                f"| {definition.measured_by} | {_meaning(bundle, prop)} |"
            )
    return "\n".join(rows)


def _type_name(shape: Shape) -> str:
    match shape.kind:
        case "str":
            base = "string"
        case "float":
            base = "number"
        case "int":
            base = "integer"
        case "bool":
            base = "boolean"
        case "any":
            base = "any"
        case "json":
            base = "object"
        case "list":
            assert shape.items is not None
            base = f"{_type_name(shape.items)}[]"
        case "map":
            assert shape.items is not None
            base = f"map<string, {_type_name(shape.items)}>"
        case "tuple":
            base = f"[{', '.join(_type_name(one) for one in shape.members)}]"
        case "ref":
            assert shape.ref is not None
            base = shape.ref.name
        case "enum":
            base = " | ".join(f'"{value}"' for value in shape.values)
        case "const":
            base = f'"{shape.const}"'
        case _:
            raise ValueError(shape.kind)
    return f"{base} | null" if shape.nullable else base


def _first_sentence(text: str) -> str:
    first, _, _ = text.partition(". ")
    return first if first.endswith(".") else f"{first}."
