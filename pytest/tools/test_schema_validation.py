import pytest

from pyssp_standard.standard.fmi2.validation import Fmi2ModelDescriptionSchemaValidator
from pyssp_standard.standard.ssp1.validation import (
    Ssp1SsbSchemaValidator,
    Ssp1SsbSemanticValidator,
    Ssp1SsdSchemaValidator,
    Ssp1SsmSemanticValidator,
    Ssp1SsmSchemaValidator,
    Ssp1SsvSemanticValidator,
    Ssp1SsvSchemaValidator,
)
from pyssp_standard.standard.ssp1.model import Ssp1ParameterMapping, Ssp1ParameterSet, Ssp1SignalDictionary


def test_schema_validators_use_in_library_schema_paths():
    validators = [
        Ssp1SsdSchemaValidator(),
        Ssp1SsbSchemaValidator(),
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
    Ssp1SsbSchemaValidator().validate_xml(
        '<ssb:SignalDictionary xmlns:ssb="http://ssp-standard.org/SSP1/SystemStructureSignalDictionary" xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon" version="1.0"><ssb:DictionaryEntry name="speed"><ssc:Real /></ssb:DictionaryEntry></ssb:SignalDictionary>'
    )
    Ssp1SsmSchemaValidator().validate_xml(embrace_ssm_fixture.read_text(encoding="utf-8"))
    Ssp1SsvSchemaValidator().validate_xml(external_ssv_fixture.read_text(encoding="utf-8"))
    Fmi2ModelDescriptionSchemaValidator().validate_xml(model_description_fixture.read_text(encoding="utf-8"))


def test_schema_validator_rejects_invalid_xml_with_useful_error_prefix():
    xml_text = '<ssv:ParameterSet xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues" version="1.0" />'

    with pytest.raises(ValueError, match="SSV XML failed XSD validation"):
        Ssp1SsvSchemaValidator().validate_xml(xml_text)


def test_ssv_validator_rejects_duplicate_parameter_names():
    model = Ssp1ParameterSet(name="Example", version="1.0")
    model.add_parameter("gain", value=1.0)
    model.add_parameter("gain", value=2.0)

    with pytest.raises(ValueError, match="Duplicate parameter 'gain'"):
        Ssp1SsvSemanticValidator().validate(model)


def test_ssm_validator_rejects_duplicate_mapping_targets():
    model = Ssp1ParameterMapping(version="1.0")
    model.add_mapping("a", "target")
    model.add_mapping("b", "target")

    with pytest.raises(ValueError, match="Duplicate mapping target 'target'"):
        Ssp1SsmSemanticValidator().validate(model)


def test_ssb_validator_rejects_duplicate_dictionary_entry_names():
    model = Ssp1SignalDictionary(version="1.0")
    model.add_entry("speed", "Real")
    model.add_entry("speed", "Real")

    with pytest.raises(ValueError, match="Duplicate dictionary entry 'speed'"):
        Ssp1SsbSemanticValidator().validate(model)
