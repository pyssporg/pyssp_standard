from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from pyssp_standard.common.document_runtime import ExternalReferenceSpec
from pyssp_standard.common.reference_discovery import discover_external_references


@dataclass
class _LeafSpec:
    """A dataclass that matches an ExternalReferenceSpec."""
    source: str | None = None
    other_attr: str | None = None


@dataclass
class _Container:
    elements: list[Any] = field(default_factory=list)


LEAF_SPEC = ExternalReferenceSpec(
    owner_type=_LeafSpec,
    source_attr="source",
    document_attr="other_attr",
    facade_type=object,
)


class TestDiscoverExternalReferences:

    def test_no_references(self):
        """When no element matches the spec, result is empty."""
        root = _Container(elements=[_Container()])
        result = discover_external_references(root, (LEAF_SPEC,))
        assert result == []

    def test_single_reference(self):
        """A single matching element is found."""
        leaf = _LeafSpec(source="ref.xml")
        root = _Container(elements=[leaf])
        result = discover_external_references(root, (LEAF_SPEC,))
        assert len(result) == 1
        assert result[0][0] is leaf
        assert result[0][1] is LEAF_SPEC

    def test_multiple_references(self):
        """Multiple matching elements at different depths are all found."""
        leaf1 = _LeafSpec(source="a.xml")
        leaf2 = _LeafSpec(source="b.xml")
        inner = _Container(elements=[leaf2])
        root = _Container(elements=[leaf1, inner])
        result = discover_external_references(root, (LEAF_SPEC,))
        assert len(result) == 2
        sources = {r[0].source for r in result}
        assert sources == {"a.xml", "b.xml"}

    def test_nested_structure(self):
        """Deeply nested matching elements are found."""
        leaf = _LeafSpec(source="deep.xml")
        level3 = _Container(elements=[leaf])
        level2 = _Container(elements=[level3])
        level1 = _Container(elements=[level2])
        root = _Container(elements=[level1])
        result = discover_external_references(root, (LEAF_SPEC,))
        assert len(result) == 1
        assert result[0][0].source == "deep.xml"

    def test_no_source_skipped(self):
        """Elements matching the type but with no source are skipped."""
        leaf = _LeafSpec(source=None)
        root = _Container(elements=[leaf])
        result = discover_external_references(root, (LEAF_SPEC,))
        assert result == []

    def test_multiple_spec_types(self):
        """Elements are matched against multiple specs."""
        @dataclass
        class _OtherSpec:
            path: str | None = None

        other_spec = ExternalReferenceSpec(
            owner_type=_OtherSpec,
            source_attr="path",
            document_attr="data",
            facade_type=object,
        )
        leaf = _LeafSpec(source="a.xml")
        other = _OtherSpec(path="b.xml")
        root = _Container(elements=[leaf, other])
        result = discover_external_references(root, (LEAF_SPEC, other_spec))
        assert len(result) == 2

    def test_cycle_does_not_loop(self):
        """Cyclic references in the dataclass graph do not cause infinite loops."""
        leaf = _LeafSpec(source="ref.xml")
        container = _Container(elements=[leaf])
        leaf.other_attr = container  # back-reference
        result = discover_external_references(container, (LEAF_SPEC,))
        assert len(result) == 1

    def test_primitive_values_skipped(self):
        """Primitive values like strings/ints/bools are not traversed."""
        leaf = _LeafSpec(source="ref.xml")
        root = _Container(elements=[leaf, "string", 42, True, b"bytes"])
        result = discover_external_references(root, (LEAF_SPEC,))
        assert len(result) == 1