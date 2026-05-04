from __future__ import annotations

from collections.abc import Iterable, Mapping

from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1DocumentMetadata
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1ParameterBinding, Ssd1ParameterMappingReference
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter, Ssp1ParameterSet


def extend_inline_parameter_binding(
    bindings: list[Ssd1ParameterBinding],
    parameters: Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object]],
    *,
    default_name: str,
    binding_name: str | None = None,
    prefix: str | None = None,
    version: str = "1.0",
    metadata: Ssp1DocumentMetadata | None = None,
) -> Ssd1ParameterBinding:
    parameter_set = get_or_create_inlined_parameter_set(
        bindings,
        binding_name=binding_name or default_name,
        prefix=prefix,
        version=version,
        metadata=metadata,
    )
    parameter_set.extend_parameters(parameters)
    return next(binding for binding in bindings if binding.parameter_set is parameter_set and binding.source is None)


def get_or_create_inlined_parameter_set(
    bindings: list[Ssd1ParameterBinding],
    binding_name: str | None = None,
    prefix: str | None = None,
    version: str = "1.0",
    metadata: Ssp1DocumentMetadata | None = None,
) -> Ssp1ParameterSet:
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
    elif prefix is not None and binding.prefix is None:
        binding.prefix = prefix

    return binding.parameter_set


def add_external_parameterset(
    bindings: list[Ssd1ParameterBinding],
    source: str,
    *,
    mapping_source: str | None = None,
    prefix: str | None = None,
) -> Ssd1ParameterBinding:
    binding = Ssd1ParameterBinding(
        source=source,
        prefix=prefix,
        parameter_mapping=(
            Ssd1ParameterMappingReference(source=mapping_source) if mapping_source is not None else None
        ),
    )
    bindings.append(binding)
    return binding
