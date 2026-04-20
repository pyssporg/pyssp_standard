# Parse/Serialize Granularity: File vs XML Element

## Context
The current architecture discussion includes where parse/serialize responsibility should live:
- file-level (`path`/document oriented),
- XML element-level (fragment oriented).

This note captures tradeoffs and a recommended approach for this project.

## Option A: File-Level Parse/Serialize

### Advantages
- Simple API surface for common workflows.
- Natural fit for document-root schema validation.
- Easy to produce canonical complete outputs.
- Lower conceptual overhead for small codebases.

### Drawbacks
- Harder reuse for inline fragments (e.g., inline `ParameterSet` in SSD).
- Tighter coupling to I/O and path context.
- More difficult composition across codecs.
- Unit testing is heavier (requires full document fixtures).

## Option B: XML Element-Level Parse/Serialize

### Advantages
- Reusable mapping logic for both full documents and embedded fragments.
- Cleaner layering: codec remains transformation-only.
- Better composability in parent codecs.
- Easier focused unit tests on small XML snippets.
- Reduces hidden side effects from path/base-uri assumptions.

### Drawbacks
- More context plumbing (namespaces, defaults, metadata ownership).
- Root-level validation needs explicit adapter stage.
- Orchestrators need more assembly/disassembly code.
- Possible ambiguity around who owns full-document attributes/order.

## Project Fit Assessment
Given the current architecture direction:
- SSD codec is XML-only,
- SSP-level orchestration resolves cross-file references,
- inline and external representations must share logic,

element-level core parsing/serialization is a better fit than file-level-only codecs.

## Recommended Hybrid
Use a two-layer codec contract:

1. Element-oriented core codecs:
- `parse_element(element_or_xml_fragment) -> domain_model`
- `serialize_element(domain_model) -> element_or_xml_fragment`

2. Thin document adapters:
- `parse_document(xml_text) -> domain_model`
  - extracts root/sections and delegates to element codecs
- `serialize_document(domain_model) -> xml_text`
  - assembles root attrs/ns/ordering and embeds element outputs

Keep file operations out of both layers:
- File I/O stays in archive/session/repository/orchestrator.

## Impact on Testing
Add explicit test buckets:
- Element codec tests (fast, focused, no filesystem).
- Document adapter tests (namespace/root assembly).
- Orchestrator tests (cross-file resolution behavior).
- Schema validation tests at full-document boundaries.


Lets go with the recommended hybrid