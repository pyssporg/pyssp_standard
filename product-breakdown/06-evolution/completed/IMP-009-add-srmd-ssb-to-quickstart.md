# IMP-009: Add SRMD and SSB to Quick-Start Documentation

**Status:** candidate  
**Priority:** low  
**Layer:** Documentation

## Problem

SRMD (SimulationResourceMetaData) and SSB (SignalDictionary) are fully
implemented public facades but are not mentioned in `README.md` or
`docs/getting_started.md`. Users may not know these capabilities exist.

## Proposed Solution

1. In `docs/getting_started.md`, add brief usage examples for SRMD and SSB
   after the existing SSP/SSD/SSV examples.
2. In `README.md`, update the feature list to mention SSB and SRMD.
3. Ensure links to the Python API docs (`docs/user/python_api.md`) cover
   SRMD and SSB.

## Verification

- `README.md` lists SRMD and SSB in its feature section.
- `docs/getting_started.md` includes SRMD and SSB examples.
- All doc links resolve correctly.