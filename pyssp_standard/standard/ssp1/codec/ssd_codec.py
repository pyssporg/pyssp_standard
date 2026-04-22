from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.codec.ssm_codec import Ssp1SsmCodec
from pyssp_standard.standard.ssp1.codec.ssv_codec import Ssp1SsvCodec
from pyssp_standard.standard.ssp1.codec.xml_utils import (
    NS_SSC,
    NS_SSD,
    NS_SSM,
    NS_SSV,
    append_annotations,
    apply_metadata_attributes,
    find_type_child,
    first_child,
    local_name,
    normalize_binding_prefix,
    parse_float,
    parse_metadata_attributes,
    qname,
    render_xml,
    serialize_binding_prefix,
)
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1SystemStructureDescription
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1Connector,
    Ssd1DefaultExperiment,
    Ssd1ParameterBinding,
    Ssd1ParameterMappingReference,
    Ssd1System,
)


class Ssp1SsdCodec:
    def __init__(self):
        self._ssv_codec = Ssp1SsvCodec()
        self._ssm_codec = Ssp1SsmCodec()

    def parse(self, xml_text: str) -> Ssd1SystemStructureDescription:
        root = ET.fromstring(xml_text)
        document = Ssd1SystemStructureDescription(
            name=root.attrib["name"],
            version=root.attrib["version"],
            metadata=parse_metadata_attributes(root),
        )
        system_element = first_child(root, NS_SSD, "System")
        if system_element is not None:
            document.system = self._parse_system(system_element)
        default_experiment_element = first_child(root, NS_SSD, "DefaultExperiment")
        if default_experiment_element is not None:
            document.default_experiment = Ssd1DefaultExperiment(
                start_time=parse_float(default_experiment_element.attrib.get("startTime")),
                stop_time=parse_float(default_experiment_element.attrib.get("stopTime")),
            )
        return document

    def serialize(self, document: Ssd1SystemStructureDescription) -> str:
        root = ET.Element(qname(NS_SSD, "SystemStructureDescription"))
        root.set("name", document.name)
        root.set("version", document.version)
        apply_metadata_attributes(root, document.metadata)
        if document.system is not None:
            root.append(self._serialize_system(document.system))
        if document.default_experiment is not None:
            default_experiment = ET.SubElement(root, qname(NS_SSD, "DefaultExperiment"))
            if document.default_experiment.start_time is not None:
                default_experiment.set("startTime", str(document.default_experiment.start_time))
            if document.default_experiment.stop_time is not None:
                default_experiment.set("stopTime", str(document.default_experiment.stop_time))
        append_annotations(root, document.metadata.annotations, NS_SSD)
        return render_xml(root, {"ssc": NS_SSC, "ssd": NS_SSD, "ssm": NS_SSM, "ssv": NS_SSV})

    def _parse_system(self, element: ET.Element) -> Ssd1System:
        system = Ssd1System(
            element=element.attrib.get("element"),
            name=element.attrib["name"],
        )
        parameter_bindings_element = first_child(element, NS_SSD, "ParameterBindings")
        if parameter_bindings_element is not None:
            system.parameter_bindings = [
                self._parse_parameter_binding(binding)
                for binding in parameter_bindings_element.findall(qname(NS_SSD, "ParameterBinding"))
            ]
        elements_element = first_child(element, NS_SSD, "Elements")
        if elements_element is not None:
            system.elements = [
                self._parse_component(component)
                for component in elements_element.findall(qname(NS_SSD, "Component"))
            ]
        connectors_element = first_child(element, NS_SSD, "Connectors")
        if connectors_element is not None:
            system.connectors = [
                self._parse_connector(connector)
                for connector in connectors_element.findall(qname(NS_SSD, "Connector"))
            ]
        connections_element = first_child(element, NS_SSD, "Connections")
        if connections_element is not None:
            system.connections = [
                Ssd1Connection(
                    start_element=connection.attrib.get("startElement"),
                    start_connector=connection.attrib["startConnector"],
                    end_element=connection.attrib.get("endElement"),
                    end_connector=connection.attrib["endConnector"],
                )
                for connection in connections_element.findall(qname(NS_SSD, "Connection"))
            ]
        return system

    def _serialize_system(self, system: Ssd1System) -> ET.Element:
        element = ET.Element(qname(NS_SSD, "System"))
        element.set("name", system.name)
        if system.element is not None:
            element.set("element", system.element)

        if system.connectors:
            connectors_element = ET.SubElement(element, qname(NS_SSD, "Connectors"))
            for connector in system.connectors:
                connectors_element.append(self._serialize_connector(connector))

        if system.parameter_bindings:
            bindings_element = ET.SubElement(element, qname(NS_SSD, "ParameterBindings"))
            for binding in system.parameter_bindings:
                bindings_element.append(self._serialize_parameter_binding(binding))

        if system.elements:
            elements_element = ET.SubElement(element, qname(NS_SSD, "Elements"))
            for component in system.elements:
                elements_element.append(self._serialize_component(component))

        if system.connections:
            connections_element = ET.SubElement(element, qname(NS_SSD, "Connections"))
            for connection in system.connections:
                connection_element = ET.SubElement(connections_element, qname(NS_SSD, "Connection"))
                if connection.start_element is not None:
                    connection_element.set("startElement", connection.start_element)
                connection_element.set("startConnector", connection.start_connector)
                if connection.end_element is not None:
                    connection_element.set("endElement", connection.end_element)
                connection_element.set("endConnector", connection.end_connector)

        return element

    def _parse_component(self, element: ET.Element) -> Ssd1Component:
        component = Ssd1Component(
            name=element.attrib["name"],
            source=element.attrib["source"],
            component_type=element.attrib.get("type"),
            implementation=element.attrib.get("implementation"),
        )
        connectors_element = first_child(element, NS_SSD, "Connectors")
        if connectors_element is not None:
            component.connectors = [
                self._parse_connector(connector)
                for connector in connectors_element.findall(qname(NS_SSD, "Connector"))
            ]
        return component

    def _serialize_component(self, component: Ssd1Component) -> ET.Element:
        element = ET.Element(qname(NS_SSD, "Component"))
        element.set("name", component.name)
        element.set("source", component.source)
        if component.component_type is not None:
            element.set("type", component.component_type)
        if component.implementation is not None:
            element.set("implementation", component.implementation)
        if component.connectors:
            connectors_element = ET.SubElement(element, qname(NS_SSD, "Connectors"))
            for connector in component.connectors:
                connectors_element.append(self._serialize_connector(connector))
        return element

    def _parse_connector(self, element: ET.Element) -> Ssd1Connector:
        type_element = find_type_child(element, exclude_local_names={"ConnectorGeometry", "Annotations"})
        type_name = local_name(type_element.tag) if type_element is not None else None
        type_attributes = dict(type_element.attrib) if type_element is not None else {}
        return Ssd1Connector(
            element=element.attrib.get("element"),
            name=element.attrib["name"],
            kind=element.attrib["kind"],
            type_name=type_name,
            type_attributes=type_attributes,
            id=element.attrib.get("id"),
            description=element.attrib.get("description"),
            annotations=parse_metadata_attributes(element).annotations,
        )

    def _serialize_connector(self, connector: Ssd1Connector) -> ET.Element:
        element = ET.Element(qname(NS_SSD, "Connector"))
        element.set("name", connector.name)
        element.set("kind", connector.kind)
        if connector.element is not None:
            element.set("element", connector.element)
        if connector.id is not None:
            element.set("id", connector.id)
        if connector.description is not None:
            element.set("description", connector.description)
        if connector.type_name is not None:
            type_element = ET.SubElement(element, qname(NS_SSC, connector.type_name))
            for key, value in connector.type_attributes.items():
                type_element.set(key, str(value))
        append_annotations(element, connector.annotations, NS_SSD)
        return element

    def _parse_parameter_binding(self, element: ET.Element) -> Ssd1ParameterBinding:
        binding = Ssd1ParameterBinding(
            source=element.attrib.get("source"),
            prefix=normalize_binding_prefix(element.attrib.get("prefix")),
        )
        parameter_values = first_child(element, NS_SSD, "ParameterValues")
        if parameter_values is not None and len(parameter_values):
            binding.parameter_set = self._ssv_codec.parse(ET.tostring(parameter_values[0], encoding="unicode"))
        parameter_mapping = first_child(element, NS_SSD, "ParameterMapping")
        if parameter_mapping is not None:
            inline_mapping = parameter_mapping[0] if len(parameter_mapping) else None
            binding.parameter_mapping = Ssd1ParameterMappingReference(
                source=parameter_mapping.attrib.get("source"),
                mapping=(
                    self._ssm_codec.parse(ET.tostring(inline_mapping, encoding="unicode"))
                    if parameter_mapping.attrib.get("source") is None and inline_mapping is not None
                    else None
                ),
            )
        return binding

    def _serialize_parameter_binding(self, binding: Ssd1ParameterBinding) -> ET.Element:
        element = ET.Element(qname(NS_SSD, "ParameterBinding"))
        serialized_prefix = serialize_binding_prefix(binding.prefix)
        if serialized_prefix is not None:
            element.set("prefix", serialized_prefix)
        if binding.source is not None:
            element.set("source", binding.source)
        if binding.parameter_set is not None:
            parameter_values = ET.SubElement(element, qname(NS_SSD, "ParameterValues"))
            parameter_values.append(ET.fromstring(self._ssv_codec.serialize(binding.parameter_set)))
        if binding.parameter_mapping is not None:
            mapping_element = ET.SubElement(element, qname(NS_SSD, "ParameterMapping"))
            if binding.parameter_mapping.source is not None:
                mapping_element.set("source", binding.parameter_mapping.source)
            elif binding.parameter_mapping.mapping is not None:
                mapping_element.append(ET.fromstring(self._ssm_codec.serialize(binding.parameter_mapping.mapping)))
        return element
