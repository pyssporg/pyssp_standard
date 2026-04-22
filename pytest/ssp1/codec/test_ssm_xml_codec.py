from __future__ import annotations

from pyssp_standard.standard.ssp1.codec import Ssp1SsmCodec


def test_parses_embrace_fixture(embrace_ssm_fixture):
    document = Ssp1SsmCodec().parse(embrace_ssm_fixture.read_text(encoding="utf-8"))

    assert document.version == "1.0"
    assert len(document.mappings) > 10
    assert document.mappings[0].target == "ECS_HW.reqCoolingTemperature"
