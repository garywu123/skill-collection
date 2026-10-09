# Lean Skill Workflow Change Plan

## Current position

**Batch 1: completed and self-validated.** The user authorized only the first batch: invocation-policy consistency, consequential questions, evidence-based review, adequate test reuse, and compact handoffs. The existing Cross-agent suite passed all 107 tests in 81.320 seconds; document and deployment-preview checks passed. Batch 2 (model configuration trials) and Batch 3 (possible runtime extensions) are deferred until real usage demonstrates a need; neither is a scheduled next step. No deployment, commit, application change, model-default change, or new review run is included.

The earlier plan was reviewed by Fable 5.1 after one GPT-6 Astra medium revision. Run `20261008-144809-general-0e4c` closed with `needs-user-decision` because its check found the invocation-policy conflict (106/107 passed). The user later allowed automatic selection. This batch repairs that conflict; it does not rewrite the closed run's result. Fable reviewed the earlier plan, not this implementation or the later model-routing proposal.

## Outcome and design claim

Small changes to existing instructions and prompts should improve project-aware questions, resist unsupported hardening and duplicate tests, and reduce repeated Orch reading. The only added resource is Cross-agent's Codex discovery policy. No engine, schema, config parser, CLI argument, provider, budget, or saved-state mechanism changes. Static walkthroughs and existing tests can expose contradictions but cannot prove model compliance, lower context usage, or cost savings.

## Evidence and limits

Current Skill Collection owners were inspected at `27ef961`:

- [Feature Plan](../../skills/coding/30.feature-plan/SKILL.md), Risks And Questions / Output, and [Testing Strategy](../../skills/coding/19.testing-strategy/SKILL.md), Evidence And Questions, already require high-value, evidence-first questions and distinguish requirements from testing methods. [Feature Delivery](../../skills/coding/40.feature-delivery/SKILL.md) already preserves safeguards, failure evidence and tested-tree provenance. Clarify application rather than add another discovery process.
- [Cross-agent](../../skills/coding/cross-agent/SKILL.md), Adjudication, already requires asking before `decide` when a blocking defect needs a user decision. [Prompts](../../skills/coding/cross-agent/scripts/crossagent/prompts.py) and [engine](../../skills/coding/cross-agent/scripts/crossagent/engine.py) preserve findings, accepted guidance and bounded revisions. Reviewer schemas have no questions field, but no recorded case demonstrates that the existing evidence-backed finding route cannot carry a necessary decision. A question hidden in notes cannot block completion; it is not the proposed route.
- `engine.py` freezes project settings at `start`; `general` and `feature-delivery` share saved `delivery_checks`. [Config](../../skills/coding/cross-agent/scripts/crossagent/config.py) already supports explicit `CROSS_AGENT_CONFIG` and role precedence of run override, stage, then defaults. Use these before adding CLI options.
- Brief/Spec owns confirmed product constraints, Architecture shared technical direction, Map outcomes/dependencies, and Plan concrete scenarios. Product Brief/Feature Map inspection found no ownership gap requiring edits. Worker rotation seeds workers, not parent Orch; worker CSVs do not measure parent context or billing.
- **Historical planning-run check:** Cross-agent executed `python -m unittest discover -s skills/coding/cross-agent/scripts/tests`: exit 1, 106/107 passed. `ExecutionTests.test_implicit_policy_is_enabled_only_for_the_three_agreed_skills` in `scripts/tests/test_execution.py:330` then expected Cross-agent `disable-model-invocation: true`, whereas `cross-agent/SKILL.md:4` says `false`. `skills/coding/README.md:28` then described an explicit-invocation boundary and agreed with that test. Accepted review evidence identifies commit `8a6733b` as enabling model invocation. The user has now confirmed automatic selection. Batch 1 preserves model-invocable frontmatter, adds the matching Codex policy, and aligns the existing test and public instructions; the historical run remains unchanged. Automatic Skill selection does not authorize new scope or bypass existing human gates.

Recorded **AGV-TOOLS** evidence supplied by Orch, snapshot `af3a114` with uncommitted D15 docs, was not reproduced here:

