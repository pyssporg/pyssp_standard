from .generated.ssv2_generated_types import (
    GeneratedSsv2Parameter,
    GeneratedSsv2ParameterSet,
    GeneratedSsv2Value,
)
from .ssv_model import Parameter, ParameterSet


def to_domain(gen: GeneratedSsv2ParameterSet) -> ParameterSet:
    return ParameterSet(
        name=gen.name,
        version=gen.version,
        parameters=[
            Parameter(name=p.name, type_name=p.value.type_name, value=p.value.value)
            for p in gen.parameters
        ],
    )


def to_generated(domain: ParameterSet) -> GeneratedSsv2ParameterSet:
    return GeneratedSsv2ParameterSet(
        name=domain.name,
        version=domain.version,
        parameters=[
            GeneratedSsv2Parameter(name=p.name, value=GeneratedSsv2Value(p.type_name, p.value))
            for p in domain.parameters
        ],
    )
