from __future__ import annotations

from pathlib import Path

from pyssp_standard.standard.ls_ref.codec import LSRefExperimentsCodec, LSRefManifestCodec
from pyssp_standard.standard.ls_ref.validation import LSRefExperimentsSchemaValidator


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
    assert document.description == "Simple set of smoke tests to validate the integration of the SSP into a simulation engine."
    assert len(document.experiments) == 2
    assert document.experiments[0].name == "Test1"
    assert document.experiments[0].target == "SystemStructure.ssd"
    assert len(document.experiments[0].stimuli) == 1
    assert document.experiments[0].stimuli[0].source == "test1-in.csv"
    assert document.experiments[0].stimuli[0].mapping == "test1-in.ssm"
    assert len(document.experiments[0].references) == 1
    assert document.experiments[0].references[0].source == "test1-ref.csv"
    assert document.experiments[0].references[0].signals == ["y", "z"]
    assert len(document.experiments[1].parameters) == 1
    assert document.experiments[1].parameters[0].type is None
    assert len(document.experiments[1].references) == 1
    assert document.experiments[1].references[0].type == "application/hdf5"

    reparsed = LSRefExperimentsCodec().parse(LSRefExperimentsCodec().serialize(document))
    assert len(reparsed.experiments) == 2
    assert reparsed.experiments[1].parameters[0].source == "dynamic-params.ssv"
    assert reparsed.experiments[1].references[0].signals == ["u", "v"]


def test_experiments_resource_lists_round_trip():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Experiments name="multiple resources">
  <Experiment name="smoke">
    <Parameters source="baseline.ssv"/>
    <Parameters source="override.ssv" mapping="override.ssm"/>
    <Stimuli source="inputs_a.csv"/>
    <Stimuli source="inputs_b.csv"/>
    <References source="expected_a.csv">
      <Signal name="y"/>
    </References>
    <References source="expected_b.csv">
      <Signal name="z"/>
    </References>
  </Experiment>
</Experiments>
"""
    LSRefExperimentsSchemaValidator().validate_xml(xml)

    document = LSRefExperimentsCodec().parse(xml)
    experiment = document.experiments[0]

    assert [resource.source for resource in experiment.parameters] == [
        "baseline.ssv",
        "override.ssv",
    ]
    assert experiment.parameters[1].mapping == "override.ssm"
    assert [resource.source for resource in experiment.stimuli] == [
        "inputs_a.csv",
        "inputs_b.csv",
    ]
    assert [resource.source for resource in experiment.references] == [
        "expected_a.csv",
        "expected_b.csv",
    ]
    assert experiment.references[1].signals == ["z"]

    reparsed = LSRefExperimentsCodec().parse(LSRefExperimentsCodec().serialize(document))
    assert [resource.source for resource in reparsed.experiments[0].parameters] == [
        "baseline.ssv",
        "override.ssv",
    ]
