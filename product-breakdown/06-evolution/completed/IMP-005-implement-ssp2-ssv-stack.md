# IMP-005: Implement SSP2 SSV Stack

**Status:** candidate  
**Priority:** medium  
**Layer:** Version-Specific (SSP2)

## Problem

`standard/ssp2/` contains empty `codec/`, `model/`, and `validation/`
directories. However, `version_routing.py` already registers
`StandardVersion("SSP", "SSV", "2.0")`, meaning the routing layer expects
SSP2 SSV support to exist.

## Proposed Solution

1. Analyze the SSP2 SSV schema in `schema/SSP2/` to determine differences
   from SSP1 SSV.
2. Implement SSP2 SSV:
   - Dataclass model(s) in `standard/ssp2/model/`
   - ElementTree codec in `standard/ssp2/codec/`
   - XSD/semantic validator in `standard/ssp2/validation/`
3. Add SSP2 SSV facade or extend existing `SSV` class to support version
   selection.
4. Write codec round-trip tests and facade tests in `pytest/ssp2/`.

## Verification

- SSP2 SSV XML can be parsed into SSP2 domain models and serialized back.
- Round-trip preserves semantic content (not necessarily exact XML formatting).
- Existing SSP1 SSV tests continue to pass unchanged.