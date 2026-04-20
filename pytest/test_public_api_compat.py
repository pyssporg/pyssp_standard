from pyssp_standard import SSD, SSV, SSP, SSB, SSM, FMU, SRMD
from pyssp_standard.common_content_ssc import Annotation, Annotations
from pyssp_standard.ssd import Connection


def test_top_level_exports_are_available():
    assert SSD is not None
    assert SSV is not None
    assert SSP is not None
    assert SSB is not None
    assert SSM is not None
    assert FMU is not None
    assert SRMD is not None


def test_submodule_imports_are_available():
    assert Connection is not None
    assert Annotation is not None
    assert Annotations is not None
