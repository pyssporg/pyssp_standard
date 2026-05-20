# IMP-008: Remove Empty layer_example Directory

**Status:** candidate  
**Priority:** low  
**Layer:** Documentation

## Problem

`docs/dev/improvements/layer_example/` exists but contains only a
`__pycache__/` directory — no useful content. This is a stale artifact.

## Proposed Solution

1. Remove `docs/dev/improvements/layer_example/` (and its parent
   `docs/dev/improvements/` if it also becomes empty).
2. If the `docs/dev/improvements/` directory had a purpose, keep the
   parent but remove only the empty `layer_example/` subdirectory.

## Verification

- `docs/dev/improvements/layer_example/` no longer exists.
- No broken links in documentation (check for references to this path).