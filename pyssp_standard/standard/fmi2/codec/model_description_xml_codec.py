from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.fmi2.model.model_description import (
    Fmi2DefaultExperiment,
    Fmi2ElementInfo,
    Fmi2ModelDescriptionDocument,
    Fmi2ModelStructure,
    Fmi2ScalarVariable,
    Fmi2TypeDefinition,
    Fmi2Unit,
    Fmi2Unknown,
)


class Fmi2ModelDescriptionXmlCodec:
    """Direct FMI2 modelDescription XML codec."""

    def parse(self, xml_text: str) -> Fmi2ModelDescriptionDocument:
        root = ET.fromstring(xml_text)
        if root.tag != "fmiModelDescription":
            raise ValueError(f"Unexpected FMI2 root tag '{root.tag}'")

        interface_type, interface_attributes = self._read_interface(root)
        default_experiment = self._read_default_experiment(root.find("DefaultExperiment"))

        return Fmi2ModelDescriptionDocument(
            root=Fmi2ElementInfo(tag=root.tag, attributes=dict(root.attrib)),
            fmi_version=root.attrib.get("fmiVersion", ""),
            model_name=root.attrib.get("modelName", ""),
            guid=root.attrib.get("guid", ""),
            generation_tool=root.attrib.get("generationTool"),
            generation_date_and_time=root.attrib.get("generationDateAndTime"),
            variable_naming_convention=root.attrib.get("variableNamingConvention"),
            number_of_event_indicators=self._parse_int(root.attrib.get("numberOfEventIndicators")),
            interface_type=interface_type,
            interface_attributes=interface_attributes,
            unit_definitions=self._read_unit_definitions(root.find("UnitDefinitions")),
            type_definitions=self._read_type_definitions(root.find("TypeDefinitions")),
            variables=self._read_variables(root.find("ModelVariables")),
            model_structure=self._read_model_structure(root.find("ModelStructure")),
            default_experiment=default_experiment,
        )

    def serialize(self, document: Fmi2ModelDescriptionDocument) -> str:
        attrib = {
            "fmiVersion": document.fmi_version,
            "modelName": document.model_name,
            "guid": document.guid,
        }
        self._maybe_set(attrib, "generationTool", document.generation_tool)
        self._maybe_set(attrib, "generationDateAndTime", document.generation_date_and_time)
        self._maybe_set(attrib, "variableNamingConvention", document.variable_naming_convention)
        if document.number_of_event_indicators is not None:
            attrib["numberOfEventIndicators"] = str(document.number_of_event_indicators)
        root = ET.Element("fmiModelDescription", attrib=attrib)
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

        if document.interface_type is not None:
            ET.SubElement(root, document.interface_type, attrib=dict(document.interface_attributes))

        if document.unit_definitions:
            units = ET.SubElement(root, "UnitDefinitions")
            for unit in document.unit_definitions:
                unit_element = ET.SubElement(units, "Unit", attrib={"name": unit.name})
                if unit.base_unit:
                    ET.SubElement(unit_element, "BaseUnit", attrib=dict(unit.base_unit))

        if document.type_definitions:
            types = ET.SubElement(root, "TypeDefinitions")
            for type_definition in document.type_definitions:
                simple_type = ET.SubElement(types, "SimpleType", attrib={"name": type_definition.name})
                type_element = ET.SubElement(simple_type, type_definition.type_name, attrib=dict(type_definition.attributes))
                for item in type_definition.enumeration_items:
                    ET.SubElement(type_element, "Item", attrib=dict(item))

        if document.default_experiment is not None:
            default_experiment_attrib: dict[str, str] = {}
            if document.default_experiment.start_time is not None:
                default_experiment_attrib["startTime"] = str(document.default_experiment.start_time)
            if document.default_experiment.stop_time is not None:
                default_experiment_attrib["stopTime"] = str(document.default_experiment.stop_time)
            if document.default_experiment.tolerance is not None:
                default_experiment_attrib["tolerance"] = str(document.default_experiment.tolerance)
            ET.SubElement(root, "DefaultExperiment", attrib=default_experiment_attrib)

        variables = ET.SubElement(root, "ModelVariables")
        for variable in document.variables:
            variable_attrib = {
                "name": variable.name,
                "valueReference": variable.value_reference,
            }
            self._maybe_set(variable_attrib, "description", variable.description)
            self._maybe_set(variable_attrib, "causality", variable.causality)
            self._maybe_set(variable_attrib, "variability", variable.variability)
            self._maybe_set(variable_attrib, "initial", variable.initial)
            variable_element = ET.SubElement(variables, "ScalarVariable", attrib=variable_attrib)
            type_attrib = dict(variable.type_attributes)
            self._maybe_set(type_attrib, "declaredType", variable.declared_type)
            self._maybe_set(type_attrib, "start", variable.start)
            ET.SubElement(variable_element, variable.type_name, attrib=type_attrib)

        model_structure = ET.SubElement(root, "ModelStructure")
        self._write_unknown_section(model_structure, "Outputs", document.model_structure.outputs)
        self._write_unknown_section(model_structure, "Derivatives", document.model_structure.derivatives)
        self._write_unknown_section(model_structure, "InitialUnknowns", document.model_structure.initial_unknowns)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        return ET.tostring(root, encoding="unicode")

    def _read_interface(self, root: ET.Element) -> tuple[str | None, dict[str, str]]:
        for interface_name in ("ModelExchange", "CoSimulation"):
            element = root.find(interface_name)
            if element is not None:
                return interface_name, dict(element.attrib)
        return None, {}

    def _read_default_experiment(self, element: ET.Element | None) -> Fmi2DefaultExperiment | None:
        if element is None:
            return None
        return Fmi2DefaultExperiment(
            start_time=self._parse_float(element.attrib.get("startTime")),
            stop_time=self._parse_float(element.attrib.get("stopTime")),
            tolerance=self._parse_float(element.attrib.get("tolerance")),
        )

    def _read_unit_definitions(self, element: ET.Element | None) -> list[Fmi2Unit]:
        if element is None:
            return []
        units: list[Fmi2Unit] = []
        for unit in list(element):
            if unit.tag != "Unit":
                continue
            base_unit = unit.find("BaseUnit")
            units.append(
                Fmi2Unit(
                    name=unit.attrib.get("name", ""),
                    base_unit=dict(base_unit.attrib) if base_unit is not None else {},
                )
            )
        return units

    def _read_type_definitions(self, element: ET.Element | None) -> list[Fmi2TypeDefinition]:
        if element is None:
            return []
        definitions: list[Fmi2TypeDefinition] = []
        for simple_type in list(element):
            if simple_type.tag != "SimpleType":
                continue
            type_element = next(iter(simple_type), None)
            if type_element is None:
                continue
            definitions.append(
                Fmi2TypeDefinition(
                    name=simple_type.attrib.get("name", ""),
                    type_name=type_element.tag,
                    attributes=dict(type_element.attrib),
                    enumeration_items=[dict(item.attrib) for item in list(type_element) if item.tag == "Item"],
                )
            )
        return definitions

    def _read_variables(self, element: ET.Element | None) -> list[Fmi2ScalarVariable]:
        if element is None:
            return []
        variables: list[Fmi2ScalarVariable] = []
        for scalar_variable in list(element):
            if scalar_variable.tag != "ScalarVariable":
                continue
            type_element = next(iter(scalar_variable), None)
            if type_element is None:
                continue
            type_attributes = dict(type_element.attrib)
            variables.append(
                Fmi2ScalarVariable(
                    name=scalar_variable.attrib.get("name", ""),
                    value_reference=scalar_variable.attrib.get("valueReference", ""),
                    description=scalar_variable.attrib.get("description"),
                    causality=scalar_variable.attrib.get("causality"),
                    variability=scalar_variable.attrib.get("variability"),
                    initial=scalar_variable.attrib.get("initial"),
                    type_name=type_element.tag,
                    declared_type=type_attributes.pop("declaredType", None),
                    start=type_attributes.pop("start", None),
                    type_attributes=type_attributes,
                )
            )
        return variables

    def _read_model_structure(self, element: ET.Element | None) -> Fmi2ModelStructure:
        if element is None:
            return Fmi2ModelStructure()
        return Fmi2ModelStructure(
            outputs=self._read_unknowns(element.find("Outputs")),
            derivatives=self._read_unknowns(element.find("Derivatives")),
            initial_unknowns=self._read_unknowns(element.find("InitialUnknowns")),
        )

    def _read_unknowns(self, element: ET.Element | None) -> list[Fmi2Unknown]:
        if element is None:
            return []
        unknowns: list[Fmi2Unknown] = []
        for child in list(element):
            if child.tag != "Unknown":
                continue
            unknowns.append(
                Fmi2Unknown(
                    index=child.attrib.get("index", ""),
                    dependencies=child.attrib.get("dependencies"),
                    dependencies_kind=child.attrib.get("dependenciesKind"),
                )
            )
        return unknowns

    def _write_unknown_section(self, parent: ET.Element, section_name: str, unknowns: list[Fmi2Unknown]) -> None:
        section = ET.SubElement(parent, section_name)
        for unknown in unknowns:
            attrib = {"index": unknown.index}
            self._maybe_set(attrib, "dependencies", unknown.dependencies)
            self._maybe_set(attrib, "dependenciesKind", unknown.dependencies_kind)
            ET.SubElement(section, "Unknown", attrib=attrib)

    @staticmethod
    def _maybe_set(attributes: dict[str, str], key: str, value: str | None) -> None:
        if value is not None:
            attributes[key] = value

    @staticmethod
    def _parse_float(value: str | None) -> float | None:
        if value is None:
            return None
        return float(value)

    @staticmethod
    def _parse_int(value: str | None) -> int | None:
        if value is None:
            return None
        return int(value)
