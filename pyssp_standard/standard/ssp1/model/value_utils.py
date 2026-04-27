from __future__ import annotations


# TODO: move all to common

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
