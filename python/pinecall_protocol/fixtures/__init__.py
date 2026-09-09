"""The golden call log and the state it reduces to: every consumer proves the same thing."""

from importlib.resources import files
from pathlib import Path

GOLDEN_LOG = Path(str(files(__package__) / "call-log-golden.json"))
GOLDEN_STATE = Path(str(files(__package__) / "call-log-golden.state.json"))
