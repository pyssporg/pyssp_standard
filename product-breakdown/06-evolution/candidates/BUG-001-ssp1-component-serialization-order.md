# BUG-001: SSP1 Component Serialization Order Breaks Flattened SSD Validation

## Status

Open

## Problem

`Ssp1SsdCodec._serialize_component()` emits `<ParameterBindings>` before
`<Connectors>`.

That ordering is rejected by the SSP1 XSD when a component carries its own
parameter bindings, which happens after flattening hierarchical SSDs.

## Evidence

- Flattening `dcmotor` promoted nested components that still carried bindings.
- The generated SSD failed validation with:
  - `Element '{...}Connectors': This element is not expected.`

## Impact

- Flattened SSDs cannot be serialized through the normal SSD facade.
- `dcmotor` fails during build unless component children are written in schema
  order.

## Local Fix

Write `<Connectors>` before `<ParameterBindings>` in component serialization.

## Follow-Up

- Keep this ordering covered by a regression test that flattens a nested SSD
  and round-trips it through the codec.
