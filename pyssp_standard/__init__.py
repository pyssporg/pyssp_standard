from pathlib import Path

from pyssp_standard.fmu import FMU
from pyssp_standard.md import ModelDescription
from pyssp_standard.ls_ref import LSRefExperiments, LSRefManifest
from pyssp_standard.srmd import SRMD
from pyssp_standard.ssb import SSB
from pyssp_standard.ssd import SSD
from pyssp_standard.ssm import SSM
from pyssp_standard.ssp import SSP
from pyssp_standard.ssv import SSV


def get_repo_root(*, file: str = "__SSP_REF_ROOT__") -> Path:
    current = Path(__file__).resolve()
    for candidate in (current.parent, *current.parents):
        marker = candidate / file
        if marker.exists():
            return candidate
    raise FileNotFoundError(f"Could not locate repository root marker '{file}' from {current}")


__all__ = [
    "FMU",
    "LSRefExperiments",
    "LSRefManifest",
    "ModelDescription",
    "SRMD",
    "SSB",
    "SSD",
    "SSM",
    "SSP",
    "SSV",
    "get_repo_root",
]
