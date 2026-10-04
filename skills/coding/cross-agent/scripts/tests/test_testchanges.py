"""B1 test-change summary (R01-R03) and its configuration/saved-run compatibility."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_cli import Harness, configuration_text, decision, finding, produce, review
from crossagent import config, testchanges
from crossagent.errors import UsageError

CALC_TEST = """import unittest
from calc import add


class AddTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
"""
WEAK_TEST = """import unittest
from calc import add


class AddTests(unittest.TestCase):
    @unittest.skip("flaky")
    def test_add(self):
        self.assertTrue(add(2, 3))
"""


def summary_of(prompt: str) -> str:
    start = prompt.index("CLI test-change summary")
    return prompt[start:prompt.index("\nReport only findings", start)]


def junit(*cases: str, root="testsuites") -> str:
    body = "".join(cases)
    totals = " ".join(f'{name}="{body.count(tag)}"' for name, tag in
                      (("tests", "<testcase"), ("failures", "<failure"), ("errors", "<error"), ("skipped", "<skipped")))
    suite = f'<testsuite name="s" {totals}>{body}</testsuite>'
    return suite if root == "testsuite" else f"<testsuites>{suite}</testsuites>"


def case(name: str, inner: str = "") -> str:
    return f'<testcase classname="t" name="{name}">{inner}</testcase>'


def seeded(test, script, **config) -> Harness:
    h = Harness(test, script, **config)
    files = {"calc.py": "def add(a, b):\n    return a + b\n", "tests/test_calc.py": CALC_TEST,
             "tests/test_old.py": "def test_old():\n    assert True\n", "tests/fixtures/data.json": '{"n": 1}\n',
             "pytest.ini": "[pytest]\n"}
    for path, text in files.items():
        (h.repo / path).parent.mkdir(parents=True, exist_ok=True)
        (h.repo / path).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "seed"]):
        subprocess.run(["git", *args], cwd=h.repo, check=True, capture_output=True)
    return h


def configure(h: Harness, checks: list[str], reports: dict) -> None:
    text = configuration_text(projects={".": dict(allowed_commands=[], delivery_checks=checks, extra_dirs=[])})
    text += "test_reports = { " + ", ".join(f"{json.dumps(k)} = {json.dumps(v)}" for k, v in reports.items()) + " }\n"
    h.config.write_text(text, encoding="utf-8")


class SummaryTests(unittest.TestCase):
    def test_r01_skip_delete_fixture_and_filter_reach_each_revision(self):
        weakened = produce(write={"tests/test_calc.py": WEAK_TEST, "tests/fixtures/data.json": '{"n": 2}\n',
                                  "pytest.ini": '[pytest]\naddopts = -k "not slow"\n', "calc.py": "def add(a, b):\n    return a + b + 0\n"},
                           delete=["tests/test_old.py"])
        later = produce(outcomes=[("R1-001", "fixed")],
                        write={"tests/test_more.py": "import pytest\n\n@pytest.mark.xfail\ndef test_more():\n    assert 1\n"})
        h = seeded(self, {"producer": [weakened, later],
                          "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")])]})
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        event = h.next(run_id)
        first = summary_of(h.calls("reviewer")[0]["prompt"])
        self.assertIn("Test-change summary for review 1", first)
        for expected in ("deleted: tests/test_old.py [test]", "modified: tests/test_calc.py [test]",
                         "modified: tests/fixtures/data.json [test, fixture/mock]", "modified: pytest.ini [runner/config]",
                         "tests/test_calc.py:6 (new side) added unittest skip/expected failure: @unittest.skip(\"flaky\")",
                         "pytest.ini:2 (new side) added runner filter/discovery", "tests/test_calc.py: -1 +1",
                         "Other changed files not classified as test-relevant: 1.", "-    assert True",
                         "proves neither unchanged tests nor adequate coverage"):
            self.assertIn(expected, first)
        self.assertNotIn("calc.py b/calc.py", first, "production hunks stay in the review diff only")
        self.assertEqual(event["test_changes"]["review"], 1)
        self.assertEqual(len(event["test_changes"]["sha256"]), 64)
        h.decide(run_id, decision("R1-001", "accepted"))
        h.next(run_id)
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        second = summary_of(h.calls("reviewer")[1]["prompt"])
        self.assertIn("Test-change summary for review 2", second)
        self.assertIn("added: tests/test_more.py [test]", second)
        self.assertIn("tests/test_more.py:3 (new side) added pytest skip/xfail", second)
        self.assertNotIn("test_old.py", second, "each review summarizes only its own revision")
        self.assertEqual([item["review"] for item in h.state(run_id)["test_changes"]], [1, 2])

    def test_user_diff_noprefix_keeps_exact_paths_and_hunks(self):
        h = seeded(self, {"producer": [produce(write={"tests/test_calc.py": WEAK_TEST,
                                                     "tests/helpers.py": "def helper():\n    return 1\n"})],
                          "reviewer": [review()]})
        subprocess.run(["git", "config", "diff.noprefix", "true"], cwd=h.repo, check=True, capture_output=True)
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        h.next(run_id)
        text = summary_of(h.calls("reviewer")[0]["prompt"])
        for expected in ("added: tests/helpers.py [test]", "modified: tests/test_calc.py [test]",
                         "tests/test_calc.py:6 (new side) added unittest skip", "diff --git a/tests/helpers.py b/tests/helpers.py",
                         "+    @unittest.skip(\"flaky\")"):
            self.assertIn(expected, text)
        self.assertNotRegex(text, r"(^|[\s:])sts/")

    def test_r01_unreadable_report_encoding_is_recorded_and_review_continues(self):
        writer = "import sys; open(sys.argv[1], 'w').write(sys.argv[2])"
        content = "<?xml version='1.0' encoding='unknown-test-encoding'?><testsuite tests='0'/>"
        check = f'"{sys.executable}" -c "{writer}" reports/bad.xml "{content}"'
        h = seeded(self, {"producer": [produce(write={"tests/test_calc.py": WEAK_TEST})], "reviewer": [review()]})
        (h.repo / ".git/info/exclude").write_text("reports/\n", encoding="utf-8")
        (h.repo / "reports").mkdir()
        configure(h, [check], {check: "reports/bad.xml"})
        run_id = h.start("produce")["run_id"]
        event = h.next(run_id)
        self.assertEqual((event["phase"], event["checks"][0]["exit_code"]), ("review", 0), event)
        self.assertEqual(event["checks"][0]["report"]["status"], "unreadable")
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        self.assertIn("counts unknown: report reports/bad.xml is unreadable", summary_of(h.calls("reviewer")[0]["prompt"]))

    def test_reviewer_retry_receives_the_identical_summary(self):
        h = seeded(self, {"producer": [produce(write={"tests/test_calc.py": WEAK_TEST})],
                          "reviewer": [{"fail": "model unavailable"}, review()]})
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        self.assertEqual(h.next(run_id)["phase"], "failed")
        h.run("retry-review", "--run", run_id)
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        prompts = [summary_of(call["prompt"]) for call in h.calls("reviewer")]
        self.assertEqual(prompts[0], prompts[1])
        self.assertEqual(len(h.state(run_id)["test_changes"]), 1)

    def test_r03_no_detected_change_is_not_adequacy_and_console_counts_stay_unknown(self):
        h = seeded(self, {"producer": [produce(write={"calc.py": "def add(a, b):\n    return 5\n"})],
                          "reviewer": [review()]})
        check = f'"{sys.executable}" -c "print(\'Ran 12 tests\')"'
        h.config.write_text(configuration_text(projects={".": dict(allowed_commands=[], delivery_checks=[check],
                                                                    extra_dirs=[])}), encoding="utf-8")
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        h.next(run_id)
        text = summary_of(h.calls("reviewer")[0]["prompt"])
        self.assertIn("Test-relevant paths (0):\n- none detected", text)
        self.assertIn("judge requirements, discovery and assertion strength yourself", text)
        evidence = next(line for line in text.splitlines() if line.startswith("- after P0"))
        self.assertIn("exit 0; counts unknown: no structured report configured", evidence)
        self.assertNotIn("12", evidence.replace(check, ""))

    def test_r02_r03_fresh_stale_and_zero_case_reports_through_checks(self):
        writer = "import sys; open(sys.argv[1], 'w').write(sys.argv[2])"
        zero = junit(root="testsuite").replace('"', "'")
        fresh = f'"{sys.executable}" -c "{writer}" reports/unit.xml "{junit(case("a"), case("b", "<skipped/>")).replace(chr(34), chr(39))}"'
        empty = f'"{sys.executable}" -c "{writer}" reports/none.xml "{zero}"'
        stale = f'"{sys.executable}" -c "print(1)"'
        metadata = "<testsuite tests='1'><properties><testcase name='metadata'/></properties></testsuite>"
        misplaced = f'"{sys.executable}" -c "{writer}" reports/misplaced.xml "{metadata}"'
        h = seeded(self, {"producer": [produce(write={"tests/test_calc.py": WEAK_TEST})], "reviewer": [review()]})
        (h.repo / "reports").mkdir()
        (h.repo / "reports/old.xml").write_text(junit(case("a")), encoding="utf-8")
        (h.repo / ".git/info/exclude").write_text("reports/\n", encoding="utf-8")
        configure(h, [fresh, empty, stale, misplaced], {fresh: "reports/unit.xml", empty: "reports/none.xml",
                                                        stale: "reports/old.xml", misplaced: "reports/misplaced.xml"})
        run_id = h.start("produce")["run_id"]
        checks = h.next(run_id)["checks"]
        self.assertEqual([c["exit_code"] for c in checks], [0, 0, 0, 0], checks)
        self.assertEqual([c["report"]["status"] for c in checks], ["fresh", "fresh", "stale", "unsupported"])
        self.assertEqual(checks[0]["report"]["counts"], {"tests": 2, "executed": 1, "failed": 0, "skipped": 1})
        h.next(run_id)
        text = summary_of(h.calls("reviewer")[0]["prompt"])
        self.assertIn("report reports/unit.xml (JUnit XML, fresh): 2 test cases, 1 executed, 0 failed or errored, "
                      "1 skipped. Scope: this command's report only, not a repository total.", text)
        self.assertIn("reports/none.xml (JUnit XML, fresh): 0 test cases, 0 executed", text)
        self.assertIn("Warning: no test case executed.", text)
        self.assertIn("counts unknown: report reports/old.xml is stale", text)
        self.assertIn("counts unknown: report reports/misplaced.xml is unsupported", text)
        self.assertNotIn("reports/misplaced.xml (JUnit XML, fresh)", text)


class ReportTests(unittest.TestCase):
    def test_r02_only_fresh_unambiguous_junit_yields_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            def read(content, before=None, exit_code=1):
                path = Path(directory) / "r.xml"
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_text(content, encoding="utf-8")
                return testchanges.read_report(directory, "r.xml", before, exit_code)

            fresh = read(junit(case("a"), case("b", "<failure/>"), case("c", "<error/>"), case("d", "<skipped/>")))
            self.assertEqual((fresh["status"], fresh["counts"]),
                             ("fresh", {"tests": 4, "executed": 3, "failed": 2, "skipped": 1}))
            self.assertEqual(fresh["scope"], "this command's report only")
            mtime = testchanges.report_mtime(directory, "r.xml")
            unknown = [testchanges.read_report(directory, "r.xml", mtime, 0), read(None),
                       read(junit(case("a")), exit_code=None), read(junit(case("a"), case("a"))),
                       read(junit(case("a", "<flakyFailure/>"))), read("<TestRun/>"), read("Ran 3 tests\nOK")]
            self.assertEqual([item["status"] for item in unknown],
                             ["stale", "absent", "unknown", "ambiguous", "ambiguous", "unsupported", "unreadable"])
            self.assertTrue(all(item["counts"] is None and item["reason"] for item in unknown))
            contradictory = {
                "totals without cases": '<testsuite tests="10" failures="2" skipped="1"/>',
                "omitted cases": f'<testsuite tests="10">{case("a")}</testsuite>',
                "missing suite total": f'<testsuites><testsuite name="s">{case("a")}</testsuite></testsuites>',
                "wrong failures": f'<testsuite tests="1" failures="1">{case("a")}</testsuite>',
                "wrong root total": f'<testsuites tests="3">{junit(case("a"), root="testsuite")}</testsuites>',
                "nonnumeric total": f'<testsuite tests="one">{case("a")}</testsuite>',
                "disabled tests": f'<testsuite tests="1" disabled="2">{case("a")}</testsuite>',
                "several outcomes": junit(case("a", "<failure/><skipped/>")),
                "unsupported outcome": junit(case("a", "<rerun/>")),
                "notrun status": junit('<testcase classname="t" name="a" status="notrun"/>'),
                "suppressed result": junit('<testcase classname="t" name="a" status="run" result="suppressed"/>'),
                "completed but skipped": junit('<testcase classname="t" name="a" result="completed"><skipped/></testcase>'),
                "unsupported child report": '<testsuites tests="0"><TestRun/></testsuites>',
                "unsupported suite child": '<testsuite tests="0"><TestRun/></testsuite>',
                "unknown encoding": "<?xml version='1.0' encoding='unknown-test-encoding'?><testsuite tests='0'/>",
                "case in suite properties": f'<testsuite tests="1"><properties>{case("a")}</properties></testsuite>',
                "case in root properties": f'<testsuites tests="1"><properties>{case("a")}</properties>'
                                           f'{junit(root="testsuite")}</testsuites>',
                "case in failure": f'<testsuite tests="2" failures="1">{case("a", "<failure>" + case("b") + "</failure>")}'
                                   '</testsuite>',
                "case in case properties": junit(case("a", f'<properties>{case("b")}</properties>')),
                "case in system-out": f'<testsuite tests="1"><system-out>{case("a")}</system-out></testsuite>',
                "suite in properties": f'<testsuite tests="0"><properties>{junit(root="testsuite")}</properties></testsuite>',
            }
            for name, content in contradictory.items():
                with self.subTest(name=name):
                    result = read(content)
                    self.assertNotEqual(result["status"], "fresh", result)
                    self.assertIsNone(result["counts"])
            nested = read(f'<testsuites tests="2"><testsuite tests="2"><testsuite tests="1">{case("a")}</testsuite>'
                          f'{case("b", "<skipped/>")}</testsuite></testsuites>')
            self.assertEqual(nested["counts"], {"tests": 2, "executed": 1, "failed": 0, "skipped": 1})
            properties = '<properties><property name="k" value="v"/></properties>'
            meta = properties + "<system-out>log</system-out>"
            described = read(f'<testsuites tests="2">{properties}<testsuite tests="2" failures="1">{meta}<testsuite tests="1">'
                             f'{case("a", meta + "<failure>boom</failure>")}</testsuite>{case("b")}</testsuite></testsuites>')
            self.assertEqual((described["status"], described["counts"]),
                             ("fresh", {"tests": 2, "executed": 2, "failed": 1, "skipped": 0}))
            gtest = read(junit('<testcase classname="t" name="a" status="run" result="completed"/>',
                               '<testcase classname="t" name="b" status="run" result="skipped"><skipped/></testcase>'))
            self.assertEqual(gtest["counts"], {"tests": 2, "executed": 1, "failed": 0, "skipped": 1})

    def test_path_classification(self):
        cases = {"src/Calc.Tests/CalcTests.cs": ["test"], "web/src/qty.test.js": ["test"],
                 "tests/__mocks__/api.js": ["test", "fixture/mock"], "conftest.py": ["fixture/mock", "runner/config"],
                 "src/app/main.py": [], "jest.config.ts": ["runner/config"], "src/App/App.csproj": [],
                 "src/App.Tests/App.Tests.csproj": ["test", "runner/config"], ".github/workflows/ci.yml": ["runner/config"],
                 "pkg/calc_test.go": ["test"], "docs/testing.md": []}
        for path, kinds in cases.items():
            with self.subTest(path=path):
                self.assertEqual(testchanges.classify(path), kinds)


class CompatibilityTests(unittest.TestCase):
    def test_report_config_is_optional_and_explicit(self):
        def parse(project):
            return config._parse_config(configuration_text(projects={".": project}), Path("config.toml"))
        base = dict(allowed_commands=[], delivery_checks=["pytest --junitxml=r.xml"], extra_dirs=[])
        self.assertNotIn("test_reports", config.project_settings(parse(base), Path(".")))
        text = configuration_text(projects={".": base}) + 'test_reports = { "pytest --junitxml=r.xml" = "r.xml" }\n'
        parsed = config._parse_config(text, Path("config.toml"))
        self.assertEqual(config.project_settings(parsed, Path("."))["test_reports"], {"pytest --junitxml=r.xml": "r.xml"})
        for bad in ('{ "other command" = "r.xml" }', '{ "pytest --junitxml=r.xml" = "r.trx" }', '["r.xml"]'):
            with self.subTest(bad=bad), self.assertRaises(UsageError):
                config._parse_config(configuration_text(projects={".": base}) + f"test_reports = {bad}\n", Path("c.toml"))

    def test_saved_run_without_b1_fields_still_reviews(self):
        h = seeded(self, {"producer": [produce(write={"tests/test_calc.py": WEAK_TEST})], "reviewer": [review()]})
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        state = h.state(run_id)
        state["project"].pop("test_reports", None)
        for check in state["checks"]:
            check.pop("report", None)
        state.pop("test_changes", None)
        (h.repo / ".cross-agent/runs" / run_id / "state.json").write_text(json.dumps(state), encoding="utf-8")
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        self.assertIn("Test-change summary for review 1", h.calls("reviewer")[0]["prompt"])


if __name__ == "__main__":
    unittest.main()
