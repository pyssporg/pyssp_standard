from __future__ import annotations

from collections.abc import Iterable, Mapping

from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1DocumentMetadata
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1ParameterBinding
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter, Ssp1ParameterSet


def extend_inline_parameter_binding(
    bindings: list[Ssd1ParameterBinding],
    parameters: Mapping[str, object] | Iterable[Ssp1Parameter | tuple[str, object] | Mapping[str, object]],
    *,
    default_name: str,
    owner_name: str,
    binding_name: str | None = None,
    prefix: str | None = None,
    version: str = "1.0",
    metadata: Ssp1DocumentMetadata | None = None,
) -> Ssd1ParameterBinding:

    # TODO: Refactor parameter_set creation/extraction
    # Then inline the two remaining functions for clarity of what is done
    binding = _find_inline_parameter_binding(bindings)
    if binding is None:
        parameter_set = Ssp1ParameterSet(
            name=binding_name or default_name,
            version=version,
            metadata=metadata or Ssp1DocumentMetadata(),
        )
        binding = Ssd1ParameterBinding(prefix=prefix, parameter_set=parameter_set)
        bindings.append(binding)
    else:
        parameter_set = binding.parameter_set
        if parameter_set is None:
            raise RuntimeError(f"Inline parameter binding for {owner_name} has no parameter set")

        if binding_name is not None:
            parameter_set.name = binding_name
        if prefix is not None:
            binding.prefix = prefix
        if metadata is not None:
            parameter_set.metadata = metadata
        parameter_set.version = version

    parameter_set.extend_parameters(parameters)
    return binding

# TODO: Inline
def _find_inline_parameter_binding(
    bindings: list[Ssd1ParameterBinding],
) -> Ssd1ParameterBinding | None:
    return next(
        (
            existing
            for existing in bindings
            if existing.parameter_set is not None and existing.source is None
        ),
        None,
    )
