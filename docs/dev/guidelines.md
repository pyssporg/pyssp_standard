# Guidelines

## Core Principles

- **One source of truth:** Prefer one clear source over multiple partially overlapping descriptions.
- **Simple over flexible:** Prefer simple solutions over flexible-but-complicated ones.
- **Single responsibility:** Keep each module, class, and document focused on one concern.
- **Early separation:** Separate concerns early so complexity does not accumulate in one place.
- **Structure sparingly:** Add structure only when it clearly reduces confusion or duplication.
- **Pure call chains:** Avoid internal monkeypatches or shims.

See also:
- **Architecture separation-of-concerns rules:** `product-breakdown/02-architecture/layer-rules.md`
- **Design constraints:** `product-breakdown/00-intent/constraints.md` (Separation of Concerns table)

## Documentation Guidelines

- Keep documents short and purpose-specific.
- Avoid repeating the same decision in multiple places; prefer references and links.
- Let each document answer one main question.
- Summarize decisions clearly before adding detail.
- Use examples to explain structure, not to replace the core recommendation.
- Remove outdated alternatives and stale notes once a direction is chosen.

## Review Heuristics

When adding new code or docs, check:

- Is this introducing a second source of truth?
- Is this repeating logic or explanation that already exists elsewhere?
- Does this file, class, or document have a single clear purpose?
- Can this be made smaller or more direct without losing clarity?
- Is the boundary between responsibilities still obvious?