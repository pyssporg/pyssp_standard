# Read The Docs Build

This page is for maintainers who need to understand how documentation is built and published.

## Source Layout

The canonical documentation lives under `docs/`.

Key pages:
- `docs/index.md`
- `docs/getting_started.md`
- `docs/command_reference.md`
- `docs/user/`
- `docs/dev/`
- `docs/integrations/`

## Build Entry Point

The Sphinx configuration lives at `docs/conf.py`.

Local build:

```bash
sphinx-build docs _build
```

## CI And Publishing

- GitHub Actions builds the docs from `docs/`
- `readthedocs.yml` points to `docs/conf.py`
- Markdown pages are parsed through `myst_parser`
