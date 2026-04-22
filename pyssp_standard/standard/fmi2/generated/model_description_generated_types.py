from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xsdata.models.datatype import XmlDateTime


class UnknownValue(Enum):
    DEPENDENT = "dependent"
    CONSTANT = "constant"
    FIXED = "fixed"
    TUNABLE = "tunable"
    DISCRETE = "discrete"


@dataclass(kw_only=True)
class Fmi2Annotation:
    """
    :ivar tool: Tool specific annotation (ignored by other tools).
    """

    class Meta:
        name = "fmi2Annotation"

    tool: list[Fmi2Annotation.Tool] = field(
        default_factory=list,
        metadata={
            "name": "Tool",
            "type": "Element",
            "min_occurs": 1,
        },
    )

    @dataclass(kw_only=True)
    class Tool:
        """
        :ivar any_element:
        :ivar name: Name of tool that can interpret the annotation.
            "name" must be unique with respect to all other elements of
            the VendorAnnotation list.
        """

        any_element: None | object = field(
            default=None,
            metadata={
                "type": "Wildcard",
                "namespace": "##any",
            },
        )
        name: str = field(
            metadata={
                "type": "Attribute",
            }
        )


class Fmi2ScalarVariableCausality(Enum):
    PARAMETER = "parameter"
    CALCULATED_PARAMETER = "calculatedParameter"
    INPUT = "input"
    OUTPUT = "output"
    LOCAL = "local"
    INDEPENDENT = "independent"


class Fmi2ScalarVariableInitial(Enum):
    EXACT = "exact"
    APPROX = "approx"
    CALCULATED = "calculated"


class Fmi2ScalarVariableVariability(Enum):
    CONSTANT = "constant"
    FIXED = "fixed"
    TUNABLE = "tunable"
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"


