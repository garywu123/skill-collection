# Direct CLI Session Feasibility

**Status:** completed

**Conclusion:** supported for adapter resume and evidence handoff; native cross-agent session adoption is not supported by the current CLI.

**Current position:** Human and scripted cases, both Orch paths, permission probes, evidence preservation, and managed independent reviews are complete. Both fixture runs independently passed and closed. No implementation changes authorized; integration remains the user's next decision.

## Question

Can a Claude CLI discussion return to cross-agent production and independent
review with inspectable context, current permissions, and preserved discussion
evidence? Can Claude itself orchestrate the same bounded test, rather than
merely serving as a configured Producer?

## Inputs

- [Reviewed proposal](cross-agent-exploration.md).
- Current cross-agent CLI, provider adapters, and result schemas in
  `skills/coding/cross-agent/`; read-only experimental subjects.
- Scripted requirements/nonces and a real human discussion, inside isolated
  fixtures under `.cross-agent/evidence/direct-cli-20261016/`. The human chose
  to discuss actual storyboard preferences and explicitly provided no token.
- Installed Claude Opus 5.5/high and Codex Sol 6.1/high. Record actual models
  when exposed; configured effort is not observed effort.
- Official Claude CLI and permissions documentation, fetched 2026-10-16.

## Method

- **Oracle:** Exact fixture facts, transcript messages and filesystem hashes;
  actual CLI commands/events and cross-agent outcomes. A successful response
  alone does not prove context continuity or permission enforcement.
- **Procedure:** Step 10: inspect supported session/permission interfaces and
  prepare disposable repositories with no commits. Step 20: start read-only
  interactive discussion, supply facts, exit, then resume the same session via
  the existing provider adapter with a structured production response. Probe
  writes using harmless sentinel files. Step 30: test the existing managed
  production/review flow using explicit evidence handoff, without editing run
  state or claiming that a fresh session is the original interactive session.
  Step 40: let Claude act as Orch and dispatch the reciprocal fixture flow;
  verify commands and run artifacts independently. Step 50: record results here.
- **Human versus scripted input:** Scripted PTY turns prove terminal/protocol
  behavior only. A real user terminal turn, when available, is separate evidence;
  do not impersonate it or claim it completed automatically. The user has been
  asked whether to participate; independent checks can proceed meanwhile.
- **Permissions:** Explore exposes Read/Grep/Glob only. Production uses normal
  scoped edit permissions; Reviewer stays read-only. Test a resumed session in
  both directions. No bypass flags, broad ACL changes, or production-code edits.
- **Evidence:** Preserve relevant original-language messages, role/session IDs,
  tool results, file hashes, invocation metadata, and private transcripts before
  any managed close. Label scripted input and Orch-attested facts. A fixture
  cleanup test must not delete the user's real sessions.
- **Budget and stop conditions:** At most two orchestration fixtures, eighteen
  CLI/model invocations and one real human interactive session; at most ten minutes per
  model invocation. One diagnostic retry for an environmental launch failure.
  Stop affected cases on permission escape, unexpected writes, missing required
  evidence, or exhausted budget; preserve the failure before recovery.

## Evidence

| Evidence item | Method | Result |
|---|---|---|
| Installed CLI and documented interfaces | Local help and official docs | Claude 2.1.301 observed; resume/fork/tool controls available. |
| Interactive session to structured adapter resume | Recall without resupplying discussion-only facts | Both passed with unchanged session IDs. Case-b retained token/corrections/candidate; case-a recalled human-only requirements and correctly reported token/correction absence. |
| Read-only exploration and permission transitions | Tool inventory, sentinel hashes, attempted writes | Case-b Read/Grep/Glob blocked writes; producer resume wrote; reviewer resume removed write tools. Claude independently repeated fork-child write/read-only probes. Tool-capability tests, not an OS-isolation proof. |
| Discussion evidence extraction and preservation | Original messages/session IDs before and after handoff | Both original sessions and message IDs survived managed close. Human export has 25 original discussion messages, excluding later adapter summaries; original source hash verified by Orch. Artifact/evidence hashes unchanged after close. |
| Existing cross-agent session adoption boundary | CLI/engine inspection and actual handoff run | Native adoption not supported: start rejects --session-id (exit 2). Adapter resume and fresh managed evidence handoff work; these are different paths. |
| Codex Orch production and independent review | Managed fixture run and evidence checks | Passed: 20261016-143044-general-78e6; fresh Claude Producer and independent Codex Reviewer; independently-passed, closed, no findings/backlog. |
| Claude Orch reciprocal execution | Observed Claude-issued CLI commands and managed fixture outcome | Passed: 20261016-141421-general-04ea produced by Codex, reviewed by Claude, independently-passed and closed. Nine observed dispatch/probe command attempts; actual results retained in private receipts. |
| Real user terminal interaction | Actual user terminal requirements, confirmed exit, process check, same-ID recall | Passed: user confirmed exit, process count was zero before resume; remembered requirements matched original messages. No token was supplied or fabricated. |

