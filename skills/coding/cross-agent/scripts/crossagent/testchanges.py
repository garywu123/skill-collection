"""Deterministic test-change summary given to each Reviewer, and JUnit XML counts.

The summary reads the same snapshot range as the review diff. It classifies
paths by naming conventions, finds supported skip/disable/filter markers in
added or removed lines, and quotes raw hunks. It never judges coverage.
"""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

from . import gitops

HUNK_LIMIT = 32 * 1024  # Raw hunks repeat the review diff; the full diff stays above them.

TEST_DIRS = {"test", "tests", "__tests__", "spec", "specs", "testing", "e2e", "unittests", "integrationtests"}
TEST_DIR_SUFFIXES = (".test", ".tests", ".specs", ".unittests", ".integrationtests")
FIXTURE_DIRS = {"fixture", "fixtures", "testdata", "test-data", "test_data", "__mocks__", "mock", "mocks",
                "fakes", "stubs", "__snapshots__", "snapshots"}
TEST_FILE = re.compile(r"(^test_.+\.py|.+_test\.(py|go)|.+\.(test|spec)\.[cm]?[jt]sx?|.+Tests?\.(cs|fs|vb|java|kt)"
                       r"|.+_spec\.rb|.+Test\.php)$")
MOCK_NAME = re.compile(r"mock|fake|stub|fixture", re.IGNORECASE)
RUNNER_FILE = re.compile(
    r"^(pytest\.ini|tox\.ini|setup\.cfg|pyproject\.toml|noxfile\.py|conftest\.py|package\.json|Makefile"
    r"|(jest|vitest|playwright|cypress|mocha|ava|karma)\.(config|conf)\.[cm]?[jt]s(on)?|\.mocharc\..+"
    r"|.+\.runsettings|Directory\.Build\.(props|targets)|phpunit\.xml(\.dist)?|\.gitlab-ci\.yml"
    r"|azure-pipelines\.ya?ml|Jenkinsfile)$")
PROJECT_FILE = re.compile(r".+\.(cs|fs|vb)proj$|^(pom\.xml|build\.gradle(\.kts)?)$")

MARKERS = (
    ("unittest skip/expected failure",
     re.compile(r"@(unittest\.)?(skip(If|Unless)?|expectedFailure)\b|\.skipTest\(|\bSkipTest\b")),
    ("pytest skip/xfail", re.compile(r"\bpytest\.(mark\.(skip|skipif|xfail)\b|skip\(|xfail\(|importorskip\()")),
    ("JS skip/todo/only",
     re.compile(r"\b(it|test|describe|suite|context)\.(skip|todo|only|fixme)\b|\b[xf](it|describe|test)\s*\("
                r"|\bt\.(skip|todo)\s*\(|[{,]\s*(skip|todo|only)\s*:")),
    (".NET skip/ignore", re.compile(r"\bSkip\s*=|\[\s*(Ignore|Explicit)\b")),
    ("JUnit disable/assumption", re.compile(r"@(Disabled\w*|Ignore)\b|\bassume(True|False|That)\s*\(")),
    ("Go skip", re.compile(r"\bt\.Skip(f|Now)?\s*\(|\btesting\.Short\(\)")),
    ("runner filter/discovery",
     re.compile(r"(^|\s)(-k|-run|--deselect|--ignore(-glob)?|--grep|--filter|--testNamePattern|--testPathPattern"
                r"|--testPathIgnorePatterns|--exclude)(\s|=|$)|\b(testPathIgnorePatterns|testMatch|testRegex"
                r"|collect_ignore(_glob)?|norecursedirs|python_files|python_classes|python_functions|testpaths"
                r"|addopts)\b")),
)
ASSERTION = re.compile(r"\bassert\w*|\bAssert\.|\bexpect\s*\(")
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
RERUN_TAGS = {"rerunFailure", "rerunError", "flakyFailure", "flakyError"}
OUTCOMES = ("failure", "error", "skipped")
CASE_CHILDREN = {*OUTCOMES, "system-out", "system-err", "properties"}
SUITE_CHILDREN = {"testsuites": {"testsuite", "properties"},
                  "testsuite": {"testsuite", "testcase", "properties", "system-out", "system-err"}}