@dataclass(kw_only=True)
class Fmi2SimpleType:
    """
    Type attributes of a scalar variable.

    :ivar real:
    :ivar integer:
    :ivar boolean:
    :ivar string:
    :ivar enumeration:
    :ivar name: Name of SimpleType element. "name" must be unique with
        respect to all other elements of the TypeDefinitions list.
        Furthermore,  "name" of a SimpleType must be different to all
        "name"s of ScalarVariable.
    :ivar description: Description of the SimpleType
    """

    class Meta:
        name = "fmi2SimpleType"

    real: None | Fmi2SimpleType.Real = field(
        default=None,
        metadata={
            "name": "Real",
            "type": "Element",
        },
    )
    integer: None | Fmi2SimpleType.Integer = field(
        default=None,
        metadata={
            "name": "Integer",
            "type": "Element",
        },
    )
    boolean: None | object = field(
        default=None,
        metadata={
            "name": "Boolean",
            "type": "Element",
        },
    )
    string: None | object = field(
        default=None,
        metadata={
            "name": "String",
            "type": "Element",
        },
    )
    enumeration: None | Fmi2SimpleType.Enumeration = field(
        default=None,
        metadata={
            "name": "Enumeration",
            "type": "Element",
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    description: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

    @dataclass(kw_only=True)
    class Real:
        """
        :ivar quantity:
        :ivar unit:
        :ivar display_unit: Default display unit, provided the
            conversion of values in "unit" to values in "displayUnit" is
            defined in UnitDefinitions / Unit / DisplayUnit.
        :ivar relative_quantity: If relativeQuantity=true, offset for
            displayUnit must be ignored.
        :ivar min:
        :ivar max: max &gt;= min required
        :ivar nominal: nominal &gt; 0.0 required
        :ivar unbounded: Set to true, e.g., for crank angle. If true and
            variable is a state, relative tolerance should be zero on
            this variable.
        """

        quantity: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        unit: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        display_unit: None | str = field(
            default=None,
            metadata={
                "name": "displayUnit",
                "type": "Attribute",
            },
        )
        relative_quantity: bool = field(
            default=False,
            metadata={
                "name": "relativeQuantity",
                "type": "Attribute",
            },
        )
        min: None | float = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        max: None | float = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        nominal: None | float = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        unbounded: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Integer:
        """
        :ivar quantity:
        :ivar min:
        :ivar max: max &gt;= min required
        """

        quantity: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        min: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        max: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Enumeration:
        item: list[Fmi2SimpleType.Enumeration.Item] = field(
            default_factory=list,
            metadata={
                "name": "Item",
                "type": "Element",
                "min_occurs": 1,
            },
        )
        quantity: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

        @dataclass(kw_only=True)
        class Item:
            """
            :ivar name:
            :ivar value: Must be a unique number in the same enumeration
            :ivar description:
            """

            name: str = field(
                metadata={
                    "type": "Attribute",
                }
            )
            value: int = field(
                metadata={
                    "type": "Attribute",
                }
            )
            description: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )


@dataclass(kw_only=True)
class Fmi2Unit:
    """
    Unit definition (with respect to SI base units) and default display
    units.

    :ivar base_unit: BaseUnit_value = factor*Unit_value + offset
    :ivar display_unit: DisplayUnit_value = factor*Unit_value + offset
    :ivar name: Name of Unit element, e.g. "N.m", "Nm",  "%/s". "name"
        must be unique will respect to all other elements of the
        UnitDefinitions list. The variable values of fmi2SetXXX and
        fmi2GetXXX are with respect to this unit.
    """

    class Meta:
        name = "fmi2Unit"

    base_unit: None | Fmi2Unit.BaseUnit = field(
        default=None,
        metadata={
            "name": "BaseUnit",
            "type": "Element",
        },
    )
    display_unit: list[Fmi2Unit.DisplayUnit] = field(
        default_factory=list,
        metadata={
            "name": "DisplayUnit",
            "type": "Element",
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )

    @dataclass(kw_only=True)
    class BaseUnit:
        """
        :ivar kg: Exponent of SI base unit "kg"
        :ivar m: Exponent of SI base unit "m"
        :ivar s: Exponent of SI base unit "s"
        :ivar a: Exponent of SI base unit "A"
        :ivar k: Exponent of SI base unit "K"
        :ivar mol: Exponent of SI base unit "mol"
        :ivar cd: Exponent of SI base unit "cd"
        :ivar rad: Exponent of SI derived unit "rad"
        :ivar factor:
        :ivar offset:
        """

        kg: int = field(
            default=0,
            metadata={
                "type": "Attribute",
            },
        )
        m: int = field(
            default=0,
            metadata={
                "type": "Attribute",
            },
        )
        s: int = field(
            default=0,
            metadata={
                "type": "Attribute",
            },
        )
        a: int = field(
            default=0,
            metadata={
                "name": "A",
                "type": "Attribute",
            },
        )
        k: int = field(
            default=0,
            metadata={
                "name": "K",
                "type": "Attribute",
            },
        )
        mol: int = field(
            default=0,
            metadata={
                "type": "Attribute",
            },
        )
        cd: int = field(
            default=0,
            metadata={
                "type": "Attribute",
            },
        )
        rad: int = field(
            default=0,
            metadata={
                "type": "Attribute",
            },
        )
        factor: float = field(
            default=1.0,
            metadata={
                "type": "Attribute",
            },
        )
        offset: float = field(
            default=0.0,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class DisplayUnit:
        """
        :ivar name: Name of DisplayUnit element, e.g. <Unit xmlns=""
            name="rad"/>, <DisplayUnit xmlns="" name="deg"
            factor="57.29..."/>. "name" must be unique with respect to
            all other "names" of the DisplayUnit definitions of the same
            Unit (different Unit elements may have the same DisplayUnit
            names).
        :ivar factor:
        :ivar offset:
        """

        name: str = field(
            metadata={
                "type": "Attribute",
            }
        )
        factor: float = field(
            default=1.0,
            metadata={
                "type": "Attribute",
            },
        )
        offset: float = field(
            default=0.0,
            metadata={
                "type": "Attribute",
            },
        )


class FmiModelDescriptionVariableNamingConvention(Enum):
    FLAT = "flat"
    STRUCTURED = "structured"


@dataclass(kw_only=True)
class Fmi2ScalarVariable:
    """
    Properties of a scalar variable.

    :ivar real:
    :ivar integer:
    :ivar boolean:
    :ivar string:
    :ivar enumeration:
    :ivar annotations: Additional data of the scalar variable, e.g., for
        the dialog menu or the graphical layout
    :ivar name: Identifier of variable, e.g. "a.b.mod[3,4].'#123'.c".
        "name" must be unique with respect to all other elements of the
        ModelVariables list
    :ivar value_reference: Identifier for variable value in FMI2
        function calls (not necessarily unique with respect to all
        variables)
    :ivar description:
    :ivar causality: parameter: independent parameter
        calculatedParameter: calculated parameter input/output: can be
        used in connections local: variable calculated from other
        variables independent: independent variable (usually time)
    :ivar variability: constant: value never changes fixed: value fixed
        after initialization tunable: value constant between external
        events discrete: value constant between internal events
        continuous: no restriction on value changes
    :ivar initial: exact: initialized with start value approx: iteration
        variable that starts with start value calculated: calculated
        from other variables. If not provided, initial is deduced from
        causality and variability (details see specification)
    :ivar can_handle_multiple_set_per_time_instant: Only for
        ModelExchange and only for variables with variability = "input":
        If present with value = false, then only one fmi2SetXXX call is
        allowed at one super dense time instant. In other words, this
        input is not allowed to appear in an algebraic loop.
    """

    class Meta:
        name = "fmi2ScalarVariable"

    real: None | Fmi2ScalarVariable.Real = field(
        default=None,
        metadata={
            "name": "Real",
            "type": "Element",
        },
    )
    integer: None | Fmi2ScalarVariable.Integer = field(
        default=None,
        metadata={
            "name": "Integer",
            "type": "Element",
        },
    )
    boolean: None | Fmi2ScalarVariable.Boolean = field(
        default=None,
        metadata={
            "name": "Boolean",
            "type": "Element",
        },
    )
    string: None | Fmi2ScalarVariable.String = field(
        default=None,
        metadata={
            "name": "String",
            "type": "Element",
        },
    )
    enumeration: None | Fmi2ScalarVariable.Enumeration = field(
        default=None,
        metadata={
            "name": "Enumeration",
            "type": "Element",
        },
    )
    annotations: None | Fmi2Annotation = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    value_reference: int = field(
        metadata={
            "name": "valueReference",
            "type": "Attribute",
        }
    )
    description: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    causality: Fmi2ScalarVariableCausality = field(
        default=Fmi2ScalarVariableCausality.LOCAL,
        metadata={
            "type": "Attribute",
        },
    )
    variability: Fmi2ScalarVariableVariability = field(
        default=Fmi2ScalarVariableVariability.CONTINUOUS,
        metadata={
            "type": "Attribute",
        },
    )
    initial: None | Fmi2ScalarVariableInitial = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    can_handle_multiple_set_per_time_instant: None | bool = field(
        default=None,
        metadata={
            "name": "canHandleMultipleSetPerTimeInstant",
            "type": "Attribute",
        },
    )

    @dataclass(kw_only=True)
    class Real:
        """
        :ivar declared_type: If present, name of type defined with
            TypeDefinitions / SimpleType providing defaults.
        :ivar quantity:
        :ivar unit:
        :ivar display_unit: Default display unit, provided the
            conversion of values in "unit" to values in "displayUnit" is
            defined in UnitDefinitions / Unit / DisplayUnit.
        :ivar relative_quantity: If relativeQuantity=true, offset for
            displayUnit must be ignored.
        :ivar min:
        :ivar max: max &gt;= min required
        :ivar nominal: nominal &gt; 0.0 required
        :ivar unbounded: Set to true, e.g., for crank angle. If true and
            variable is a state, relative tolerance should be zero on
            this variable.
        :ivar start: Value before initialization, if initial=exact or
            approx. max &gt;= start &gt;= min required
        :ivar derivative: If present, this variable is the derivative of
            variable with ScalarVariable index "derivative".
        :ivar reinit: Only for ModelExchange and if variable is a
            continuous-time state: If true, state can be reinitialized
            at an event by the FMU If false, state will never be
            reinitialized at an event by the FMU
        """

        declared_type: None | str = field(
            default=None,
            metadata={
                "name": "declaredType",
                "type": "Attribute",
            },
        )
        quantity: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        unit: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        display_unit: None | str = field(
            default=None,
            metadata={
                "name": "displayUnit",
                "type": "Attribute",
            },
        )
        relative_quantity: bool = field(
            default=False,
            metadata={
                "name": "relativeQuantity",
                "type": "Attribute",
            },
        )
        min: None | float = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        max: None | float = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        nominal: None | float = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        unbounded: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
            },
        )
        start: None | float = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        derivative: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        reinit: bool = field(
            default=False,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Integer:
        """
        :ivar declared_type: If present, name of type defined with
            TypeDefinitions / SimpleType providing defaults.
        :ivar quantity:
        :ivar min:
        :ivar max: max &gt;= min required
        :ivar start: Value before initialization, if initial=exact or
            approx. max &gt;= start &gt;= min required
        """

        declared_type: None | str = field(
            default=None,
            metadata={
                "name": "declaredType",
                "type": "Attribute",
            },
        )
        quantity: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        min: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        max: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        start: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Boolean:
        """
        :ivar declared_type: If present, name of type defined with
            TypeDefinitions / SimpleType providing defaults.
        :ivar start: Value before initialization, if initial=exact or
            approx
        """

        declared_type: None | str = field(
            default=None,
            metadata={
                "name": "declaredType",
                "type": "Attribute",
            },
        )
        start: None | bool = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class String:
        """
        :ivar declared_type: If present, name of type defined with
            TypeDefinitions / SimpleType providing defaults.
        :ivar start: Value before initialization, if initial=exact or
            approx
        """

        declared_type: None | str = field(
            default=None,
            metadata={
                "name": "declaredType",
                "type": "Attribute",
            },
        )
        start: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Enumeration:
        """
        :ivar declared_type: Name of type defined with TypeDefinitions /
            SimpleType
        :ivar quantity:
        :ivar min:
        :ivar max: max &gt;= min required
        :ivar start: Value before initialization, if initial=exact or
            approx. max &gt;= start &gt;= min required
        """

        declared_type: str = field(
            metadata={
                "name": "declaredType",
                "type": "Attribute",
            }
        )
        quantity: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        min: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        max: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        start: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )


@dataclass(kw_only=True)
class Fmi2VariableDependency:
    """
    :ivar unknown: Dependency of scalar Unknown from Knowns in
        Continuous-Time and Event Mode (ModelExchange), and at
        Communication Points (CoSimulation): Unknown=f(Known_1, Known_2,
        ...). The Knowns are "inputs", "continuous states" and
        "independent variable" (usually time)".
    """

    class Meta:
        name = "fmi2VariableDependency"

    unknown: list[Fmi2VariableDependency.Unknown] = field(
        default_factory=list,
        metadata={
            "name": "Unknown",
            "type": "Element",
            "min_occurs": 1,
        },
    )

    @dataclass(kw_only=True)
    class Unknown:
        """
        :ivar index: ScalarVariable index of Unknown
        :ivar dependencies: Defines the dependency of the Unknown
            (directly or indirectly via auxiliary variables) on the
            Knowns in Continuous-Time and Event Mode (ModelExchange) and
            at Communication Points (CoSimulation). If not present, it
            must be assumed that the Unknown depends on all Knowns. If
            present as empty list, the Unknown depends on none of the
            Knowns. Otherwise the Unknown depends on the Knowns defined
            by the given ScalarVariable indices. The indices are ordered
            according to size, starting with the smallest index.
        :ivar dependencies_kind: If not present, it must be assumed that
            the Unknown depends on the Knowns without a particular
            structure. Otherwise, the corresponding Known v enters the
            equation as: = "dependent": no particular structure, f(v) =
            "constant"   : constant factor, c*v (only for Real
            variablse) = "fixed"        : fixed factor, p*v (only for
            Real variables) = "tunable"    : tunable factor, p*v (only
            for Real variables) = "discrete"    : discrete factor, d*v
            (only for Real variables) If "dependenciesKind" is present,
            "dependencies" must be present and must have the same number
            of list elements.
        """

        index: int = field(
            metadata={
                "type": "Attribute",
            }
        )
        dependencies: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )
        dependencies_kind: list[UnknownValue] = field(
            default_factory=list,
            metadata={
                "name": "dependenciesKind",
                "type": "Attribute",
                "tokens": True,
            },
        )


