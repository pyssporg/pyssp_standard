from __future__ import annotations

from xml.etree import ElementTree as ET

from pyssp_standard.standard.fmi3.model.model_description import (
    Fmi3CoSimulation,
    Fmi3DefaultExperiment,
    Fmi3ElementInfo,
    Fmi3InterfaceAttributes,
    Fmi3ModelDescriptionDocument,
    Fmi3ModelExchange,
    Fmi3ModelStructure,
    Fmi3ScheduledExecution,
    Fmi3ScalarVariable,
    Fmi3TypeDefinition,
    Fmi3Unit,
    Fmi3Unknown,
)


class Fmi3ModelDescriptionXmlCodec:
    def parse(self, xml_text: str) -> Fmi3ModelDescriptionDocument:
        root = ET.fromstring(xml_text)
        document = Fmi3ModelDescriptionDocument(
            root=Fmi3ElementInfo(tag=root.tag, attributes=dict(root.attrib)),
            fmi_version=root.attrib["fmiVersion"],
            model_name=root.attrib["modelName"],
            instantiation_token=root.attrib["instantiationToken"],
            description=root.attrib.get("description"),
            author=root.attrib.get("author"),
            version=root.attrib.get("version"),
            copyright=root.attrib.get("copyright"),
            license=root.attrib.get("license"),
            generation_tool=root.attrib.get("generationTool"),
            generation_date_and_time=root.attrib.get("generationDateAndTime"),
            variable_naming_convention=root.attrib.get("variableNamingConvention"),
        )
        document.unit_definitions = self._parse_units(root.find("UnitDefinitions"))
        document.type_definitions = self._parse_type_definitions(root.find("TypeDefinitions"))
        document.default_experiment = self._parse_default_experiment(root.find("DefaultExperiment"))
        document.variables = self._parse_variables(root.find("ModelVariables"))
        document.model_structure = self._parse_model_structure(root.find("ModelStructure"))
        document.model_exchange = self._parse_model_exchange(root.find("ModelExchange"))
        document.co_simulation = self._parse_co_simulation(root.find("CoSimulation"))
        document.scheduled_execution = self._parse_scheduled_execution(root.find("ScheduledExecution"))
        return document

    def serialize(self, document: Fmi3ModelDescriptionDocument) -> str:
        root_tag = document.root.tag if document.root is not None else "fmiModelDescription"
        root = ET.Element(root_tag)
        root_attributes: dict[str, str] = dict(document.root.attributes) if document.root is not None else {}
        root_attributes.update(
            {
                "fmiVersion": document.fmi_version,
                "modelName": document.model_name,
                "instantiationToken": document.instantiation_token,
            }
        )
        self._set_optional(root_attributes, "description", document.description)
        self._set_optional(root_attributes, "author", document.author)
        self._set_optional(root_attributes, "version", document.version)
        self._set_optional(root_attributes, "copyright", document.copyright)
        self._set_optional(root_attributes, "license", document.license)
        self._set_optional(root_attributes, "generationTool", document.generation_tool)
        self._set_optional(root_attributes, "generationDateAndTime", document.generation_date_and_time)
        self._set_optional(root_attributes, "variableNamingConvention", document.variable_naming_convention)
        for key, value in root_attributes.items():
            root.set(key, value)

        if document.model_exchange is not None:
            self._serialize_interface(root, "ModelExchange", document.model_exchange)
        if document.co_simulation is not None:
            self._serialize_interface(root, "CoSimulation", document.co_simulation)
        if document.scheduled_execution is not None:
            self._serialize_interface(root, "ScheduledExecution", document.scheduled_execution)

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
            self._set_optional(default_experiment.attrib, "stepSize", self._format_float(document.default_experiment.step_size))

        model_variables = ET.SubElement(root, "ModelVariables")
        for variable in document.variables:
            variable_element = ET.SubElement(model_variables, variable.type_name)
            variable_element.set("name", variable.name)
            variable_element.set("valueReference", str(variable.value_reference))
            self._set_optional(variable_element.attrib, "description", variable.description)
            self._set_optional(variable_element.attrib, "causality", variable.causality)
            self._set_optional(variable_element.attrib, "variability", variable.variability)
            self._set_optional(variable_element.attrib, "initial", variable.initial)
            self._set_optional(variable_element.attrib, "declaredType", variable.declared_type)
            self._set_optional(variable_element.attrib, "start", variable.start)
            for key, value in variable.type_attributes.items():
                variable_element.set(key, value)

        model_structure = ET.SubElement(root, "ModelStructure")
        self._append_unknown_group(model_structure, "Output", document.model_structure.outputs)
        self._append_unknown_group(model_structure, "ContinuousStateDerivative", document.model_structure.continuous_state_derivatives)
        self._append_unknown_group(model_structure, "ClockedState", document.model_structure.clocked_states)
        self._append_unknown_group(model_structure, "InitialUnknown", document.model_structure.initial_unknowns)
        self._append_unknown_group(model_structure, "EventIndicator", document.model_structure.event_indicators)

        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    # ------------------------------------------------------------------ #
    # Parse helpers
    # ------------------------------------------------------------------ #

    def _parse_units(self, units_element: ET.Element | None) -> list[Fmi3Unit]:
        if units_element is None:
            return []
        units: list[Fmi3Unit] = []
        for unit_element in units_element.findall("Unit"):
            base_unit_element = unit_element.find("BaseUnit")
            units.append(
                Fmi3Unit(
                    name=unit_element.attrib["name"],
                    base_unit=dict(base_unit_element.attrib) if base_unit_element is not None else {},
                )
            )
        return units

    def _parse_type_definitions(self, type_definitions: ET.Element | None) -> list[Fmi3TypeDefinition]:
        if type_definitions is None:
            return []
        definitions: list[Fmi3TypeDefinition] = []
        for simple_type in type_definitions.findall("SimpleType"):
            type_element = next(iter(simple_type), None)
            if type_element is None:
                continue
            definitions.append(
                Fmi3TypeDefinition(
                    name=simple_type.attrib["name"],
                    type_name=type_element.tag,
                    attributes=dict(type_element.attrib),
                    enumeration_items=[dict(item.attrib) for item in type_element.findall("Item")],
                )
            )
        return definitions

    def _parse_default_experiment(self, element: ET.Element | None) -> Fmi3DefaultExperiment | None:
        if element is None:
            return None
        return Fmi3DefaultExperiment(
            start_time=self._parse_float(element.attrib.get("startTime")),
            stop_time=self._parse_float(element.attrib.get("stopTime")),
            tolerance=self._parse_float(element.attrib.get("tolerance")),
            step_size=self._parse_float(element.attrib.get("stepSize")),
        )

    _FMI3_VARIABLE_TYPES: frozenset[str] = frozenset({
        "Float32", "Float64", "Int8", "UInt8", "Int16", "UInt16",
        "Int32", "UInt32", "Int64", "UInt64", "Boolean", "String",
        "Binary", "Enumeration", "Clock",
    })

    def _parse_variables(self, model_variables: ET.Element | None) -> list[Fmi3ScalarVariable]:
        if model_variables is None:
            return []
        variables: list[Fmi3ScalarVariable] = []
        for variable_element in model_variables:
            if variable_element.tag in self._FMI3_VARIABLE_TYPES:
                type_attributes = dict(variable_element.attrib)
                name = type_attributes.pop("name")
                value_reference = int(type_attributes.pop("valueReference"))
                description = type_attributes.pop("description", None)
                causality = type_attributes.pop("causality", None)
                variability = type_attributes.pop("variability", None)
                initial = type_attributes.pop("initial", None)
                declared_type = type_attributes.pop("declaredType", None)
                start = type_attributes.pop("start", None)
                variables.append(
                    Fmi3ScalarVariable(
                        name=name,
                        value_reference=value_reference,
                        type_name=variable_element.tag,
                        description=description,
                        causality=causality,
                        variability=variability,
                        initial=initial,
                        declared_type=declared_type,
                        start=start,
                        type_attributes=type_attributes,
                    )
                )
        return variables

    def _parse_model_structure(self, model_structure: ET.Element | None) -> Fmi3ModelStructure:
        if model_structure is None:
            return Fmi3ModelStructure()
        return Fmi3ModelStructure(
            outputs=self._parse_unknown_group(model_structure.find("Output")),
            continuous_state_derivatives=self._parse_unknown_group(model_structure.find("ContinuousStateDerivative")),
            clocked_states=self._parse_unknown_group(model_structure.find("ClockedState")),
            initial_unknowns=self._parse_unknown_group(model_structure.find("InitialUnknown")),
            event_indicators=self._parse_unknown_group(model_structure.find("EventIndicator")),
        )

    def _parse_unknown_group(self, element: ET.Element | None) -> list[Fmi3Unknown]:
        if element is None:
            return []
        result: list[Fmi3Unknown] = []
        for unknown in element:
            if unknown.tag != "Annotations":
                result.append(self._parse_unknown(unknown))
        return result

    def _parse_unknown(self, element: ET.Element) -> Fmi3Unknown:
        vr_text = element.attrib.get("valueReference")
        dependencies_text = element.attrib.get("dependencies")
        dependencies_kind_text = element.attrib.get("dependenciesKind")
        return Fmi3Unknown(
            value_reference=int(vr_text) if vr_text is not None else 0,
            dependencies=[int(v) for v in dependencies_text.split()] if dependencies_text else [],
            dependencies_kind=dependencies_kind_text.split() if dependencies_kind_text else [],
        )

    def _parse_interface_attributes(self, element: ET.Element) -> Fmi3InterfaceAttributes:
        return Fmi3InterfaceAttributes(
            model_identifier=element.attrib["modelIdentifier"],
            needs_execution_tool=self._parse_bool(element.attrib.get("needsExecutionTool", "false")),
            can_be_instantiated_only_once_per_process=self._parse_bool(
                element.attrib.get("canBeInstantiatedOnlyOncePerProcess", "false")
            ),
            can_get_and_set_fmu_state=self._parse_bool(element.attrib.get("canGetAndSetFMUState", "false")),
            can_serialize_fmu_state=self._parse_bool(element.attrib.get("canSerializeFMUState", "false")),
            provides_directional_derivatives=self._parse_bool(element.attrib.get("providesDirectionalDerivatives", "false")),
            provides_adjoint_derivatives=self._parse_bool(element.attrib.get("providesAdjointDerivatives", "false")),
            provides_per_element_dependencies=self._parse_bool(element.attrib.get("providesPerElementDependencies", "false")),
            extra_attributes={k: v for k, v in element.attrib.items() if k not in self._BASE_INTERFACE_ATTRS},
        )

    def _parse_model_exchange(self, element: ET.Element | None) -> Fmi3ModelExchange | None:
        if element is None:
            return None
        base = self._parse_interface_attributes(element)
        return Fmi3ModelExchange(
            model_identifier=base.model_identifier,
            needs_execution_tool=base.needs_execution_tool,
            can_be_instantiated_only_once_per_process=base.can_be_instantiated_only_once_per_process,
            can_get_and_set_fmu_state=base.can_get_and_set_fmu_state,
            can_serialize_fmu_state=base.can_serialize_fmu_state,
            provides_directional_derivatives=base.provides_directional_derivatives,
            provides_adjoint_derivatives=base.provides_adjoint_derivatives,
            provides_per_element_dependencies=base.provides_per_element_dependencies,
            extra_attributes=base.extra_attributes,
            needs_completed_integrator_step=self._parse_bool(element.attrib.get("needsCompletedIntegratorStep", "false")),
            provides_evaluate_discrete_states=self._parse_bool(element.attrib.get("providesEvaluateDiscreteStates", "false")),
        )

    def _parse_co_simulation(self, element: ET.Element | None) -> Fmi3CoSimulation | None:
        if element is None:
            return None
        base = self._parse_interface_attributes(element)
        return Fmi3CoSimulation(
            model_identifier=base.model_identifier,
            needs_execution_tool=base.needs_execution_tool,
            can_be_instantiated_only_once_per_process=base.can_be_instantiated_only_once_per_process,
            can_get_and_set_fmu_state=base.can_get_and_set_fmu_state,
            can_serialize_fmu_state=base.can_serialize_fmu_state,
            provides_directional_derivatives=base.provides_directional_derivatives,
            provides_adjoint_derivatives=base.provides_adjoint_derivatives,
            provides_per_element_dependencies=base.provides_per_element_dependencies,
            extra_attributes=base.extra_attributes,
            can_handle_variable_communication_step_size=self._parse_bool(
                element.attrib.get("canHandleVariableCommunicationStepSize", "false")
            ),
            fixed_internal_step_size=self._parse_float(element.attrib.get("fixedInternalStepSize")),
            max_output_derivative_order=int(element.attrib.get("maxOutputDerivativeOrder", "0")),
            recommended_intermediate_input_smoothness=int(element.attrib.get("recommendedIntermediateInputSmoothness", "0")),
            provides_intermediate_update=self._parse_bool(element.attrib.get("providesIntermediateUpdate", "false")),
            might_return_early_from_do_step=self._parse_bool(element.attrib.get("mightReturnEarlyFromDoStep", "false")),
            can_return_early_after_intermediate_update=self._parse_bool(
                element.attrib.get("canReturnEarlyAfterIntermediateUpdate", "false")
            ),
            has_event_mode=self._parse_bool(element.attrib.get("hasEventMode", "false")),
            provides_evaluate_discrete_states=self._parse_bool(element.attrib.get("providesEvaluateDiscreteStates", "false")),
        )

    def _parse_scheduled_execution(self, element: ET.Element | None) -> Fmi3ScheduledExecution | None:
        if element is None:
            return None
        base = self._parse_interface_attributes(element)
        return Fmi3ScheduledExecution(
            model_identifier=base.model_identifier,
            needs_execution_tool=base.needs_execution_tool,
            can_be_instantiated_only_once_per_process=base.can_be_instantiated_only_once_per_process,
            can_get_and_set_fmu_state=base.can_get_and_set_fmu_state,
            can_serialize_fmu_state=base.can_serialize_fmu_state,
            provides_directional_derivatives=base.provides_directional_derivatives,
            provides_adjoint_derivatives=base.provides_adjoint_derivatives,
            provides_per_element_dependencies=base.provides_per_element_dependencies,
            extra_attributes=base.extra_attributes,
        )

    # ------------------------------------------------------------------ #
    # Serialize helpers
    # ------------------------------------------------------------------ #

    _BASE_INTERFACE_ATTRS: frozenset[str] = frozenset({
        "modelIdentifier", "needsExecutionTool", "canBeInstantiatedOnlyOncePerProcess",
        "canGetAndSetFMUState", "canSerializeFMUState", "providesDirectionalDerivatives",
        "providesAdjointDerivatives", "providesPerElementDependencies",
    })

    def _serialize_interface(self, parent: ET.Element, tag: str, attrs: Fmi3InterfaceAttributes) -> None:
        element = ET.SubElement(parent, tag)
        element.set("modelIdentifier", attrs.model_identifier)
        self._set_optional_bool(element.attrib, "needsExecutionTool", attrs.needs_execution_tool)
        self._set_optional_bool(element.attrib, "canBeInstantiatedOnlyOncePerProcess", attrs.can_be_instantiated_only_once_per_process)
        self._set_optional_bool(element.attrib, "canGetAndSetFMUState", attrs.can_get_and_set_fmu_state)
        self._set_optional_bool(element.attrib, "canSerializeFMUState", attrs.can_serialize_fmu_state)
        self._set_optional_bool(element.attrib, "providesDirectionalDerivatives", attrs.provides_directional_derivatives)
        self._set_optional_bool(element.attrib, "providesAdjointDerivatives", attrs.provides_adjoint_derivatives)
        self._set_optional_bool(element.attrib, "providesPerElementDependencies", attrs.provides_per_element_dependencies)
        if isinstance(attrs, Fmi3ModelExchange):
            self._set_optional_bool(element.attrib, "needsCompletedIntegratorStep", attrs.needs_completed_integrator_step)
            self._set_optional_bool(element.attrib, "providesEvaluateDiscreteStates", attrs.provides_evaluate_discrete_states)
        if isinstance(attrs, Fmi3CoSimulation):
            self._set_optional_bool(element.attrib, "canHandleVariableCommunicationStepSize", attrs.can_handle_variable_communication_step_size)
            self._set_optional(element.attrib, "fixedInternalStepSize", self._format_float(attrs.fixed_internal_step_size))
            if attrs.max_output_derivative_order != 0:
                element.set("maxOutputDerivativeOrder", str(attrs.max_output_derivative_order))
            if attrs.recommended_intermediate_input_smoothness != 0:
                element.set("recommendedIntermediateInputSmoothness", str(attrs.recommended_intermediate_input_smoothness))
            self._set_optional_bool(element.attrib, "providesIntermediateUpdate", attrs.provides_intermediate_update)
            self._set_optional_bool(element.attrib, "mightReturnEarlyFromDoStep", attrs.might_return_early_from_do_step)
            self._set_optional_bool(element.attrib, "canReturnEarlyAfterIntermediateUpdate", attrs.can_return_early_after_intermediate_update)
            self._set_optional_bool(element.attrib, "hasEventMode", attrs.has_event_mode)
            self._set_optional_bool(element.attrib, "providesEvaluateDiscreteStates", attrs.provides_evaluate_discrete_states)
        for key, value in attrs.extra_attributes.items():
            element.set(key, value)

    def _append_unknown_group(self, parent: ET.Element, tag: str, unknowns: list[Fmi3Unknown]) -> None:
        if not unknowns:
            return
        group = ET.SubElement(parent, tag)
        for unknown in unknowns:
            unknown_element = ET.SubElement(group, "Unknown")
            unknown_element.set("valueReference", str(unknown.value_reference))
            if unknown.dependencies:
                unknown_element.set("dependencies", " ".join(str(v) for v in unknown.dependencies))
            if unknown.dependencies_kind:
                unknown_element.set("dependenciesKind", " ".join(unknown.dependencies_kind))

    def _set_optional(self, attrs: dict[str, str], key: str, value: str | None) -> None:
        if value is not None:
            attrs[key] = value

    def _set_optional_bool(self, attrs: dict[str, str], key: str, value: bool) -> None:
        if value:
            attrs[key] = "true"

    def _parse_float(self, value: str | None) -> float | None:
        if value is None:
            return None
        return float(value)

    def _format_float(self, value: float | None) -> str | None:
        if value is None:
            return None
        return str(value)

    def _parse_bool(self, value: str) -> bool:
        return value.strip().lower() in ("true", "1")