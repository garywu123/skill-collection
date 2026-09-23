# Python Code-Style Decisions

Read this reference only when Python is a confirmed language for the project.

## Evidence

- project metadata in `pyproject.toml`, `setup.cfg`, and `setup.py`;
- requirements files and locks such as `uv.lock`, `poetry.lock`, `Pipfile`, and
  `Pipfile.lock`;
- Ruff configuration in `pyproject.toml`, `ruff.toml`, or `.ruff.toml`;
- Black configuration, when present;
- type-checking policy in `mypy.ini`, project configuration,
  `pyrightconfig.json`, and repository-scoped Pylance settings;
- pytest configuration, `tox.ini`, `noxfile.py`, and unittest evidence;
- CI, tasks, and scripts that establish commands;
- `src` and `tests` layout and plugin declarations;
- the declared minimum Python version and every supported runtime.

All of these are read-only. Never create or modify Python configuration,
environments, interpreter selections, lock files, dependencies, or tool
settings. When cross-language file hygiene is material, consult the
[EditorConfig baseline](editorconfig-baseline.md) without repeating it here.

## Precedence And Compatibility

Prefer explicit user direction, then an approved project document, then current
configuration, then a consistent repository pattern the user confirms. Honor the
declared minimum Python version and every supported runtime. A locally selected
or newly installed interpreter is execution evidence, not permission to raise
the supported version.

## Environment And Dependencies

Detect and preserve the existing workflow: virtual environment location; uv,
Poetry, pip, Pipenv, or another tool; lock strategy; and the exact install,
sync, run, and check commands. Never switch package managers, change the lock
strategy, or add a dependency. List only commands verified by CI, tasks,
scripts, configuration, or an observed successful run.

## Enforced By Tooling

| Concern | Authoritative surface |
|---|---|
| Formatting, linting, and import order | Configured Ruff, Black, or import tool |
| Type checking | mypy, Pyright, or repository-scoped Pylance configuration |
| Tests | The configured pytest or unittest workflow |
| Commands | CI, tasks, scripts, and project configuration |

Preserve each tool's current ownership: do not pair Ruff formatting with Black
unless the repository intentionally uses both, and keep an existing split where
Ruff owns linting or imports while another tool owns formatting.

## Rules To Decide And Write

Tooling does not enforce these. Settle each one with the user and write it into
the Python section, or omit it deliberately:

- type hints required on public boundaries, and what counts as a boundary;
- explicit `None`, empty, and missing-value behavior;
- exception contracts versus typed or structured result contracts;
- context managers and resource ownership;
- async and cancellation behavior where relevant;
- dataclass, `TypedDict`, and model conventions, including mutability;
- import and architectural layer boundaries, including forbidden imports;
- docstring format and which APIs require one;
- security, secrets, privacy, and data-handling constraints.

A consistently observed source pattern is a proposal to confirm, not policy.

## Tests

Detect the framework, plugins, file and test naming, fixtures, parametrization,
markers, and integration-test boundaries before writing a test rule. Write the
detected profile as binding; never invent a framework, plugin, marker, fixture
pattern, or command.

## Placement

| Finding | Destination |
|---|---|
| Formatting, linting, import, typing, or test enforcement | Tooling table route; configuration stays read-only |
| A decided semantic, structural, or documentation rule | The Python section of `docs/code-style.md` |
| A rule that applies to every language | The cross-language sections of `docs/code-style.md` |
| Unknown or conflicting evidence | Ask, or omit and report |
