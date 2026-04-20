# Why xsdata

`xsdata` should be the primary XML binding strategy for this rework.

## Why It Fits
- faster schema coverage for SSP2 and FMI2/FMI3
- less handwritten XML parsing and serialization code
- better alignment with XSD as the source of truth
- lower maintenance cost when standards evolve

## What xsdata Solves
- generated classes from XSD
- parser/serializer integration
- most schema-shaped XML boilerplate

## What xsdata Does Not Solve
- ergonomic authoring APIs
- backward-compatible public behavior by itself
- cross-file resolution
- semantic validation
- archive persistence rules

That work remains handwritten.

## Recommended Pattern
Use a layered `xsdata` hybrid:
- generated bindings for schema-shaped XML objects
- handwritten mapper layer for generated `<->` domain conversion
- handwritten codec layer for parse/serialize orchestration
- handwritten orchestration and validation above that

In short:
- `xsdata` owns XML shape
- mappers own model adaptation
- orchestration owns workflow behavior

## Main Tradeoff
The main downside is that generated classes are verbose and schema-shaped. That is acceptable as long as they stay internal and the rest of the codebase talks to compact domain models instead.

## Rules
- keep generated types internal
- regenerate from wrapper scripts, do not hand-edit
- keep public classes stable
- keep cross-file resolution outside codecs
- keep semantic validation outside generated bindings

## Demo References
Current demo examples:
- `demo/codec/ssv_hybrid_codec.py`
- `demo/generated/generate_ssv_bindings.py`
- `demo/codec/ssd_xsdata_codec.py`
- `demo/codec/ssd_mapper.py`
