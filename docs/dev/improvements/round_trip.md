I am designing a Python prototype for XML de/serialization where element and attribute order must be preserved.

The immediate goal is a focused prototype. The final goal is to feed the approach back into `pyssp_standard` if the prototype proves sound.

# Round-Trip Prototype

## Core idea

Treat XML as a structured, ordered document, not just as data.

- The XML tree is the source of truth.
- Typed or domain objects are views over that tree.
- Serialization always comes from the XML tree.

## Prototype scope

- Use Python.
- Prefer stdlib `xml.etree.ElementTree` if it is feasible for the required fidelity.
- Minimize custom parsing and patching logic.
- Push reusable behavior into generic helpers rather than many special-purpose classes.
- Keep the domain layer clean and focused on domain concepts.

## Layer 1: Ordered XML document model

This layer owns round-tripping.

### Preserve

- Element order.
- Attribute order.
- Mixed content order where feasible with the chosen backend.
- Comments and processing instructions if feasible in the prototype.
- Namespace correctness.
- Original namespace prefixes if possible.
- Must preserve namespace prefix spelling if untouched, best effort otherwise.

### Do not preserve exactly

- Original whitespace and indentation.
- Attribute quote style.
- Byte-for-byte formatting.

Pretty printing and readability are more important than preserving original formatting whitespace.
Output may be pretty-printed and differ in whitespace.

### Out of scope for now

- CDATA preservation as a distinct fidelity target.

## Layer 2: Typed or domain projection

This layer exists for application logic and ergonomics.

- It should expose a cleaner API than raw tree navigation.
- It may be schema-aware.
- Validation and business rules live here.
- It does not own serialization fidelity.

Example style:

```python
@dataclass
class Book:
    book_id: str
    title: str
    authors: list[str]

    def read(self): ...
    def get_page_numbers(self): ...
```

## Boundary between domain and document

Keep this open during the prototype. We should reason about update mechanics before settling on one method.

Current working rule:

- Parse XML into the ordered document model.
- Project selected data into domain objects.
- Perform business edits through the domain layer.
- Apply those edits back onto the document model explicitly.
- Serialize from the document model.

What is not decided yet:

- Whether updates should use a generic patch API.
- Whether domain objects should hold references back to document nodes.
- Whether synchronization should be pull-based, push-based, or command-based.

The prototype should help answer this rather than assume the final mechanism too early.

### Recommended prototype approach

Use explicit apply-back methods over small generic document mutation helpers.

Recommended shape:

- `read_book(element) -> Book`
- `apply_book(book, element, ordering_rules) -> None`

Supporting generic helpers:

- `set_or_insert_attr(...)`
- `find_child(...)`
- `insert_child_schema_ordered(...)`
- `replace_text_content(...)`

Why this is a good prototype default:

- keeps the domain layer clean
- keeps XML fidelity decisions explicit
- avoids coupling domain objects directly to XML node lifetimes
- avoids committing too early to a full patch or command system

Avoid in the first prototype:

- domain objects with hidden live XML node references
- diff-based reconciliation between regenerated XML and original XML
- rebuilding whole subtrees when a targeted in-place update is enough

## Mutation guidelines

To keep output deterministic:

- Modify nodes in place where possible.
- Avoid rebuilding larger subtrees unless necessary.
- Insert new attributes and elements with position awareness.
- Preserve existing order for existing content.
- Use schema-aware ordering when inserting new content.

Examples:

- Insert attribute after a known attribute.
- Replace a child at a specific index.
- Insert a new element at the schema-preferred location.

## Schema-aware insertion

This is in scope for the prototype.

Rule:

- Existing attributes and elements keep their original order.
- New attributes and elements should be inserted using schema-preferred ordering rules.

This should improve generated output without sacrificing round-trip stability for existing content.

## Suggested test criteria

Start with a small prototype test set that proves the boundaries.

### 1. Round-trip order preservation

Given XML with multiple sibling elements and multiple attributes:

- parse -> serialize preserves sibling order
- parse -> serialize preserves attribute order

### 2. Namespace handling

Given XML with prefixed namespaces:

- namespace URIs remain correct after serialization
- original prefixes must be preserved if untouched, best effort otherwise

### 3. Formatting normalization is acceptable

Given input with irregular indentation:

- serialization may normalize whitespace and indentation
- output may be pretty-printed and differ in whitespace
- semantic structure and ordering remain intact

### 4. Schema-aware insertion

Given a document missing an optional attribute or child:

- inserting new content places it in schema-preferred order
- existing neighboring content does not get reordered

### 5. Comments and processing instructions

If supported by the prototype backend:

- comments survive parse -> serialize
- processing instructions survive parse -> serialize

### 6. Domain edit application

Given a projected domain object edit:

- the intended change is applied back to the document model
- unrelated sibling order, attribute order, and namespace bindings remain stable