LIMITS = (
    "Detection is limited to path naming conventions and the marker patterns named below "
    "(unittest, pytest, Jest/Vitest/Mocha/node:test, xUnit/NUnit/MSTest, JUnit, Go, common runner filter "
    "options and keys). Dynamic or conditional skips, environment-driven filters, custom runners, generated "
    "tests, tests outside conventional paths and changed assertion intent are not detected. An empty section "
    "proves neither unchanged tests nor adequate coverage or assertions: judge requirements, discovery and "
    "assertion strength yourself from the diff, files and check evidence."
)


def classify(path: str) -> list[str]:
    parts = PurePosixPath(path).parts
    name, dirs = parts[-1], [part.lower() for part in parts[:-1]]
    kinds = []
    in_tests = any(part in TEST_DIRS or part.endswith(TEST_DIR_SUFFIXES) for part in dirs)
    if in_tests or TEST_FILE.match(name):
        kinds.append("test")
    if any(part in FIXTURE_DIRS for part in dirs) or name == "conftest.py" or (kinds and MOCK_NAME.search(name)):
        kinds.append("fixture/mock")
    if (RUNNER_FILE.match(name) or path.startswith(".github/workflows/")
            or (PROJECT_FILE.match(name) and "test" in path.lower())):
        kinds.append("runner/config")
    return kinds


