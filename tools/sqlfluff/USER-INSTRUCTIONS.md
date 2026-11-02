# Use SQLFluff in Another Project

## Install

Use an existing project `.venv`, or create one from the project root:

```powershell
py -m venv .venv
```

Copy this entire tool folder wherever convenient. In the following commands, replace `C:\path\to\tools\sqlfluff` with its actual location. Run commands from the target project root. Install the built plugin; pip also installs its pinned SQLFluff dependency when needed:

```powershell
.\.venv\Scripts\python.exe -m pip install "C:\path\to\tools\sqlfluff\dist\sqlfluff_personal_layout-0.1.0-py3-none-any.whl"
```

The supplied `dist` directory also contains SQLFluff and dependency wheels for the machine on which they were downloaded. For an offline installation on a compatible Windows/Python environment:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --find-links "C:\path\to\tools\sqlfluff\dist" sqlfluff-personal-layout==0.1.0
```

Python 3.11 or newer is required. The custom plugin wheel is pure Python; dependency wheels may depend on Python version and platform. Use the online command on a different platform/Python version. `dist` and virtual environments are generated local artifacts and are excluded from Git.

Do not copy files directly into `.venv\Scripts` or `site-packages`. Pip installs the executable, dependencies and plugin-discovery metadata together.

## Configure the project and VS Code

Copy the supplied [`.sqlfluff`](.sqlfluff) into the target project root. If that project already has SQLFluff settings, compare and merge them instead of overwriting them. This profile assumes T-SQL and raw SQL, not a templated SQL project.

Install `sqlfluff.vscode-sqlfluff` in VS Code. Merge the keys in [`examples/settings.json`](examples/settings.json) into the target project's `.vscode/settings.json`. The example assumes `.venv` and `.sqlfluff` are directly below the opened project folder. Adjust both paths when using a nested project. An opened `.code-workspace` can override folder settings; check its SQLFluff paths too.

Use **Format Document**. Save-time formatting stays disabled. The equivalent command from the target project root is:

```powershell
.\.venv\Scripts\sqlfluff.exe fix --config .sqlfluff path\to\example.sql
```

First use a SQL copy and review the diff. Check that SQLFluff discovers `Case_C001`, `Case_L002` and `Case_L003`:

```powershell
.\.venv\Scripts\sqlfluff.exe --version
.\.venv\Scripts\sqlfluff.exe rules
```

Projects can install the same versioned wheel and copy the same profile. Profile copies do not automatically synchronize. To reproduce a project's setup, retain the chosen wheel or its source revision alongside that project's dependency-install instructions.

## Maintain and rebuild

Change CASE formatting in `src/sqlfluff_personal_layout/rules/case_layout.py`. Keep plugin registration and native-rule compatibility out of that module's formatting decisions. Add an example to the existing test file whenever behavior changes. Do not add unrelated formatting preferences without agreeing examples first.

Use a Python environment with this package installed. From this tool folder, install an editable development copy and run tests:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
python tests/check_reports.py C:\path\to\order_report.sql C:\path\to\inventory_request_report.sql
```

The report check accepts file paths and works entirely in memory. It asserts token preservation, successful parsing, idempotence and no remaining custom-rule violations; it reports native warnings separately.

After tests pass, increment the package version in `pyproject.toml` for a release, update the installation examples, and build a new wheel. Download dependencies for the target Python/platform when offline installation is needed:

```powershell
python -m pip wheel --no-deps --wheel-dir dist .
python -m pip download --only-binary=:all: --dest dist sqlfluff==4.4.0
```

Install the new wheel in each target environment and merge any profile changes. Never silently upgrade SQLFluff: its native rule APIs are part of this plugin's compatibility boundary.
