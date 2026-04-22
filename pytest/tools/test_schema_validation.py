from pyssp_standard.standard.fmi2.validation import Fmi2ModelDescriptionSchemaValidator
from pyssp_standard.standard.ssp1.validation import (
    Ssp1SsdSchemaValidator,
    Ssp1SsmSchemaValidator,
    Ssp1SsvSchemaValidator,
)


def test_schema_validators_use_in_library_schema_paths():
    validators = [
        Ssp1SsdSchemaValidator(),
        Ssp1SsmSchemaValidator(),
        Ssp1SsvSchemaValidator(),
        Fmi2ModelDescriptionSchemaValidator(),
    ]

    for validator in validators:
        assert validator.schema_path.exists()
        assert "pyssp_standard/schema" in validator.schema_path.as_posix()


def test_schema_validators_accept_real_fixture_xml(
    embrace_ssd_fixture,
    embrace_ssm_fixture,
    external_ssv_fixture,
    model_description_fixture,
):
    Ssp1SsdSchemaValidator().validate_xml(embrace_ssd_fixture.read_text(encoding="utf-8"))
    Ssp1SsmSchemaValidator().validate_xml(embrace_ssm_fixture.read_text(encoding="utf-8"))
    Ssp1SsvSchemaValidator().validate_xml(external_ssv_fixture.read_text(encoding="utf-8"))
    Fmi2ModelDescriptionSchemaValidator().validate_xml(model_description_fixture.read_text(encoding="utf-8"))
