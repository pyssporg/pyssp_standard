from __future__ import annotations
from collections.abc import Mapping
from typing import Iterable

from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1DocumentMetadata
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1ParameterBinding
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter, Ssp1ParameterSet


def extend_inline_parameter_binding(
    bindings: list[Ssd1ParameterBinding],
    parameters: Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object]],
    *,
    default_name: str,
    owner_name: str,
    binding_name: str | None = None,
    prefix: str | None = None,
    version: str = "1.0",
    metadata: Ssp1DocumentMetadata | None = None,
) -> None:
    
    parameter_set = get_or_create_inlined_parameter_set(bindings, default_name, binding_name, prefix, version, metadata)

    parameter_set.extend_parameters(parameters)


def get_or_create_inlined_parameter_set(bindings: list[Ssd1ParameterBinding], binding_name: str = None, prefix: str = None, version: str = "1.0", metadata: Ssp1DocumentMetadata | None = None,) -> Ssp1ParameterSet:
    binding = next(
        (
            existing
            for existing in bindings
            if existing.parameter_set is not None and existing.source is None
        ),
        None,
    )
    if binding is None:
        parameter_set = Ssp1ParameterSet(
            name=binding_name or "Bindings",
            version=version,
            metadata=metadata or Ssp1DocumentMetadata(),
        )
        binding = Ssd1ParameterBinding(prefix=prefix, parameter_set=parameter_set)
        bindings.append(binding)

    return binding.parameter_set



