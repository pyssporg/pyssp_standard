"""Shared external reference specifications for document resolution.

EXTERNAL_REFERENCE_SPECS defines which document types (SSV, SSM, etc.)
are referenced by which model types (Ssd1ParameterBinding, etc.).
"""

from __future__ import annotations

from pyssp_standard.common.document_runtime import ExternalReferenceSpec
from pyssp_standard.ssm import SSM
from pyssp_standard.ssv import SSV
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1ParameterBinding,
    Ssd1ParameterMappingReference,
)


EXTERNAL_REFERENCE_SPECS = (
    ExternalReferenceSpec(
        owner_type=Ssd1ParameterBinding,
        source_attr="source",
        document_attr="parameter_set",
        facade_type=SSV,
    ),
    ExternalReferenceSpec(
        owner_type=Ssd1ParameterMappingReference,
        source_attr="source",
        document_attr="mapping",
        facade_type=SSM,
    ),
)