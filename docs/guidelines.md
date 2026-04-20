# Guidelines

These guidelines are meant to keep both code and documentation simple, readable, and maintainable.

## Core Principles
- Prefer one clear source of truth over multiple partially overlapping descriptions.
- Prefer simple solutions over flexible-but-complicated ones.
- Keep each module, class, and document focused on one responsibility.
- Separate concerns early so complexity does not accumulate in one place.
- Add structure only when it clearly reduces confusion or duplication.
- Avoid internal monkeypatches or shims, keep the call chain as pure as possible

## Code Guidelines
- Avoid duplication of logic, schema knowledge, and workflow rules.
- Keep parsing, mapping, validation, archive handling, and public API behavior in separate layers.
- Prefer small, composable classes and functions over large multi-purpose ones.
- Keep generated code, domain models, orchestration, and compatibility behavior clearly separated.
- Do not let file I/O, XML handling, and business rules collapse into the same class.
- Prefer simple data flow that is easy to trace and test.
- Optimize for maintainability first, then for cleverness or abstraction.
- Add abstractions only when they remove real repetition or clarify ownership.

## Documentation Guidelines
- Keep documents short and purpose-specific.
- Avoid repeating the same architectural decision in multiple places.
- Let each document answer one main question.
- Prefer references and links over restating the same content.
- Summarize decisions clearly before adding detail.
- Use examples to explain structure, not to replace the core recommendation.
- Remove outdated alternatives and stale notes once a direction is chosen.

## Separation of Concerns
- Archive/session code should manage files and persistence only.
- Generated bindings should represent schema-shaped XML only.
- Codecs should orchestrate parse/serialize only.
- Mappers should convert between generated bindings and compact domain models.
- Domain models should stay independent of XML libraries and generated types.
- Validation should remain separate from parsing and persistence.
- Public APIs should focus on user workflows, not internal schema details.

## Review Heuristics
When adding new code or docs, check:
- Is this introducing a second source of truth?
- Is this repeating logic or explanation that already exists elsewhere?
- Does this file/class/document have a single clear purpose?
- Can this be made smaller or more direct without losing clarity?
- Is the boundary between responsibilities still obvious?
