from __future__ import annotations

from dataclasses import dataclass, field

from pyssp_standard.standard.ls_ref.constants import (
    DEFAULT_LS_REF_DESCRIPTION,
    DEFAULT_LS_REF_NAME,
    DEFAULT_LS_REF_VERSION,
)


@dataclass
class LSRefRelated:
    source: str
    role: str
    type: str | None = None
    description: str | None = None


@dataclass
class LSRefManifestDocument:
    version: str = DEFAULT_LS_REF_VERSION
    name: str = DEFAULT_LS_REF_NAME
    description: str = DEFAULT_LS_REF_DESCRIPTION
    related: list[LSRefRelated] = field(default_factory=list)

    def add_related(
        self,
        source: str,
        role: str,
        *,
        type: str | None = None,
        description: str | None = None,
    ) -> LSRefRelated:
        related = LSRefRelated(source=source, role=role, type=type, description=description)
        self.related.append(related)
        return related
