from __future__ import annotations


FMI_LS_MANIFEST_NAMESPACE = "http://fmi-standard.org/fmi-ls-manifest"
FMI_LS_MANIFEST_PREFIX = "fmi-ls"

DEFAULT_LS_REF_VERSION = "1.0.0-alpha.1"
DEFAULT_LS_REF_NAME = "org.fmi-standard.fmi-ls-ref"
DEFAULT_LS_REF_DESCRIPTION = "Layered Standard providing information on related files included in an FMU."

DEFAULT_RELATED_TYPE = "application/octet-stream"
DEFAULT_EXPERIMENT_PARAMETERS_TYPE = "application/x-ssp-parameter-set"
DEFAULT_EXPERIMENT_STIMULI_TYPE = "text/csv"
DEFAULT_EXPERIMENT_REFERENCES_TYPE = "text/csv"

MANIFEST_ROOT_TAG = "fmiReferences"
RELATED_TAG = "Related"

EXPERIMENTS_ROOT_TAG = "Experiments"
EXPERIMENT_TAG = "Experiment"
PARAMETERS_TAG = "Parameters"
STIMULI_TAG = "Stimuli"
REFERENCES_TAG = "References"
