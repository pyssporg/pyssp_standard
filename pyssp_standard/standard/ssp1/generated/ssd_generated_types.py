from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xsdata.models.datatype import XmlDateTime


@dataclass(kw_only=True)
class Tannotations:
    class Meta:
        name = "TAnnotations"
        target_namespace = "http://ssp-standard.org/SSP1/SystemStructureCommon"

    annotation: list[Tannotations.Annotation] = field(
        default_factory=list,
        metadata={
            "name": "Annotation",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            "min_occurs": 1,
        },
    )

    @dataclass(kw_only=True)
    class Annotation:
        """
        :ivar any_element:
        :ivar type_value: The unique name of the type of the annotation.
            In order to ensure uniqueness all types should be identified
            with reverse domain name notation (cf. Java package names or
            Apple UTIs) of a domain that is controlled by the entity
            defining the semantics and content of the annotation. For
            vendor-specific annotations this would e.g. be a domain
            controlled by the tool vendor. For MAP-SSP defined
            annotations, this will be a domain under the org.modelica
            prefix.
        """

        any_element: None | object = field(
            default=None,
            metadata={
                "type": "Wildcard",
                "namespace": "##any",
            },
        )
        type_value: str = field(
            metadata={
                "name": "type",
                "type": "Attribute",
            }
        )


class ConnectorKind(Enum):
    INPUT = "input"
    OUTPUT = "output"
    PARAMETER = "parameter"
    CALCULATED_PARAMETER = "calculatedParameter"
    INOUT = "inout"


class ParameterBindingSourceBase(Enum):
    SSD = "SSD"
    COMPONENT = "component"


class ParameterMappingSourceBase(Enum):
    SSD = "SSD"
    COMPONENT = "component"


class TcomponentImplementation(Enum):
    ANY = "any"
    MODEL_EXCHANGE = "ModelExchange"
    CO_SIMULATION = "CoSimulation"


@dataclass(kw_only=True)
class TsignalDictionaries:
    """
    :ivar signal_dictionary: This element defines a signal dictionary,
        describing the signal dictionary entries present in the signal
        dictionary. The contents of the element can be used to provide a
        signal dictionary inline, in which case the source attribute of
        the SignalDictionary element must be empty. The contents must be
        an ssb:SignalDictionary element, if the type attribute of this
        element is application/x-ssp-signal-dictionary, or any other
        valid XML content if the type attribute references another MIME
        type (in that case there should be a layered specification that
        defines how embedding the content works for that MIME type).
    """

    class Meta:
        name = "TSignalDictionaries"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureDescription"
        )

    signal_dictionary: list[TsignalDictionaries.SignalDictionary] = field(
        default_factory=list,
        metadata={
            "name": "SignalDictionary",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            "min_occurs": 1,
        },
    )

    @dataclass(kw_only=True)
    class SignalDictionary:
        """
        :ivar any_element:
        :ivar id: This attribute gives the model element a file-wide
            unique id which can be referenced from other elements or via
            URI fragment identifier.
        :ivar description: This attribute gives a human readable longer
            description of the model element, which can be shown to the
            user where appropriate.
        :ivar type_value:
        :ivar source: This attribute indicates the source of the signal
            dictionary as a URI (cf. RFC 3986).  For purposes of the
            resolution of relative URIs the base URI is the URI of the
            SSD. If the source attribute is missing, the signal
            dictionary is provided inline as contents of the
            SignalDictionary element, which must be empty otherwise. For
            the default type application/x-ssp-signal-dictionary such
            inline content must be an ssb:SignalDictionary element.
        :ivar name: This attribute gives the signal dictionary a name,
            which shall be unique within the directly enclosing system.
            The name is used for purposes of specifying the signal
            dictionary referenced by a signal dictionary reference.
            Name lookups occur in hierarchical fashion, i.e. the name is
            first looked up in the system that contains a signal
            dictionary reference.  If that lookup yields no match, the
            lookup is performed on the enclosing system, etc., until a
            match is found.  It is an error if no matching signal
            dictionary is found.
        """

        any_element: list[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "##any",
            },
        )
        id: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        description: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        type_value: str = field(
            default="application/x-ssp-signal-dictionary",
            metadata={
                "name": "type",
                "type": "Attribute",
            },
        )
        source: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        name: str = field(
            metadata={
                "type": "Attribute",
            }
        )


