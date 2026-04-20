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
class Tparameter:
    """
    :ivar real:
    :ivar integer:
    :ivar boolean:
    :ivar string:
    :ivar enumeration:
    :ivar binary:
    :ivar annotations:
    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    :ivar name: This attribute specifies the name of the parameter in
        the parameter set, which must be unique within in the parameter
        set.
    """

    class Meta:
        name = "TParameter"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureParameterValues"
        )

    real: None | Tparameter.Real = field(
        default=None,
        metadata={
            "name": "Real",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    integer: None | Tparameter.Integer = field(
        default=None,
        metadata={
            "name": "Integer",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    boolean: None | Tparameter.Boolean = field(
        default=None,
        metadata={
            "name": "Boolean",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    string: None | Tparameter.String = field(
        default=None,
        metadata={
            "name": "String",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    enumeration: None | Tparameter.Enumeration = field(
        default=None,
        metadata={
            "name": "Enumeration",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    binary: None | Tparameter.Binary = field(
        default=None,
        metadata={
            "name": "Binary",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    annotations: None | Tannotations = field(
        default=None,
        metadata={
            "name": "Annotations",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
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
    class Real:
        """
        :ivar value: This attribute gives the value of the parameter.
        :ivar unit: This attribute gives the unit of the parameter value
            and must reference one of the unit definitions provided in
            the Units element of the enclosing file.
        """

        value: float = field(
            metadata={
                "type": "Attribute",
            }
        )
        unit: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Integer:
        """
        :ivar value: This attribute gives the value of the parameter.
        """

        value: int = field(
            metadata={
                "type": "Attribute",
            }
        )

    @dataclass(kw_only=True)
    class Boolean:
        """
        :ivar value: This attribute gives the value of the parameter.
        """

        value: bool = field(
            metadata={
                "type": "Attribute",
            }
        )

    @dataclass(kw_only=True)
    class String:
        """
        :ivar value: This attribute gives the value of the parameter.
        """

        value: str = field(
            metadata={
                "type": "Attribute",
            }
        )

    @dataclass(kw_only=True)
    class Enumeration:
        """
        :ivar value: This attribute gives the value of the parameter as
            the enumeration item name.  Note that the actual numeric
            value this value is mapped to at run time will depend on the
            item mapping of the enumeration type of the variables being
            parameterized.
        :ivar name: This attribute specifies the name of the enumeration
            which references into the set of defined enumerations of the
            system structure description, as contained in the
            Enumerations element of the root element. This attribute is
            optional; if it is not specified, then the list of valid
            enumeration items with their names and values is not
            specified, and the interpretation of the enumeration value
            is left solely to the variables that are being
            parameterized. If the attribute is specified,
            implementations MAY use that information for user interface
            purposes, and/or for additional consistency checking.
        """

        value: str = field(
            metadata={
                "type": "Attribute",
            }
        )
        name: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Binary:
        """
        :ivar mime_type: This optional attribute specifies the MIME type
            of the underlying binary data, which defaults to the non-
            specific application/octet-stream type.  This information
            can be used by the implementation to detect mismatches
            between binary parameters, or provide automatic conversions
            between different formats.  It should be noted that the
            implementation is not required to provide this service, i.e.
            it remains the responsibility of the operator to ensure only
            compatible binary connectors/parameters are connected.
        :ivar value: This attribute gives the value of the parameter as
            a hex encoded binary value.
        """

        mime_type: str = field(
            default="application/octet-stream",
            metadata={
                "name": "mime-type",
                "type": "Attribute",
            },
        )
        value: bytes = field(
            metadata={
                "type": "Attribute",
                "format": "base16",
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
class Tparameters:
    class Meta:
        name = "TParameters"
        target_namespace = (
            "http://ssp-standard.org/SSP1/SystemStructureParameterValues"
        )

    parameter: list[Tparameter] = field(
        default_factory=list,
        metadata={
            "name": "Parameter",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )


@dataclass(kw_only=True)
class ParameterSet:
    """
    :ivar parameters:
    :ivar enumerations:
    :ivar units:
    :ivar annotations:
    :ivar version: Version of SSV format, 1.0 for this release.
    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    :ivar name: Name of the Parameter Set.
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
            "http://ssp-standard.org/SSP1/SystemStructureParameterValues"
        )

    parameters: Tparameters = field(
        metadata={
            "name": "Parameters",
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
    name: str = field(
        metadata={
            "type": "Attribute",
        }
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
