"""The golden log is the contract: every entry decodes to the model its type names."""


import pytest

from pinecall_protocol import EPHEMERAL_EVENTS, EVENTS, decode_entries, event_of
from pinecall_protocol.envelope import Entry
from tests.paths import FIXTURES

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def golden() -> list[Entry]:
    return decode_entries((FIXTURES / "call-log-golden.json").read_text())


def test_every_golden_entry_decodes_to_the_model_its_type_names(golden: list[Entry]) -> None:
    for entry in golden:
        model = event_of(entry)
        assert type(model) is EVENTS[entry.type]


def test_seqs_climb_and_the_only_hole_is_the_one_the_gap_declares(golden: list[Entry]) -> None:
    gaps = [event_of(entry) for entry in golden if entry.type == "log.gap"]
    declared = {seq for gap in gaps for seq in range(gap.from_seq, gap.to_seq + 1)}  # type: ignore[attr-defined]
    seen = [entry.seq for entry in golden if entry.type not in ("log.gap", "log.caught_up")]
    assert seen == sorted(seen)
    assert set(range(1, seen[-1] + 1)) - set(seen) == declared


def test_the_fixture_exercises_one_of_each_thing_the_card_asked_for(golden: list[Entry]) -> None:
    types = [entry.type for entry in golden]
    assert types.count("turn.user") == 5 and types.count("turn.agent") == 7
    for required in (
        "room.opened",
        "participant.joined",
        "participant.speaking",
        "participant.left",
        "event.received",
        "room.sent",
        "tool.call",
        "tool.result",
        "state.changed",
        "confirm.request",
        "confirm.granted",
        "memory.ops",
        "log.gap",
        "call.summary",
        "metrics.llm",
        "metrics.stt",
        "metrics.tts",
        "metrics.vad",
        "metrics.eou",
        "metrics.eot",
        "metrics.interruption",
    ):
        assert required in types, required


def test_ephemeral_entries_are_the_kinds_the_schema_says_may_be_dropped(
    golden: list[Entry],
) -> None:
    for entry in golden:
        if entry.ephemeral:
            assert entry.type in EPHEMERAL_EVENTS or entry.type == "user.transcript"
        if entry.type in ("log.gap", "log.caught_up", "metrics.vad", "pong"):
            assert entry.ephemeral
        if entry.type in ("participant.speaking", "room.sent"):
            assert entry.ephemeral


def test_the_outside_fact_moves_the_state_and_the_agent_speaks_to_it(golden: list[Entry]) -> None:
    received = next(entry for entry in golden if entry.type == "event.received")
    after = [entry for entry in golden if entry.seq > received.seq]
    moved = next(entry for entry in after if entry.type == "state.changed")
    assert moved.data["cause"] == {"kind": "event", "name": "slot.released", "seq": received.seq}
    spoke = next(entry for entry in after if entry.type in ("turn.agent", "turn.user"))
    assert spoke.type == "turn.agent" and "diez y cuarto" in spoke.data["text"]


def test_the_sip_caller_joins_with_the_trunk_facts_the_room_reported(golden: list[Entry]) -> None:
    joined = [entry.data for entry in golden if entry.type == "participant.joined"]
    caller = next(who for who in joined if who["kind"] == "caller")
    assert caller["attributes"]["sip.phoneNumber"] == caller["identity"].removeprefix("sip_")
    assert {"sip.callID", "sip.trunkPhoneNumber", "sip.ruleID"} <= set(caller["attributes"])
