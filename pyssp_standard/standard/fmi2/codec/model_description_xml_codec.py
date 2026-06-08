from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.fmi2.model.model_description import (
    Fmi2DefaultExperiment,
    Fmi2ElementInfo,
    Fmi2InterfaceAttributes,
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
            description=root.attrib.get("description"),
            author=root.attrib.get("author"),
            version=root.attrib.get("version"),
            generation_tool=root.attrib.get("generationTool"),
            generation_date_and_time=root.attrib.get("generationDateAndTime"),
            variable_naming_convention=root.attrib.get("variableNamingConvention"),
            number_of_event_indicators=(
                int(root.attrib["numberOfEventIndicators"])
                if root.attrib.get("numberOfEventIndicators") is not None
                else None
            ),
            interface_type=interface_element.tag if interface_element is not None else None,
            capabilities=self._parse_interface_attributes(interface_element) if interface_element is not None else None,
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
        self._set_optional(root_attributes, "description", document.description)
        self._set_optional(root_attributes, "author", document.author)
        self._set_optional(root_attributes, "version", document.version)
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

        self._serialize_interface(root, document)

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
            variable_element.set("valueReference", str(variable.value_reference))
            self._set_optional(variable_element.attrib, "description", variable.description)
            self._set_optional(variable_element.attrib, "causality", variable.causality)
            self._set_optional(variable_element.attrib, "variability", variable.variability)
            self._set_optional(variable_element.attrib, "initial", variable.initial)

            type_element = ET.SubElement(variable_element, variable.type_name)
            type_attributes = dict(variable.type_attributes)
            self._set_optional(type_attributes, "declaredType", variable.declared_type)
            if variable.start is not None:
                if isinstance(variable.start, float) and variable.type_name in ("Integer", "Enumeration"):
                    type_attributes["start"] = str(int(variable.start))
                else:
                    type_attributes["start"] = str(variable.start)
            self._set_optional(type_attributes, "unit", variable.unit)
            for key, value in type_attributes.items():
                type_element.set(key, value)

        model_structure = ET.SubElement(root, "ModelStructure")
        self._append_unknown_group(model_structure, "Outputs", document.model_structure.outputs)
        self._append_unknown_group(model_structure, "Derivatives", document.model_structure.derivatives)
        self._append_unknown_group(model_structure, "InitialUnknowns", document.model_structure.initial_unknowns)

        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    def _parse_interface_attributes(self, element: ET.Element) -> Fmi2InterfaceAttributes:
        attribs = dict(element.attrib)
        model_identifier = attribs.pop("modelIdentifier", "")
        known_bools = {
            "canGetAndSetFMUstate": "can_get_and_set_fmu_state",
            "canSerializeFMUstate": "can_serialize_fmu_state",
            "providesDirectionalDerivative": "provides_directional_derivative",
            "needsExecutionTool": "needs_execution_tool",
            "completedIntegratorStepNotNeeded": "completed_integrator_step_not_needed",
            "canBeInstantiatedOnlyOncePerProcess": "can_be_instantiated_only_once_per_process",
            "canNotUseMemoryManagementFunctions": "can_not_use_memory_management_functions",
        }
        kwargs: dict[str, bool | str | dict] = {}
        for xml_key, py_key in known_bools.items():
            if xml_key in attribs:
                kwargs[py_key] = attribs.pop(xml_key).strip().lower() == "true"
        kwargs["extra_attributes"] = attribs
        return Fmi2InterfaceAttributes(
            model_identifier=model_identifier,
            can_get_and_set_fmu_state=kwargs.get("can_get_and_set_fmu_state", False),
            can_serialize_fmu_state=kwargs.get("can_serialize_fmu_state", False),
            provides_directional_derivative=kwargs.get("provides_directional_derivative", False),
            needs_execution_tool=kwargs.get("needs_execution_tool", False),
            completed_integrator_step_not_needed=kwargs.get("completed_integrator_step_not_needed", False),
            can_be_instantiated_only_once_per_process=kwargs.get("can_be_instantiated_only_once_per_process", False),
            can_not_use_memory_management_functions=kwargs.get("can_not_use_memory_management_functions", False),
            extra_attributes=kwargs.get("extra_attributes", {}),
        )

    def _serialize_interface(self, root: ET.Element, document: Fmi2ModelDescriptionDocument) -> None:
        if document.interface_type is None or document.capabilities is None:
            return
        interface_element = ET.SubElement(root, document.interface_type)
        caps = document.capabilities

        # Required
        interface_element.set("modelIdentifier", caps.model_identifier)

        # Known booleans — only write if True (FMI convention)
        bool_attributes: list[tuple[str, str]] = [
            ("canGetAndSetFMUstate", "can_get_and_set_fmu_state"),
            ("canSerializeFMUstate", "can_serialize_fmu_state"),
            ("providesDirectionalDerivative", "provides_directional_derivative"),
            ("needsExecutionTool", "needs_execution_tool"),
            ("completedIntegratorStepNotNeeded", "completed_integrator_step_not_needed"),
            ("canBeInstantiatedOnlyOncePerProcess", "can_be_instantiated_only_once_per_process"),
            ("canNotUseMemoryManagementFunctions", "can_not_use_memory_management_functions"),
        ]
        for xml_key, py_key in bool_attributes:
            if getattr(caps, py_key, False):
                interface_element.set(xml_key, "true")

        # Extra attributes
        for key, value in caps.extra_attributes.items():
            interface_element.set(key, value)

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
            raw_start = type_attributes.pop("start", None)
            unit = type_attributes.pop("unit", None)

            value_reference = int(variable_element.attrib["valueReference"])

            start: str | float | None = raw_start
            if raw_start is not None:
                if type_element.tag in ("Integer", "Enumeration"):
                    try:
                        start = int(raw_start)
                    except ValueError:
                        start = raw_start
                elif type_element.tag == "Real":
                    try:
                        start = float(raw_start)
                    except ValueError:
                        start = raw_start
                else:
                    start = raw_start

            variables.append(
                Fmi2ScalarVariable(
                    name=variable_element.attrib["name"],
                    value_reference=value_reference,
                    type_name=type_element.tag,
                    description=variable_element.attrib.get("description"),
                    causality=variable_element.attrib.get("causality"),
                    variability=variable_element.attrib.get("variability"),
                    initial=variable_element.attrib.get("initial"),
                    declared_type=declared_type,
                    start=start,
                    unit=unit,
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
                index=int(unknown.attrib["index"]),
                dependencies=self._parse_dependencies(unknown.attrib.get("dependencies")),
                dependencies_kind=self._parse_dependencies_kind(unknown.attrib.get("dependenciesKind")),
            )
            for unknown in element.findall("Unknown")
        ]

    def _parse_dependencies(self, raw: str | None) -> list[int]:
        if not raw:
            return []
        return [int(x) for x in raw.split()]

    def _parse_dependencies_kind(self, raw: str | None) -> list[str]:
        if not raw:
            return []
        return raw.split()

    def _append_unknown_group(self, parent: ET.Element, tag: str, unknowns: list[Fmi2Unknown]) -> None:
        if not unknowns:
            return
        group = ET.SubElement(parent, tag)
        for unknown in unknowns:
            unknown_element = ET.SubElement(group, "Unknown")
            unknown_element.set("index", str(unknown.index))
            if unknown.dependencies:
                unknown_element.set("dependencies", " ".join(str(d) for d in unknown.dependencies))
            if unknown.dependencies_kind:
                unknown_element.set("dependenciesKind", " ".join(unknown.dependencies_kind))

    def _set_optional(self, attrs: dict[str, str], key: str, value: str | None) -> None:
        if value is None:
            attrs.pop(key, None)
            return
        attrs[key] = value

    def _parse_float(self, value: str | None) -> float | None:
        if value is None:
            return None
        return float(value)

    def _format_float(self, value: float | None) -> str | None:
        if value is None:
            return None
        return str(value)
