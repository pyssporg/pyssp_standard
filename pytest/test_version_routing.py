from pathlib import Path

import pytest

from pyssp_standard.standard.version_routing import (
    StandardVersion,
    detect_ssv_standard_version,
    resolve_parse_stack,
    resolve_parse_stack_from_file,
)


def test_detect_ssv_version_from_fixture():
    path = Path("pytest/doc/ssv2_ex.ssv")
    standard = detect_ssv_standard_version(path.read_text(encoding="utf-8"))
    assert standard == StandardVersion(format="ssv", family="SSP", version="2.0")


def test_detect_ssv_version_1_0_from_xml():
    xml_text = """\
<ssv:ParameterSet xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues" version="1.0" name="Example">
  <ssv:Parameters />
</ssv:ParameterSet>
"""
    standard = detect_ssv_standard_version(xml_text)
    assert standard == StandardVersion(format="ssv", family="SSP", version="1.0")


def test_resolve_ssv_parse_stacks():
    ssp1 = resolve_parse_stack(StandardVersion(format="ssv", family="SSP", version="1.0"))
    ssp2 = resolve_parse_stack(StandardVersion(format="ssv", family="SSP", version="2.0"))

    assert ssp1.generated_module.endswith("ssp1.generated.ssv_generated_types")
    assert ssp2.generated_module.endswith("ssp2.generated.ssv_generated_types")
    assert ssp1.generated_output_path.exists()
    assert ssp2.generated_output_path.exists()
    assert ssp1.schema_path.exists()
    assert ssp2.schema_path.exists()


def test_resolve_from_file_uses_detection():
    stack = resolve_parse_stack_from_file(Path("pytest/doc/ssv2_ex.ssv"), format_hint="ssv")
    assert stack.standard.version == "2.0"


def test_unknown_version_raises():
    with pytest.raises(ValueError):
        detect_ssv_standard_version(
            """\
<ssv:ParameterSet xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues" version="3.0" name="X">
  <ssv:Parameters />
</ssv:ParameterSet>
"""
        )
