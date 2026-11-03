"""Checkpoint sessions, per-role rotation, segment review, and automatic adjudication."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_cli import Harness, decision, finding, produce, review
from crossagent import config as cfg
from crossagent.errors import UsageError

SEGMENTED = dict(segment_review=True, max_reviews=6, max_segment_reviews=2, final_review_reserve=2,
                 checkpoint_session="resume")


def checkpoint(summary="S1 accepted: focused checks passed; next S2.", write=None,
               outcomes=("S1 parser accepts valid input",), remaining=("S2 persistence",)):
    step = produce(status="checkpoint", write=write)
    step["output"].update(summary=summary, segment_outcomes=list(outcomes), remaining_work=list(remaining))
    return step


def repaired(*outcomes, write=None):
    return produce(outcomes=outcomes, status="segment-repaired", write=write)


def delivery(h, *extra):
    return h.run("start", "--stage", "feature-delivery", "--artifact", "docs/plan.md", "--first", "produce",
                 "--request", "Deliver the plan.", "--producer", "fake:test-model:high",
                 "--reviewer", "fake:test-model:high", *extra)["run_id"]


class CheckpointSessionTests(unittest.TestCase):
    def test_resume_keeps_the_producer_session_and_fresh_replaces_it(self):
        for mode, resumed in (("resume", True), ("fresh", False)):
            with self.subTest(mode=mode):
                h = Harness(self, {"producer": [checkpoint(outcomes=(), remaining=()), produce()],
                                   "reviewer": [review()]}, checkpoint_session=mode)
                run_id = h.start("produce")["run_id"]
                event = h.next(run_id)
                self.assertIn("same session" if resumed else "new session", event["message"])
                h.next(run_id)
                first = h.state(run_id)["workers"]["producer"]["sessions"][0]
                self.assertEqual(h.calls("producer")[1]["session_id"], first if resumed else None)
                self.assertIn("Latest execution checkpoint", h.calls("producer")[1]["prompt"])

    def test_rotation_thresholds_apply_per_role(self):
        h = Harness(self, {"producer": [produce(context_tokens=500), produce(outcomes=[("R1-001", "fixed")])],
                           "reviewer": [{**review(findings=[finding()]), "context_tokens": 500},
                                        review(earlier=[("R1-001", "resolved")])]},
                    rotate_at_tokens={"producer": 100, "reviewer": 1000})
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        h.next(run_id)
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        self.assertIsNone(h.calls("producer")[1]["session_id"], "Producer exceeded its 100-token threshold")
        self.assertIsNotNone(h.calls("reviewer")[1]["session_id"], "Reviewer stayed under its 1000-token threshold")


class SegmentReviewTests(unittest.TestCase):
    def test_clean_segments_advance_the_base_and_final_review_reads_the_whole_run(self):
        h = Harness(self, {"producer": [checkpoint(write={"src/one.txt": "segment one"}),
                                        checkpoint(summary="S2 accepted; next S3.", write={"src/two.txt": "segment two"},
                                                   outcomes=("S2 persists records",), remaining=("S3 report",)),
                                        produce(write={"src/three.txt": "segment three"})],
                           "reviewer": [review(), review(), review()]}, **SEGMENTED)
        run_id = delivery(h)
        self.assertEqual(h.next(run_id)["phase"], "segment-review")
        passed = h.next(run_id)
        self.assertEqual(passed["phase"], "produce")
        state = h.state(run_id)
        self.assertEqual(state["trees"]["segment_base"], state["segments"][0]["tree"])
        self.assertIsNone(state["trees"]["last_review"], "segment reviews never move the final review base")
        self.assertEqual(h.next(run_id)["phase"], "segment-review")
        h.next(run_id)
        self.assertEqual(h.next(run_id)["phase"], "review")
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        first, second, final = (call["prompt"] for call in h.calls("reviewer"))
        self.assertIn("S1 parser accepts valid input", first)
        self.assertIn("Do not report unfinished later work", first)
        self.assertIn("segment two", second)
        self.assertNotIn("segment one", second, "the second segment diffs from the accepted first segment")
        for text in ("segment one", "segment two", "segment three", "Changes since the run baseline"):
            self.assertIn(text, final)
        self.assertNotIn("This is a segment review", final)
        sessions = {call["session_id"] for call in h.calls("producer")[1:]} | {
            call["session_id"] for call in h.calls("reviewer")[1:]}
        self.assertNotIn(None, sessions, "both roles resume one session across the run")
        self.assertEqual(h.state(run_id)["reviews_done"], 3)

    def test_segment_findings_repair_then_rereview_and_final_demotion_resets(self):
        h = Harness(self, {"producer": [checkpoint(write={"src/one.txt": "draft"}),
                                        repaired(("R1-001", "fixed"), write={"src/one.txt": "fixed"}),
                                        produce(), produce(outcomes=[("R3-001", "fixed")])],
                           "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")]),
                                        review(findings=[finding("Final gap.")]),
                                        review(earlier=[("R3-001", "resolved")])]}, **SEGMENTED)
        run_id = delivery(h)
        h.next(run_id)
        pending = h.next(run_id)
        self.assertEqual(pending["phase"], "awaiting-decision")
        self.assertEqual(pending["pending_findings"][0]["scope"], "segment-1")
        self.assertEqual(h.decide(run_id, decision("R1-001", "accepted"))["phase"], "segment-repair")
        self.assertEqual(h.next(run_id)["phase"], "segment-review")
        repair_prompt = h.calls("producer")[1]["prompt"]
        self.assertIn("segment-repaired", repair_prompt)
        self.assertIn("R1-001", repair_prompt)
        self.assertEqual(h.state(run_id)["checks"], [], "repairs run no whole-stage delivery checks")
        self.assertEqual(h.next(run_id)["phase"], "produce")
        self.assertIn("not the first review of this segment", h.calls("reviewer")[1]["prompt"])
        self.assertIn("fixed", h.calls("reviewer")[1]["prompt"])
        h.next(run_id)
        final = h.next(run_id)
        self.assertEqual([item["id"] for item in final["pending_findings"]], ["R3-001"],
                         "the final review is its own first attempt, so a major finding is not demoted")
        self.assertNotIn("This is not the first review", h.calls("reviewer")[2]["prompt"])
        h.decide(run_id, decision("R3-001", "accepted"))
        h.next(run_id)
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")

    def test_segment_cap_escalates_and_orch_acceptance_buys_exactly_one_more_round(self):
        h = Harness(self, {"producer": [checkpoint(), repaired(("R1-001", "fixed")), repaired(("R1-001", "fixed"))],
                           "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "open")])]},
                    **{**SEGMENTED, "max_segment_reviews": 1, "max_reviews": 5}, adjudication="auto")
        run_id = delivery(h)
        h.next(run_id)
        capped = h.next(run_id)
        self.assertEqual(capped["phase"], "awaiting-decision")
        self.assertEqual(capped["pending_findings"][0]["escalation"], "segment-review-cap")
        self.assertIn("segment review cap is reached", capped["decision_rules"])
        self.assertEqual(h.decide(run_id, decision("R1-001", "accepted"))["phase"], "segment-repair")
        self.assertEqual(h.next(run_id)["phase"], "segment-review")
        again = h.next(run_id)
        self.assertEqual(again["phase"], "awaiting-decision", "findings still open after the extra round escalate again")
        self.assertEqual(h.state(run_id)["segment"]["extra_reviews"], 1)
        self.assertEqual(len(h.calls("producer")), 2)

    def test_cap_acceptance_cannot_spend_the_final_review_reserve_without_the_user(self):
        h = Harness(self, {"producer": [checkpoint(), repaired(("R1-001", "fixed"))],
                           "reviewer": [review(findings=[finding()])]},
                    **{**SEGMENTED, "max_segment_reviews": 1, "max_reviews": 3})
        run_id = delivery(h)
        h.next(run_id)
        h.next(run_id)
        refused = h.decide(run_id, decision("R1-001", "accepted"), expect=2)
        self.assertIn("final-review reserve", refused["error"])
        self.assertEqual(h.state(run_id)["phase"], "awaiting-decision")
        path = h.dir / "decisions.json"
        accepted = h.run("decide", "--run", run_id, "--input", str(path), "--max-reviews", "4")
        self.assertEqual(accepted["phase"], "segment-repair")
        self.assertEqual(h.state(run_id)["settings"]["max_reviews"], 4)

    def test_reserve_waiver_is_an_explicit_decide_flag(self):
        h = Harness(self, {"producer": [checkpoint()], "reviewer": [review(findings=[finding()])]},
                    **{**SEGMENTED, "max_segment_reviews": 1, "max_reviews": 3})
        run_id = delivery(h)
        h.next(run_id)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"), expect=2)
        path = h.dir / "decisions.json"
        self.assertEqual(h.run("decide", "--run", run_id, "--input", str(path), "--waive-reserve")["phase"],
                         "segment-repair")
        self.assertTrue(h.state(run_id)["reserve_waived"])

    def test_segment_review_is_skipped_when_it_would_use_the_final_reserve(self):
        h = Harness(self, {"producer": [checkpoint(), checkpoint(summary="S2 done; next S3."), produce()],
                           "reviewer": [review(), review()]},
                    **{**SEGMENTED, "max_segment_reviews": 1, "max_reviews": 3})
        run_id = delivery(h)
        h.next(run_id)
        h.next(run_id)
        skipped = h.next(run_id)
        self.assertEqual(skipped["phase"], "produce")
        self.assertIn("segment review skipped", skipped["message"])
        self.assertEqual(skipped["segment_review_skipped"]["segment"], 2)
        self.assertEqual(h.next(run_id)["phase"], "review")
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        self.assertEqual(h.state(run_id)["reviews_done"], 2)

    def test_segment_lists_are_required_exactly_for_reviewed_checkpoints(self):
        bad_done = produce()
        bad_done["output"]["remaining_work"] = ["More work."]
        for step in (checkpoint(outcomes=(), remaining=()), checkpoint(remaining=()), bad_done):
            with self.subTest(step=step["output"]["status"]):
                h = Harness(self, {"producer": [step]}, **SEGMENTED)
                event = h.next(delivery(h))
                self.assertEqual(event["phase"], "failed")
                self.assertIn("segment lists", event["error"]["message"])
        h = Harness(self, {"producer": [checkpoint()]}, **SEGMENTED)
        self.assertIn("segment lists", h.next(h.start("produce")["run_id"])["error"]["message"],
                      "general checkpoints keep the legacy rule")

    def test_segment_repaired_status_is_valid_only_for_a_repair(self):
        h = Harness(self, {"producer": [repaired()]}, **SEGMENTED)
        event = h.next(delivery(h))
        self.assertIn("segment-repaired answers exactly a segment repair", event["error"]["message"])

    def test_recovery_and_answers_return_to_the_segment_phase(self):
        h = Harness(self, {"producer": [checkpoint(), {"fail": "model unavailable"},
                                        produce(status="needs-user-decision", questions=["Which format?"]),
                                        repaired(("R1-001", "fixed"))],
                           "reviewer": [review(findings=[finding()]), {"fail": "model unavailable"},
                                        review(earlier=[("R1-001", "resolved")])]}, **SEGMENTED)
        run_id = delivery(h)
        h.next(run_id)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        self.assertEqual(h.next(run_id)["phase"], "failed")
        self.assertEqual(h.run("retry-producer", "--run", run_id)["phase"], "segment-repair")
        self.assertEqual(h.next(run_id)["phase"], "awaiting-answer")
        self.assertEqual(h.run("answer", "--run", run_id, "--text", "Use JSON.")["phase"], "segment-repair")
        self.assertEqual(h.next(run_id)["phase"], "segment-review")
        self.assertEqual(h.next(run_id)["phase"], "failed")
        self.assertEqual(h.run("retry-review", "--run", run_id)["phase"], "segment-review")
        self.assertEqual(h.next(run_id)["phase"], "produce")


class AutoAdjudicationTests(unittest.TestCase):
    def test_rules_escalate_before_demotion_and_pause_the_whole_round(self):
        findings = [finding("Changes the public API.", needs_user_decision=True, evidence=[]),
                    finding("Missing outcome."),
                    finding("Wording nit.", severity="minor"),
                    finding("Unsupported claim.", evidence=[])]
        h = Harness(self, {"producer": [produce(), produce(outcomes=[("R1-002", "not-fixed")])],
                           "reviewer": [review(findings=findings), review(earlier=[("R1-002", "open")])]})
        run_id = h.start("produce", "--adjudication", "auto")["run_id"]
        self.assertEqual(h.state(run_id)["adjudication_source"], "start")
        h.next(run_id)
        paused = h.next(run_id)
        self.assertEqual(paused["phase"], "awaiting-decision")
        self.assertEqual([item["id"] for item in paused["pending_findings"]], ["R1-001"])
        self.assertEqual(paused["pending_findings"][0]["escalation"], "needs-user-decision")
        self.assertIn("Demoted, no evidence: Unsupported claim.", paused["notes"])
        self.assertEqual(len(h.calls("producer")), 1, "no partial execution while a finding is escalated")
        by_id = {item["id"]: item for item in h.run("status", "--run", run_id)["adjudications"]}
        self.assertEqual((by_id["R1-002"]["by"], by_id["R1-002"]["rule"], by_id["R1-002"]["disposition"]),
                         ("auto", "blocker-or-major", "accepted"))
        self.assertEqual((by_id["R1-003"]["rule"], by_id["R1-003"]["disposition"]), ("minor", "note-only"))
        self.assertEqual(h.state(run_id)["findings"][2]["priority"], "low")
        self.assertIsNone(by_id["R1-001"]["by"])
        h.decide(run_id, decision("R1-001", "rejected", "Out of scope.", "none"))
        self.assertEqual(h.state(run_id)["findings"][0]["history"][-1]["by"], "orch")
        h.next(run_id)
        reopened = h.next(run_id)
        self.assertEqual(reopened["phase"], "awaiting-decision")
        self.assertEqual(reopened["pending_findings"][0]["escalation"], "not-fixed-still-open")
        h.decide(run_id, decision("R1-002", "needs-user-decision", "User owns this trade-off.", "high"))
        self.assertEqual(h.state(run_id)["final_status"], "independently-passed")
        closed = h.run("close", "--run", run_id)
        backlog = (h.repo / "docs" / "review-backlog.md").read_text(encoding="utf-8")
        self.assertIn("[auto:minor] Minor finding kept as a note", backlog)
        self.assertIn("User owns this trade-off.", backlog)
        self.assertEqual(closed["report"]["findings_by_disposition"]["note-only"], 1)

    def test_clean_auto_rounds_continue_without_orch(self):
        h = Harness(self, {"producer": [produce(), produce(outcomes=[("R1-001", "fixed")]), produce()],
                           "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "open")]),
                                        review(earlier=[("R1-001", "resolved")])]},
                    adjudication="auto", max_reviews=3)
        run_id = h.start("produce")["run_id"]
        self.assertEqual(h.state(run_id)["adjudication_source"], "config")
        h.next(run_id)
        self.assertEqual(h.next(run_id)["phase"], "produce", "a major finding is accepted automatically")
        h.next(run_id)
        self.assertEqual(h.next(run_id)["phase"], "produce", "a fixed finding kept open is accepted again")
        self.assertEqual(h.state(run_id)["findings"][0]["history"][-1]["rule"], "still-open")
        h.next(run_id)
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")

    def test_orch_mode_keeps_needs_user_decision_findings_as_ordinary_pending(self):
        h = Harness(self, {"producer": [produce()],
                           "reviewer": [review(findings=[finding(needs_user_decision=True, evidence=[]), finding()])]})
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        event = h.next(run_id)
        self.assertEqual([item["id"] for item in event["pending_findings"]], ["R1-001"], "orch mode still demotes")
        self.assertNotIn("escalation", event["pending_findings"][0])


class CompatibilityTests(unittest.TestCase):
    def test_legacy_saved_state_runs_with_original_behavior(self):
        h = Harness(self, {"producer": [checkpoint(outcomes=(), remaining=()), produce(),
                                        produce(outcomes=[("R1-001", "fixed")])],
                           "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")])]},
                    **SEGMENTED, adjudication="auto")
        run_id = h.start("produce")["run_id"]
        path = h.repo / ".cross-agent" / "runs" / run_id / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["settings"] = {key: state["settings"][key] for key in cfg.REQUIRED_SETTINGS}
        state["settings"]["rotate_at_tokens"] = 350000
        for key in ("segment", "segments", "segment_skips", "segment_reviews_done", "adjudication_source"):
            del state[key]
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assertIn("new session", h.next(run_id)["message"])
        h.next(run_id)
        pending = h.next(run_id)
        self.assertEqual(pending["phase"], "awaiting-decision", "legacy runs keep Orch adjudication")
        self.assertEqual(pending["settings"]["adjudication"], "orch")
        self.assertEqual(h.calls("producer")[1]["session_id"], None)
        h.decide(run_id, decision("R1-001", "accepted"))
        h.next(run_id)
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")

    def test_legacy_config_reports_legacy_settings(self):
        h = Harness(self, {})
        settings = h.run("status")["settings"]
        self.assertEqual({key: settings[key] for key in cfg.LEGACY_SETTINGS}, cfg.LEGACY_SETTINGS)

    def test_rotation_table_round_trips_through_the_renderer(self):
        config = cfg._parse_config(Path(cfg.__file__).resolve().parents[2].joinpath(
            "assets", "config.example.toml").read_text(encoding="utf-8"), Path("template.toml"))
        self.assertEqual(config["rotate_at_tokens"], {"producer": 250000, "reviewer": 400000})
        rendered = cfg._render_config(config)
        self.assertIn("rotate_at_tokens = { producer = 250000, reviewer = 400000 }", rendered)
        again = cfg._parse_config(rendered, Path("rendered.toml"))
        self.assertEqual({key: again[key] for key in cfg.RUN_SETTINGS}, {key: config[key] for key in cfg.RUN_SETTINGS})

    def test_invalid_new_settings_are_rejected(self):
        h = Harness(self, {})
        base = h.config.read_text(encoding="utf-8")
        cases = {
            "rotate_at_tokens = { producer = 1 }": "rotate_at_tokens",
            'checkpoint_session = "sometimes"': "checkpoint_session",
            'adjudication = "producer"': "adjudication",
            "segment_review = true\nmax_segment_reviews = 3\nfinal_review_reserve = 2": "max_reviews >=",
            "segment_review = true": "requires max_segment_reviews",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                text = "\n".join(item for item in base.split("\n")
                                 if not (line.startswith("rotate") and item.startswith("rotate_at_tokens")))
                h.config.write_text(line + "\n" + text, encoding="utf-8")
                self.assertIn(message, h.run("status", expect=2)["error"])
        with self.assertRaises(UsageError):
            cfg._check({**cfg._parse_config(base, Path("c.toml")), "final_review_reserve": 0}, Path("c.toml"))


if __name__ == "__main__":
    unittest.main()
