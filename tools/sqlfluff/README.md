# SQLFluff Personal Layout

Reusable SQL Server 2022 T-SQL formatting, based on SQLFluff 4.4.0. Install the tool into a project's Python environment; do not copy an existing virtual environment or its executable.

Start with [user instructions](USER-INSTRUCTIONS.md). The VS Code extension invokes the installed SQLFluff executable. This package adds SQLFluff rules; it is not a VS Code extension or a replacement SQL parser.

## Files to maintain

| File | Responsibility |
|---|---|
| [`.sqlfluff`](.sqlfluff) | Shared 100-character profile, alias alignment and enabled rules |
| [`case_layout.py`](src/sqlfluff_personal_layout/rules/case_layout.py) | CASE length decisions, placement and whitespace-only edits |
| [`indentation.py`](src/sqlfluff_personal_layout/rules/indentation.py) | Native LT02 outside lines managed by CASE layout |
| [`operators.py`](src/sqlfluff_personal_layout/rules/operators.py) | Native LT03 outside assignments managed by CASE layout |
| [`__init__.py`](src/sqlfluff_personal_layout/__init__.py) | SQLFluff plugin registration |
| [`pyproject.toml`](pyproject.toml) | Package version, entry point and SQLFluff version |
| [`settings.json`](examples/settings.json) | VS Code example for a project-root `.venv` |
| [`test_case_layout.py`](tests/test_case_layout.py) | Layout expectations, token preservation and idempotence |
| [`check_reports.py`](tests/check_reports.py) | Check actual report files in memory, without changing SQL or accessing a database |

## Behavior and limits

Short CASE expressions may remain inline when the complete line fits 100 characters. Existing multiline outer CASE expressions stay multiline. Long direct assignments put CASE below the equals sign, with CASE/END aligned and WHEN/ELSE indented one additional level. Short nested CASE expressions may remain inline; longer nested CASE expressions expand. Existing AS aliases remain AS aliases.

The implementation edits parsed whitespace only; it does not rewrite conditions, flatten nesting, rename identifiers or edit literal/comment contents. CASE expressions containing comments or SELECT subqueries are left to native rules. The compatibility indentation rule delegates LT02 except on complete physical lines occupied by supported CASE expressions, where CASE layout owns its boundaries. It does not validate every indentation choice inside an unusually long branch. Other native layout rules remain enabled.

The profile replaces LT02 and LT03 with compatibility rules; do not also enable the original LT02/LT03. SQLFluff internals are version-sensitive, so SQLFluff is pinned to 4.4.0. Upgrade only after running the tests and report checks. Some long lines remain LT05 warnings, including unsplittable SQL and comments. Formatting is not proof of query correctness or performance.

## Validation

Thirteen tests cover short CASE with/without ELSE, the 100/101-character boundary, UPDATE and SELECT assignments, AS aliases, nested CASE, IR-style aggregates/functions, comments/literals, subqueries, native indentation/operator behavior and VS Code-style stdin formatting with a successful exit code. Each in-process formatting test checks unchanged non-whitespace tokens and a stable second formatting pass.

The SGVM Order and Inventory Request report copies were also checked in memory: unchanged non-whitespace tokens (including comments), no parse errors, stable repeated formatting, and no custom-rule violations. Native LT05 warnings remain. No database was accessed and the original report files were not formatted in place.