@dataclass(kw_only=True)
class Tenumeration:
    """
    :ivar item:
    :ivar annotations:
    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    :ivar name: This attribute specifies the name of the enumeration in
        the system description, which must be unique within in the
        system description.
    """

    class Meta:
        name = "TEnumeration"
        target_namespace = "http://ssp-standard.org/SSP1/SystemStructureCommon"

    item: list[Tenumeration.Item] = field(
        default_factory=list,
        metadata={
            "name": "Item",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            "min_occurs": 1,
        },
    )
    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )

    @dataclass(kw_only=True)
    class Item:
        """
        :ivar name: Name of the Enumeration Item
        :ivar value: The Value of the Enumeration Item
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


@dataclass(kw_only=True)
class Tunit:
    """
    :ivar base_unit:
    :ivar annotations:
    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    :ivar name: This attribute specifies the name of the unit in the
        system description, which must be unique within in the system
        description.
    """

    class Meta:
        name = "TUnit"
        target_namespace = "http://ssp-standard.org/SSP1/SystemStructureCommon"

    base_unit: Tunit.BaseUnit = field(
        metadata={
            "name": "BaseUnit",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        }
    )
    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
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
class Tconnectors:
    class Meta:
        name = "TConnectors"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureDescription"
        )

    connector: list[Tconnectors.Connector] = field(
        default_factory=list,
        metadata={
            "name": "Connector",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            "min_occurs": 1,
        },
    )

    @dataclass(kw_only=True)
    class Connector:
        """
        :ivar real:
        :ivar integer:
        :ivar boolean:
        :ivar string:
        :ivar enumeration:
        :ivar binary:
        :ivar connector_geometry: This optional element gives the
            geometry information of the connector. Note that x and y
            coordinates are in a special coordinate system, where 0,0 is
            the lower-left corner of the component/system, and 1,1 is
            the upper-right corner of the component, regardless of
            aspect ratio. For systems the placement of connectors for
            the inside and outside view of the system is identical, the
            special coordinate system is just translated to different
            actual coordinate systems, namely the one determined by the
            ElementGeometry for the outside view, and the one determined
            by SystemGeometry for the inside view.
        :ivar annotations:
        :ivar id: This attribute gives the model element a file-wide
            unique id which can be referenced from other elements or via
            URI fragment identifier.
        :ivar description: This attribute gives a human readable longer
            description of the model element, which can be shown to the
            user where appropriate.
        :ivar name: This attribute gives the connector a name, which
            shall be unique within the component or system and, for
            components, must match the name of a relevant variable/port
            in the underlying component implementation, e.g. the
            referenced FMU. Note that there is no requirement that
            connectors must be present for all variables/ports of an
            underlying component implementation.  Only those connectors
            must be present which are referenced in connections inside
            the SSD.
        :ivar kind: This attribute specifies the kind of the given
            connector, which indicates whether the connector is an
            input, an output, both (inout), a parameter or a calculated
            parameter (i.e. a parameter that is calculated by the
            component during initialization). For components this must
            match the related kind of the underlying component
            implementation, e.g. for referenced FMUs it must match the
            combination of variability and causality. For FMI 2.0 this
            means that the causality of the variable must match the kind
            of the connector. For FMI 1.0 this means that for connectors
            of kind input or output the causality of the variable must
            be input or output and the variability of the variable must
            be discrete or continuous (for outputs also constant and
            parameter are allowable).  For connectors of kind parameter
            the causality must be input or internal and the variablity
            must be parameter.  For connectors of kind
            calculatedParameter the causality must be output and the
            variablity must be parameter. For
            SignalDictionaryReferences, the kind of a given connector
            can additionally be 'inout', which indicates that the
            semantics of the connector are derived from the connections
            going to the connector. This can be used for example to
            allow a connector to function as both an input and output
            within the same SignaleDictionaryReference.
        """

        real: None | Tconnectors.Connector.Real = field(
            default=None,
            metadata={
                "name": "Real",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            },
        )
        integer: None | object = field(
            default=None,
            metadata={
                "name": "Integer",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            },
        )
        boolean: None | object = field(
            default=None,
            metadata={
                "name": "Boolean",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            },
        )
        string: None | object = field(
            default=None,
            metadata={
                "name": "String",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            },
        )
        enumeration: None | Tconnectors.Connector.Enumeration = field(
            default=None,
            metadata={
                "name": "Enumeration",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            },
        )
        binary: None | Tconnectors.Connector.Binary = field(
            default=None,
            metadata={
                "name": "Binary",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            },
        )
        connector_geometry: None | Tconnectors.Connector.ConnectorGeometry = (
            field(
                default=None,
                metadata={
                    "name": "ConnectorGeometry",
                    "type": "Element",
                    "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
                },
            )
        )
        annotations: None | Tannotations = field(
            default=None,
            metadata={
                "name": "Annotations",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            },
        )
        id: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        description: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        name: object = field(
            metadata={
                "type": "Attribute",
            }
        )
        kind: ConnectorKind = field(
            metadata={
                "type": "Attribute",
            }
        )

        @dataclass(kw_only=True)
        class ConnectorGeometry:
            x: float = field(
                metadata={
                    "type": "Attribute",
                }
            )
            y: float = field(
                metadata={
                    "type": "Attribute",
                }
            )

        @dataclass(kw_only=True)
        class Real:
            """
            :ivar unit: This attribute gives the unit of the entity and
                must reference one of the unit definitions provided in
                the Units element of the containing file. If a unit is
                not supplied, the unit is determined through default
                mechanisms: For FMU components, the unit of the
                underlying variable would be used, for systems the units
                of connected underlying connectors could be used if
                unambiguous. If a unit cannot be deduced unambinguously,
                the user should be informed of this error.
            """

            unit: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )

        @dataclass(kw_only=True)
        class Enumeration:
            """
            :ivar name: This attribute specifies the name of the
                enumeration which references into the set of defined
                enumerations of the system structure description, as
                contained in the Enumerations element of the root
                element.
            """

            name: str = field(
                metadata={
                    "type": "Attribute",
                }
            )

        @dataclass(kw_only=True)
        class Binary:
            """
            :ivar mime_type: This optional attribute specifies the MIME
                type of the underlying binary data, which defaults to
                the non-specific application/octet-stream type.  This
                information can be used by the implementation to detect
                mismatches between connected binary connectors, or
                provide automatic means of conversion between different
                formats.  It should be noted that the implementation is
                not required to provide this service, i.e. it remains
                the responsibility of the operator to ensure only
                compatible binary connectors are connected.
            """

            mime_type: str = field(
                default="application/octet-stream",
                metadata={
                    "name": "mime-type",
                    "type": "Attribute",
                },
            )


@dataclass(kw_only=True)
class TdefaultExperiment:
    """
    The attributes of this element, if present, specify reasonable default
    values for running an experiment of the given system.

    Any tool is free to ignore this information.

    :ivar annotations:
    :ivar start_time: Default start time of simulation
    :ivar stop_time: Default stop time of simulation
    """

    class Meta:
        name = "TDefaultExperiment"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureDescription"
        )

    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
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


@dataclass(kw_only=True)
class TparameterBindings:
    """
    :ivar parameter_binding: This provides a parameter binding for a
        component or system.  For FMU components this allows the
        parametrization of the FMU's parameters and start values of
        other variables with a parameter source (e.g. a parameter file).
        Note that in this case the names provided in the parameter
        source must match the names of the FMU variables, or must be
        mapped to the names of the FMU variables through a
        ParameterMapping element, or are ignored if no matching variable
        is found. For systems the names in the parameter source must
        either match the hierarchical names of parameters or other
        variables in the system, or must be mapped to those names
        through a ParameterMapping element, or are ignored if no
        matching variable is found. The hierarchical names of the
        parameters or other variables of a system are formed in the
        following way: Any variables of the system exposed through
        connectors of the system have the name of the connector as their
        name.  For all elements of the system, the hierarchical names of
        the variables of those elements are formed by prepending the
        element name and a dot to the hierarchical names of the
        variables in that element.  E.g. for a system A containing a
        system B which contains an exposed parameter named SP1 and an
        element C with a parameter P2, the hierarchical names of the
        parameters in system A are B.SP1 and B.C.P2 respectively.  The
        hierarchical name of those parameters inside system B are SP1
        and C.P2 respectively. More than one ParameterBinding can be
        supplied, in which case all of the parameters found will be used
        to parametrize the component, with parameter values in
        ParameterBinding sources appearing at a succeeding position in
        the element order taking priority over prior sources at the same
        hierarchy level, should a parameter be included in more than one
        ParameterBinding source. When ParameterBinding sources on
        multiple levels of the hierarchy supply values for the same
        parameter, bindings at a higher hierarchy level take precedence
        over lower levels, i.e. bindings at a system level take
        precedence over bindings at a sub-system or component level.
        Parameter bindings for FMU components can be used to set any
        initial values in the FMU which are legal to change.  It is
        assumed that the parameterization is applied prior to
        initializing for FMI 1.0, or before entering initialization mode
        for FMI 2.0. This means that variables eligible for
        parameterization are those with: * either causality = "input" or
        a start value for FMI 1.0 * variability != "constant" and
        initial = "exact" or "approx" for FMI 2.0 All kinds of system
        connectors can be parameterized.  In case the system level
        connectors are connected to FMU components, the parameterization
        must be compatible with the variable in the connected FMU.
        ParameterBindings that apply to a component that references
        another SSD/SSP are handled as if the top-level system of the
        SSD/SSP was present in the enclosing system instead of the
        component with one special case: Any parameter bindings in the
        component are treated as if they were present in the top-level
        system of the SSP/SSD after all parameter bindings of the
        system.  Therefore they take priority over any of the existing
        parameter bindings (for parameters with identical names).
    """

    class Meta:
        name = "TParameterBindings"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureDescription"
        )

    parameter_binding: list[TparameterBindings.ParameterBinding] = field(
        default_factory=list,
        metadata={
            "name": "ParameterBinding",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            "min_occurs": 1,
        },
    )

    @dataclass(kw_only=True)
    class ParameterBinding:
        """
        :ivar parameter_values: This optional element can be used to
            provide parameter values inline to the parameter binding, in
            which case the source attribute of the ParameterBinding
            element must be empty. The contents must be an
            ssv:ParameterSet element, if the type attribute of the
            ParameterBinding element is application/x-ssp-parameter-set,
            or any other valid XML content if the type attribute
            references another MIME type (in that case there should be a
            layered specification that defines how embedding the content
            works for that MIME type).
        :ivar parameter_mapping: This element provides an optional
            parameter mapping, which specifies how the parameter names
            and values provided in the parameter source are to be mapped
            to the parameters of the component or system in question.
            If no mapping is supplied, the parameter names of the
            parameter source are used as is for name matching against
            the names of parameters in the component or system and the
            values of the parameter source are not transformed further
            before being applied. The contents of the element can be
            used to provide a parameter mapping inline, in which case
            the source attribute of the ParameterMapping element must be
            empty. The contents must be an ssm:ParameterMapping element,
            if the type attribute of this element is application/x-ssp-
            parameter-mapping, or any other valid XML content if the
            type attribute references another MIME type (in that case
            there should be a layered specification that defines how
            embedding the content works for that MIME type).
        :ivar annotations:
        :ivar id: This attribute gives the model element a file-wide
            unique id which can be referenced from other elements or via
            URI fragment identifier.
        :ivar description: This attribute gives a human readable longer
            description of the model element, which can be shown to the
            user where appropriate.
        :ivar type_value: This attribute specifies the MIME type of the
            parameter source, which defaults to application/x-ssp-
            parameter-set to indicate the SSP parameter set file format.
            No further types are currently defined, but can of course be
            added at a later date, e.g. for pre-existing parameter file
            formats, like CDF, etc.
        :ivar source: This attribute indicates the source of the
            parameters as a URI (cf. RFC 3986).  For purposes of the
            resolution of relative URIs the base URI is the URI of the
            SSD, if the sourcebase attribute is not specified or is
            specified as SSD, and the URI of the referenced component if
            the base attribute is specified as component. This allows
            the specification of parameter sources that reside inside
            the component (e.g. an FMU) through relative URIs. Access to
            parameter sets over the SSP Parameter Repository Protocol is
            mediated through URIs with the http or https scheme. If the
            source attribute is missing, the parameter mapping is
            provided inline as contents of a ParameterValues element,
            which must not be present otherwise.
        :ivar source_base: Defines the base the source URI is resolved
            against:  If the attribute is missing or is specified as
            SSD, the source is resolved against the URI of the SSD, if
            the attribute is specified as component the URI is resolved
            against the (resolved) URI of the component source.
        :ivar prefix: Defines the optional prefix for name resolution
            and mapping purposes for this binding.  If this attribute is
            empty or not supplied no prefix is used for name resolution
            and mapping, otherwise the specified prefix is prepended to
            all names in the parameter source prior to processing the
            normal name resolution or name mapping rules.  This allows
            the user to apply a parameter set normally intended for a
            component (and thus containing bare parameter names) at a
            system level targeted to one element of the system by
            supplying the name of the element plus a dot as a prefix on
            the binding, thus causing all parameter names in the
            parameter set to be treated as if they were specified with
            proper hierarchical names.
        """

        parameter_values: (
            None | TparameterBindings.ParameterBinding.ParameterValues
        ) = field(
            default=None,
            metadata={
                "name": "ParameterValues",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            },
        )
        parameter_mapping: (
            None | TparameterBindings.ParameterBinding.ParameterMapping
        ) = field(
            default=None,
            metadata={
                "name": "ParameterMapping",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            },
        )
        annotations: None | Tannotations = field(
            default=None,
            metadata={
                "name": "Annotations",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            },
        )
        id: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        description: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        type_value: str = field(
            default="application/x-ssp-parameter-set",
            metadata={
                "name": "type",
                "type": "Attribute",
            },
        )
        source: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        source_base: ParameterBindingSourceBase = field(
            default=ParameterBindingSourceBase.SSD,
            metadata={
                "name": "sourceBase",
                "type": "Attribute",
            },
        )
        prefix: str = field(
            default="",
            metadata={
                "type": "Attribute",
            },
        )

        @dataclass(kw_only=True)
        class ParameterValues:
            any_element: list[object] = field(
                default_factory=list,
                metadata={
                    "type": "Wildcard",
                    "namespace": "##any",
                },
            )

        @dataclass(kw_only=True)
        class ParameterMapping:
            """
            :ivar any_element:
            :ivar id: This attribute gives the model element a file-wide
                unique id which can be referenced from other elements or
                via URI fragment identifier.
            :ivar description: This attribute gives a human readable
                longer description of the model element, which can be
                shown to the user where appropriate.
            :ivar type_value:
            :ivar source: This attribute indicates the source of the
                parameter mapping as a URI (cf. RFC 3986).  For purposes
                of the resolution of relative URIs the base URI is the
                URI of the SSD, if the sourcebase attribute is not
                specified or is specified as SSD, and the URI of the
                referenced component if the base attribute is specified
                as component. This allows the specification of parameter
                mapping sources that reside inside the component (e.g.
                an FMU) through relative URIs. If the source attribute
                is missing, the parameter mapping is provided inline as
                contents of the ParameterMapping element, which must be
                empty otherwise.
            :ivar source_base: Defines the base the source URI is
                resolved against:  If the attribute is missing or is
                specified as SSD, the source is resolved against the URI
                of the SSD, if the attribute is specified as component
                the URI is resolved against the (resolved) URI of the
                component source.
            """

            any_element: list[object] = field(
                default_factory=list,
                metadata={
                    "type": "Wildcard",
                    "namespace": "##any",
                },
            )
            id: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            description: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            type_value: str = field(
                default="application/x-ssp-parameter-mapping",
                metadata={
                    "name": "type",
                    "type": "Attribute",
                },
            )
            source: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            source_base: ParameterMappingSourceBase = field(
                default=ParameterMappingSourceBase.SSD,
                metadata={
                    "name": "sourceBase",
                    "type": "Attribute",
                },
            )


@dataclass(kw_only=True)
class Tenumerations:
    class Meta:
        name = "TEnumerations"
        target_namespace = "http://ssp-standard.org/SSP1/SystemStructureCommon"

    enumeration: list[Tenumeration] = field(
        default_factory=list,
        metadata={
            "name": "Enumeration",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class Tunits:
    class Meta:
        name = "TUnits"
        target_namespace = "http://ssp-standard.org/SSP1/SystemStructureCommon"

    unit: list[Tunit] = field(
        default_factory=list,
        metadata={
            "name": "Unit",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class Telement:
    """
    This is the base type for all elements, currently consisting of
    components and systems.

    :ivar connectors: The set of connectors of this element, which
        represent the interface of the element to the outside world. For
        components the set of connectors must match variable/ports of
        the underlying component implementation, e.g. the referenced
        FMU, by name. Note that there is no requirement that connectors
        must be present for all variables/ports of an underlying
        component implementation.  Only those connectors must be present
        which are referenced in connections inside the SSD.
    :ivar element_geometry: This optional element defines the geometry
        information of the component. (x1,y1) and (x2,y2) define the
        positions of the lower-left and upper-right corners of the
        component in the coordinate system of the parent. x1&gt;x2
        indicates horizontal flipping, y1&gt;y2 indicates vertical
        flipping. The optional attribute rotation (in degrees) defines
        an additional rotation (applied after flipping), where positive
        numbers indicate left rotation (x-&gt;y). The coordinate system
        is oriented: x -&gt; right, y -&gt; up. The optional attribute
        iconSource defines an icon URI with the same semantics as for
        the source attribute of the Component element.  If defined, this
        icon overrides any icon that may be defined e.g. in an .fmu file
        (as disccused in the FMI group). The optional attribute rotation
        defines the rotation (in degrees) of the icon. The optional
        attribute FixedAspectRatio defines whether the icon shall be fit
        into the extent defined by (x1,y1), (x2,y2) and iconRotation
        with fixed aspect ratio. The optional attribute iconFlip defines
        whether any flipping indicated by (x1,y1), (x2, y2) shall be
        applied to the icon graphics, too.
    :ivar parameter_bindings: The set of parameter bindings for this
        element.
    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    :ivar name: This attribute gives the element a name, which shall be
        unique within the directly enclosing system. The name is used
        for purposes of specifying the element's connectors in
        connections.
    """

    class Meta:
        name = "TElement"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureDescription"
        )

    connectors: None | Tconnectors = field(
        default=None,
        metadata={
            "name": "Connectors",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    element_geometry: None | Telement.ElementGeometry = field(
        default=None,
        metadata={
            "name": "ElementGeometry",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    parameter_bindings: None | TparameterBindings = field(
        default=None,
        metadata={
            "name": "ParameterBindings",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
            "min_length": 1,
        }
    )

    @dataclass(kw_only=True)
    class ElementGeometry:
        x1: float = field(
            metadata={
                "type": "Attribute",
            }
        )
        y1: float = field(
            metadata={
                "type": "Attribute",
            }
        )
        x2: float = field(
            metadata={
                "type": "Attribute",
            }
        )
        y2: float = field(
            metadata={
                "type": "Attribute",
            }
        )
        rotation: float = field(
            default=0.0,
            metadata={
                "type": "Attribute",
            },
        )
        icon_source: None | str = field(
            default=None,
            metadata={
                "name": "iconSource",
                "type": "Attribute",
            },
        )
        icon_rotation: float = field(
            default=0.0,
            metadata={
                "name": "iconRotation",
                "type": "Attribute",
            },
        )
        icon_flip: bool = field(
            default=False,
            metadata={
                "name": "iconFlip",
                "type": "Attribute",
            },
        )
        icon_fixed_aspect_ratio: bool = field(
            default=False,
            metadata={
                "name": "iconFixedAspectRatio",
                "type": "Attribute",
            },
        )


@dataclass(kw_only=True)
class Tcomponent(Telement):
    """
    :ivar annotations:
    :ivar type_value: This attribute specifies the MIME type of the
        component, which defaults to application/x-fmu-sharedlibrary to
        indicate an FMU.  When referencing another system structure
        definition file, the MIME type application/x-ssp-definition is
        used, and the MIME type application/x-ssp-package is used for
        referenced system structure packages (SSPs). No further types
        are currently defined.
    :ivar source: This attribute indicates the source of the component
        as an URI (cf. RFC 3986).  For purposes of the resolution of
        relative URIs the base URI is the URI of the SSD.  Therefore for
        components that are located alongside the SSD, relative URIs
        without scheme and authority can and should be used to specify
        the component sources.  For components that are packaged inside
        an SSP that contains this SSD, this is mandatory (in this way,
        the SSD URIs remain valid after unpacking the SSP into the
        filesystem). E.g. for an FMU called MyDemoFMU.fmu, that is
        located in the resources directory of an SSP, the correct URI
        would be "resources/MyDemoFMU.fmu". When referencing another
        SSP, by default the default SSD of the SSP (i.e.
        SystemStructure.ssd) is referenced.  When a non-default SSD
        should be selected, then the name of the non-default SSD must be
        given through a fragment identifier, i.e. the URI
        "resources/SubSSP.ssp#VariantB.ssd" would reference the
        VariantB.ssd of SubSSP.ssp located in the resources directory
        relative to this SSD. When the URI is a same-document URI with a
        fragment identifier, e.g. "#other-system", then the fragment
        identifier should identify a system element in this SSD document
        with an id attribute identical to the fragment identifier.  This
        mechanism can be used to instantiate an embedded system
        definition multiple times through reference to its definition
        element. Note that implementations are only required to support
        relative URIs as specified above, and that especially relative
        URIs that move beyond the baseURI (e.g. go "up" a level via ..)
        are not required to be supported by implementations, and are in
        fact often not supported for security or other reasons.
        Implementations are also not required to support any absolute
        URIs and any specific URI schemes (but are of course allowed to
        support any and all kinds of URIs where useful).
    :ivar implementation: When the referenced component is an FMU that
        contains multiple implementations (e.g. Co-Simulation and Model
        Exchange), this optional attribute can be used to determine
        which FMU implementation should be employed.  If the attribute
        is missing or uses the default value "any", the importing tool
        is free to choose what kind of FMU implementation to use.  If
        the value is "CoSimulation" or "ModelExchange" the corresponding
        FMU implementation must be used.  It is an error if the
        specified type of FMU implementation is not present in the FMU.
    """

    class Meta:
        name = "TComponent"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureDescription"
        )

    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    type_value: str = field(
        default="application/x-fmu-sharedlibrary",
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    source: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    implementation: TcomponentImplementation = field(
        default=TcomponentImplementation.ANY,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class TsignalDictionaryReference(Telement):
    """
    :ivar annotations:
    :ivar dictionary: This attribute gives the name of the signal
        dictionary that is to be referenced.  Name lookups occur in
        hierarchical fashion, i.e. the name is first looked up in the
        system that contains a signal dictionary reference.  If that
        lookup yields no match, the lookup is performed on the enclosing
        system, etc., until a match is found. It is an error if no
        matching signal dictionary is found.
    """

    class Meta:
        name = "TSignalDictionaryReference"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureDescription"
        )

    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    dictionary: str = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Tsystem(Telement):
    """
    This element describes a system, which can contain components and other
    systems as elements, connectors as an interface to the outside world,
    and connections connecting the connectors of itself and of its elements
    to another.

    :ivar elements:
    :ivar connections:
    :ivar signal_dictionaries:
    :ivar system_geometry: This optional element defines the extent of
        the system canvas. (x1,y1) and (x2,y2) define the lower-left and
        upper-right corner, respectively. Different from
        ElementGeometry, where x1&gt;x2 and y1&gt;y2 indicate flipping,
        x1 &lt; x2 and y1 &lt; y2 must hold here. If undefined, the
        system canvas extent defaults to the bounding box of all
        ElementGeometry elements of the child elements of the system.
        When displaying the content of a sub-system together with the
        enclosing parent system, the transformation of co-coordinates
        inside the sub-system to co-ordinates in the parent system is
        defined by the transformation from SystemGeometry.{x1,y1,x2,y2}
        to ElementGeometry.{x1', y1', x2', y2'}, where
        ElementGeometry.z' is the respective coordinate of the sub-
        system when instantiated in the parent system after rotation.
    :ivar graphical_elements: This optional element contains the set of
        purely graphical elements that are contained in the system, e.g.
        things like notes, which have no semantic impact on the system
        but aid in presentation of the system in graphical user
        interfaces. Currently the only graphical element defined is the
        Note element, which allows for simple textual notes to be placed
        into the system diagram, but in the future more elements might
        be added as needed for exchange of graphical information.
    :ivar annotations:
    """

    class Meta:
        name = "TSystem"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureDescription"
        )

    elements: None | Tsystem.Elements = field(
        default=None,
        metadata={
            "name": "Elements",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    connections: None | Tsystem.Connections = field(
        default=None,
        metadata={
            "name": "Connections",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    signal_dictionaries: None | TsignalDictionaries = field(
        default=None,
        metadata={
            "name": "SignalDictionaries",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    system_geometry: None | Tsystem.SystemGeometry = field(
        default=None,
        metadata={
            "name": "SystemGeometry",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    graphical_elements: None | Tsystem.GraphicalElements = field(
        default=None,
        metadata={
            "name": "GraphicalElements",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )
    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        },
    )

    @dataclass(kw_only=True)
    class Elements:
        component: list[Tcomponent] = field(
            default_factory=list,
            metadata={
                "name": "Component",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            },
        )
        signal_dictionary_reference: list[TsignalDictionaryReference] = field(
            default_factory=list,
            metadata={
                "name": "SignalDictionaryReference",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            },
        )
        system: list[Tsystem] = field(
            default_factory=list,
            metadata={
                "name": "System",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            },
        )

    @dataclass(kw_only=True)
    class Connections:
        """
        :ivar connection: This element specifies a connection between
            two connectors, either of the system or its directly
            contained elements. Note that connections between connectors
            on a system are allowed, so neither startElement nor
            endElement has to be supplied. Note also that the terms
            start and end in the attribute names of the connector, like
            startElement or endConnector, do not denote directionality
            of the data flow implied by the connector. That is
            determined by the combination of the semantics of the actual
            connectors (variables/ports) connected and their kind
            attributes: For component to component connections as well
            as for connections between two connectors at the system
            level, currently the kind of one connector must be output
            and of another connector must be input, or for parameter
            connections the kind of one connector must be
            calculatedParameter and the other must be parameter.
            Information flows from the output/calculatedParameter to the
            input/parameter connector. For system to component
            connections the kinds of the connectors must match, i.e.
            either both are input or both output or both parameter or
            both calculatedParameter.
        """

        connection: list[Tsystem.Connections.Connection] = field(
            default_factory=list,
            metadata={
                "name": "Connection",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
                "min_occurs": 1,
            },
        )

        @dataclass(kw_only=True)
        class Connection:
            """
            :ivar linear_transformation: This element provides for a
                linear transformation to be performed on the parameter
                values and is valid for parameters of a continuous type.
            :ivar boolean_mapping_transformation: This element provides
                for a transformation of boolean parameter values based
                on a mapping table and is valid for parameters of
                boolean type. Each mapping table entry is provided by a
                MapEntry element.
            :ivar integer_mapping_transformation: This element provides
                for a transformation of integer parameter values based
                on a mapping table and is valid for parameters of
                integer and enumeration type.  Each mapping table entry
                is provided by a MapEntry element.
            :ivar enumeration_mapping_transformation: This element
                provides for a transformation of enumeration parameter
                values based on a mapping table of their enumeration
                item names and is valid for parameters of enumeration
                type.  Each mapping table entry is provided by a
                MapEntry element.
            :ivar connection_geometry: This optional element defines the
                geometry information of the connection. The start and
                end coordinates of the connection are derived
                automatically through the coordinates of the
                corresponding connectors.  The only relevant geometry
                information provided by the connection geometry is a, by
                default empty, list of intermediate waypoint
                coordinates, which are to be interpreted as for the
                svg:polyline primitive, i.e. as waypoints for straight
                line segments, with the first and last points added
                automatically based on the translated coordinates of the
                start and end connectors. Note that x and y coordinates
                are in the coordinate system of the enclosing system.
            :ivar annotations:
            :ivar id: This attribute gives the model element a file-wide
                unique id which can be referenced from other elements or
                via URI fragment identifier.
            :ivar description: This attribute gives a human readable
                longer description of the model element, which can be
                shown to the user where appropriate.
            :ivar start_element: This attribute gives the name of the
                element that contains the connector given as
                startConnector.  If the attribute is elided, then the
                startConnector names a connector on this system.
            :ivar start_connector: This attribute gives the name of the
                connector that is the start of the connection.  If
                startElement is not supplied this indicates a connector
                on this system, otherwise the connector is to be found
                on the given element.
            :ivar end_element: This attribute gives the name of the
                element that contains the connector given as
                endConnector.  If the attribute is elided, then the
                endConnector names a connector on this system.
            :ivar end_connector: This attribute gives the name of the
                connector that is the end of the connection.  If
                endElement is not supplied this indicates a connector on
                this system, otherwise the connector is to be found on
                the given element.
            :ivar suppress_unit_conversion: This attribute specifies
                whether automatic conversions between start and end
                connector are performed using unit information
                potentially available for both start and end
                definitions.  If this attribute is supplied and its
                value is true, then the environment will not perform any
                automatic unit conversions, otherwise automatic unit
                conversions can be performed.  This is also useful in
                conjunction with the optional linear transformation
                supplied via the LinearTransformation element: With
                suppressUnitConversion = true, the linear transformation
                is performed instead of any unit conversions, whereas
                otherwise the linear transformation is performed in
                addition to any unit conversions.
            """

            linear_transformation: (
                None | Tsystem.Connections.Connection.LinearTransformation
            ) = field(
                default=None,
                metadata={
                    "name": "LinearTransformation",
                    "type": "Element",
                    "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
                },
            )
            boolean_mapping_transformation: (
                None
                | Tsystem.Connections.Connection.BooleanMappingTransformation
            ) = field(
                default=None,
                metadata={
                    "name": "BooleanMappingTransformation",
                    "type": "Element",
                    "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
                },
            )
            integer_mapping_transformation: (
                None
                | Tsystem.Connections.Connection.IntegerMappingTransformation
            ) = field(
                default=None,
                metadata={
                    "name": "IntegerMappingTransformation",
                    "type": "Element",
                    "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
                },
            )
            enumeration_mapping_transformation: (
                None
                | Tsystem.Connections.Connection.EnumerationMappingTransformation
            ) = field(
                default=None,
                metadata={
                    "name": "EnumerationMappingTransformation",
                    "type": "Element",
                    "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
                },
            )
            connection_geometry: (
                None | Tsystem.Connections.Connection.ConnectionGeometry
            ) = field(
                default=None,
                metadata={
                    "name": "ConnectionGeometry",
                    "type": "Element",
                    "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
                },
            )
            annotations: None | Tannotations = field(
                default=None,
                metadata={
                    "name": "Annotations",
                    "type": "Element",
                    "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
                },
            )
            id: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            description: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            start_element: None | str = field(
                default=None,
                metadata={
                    "name": "startElement",
                    "type": "Attribute",
                },
            )
            start_connector: str = field(
                metadata={
                    "name": "startConnector",
                    "type": "Attribute",
                }
            )
            end_element: None | str = field(
                default=None,
                metadata={
                    "name": "endElement",
                    "type": "Attribute",
                },
            )
            end_connector: str = field(
                metadata={
                    "name": "endConnector",
                    "type": "Attribute",
                }
            )
            suppress_unit_conversion: bool = field(
                default=False,
                metadata={
                    "name": "suppressUnitConversion",
                    "type": "Attribute",
                },
            )

            @dataclass(kw_only=True)
            class ConnectionGeometry:
                points_x: list[float] = field(
                    default_factory=list,
                    metadata={
                        "name": "pointsX",
                        "type": "Attribute",
                        "tokens": True,
                    },
                )
                points_y: list[float] = field(
                    default_factory=list,
                    metadata={
                        "name": "pointsY",
                        "type": "Attribute",
                        "tokens": True,
                    },
                )

            @dataclass(kw_only=True)
            class LinearTransformation:
                """
                :ivar factor: This attribute specifies an optional
                    factor value to use in a linear transformation of
                    the source parameter value to the target parameter
                    value, i.e. in the calculation target = factor *
                    source + offset. Note that conversions based on
                    different units are performed, unless prevented by
                    suppressUnitConversion, prior to the application of
                    the linear transformation, i.e. the value of source
                    is already converted to the target unit in the
                    formula above.
                :ivar offset: This attribute specifies an optional
                    offset value to use in a linear transformation of
                    the source parameter value to the target parameter
                    value, i.e. in the calculation target = factor *
                    source + offset. Note that conversions based on
                    different units are performed, unless prevented by
                    suppressUnitConversion, prior to the application of
                    the linear transformation, i.e. the value of source
                    is already converted to the target unit in the
                    formula above.
                """

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
            class BooleanMappingTransformation:
                map_entry: list[
                    Tsystem.Connections.Connection.BooleanMappingTransformation.MapEntry
                ] = field(
                    default_factory=list,
                    metadata={
                        "name": "MapEntry",
                        "type": "Element",
                        "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
                        "min_occurs": 1,
                    },
                )

                @dataclass(kw_only=True)
                class MapEntry:
                    """
                    :ivar source: This attribute gives the value of the
                        parameter in the parameter source that this
                        entry applies to.
                    :ivar target: This attribute gives the value of the
                        parameter to use when applying it to the system
                        or component that is to be parametrized.
                    """

                    source: bool = field(
                        metadata={
                            "type": "Attribute",
                        }
                    )
                    target: bool = field(
                        metadata={
                            "type": "Attribute",
                        }
                    )

            @dataclass(kw_only=True)
            class IntegerMappingTransformation:
                map_entry: list[
                    Tsystem.Connections.Connection.IntegerMappingTransformation.MapEntry
                ] = field(
                    default_factory=list,
                    metadata={
                        "name": "MapEntry",
                        "type": "Element",
                        "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
                        "min_occurs": 1,
                    },
                )

                @dataclass(kw_only=True)
                class MapEntry:
                    """
                    :ivar source: This attribute gives the value of the
                        parameter in the parameter source that this
                        entry applies to.
                    :ivar target: This attribute gives the value of the
                        parameter to use when applying it to the system
                        or component that is to be parametrized.
                    """

                    source: int = field(
                        metadata={
                            "type": "Attribute",
                        }
                    )
                    target: int = field(
                        metadata={
                            "type": "Attribute",
                        }
                    )

            @dataclass(kw_only=True)
            class EnumerationMappingTransformation:
                map_entry: list[
                    Tsystem.Connections.Connection.EnumerationMappingTransformation.MapEntry
                ] = field(
                    default_factory=list,
                    metadata={
                        "name": "MapEntry",
                        "type": "Element",
                        "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
                        "min_occurs": 1,
                    },
                )

                @dataclass(kw_only=True)
                class MapEntry:
                    """
                    :ivar source: This attribute gives the value of the
                        parameter in the parameter source that this
                        entry applies to.
                    :ivar target: This attribute gives the value of the
                        parameter to use when applying it to the system
                        or component that is to be parametrized.
                    """

                    source: str = field(
                        metadata={
                            "type": "Attribute",
                        }
                    )
                    target: str = field(
                        metadata={
                            "type": "Attribute",
                        }
                    )

    @dataclass(kw_only=True)
    class SystemGeometry:
        x1: float = field(
            metadata={
                "type": "Attribute",
            }
        )
        y1: float = field(
            metadata={
                "type": "Attribute",
            }
        )
        x2: float = field(
            metadata={
                "type": "Attribute",
            }
        )
        y2: float = field(
            metadata={
                "type": "Attribute",
            }
        )

    @dataclass(kw_only=True)
    class GraphicalElements:
        """
        :ivar note: This element defines a graphical note to be placed
            on the canvas of the enclosing system.  It is sized using
            the attributes so that the coordinates (x1,y1) and (x2,y2)
            define the positions of the lower-left and upper-right
            corners of the note in the coordinate system of the parent.
            The note text is given by the text attribute.  The
            presentation expectation is that the text is automatically
            sized ad wrapped in such a way that it fits the note area.
            If this would lead to too small text, it might be necessary
            to provide an interactive method (like expanding triangle,
            or popup, or other means) to show the remainder of the note
            text.  Inside the text attribute, newlines indicate
            paragraph breaks.
        """

        note: list[Tsystem.GraphicalElements.Note] = field(
            default_factory=list,
            metadata={
                "name": "Note",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureDescription",
            },
        )

        @dataclass(kw_only=True)
        class Note:
            x1: float = field(
                metadata={
                    "type": "Attribute",
                }
            )
            y1: float = field(
                metadata={
                    "type": "Attribute",
                }
            )
            x2: float = field(
                metadata={
                    "type": "Attribute",
                }
            )
            y2: float = field(
                metadata={
                    "type": "Attribute",
                }
            )
            text: str = field(
                metadata={
                    "type": "Attribute",
                }
            )


@dataclass(kw_only=True)
class SystemStructureDescription:
    """
    :ivar system:
    :ivar enumerations:
    :ivar units:
    :ivar default_experiment:
    :ivar annotations:
    :ivar version: Version of SSD format, 1.0 for this release.
    :ivar name: This attribute gives the system structure a name, which
        can be used for purposes of presenting the system structure to
        the user, e.g. when selecting individual variant SSDs from an
        SSP.
    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    :ivar author: This attribute gives the name of the author of this
        file's content.
    :ivar fileversion: This attribute gives a version number for this
        file's content.
    :ivar copyright: This attribute gives copyright information for this
        file's content.
    :ivar license: This attribute gives license information for this
        file's content.
    :ivar generation_tool: This attribute gives the name of the tool
        that generated this file.
    :ivar generation_date_and_time: This attribute gives the date and
        time this file was generated.
    """

    class Meta:
        namespace = "http://ssp-standard.org/SSP1/SystemStructureDescription"

    system: Tsystem = field(
        metadata={
            "name": "System",
            "type": "Element",
        }
    )
    enumerations: None | Tenumerations = field(
        default=None,
        metadata={
            "name": "Enumerations",
            "type": "Element",
        },
    )
    units: None | Tunits = field(
        default=None,
        metadata={
            "name": "Units",
            "type": "Element",
        },
    )
    default_experiment: None | TdefaultExperiment = field(
        default=None,
        metadata={
            "name": "DefaultExperiment",
            "type": "Element",
        },
    )
    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
        },
    )
    version: str = field(
        metadata={
            "type": "Attribute",
            "pattern": r"1[.][0-9]+(-.*)?",
        }
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    id: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
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
    fileversion: None | str = field(
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
