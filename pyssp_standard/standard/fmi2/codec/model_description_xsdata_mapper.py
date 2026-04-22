from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum

from xsdata.models.datatype import XmlDateTime

from pyssp_standard.standard.fmi2.generated.model_description_generated_types import (
    Fmi2ScalarVariable,
    Fmi2ScalarVariableCausality,
    Fmi2ScalarVariableInitial,
    Fmi2ScalarVariableVariability,
    Fmi2SimpleType,
    Fmi2Unit,
    Fmi2VariableDependency,
    FmiModelDescription,
    FmiModelDescriptionVariableNamingConvention,
    UnknownValue,
)
from pyssp_standard.standard.fmi2.model.model_description import (
    Fmi2DefaultExperiment,
    Fmi2ElementInfo,
    Fmi2ModelDescriptionDocument,
    Fmi2ModelStructure,
    Fmi2ScalarVariable as DomainScalarVariable,
    Fmi2TypeDefinition,
    Fmi2Unit as DomainUnit,
    Fmi2Unknown,
)


class Fmi2ModelDescriptionXsdataMapper:
    def read_model_description(self, generated: FmiModelDescription) -> Fmi2ModelDescriptionDocument:
        interface_type, interface_attributes = self._read_interface(generated)
        root_attributes = {
            "fmiVersion": generated.fmi_version,
            "modelName": generated.model_name,
            "guid": generated.guid,
        }
        for key, value in (
            ("description", generated.description),
            ("author", generated.author),
            ("version", generated.version),
            ("copyright", generated.copyright),
            ("license", generated.license),
            ("generationTool", generated.generation_tool),
            (
                "generationDateAndTime",
                str(generated.generation_date_and_time) if generated.generation_date_and_time is not None else None,
            ),
            (
                "variableNamingConvention",
                generated.variable_naming_convention.value if generated.variable_naming_convention is not None else None,
            ),
            (
                "numberOfEventIndicators",
                str(generated.number_of_event_indicators) if generated.number_of_event_indicators is not None else None,
            ),
        ):
            if value is not None:
                root_attributes[key] = value

        return Fmi2ModelDescriptionDocument(
            root=Fmi2ElementInfo(tag="fmiModelDescription", attributes=root_attributes),
            fmi_version=generated.fmi_version,
            model_name=generated.model_name,
            guid=generated.guid,
            generation_tool=generated.generation_tool,
            generation_date_and_time=str(generated.generation_date_and_time)
            if generated.generation_date_and_time is not None
            else None,
            variable_naming_convention=generated.variable_naming_convention.value
            if generated.variable_naming_convention is not None
            else None,
            number_of_event_indicators=generated.number_of_event_indicators,
            interface_type=interface_type,
            interface_attributes=interface_attributes,
            unit_definitions=self._read_unit_definitions(generated.unit_definitions),
            type_definitions=self._read_type_definitions(generated.type_definitions),
            variables=self._read_variables(generated.model_variables),
            model_structure=self._read_model_structure(generated.model_structure),
            default_experiment=self._read_default_experiment(generated.default_experiment),
        )

    def write_model_description(self, document: Fmi2ModelDescriptionDocument) -> FmiModelDescription:
        generated = FmiModelDescription(
            model_name=document.model_name,
            guid=document.guid,
            model_variables=FmiModelDescription.ModelVariables(
                scalar_variable=[self._write_variable(variable) for variable in document.variables]
            ),
            model_structure=self._write_model_structure(document.model_structure),
            unit_definitions=self._write_unit_definitions(document.unit_definitions),
            type_definitions=self._write_type_definitions(document.type_definitions),
            default_experiment=self._write_default_experiment(document.default_experiment),
            description=document.root.attributes.get("description") if document.root else None,
            author=document.root.attributes.get("author") if document.root else None,
            version=document.root.attributes.get("version") if document.root else None,
            copyright=document.root.attributes.get("copyright") if document.root else None,
            license=document.root.attributes.get("license") if document.root else None,
            generation_tool=document.generation_tool,
            generation_date_and_time=XmlDateTime.from_string(document.generation_date_and_time)
            if document.generation_date_and_time
            else None,
            variable_naming_convention=FmiModelDescriptionVariableNamingConvention(
                document.variable_naming_convention or "flat"
            ),
            number_of_event_indicators=document.number_of_event_indicators,
        )
        self._write_interface(document, generated)
        return generated

    @staticmethod
    def _read_interface(generated: FmiModelDescription) -> tuple[str | None, dict[str, str]]:
        if generated.model_exchange:
            return "ModelExchange", _attribute_dict(generated.model_exchange[0])
        if generated.co_simulation:
            return "CoSimulation", _attribute_dict(generated.co_simulation[0])
        return None, {}

    @staticmethod
    def _write_interface(document: Fmi2ModelDescriptionDocument, generated: FmiModelDescription) -> None:
        attrs = dict(document.interface_attributes)
        if document.interface_type == "ModelExchange":
            generated.model_exchange.append(
                FmiModelDescription.ModelExchange(
                    model_identifier=attrs.pop("modelIdentifier", ""),
                    needs_execution_tool=_parse_bool(attrs.pop("needsExecutionTool", None), default=False),
                    completed_integrator_step_not_needed=_parse_bool(
                        attrs.pop("completedIntegratorStepNotNeeded", None), default=False
                    ),
                    can_be_instantiated_only_once_per_process=_parse_bool(
                        attrs.pop("canBeInstantiatedOnlyOncePerProcess", None),
                        default=False,
                    ),
                    can_not_use_memory_management_functions=_parse_bool(
                        attrs.pop("canNotUseMemoryManagementFunctions", None),
                        default=False,
                    ),
                    can_get_and_set_fmustate=_parse_bool(attrs.pop("canGetAndSetFMUstate", None), default=False),
                    can_serialize_fmustate=_parse_bool(attrs.pop("canSerializeFMUstate", None), default=False),
                    provides_directional_derivative=_parse_bool(
                        attrs.pop("providesDirectionalDerivative", None),
                        default=False,
                    ),
                )
            )
        elif document.interface_type == "CoSimulation":
            generated.co_simulation.append(
                FmiModelDescription.CoSimulation(
                    model_identifier=attrs.pop("modelIdentifier", ""),
                    needs_execution_tool=_parse_bool(attrs.pop("needsExecutionTool", None), default=False),
                    can_handle_variable_communication_step_size=_parse_bool(
                        attrs.pop("canHandleVariableCommunicationStepSize", None),
                        default=False,
                    ),
                    can_interpolate_inputs=_parse_bool(attrs.pop("canInterpolateInputs", None), default=False),
                    max_output_derivative_order=_parse_int(
                        attrs.pop("maxOutputDerivativeOrder", None),
                        default=0,
                    ),
                    can_run_asynchronuously=_parse_bool(attrs.pop("canRunAsynchronuously", None), default=False),
                    can_be_instantiated_only_once_per_process=_parse_bool(
                        attrs.pop("canBeInstantiatedOnlyOncePerProcess", None),
                        default=False,
                    ),
                    can_not_use_memory_management_functions=_parse_bool(
                        attrs.pop("canNotUseMemoryManagementFunctions", None),
                        default=False,
                    ),
                    can_get_and_set_fmustate=_parse_bool(attrs.pop("canGetAndSetFMUstate", None), default=False),
                    can_serialize_fmustate=_parse_bool(attrs.pop("canSerializeFMUstate", None), default=False),
                    provides_directional_derivative=_parse_bool(
                        attrs.pop("providesDirectionalDerivative", None),
                        default=False,
                    ),
                )
            )

    @staticmethod
    def _read_unit_definitions(
        unit_definitions: FmiModelDescription.UnitDefinitions | None,
    ) -> list[DomainUnit]:
        if unit_definitions is None:
            return []
        return [
            DomainUnit(
                name=unit.name,
                base_unit=_attribute_dict(unit.base_unit) if unit.base_unit is not None else {},
            )
            for unit in unit_definitions.unit
        ]

    @staticmethod
    def _write_unit_definitions(units: list[DomainUnit]) -> FmiModelDescription.UnitDefinitions | None:
        if not units:
            return None
        return FmiModelDescription.UnitDefinitions(
            unit=[
                Fmi2Unit(
                    name=unit.name,
                    base_unit=Fmi2Unit.BaseUnit(
                        kg=_parse_int(unit.base_unit.get("kg"), default=0),
                        m=_parse_int(unit.base_unit.get("m"), default=0),
                        s=_parse_int(unit.base_unit.get("s"), default=0),
                        a=_parse_int(unit.base_unit.get("A"), default=0),
                        k=_parse_int(unit.base_unit.get("K"), default=0),
                        mol=_parse_int(unit.base_unit.get("mol"), default=0),
                        cd=_parse_int(unit.base_unit.get("cd"), default=0),
                        rad=_parse_int(unit.base_unit.get("rad"), default=0),
                        factor=_parse_float(unit.base_unit.get("factor"), default=1.0),
                        offset=_parse_float(unit.base_unit.get("offset"), default=0.0),
                    )
                    if unit.base_unit
                    else None,
                )
                for unit in units
            ]
        )

    def _read_type_definitions(
        self,
        type_definitions: FmiModelDescription.TypeDefinitions | None,
    ) -> list[Fmi2TypeDefinition]:
        if type_definitions is None:
            return []
        definitions: list[Fmi2TypeDefinition] = []
        for simple_type in type_definitions.simple_type:
            type_name, attributes, items = self._read_simple_type(simple_type)
            definitions.append(
                Fmi2TypeDefinition(
                    name=simple_type.name,
                    type_name=type_name,
                    attributes=attributes,
                    enumeration_items=items,
                )
            )
        return definitions

    def _write_type_definitions(
        self,
        definitions: list[Fmi2TypeDefinition],
    ) -> FmiModelDescription.TypeDefinitions | None:
        if not definitions:
            return None
        return FmiModelDescription.TypeDefinitions(
            simple_type=[self._write_simple_type(definition) for definition in definitions]
        )

    def _read_simple_type(
        self,
        simple_type: Fmi2SimpleType,
    ) -> tuple[str, dict[str, str], list[dict[str, str]]]:
        if simple_type.real is not None:
            return "Real", _attribute_dict(simple_type.real), []
        if simple_type.integer is not None:
            return "Integer", _attribute_dict(simple_type.integer), []
        if simple_type.boolean is not None:
            return "Boolean", {}, []
        if simple_type.string is not None:
            return "String", {}, []
        if simple_type.enumeration is not None:
            return (
                "Enumeration",
                _attribute_dict(simple_type.enumeration, skip={"item"}),
                [_attribute_dict(item) for item in simple_type.enumeration.item],
            )
        raise ValueError(f"Unsupported FMI2 simple type '{simple_type.name}'")

    def _write_simple_type(self, definition: Fmi2TypeDefinition) -> Fmi2SimpleType:
        generated = Fmi2SimpleType(name=definition.name)
        attrs = definition.attributes
        if definition.type_name == "Real":
            generated.real = Fmi2SimpleType.Real(
                quantity=attrs.get("quantity"),
                unit=attrs.get("unit"),
                display_unit=attrs.get("displayUnit"),
                relative_quantity=_parse_bool(attrs.get("relativeQuantity"), default=False),
                min=_parse_float(attrs.get("min")),
                max=_parse_float(attrs.get("max")),
                nominal=_parse_float(attrs.get("nominal")),
                unbounded=_parse_bool(attrs.get("unbounded"), default=False),
            )
        elif definition.type_name == "Integer":
            generated.integer = Fmi2SimpleType.Integer(
                quantity=attrs.get("quantity"),
                min=_parse_int(attrs.get("min")),
                max=_parse_int(attrs.get("max")),
            )
        elif definition.type_name == "Boolean":
            generated.boolean = object()
        elif definition.type_name == "String":
            generated.string = object()
        elif definition.type_name == "Enumeration":
            generated.enumeration = Fmi2SimpleType.Enumeration(
                quantity=attrs.get("quantity"),
                item=[
                    Fmi2SimpleType.Enumeration.Item(
                        name=item.get("name", ""),
                        value=_parse_int(item.get("value"), default=0),
                        description=item.get("description"),
                    )
                    for item in definition.enumeration_items
                ],
            )
        else:
            raise ValueError(f"Unsupported FMI2 type definition '{definition.type_name}'")
        return generated

    def _read_variables(
        self,
        model_variables: FmiModelDescription.ModelVariables,
    ) -> list[DomainScalarVariable]:
        variables: list[DomainScalarVariable] = []
        for variable in model_variables.scalar_variable:
            type_name, declared_type, start, type_attributes = self._read_scalar_variable_type(variable)
            variables.append(
                DomainScalarVariable(
                    name=variable.name,
                    value_reference=str(variable.value_reference),
                    description=variable.description,
                    causality=variable.causality.value if variable.causality is not None else None,
                    variability=variable.variability.value if variable.variability is not None else None,
                    initial=variable.initial.value if variable.initial is not None else None,
                    type_name=type_name,
                    declared_type=declared_type,
                    start=start,
                    type_attributes=type_attributes,
                )
            )
        return variables

    def _write_variable(self, variable: DomainScalarVariable) -> Fmi2ScalarVariable:
        generated = Fmi2ScalarVariable(
            name=variable.name,
            value_reference=int(variable.value_reference),
            description=variable.description,
            causality=Fmi2ScalarVariableCausality(variable.causality) if variable.causality else Fmi2ScalarVariableCausality.LOCAL,
            variability=Fmi2ScalarVariableVariability(variable.variability)
            if variable.variability
            else Fmi2ScalarVariableVariability.CONTINUOUS,
            initial=Fmi2ScalarVariableInitial(variable.initial) if variable.initial else None,
        )
        attrs = variable.type_attributes
        if variable.type_name == "Real":
            generated.real = Fmi2ScalarVariable.Real(
                declared_type=variable.declared_type,
                quantity=attrs.get("quantity"),
                unit=attrs.get("unit"),
                display_unit=attrs.get("displayUnit"),
                relative_quantity=_parse_bool(attrs.get("relativeQuantity"), default=False),
                min=_parse_float(attrs.get("min")),
                max=_parse_float(attrs.get("max")),
                nominal=_parse_float(attrs.get("nominal")),
                unbounded=_parse_bool(attrs.get("unbounded"), default=False),
                start=_parse_float(variable.start),
                derivative=_parse_int(attrs.get("derivative")),
                reinit=_parse_bool(attrs.get("reinit"), default=False),
            )
        elif variable.type_name == "Integer":
            generated.integer = Fmi2ScalarVariable.Integer(
                declared_type=variable.declared_type,
                quantity=attrs.get("quantity"),
                min=_parse_int(attrs.get("min")),
                max=_parse_int(attrs.get("max")),
                start=_parse_int(variable.start),
            )
        elif variable.type_name == "Boolean":
            generated.boolean = Fmi2ScalarVariable.Boolean(
                declared_type=variable.declared_type,
                start=_parse_bool(variable.start),
            )
        elif variable.type_name == "String":
            generated.string = Fmi2ScalarVariable.String(
                declared_type=variable.declared_type,
                start=variable.start,
            )
        elif variable.type_name == "Enumeration":
            generated.enumeration = Fmi2ScalarVariable.Enumeration(
                declared_type=variable.declared_type or "",
                quantity=attrs.get("quantity"),
                min=_parse_int(attrs.get("min")),
                max=_parse_int(attrs.get("max")),
                start=_parse_int(variable.start),
            )
        else:
            raise ValueError(f"Unsupported FMI2 variable type '{variable.type_name}'")
        return generated

    def _read_scalar_variable_type(
        self,
        variable: Fmi2ScalarVariable,
    ) -> tuple[str, str | None, str | None, dict[str, str]]:
        if variable.real is not None:
            attrs = _attribute_dict(variable.real)
        elif variable.integer is not None:
            attrs = _attribute_dict(variable.integer)
        elif variable.boolean is not None:
            attrs = _attribute_dict(variable.boolean)
        elif variable.string is not None:
            attrs = _attribute_dict(variable.string)
        elif variable.enumeration is not None:
            attrs = _attribute_dict(variable.enumeration)
        else:
            raise ValueError(f"Unsupported FMI2 variable '{variable.name}'")

        if variable.real is not None:
            type_name = "Real"
        elif variable.integer is not None:
            type_name = "Integer"
        elif variable.boolean is not None:
            type_name = "Boolean"
        elif variable.string is not None:
            type_name = "String"
        else:
            type_name = "Enumeration"

        declared_type = attrs.pop("declaredType", None)
        start = attrs.pop("start", None)
        return type_name, declared_type, start, attrs

    @staticmethod
    def _read_model_structure(model_structure: FmiModelDescription.ModelStructure) -> Fmi2ModelStructure:
        return Fmi2ModelStructure(
            outputs=_read_unknown_list(model_structure.outputs.unknown) if model_structure.outputs is not None else [],
            derivatives=_read_unknown_list(model_structure.derivatives.unknown)
            if model_structure.derivatives is not None
            else [],
            initial_unknowns=_read_unknown_list(model_structure.initial_unknowns.unknown)
            if model_structure.initial_unknowns is not None
            else [],
        )

    @staticmethod
    def _write_model_structure(model_structure: Fmi2ModelStructure) -> FmiModelDescription.ModelStructure:
        return FmiModelDescription.ModelStructure(
            outputs=Fmi2VariableDependency(unknown=[_write_unknown(unknown, Fmi2VariableDependency.Unknown) for unknown in model_structure.outputs])
            if model_structure.outputs
            else None,
            derivatives=Fmi2VariableDependency(
                unknown=[_write_unknown(unknown, Fmi2VariableDependency.Unknown) for unknown in model_structure.derivatives]
            )
            if model_structure.derivatives
            else None,
            initial_unknowns=FmiModelDescription.ModelStructure.InitialUnknowns(
                unknown=[
                    _write_unknown(unknown, FmiModelDescription.ModelStructure.InitialUnknowns.Unknown)
                    for unknown in model_structure.initial_unknowns
                ]
            )
            if model_structure.initial_unknowns
            else None,
        )

    @staticmethod
    def _read_default_experiment(
        default_experiment: FmiModelDescription.DefaultExperiment | None,
    ) -> Fmi2DefaultExperiment | None:
        if default_experiment is None:
            return None
        return Fmi2DefaultExperiment(
            start_time=default_experiment.start_time,
            stop_time=default_experiment.stop_time,
            tolerance=default_experiment.tolerance,
        )

    @staticmethod
    def _write_default_experiment(
        default_experiment: Fmi2DefaultExperiment | None,
    ) -> FmiModelDescription.DefaultExperiment | None:
        if default_experiment is None:
            return None
        return FmiModelDescription.DefaultExperiment(
            start_time=default_experiment.start_time,
            stop_time=default_experiment.stop_time,
            tolerance=default_experiment.tolerance,
        )


