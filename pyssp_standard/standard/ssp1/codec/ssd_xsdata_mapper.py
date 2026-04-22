from __future__ import annotations

from xml.etree import ElementTree as ET

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from pyssp_standard.standard.ssp1.codec.ssm_xsdata_mapper import Ssp1SsmXsdataMapper
from pyssp_standard.standard.ssp1.codec.ssv_xsdata_mapper import Ssp1SsvXsdataMapper
from pyssp_standard.standard.ssp1.generated.ssd_generated_types import (
    ConnectorKind,
    ParameterBindingSourceBase,
    ParameterMappingSourceBase,
    SystemStructureDescription,
    Tcomponent,
    TcomponentImplementation,
    Tconnectors,
    TdefaultExperiment,
    TparameterBindings,
    Tsystem,
)
from pyssp_standard.standard.ssp1.generated.ssm_generated_types import ParameterMapping
from pyssp_standard.standard.ssp1.generated.ssv_generated_types import ParameterSet
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1Connector,
    Ssd1DefaultExperiment,
    Ssd1ParameterBinding,
    Ssd1ParameterMappingReference,
    Ssd1System,
    Ssd1SystemStructureDescription,
)


class Ssp1SsdXsdataMapper:
    def __init__(self):
        self._parser = XmlParser()
        self._serializer = XmlSerializer(config=SerializerConfig(indent="  "))
        self._ssv_mapper = Ssp1SsvXsdataMapper()
        self._ssm_mapper = Ssp1SsmXsdataMapper()

    def read_system_structure_description(
        self,
        generated: SystemStructureDescription,
    ) -> Ssd1SystemStructureDescription:
        return Ssd1SystemStructureDescription(
            name=generated.name,
            version=generated.version,
            system=self._read_system(generated.system) if generated.system is not None else None,
            default_experiment=self._read_default_experiment(generated.default_experiment),
        )

    def write_system_structure_description(
        self,
        document: Ssd1SystemStructureDescription,
    ) -> SystemStructureDescription:
        return SystemStructureDescription(
            version=document.version,
            name=document.name,
            system=self._write_system(document.system) if document.system is not None else None,
            default_experiment=self._write_default_experiment(document.default_experiment),
        )

    @staticmethod
    def _read_default_experiment(generated: TdefaultExperiment | None) -> Ssd1DefaultExperiment | None:
        if generated is None:
            return None
        return Ssd1DefaultExperiment(start_time=generated.start_time, stop_time=generated.stop_time)

    @staticmethod
    def _write_default_experiment(model: Ssd1DefaultExperiment | None) -> TdefaultExperiment | None:
        if model is None:
            return None
        return TdefaultExperiment(start_time=model.start_time, stop_time=model.stop_time)

    def _read_system(self, generated: Tsystem) -> Ssd1System:
        system = Ssd1System(name=generated.name)

        if generated.connectors is not None:
            system.connectors = [self._read_connector(connector) for connector in generated.connectors.connector]

        if generated.elements is not None:
            system.elements = [self._read_component(component) for component in generated.elements.component]

        if generated.connections is not None:
            system.connections = [
                Ssd1Connection(
                    start_element=connection.start_element,
                    start_connector=connection.start_connector,
                    end_element=connection.end_element,
                    end_connector=connection.end_connector,
                )
                for connection in generated.connections.connection
            ]

        if generated.parameter_bindings is not None:
            system.parameter_bindings = [
                self._read_parameter_binding(binding)
                for binding in generated.parameter_bindings.parameter_binding
            ]

        return system

    def _write_system(self, model: Ssd1System) -> Tsystem:
        return Tsystem(
            name=model.name,
            connectors=Tconnectors(connector=[self._write_connector(connector) for connector in model.connectors])
            if model.connectors
            else None,
            elements=Tsystem.Elements(component=[self._write_component(component) for component in model.elements])
            if model.elements
            else None,
            connections=Tsystem.Connections(
                connection=[
                    Tsystem.Connections.Connection(
                        start_element=connection.start_element,
                        start_connector=connection.start_connector,
                        end_element=connection.end_element,
                        end_connector=connection.end_connector,
                    )
                    for connection in model.connections
                ]
            )
            if model.connections
            else None,
            parameter_bindings=TparameterBindings(
                parameter_binding=[self._write_parameter_binding(binding) for binding in model.parameter_bindings]
            )
            if model.parameter_bindings
            else None,
        )

    def _read_component(self, generated: Tcomponent) -> Ssd1Component:
        implementation = None
        if generated.implementation != TcomponentImplementation.ANY:
            implementation = generated.implementation.value
        return Ssd1Component(
            name=generated.name,
            source=generated.source,
            component_type=generated.type_value,
            implementation=implementation,
            connectors=[self._read_connector(connector) for connector in generated.connectors.connector]
            if generated.connectors is not None
            else [],
        )

    def _write_component(self, model: Ssd1Component) -> Tcomponent:
        implementation = TcomponentImplementation.ANY
        if model.implementation is not None:
            implementation = TcomponentImplementation(model.implementation)

        return Tcomponent(
            name=model.name,
            source=model.source,
            type_value=model.component_type or "application/x-fmu-sharedlibrary",
            implementation=implementation,
            connectors=Tconnectors(connector=[self._write_connector(connector) for connector in model.connectors])
            if model.connectors
            else None,
        )

    @staticmethod
    def _read_connector(generated: Tconnectors.Connector) -> Ssd1Connector:
        type_name = None
        type_attributes: dict[str, str] = {}

        if generated.real is not None:
            type_name = "Real"
            if generated.real.unit is not None:
                type_attributes["unit"] = generated.real.unit
        elif generated.integer is not None:
            type_name = "Integer"
        elif generated.boolean is not None:
            type_name = "Boolean"
        elif generated.string is not None:
            type_name = "String"
        elif generated.enumeration is not None:
            type_name = "Enumeration"
            type_attributes["name"] = generated.enumeration.name
        elif generated.binary is not None:
            type_name = "Binary"
            type_attributes["mime-type"] = generated.binary.mime_type

        return Ssd1Connector(
            name=str(generated.name),
            kind=generated.kind.value,
            type_name=type_name,
            type_attributes=type_attributes,
        )

    @staticmethod
    def _write_connector(model: Ssd1Connector) -> Tconnectors.Connector:
        generated = Tconnectors.Connector(name=model.name, kind=ConnectorKind(model.kind))
        if model.type_name == "Real":
            generated.real = Tconnectors.Connector.Real(unit=model.type_attributes.get("unit"))
        elif model.type_name == "Integer":
            generated.integer = ""
        elif model.type_name == "Boolean":
            generated.boolean = ""
        elif model.type_name == "String":
            generated.string = ""
        elif model.type_name == "Enumeration":
            generated.enumeration = Tconnectors.Connector.Enumeration(name=model.type_attributes.get("name", ""))
        elif model.type_name == "Binary":
            generated.binary = Tconnectors.Connector.Binary(
                mime_type=model.type_attributes.get("mime-type", "application/octet-stream")
            )
        return generated

    def _read_parameter_binding(self, generated: TparameterBindings.ParameterBinding) -> Ssd1ParameterBinding:
        prefix = self._normalize_prefix(generated.prefix)
        parameter_mapping = self._read_parameter_mapping(generated.parameter_mapping)

        if generated.source is not None:
            return Ssd1ParameterBinding(
                source=generated.source,
                prefix=prefix,
                parameter_mapping=parameter_mapping,
            )

        parameter_set = None
        if generated.parameter_values is not None and generated.parameter_values.any_element:
            parameter_set = self._read_inline_parameter_set(generated.parameter_values.any_element[0])

        return Ssd1ParameterBinding(
            prefix=prefix,
            parameter_set=parameter_set,
            parameter_mapping=parameter_mapping,
        )

    def _write_parameter_binding(self, model: Ssd1ParameterBinding) -> TparameterBindings.ParameterBinding:
        binding = TparameterBindings.ParameterBinding(
            prefix=f"{model.prefix}." if model.prefix else "",
            source=model.source,
            source_base=ParameterBindingSourceBase.SSD,
        )
        if model.parameter_set is not None:
            binding.parameter_values = TparameterBindings.ParameterBinding.ParameterValues(
                any_element=[self._ssv_mapper.write_parameterset(model.parameter_set)]
            )
        if model.parameter_mapping is not None:
            binding.parameter_mapping = self._write_parameter_mapping(model.parameter_mapping)
        return binding

    def _read_parameter_mapping(
        self,
        generated: TparameterBindings.ParameterBinding.ParameterMapping | None,
    ) -> Ssd1ParameterMappingReference | None:
        if generated is None:
            return None
        if generated.source is not None:
            return Ssd1ParameterMappingReference(source=generated.source)
        if not generated.any_element:
            return Ssd1ParameterMappingReference()
        return Ssd1ParameterMappingReference(mapping=self._read_inline_parameter_mapping(generated.any_element[0]))

    @staticmethod
    def _write_parameter_mapping(
        model: Ssd1ParameterMappingReference,
    ) -> TparameterBindings.ParameterBinding.ParameterMapping:
        mapping = TparameterBindings.ParameterBinding.ParameterMapping(
            source=model.source,
            source_base=ParameterMappingSourceBase.SSD,
        )
        if model.mapping is not None:
            mapping.any_element = [Ssp1SsmXsdataMapper().write_parameter_mapping(model.mapping)]
        return mapping

    def _read_inline_parameter_set(self, value: object):
        if isinstance(value, ParameterSet):
            return self._ssv_mapper.read_parameterset(value)
        xml_text = self._serialize_unknown_element(value)
        generated = self._parser.from_string(xml_text, ParameterSet)
        return self._ssv_mapper.read_parameterset(generated)

    def _read_inline_parameter_mapping(self, value: object):
        if isinstance(value, ParameterMapping):
            return self._ssm_mapper.read_parameter_mapping(value)
        xml_text = self._serialize_unknown_element(value)
        generated = self._parser.from_string(xml_text, ParameterMapping)
        return self._ssm_mapper.read_parameter_mapping(generated)

    def _serialize_unknown_element(self, value: object) -> str:
        if isinstance(value, ET.Element):
            return ET.tostring(value, encoding="unicode")
        return self._serializer.render(value)

    @staticmethod
    def _normalize_prefix(prefix: str | None) -> str | None:
        if prefix is None:
            return None
        prefix = prefix.strip()
        if prefix.endswith("."):
            prefix = prefix[:-1]
        return prefix or None
