from __future__ import annotations

from types import SimpleNamespace

import pytest
from xsdata.models.datatype import XmlDateTime

from pyssp_standard.standard.ssp1.codec.ssc_xsdata_mapper import Ssp1SscXsdataMapper
from pyssp_standard.standard.ssp1.generated.ssd_generated_types import ConnectorKind, Tconnectors
from pyssp_standard.standard.ssp1.generated.ssm_generated_types import TmappingEntry
from pyssp_standard.standard.ssp1.generated.ssv_generated_types import Tparameter, Tunit
from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1BaseUnit, Ssp1DocumentMetadata, Ssp1Transformation, Ssp1Unit


def test_base_unit_from_dict_normalizes_schema_attribute_names():
    unit = Ssp1BaseUnit.from_dict({"kg": 1, "A": -2, "K": 3, "factor": 2.5})

    assert unit.kg == 1
    assert unit.a == -2
    assert unit.k == 3
    assert unit.factor == 2.5


def test_document_metadata_round_trip_preserves_common_fields():
    generated = SimpleNamespace(
        id="meta-id",
        description="demo",
        author="tester",
        fileversion="1.2",
        copyright="copyright",
        license="MIT",
        generation_tool="tool",
        generation_date_and_time=XmlDateTime.from_string("2026-04-22T09:15:00Z"),
    )

    metadata = Ssp1SscXsdataMapper.read_document_metadata(generated)
    written = Ssp1SscXsdataMapper.write_document_metadata(metadata)

    assert metadata == Ssp1DocumentMetadata(
        id="meta-id",
        description="demo",
        author="tester",
        fileversion="1.2",
        copyright="copyright",
        license="MIT",
        generation_tool="tool",
        generation_date_and_time="2026-04-22T09:15:00Z",
    )
    assert written["generation_date_and_time"] == "2026-04-22T09:15:00Z"


def test_unit_round_trip_preserves_common_content_fields():
    unit = Ssp1Unit(
        name="km",
        id="u1",
        description="distance",
        base_unit=Ssp1BaseUnit(m=1, factor=1000.0),
    )

    generated = Ssp1SscXsdataMapper.write_unit(unit)
    reparsed = Ssp1SscXsdataMapper.read_unit(generated)

    assert generated == Tunit(
        name="km",
        id="u1",
        description="distance",
        base_unit=Tunit.BaseUnit(m=1, factor=1000.0),
    )
    assert reparsed == Ssp1Unit(
        name="km",
        id="u1",
        description="distance",
        base_unit=Ssp1BaseUnit(
            kg=0,
            m=1,
            s=0,
            a=0,
            k=0,
            mol=0,
            cd=0,
            rad=0,
            factor=1000.0,
            offset=0.0,
        ),
    )


@pytest.mark.parametrize(
    ("type_name", "attributes"),
    [
        ("Real", {"value": "1.5", "unit": "m"}),
        ("Integer", {"value": "7"}),
        ("Boolean", {"value": "true"}),
        ("String", {"value": "demo"}),
        ("Enumeration", {"value": "2", "name": "On"}),
        ("Binary", {"value": "cafe", "mime-type": "application/octet-stream"}),
    ],
)
def test_parameter_type_round_trip_preserves_supported_common_variants(type_name: str, attributes: dict[str, str]):
    generated = Ssp1SscXsdataMapper.write_parameter_type("p", type_name, attributes)
    reparsed_type, reparsed_attributes = Ssp1SscXsdataMapper.read_parameter_type(generated)

    assert generated.name == "p"
    assert reparsed_type == type_name
    assert reparsed_attributes == attributes


def test_connector_type_round_trip_preserves_shared_type_choice():
    generated = Tconnectors.Connector(name="speed", kind=ConnectorKind.INPUT)
    Ssp1SscXsdataMapper.apply_connector_type(generated, "Enumeration", {"name": "Gear"})

    type_name, attributes = Ssp1SscXsdataMapper.read_connector_type(generated)

    assert type_name == "Enumeration"
    assert attributes == {"name": "Gear"}


@pytest.mark.parametrize(
    ("transformation", "expected_kind"),
    [
        (
            Ssp1Transformation(
                type_name="LinearTransformation",
                attributes={"factor": "2", "offset": "0.5"},
            ),
            "linear_transformation",
        ),
        (Ssp1Transformation(type_name="BooleanMappingTransformation"), "boolean_mapping_transformation"),
        (Ssp1Transformation(type_name="IntegerMappingTransformation"), "integer_mapping_transformation"),
        (
            Ssp1Transformation(type_name="EnumerationMappingTransformation"),
            "enumeration_mapping_transformation",
        ),
    ],
)
def test_transformation_round_trip_preserves_shared_transformation_choice(
    transformation: Ssp1Transformation,
    expected_kind: str,
):
    generated = TmappingEntry(source="a", target="b")

    Ssp1SscXsdataMapper.apply_transformation(generated, transformation)
    reparsed = Ssp1SscXsdataMapper.read_transformation(generated)

    assert getattr(generated, expected_kind) is not None
    assert reparsed == transformation


def test_parameter_type_writer_rejects_unknown_type():
    with pytest.raises(ValueError, match="Unsupported SSV1 parameter type 'Custom'"):
        Ssp1SscXsdataMapper.write_parameter_type("p", "Custom", {})
