Legacy tests quarantined here target APIs or modules that no longer exist in the
current layered architecture, for example `ssb`, `srmd`, `unit`, and older
utility wrappers.

They are excluded from default collection through the repo root `conftest.py`
so the active suite stays focused on the maintained layers:
- codec
- validation
- public facade
- archive orchestration

If those APIs are reintroduced, move the relevant tests back into the active
layered tree and update them to the current public surface.