def _sections(diff: str) -> list[dict]:
    """Split a --no-renames unified diff into one section per path."""
    sections = []
    for block in re.split(r"(?m)^(?=diff --git )", diff):
        if not block.startswith("diff --git "):
            continue
        lines = block.splitlines()
        rest = lines[0][len("diff --git "):]
        quoted = rest.startswith('"')
        # With renames off both sides are equal: "a/P b/P".
        path = rest[2:2 + (len(rest) - 5) // 2] if not quoted else rest.strip('"').split(' "b/')[-1]
        change = "modified"
        if any(line.startswith("new file mode") for line in lines[1:4]):
            change = "added"
        elif any(line.startswith("deleted file mode") for line in lines[1:4]):
            change = "deleted"
        sections.append({"path": path, "change": change, "quoted": quoted, "text": block,
                         "binary": any(line.startswith("Binary files ") for line in lines[1:6]), "lines": lines})
    return sections


def _scan(section: dict) -> tuple[list[dict], int, int]:
    markers, added, removed = [], 0, 0
    old = new = 0
    in_hunk = False
    for line in section["lines"]:
        header = HUNK.match(line)
        if header:
            old, new, in_hunk = int(header.group(1)), int(header.group(2)), True
            continue
        if not in_hunk or line.startswith("\\"):
            continue
        sign, text = line[:1], line[1:]
        if sign == " ":
            old, new = old + 1, new + 1
            continue
        if not sign or sign not in "+-":
            continue
        number = new if sign == "+" else old
        if sign == "+":
            new += 1
        else:
            old += 1
        for kind, pattern in MARKERS:
            if pattern.search(text):
                markers.append({"path": section["path"], "line": number, "side": "new" if sign == "+" else "old",
                                "change": "added" if sign == "+" else "removed", "kind": kind,
                                "text": text.strip()[:160]})
        if ASSERTION.search(text):
            added, removed = added + (sign == "+"), removed + (sign == "-")
    return markers, added, removed


def summarize(cwd: Path, base: str, tree: str, review: int, checks: list[dict]) -> dict:
    """Build the fixed Reviewer input for one reviewed revision."""
    # Explicit prefixes keep "a/P b/P" headers even when the user's Git sets diff.noprefix.
    diff = "" if base == tree else gitops.git(
        ["-c", "core.quotePath=false", "diff", "--no-color", "--no-ext-diff", "--no-renames",
         "--src-prefix=a/", "--dst-prefix=b/", base, tree], cwd).stdout
    paths, markers, assertions, unknowns, hunks = [], [], [], [], []
    other, hunk_bytes, omitted = 0, 0, []
    for section in _sections(diff):
        kinds = classify(section["path"])
        found, added, removed = _scan(section)
        if found and not kinds:
            kinds = ["marker only"]
        if not kinds:
            other += 1
            continue
        paths.append({"path": section["path"], "change": section["change"], "kinds": kinds})
        markers += found
        if "test" in kinds and (added or removed):
            assertions.append({"path": section["path"], "added": added, "removed": removed})
        if section["binary"]:
            unknowns.append(f"{section['path']}: binary change; hunks and markers unknown")
        if section["quoted"]:
            unknowns.append(f"{section['path']}: quoted Git path; classification may be incomplete")
        size = len(section["text"].encode("utf-8"))
        if hunk_bytes + size > HUNK_LIMIT:
            omitted.append(section["path"])
        else:
            hunk_bytes += size
            hunks.append(section["text"].rstrip("\n"))
    if omitted:
        unknowns.append(f"Raw hunks omitted over {HUNK_LIMIT // 1024} KB (still in the review diff): {', '.join(omitted)}")
    evidence = [_evidence(check) for check in checks]
    record = {"review": review, "base": base, "tree": tree, "paths": paths, "markers": markers,
              "assertion_lines": assertions, "other_changed_files": other, "unknowns": unknowns,
              "evidence": evidence}
    record["text"] = _render(record, hunks)
    return record


def _evidence(check: dict) -> dict:
    item = {"after": check.get("after"), "command": check["command"], "exit_code": check["exit_code"]}
    report = check.get("report")
    item["counts"] = report["counts"] if report and report.get("status") == "fresh" else None
    item["report"] = report
    return item


def _render(record: dict, hunks: list[str]) -> str:
    lines = [f"Test-change summary for review {record['review']} (deterministic; snapshot range "
             f"{record['base'][:12]}..{record['tree'][:12]}, the same range as the diff above).",
             "Limits: " + LIMITS, "", f"Test-relevant paths ({len(record['paths'])}):"]
    lines += [f"- {item['change']}: {item['path']} [{', '.join(item['kinds'])}]" for item in record["paths"]] or ["- none detected"]
    lines += [f"Other changed files not classified as test-relevant: {record['other_changed_files']}.", "",
              f"Skip/disable/filter markers in added or removed lines ({len(record['markers'])}):"]
    lines += [f"- {item['path']}:{item['line']} ({item['side']} side) {item['change']} {item['kind']}: {item['text']}"
              for item in record["markers"]] or ["- none detected"]
    lines += ["", "Assertion-like lines changed in test paths (a signal, not a strength measure):"]
    lines += [f"- {item['path']}: -{item['removed']} +{item['added']}" for item in record["assertion_lines"]] or ["- none detected"]
    lines += ["", "Verification evidence from the latest checks (counts only from a fresh configured JUnit XML "
              "report for that command; console output is never parsed):"]
    for item in record["evidence"]:
        report = item["report"]
        text = f"- after {item['after']}: `{item['command']}` exit {item['exit_code']}; "
        if not report:
            text += "counts unknown: no structured report configured for this command."
        elif item["counts"] is None:
            text += f"counts unknown: report {report['path']} is {report['status']} ({report['reason']})."
        else:
            counts = item["counts"]
            text += (f"report {report['path']} (JUnit XML, fresh): {counts['tests']} test cases, "
                     f"{counts['executed']} executed, {counts['failed']} failed or errored, {counts['skipped']} skipped. "
                     "Scope: this command's report only, not a repository total.")
            if counts["tests"] == 0 or counts["executed"] == 0:
                text += " Warning: no test case executed."
        lines.append(text)
    if not record["evidence"]:
        lines.append("- none: no delivery check result exists for this revision (none configured or none run yet); "
                     "test execution is unknown.")
    lines += ["", "Unknowns:"]
    lines += [f"- {item}" for item in record["unknowns"]] or ["- none beyond the limits above"]
    if hunks:
        lines += ["", "Raw hunks for test-relevant paths:", "```diff", *hunks, "```"]
    return "\n".join(lines)


def report_mtime(project_root: str, path: str) -> int | None:
    try:
        return os.stat(Path(project_root) / path).st_mtime_ns
    except OSError:
        return None


def read_report(project_root: str, path: str, before_mtime: int | None, exit_code: int | None) -> dict:
    """Return counts only from a fresh, unambiguous JUnit XML report written by this command."""
    report = {"path": path, "format": "junit-xml", "status": "unknown", "reason": "", "counts": None,
              "scope": "this command's report only"}
    after = report_mtime(project_root, path)
    if exit_code is None:
        return {**report, "reason": "the command did not finish"}
    if after is None:
        return {**report, "status": "absent", "reason": "no report after the command"}
    if before_mtime is not None and after == before_mtime:
        return {**report, "status": "stale", "reason": "the command did not rewrite the report"}
    try:
        root = ET.parse(Path(project_root) / path).getroot()
    except (OSError, ET.ParseError, LookupError, UnicodeError, ValueError) as exc:
        return {**report, "status": "unreadable", "reason": f"cannot parse JUnit XML: {exc}"}
    if root.tag not in ("testsuites", "testsuite"):
        return {**report, "status": "unsupported", "reason": f"root element {root.tag} is not JUnit XML"}
    problem = _inconsistency(root)
    if problem:
        return {**report, "status": problem[0], "reason": problem[1]}
    cases = _placed(root)[1]
    failed = sum(_outcome(case) in ("failure", "error") for case in cases)
    skipped = sum(_outcome(case) == "skipped" for case in cases)
    counts = {"tests": len(cases), "executed": len(cases) - skipped, "failed": failed, "skipped": skipped}
    return {**report, "status": "fresh", "reason": "rewritten by this command; declared totals match", "counts": counts}


def _outcome(case) -> str | None:
    return next((child.tag for child in case if child.tag in OUTCOMES), None)


def _placed(suite) -> tuple[list, list]:
    """Return the suites and test cases reached only through direct suite children, starting at this suite."""
    suites, cases, pending = [], [], [suite]
    while pending:
        suites.append(pending.pop())
        for child in suites[-1]:
            if child.tag == "testsuite":
                pending.append(child)
            elif child.tag == "testcase":
                cases.append(child)
    return suites, cases


def _inconsistency(root) -> tuple[str, str] | None:
    """Accept only one plain outcome per test case, unique IDs and suite totals matching the test cases."""
    for element in root.iter():
        allowed = SUITE_CHILDREN.get(element.tag)
        if allowed is not None and any(child.tag not in allowed for child in element):
            return "unsupported", f"unsupported element under {element.tag}"
    suites, cases = _placed(root)
    # A suite or case inside metadata or an outcome (properties, failure, ...) is not a standard placement.
    placed = len(suites) + len(cases)
    if placed != sum(element.tag in ("testsuites", "testsuite", "testcase") for element in root.iter()):
        return "unsupported", "a test suite or test case is nested outside a supported suite position"
    for case in cases:
        tags = [child.tag for child in case]
        status, result = case.get("status"), case.get("result")
        # Only the plain run/completed/skipped attribute form is understood; notrun, suppressed etc. stay unknown.
        if (status not in (None, "run") or result not in (None, "completed", "skipped")
                or (result is not None and (result == "skipped") != (_outcome(case) == "skipped"))):
            return "unsupported", f"unsupported test case status/result attributes in {case.get('name')}"
        if any(tag in RERUN_TAGS for tag in tags):
            return "ambiguous", "rerun/flaky entries"
        if any(tag not in CASE_CHILDREN for tag in tags):
            return "unsupported", f"unsupported test case element in {case.get('name')}"
        if sum(tag in OUTCOMES for tag in tags) > 1:
            return "ambiguous", f"several outcomes for {case.get('name')}"
    ids = [(case.get("classname", ""), case.get("name", "")) for case in cases]
    if len(ids) != len(set(ids)):
        return "ambiguous", "duplicate test case IDs"
    for suite in suites:
        if suite.tag == "testsuite" and suite.get("tests") is None:
            return "inconsistent", "a testsuite does not declare tests, so completeness cannot be checked"
        outcomes = [_outcome(case) for case in _placed(suite)[1]]
        actual = {"tests": len(outcomes), "failures": outcomes.count("failure"), "errors": outcomes.count("error"),
                  "skipped": outcomes.count("skipped"), "disabled": 0}
        for name, value in actual.items():
            declared = suite.get(name)
            if declared is None:
                continue
            try:
                matches = int(declared) == value
            except ValueError:
                matches = False
            if not matches:
                return "inconsistent", f"{suite.tag} declares {name}={declared} but has {value} matching test cases"
    return None
