"""The base every wire model shares: unknown keys are refused; a field builds by name or alias."""

from pydantic import BaseModel, ConfigDict


class WireModel(BaseModel):
    """A shape on the wire. extra=forbid is the schema's additionalProperties: false."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True, validate_by_alias=True)


class ProtocolError(ValueError):
    """A message did not match the protocol: unknown type, bad shape, a seq out of order."""