## Decision Criteria

These follow the user's requested capabilities, not a performance benchmark.

| Conclusion | When |
|---|---|
| supported | Required continuity, scoped permission transitions, inspectable retained evidence, and both actual Orch paths work; distinguish adapter support from built-in run adoption. |
| not supported | A reproducible tested interface cannot provide a required capability; report the exact boundary and any narrower working path. |
| inconclusive | All planned observations exist but do not settle a required capability. |

Missing planned human or other required evidence leaves execution incomplete
and the overall conclusion pending; report completed subcases separately.
Do not promote a negative session-adoption result into failure of a working
evidence-handoff path, or vice versa.

## Decisions

- Use experiment-local configuration and Git fixtures; preserve the repository's
  existing config, open runs, and unrelated edits. No commits or deployment.
- Direct CLI launches are the explicitly authorized subject of this experiment;
  production/review mechanisms still run through the existing cross-agent CLI.
- Claude-as-Orch must issue and interpret managed workflow commands itself;
  naming a Claude Producer does not satisfy that test.
- Evidence root: `.cross-agent/evidence/direct-cli-20261016/`; receipts include
  `case-b-audit.receipt.json`, `session-adoption-interface.receipt.json`, and
  case-b provider/managed results. Current source is uncommitted; the copied
  synthetic messages and hashes identify the tested input independently of HEAD.
- The initial scripted launch used `--disable-slash-commands`, which also made
  `/exit` unavailable. Two Ctrl+C presses exited normally; subsequent launcher
  omits the flag. Preserve this failure rather than claiming /exit succeeded.
- Same-ID adapter continuity was tested only after the terminal process exited.
  Claude-led rechecks used a distinct fork to avoid concurrently driving its
  own active session. Forking mid-tool introduced an interrupted-tool context
  warning; prefer a completed-turn handoff boundary.
- Human evidence uses actual terminal-only requirements instead of forcing a
  random token or codename. The user explicitly denied that "3" was a token
  and said no requirement correction was needed. Missing input is an observed
  result, not grounds to invent values or force another interview round.
- Invocation budget refers to externally launched CLI/model sessions/calls;
  internal model requests, tool turns, and real human turns are not equivalent
  units. Raw usage is retained by provider/run, not presented as complete cost
  or a measured token saving. No user-specified time/token ceiling was changed.

## Results And Limits

- Claude 2.1.301 and Codex CLI 0.162.1 were the tested clients. Claude reported
  its actual model; effort remained a configured value when telemetry was null.
  Codex worker telemetry reported model and high effort.
- Native same-ID continuation worked through the unmodified Claude provider
  adapter after terminal exit. Managed production/review used fresh worker
  sessions and preserved original discussion through explicit evidence handoff.
  The current CLI rejected `start --session-id`; no run-state editing was used.
- Both actual coordinators dispatched real configured workers. Claude Orch
  also independently issued production/read-only probes on a separate fork;
  retained tool records show a Write followed by a read-only result without
  write tools. A fork has a new ID and is not same-ID continuation.
- Tool-capability restriction and file sentinels were tested. This is not a
  proof of OS sandboxing, hostile escape resistance, whole-provider privacy,
  or safe multi-user concurrency. Claude production command permissions are
  not a directory-level OS sandbox.
- The human-case Reviewer independently checked original message evidence,
  JSON and provenance fields, but could not independently verify Git scope
  because its commands reported a non-worktree environment. It also did not
  independently hash the original provider file. Orch verified that source
  hash and post-close hashes; the CLI's own check/snapshot guards passed.
- Current close retained the human/expert source sessions because those IDs
  were never registered as managed workers. It deleted the fixture worker
  sessions as designed. This does not establish that adopting a user session
  into the current worker list would preserve it: ownership/cleanup changes
  would still be required before implementing adoption.
- Evidence receipts: `case-a-audit.receipt.json`, `case-b-audit.receipt.json`,
  `case-b-fork-new-tools.receipt.json`, and the two fixture history CSVs. The
  human-case outcome hash after close is
  `e7bd212037217766e3fb6a40f197abdc1e62c23a0dddb8de47e01111c03dfc2f`.
  Raw discussion and tool evidence stays private and out of Git; exported
  messages omit private thinking. No application/Skill implementation changed.

## Decision Informed

The prerequisites for a small direct-discussion handoff are demonstrated.
If the user proceeds, add only a controlled existing-session entry and the
already proposed provenance, permission transition, ownership and retention
rules. Preserve a fresh-worker evidence-handoff fallback. No chat GUI, general
agent framework, always-on Tester, or promised token-saving percentage is
justified by this experiment. This result does not authorize implementation.

## Blockers

- None. Native adoption and the independent Git-scope limitation are recorded
  interface/environment results, not hidden unresolved acceptance passes.