- G01-F10 history: 16 runs, 39 Producer calls, 29 Reviewer calls, about 377 worker minutes; five runs had only R1, two reached R3. Scope included browser Open/Save, shell migration, D11 Host store, D12/D13 429 simplification and D14/D15 direction changes. This neither isolates review overhead nor proves `xhigh` inherently finds defects. Full closed-run transcripts are unavailable; do not infer defect/rejection rates.
- `docs/features/05.full-gui/G01-F10-project-files.md`, historical Decisions R1/R2: file association/unsaved protection and `useLayoutEffect` shortcut-state correction were useful. D11 required each committed edit durable and D14 retained that. The current Product Brief makes the OneDrive-synced SharePoint file official and Host store a working copy. Local use does not cancel safeguards; trusted-file/no-attacker assumptions were unconfirmed.
- `frontend/docs/review-backlog.md`: RB-0027, source `20261006-155718-feature-delivery-8435` R1-003, fixed cleanup that trusted an inherited directory and could delete user data. RB-0029 strengthened the existing Retry-After case with positive time/fake timer, explicitly without another case. RB-0036 rejected a native Edge picker drawing requirement. RB-0038 was manual-acceptance Host build/port interference during storyboard work, not a document defect.
- The F10 file's Revision decision at snapshot line 193 removes the flaky `holdProjectGate` e2e seam: backend tests prove gate ordering; an App test proves envelope behavior. `fd7707c` (+151/-640), `cf2e3ef` (+100/-236), `f555d5f` (+321/-541) are additions/deletions, not net deletions. `7985fae` added HTTP ExpectContinue and adjusted socket deadline/count oracles, not universal clock injection.
- F10 Plan: 368 lines/about 143,352 characters; temporary tracker: 442/about 125,949. Line caps alone do not bound reading cost. No unavailable tracker locator, parent usage or billing estimate is inferred.

## Batch 1 implementation scope

Paths below are relative to `skills/coding/`. The changes update the existing owners; templates need no change. Cross-agent automatic discovery is aligned in its description, `agents/openai.yaml`, collection README and existing `test_execution.py` policy check. Existing unrelated Storyboard edits, including its README row, are preserved.

1. **`30.feature-plan/SKILL.md`, Risks And Questions / Workflow.** For a mechanism or test addition, explain supported trigger, source, user consequence and simplest acceptable behavior in existing prose/scenario rows. Read prior decisions first; ask only unresolved choices changing design or acceptance, using user terms instead of implementation jargon. Preserve confirmed answers; route new guarantees to their upstream owner. Remove the “two to four rows is normal” cue, which can act as a quota.
2. **`19.testing-strategy/SKILL.md`, Output / Review Criteria.** Each unit, component, integration or e2e check names the distinct failure it detects and uses the smallest adequate level. Prefer strengthening existing cases. Multiple levels are justified by different failures, including real native/browser boundaries. Plan references this reusable rule rather than copying it.
3. **`40.feature-delivery/SKILL.md`, Delivery Loop.** Existing adequate coverage may satisfy a behavior; add/strengthen only for a gap. Preserve happy-path-first work, discovery, safeguards, required regressions and tested-tree evidence. Classify product failure, test defect and environment problem before repair. An unexplained passing retry leaves a risk. Do not repeat discretionary whole suites without changed relevant evidence or a verification gap; required checks still run at their required boundaries. No result cache or relaxed CLI gate.
4. **`cross-agent/SKILL.md`, Adjudication, and `cross-agent/scripts/crossagent/prompts.py`, Reviewer instructions.** Existing `claim`, `evidence`, `recommendation` explain the supported trigger, violated promise, impact and smallest repair. Concrete code-supported data-loss/security consequences remain valid even without exhaustive written requirements. Orch evaluates evidence rather than automatically accepting severity labels; preserve dispositions, severity eligibility and later-review restrictions. Apply the decision route below.
5. **Plan Output, Delivery handoff/results, Cross-agent Inputs / Live Reporting.** Keep current outcome/source links, latest decisions, completed/next segment, unresolved failures/findings, remaining gates and tested evidence locators. Remove obsolete scenarios from the active view only when decisions and evidence remain recoverable in existing history or retained references. Keep a short supersession reason; never discard unique audit evidence or hide unresolved failure. No new tracker/archive. Orch reads cited sources/diff hunks on demand and reports concise progress rather than replaying logs. A fresh executor can resume without the transcript; worker rotation does not rotate Orch, and no restart after every step is required.
Model/check separation: Batch 1 clarifies selection of an existing suitable check configuration before start, without modifying any configuration. Model guidance and example changes belong to deferred Batch 2.

