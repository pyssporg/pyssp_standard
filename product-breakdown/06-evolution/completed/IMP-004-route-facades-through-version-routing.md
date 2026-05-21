# IMP-004: Route Facades Through version_routing

**Status:** candidate  
**Priority:** high  
**Layer:** Public API / Versioning

## Problem

Public facades (`ssd.py`, `ssv.py`, `ssm.py`, `srmd.py`, `ssb.py`, `md.py`,
`ls_ref.py`) import and instantiate specific codec/validator classes directly
(e.g., `from standard.ssp1.codec import ...`). The `version_routing.py`
module exists to centralize this dispatch but is not used as the universal
entry path.

Adding a new document version currently requires:
1. Building a new codec/model/validation stack
2. Modifying the facade to import and instantiate the new classes

## Proposed Solution

1. Extend `version_routing.py` (or create a lookup registry) so that a facade
   can query: "give me the codec and validator for document type X, version Y."
2. Update each facade to call the version router instead of importing specific
   codec/validator classes directly.
3. Ensure backward compatibility: existing default-version behavior is preserved.

## Verification

- All existing codec, facade, and orchestration tests pass.
- Version routing can dispatch to SSP1 codecs (current behavior unchanged).
- Adding a theoretical SSP2 codec registration exercises the routing path
  without requiring full SSP2 implementation.
- No hardcoded `from standard.ssp1.codec import ...` remains in facade files.