from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExternalReference:
    source: str | None = None

    @property
    def is_external(self) -> bool:
        return self.source is not None


# Shared value coercion helpers for compact SSP1 model convenience APIs.


def infer_parameter_type_name(value: object) -> str:
    if isinstance(value, bool):
        return "Boolean"
    if isinstance(value, int):
        return "Integer"
    if isinstance(value, float):
        return "Real"
    return "String"


def stringify_attribute_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def merge_value_attribute(attributes: dict[str, str], value: object) -> dict[str, str]:
    """Return attributes with a stringified SSP value when one is provided.

    Example:
        merge_value_attribute({"unit": "kg"}, 2.5)
        # {"unit": "kg", "value": "2.5"}
    """
    merged = dict(attributes)
    if value is not None:
        merged["value"] = stringify_attribute_value(value)
    return merged
