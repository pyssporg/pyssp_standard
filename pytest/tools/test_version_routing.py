from __future__ import annotations

from pyssp_standard.standard.version_routing import (
    StandardVersion,
    get_parse_stack,
    get_parse_stack_from_file,
    get_standard_version,
)


def test_detects_ssv_version_from_fixture(ssv2_fixture):
    standard = get_standard_version(ssv2_fixture.read_text(encoding="utf-8"))
    assert standard == StandardVersion(format="SSV", family="SSP", version="2.0")


def test_detects_ssv_1_0_from_xml():
    xml_text = """\
<ssv:ParameterSet xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues" version="1.0" name="Example">
  <ssv:Parameters />
</ssv:ParameterSet>
"""
    standard = get_standard_version(xml_text)
    assert standard == StandardVersion(format="SSV", family="SSP", version="1.0")


def test_resolves_registered_parse_stacks():
    ssp1 = get_parse_stack(StandardVersion(format="SSV", family="SSP", version="1.0"))
    ssd1 = get_parse_stack(StandardVersion(format="SSD", family="SSP", version="1.0"))
    ssm1 = get_parse_stack(StandardVersion(format="SSM", family="SSP", version="1.0"))
    ssp2 = get_parse_stack(StandardVersion(format="SSV", family="SSP", version="2.0"))
    fmi2 = get_parse_stack(StandardVersion(format="MD", family="FMI", version="2.0"))

    assert ssp1.generated_module.endswith("standard.ssp1.generated.ssv_generated_types")
    assert ssd1.generated_module.endswith("standard.ssp1.generated.ssd_generated_types")
    assert ssm1.generated_module.endswith("standard.ssp1.generated.ssm_generated_types")
    assert ssp2.generated_module.endswith("standard.ssp2.generated.ssv_generated_types")
    assert fmi2.generated_module.endswith("standard.fmi2.generated.model_description_generated_types")
    assert ssp1.generated_output_path.name == "ssv_generated_types.py"
    assert ssd1.generated_output_path.name == "ssd_generated_types.py"
    assert ssm1.generated_output_path.name == "ssm_generated_types.py"
    assert ssp2.generated_output_path.name == "ssv_generated_types.py"
    assert fmi2.generated_output_path.name == "model_description_generated_types.py"
    assert "pyssp_standard/standard/ssp1/generated" in str(ssp1.generated_output_path.parent)
    assert "pyssp_standard/standard/ssp1/generated" in str(ssd1.generated_output_path.parent)
    assert "pyssp_standard/standard/ssp1/generated" in str(ssm1.generated_output_path.parent)
    assert "pyssp_standard/standard/ssp2/generated" in str(ssp2.generated_output_path.parent)
    assert "pyssp_standard/standard/fmi2/generated" in str(fmi2.generated_output_path.parent)
    assert ssp1.schema_path.exists()
    assert ssd1.schema_path.exists()
    assert ssm1.schema_path.exists()
    assert ssp2.schema_path.exists()
    assert fmi2.schema_path.exists()


def test_detects_ssd_ssm_and_fmi2_versions():
    ssd = get_standard_version(
        '<ssd:SystemStructureDescription xmlns:ssd="http://ssp-standard.org/SSP1/SystemStructureDescription" version="1.0" name="x" />'
    )
    ssm = get_standard_version(
        '<ssm:ParameterMapping xmlns:ssm="http://ssp-standard.org/SSP1/SystemStructureParameterMapping" version="1.0" />'
    )
    fmi2 = get_standard_version('<fmiModelDescription fmiVersion="2.0" modelName="x" guid="g" />')

    assert ssd == StandardVersion(format="SSD", family="SSP", version="1.0")
    assert ssm == StandardVersion(format="SSM", family="SSP", version="1.0")
    assert fmi2 == StandardVersion(format="MD", family="FMI", version="2.0")


def test_resolve_from_file_uses_detection(ssv2_fixture):
    stack = get_parse_stack_from_file(ssv2_fixture)
    assert stack.standard.version == "2.0"
