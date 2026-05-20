# IMP-010: Fill FMI3 Skeleton codec/model/validation

**Status:** candidate  
**Priority:** low  
**Layer:** Version-Specific (FMI3)

## Problem

`standard/fmi3/` contains skeleton directories (`codec/`, `model/`,
`validation/`) but they are empty aside from `__init__.py`. No FMI3
model description parsing/serialization exists.

## Proposed Solution

1. Analyze the FMI3 schema in `schema/FMI3/` and compare with the
   existing FMI2 implementation.
2. Implement FMI3 support:
   - Dataclass models in `standard/fmi3/model/`
   - ElementTree codec in `standard/fmi3/codec/`
   - Validator in `standard/fmi3/validation/`
3. Extend or create an `Fmi3ModelDescription` facade.
4. Write codec round-trip and facade tests.

## Verification

- FMI3 XML can be parsed into FMI3 domain models and serialized back.
- Round-trip preserves semantic content.
- Existing FMI2 tests continue to pass unchanged.