# AGENTS

## AI Context Guidelines

Keep repository context narrow. Do not scan the whole repo by default.

Read in this order:
- `AGENTS.md`
- `docs/dev/repo_map.md`
- `pyssp_standard/__init__.py`
- the specific module under `pyssp_standard/` that matches the task
- the smallest relevant test under `pytest/`
- `README.md` only for package positioning, not for implementation details

Use `docs/dev/repo_map.md` for first-pass orientation. Do not open `pyssp_standard/__README__.md` unless the task needs architectural background beyond the repo map.

Default working set:
- `pyssp_standard/`
- `pytest/`
- `docs/` only when the task is documentation-related

Avoid reading these paths unless the task explicitly requires them:
- `venv/`
- `.git/`
- `.pytest_cache/`
- `__pycache__/`
- `3rdParty/`
- `pytest/legacy_unsupported/`
- large binary or archive fixtures such as `*.fmu`, `*.ssp`, `*.zip`

For tests, do not scan all fixtures up front. Open only the fixture files referenced by the test you are editing.

Search strategy:
- Prefer targeted `rg` queries scoped to `pyssp_standard/` or a specific `pytest/` file
- Prefer opening one file at a time over reading complete directories
- Do not read vendored standards or generated/cache content for general feature work

## Guidelines

try to generate code by the common code guidelines
 - Keep it simple
 - Minimize duplication
 - Keep files small and focused
 - Any unit or function should try and contain a common level of abstraction  

This is an experimental software, this means:
- Interfaces do not need to be stable, prioritize code clarity and ease of use
- Avoid creating thin shims or wrappers, change the references directly  


## Environment Guidelines

- Use the repo-local `venv` for Python commands, test runs, and workflow scripts when it exists.
- Prefer `. venv/bin/activate && <command>` over the system Python for `pytest`, `python -m ...`, and related tooling.


## Documentation Guidelines

- Keep docs short, focused, and single-purpose.
- Prefer adding a new focused page over growing a mixed-purpose page.
- Treat `README.md` as a landing page, not a full manual.
- Keep the main onboarding flow in `docs/getting_started.md`.
- Keep reference material in `docs/command_reference.md`, not in onboarding pages.
- Organize docs by audience:
  `docs/user/` for user workflows,
  `docs/dev/` for maintainer and implementation notes,
  `docs/integrations/` for external system integrations.
- Strongly prefer canonical pages over compatibility stubs or redirect files.
- When moving docs, update links to the new destination and remove obsolete references.
- Optimize for the easiest first success:
  show the lowest-friction path before the full rebuild path.
- Scope prerequisites to the workflow that actually needs them.
- Avoid duplication across pages.
- If two pages repeat the same explanation, keep it in one page and link to it.
- Start pages with what the reader can do there and who the page is for.
- Keep filenames stable and descriptive.
- Use `docs/index.md` as the main documentation router.
