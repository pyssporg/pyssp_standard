from pathlib import Path


class ModelicaStandard:
    namespaces = {
        # SSP
        "ssc": "http://ssp-standard.org/SSP1/SystemStructureCommon",
        "ssv": "http://ssp-standard.org/SSP1/SystemStructureParameterValues",
        "ssb": "http://ssp-standard.org/SSP1/SystemStructureSignalDictionary",
        "ssm": "http://ssp-standard.org/SSP1/SystemStructureParameterMapping",
        "ssd": "http://ssp-standard.org/SSP1/SystemStructureDescription",
        # SRMD
        "stc": "http://ssp-standard.org/SSPTraceability1/SSPTraceabilityCommon",
        "srmd": "http://ssp-standard.org/SSPTraceability1/SimulationResourceMetaData",
        # FMI
        "fmi30": "",
        # XLink
        "xlink": "http://www.w3.org/1999/xlink"
    }

    _repo_root = Path(__file__).resolve().parent.parent
    _installed_resource_path = Path.home() / ".local" / "lib" / "python3.10" / "site-packages" / "pyssp_standard" / "resources"
    __resource_path = _repo_root / "3rdParty" / "SSP1" / "schema"

    @staticmethod
    def _fallback_resource(*candidates: Path) -> Path:
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]
    schemas = {
        # SSP
        "ssc": __resource_path / "SystemStructureCommon.xsd",
        "ssd": __resource_path / "SystemStructureDescription.xsd",
        "ssd11": _repo_root / "3rdParty" / "SSP1" / "schema" / "SystemStructureDescription11.xsd",
        "ssm": __resource_path / "SystemStructureParameterMapping.xsd",
        "ssv": __resource_path / "SystemStructureParameterValues.xsd",
        "ssb": __resource_path / "SystemStructureSignalDictionary.xsd",
        # SSP 2.0
        "ssc2": _repo_root / "3rdParty" / "SSP2" / "schema" / "SystemStructureCommon.xsd",
        "ssd2": _repo_root / "3rdParty" / "SSP2" / "schema" / "SystemStructureDescription.xsd",
        "ssd2_11": _repo_root / "3rdParty" / "SSP2" / "schema" / "SystemStructureDescription11.xsd",
        "ssm2": _repo_root / "3rdParty" / "SSP2" / "schema" / "SystemStructureParameterMapping.xsd",
        "ssv2": _repo_root / "3rdParty" / "SSP2" / "schema" / "SystemStructureParameterValues.xsd",
        "ssb2": _repo_root / "3rdParty" / "SSP2" / "schema" / "SystemStructureSignalDictionary.xsd",
        # SSPTraceabillity
        "stc11": _fallback_resource.__func__(
            _repo_root / "pyssp_standard_v1" / "resources" / "STC11.xsd",
            _installed_resource_path / "STC11.xsd",
        ),
        "srmd11": _fallback_resource.__func__(
            _repo_root / "pyssp_standard_v1" / "resources" / "SRMD11.xsd",
            _installed_resource_path / "SRMD11.xsd",
        ),
        # FMI
        "fmi30": _repo_root / "3rdParty" / "FMI3" / "schema" / "fmi3ModelDescription.xsd",
    }