def _attribute_dict(value: object, skip: set[str] | None = None) -> dict[str, str]:
    skip = skip or set()
    if value is None or not is_dataclass(value):
        return {}
    result: dict[str, str] = {}
    for field in fields(value):
        if field.name in skip:
            continue
        metadata_type = field.metadata.get("type")
        if metadata_type != "Attribute":
            continue
        raw = getattr(value, field.name)
        if raw is None:
            continue
        name = field.metadata.get("name", field.name)
        result[name] = _stringify(raw)
    return result


def _stringify(value: object) -> str:
    if isinstance(value, Enum):
        return value.value
    return str(value)


def _read_unknown_list(unknowns: list[object]) -> list[Fmi2Unknown]:
    result: list[Fmi2Unknown] = []
    for unknown in unknowns:
        dependencies = " ".join(str(value) for value in unknown.dependencies) if unknown.dependencies else None
        dependencies_kind = " ".join(value.value for value in unknown.dependencies_kind) if unknown.dependencies_kind else None
        result.append(
            Fmi2Unknown(
                index=str(unknown.index),
                dependencies=dependencies,
                dependencies_kind=dependencies_kind,
            )
        )
    return result


def _write_unknown(unknown: Fmi2Unknown, target_type):
    return target_type(
        index=int(unknown.index),
        dependencies=[int(value) for value in unknown.dependencies.split()] if unknown.dependencies else [],
        dependencies_kind=[UnknownValue(value) for value in unknown.dependencies_kind.split()]
        if unknown.dependencies_kind
        else [],
    )


def _parse_bool(value: str | None, default: bool | None = None) -> bool | None:
    if value is None:
        return default
    return value.lower() in {"true", "1"}


def _parse_int(value: str | None, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    return int(value)


def _parse_float(value: str | None, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    return float(value)