@dataclass(kw_only=True)
class FmiModelDescription:
    """
    :ivar model_exchange: The FMU includes a model or the communication
        to a tool that provides a model. The environment provides the
        simulation engine for the model.
    :ivar co_simulation: The FMU includes a model and the simulation
        engine, or the communication to a tool that provides this. The
        environment provides the master algorithm for the Co-Simulation
        coupling.
    :ivar unit_definitions:
    :ivar type_definitions:
    :ivar log_categories: Log categories available in FMU
    :ivar default_experiment:
    :ivar vendor_annotations: Tool specific data (ignored by other
        tools)
    :ivar model_variables: Ordered list of all variables (first
        definition has index = 1).
    :ivar model_structure: Ordered lists of outputs, exposed state
        derivatives, and the initial unknowns. Optionally, the
        functional dependency of these variables can be defined.
    :ivar fmi_version: Version of FMI (Clarification for FMI 2.0.2: for
        FMI 2.0.x revisions fmiVersion is defined as "2.0").
    :ivar model_name: Class name of FMU, e.g. "A.B.C" (several FMU
        instances are possible)
    :ivar guid: Fingerprint of xml-file content to verify that xml-file
        and C-functions are compatible to each other
    :ivar description:
    :ivar author:
    :ivar version: Version of FMU, e.g., "1.4.1"
    :ivar copyright: Information on intellectual property copyright for
        this FMU, such as “© MyCompany 2011“
    :ivar license: Information on intellectual property licensing for
        this FMU, such as “BSD license”, "Proprietary", or "Public
        Domain"
    :ivar generation_tool:
    :ivar generation_date_and_time:
    :ivar variable_naming_convention:
    :ivar number_of_event_indicators:
    """

    class Meta:
        name = "fmiModelDescription"

    model_exchange: list[FmiModelDescription.ModelExchange] = field(
        default_factory=list,
        metadata={
            "name": "ModelExchange",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    co_simulation: list[FmiModelDescription.CoSimulation] = field(
        default_factory=list,
        metadata={
            "name": "CoSimulation",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    unit_definitions: None | FmiModelDescription.UnitDefinitions = field(
        default=None,
        metadata={
            "name": "UnitDefinitions",
            "type": "Element",
        },
    )
    type_definitions: None | FmiModelDescription.TypeDefinitions = field(
        default=None,
        metadata={
            "name": "TypeDefinitions",
            "type": "Element",
        },
    )
    log_categories: None | FmiModelDescription.LogCategories = field(
        default=None,
        metadata={
            "name": "LogCategories",
            "type": "Element",
        },
    )
    default_experiment: None | FmiModelDescription.DefaultExperiment = field(
        default=None,
        metadata={
            "name": "DefaultExperiment",
            "type": "Element",
        },
    )
    vendor_annotations: None | Fmi2Annotation = field(
        default=None,
        metadata={
            "name": "VendorAnnotations",
            "type": "Element",
        },
    )
    model_variables: FmiModelDescription.ModelVariables = field(
        metadata={
            "name": "ModelVariables",
            "type": "Element",
        }
    )
    model_structure: FmiModelDescription.ModelStructure = field(
        metadata={
            "name": "ModelStructure",
            "type": "Element",
        }
    )
    fmi_version: str = field(
        init=False,
        default="2.0",
        metadata={
            "name": "fmiVersion",
            "type": "Attribute",
            "required": True,
        },
    )
    model_name: str = field(
        metadata={
            "name": "modelName",
            "type": "Attribute",
        }
    )
    guid: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    description: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    author: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    version: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    copyright: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    license: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    generation_tool: None | str = field(
        default=None,
        metadata={
            "name": "generationTool",
            "type": "Attribute",
        },
    )
    generation_date_and_time: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "generationDateAndTime",
            "type": "Attribute",
        },
    )
    variable_naming_convention: FmiModelDescriptionVariableNamingConvention = (
        field(
            default=FmiModelDescriptionVariableNamingConvention.FLAT,
            metadata={
                "name": "variableNamingConvention",
                "type": "Attribute",
            },
        )
    )
    number_of_event_indicators: None | int = field(
        default=None,
        metadata={
            "name": "numberOfEventIndicators",
            "type": "Attribute",
        },
    )

    @dataclass(kw_only=True)
    class UnitDefinitions:
        unit: list[Fmi2Unit] = field(
            default_factory=list,
            metadata={
                "name": "Unit",
                "type": "Element",
                "min_occurs": 1,
            },
        )

    @dataclass(kw_only=True)
    class TypeDefinitions:
        simple_type: list[Fmi2SimpleType] = field(
            default_factory=list,
            metadata={
                "name": "SimpleType",
                "type": "Element",
                "min_occurs": 1,
            },
        )

    @dataclass(kw_only=True)
    class LogCategories:
        category: list[FmiModelDescription.LogCategories.Category] = field(
            default_factory=list,
            metadata={
                "name": "Category",
                "type": "Element",
                "min_occurs": 1,
            },
        )

        @dataclass(kw_only=True)
        class Category:
            """
            :ivar name: Name of Category element. "name" must be unique
                with respect to all other elements of the LogCategories
                list. Standardized names: "logEvents",
                "logSingularLinearSystems", "logNonlinearSystems",
                "logDynamicStateSelection", "logStatusWarning",
                "logStatusDiscard", "logStatusError", "logStatusFatal",
                "logStatusPending", "logAll"
            :ivar description: Description of the log category
            """

            name: str = field(
                metadata={
                    "type": "Attribute",
                }
            )
            description: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )

    @dataclass(kw_only=True)
    class DefaultExperiment:
        """
        :ivar start_time: Default start time of simulation
        :ivar stop_time: Default stop time of simulation
        :ivar tolerance: Default relative integration tolerance
        :ivar step_size: ModelExchange: Default step size for fixed step
            integrators. CoSimulation: Preferred communicationStepSize.
        """

        start_time: None | float = field(
            default=None,
            metadata={
                "name": "startTime",
                "type": "Attribute",
            },
        )
        stop_time: None | float = field(
            default=None,
            metadata={
                "name": "stopTime",
                "type": "Attribute",
            },
        )
        tolerance: None | float = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        step_size: None | float = field(
            default=None,
            metadata={
                "name": "stepSize",
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class ModelVariables:
        scalar_variable: list[Fmi2ScalarVariable] = field(
            default_factory=list,
            metadata={
                "name": "ScalarVariable",
                "type": "Element",
                "min_occurs": 1,
            },
        )

    @dataclass(kw_only=True)
    class ModelStructure:
        """
        :ivar outputs: Ordered list of all outputs. Exactly all
            variables with causality="output" must be in this list. The
            dependency definition holds for Continuous-Time and for
            Event Mode (ModelExchange) and for Communication Points
            (CoSimulation).
        :ivar derivatives: Ordered list of all exposed state derivatives
            (and therefore implicitely associated continuous-time
            states). Exactly all state derivatives of a ModelExchange
            FMU must be in this list. A CoSimulation FMU need not expose
            its state derivatives. If a model has dynamic state
            selection, introduce dummy state variables. The dependency
            definition holds for Continuous-Time and for Event Mode
            (ModelExchange) and for Communication Points (CoSimulation).
        :ivar initial_unknowns: Ordered list of all exposed Unknowns in
            Initialization Mode. This list consists of all variables
            with (1) causality = "output" and (initial="approx" or
            calculated"), (2) causality = "calculatedParameter", and (3)
            all continuous-time states and all state derivatives
            (defined with element Derivatives from ModelStructure)with
            initial=("approx" or "calculated"). The resulting list is
            not allowed to have duplicates (e.g. if a state is also an
            output, it is included only once in the list). The Unknowns
            in this list must be ordered according to their
            ScalarVariable index (e.g. if for two variables A and B the
            ScalarVariable index of A is less than the index of B, then
            A must appear before B in InitialUnknowns).
        """

        outputs: None | Fmi2VariableDependency = field(
            default=None,
            metadata={
                "name": "Outputs",
                "type": "Element",
            },
        )
        derivatives: None | Fmi2VariableDependency = field(
            default=None,
            metadata={
                "name": "Derivatives",
                "type": "Element",
            },
        )
        initial_unknowns: (
            None | FmiModelDescription.ModelStructure.InitialUnknowns
        ) = field(
            default=None,
            metadata={
                "name": "InitialUnknowns",
                "type": "Element",
            },
        )

        @dataclass(kw_only=True)
        class InitialUnknowns:
            """
            :ivar unknown: Dependency of scalar Unknown from Knowns:
                Unknown=f(Known_1, Known_2, ...). The Knowns are
                "inputs", "variables with initial=exact", and
                "independent variable".
            """

            unknown: list[
                FmiModelDescription.ModelStructure.InitialUnknowns.Unknown
            ] = field(
                default_factory=list,
                metadata={
                    "name": "Unknown",
                    "type": "Element",
                    "min_occurs": 1,
                },
            )

            @dataclass(kw_only=True)
            class Unknown:
                """
                :ivar index: ScalarVariable index of Unknown
                :ivar dependencies: Defines the dependency of the
                    Unknown (directly or indirectly via auxiliary
                    variables) on the Knowns in the Initialization Mode.
                    If not present, it must be assumed that the Unknown
                    depends on all Knowns. If present as empty list, the
                    Unknown depends on none of the Knowns. Otherwise the
                    Unknown depends on the Knowns defined by the given
                    ScalarVariable indices. The indices are ordered
                    according to size, starting with the smallest index.
                :ivar dependencies_kind: If not present, it must be
                    assumed that the Unknown depends on the Knowns
                    without a particular structure. Otherwise, the
                    corresponding Known v enters the equation as: =
                    "dependent": no particular structure, f(v) =
                    "constant"   : constant factor, c*v (only for Real
                    variables) If "dependenciesKind" is present,
                    "dependencies" must be present and must have the
                    same number of list elements.
                """

                index: int = field(
                    metadata={
                        "type": "Attribute",
                    }
                )
                dependencies: list[int] = field(
                    default_factory=list,
                    metadata={
                        "type": "Attribute",
                        "tokens": True,
                    },
                )
                dependencies_kind: list[UnknownValue] = field(
                    default_factory=list,
                    metadata={
                        "name": "dependenciesKind",
                        "type": "Attribute",
                        "tokens": True,
                    },
                )

    @dataclass(kw_only=True)
    class ModelExchange:
        """
        List of capability flags that an FMI2 Model Exchange interface can
        provide.

        :ivar source_files: List of source file names that are present
            in the "sources" directory of the FMU and need to be
            compiled in order to generate the binary of the FMU (only
            meaningful for source code FMUs).
        :ivar model_identifier: Short class name according to C-syntax,
            e.g. "A_B_C". Used as prefix for FMI2 functions if the
            functions are provided in C source code or in static
            libraries, but not if the functions are provided by a
            DLL/SharedObject. modelIdentifier is also used as name of
            the static library or DLL/SharedObject.
        :ivar needs_execution_tool: If true, a tool is needed to execute
            the model and the FMU just contains the communication to
            this tool.
        :ivar completed_integrator_step_not_needed:
        :ivar can_be_instantiated_only_once_per_process:
        :ivar can_not_use_memory_management_functions:
        :ivar can_get_and_set_fmustate:
        :ivar can_serialize_fmustate:
        :ivar provides_directional_derivative:
        """

        source_files: None | FmiModelDescription.ModelExchange.SourceFiles = (
            field(
                default=None,
                metadata={
                    "name": "SourceFiles",
                    "type": "Element",
                },
            )
        )
        model_identifier: str = field(
            metadata={
                "name": "modelIdentifier",
                "type": "Attribute",
            }
        )
        needs_execution_tool: bool = field(
            default=False,
            metadata={
                "name": "needsExecutionTool",
                "type": "Attribute",
            },
        )
        completed_integrator_step_not_needed: bool = field(
            default=False,
            metadata={
                "name": "completedIntegratorStepNotNeeded",
                "type": "Attribute",
            },
        )
        can_be_instantiated_only_once_per_process: bool = field(
            default=False,
            metadata={
                "name": "canBeInstantiatedOnlyOncePerProcess",
                "type": "Attribute",
            },
        )
        can_not_use_memory_management_functions: bool = field(
            default=False,
            metadata={
                "name": "canNotUseMemoryManagementFunctions",
                "type": "Attribute",
            },
        )
        can_get_and_set_fmustate: bool = field(
            default=False,
            metadata={
                "name": "canGetAndSetFMUstate",
                "type": "Attribute",
            },
        )
        can_serialize_fmustate: bool = field(
            default=False,
            metadata={
                "name": "canSerializeFMUstate",
                "type": "Attribute",
            },
        )
        provides_directional_derivative: bool = field(
            default=False,
            metadata={
                "name": "providesDirectionalDerivative",
                "type": "Attribute",
            },
        )

        @dataclass(kw_only=True)
        class SourceFiles:
            file: list[FmiModelDescription.ModelExchange.SourceFiles.File] = (
                field(
                    default_factory=list,
                    metadata={
                        "name": "File",
                        "type": "Element",
                        "min_occurs": 1,
                    },
                )
            )

            @dataclass(kw_only=True)
            class File:
                """
                :ivar name: Name of the file including the path relative
                    to the sources directory, using the forward slash as
                    separator (for example: name = "myFMU.c"; name =
                    "modelExchange/solve.c")
                """

                name: str = field(
                    metadata={
                        "type": "Attribute",
                    }
                )

    @dataclass(kw_only=True)
    class CoSimulation:
        """
        :ivar source_files: List of source file names that are present
            in the "sources" directory of the FMU and need to be
            compiled in order to generate the binary of the FMU (only
            meaningful for source code FMUs).
        :ivar model_identifier: Short class name according to C-syntax,
            e.g. "A_B_C". Used as prefix for FMI2 functions if the
            functions are provided in C source code or in static
            libraries, but not if the functions are provided by a
            DLL/SharedObject. modelIdentifier is also used as name of
            the static library or DLL/SharedObject.
        :ivar needs_execution_tool: If true, a tool is needed to execute
            the model and the FMU just contains the communication to
            this tool.
        :ivar can_handle_variable_communication_step_size:
        :ivar can_interpolate_inputs:
        :ivar max_output_derivative_order:
        :ivar can_run_asynchronuously:
        :ivar can_be_instantiated_only_once_per_process:
        :ivar can_not_use_memory_management_functions:
        :ivar can_get_and_set_fmustate:
        :ivar can_serialize_fmustate:
        :ivar provides_directional_derivative: Directional derivatives
            at communication points
        """

        source_files: None | FmiModelDescription.CoSimulation.SourceFiles = (
            field(
                default=None,
                metadata={
                    "name": "SourceFiles",
                    "type": "Element",
                },
            )
        )
        model_identifier: str = field(
            metadata={
                "name": "modelIdentifier",
                "type": "Attribute",
            }
        )
        needs_execution_tool: bool = field(
            default=False,
            metadata={
                "name": "needsExecutionTool",
                "type": "Attribute",
            },
        )
        can_handle_variable_communication_step_size: bool = field(
            default=False,
            metadata={
                "name": "canHandleVariableCommunicationStepSize",
                "type": "Attribute",
            },
        )
        can_interpolate_inputs: bool = field(
            default=False,
            metadata={
                "name": "canInterpolateInputs",
                "type": "Attribute",
            },
        )
        max_output_derivative_order: int = field(
            default=0,
            metadata={
                "name": "maxOutputDerivativeOrder",
                "type": "Attribute",
            },
        )
        can_run_asynchronuously: bool = field(
            default=False,
            metadata={
                "name": "canRunAsynchronuously",
                "type": "Attribute",
            },
        )
        can_be_instantiated_only_once_per_process: bool = field(
            default=False,
            metadata={
                "name": "canBeInstantiatedOnlyOncePerProcess",
                "type": "Attribute",
            },
        )
        can_not_use_memory_management_functions: bool = field(
            default=False,
            metadata={
                "name": "canNotUseMemoryManagementFunctions",
                "type": "Attribute",
            },
        )
        can_get_and_set_fmustate: bool = field(
            default=False,
            metadata={
                "name": "canGetAndSetFMUstate",
                "type": "Attribute",
            },
        )
        can_serialize_fmustate: bool = field(
            default=False,
            metadata={
                "name": "canSerializeFMUstate",
                "type": "Attribute",
            },
        )
        provides_directional_derivative: bool = field(
            default=False,
            metadata={
                "name": "providesDirectionalDerivative",
                "type": "Attribute",
            },
        )

        @dataclass(kw_only=True)
        class SourceFiles:
            file: list[FmiModelDescription.CoSimulation.SourceFiles.File] = (
                field(
                    default_factory=list,
                    metadata={
                        "name": "File",
                        "type": "Element",
                        "min_occurs": 1,
                    },
                )
            )

            @dataclass(kw_only=True)
            class File:
                """
                :ivar name: Name of the file including the path relative
                    to the sources directory, using the forward slash as
                    separator (for example: name = "myFMU.c"; name =
                    "coSimulation/solve.c")
                """

                name: str = field(
                    metadata={
                        "type": "Attribute",
                    }
                )
