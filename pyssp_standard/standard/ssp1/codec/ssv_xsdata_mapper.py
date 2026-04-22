from __future__ import annotations

from pyssp_standard.standard.ssp1.generated.ssv_generated_types import ParameterSet, Tannotations, Tparameter, Tparameters, Tunits, Tunit
from pyssp_standard.standard.ssp1.codec.ssc_xsdata_mapper import Ssp1SscXsdataMapper
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter, Ssp1ParameterSet


class Ssp1SsvXsdataMapper:
    def read_parameterset(self, generated: ParameterSet) -> Ssp1ParameterSet:
        parameters: list[Ssp1Parameter] = []
        for entry in generated.parameters.parameter:
            ptype, attrs = Ssp1SscXsdataMapper.read_parameter_type(entry)
            if ptype is None:
                continue
            parameters.append(Ssp1Parameter(name=entry.name, type_name=ptype, attributes=attrs))
            parameters[-1].id = entry.id
            parameters[-1].description = entry.description
            parameters[-1].annotations = Ssp1SscXsdataMapper.read_annotations(entry.annotations)

        units = [Ssp1SscXsdataMapper.read_unit(entry) for entry in generated.units.unit] if generated.units is not None else []
        metadata = Ssp1SscXsdataMapper.read_document_metadata(generated)

        return Ssp1ParameterSet(
            name=generated.name,
            version=generated.version,
            metadata=metadata,
            parameters=parameters,
            units=units,
        )

    def write_parameterset(self, model: Ssp1ParameterSet) -> ParameterSet:
        units = Tunits(unit=[Ssp1SscXsdataMapper.write_unit(unit) for unit in model.units]) if model.units else None
        return ParameterSet(
            version=model.version,
            name=model.name,
            parameters=Tparameters(
                parameter=[
                    self._write_parameter(param)
                    for param in model.parameters
                ]
            ),
            units=units,
            **Ssp1SscXsdataMapper.write_document_metadata(model.metadata, annotations_cls=Tannotations),
        )

    @staticmethod
    def _write_parameter(param: Ssp1Parameter) -> Tparameter:
        generated = Ssp1SscXsdataMapper.write_parameter_type(param.name, param.type_name, param.attributes)
        generated.id = param.id
        generated.description = param.description
        generated.annotations = Ssp1SscXsdataMapper.write_annotations(param.annotations, annotations_cls=Tannotations)
        return generated
