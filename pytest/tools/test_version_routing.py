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
    ssb1 = get_parse_stack(StandardVersion(format="SSB", family="SSP", version="1.0"))
    ssp1 = get_parse_stack(StandardVersion(format="SSV", family="SSP", version="1.0"))
    ssd1 = get_parse_stack(StandardVersion(format="SSD", family="SSP", version="1.0"))
    ssm1 = get_parse_stack(StandardVersion(format="SSM", family="SSP", version="1.0"))
    ssp2 = get_parse_stack(StandardVersion(format="SSV", family="SSP", version="2.0"))
    fmi2 = get_parse_stack(StandardVersion(format="MD", family="FMI", version="2.0"))
    ls_ref_manifest = get_parse_stack(StandardVersion(format="LS-REF-MANIFEST", family="FMI", version="1.0.0-alpha.1"))
    ls_ref_experiments = get_parse_stack(StandardVersion(format="LS-REF-EXPERIMENTS", family="FMI", version="1.0.0-alpha.1"))

    assert ssb1.schema_path.exists()
    assert ssp1.schema_path.exists()
    assert ssd1.schema_path.exists()
    assert ssm1.schema_path.exists()
    assert ssp2.schema_path.exists()
    assert fmi2.schema_path.exists()
    assert ls_ref_manifest.schema_path.exists()
    assert ls_ref_experiments.schema_path.exists()


def test_detects_ssb_ssd_ssm_and_fmi2_versions():
    ssb = get_standard_version(
        '<ssb:SignalDictionary xmlns:ssb="http://ssp-standard.org/SSP1/SystemStructureSignalDictionary" version="1.0" />'
    )
    ssd = get_standard_version(
        '<ssd:SystemStructureDescription xmlns:ssd="http://ssp-standard.org/SSP1/SystemStructureDescription" version="1.0" name="x" />'
    )
    ssm = get_standard_version(
        '<ssm:ParameterMapping xmlns:ssm="http://ssp-standard.org/SSP1/SystemStructureParameterMapping" version="1.0" />'
    )
    fmi2 = get_standard_version('<fmiModelDescription fmiVersion="2.0" modelName="x" guid="g" />')

    assert ssb == StandardVersion(format="SSB", family="SSP", version="1.0")
    assert ssd == StandardVersion(format="SSD", family="SSP", version="1.0")
    assert ssm == StandardVersion(format="SSM", family="SSP", version="1.0")
    assert fmi2 == StandardVersion(format="MD", family="FMI", version="2.0")


def test_detects_ls_ref_versions():
    manifest = get_standard_version(
        '<fmiReferences xmlns:fmi-ls="http://fmi-standard.org/fmi-ls-manifest" '
        'fmi-ls:fmi-ls-name="org.fmi-standard.fmi-ls-ref" '
        'fmi-ls:fmi-ls-version="1.0.0-alpha.1" '
        'fmi-ls:fmi-ls-description="Layered Standard providing information on related files included in an FMU.">'
        "</fmiReferences>"
    )
    experiments = get_standard_version('<Experiments name="Smoke Tests" />')

    assert manifest == StandardVersion(format="LS-REF-MANIFEST", family="FMI", version="1.0.0-alpha.1")
    assert experiments == StandardVersion(format="LS-REF-EXPERIMENTS", family="FMI", version="1.0.0-alpha.1")


def test_resolve_from_file_uses_detection(ssv2_fixture):
    stack = get_parse_stack_from_file(ssv2_fixture)
    assert stack.standard.version == "2.0"
