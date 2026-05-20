# IMP-007: Add Explicit Test Coverage for DocumentRuntime Reference Discovery

**Status:** candidate  
**Priority:** medium  
**Layer:** Testing

## Problem

`common/document_runtime.py` contains reference discovery logic that has
no dedicated test coverage. Cross-document reference resolution is only
tested indirectly through SSP archive integration tests. The code itself
contains a TODO noting this gap.

## Proposed Solution

1. After implementing IMP-002 (extract reference discovery), write dedicated
   unit tests covering:
   - No references present
   - Single reference of each type (SSD components, SSV files, SSM files)
   - Multiple references of mixed types
   - Nested/recursive references
   - Malformed reference paths
   - Circular reference detection (if applicable)
2. If IMP-002 is deferred, write tests against the existing
   `DocumentRuntime` instance methods using mocked archive directories.

## Verification

- Test coverage for reference discovery functions is added.
- All tests pass.
- The TODO about testability in `document_runtime.py` can be removed once
  tests are in place.