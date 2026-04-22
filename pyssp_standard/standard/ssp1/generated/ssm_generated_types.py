from __future__ import annotations

from dataclasses import dataclass, field

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
class TmappingEntry:
    """
    :ivar linear_transformation: This element provides for a linear
        transformation to be performed on the parameter values and is
        valid for parameters of a continuous type.
    :ivar boolean_mapping_transformation: This element provides for a
        transformation of boolean parameter values based on a mapping
        table and is valid for parameters of boolean type. Each mapping
        table entry is provided by a MapEntry element.
    :ivar integer_mapping_transformation: This element provides for a
        transformation of integer parameter values based on a mapping
        table and is valid for parameters of integer and enumeration
        type.  Each mapping table entry is provided by a MapEntry
        element.
    :ivar enumeration_mapping_transformation: This element provides for
        a transformation of enumeration parameter values based on a
        mapping table of their enumeration item names and is valid for
        parameters of enumeration type.  Each mapping table entry is
        provided by a MapEntry element.
    :ivar annotations:
    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    :ivar source: This attribute specifies the name of the parameter in
        the parameter source that is to be mapped to a new name and/or
        provided with a transformation in this mapping entry.
    :ivar target: This attribute specifies the name of the parameter in
        the system or component that is to be parametrized, i.e. that is
        the target of this mapping entry.
    :ivar suppress_unit_conversion: This attribute specifies whether
        automatic conversions between start and end connector are
        performed using unit information potentially available for both
        start and end definitions.  If this attribute is supplied and
        its value is true, then the environment will not perform any
        automatic unit conversions, otherwise automatic unit conversions
        can be performed.  This is also useful in conjunction with the
        optional linear transformation supplied via the
        LinearTransformation element: With suppressUnitConversion =
        true, the linear transformation is performed instead of any unit
        conversions, whereas otherwise the linear transformation is
        performed in addition to any unit conversions.
    """

    class Meta:
        name = "TMappingEntry"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureParameterMapping"
        )

    linear_transformation: None | TmappingEntry.LinearTransformation = field(
        default=None,
        metadata={
            "name": "LinearTransformation",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        },
    )
    boolean_mapping_transformation: (
        None | TmappingEntry.BooleanMappingTransformation
    ) = field(
        default=None,
        metadata={
            "name": "BooleanMappingTransformation",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        },
    )
    integer_mapping_transformation: (
        None | TmappingEntry.IntegerMappingTransformation
    ) = field(
        default=None,
        metadata={
            "name": "IntegerMappingTransformation",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        },
    )
    enumeration_mapping_transformation: (
        None | TmappingEntry.EnumerationMappingTransformation
    ) = field(
        default=None,
        metadata={
            "name": "EnumerationMappingTransformation",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        },
    )
    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterMapping",
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
    suppress_unit_conversion: bool = field(
        default=False,
        metadata={
            "name": "suppressUnitConversion",
            "type": "Attribute",
        },
    )

    @dataclass(kw_only=True)
    class LinearTransformation:
        """
        :ivar factor: This attribute specifies an optional factor value
            to use in a linear transformation of the source parameter
            value to the target parameter value, i.e. in the calculation
            target = factor * source + offset. Note that conversions
            based on different units are performed, unless prevented by
            suppressUnitConversion, prior to the application of the
            linear transformation, i.e. the value of source is already
            converted to the target unit in the formula above.
        :ivar offset: This attribute specifies an optional offset value
            to use in a linear transformation of the source parameter
            value to the target parameter value, i.e. in the calculation
            target = factor * source + offset. Note that conversions
            based on different units are performed, unless prevented by
            suppressUnitConversion, prior to the application of the
            linear transformation, i.e. the value of source is already
            converted to the target unit in the formula above.
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
            TmappingEntry.BooleanMappingTransformation.MapEntry
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
                parameter in the parameter source that this entry
                applies to.
            :ivar target: This attribute gives the value of the
                parameter to use when applying it to the system or
                component that is to be parametrized.
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
            TmappingEntry.IntegerMappingTransformation.MapEntry
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
                parameter in the parameter source that this entry
                applies to.
            :ivar target: This attribute gives the value of the
                parameter to use when applying it to the system or
                component that is to be parametrized.
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
            TmappingEntry.EnumerationMappingTransformation.MapEntry
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
                parameter in the parameter source that this entry
                applies to.
            :ivar target: This attribute gives the value of the
                parameter to use when applying it to the system or
                component that is to be parametrized.
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
class ParameterMapping:
    """
    :ivar mapping_entry:
    :ivar annotations:
    :ivar version: Version of SSM format, 1.0 for this release.
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
        namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureParameterMapping"
        )

    mapping_entry: list[TmappingEntry] = field(
        default_factory=list,
        metadata={
            "name": "MappingEntry",
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
