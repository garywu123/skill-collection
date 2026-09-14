# Python Code-Style Decisions

## Trigger And Evidence

Read this reference only when repository evidence includes Python. Inspect only
the relevant surfaces:

- project metadata in `pyproject.toml`, `setup.cfg`, and `setup.py`;
- requirements files and locks such as `uv.lock`, `poetry.lock`, `Pipfile`, and
  `Pipfile.lock`;
- Ruff configuration in `pyproject.toml`, `ruff.toml`, or `.ruff.toml`;
- Black configuration, when present;
- type-checking policy in `mypy.ini`, applicable project configuration,
  `pyrightconfig.json`, and repository-scoped Pylance settings;
- pytest configuration, `tox.ini`, `noxfile.py`, and unittest evidence;
- CI, tasks, and scripts that establish commands;
- `src` and `tests` layout, test files, and plugin declarations;
- selected interpreter and version evidence, including repository runtime files.

These surfaces are read-only evidence. When cross-language formatting or file
hygiene is material, also consult the
[EditorConfig comparison baseline](editorconfig-baseline.md) without repeating
its content here.

## Precedence And Compatibility

Prefer explicit user direction, approved project documents, current
configuration, and consistent repository evidence, in that order. Honor the
minimum Python version and every supported runtime declared by the repository.
A selected or newly installed local interpreter is execution evidence, not
permission to raise the supported version. Report conflicts or omit unknown
rules instead of inferring policy from the latest local interpreter.

## Environment And Dependencies

Detect the existing environment and dependency workflow from repository
evidence: virtual environment location, uv, Poetry, pip, Pipenv, or another
tool; lock strategy; and exact install, sync, run, and check commands. Preserve
that workflow. Never switch package managers, change the lock strategy, or add
dependencies automatically. List only commands verified by CI, tasks, scripts,
configuration, or an observed successful run.

## Mechanical Enforcement

| Concern | Authoritative surface | Audit action |
|---|---|---|
| Formatting, linting, and import order | Configured Ruff, Black, or import tool | Preserve each tool's current ownership |
| Type checking | mypy, Pyright, or repository-scoped Pylance configuration | Record only configured scope and strictness |
| Tests | Configured pytest or unittest workflow | Preserve the detected framework and plugins |
| Commands | CI, tasks, scripts, and project configuration | Keep exact verified commands and arguments |

Do not recommend Ruff formatting and Black together unless repository evidence
shows that both are intentionally used. Preserve existing boundaries when Ruff
owns linting or imports while another tool owns formatting. Treat every command
as a candidate until its executable, working directory, arguments, and relevant
environment are verified.

## Semantic Candidates

Put a short semantic rule in `AGENTS.md` only when explicit user direction, a
governing document, or configuration approves it across the applicable project
surface. A consistently observed source pattern is evidence to report, not
authority to establish policy. Candidates include:

- type hints on public boundaries;
- explicit `None`, empty, and missing-value behavior;
- exception contracts versus typed or structured result contracts;
- context managers and resource ownership;
- async and cancellation behavior where relevant;
- dataclass and model conventions;
- import and architectural layer boundaries;
- docstrings for public APIs when required;
- security, secrets, privacy, and data-handling constraints.

Do not turn this list into project policy without evidence.

## Test Profile

Detect the framework, plugins, file and test naming, fixtures, parametrization,
markers, and integration-test boundaries before writing test guidance. Preserve
the repository's pytest or unittest conventions; never invent a framework,
plugin, marker, fixture pattern, or command.

## Output Placement

| Finding | Destination |
|---|---|
| Mechanical formatting, linting, import, typing, or test enforcement | Existing configuration; read-only for this Skill |
| Short universal semantic rule | `AGENTS.md` |
| Detailed examples or specialized workflow | Existing project docs or scoped instructions |
| Unknown, absent, or conflicting evidence | Omit or report |

## Read-Only Boundary

Agent Instructions never creates or updates Python configuration, environments,
interpreter selections, lock files, dependencies, or tool settings. It reads
those surfaces only to route verified project rules and commands.
