"""A tuple survives the generator into all three languages: a transcript line is [who, what]."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pinecall_protocol.rest import ExtractionCases, ExtractionGolden


def test_a_line_of_a_transcript_keeps_both_speakers() -> None:
    golden = ExtractionGolden(
        name="la alergia", said=[("caller", "Soy alérgica"), ("agent", "Anotado")]
    )
    assert golden.said[0] == ("caller", "Soy alérgica")


def test_a_case_with_no_expectations_still_carries_the_model_and_not_a_bare_dict() -> None:
    golden = ExtractionGolden(name="solo planta", said=[("caller", "hola")])
    assert golden.expect.writes == []
    assert golden.expect.never_says == []


def test_a_line_of_one_thing_is_refused() -> None:
    with pytest.raises(ValidationError):
        ExtractionGolden(name="media línea", said=[("caller",)])  # type: ignore[list-item]


def test_a_transcript_survives_the_wire_as_pairs_and_not_as_one_flat_list() -> None:
    said = [("caller", "¿Cuánto cuesta?"), ("agent", "Cuarenta euros.")]
    cases = ExtractionCases(cases=[ExtractionGolden(name="tarifas", said=said)])
    written = cases.model_dump(mode="json")
    as_json = [["caller", "¿Cuánto cuesta?"], ["agent", "Cuarenta euros."]]
    assert written["cases"][0]["said"] == as_json
    assert ExtractionCases.model_validate(written).cases[0].said == said
