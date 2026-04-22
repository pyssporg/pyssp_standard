from __future__ import annotations

from pyssp_standard.standard.ssp1.codec.ssc_xsdata_mapper import Ssp1SscXsdataMapper
from pyssp_standard.standard.ssp1.generated.ssm_generated_types import ParameterMapping, Tannotations, TmappingEntry
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1MappingEntry, Ssp1ParameterMapping


class Ssp1SsmXsdataMapper:
    def read_parameter_mapping(self, generated: ParameterMapping) -> Ssp1ParameterMapping:
        document = Ssp1ParameterMapping(
            version=generated.version,
            metadata=Ssp1SscXsdataMapper.read_document_metadata(generated),
        )
        for entry in generated.mapping_entry:
            document.mappings.append(
                Ssp1MappingEntry(
                    source=entry.source,
                    target=entry.target,
                    suppress_unit_conversion=self._read_suppress_unit_conversion(entry),
                    transformation=Ssp1SscXsdataMapper.read_transformation(entry),
                    id=entry.id,
                    description=entry.description,
                    annotations=Ssp1SscXsdataMapper.read_annotations(entry.annotations),
                )
            )
        return document

    def write_parameter_mapping(self, model: Ssp1ParameterMapping) -> ParameterMapping:
        return ParameterMapping(
            version=model.version,
            mapping_entry=[self._write_mapping_entry(entry) for entry in model.mappings],
            **Ssp1SscXsdataMapper.write_document_metadata(model.metadata, annotations_cls=Tannotations),
        )

    @staticmethod
    def _read_suppress_unit_conversion(entry: TmappingEntry) -> bool | None:
        return True if entry.suppress_unit_conversion else None

    def _write_mapping_entry(self, entry: Ssp1MappingEntry) -> TmappingEntry:
        generated = TmappingEntry(
            source=entry.source,
            target=entry.target,
            suppress_unit_conversion=bool(entry.suppress_unit_conversion),
            id=entry.id,
            description=entry.description,
            annotations=Ssp1SscXsdataMapper.write_annotations(entry.annotations, annotations_cls=Tannotations),
        )
        if entry.transformation is not None:
            Ssp1SscXsdataMapper.apply_transformation(generated, entry.transformation)
        return generated
