from __future__ import annotations

import shutil
import sys
from pathlib import Path

DEMO_ROOT = Path("docs/RFC/architecture-review/demo")
sys.path.insert(0, str(DEMO_ROOT.parent))

from demo.generated.generate_ssv_bindings import generate_bindings
from demo.codec.ssv_hybrid_codec import Ssv2HybridCodec
from demo.public_api import PublicSSP

SSV_FIXTURE = DEMO_ROOT / "__data__" / "external_values.ssv"


def test_generate_bindings_wrapper_writes_python_module(tmp_path):
    output_path = tmp_path / "bindings.py"
    generate_bindings(output_path=output_path)

    generated = output_path.read_text(encoding="utf-8")
    assert "class ParameterSet" in generated
    assert "class Tparameter" in generated


def test_xsdata_codec_parses_real_only_fixture():
    xml_text = SSV_FIXTURE.read_text(encoding="utf-8")

    model = Ssv2HybridCodec().parse(xml_text)

    assert model.name == "ControllerExternal"
    assert model.version == "2.0"
    assert [parameter.name for parameter in model.parameters] == ["gain"]


def test_public_ssp_xsdata_codec_round_trip(tmp_path):
    source_dir = DEMO_ROOT / "__data__"
    work_dir = tmp_path / "demo_data"
    shutil.copytree(source_dir, work_dir)

    ssp = PublicSSP(work_dir.parent, ssv_codec_name="xsdata")
    doc = ssp.load_ssd(Path("demo_data") / "mixed_example.ssd")

    for binding in doc.parameter_bindings:
        if binding.parameter_set is not None:
            binding.parameter_set.add_real_parameter("offset", 2.0)

    result_path = Path("demo_data") / "result" / "mixed_example.ssd"
    ssp.save_ssd(result_path, doc)

    reloaded = ssp.load_ssd(result_path)
    resolved = [binding for binding in reloaded.parameter_bindings if binding.parameter_set is not None]

    assert len(resolved) == 2
    assert all(any(param.name == "offset" for param in binding.parameter_set.parameters) for binding in resolved)
