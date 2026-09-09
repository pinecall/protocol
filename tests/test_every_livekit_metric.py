"""The schema carries every field livekit-agents measures; the list is read from the library."""

import dataclasses
import json
import re
import typing
from typing import Any

import pytest

livekit_metrics = pytest.importorskip(
    "livekit.agents.metrics",
    reason="livekit-agents is the runtime extra: `uv sync --extra runtime` to run this test",
)
from livekit.agents.llm import chat_context  # noqa: E402
from livekit.agents.metrics import base, usage  # noqa: E402

from pinecall_protocol import EVENTS  # noqa: E402
from tests.paths import DOCS, SCHEMA  # noqa: E402

pytestmark = pytest.mark.unit

DEFS: dict[str, Any] = json.loads((SCHEMA / "metrics.json").read_text())["$defs"]


def schema_fields(name: str) -> dict[str, bool]:
    """The schema's fields for one definition, each with whether it is required."""
    definition = DEFS[name]
    required = set(definition.get("required", ()))
    return {field: field in required for field in definition["properties"]}


# The one field the schema requires and the library defaults: the type tag. livekit fills it in by
# default and dumps it every time, and both unions (ModelUsage, the event registry) are told apart
# by it, so on the wire it is never absent.
def library_fields(model: type[Any]) -> dict[str, bool]:
    """A pydantic model's fields, each with whether the library insists on it."""
    return {
        name: field.is_required() or name == "type" for name, field in model.model_fields.items()
    }


def nested_models(model: type[Any]) -> dict[str, type[Any]]:
    """The models a model nests, under the schema name RealtimeModelMetrics.X gets: RealtimeX."""
    found: dict[str, type[Any]] = {}
    prefix = model.__name__.removesuffix("ModelMetrics")
    for field in model.model_fields.values():
        for candidate in typing.get_args(field.annotation) or (field.annotation,):
            if isinstance(candidate, type) and candidate.__qualname__.startswith(
                model.__name__ + "."
            ):
                found[prefix + candidate.__name__] = candidate
    return found


def every_block() -> dict[str, type[Any]]:
    blocks: dict[str, type[Any]] = {"Metadata": base.Metadata}
    for block in typing.get_args(base.AgentMetrics):
        blocks[block.__name__] = block
        blocks.update(nested_models(block))
    return blocks


@pytest.mark.parametrize(("name", "model"), sorted(every_block().items()))
def test_a_metrics_block_has_every_field_the_library_declares_and_no_other(
    name: str, model: type[Any]
) -> None:
    assert schema_fields(name) == library_fields(model), name


@pytest.mark.parametrize(
    ("name", "model"), [(m.__name__, m) for m in typing.get_args(usage.ModelUsage)]
)
def test_a_usage_row_has_every_field_the_library_sums(name: str, model: type[Any]) -> None:
    assert schema_fields(name) == library_fields(model), name


def test_the_session_usage_is_a_list_of_those_rows_and_nothing_else() -> None:
    assert [field.name for field in dataclasses.fields(usage.AgentSessionUsage)] == ["model_usage"]
    members = {member["$ref"].rsplit("/", 1)[1] for member in DEFS["ModelUsage"]["oneOf"]}
    assert members == {m.__name__ for m in typing.get_args(usage.ModelUsage)}


def test_the_turn_metrics_cover_every_key_of_the_chat_message_report_by_role() -> None:
    report = set(typing.get_type_hints(chat_context.MetricsReport))
    user = set(schema_fields("UserTurnMetrics"))
    agent = set(schema_fields("AgentTurnMetrics"))
    assert user | agent == report
    assert all(not required for required in schema_fields("UserTurnMetrics").values())
    assert all(not required for required in schema_fields("AgentTurnMetrics").values())
    assert set(schema_fields("TurnMetadata")) == set(
        typing.get_type_hints(chat_context.MetricsMetadata)
    )


def test_every_block_the_session_emits_has_its_own_event() -> None:
    for block in typing.get_args(base.AgentMetrics):
        tag = block.model_fields["type"].default
        assert EVENTS[f"metrics.{tag.split('_')[0]}"] is not None, tag


# ── the decision doc, held to the same library ──────────────────────────────────

DECISION_DOC = DOCS / "livekit-metrics.md"
TABLE_HEADER = "| class | where | fields |"


def documented_classes() -> list[tuple[str, list[str]]]:
    """Every class the metrics table names, with its fields, in the order the doc lists them."""
    rows: list[tuple[str, list[str]]] = []
    lines = DECISION_DOC.read_text().splitlines()
    start = lines.index(TABLE_HEADER) + 2  # the header, then its |---|---|---| rule
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        name, _where, fields = (cell.strip() for cell in line.strip("|").split("|"))
        rows.append((name.strip("`"), re.findall(r"`([^`]+)`", fields)))
    return rows


def library_classes() -> list[tuple[str, list[str]]]:
    """The same list, read off livekit-agents: the blocks, their nested types, the usage rows."""
    rows: list[tuple[str, list[str]]] = [("Metadata", list(base.Metadata.model_fields))]
    for block in typing.get_args(base.AgentMetrics):
        rows.append((block.__name__, list(block.model_fields)))
        rows += [
            (nested.__qualname__, list(nested.model_fields))
            for nested in nested_models(block).values()
        ]
    rows += [(row.__name__, list(row.model_fields)) for row in typing.get_args(usage.ModelUsage)]
    rows.append(("MetricsReport", list(typing.get_type_hints(chat_context.MetricsReport))))
    rows.append(("MetricsMetadata", list(typing.get_type_hints(chat_context.MetricsMetadata))))
    return rows


def test_the_decision_doc_names_every_metrics_class_and_field_the_library_declares() -> None:
    """The doc is the contract the bridge is built against, so the library pins it."""
    assert documented_classes() == library_classes()
