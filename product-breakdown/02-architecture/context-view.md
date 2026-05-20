# Context View

> **Layer:** 02-architecture
> **Artifact type:** context-view.md

## System Context

```text
┌────────────────────────────────────────────────────────────────┐
│                        pyssp_standard                           │
│  Python library for inspecting and editing SSP/FMI artifacts    │
└────────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                   │
        ▼                  ▼                   ▼
   ┌──────────┐     ┌───────────┐      ┌──────────────┐
   │  .ssp    │     │  .fmu     │      │ Standalone   │
   │ Archives │     │ Archives  │      │ .ssd/.ssv/   │
   │ & Dirs   │     │ & Dirs    │      │ .ssm/.ssb/   │
   └──────────┘     └───────────┘      │ .srmd/.xml   │
                                        └──────────────┘
```

## External Actors

| Actor | Description | Interaction |
|-------|-------------|-------------|
| **SSP/FMI File System** | Source and destination for all artifact I/O | Read/write XML files, zip archives, directories |
| **Python Caller** | CI scripts, higher-level tools, or interactive use | Imports `pyssp_standard`, uses context-managed facades |
| **XSD Schema Files** | Vendored schema definitions for validation | Located at `pyssp_standard/schema/` |
| **Standard Documents** | SSP1, FMI2, LS-REF specification documents | Reference only; not loaded at runtime |

## Boundaries

- `pyssp_standard` is a **library**, not a service. It has no network interface,
  no server process, and no persistent state beyond the files it reads/writes.
- All I/O is local filesystem. No HTTP, database, or message queue.
- External schema files are vendored in-tree (`pyssp_standard/schema/`).
- The library does not invoke FMU simulation or co-simulation.

## Evidence

- `README.md`: package positioning
- All facade modules: none use network or external service
- `pyssp_standard/schema/`: vendored XSD files
- `docs/dev/architecture.md`: purpose section