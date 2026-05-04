from __future__ import annotations

from pyssp_standard.ls_ref import LSRefExperiments, LSRefManifest


def test_manifest_facade_round_trip(tmp_path):
    path = tmp_path / "fmi-ls-manifest.xml"

    with LSRefManifest(path, "w") as manifest:
        manifest.xml.add_related(
            "modelica/mymodel.mo",
            "model",
            type="text/modelica",
            description="Modelica Model Source",
        )
        manifest.xml.add_related(
            "baseline-params.ssv",
            "parameter",
            type="application/x-ssp-parameter-set",
        )
        assert manifest.check_compliance() is True

    with LSRefManifest(path) as manifest:
        assert manifest.xml.name == "org.fmi-standard.fmi-ls-ref"
        assert len(manifest.xml.related) == 2
        assert manifest.xml.related[0].source == "modelica/mymodel.mo"
        assert manifest.xml.related[1].role == "parameter"


def test_experiments_facade_round_trip(tmp_path):
    path = tmp_path / "fmi-ls-experiments.xml"

    with LSRefExperiments(path, "w") as experiments:
        experiment = experiments.xml.add_experiment(
            "Smoke Test",
            description="Simple smoke test",
            start_time=0.0,
            stop_time=10.0,
            step_size=0.1,
        )
        experiment.add_parameters("baseline-params.ssv")
        experiment.add_stimuli("stimuli.csv", type="text/csv")
        experiment.add_references("references.csv")
        assert experiments.check_compliance() is True

    with LSRefExperiments(path) as experiments:
        assert experiments.xml.name == "fmi-ls-experiments"
        assert len(experiments.xml.experiments) == 1
        stored = experiments.xml.experiments[0]
        assert stored.name == "Smoke Test"
        assert stored.parameters is not None
        assert stored.parameters.source == "baseline-params.ssv"
        assert stored.stimuli is not None
        assert stored.references is not None
