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
    def parse(self, xml_text: str) -> Fmi2ModelDescriptionDocument:
        root = ET.fromstring(xml_text)
        interface_element = self._find_interface_element(root)
        document = Fmi2ModelDescriptionDocument(
            root=Fmi2ElementInfo(tag=root.tag, attributes=dict(root.attrib)),
            fmi_version=root.attrib["fmiVersion"],
            model_name=root.attrib["modelName"],
            guid=root.attrib["guid"],
            generation_tool=root.attrib.get("generationTool"),
            generation_date_and_time=root.attrib.get("generationDateAndTime"),
            variable_naming_convention=root.attrib.get("variableNamingConvention"),
            number_of_event_indicators=(
                int(root.attrib["numberOfEventIndicators"])
                if root.attrib.get("numberOfEventIndicators") is not None
                else None
            ),
            interface_type=interface_element.tag if interface_element is not None else None,
            interface_attributes=dict(interface_element.attrib) if interface_element is not None else {},
        )
        document.unit_definitions = self._parse_units(root.find("UnitDefinitions"))
        document.type_definitions = self._parse_type_definitions(root.find("TypeDefinitions"))
        document.default_experiment = self._parse_default_experiment(root.find("DefaultExperiment"))
        document.variables = self._parse_variables(root.find("ModelVariables"))
        document.model_structure = self._parse_model_structure(root.find("ModelStructure"))
        return document

    def serialize(self, document: Fmi2ModelDescriptionDocument) -> str:
        root_tag = document.root.tag if document.root is not None else "fmiModelDescription"
        root = ET.Element(root_tag)
        root_attributes = dict(document.root.attributes) if document.root is not None else {}
        root_attributes.update(
            {
                "fmiVersion": document.fmi_version,
                "modelName": document.model_name,
                "guid": document.guid,
            }
        )
        self._set_optional(root_attributes, "generationTool", document.generation_tool)
        self._set_optional(root_attributes, "generationDateAndTime", document.generation_date_and_time)
        self._set_optional(root_attributes, "variableNamingConvention", document.variable_naming_convention)
        self._set_optional(
            root_attributes,
            "numberOfEventIndicators",
            None if document.number_of_event_indicators is None else str(document.number_of_event_indicators),
        )
        for key, value in root_attributes.items():
            root.set(key, value)

        if document.interface_type is not None:
            interface_element = ET.SubElement(root, document.interface_type)
            for key, value in document.interface_attributes.items():
                interface_element.set(key, value)

        if document.unit_definitions:
            units_element = ET.SubElement(root, "UnitDefinitions")
            for unit in document.unit_definitions:
                unit_element = ET.SubElement(units_element, "Unit")
                unit_element.set("name", unit.name)
                if unit.base_unit:
                    base_unit = ET.SubElement(unit_element, "BaseUnit")
                    for key, value in unit.base_unit.items():
                        base_unit.set(key, value)

        if document.type_definitions:
            type_definitions = ET.SubElement(root, "TypeDefinitions")
            for type_definition in document.type_definitions:
                simple_type = ET.SubElement(type_definitions, "SimpleType")
                simple_type.set("name", type_definition.name)
                type_element = ET.SubElement(simple_type, type_definition.type_name)
                for key, value in type_definition.attributes.items():
                    type_element.set(key, value)
                for item in type_definition.enumeration_items:
                    item_element = ET.SubElement(type_element, "Item")
                    for key, value in item.items():
                        item_element.set(key, value)

        if document.default_experiment is not None:
            default_experiment = ET.SubElement(root, "DefaultExperiment")
            self._set_optional(default_experiment.attrib, "startTime", self._format_float(document.default_experiment.start_time))
            self._set_optional(default_experiment.attrib, "stopTime", self._format_float(document.default_experiment.stop_time))
            self._set_optional(default_experiment.attrib, "tolerance", self._format_float(document.default_experiment.tolerance))

        model_variables = ET.SubElement(root, "ModelVariables")
        for variable in document.variables:
            variable_element = ET.SubElement(model_variables, "ScalarVariable")
            variable_element.set("name", variable.name)
            variable_element.set("valueReference", variable.value_reference)
            self._set_optional(variable_element.attrib, "description", variable.description)
            self._set_optional(variable_element.attrib, "causality", variable.causality)
            self._set_optional(variable_element.attrib, "variability", variable.variability)
            self._set_optional(variable_element.attrib, "initial", variable.initial)

            type_element = ET.SubElement(variable_element, variable.type_name)
            type_attributes = dict(variable.type_attributes)
            self._set_optional(type_attributes, "declaredType", variable.declared_type)
            self._set_optional(type_attributes, "start", variable.start)
            for key, value in type_attributes.items():
                type_element.set(key, value)

        model_structure = ET.SubElement(root, "ModelStructure")
        self._append_unknown_group(model_structure, "Outputs", document.model_structure.outputs)
        self._append_unknown_group(model_structure, "Derivatives", document.model_structure.derivatives)
        self._append_unknown_group(model_structure, "InitialUnknowns", document.model_structure.initial_unknowns)

        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    def _find_interface_element(self, root: ET.Element) -> ET.Element | None:
        for tag in ("ModelExchange", "CoSimulation"):
            element = root.find(tag)
            if element is not None:
                return element
        return None

    def _parse_units(self, units_element: ET.Element | None) -> list[Fmi2Unit]:
        if units_element is None:
            return []
        units: list[Fmi2Unit] = []
        for unit_element in units_element.findall("Unit"):
            base_unit_element = unit_element.find("BaseUnit")
            units.append(
                Fmi2Unit(
                    name=unit_element.attrib["name"],
                    base_unit=dict(base_unit_element.attrib) if base_unit_element is not None else {},
                )
            )
        return units

    def _parse_type_definitions(self, type_definitions: ET.Element | None) -> list[Fmi2TypeDefinition]:
        if type_definitions is None:
            return []
        definitions: list[Fmi2TypeDefinition] = []
        for simple_type in type_definitions.findall("SimpleType"):
            type_element = next(iter(simple_type), None)
            if type_element is None:
                continue
            definitions.append(
                Fmi2TypeDefinition(
                    name=simple_type.attrib["name"],
                    type_name=type_element.tag,
                    attributes=dict(type_element.attrib),
                    enumeration_items=[dict(item.attrib) for item in type_element.findall("Item")],
                )
            )
        return definitions

    def _parse_default_experiment(self, element: ET.Element | None) -> Fmi2DefaultExperiment | None:
        if element is None:
            return None
        return Fmi2DefaultExperiment(
            start_time=self._parse_float(element.attrib.get("startTime")),
            stop_time=self._parse_float(element.attrib.get("stopTime")),
            tolerance=self._parse_float(element.attrib.get("tolerance")),
        )

    def _parse_variables(self, model_variables: ET.Element | None) -> list[Fmi2ScalarVariable]:
        if model_variables is None:
            return []
        variables: list[Fmi2ScalarVariable] = []
        for variable_element in model_variables.findall("ScalarVariable"):
            type_element = next(
                (child for child in variable_element if child.tag != "Annotations"),
                None,
            )
            if type_element is None:
                continue
            type_attributes = dict(type_element.attrib)
            declared_type = type_attributes.pop("declaredType", None)
            start = type_attributes.pop("start", None)
            variables.append(
                Fmi2ScalarVariable(
                    name=variable_element.attrib["name"],
                    value_reference=variable_element.attrib["valueReference"],
                    type_name=type_element.tag,
                    description=variable_element.attrib.get("description"),
                    causality=variable_element.attrib.get("causality"),
                    variability=variable_element.attrib.get("variability"),
                    initial=variable_element.attrib.get("initial"),
                    declared_type=declared_type,
                    start=start,
                    type_attributes=type_attributes,
                )
            )
        return variables

    def _parse_model_structure(self, model_structure: ET.Element | None) -> Fmi2ModelStructure:
        if model_structure is None:
            return Fmi2ModelStructure()
        return Fmi2ModelStructure(
            outputs=self._parse_unknown_group(model_structure.find("Outputs")),
            derivatives=self._parse_unknown_group(model_structure.find("Derivatives")),
            initial_unknowns=self._parse_unknown_group(model_structure.find("InitialUnknowns")),
        )

    def _parse_unknown_group(self, element: ET.Element | None) -> list[Fmi2Unknown]:
        if element is None:
            return []
        return [
            Fmi2Unknown(
                index=unknown.attrib["index"],
                dependencies=unknown.attrib.get("dependencies"),
                dependencies_kind=unknown.attrib.get("dependenciesKind"),
            )
            for unknown in element.findall("Unknown")
        ]

    def _append_unknown_group(self, parent: ET.Element, tag: str, unknowns: list[Fmi2Unknown]) -> None:
        if not unknowns:
            return
        group = ET.SubElement(parent, tag)
        for unknown in unknowns:
            unknown_element = ET.SubElement(group, "Unknown")
            unknown_element.set("index", unknown.index)
            self._set_optional(unknown_element.attrib, "dependencies", unknown.dependencies)
            self._set_optional(unknown_element.attrib, "dependenciesKind", unknown.dependencies_kind)

    def _set_optional(self, attrs: dict[str, str], key: str, value: str | None) -> None:
        if value is not None:
            attrs[key] = value

    def _parse_float(self, value: str | None) -> float | None:
        if value is None:
            return None
        return float(value)

    def _format_float(self, value: float | None) -> str | None:
        if value is None:
            return None
        return str(value)
