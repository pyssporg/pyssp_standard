from __future__ import annotations

from importlib import import_module
import sys


_ALIASES = {
    "common_content_ssc": "pyssp_standard_v1.common_content_ssc",
    "fmu": "pyssp_standard_v1.fmu",
    "parameter_types": "pyssp_standard_v1.parameter_types",
    "srmd": "pyssp_standard_v1.srmd",
    "ssb": "pyssp_standard_v1.ssb",
    "ssd": "pyssp_standard_v1.ssd",
    "ssm": "pyssp_standard_v1.ssm",
    "ssp": "pyssp_standard_v1.ssp",
    "standard": "pyssp_standard_v1.standard",
    "transformation_types": "pyssp_standard_v1.transformation_types",
    "unit": "pyssp_standard_v1.unit",
    "unit_conversion": "pyssp_standard_v1.unit_conversion",
    "utils": "pyssp_standard_v1.utils",
}


def _install_module_aliases() -> None:
    for public_name, legacy_name in _ALIASES.items():
        sys.modules[f"{__name__}.{public_name}"] = import_module(legacy_name)


_install_module_aliases()

from pyssp_standard.ssv import SSV  # noqa: E402,F401
from pyssp_standard_v1 import (  # noqa: E402,F401
    Annotation,
    Annotations,
    Classification,
    ClassificationEntry,
    Connection,
    FMU,
    SRMD,
    SSB,
    SSD,
    SSM,
    SSP,
    Transformation,
    classification_parser,
)

__all__ = [
    "Annotation",
    "Annotations",
    "Classification",
    "ClassificationEntry",
    "Connection",
    "FMU",
    "SRMD",
    "SSB",
    "SSD",
    "SSM",
    "SSP",
    "SSV",
    "Transformation",
    "classification_parser",
]
