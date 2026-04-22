from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xsdata.models.datatype import XmlDateTime


@dataclass(kw_only=True)
class ContentType:
    """
    This optional element can contain inlined content of an entity.

    If it is present, then the attribute source of the enclosing element
    must not be present.

    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    :ivar content:
    """

    class Meta:
        target_namespace = "http://ssp-standard.org/SSP1/SystemStructureCommon"

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
    content: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
        },
    )


class MetaDataKind(Enum):
    GENERAL = "general"
    QUALITY = "quality"


class MetaDataSourceBase(Enum):
    FILE = "file"
    RESOURCE = "resource"


class SignatureTypeRole(Enum):
    AUTHENTICITY = "authenticity"
    SUITABILITY = "suitability"


class SignatureTypeSourceBase(Enum):
    FILE = "file"
    RESOURCE = "resource"
    META_DATA = "metaData"


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
        :ivar type_value: The unique name of the type of the annotation.
            In order to ensure uniqueness all types should be identified
            with reverse domain name notation (cf. Java package names or
            Apple UTIs) of a domain that is controlled by the entity
            defining the semantics and content of the annotation. For
            vendor-specific annotations this would e.g. be a domain
            controlled by the tool vendor. For MAP-SSP defined
            annotations, this will be a domain under the org.modelica
            prefix.
        :ivar content:
        """

        type_value: str = field(
            metadata={
                "name": "type",
                "type": "Attribute",
            }
        )
        content: list[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "##any",
                "mixed": True,
            },
        )


@dataclass(kw_only=True)
class SignatureType:
    """
    :ivar content:
    :ivar role: This mandatory attribute specifies the role this
        signature has in the overall process. It indicates whether the
        digital signature is intended to just convey the authenticity of
        the information, or whether a claim for suitability of the
        information for certain purposes is made.  In the later case,
        the digital signature format should include detailed information
        about what suitability claims are being made.
    :ivar type_value: This mandatory attribute specifies the MIME type
        of the resource signature, which does not have a default value.
        If no specific MIME type can be indicated, then the type
        application/octet-stream is to be used.
    :ivar source: This attribute indicates the source of the digital
        signature as a URI (cf. RFC 3986).  The base URI for the
        resolution of relative URIs is determined by the sourceBase
        attribute. If the source attribute is missing, the signature
        must be provided inline as contents of a Content element, which
        must not be present otherwise.
    :ivar source_base: Defines the base the source URI is resolved
        against:  If the attribute is missing or is specified as file,
        the source is resolved against the URI of the containing file.
        If the containing model element has a source attribute, the
        sourceBase attribute can be specified as resource. In this case
        the URI is resolved against the (resolved) source URI of the
        containing model element.  If the Signature element is contained
        within a MetaData element, the sourceBase attribute can be
        specified as metaData.  In this case the URI is resolved against
        the (resolved) URI of the meta data source. The last two options
        allow the specification of signature sources that reside inside
        a resource (for example an FMU), or the meta data through
        relative URIs.
    :ivar id: This attribute gives the model element a file-wide unique
        id which can be referenced from other elements or via URI
        fragment identifier.
    :ivar description: This attribute gives a human readable longer
        description of the model element, which can be shown to the user
        where appropriate.
    """

    class Meta:
        target_namespace = "http://ssp-standard.org/SSP1/SystemStructureCommon"

    content: None | ContentType = field(
        default=None,
        metadata={
            "name": "Content",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        },
    )
    role: SignatureTypeRole = field(
        metadata={
            "type": "Attribute",
        }
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
        }
    )
    source: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    source_base: SignatureTypeSourceBase = field(
        default=SignatureTypeSourceBase.FILE,
        metadata={
            "name": "sourceBase",
            "type": "Attribute",
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
    :ivar float64:
    :ivar float32:
    :ivar integer:
    :ivar int8:
    :ivar uint8:
    :ivar int16:
    :ivar uint16:
    :ivar int32:
    :ivar uint32:
    :ivar int64:
    :ivar uint64:
    :ivar boolean:
    :ivar string:
    :ivar enumeration:
    :ivar binary:
    :ivar dimension: This optional element specifies one dimension of an
        array connector. If no dimension elements are present in a
        connector, it is a scalar connector. The number of dimension
        elements in a connector provides the dimensionality of the
        array. Either the size or the sizeConnector attributes CAN be
        present on the element, indicating a fixed size, or a size that
        depends on the structural parameter or constant referenced by
        the sizeConnector attribute. If none of the attributes are
        present, then the size of the dimension is unspecified at the
        SSD level. If both attributes are present this is considered an
        error.
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
    float64: None | Tparameter.Float64 = field(
        default=None,
        metadata={
            "name": "Float64",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    float32: None | Tparameter.Float32 = field(
        default=None,
        metadata={
            "name": "Float32",
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
    int8: None | Tparameter.Int8 = field(
        default=None,
        metadata={
            "name": "Int8",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    uint8: None | Tparameter.Uint8 = field(
        default=None,
        metadata={
            "name": "UInt8",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    int16: None | Tparameter.Int16 = field(
        default=None,
        metadata={
            "name": "Int16",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    uint16: None | Tparameter.Uint16 = field(
        default=None,
        metadata={
            "name": "UInt16",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    int32: None | Tparameter.Int32 = field(
        default=None,
        metadata={
            "name": "Int32",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    uint32: None | Tparameter.Uint32 = field(
        default=None,
        metadata={
            "name": "UInt32",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    int64: None | Tparameter.Int64 = field(
        default=None,
        metadata={
            "name": "Int64",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        },
    )
    uint64: None | Tparameter.Uint64 = field(
        default=None,
        metadata={
            "name": "UInt64",
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
    dimension: list[Tparameter.Dimension] = field(
        default_factory=list,
        metadata={
            "name": "Dimension",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
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
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        :ivar unit: This attribute gives the unit of the parameter value
            and must reference one of the unit definitions provided in
            the Units element of the enclosing file.
        """

        value: list[float] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )
        unit: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Float64:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        :ivar unit: This attribute gives the unit of the parameter value
            and must reference one of the unit definitions provided in
            the Units element of the enclosing file.
        """

        value: list[float] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )
        unit: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

    @dataclass(kw_only=True)
    class Float32:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        :ivar unit: This attribute gives the unit of the parameter value
            and must reference one of the unit definitions provided in
            the Units element of the enclosing file.
        """

        value: list[float] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
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
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Int8:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Uint8:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Int16:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Uint16:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Int32:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Uint32:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Int64:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Uint64:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class Boolean:
        """
        :ivar value: This attribute gives the value(s) of the parameter.
            Array values are serialized in row-major order, as defined
            in FMI.
        """

        value: list[bool] = field(
            default_factory=list,
            metadata={
                "type": "Attribute",
                "tokens": True,
            },
        )

    @dataclass(kw_only=True)
    class String:
        """
        :ivar value: This element gives the value for one array element
            of the parameter. If any Value element is present, then the
            value attribute on the parent element MUST NOT be used.
            Array values are serialized in row-major order, as defined
            in FMI.
        :ivar value_attribute: This attribute gives the value of the
            parameter, if it is a scalar parameter. For array parameters
            requiring more than one element, Value elements MUST be
            used. For scalar and one element array parameters the Value
            element CAN be used. In either case, if Value elements are
            used, then this value attribute MUST NOT be present.
        """

        value: list[Tparameter.String.Value] = field(
            default_factory=list,
            metadata={
                "name": "Value",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
            },
        )
        value_attribute: None | str = field(
            default=None,
            metadata={
                "name": "value",
                "type": "Attribute",
            },
        )

        @dataclass(kw_only=True)
        class Value:
            value: str = field(
                metadata={
                    "type": "Attribute",
                }
            )

    @dataclass(kw_only=True)
    class Enumeration:
        """
        :ivar value: This element gives the value for one array element
            of the parameter as the enumeration item name. If any Value
            element is present, then the value attribute on the parent
            element MUST NOT be used. Note that the actual numeric value
            this value is mapped to at run time will depend on the item
            mapping of the enumeration type of the variables being
            parameterized. Array values are serialized in row-major
            order, as defined in FMI.
        :ivar value_attribute: This attribute gives the value of the
            parameter as the enumeration item name, if it is a scalar
            parameter. For array parameters requiring more than one
            element, Value elements MUST be used. For scalar and one
            element array parameters the Value element CAN be used. In
            either case, if Value elements are used, then this value
            attribute MUST NOT be present. Note that the actual numeric
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

        value: list[Tparameter.Enumeration.Value] = field(
            default_factory=list,
            metadata={
                "name": "Value",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
            },
        )
        value_attribute: None | str = field(
            default=None,
            metadata={
                "name": "value",
                "type": "Attribute",
            },
        )
        name: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

        @dataclass(kw_only=True)
        class Value:
            value: str = field(
                metadata={
                    "type": "Attribute",
                }
            )

    @dataclass(kw_only=True)
    class Binary:
        """
        :ivar value: This element gives the value for one array element
            of the parameter. If any Value element is present, then the
            value attribute on the parent element MUST NOT be used.
            Array values are serialized in row-major order, as defined
            in FMI.
        :ivar mime_type: This optional attribute specifies the MIME type
            of the underlying binary data, which defaults to the non-
            specific application/octet-stream type.  This information
            can be used by the implementation to detect mismatches
            between binary parameters, or provide automatic conversions
            between different formats.  It should be noted that the
            implementation is not required to provide this service, i.e.
            it remains the responsibility of the operator to ensure only
            compatible binary connectors/parameters are connected.
        :ivar value_attribute: This attribute gives the value of the
            parameter as a hex encoded binary value, if it is a scalar
            parameter. For array parameters requiring more than one
            element, Value elements MUST be used. For scalar and one
            element array parameters the Value element CAN be used. In
            either case, if Value elements are used, then this value
            attribute MUST NOT be present.
        """

        value: list[Tparameter.Binary.Value] = field(
            default_factory=list,
            metadata={
                "name": "Value",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
            },
        )
        mime_type: str = field(
            default="application/octet-stream",
            metadata={
                "name": "mime-type",
                "type": "Attribute",
            },
        )
        value_attribute: None | bytes = field(
            default=None,
            metadata={
                "name": "value",
                "type": "Attribute",
                "format": "base16",
            },
        )

        @dataclass(kw_only=True)
        class Value:
            value: bytes = field(
                metadata={
                    "type": "Attribute",
                    "format": "base16",
                }
            )

    @dataclass(kw_only=True)
    class Dimension:
        """
        :ivar size: This attribute gives the size of this dimension of
            the connector as a fixed, unchangeable number.
        :ivar size_connector: This attribute references another
            connector by name, that gives the size of this dimension of
            the connector, e.g. a structural parameter or a constant of
            the underlying component that gives the dimension size.
        """

        size: None | int = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        size_connector: None | str = field(
            default=None,
            metadata={
                "name": "sizeConnector",
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
    :ivar meta_data: This element can specify additional meta data for
        the given resource. Multiple (or no) MetaData elements may be
        present.
    :ivar signature: This element can contain digital signature
        information on the data referenced by the enclosing element. It
        is left unspecified what types of signatures are used and/or
        available for now.  Multiple or no signature elements may be
        present.
    :ivar annotations:
    :ivar version: Version of SSV format, 1.0 or 2.0 for this release.
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
    meta_data: list[ParameterSet.MetaData] = field(
        default_factory=list,
        metadata={
            "name": "MetaData",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        },
    )
    signature: list[SignatureType] = field(
        default_factory=list,
        metadata={
            "name": "Signature",
            "type": "Element",
            "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
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
            "pattern": r"1[.]0|2[.]0",
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

    @dataclass(kw_only=True)
    class MetaData:
        """
        :ivar content: This optional element can contain inlined content
            of the resource meta data. If it is present, then the
            attribute source of the MetaData element must not be
            present.
        :ivar signature: This element can contain digital signature
            information on the data referenced by the enclosing element.
            It is left unspecified what types of signatures are used
            and/or available for now.  Multiple or no signature elements
            may be present.
        :ivar kind: This attribute indicates the kind of resource meta
            data that is referenced, i.e. what role it plays in relation
            to the resource being described.
        :ivar type_value: This mandatory attribute specifies the MIME
            type of the resource meta data, which does not have a
            default value.  If no specific MIME type can be indicated,
            then the type application/octet-stream is to be used.
        :ivar source: This attribute indicates the source of the
            resource meta data as a URI (cf. RFC 3986).  The base URI
            for the resolution of relative URIs is determined by the
            sourceBase attribute. If the source attribute is missing,
            the meta data is provided inline as contents of a Content
            element, which must not be present otherwise.
        :ivar source_base: Defines the base the source URI is resolved
            against:  If the attribute is missing or is specified as
            file, the source is resolved against the URI of the
            containing file.  If the containing model element has a
            source attribute, the sourceBase attribute can be specified
            as resource. In this case the URI is resolved against the
            (resolved) source URI of the containing model element. The
            last option allows the specification of meta data sources
            that reside inside a resource (for example an FMU) through
            relative URIs.
        :ivar id: This attribute gives the model element a file-wide
            unique id which can be referenced from other elements or via
            URI fragment identifier.
        :ivar description: This attribute gives a human readable longer
            description of the model element, which can be shown to the
            user where appropriate.
        """

        content: None | ContentType = field(
            default=None,
            metadata={
                "name": "Content",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            },
        )
        signature: list[SignatureType] = field(
            default_factory=list,
            metadata={
                "name": "Signature",
                "type": "Element",
                "namespace": "http://ssp-standard.org/SSP1/SystemStructureCommon",
            },
        )
        kind: MetaDataKind = field(
            metadata={
                "type": "Attribute",
            }
        )
        type_value: str = field(
            metadata={
                "name": "type",
                "type": "Attribute",
            }
        )
        source: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        source_base: MetaDataSourceBase = field(
            default=MetaDataSourceBase.FILE,
            metadata={
                "name": "sourceBase",
                "type": "Attribute",
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