### Batch 2: deferred model-routing candidates

**Deferred by the user; revisit only after actual usage, not automatically after Batch 1.** If reopened, use configuration for repeatable defaults and Orch judgment for exceptions. Do not add a classifier agent, scoring system or new router. The existing precedence is run override > stage configuration > defaults. Before launching, report one concise line containing the outcome, stage, chosen Producer/Reviewer and effort, reason, and applicable checks. Reuse this in the existing request/handoff rather than create another artifact.

These are trial defaults, subject to installed CLI/account availability and actual results; they are not claims that a model always costs less or finishes faster:

| Task and boundary | Producer | Reviewer | Override reason |
|---|---|---|---|
| Routine implementation, including UI, with agreed behavior and local effects | Sonnet 5.5 medium | GPT-6.1 Sol medium | Escalate for concrete cross-component uncertainty or serious failure consequences, not merely because the code is frontend/backend. |
| Feature Map / Feature Plan with unresolved decomposition or acceptance choices | Opus 5.5 medium | GPT-6.1 Sol high | Astra medium is an alternative Producer; a small revision to an agreed plan may use routine roles. |
| Architecture with consequential shared contracts or difficult tradeoffs | Astra medium or Opus 5.5 medium | Fable 5.1 high | Choose one Producer before start. Reserve the strongest pair for these decisions or evidenced reasoning difficulties. |
| Delivery involving persistence, concurrency, permissions or credible data-loss risk | Opus 5.5 medium | GPT-6.1 Sol high | Use Fable for unusually difficult invariants; strong review cannot substitute for an authoritative product decision. |

