from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.ssp1.codec.ssm_xml_codec import Ssp1SsmXmlCodec
from pyssp_standard.standard.ssp1.codec.ssv_xsdata_codec import NS_SSV, Ssp1SsvXsdataCodec
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1Component,
    Ssd1Connection,
    Ssd1Connector,
    Ssd1DefaultExperiment,
    Ssd1ParameterBinding,
    Ssd1ParameterMappingReference,
    Ssd1SystemStructureDescription,
    Ssd1System,
)


NS_SSD = "http://ssp-standard.org/SSP1/SystemStructureDescription"
NS_SSC = "http://ssp-standard.org/SSP1/SystemStructureCommon"
TYPE_TAGS = {"Real", "Integer", "Boolean", "String", "Enumeration", "Binary"}


class Ssp1SsdXmlCodec:
    """Direct SSP1 SSD XML codec without generated bindings or archive logic."""

    def __init__(self, ssv_codec: Ssp1SsvXsdataCodec | None = None, ssm_codec: Ssp1SsmXmlCodec | None = None):
        self._ssv_codec = ssv_codec or Ssp1SsvXsdataCodec()
        self._ssm_codec = ssm_codec or Ssp1SsmXmlCodec()

    def parse(self, xml_text: str) -> Ssd1SystemStructureDescription:
        root = ET.fromstring(xml_text)
        self._require_root(root, "SystemStructureDescription")

        document = Ssd1SystemStructureDescription(
            name=root.attrib.get("name", ""),
            version=root.attrib.get("version", "1.0"),
        )
        system = root.find(f"{{{NS_SSD}}}System")
        if system is not None:
            document.system = self._read_system(system)

        default_experiment = root.find(f"{{{NS_SSD}}}DefaultExperiment")
        if default_experiment is not None:
            document.default_experiment = Ssd1DefaultExperiment(
                start_time=self._parse_float(default_experiment.attrib.get("startTime")),
                stop_time=self._parse_float(default_experiment.attrib.get("stopTime")),
            )
        return document

    def serialize(self, document: Ssd1SystemStructureDescription) -> str:
        root = ET.Element(
            f"{{{NS_SSD}}}SystemStructureDescription",
            attrib={"name": document.name, "version": document.version},
        )
        ET.register_namespace("ssd", NS_SSD)
        ET.register_namespace("ssc", NS_SSC)

        if document.system is not None:
            root.append(self._write_system(document.system))
        if document.default_experiment is not None:
            attrib: dict[str, str] = {}
            if document.default_experiment.start_time is not None:
                attrib["startTime"] = str(document.default_experiment.start_time)
            if document.default_experiment.stop_time is not None:
                attrib["stopTime"] = str(document.default_experiment.stop_time)
            ET.SubElement(root, f"{{{NS_SSD}}}DefaultExperiment", attrib=attrib)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        return ET.tostring(root, encoding="unicode")

    def _read_system(self, element: ET.Element) -> Ssd1System:
        system = Ssd1System(name=element.attrib.get("name", ""))

        connectors = element.find(f"{{{NS_SSD}}}Connectors")
        if connectors is not None:
            system.connectors = [self._read_connector(child) for child in list(connectors)]

        elements = element.find(f"{{{NS_SSD}}}Elements")
        if elements is not None:
            for child in list(elements):
                if self._local_name(child.tag) != "Component":
                    continue
                component = Ssd1Component(
                    name=child.attrib.get("name", ""),
                    source=child.attrib.get("source", ""),
                    component_type=child.attrib.get("type"),
                    implementation=child.attrib.get("implementation"),
                )
                component_connectors = child.find(f"{{{NS_SSD}}}Connectors")
                if component_connectors is not None:
                    component.connectors = [self._read_connector(connector) for connector in list(component_connectors)]
                system.elements.append(component)

        connections = element.find(f"{{{NS_SSD}}}Connections")
        if connections is not None:
            system.connections = [
                Ssd1Connection(
                    start_element=connection.attrib.get("startElement"),
                    start_connector=connection.attrib.get("startConnector", ""),
                    end_element=connection.attrib.get("endElement"),
                    end_connector=connection.attrib.get("endConnector", ""),
                )
                for connection in list(connections)
                if self._local_name(connection.tag) == "Connection"
            ]

        bindings = element.find(f"{{{NS_SSD}}}ParameterBindings")
        if bindings is not None:
            system.parameter_bindings = [
                self._read_parameter_binding(binding)
                for binding in list(bindings)
                if self._local_name(binding.tag) == "ParameterBinding"
            ]
        return system

    def _write_system(self, system: Ssd1System) -> ET.Element:
        element = ET.Element(f"{{{NS_SSD}}}System", attrib={"name": system.name})

        if system.connectors:
            connectors = ET.SubElement(element, f"{{{NS_SSD}}}Connectors")
            for connector in system.connectors:
                connectors.append(self._write_connector(connector))

        if system.parameter_bindings:
            bindings = ET.SubElement(element, f"{{{NS_SSD}}}ParameterBindings")
            for binding in system.parameter_bindings:
                bindings.append(self._write_parameter_binding(binding))

        elements = ET.SubElement(element, f"{{{NS_SSD}}}Elements")
        for component in system.elements:
            component_attrib = {"name": component.name, "source": component.source}
            if component.component_type is not None:
                component_attrib["type"] = component.component_type
            if component.implementation is not None:
                component_attrib["implementation"] = component.implementation
            component_element = ET.SubElement(elements, f"{{{NS_SSD}}}Component", attrib=component_attrib)
            if component.connectors:
                component_connectors = ET.SubElement(component_element, f"{{{NS_SSD}}}Connectors")
                for connector in component.connectors:
                    component_connectors.append(self._write_connector(connector))

        if system.connections:
            connections = ET.SubElement(element, f"{{{NS_SSD}}}Connections")
            for connection in system.connections:
                attrib = {
                    "startConnector": connection.start_connector,
                    "endConnector": connection.end_connector,
                }
                if connection.start_element is not None:
                    attrib["startElement"] = connection.start_element
                if connection.end_element is not None:
                    attrib["endElement"] = connection.end_element
                ET.SubElement(connections, f"{{{NS_SSD}}}Connection", attrib=attrib)

        return element

    def _read_connector(self, element: ET.Element) -> Ssd1Connector:
        type_name = None
        type_attributes: dict[str, str] = {}
        for child in list(element):
            local_name = self._local_name(child.tag)
            if local_name in TYPE_TAGS:
                type_name = local_name
                type_attributes = dict(child.attrib)
                break
        return Ssd1Connector(
            name=element.attrib.get("name", ""),
            kind=element.attrib.get("kind", ""),
            type_name=type_name,
            type_attributes=type_attributes,
        )

    def _write_connector(self, connector: Ssd1Connector) -> ET.Element:
        element = ET.Element(
            f"{{{NS_SSD}}}Connector",
            attrib={"name": connector.name, "kind": connector.kind},
        )
        if connector.type_name in TYPE_TAGS:
            ET.SubElement(
                element,
                f"{{{NS_SSC}}}{connector.type_name}",
                attrib=dict(connector.type_attributes),
            )
        return element

    def _read_parameter_binding(self, element: ET.Element) -> Ssd1ParameterBinding:
        prefix = element.attrib.get("prefix")
        if prefix:
            prefix = prefix[:-1] if prefix.endswith(".") else prefix
        external_path = element.attrib.get("source")
        parameter_mapping = self._read_parameter_mapping(element)
        if external_path is not None:
            return Ssd1ParameterBinding(
                prefix=prefix,
                parameter_set_source=external_path,
                parameter_mapping=parameter_mapping,
            )

        parameter_values = next(
            (child for child in list(element) if self._local_name(child.tag) == "ParameterValues"),
            None,
        )
        inline_parameter_set = None
        if parameter_values is not None:
            inline_parameter_set = next(iter(parameter_values), None)
        elif list(element):
            # Backward-compatible parse path for earlier demo-style fixtures.
            inline_parameter_set = next((child for child in list(element) if self._local_name(child.tag) == "ParameterSet"), None)

        if inline_parameter_set is not None:
            xml_text = ET.tostring(inline_parameter_set, encoding="unicode")
            return Ssd1ParameterBinding(
                prefix=prefix,
                parameter_set=self._ssv_codec.parse(xml_text),
                parameter_mapping=parameter_mapping,
            )

        return Ssd1ParameterBinding(
            prefix=prefix,
            parameter_mapping=parameter_mapping,
        )

    def _write_parameter_binding(self, binding: Ssd1ParameterBinding) -> ET.Element:
        attrib: dict[str, str] = {}
        if binding.prefix:
            attrib["prefix"] = f"{binding.prefix}."
        element = ET.Element(f"{{{NS_SSD}}}ParameterBinding", attrib=attrib)

        if binding.parameter_set_source is None and binding.parameter_set is not None:
            xml_text = self._ssv_codec.serialize(binding.parameter_set)
            values_element = ET.SubElement(element, f"{{{NS_SSD}}}ParameterValues")
            values_element.append(ET.fromstring(xml_text))
        elif binding.parameter_set_source:
            element.set("source", binding.parameter_set_source)

        if binding.parameter_mapping is not None:
            mapping_element = ET.SubElement(element, f"{{{NS_SSD}}}ParameterMapping")
            if binding.parameter_mapping.source:
                mapping_element.set("source", binding.parameter_mapping.source)
            elif binding.parameter_mapping.mapping is not None:
                xml_text = self._ssm_codec.serialize(binding.parameter_mapping.mapping)
                mapping_element.append(ET.fromstring(xml_text))
        return element

    def _read_parameter_mapping(self, element: ET.Element) -> Ssd1ParameterMappingReference | None:
        mapping_element = next(
            (child for child in list(element) if self._local_name(child.tag) == "ParameterMapping"),
            None,
        )
        if mapping_element is None:
            return None

        mapping_path = mapping_element.attrib.get("source")
        if mapping_path is not None:
            return Ssd1ParameterMappingReference(source=mapping_path)

        inline_mapping = next(iter(mapping_element), None)
        if inline_mapping is None:
            return Ssd1ParameterMappingReference()

        xml_text = ET.tostring(inline_mapping, encoding="unicode")
        return Ssd1ParameterMappingReference(mapping=self._ssm_codec.parse(xml_text))

    @staticmethod
    def _require_root(root: ET.Element, expected_local_name: str) -> None:
        if root.tag != f"{{{NS_SSD}}}{expected_local_name}":
            raise ValueError(f"Unexpected SSD root tag '{root.tag}'")

    @staticmethod
    def _local_name(tag: str) -> str:
        return tag.split("}", 1)[-1]

    @staticmethod
    def _parse_float(value: str | None) -> float | None:
        if value is None:
            return None
        return float(value)
