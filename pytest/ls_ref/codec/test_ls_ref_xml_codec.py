from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ls_ref.codec import LSRefExperimentsCodec, LSRefManifestCodec


def test_parses_manifest_example():
    fixture = Path("3rdParty/ls-ref/docs/examples/fmi_ls_ref_manifest_example.xml")
    document = LSRefManifestCodec().parse(fixture.read_text(encoding="utf-8"))

    assert document.name == "org.fmi-standard.fmi-ls-ref"
    assert document.version == "1.0.0-alpha.1"
    assert document.description == "Layered Standard providing information on related files included in an FMU."
    assert len(document.related) == 6
    assert document.related[0].role == "model"
    assert document.related[1].role == "parameter"
    assert document.related[5].type == "application/x-ma-ls-experiments"

    reparsed = LSRefManifestCodec().parse(LSRefManifestCodec().serialize(document))
    assert len(reparsed.related) == 6
    assert reparsed.related[0].source == "modelica/mymodel.mo"


def test_parses_experiments_example():
    fixture = Path("3rdParty/ls-ref/docs/examples/fmi_ls_ref_experiments_example.xml")
    document = LSRefExperimentsCodec().parse(fixture.read_text(encoding="utf-8"))

    assert document.name == "Smoke Tests"
    assert document.description == "Simple set of smoke tests to validate the integration of the FMU into a simulation engine."
    assert len(document.experiments) == 2
    assert document.experiments[0].name == "Test1"
    assert document.experiments[0].stimuli is not None
    assert document.experiments[0].stimuli.source == "test1-in.csv"
    assert document.experiments[0].references is not None
    assert document.experiments[0].references.source == "test1-ref.csv"
    assert document.experiments[1].parameters is not None
    assert document.experiments[1].parameters.type is None
    assert document.experiments[1].references is not None
    assert document.experiments[1].references.type == "application/hdf5"

    reparsed = LSRefExperimentsCodec().parse(LSRefExperimentsCodec().serialize(document))
    assert len(reparsed.experiments) == 2
    assert reparsed.experiments[1].parameters is not None
    assert reparsed.experiments[1].parameters.source == "dynamic-params.ssv"