Official family guidance supports Sonnet for everyday coding and Opus/Fable for harder work, and Sol as a capable coding option alongside Astra: [Claude model configuration](https://code.claude.com/docs/en/model-config), [OpenAI model guidance](https://learn.chatgpt.com/docs/models). The table is our proposed trial policy, not a provider guarantee. Effort labels are not equivalent across models. Explicit IDs pin versions; reassess availability when configuring, without making every run a model research exercise.

Illustrative **fragment to merge into an existing complete configuration**, not a replacement file or an applied change:

```toml
[defaults]
producer = "claude:claude-sonnet-5-5:medium"
reviewer = "codex:gpt-6.1-sol:medium"

[stages.feature-map]
producer = "claude:claude-opus-5-5:medium"
reviewer = "codex:gpt-6.1-sol:high"

[stages.feature-plan]
producer = "claude:claude-opus-5-5:medium"
reviewer = "codex:gpt-6.1-sol:high"
```

`feature-delivery` inherits routine defaults in this example. The only supported stages are `feature-map`, `feature-plan`, `feature-delivery` and `general`; Architecture Design currently uses `general` with explicit start role overrides. Do not invent `[stages.architecture-design]` or make every `general` task expensive. Existing explicit user role assignments still override this policy, including Astra medium/Fable 5.1 for the earlier planning review.

Roles are fixed for a run. Make risk adjustments before `start`; do not promise live switching between steps, split coherent work solely to change models, or restart to replenish budgets. For a mixed run, choose roles adequate for its hardest material decision. Consider runtime routing only if actual repeated use shows stage defaults plus start overrides are insufficient.

If Batch 2 is reopened, pilot on naturally occurring routine UI change, planning task and persistence-sensitive change; do not manufacture tasks or repeat completed work solely for comparison. Use existing history to compare elapsed task time (including checks/rework), worker calls, input/cache/output usage as reported, accepted/rejected findings and observed defects. Track parent Orch context separately if available; cumulative worker tokens are not its context size or a bill. Retain cheaper roles only when correctness and rework remain acceptable. This is an observational pilot, not a controlled benchmark or a mandatory numerical quota.

### Necessary decisions through existing findings

When a genuinely missing authoritative decision prevents judging an already-requested outcome, Reviewer reports the concrete acceptance gap, checked sources/evidence, consequence and question for Orch using existing finding prose. Do not invent a requirement, unsupported defect, confirmed assumption or severity merely to transport a question. Optional/speculative uncertainty remains notes.

Orch resolves it from a cited explicit prior/current user decision, or asks the user **before `decide`** and leaves the finding pending while waiting. Put the answer and authority in adjudication guidance so accepted work reaches Producer and subsequent review. Keep the existing acceptance eligibility, single revision per qualifying review, and later-review limits; questions earn no extra review slots. Do not reject a necessary unresolved gap or demote it to notes just to obtain a pass. A deferred blocker is disclosed, and `completed-by-orchestrator` is never an independent pass. If this route cannot represent a demonstrated necessary decision honestly, report that limitation; do not fabricate a finding to fit it.

Defer first-class Reviewer questions and schema/engine/CLI changes until such an observed case shows this route inadequate. There is no question-origin state, new phase, answer-routing mechanism or compatibility migration in this increment.

### Task checks through existing configuration

Before starting, use the normal project configuration or explicitly select an existing task-appropriate complete configuration with `CROSS_AGENT_CONFIG`. Inspect it through `status` and the task's authoritative check requirements: commands must be verified, all required settings/CLI paths and the matching project entry present, required user/project gates retained, and `allowed_commands`/`extra_dirs` within authorized permissions. A configuration suitable for document work must not inherit unrelated Host checks or broaden permissions. Selection does not authorize creating/editing configuration; if none is suitable, disclose the gap and seek separately authorized configuration work.

Record the selected configuration locator, reason, effective checks and permissions in the existing stage request/handoff with its run ID; do not expose private paths in tracked documents or require a new record. Keep the selected configuration available for subsequent calls, since executable paths are reread. `start` already saves checks, roles and budgets; use CLI status to inspect them, never edit run state. No override preserves existing default behavior. Empty checks mean no automated checks configured, not passed tests; state applicable document/manual verification.

Do not switch configuration, drop saved checks or open another run to evade a failure. Preserve its evidence and apply existing recovery rules after resolving the cause. Defer `--checks-file` and check profiles until concrete operational friction demonstrates that existing explicit selection is insufficient. Saved-run compatibility and budgets are unchanged.

## Batch status and verification

| Batch | Scope | Status |
|---|---|---|
| 1 | Align automatic invocation; update Plan/Testing Strategy/Delivery rules, Cross-agent adjudication and handoffs, worker prompts, public descriptions and the existing invocation test. | Completed; 107/107 existing tests passed, plus static acceptance and document checks. |
| 2 | Trial different Producer/Reviewer defaults and risk-based start overrides. | Deferred; no project configuration or example changed. |
| 3 | Consider runtime routing, live model changes, first-class Reviewer questions or other mechanisms only for demonstrated gaps. | Deferred; no runtime extension implemented. |

The existing full suite includes the focused `test_cli.py` path and the corrected invocation test: `python -m unittest discover -s skills/coding/cross-agent/scripts/tests`. Run it once after edits instead of separately repeating that subset. No new test suite, live-provider test, application e2e run, or string-mirroring prompt test is added. Inspect complete generated Producer and later-round Reviewer prompts, document links/headings/discovery policy, and the adversarial cases below. Run deployment `-ListOnly` solely to validate active mappings; it does not deploy. Broaden or repeat checks only for changed evidence, a failure, or an unresolved verification gap.

## Adversarial acceptance walkthrough

| Scenario | Required outcome |
|---|---|
| Speculative hardening | Universal retries/locks supported only by hypothetical future concurrency are omitted or noted; no invented guarantee/test appears. A real missing supported-use choice is asked in user terms. |
| Necessary protection | Local single-user use does not justify removing durable edits, unsaved protection or safe cleanup. The sourced promise/concrete deletion consequence governs. |
| Test placement | Backend gate-order and App envelope tests cover distinct failures without a duplicate e2e seam. A real native/browser gap still merits adequate evidence. Strengthen the existing Retry-After case. |
| Reviewer decision | An evidenced acceptance gap remains pending while Orch obtains an authoritative answer before `decide`. Guidance carries that answer; no unsupported finding/severity is invented and no unresolved blocker is presented as an independent pass. Existing review/revision limits remain binding. |
| Document checks | Before start, an existing complete configuration selects verified document checks without an unrelated Host or broader permissions, while preserving required gates. Without a suitable config, report the gap. A later port failure remains environment evidence, not authority to drop checks. |
| Fresh handoff | Current position, source links and CLI status identify next work, tested revision/content, open failures and gates without old transcripts. Necessary provenance survives compaction; no parent-usage claim or mandatory restart. |

Author walkthrough completed against the final instructions: unsupported retries/locks remain optional; durable edits and cleanup protections remain required; gate-order and envelope checks cover different failures; evidenced acceptance questions route through pending adjudication; document checks are selected before start without dropping gates; compact handoffs retain decisions and evidence locators. These are static scenario assessments, not new live-model or AGV test results. The generated prompts and existing suite were also checked. It requires neither token savings nor a quota of tests/findings. Saved-budget integrity is preserved through existing paths, not a new implementation segment.

## Decisions, exclusions and remaining risk

- Automatic Cross-agent selection is confirmed. Discovery does not authorize new product scope, mandatory multi-agent execution for every edit, or bypassing selected gates.
- Only Batch 1 is authorized now. Batches 2 and 3 remain candidates, with no automatic continuation. No model defaults, application configuration, engine, schema, budgets or runtime checks were changed.
- Implementation updates this same Plan with actual results. No new tracking document, transcript or per-round narrative is required. Existing unrelated work and untracked files are preserved; no deployment or commit was requested.

Remaining limits: instruction changes cannot guarantee agent behavior or savings; configuration selection cannot mechanically prove compliance with prose gates. A Reviewer decision that cannot honestly fit the existing finding route remains a disclosed limitation, not a reason to fabricate severity or add a runtime mechanism now. Other upstream Skills already have some explicit-invocation descriptions paired with model-invocable Claude frontmatter; that pre-existing policy mismatch is outside the Cross-agent-only invocation decision and is not silently broadened here.

## Verification and retained history

Implementation verification at revision `27ef961` with these uncommitted task changes:

- `python -m unittest discover -s skills/coding/cross-agent/scripts/tests`: **107/107 passed**, 81.320 seconds. Includes focused CLI/prompt paths, invocation metadata, review budgets and existing guards. The existing discovery-policy test was updated; no additional suite was created.
- Complete generated Producer and R2 Reviewer prompts: inspected for scope, decision routing, concise handoffs, test reuse and preserved later-round restrictions.
- Six changed Markdown documents: UTF-8 without BOM, one H1, heading hierarchy, local links, Skill folder/name alignment and whitespace checked; Cross-agent discovery YAML and the deferred TOML fragment also checked.
- `powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1 -ListOnly`: passed; all four changed Skills remain mapped. No deployment or external synchronization was performed.
- `git diff --check`: passed. Pre-existing Storyboard files and their README row, backlog content, and private configuration were not edited by this batch. Repository instruction routes, commands and structure remain unchanged, so `AGENTS.md` needs no update.

This is author validation, not an independent Fable pass. No live worker, client discovery behavior, app behavior, token saving or parent context improvement has been re-evaluated. Changes remain uncommitted and undeployed.

Historical plan review: R1-001 accepted and resolved by disclosing the baseline policy conflict; R1-002 accepted and resolved by removing unproven runtime proposals; R2-001 note-only (CLI backlog `RB-0005`), UTF-8 BOM mechanically removed after close. The earlier planning checks produced 106/107 tests plus passing deployment preview, installation list and whitespace checks. Test execution belonged to Cross-agent's configured checks, not the planning Producer. Worker history remains in ignored `.cross-agent/history/20261008-144809-general-0e4c.csv`; it excludes parent Orch usage. The earlier `.claude/` directory was left untouched. Earlier post-close mechanical edits and the model-routing amendment were not independently re-reviewed.
