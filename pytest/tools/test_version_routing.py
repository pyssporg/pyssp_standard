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
    ssp2 = get_parse_stack(StandardVersion(format="SSV", family="SSP", version="2.0"))

    assert ssp1.generated_module.endswith("ssp1.generated.ssv_generated_types")
    assert ssp2.generated_module.endswith("ssp2.generated.ssv_generated_types")
    assert ssp1.generated_output_path.name == "ssv_generated_types.py"
    assert ssp2.generated_output_path.name == "ssv_generated_types.py"
    assert "pyssp_standard/ssp1/generated" in str(ssp1.generated_output_path.parent)
    assert "pyssp_standard/ssp2/generated" in str(ssp2.generated_output_path.parent)
    assert ssp1.schema_path.exists()
    assert ssp2.schema_path.exists()


def test_resolve_from_file_uses_detection(ssv2_fixture):
    stack = get_parse_stack_from_file(ssv2_fixture)
    assert stack.standard.version == "2.0"
