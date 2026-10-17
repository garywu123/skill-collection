# Cross-Agent Expert Exploration

Status: implemented, independently reviewed, and selectively deployed on 2026-10-16.
This decision supersedes the proposal-only and feasibility-pending statements
in the retained historical review record below. It does not authorize commits.
Implementation and deployment results must be reported from actual checks.

## Implementation Result

- Branch: `feature/cross-agent-expert-sessions`; no commits or pushes.
- Existing project configuration remains compatible. The bundled template adds
  optional domain-expert routes; existing project files are not auto-migrated.
- Implemented `start --first explore --skill`, foreground `expert`, explicit
  `promote`, review opt-out, verified discussion export, protected interactive
  sessions, retained handoff, and scoped local history removal.
- All 138 tests passed. Real Claude terminal discussion resumed as the same
  managed Producer, then an independent Codex Reviewer passed its artifact.
  Close retained the original discussion/session. A separate real terminal
  recheck confirmed automatic startup context and full Skill injection after
  fixing variadic CLI option parsing.
- Claude Opus 5.5 independently reviewed the implementation twice; one Codex
  Producer revision resolved all three accepted major findings. Final status:
  `independently-passed`. Three non-blocking notes remain as `RB-0012` through
  `RB-0014`: close side-effect ordering on retention failure, review-only waiver
  semantics, and provider-generated user-role provenance hardening.
- Deployed only `cross-agent` and `feature-map` to both configured platforms.
  Source/deployment hashes match; all 669 unrelated deployed files and ownership
  manifests were unchanged. Previous copies are retained in private local storage.
- The existing full deployment script still clears its target despite a
  manifest-only statement in `scripts/README.md`; this unrelated conflict was
  avoided by staging the selected Skills and overlaying only their directories.
- Direct terminal control currently supports Claude only. Either host can be
  Orch. Terminal exit does not trigger automatic submission or review; the
  user explicitly returns control. Interactive usage remains unknown, and
  reported managed-worker usage excludes Orch and does not prove total billing.

## Why Change

One coordinating conversation should route work to existing domain experts.
The expert needs to participate while the user discovers the problem, continue
into production when authorized, and preserve evidence that a separate Reviewer
can inspect. Repeatedly reconstructing the discussion through Orch wastes
context and risks turning model suggestions into user requirements. Direct
conversation reduces that repetition; it does not remove production, handoff,
or review context costs, and no token-saving percentage has been established.

Model allocation is configurable judgment, not a proven rule that one model
family designs architecture while another writes code. Orch is the current
Claude or Codex chat. Expertise comes from the domain Skill and supplied
project background; Producer and Reviewer remain the only worker roles.

## Confirmed Workflow

1. Orch resolves intent and existing inputs. Discussion selects read-only
   exploration; a concrete create/update request selects production. Routine
   decomposition can be delegated explicitly. Missing files alone never
   authorize new product scope.
2. Select the domain Skill and configured expert. Supply the goal, background,
   confirmed decisions, consequential questions, relevant AGENTS/CLAUDE guidance,
   and current authorization before opening the expert. Do not demand a title,
   project codename, test token, or another full task description from the user.
3. For supported direct Claude exploration, the user talks to the expert in a
   foreground terminal. The same compatible session can become Producer within
   this stage. Either host provider can orchestrate it. Codex expert work keeps
   the existing relay/fresh-worker evidence route in this release.
4. Exiting the terminal only returns control. Explicit production/submission
   authorization, inspectable in the discussion or supplied by Orch with its
   provenance limitation, permits promotion. Orch reconciles intervening file
   changes against the explore-entry baseline and acquires output ownership.
   The expert cannot authorize its own production.
5. Production normally proceeds to a separate read-only Reviewer. Pause writers
   during review; retain the expert session for accepted repairs. Stage changes,
   unavailable sessions, model changes, or rotation use a fresh worker and cited
   evidence. They do not imply memory continuity.
6. The user can explicitly skip independent review for this run. Retain the
   reason and report that outcome honestly; required self-checks/tests remain.
   An already selected independent gate is not passed by skipping it. A project
   requirement needs the user's explicit adjustment.

“Discuss the Map” does not write rows or statuses. “Generate the Map from the
confirmed Brief and Architecture; decide the decomposition” authorizes that
bounded output. Add only this explore boundary to Feature Map; existing Map,
Plan, delivery ownership, TDD, review budgets and stage sequencing stay intact.
Product Brief, Architecture Design and other existing domain Skills continue
to own their subjects, rather than introducing a parallel department framework.

## Configuration And Minimal Interfaces

Keep one existing project `.cross-agent/config.toml`; no additional mandatory
configuration file. Optional `[experts.<logical-skill>]` tables name `skill`,
`producer`, and `reviewer`. Role precedence is run override, selected expert,
stage, then defaults. `start --skill <logical-name-or-path>` makes general work
select its domain without binding every general run to that Skill. Absent
expert tables preserve old behavior. Config controls worker CLI/model/effort;
it cannot change the current Orch chat's model.

Use existing CLI mechanisms and add only the direct transition:

```text
start --first explore --stage <stage> --skill <name-or-path> --request <context>
expert --run <id>
promote --run <id> --artifact <path> --request <explicit-authorization-and-context>
next --run <id> --stream
```

Promotion can record explicit `--reconcile` direction for intervening changes;
`start --first produce` and `promote` accept `--skip-review --reason` for an
explicit user opt-out. No automatic terminal-close watcher, background polling,
new messaging service, universal evidence schema or permanent memory document.

## Evidence, Permissions And Retention

Preserve relevant provider discussion with available message/session locators,
original-language user statements, corrections, confirmed decisions and
candidate suggestions. Keep Orch translations/interpretations separate. A
provider transcript proves what that session received; host-chat excerpts
remain Orch-attested when their originals are unavailable. Never invent
missing messages or locators. Import relevant authorized material only.

Exploration uses enforced read-only tools; promotion changes permissions through
the managed adapter. Preserve the exploration baseline and reconciled changes
through final review. Retain discussion evidence and handoff under the existing
private history mechanism, `.cross-agent/history/<run-id>/`, together with CSV
telemetry. Session origin and a sticky user-driven marker govern cleanup:
user-supplied or ever user-driven provider sessions survive close. Only CLI-owned
sessions never driven by the user are eligible for cleanup, after necessary
evidence import succeeds. `forget-history --run` removes that run's retained
local history/evidence only, never provider sessions or product artifacts.

## Independent Review And Testing

Reviewer reuses the domain Skill as criteria and checks inspectable originals,
upstream requirements/contracts, relevant business paths, architecture/code,
test changes and real check evidence. Producer summaries are navigation, never
sole intent or correctness proof. Existing review notes record checked areas,
source locators, conclusions and material limitations. Missing provenance stays
unverified and can require a question/finding. Reviewer remains read-only and
proposes evidenced test changes; Producer implements accepted fixes.

No permanent Tester role is needed now. TDD, review and independent execution
cover different risks. For a concrete gap such as an independent oracle,
realistic resource measurement, migration/recovery or browser behavior, use an
existing standalone validation Plan and a fresh Delivery session, with explicit
scope, sources, evidence ownership and final revision. Neither complexity nor
model diversity alone warrants another worker.

## Verification Basis And Authorized Next Step

[Direct CLI feasibility](direct-cli-feasibility.md) records completed human and
scripted tests: same Claude session restoration, read-only/production permission
changes, inspectable source handoff, both Claude-as-Orch and Codex-as-Orch managed
flows, and retention. The tested source CLI did not yet have native adoption;
that negative result motivates this integration. The record remains historical
experimental evidence, not a claim that subsequent implementation is verified.
It includes the independent Reviewer's Git-scope limitation and the distinction
between configured and observed effort.

The user now authorizes a dedicated branch, implementation, validation and
deployment for project testing. Existing projects with Map and Plan should
continue their established planning/delivery route. Deployment does not rewrite
their private configs or migrate active sessions automatically. Report actual
checks, remaining limitations, deployed targets and how to opt into expert routes.

## Historical Reviewed Proposal

The following preserves the earlier proposal and its evidence attribution.
Its proposal-only authorization and pending-feasibility statements describe that
earlier review boundary and are superseded by the current decision above.

### Purpose And User Evidence

The user wants one coordinating conversation with access to domain experts,
without forcing the coordinator to rediscover and rewrite every expert answer.
An expert should participate during exploration, retain relevant decisions into
production, and hand off verifiable discussion evidence. Independent review
must check actual intent, business behavior, architecture, and code as relevant.

The following are faithful excerpts supplied by Orch from the host chat, not
independently verified chat evidence. This worker and Claude cannot inspect
that chat; the excerpts remain Orch-attested. U1-U7 are local excerpt locators,
not host-chat message IDs:

- U1: "尽量复用现有 SKILL 和机制，保持简单，先给方案，不要改文件。"
- U2: "你其实会 launch Claude CLI，然后我在 Claude 中进行来回 chat"
- U3: "会不会造成大量的重复 token 消耗？"
- U4: "你目前即是 producer 也是 orch，而 Claude 是 Reviewer。"
- U5: "有没有必要有 Tester，因为我目前开发，也就是 delivery，他用的是 TDD"
- U6: "reviewer 理论上也会审核并补充或者删除不必要的测试"
- U7: "交给 Claude 5.5 high 去审阅"

U1 requests a proposal first and no file edits at that point; U4 assigns
Codex the Producer/Orch roles and Claude the Reviewer role. U7 requests Claude
5.5 at high effort for review. Opus is Orch's model/configuration resolution
from the prior conversation, not a model specified by U4 or U7. The current
run request authorizes bounded proposal review and adjudicated revisions to
this file only. It does not authorize workflow implementation, deployment,
or imply user approval of the proposed design. U6 describes an expectation
to assess: the current Reviewer cannot edit tests. U2 makes direct expert
conversation a priority; redirecting host-chat input to a CLI is not an
established capability.

### Existing Evidence And Reuse

Read these sources independently rather than relying on this summary:

- [Cross-agent contract](../../skills/coding/cross-agent/SKILL.md): bounded
  runs, relay questions, stage ownership, review budgets, history, recovery,
  snapshots, and no automatic expansion of task authorization. Lines 370-376
  require quoting user answers but also English relay/translation; that does
  not independently establish host-chat wording for the worker.
- [Prompts](../../skills/coding/cross-agent/scripts/crossagent/prompts.py):
  Producer questions are relayed; Reviewer uses Skill, AGENTS, upstream sources,
  evidence-bearing findings, diff, and check results.
- [Provider adapters](../../skills/coding/cross-agent/scripts/crossagent/providers.py):
  Claude currently runs noninteractively with structured results and session
  resume; its Reviewer has Read/Grep/Glob only (lines 204-233). Codex Reviewer
  is read-only (lines 350-365). These managed command flags do not establish
  the permissions of a user-driven interactive session.
- [Engine](../../skills/coding/cross-agent/scripts/crossagent/engine.py):
  full Skill content is injected into both roles on each invocation;
  state, snapshots, checks, session rotation, and cleanup are already managed.
  Lines 693-714 show prompt injection. Lines 393-399 clean every recorded
  worker session and delete run state; provider cleanup deletes Claude
  transcripts/history (providers.py:277-288) and Codex rollouts (432-433).
  Retaining discussion evidence and user-driven sessions requires an explicit
  contract change, not reliance on today's history CSV.
- [Configuration](../../skills/coding/cross-agent/scripts/crossagent/config.py):
  only producer/reviewer roles and four stages exist; a general Skill override
  currently applies to all general runs using that configuration.
- [Product Brief](../../skills/coding/10.product-brief/SKILL.md): explore,
  write, and review already exist; preserve authorized discovery evidence,
  distinguish confirmed decisions from suggestions, and do not write on an
  exploration request. Saving discovery notes requires authorized scope.
- [Architecture Design](../../skills/coding/18.architecture-design/SKILL.md):
  already owns technical exploration, decisions, contracts, and review.
- [Testing Strategy](../../skills/coding/19.testing-strategy/SKILL.md):
  names independent oracles and concrete independent-testing gaps; does not
  launch testers or mandate them solely because work is complex.
- [Feature Plan](../../skills/coding/30.feature-plan/SKILL.md) and
  [Feature Delivery](../../skills/coding/40.feature-delivery/SKILL.md):
  own scenario design, TDD/self-tests, actual results, and selected independent
  gates. Readiness is not an independent pass.

### Proposed Smallest Complete Workflow

Keep Producer and Reviewer as the only configured worker roles. Product and
architecture expertise comes from an existing domain Skill, not new department
classes or copies of that Skill. The current chat remains the Orchestrator.

First, plan a bounded feasibility check for direct conversation, interactive
session resume into managed work, read-only permissions, and available evidence.
Use `feature-plan` validation mode, then a fresh `feature-delivery` session to
execute it only when separately authorized. Direct mode is a user priority;
enable its integration only on positive evidence for the tested provider setup.
The existing managed relay is an interim path, not a replacement for that
objective. Do not prebuild session switching, automatic notifications, or
duplicate-delivery machinery before the feasibility result.

If feasibility supports integration, one task progresses through explore,
explicit write authorization, production, and independent review. Reuse a
compatible Producer session within the same stage when demonstrated feasible;
retain the existing fresh-session boundary between stages
(cross-agent/SKILL.md:215-220). Use the existing request/run-summary handoff and
cited evidence for a missing session or model change; continuity is not memory.

For later integration, add per-run Skill selection for general work as needed,
reusing existing model/effort and CLI configuration. Preserve stage defaults
and old run behavior. Exploration need not have an artifact yet; associate its
intended output before production and acquire the existing ownership lock then.
Competing production runs must still be rejected. Do not invent Feature IDs or
lifecycle documents.

Apply one evidence/transition contract to the interim and proposed paths:

- Relay: the user stays in the Orch chat. Resume the expert with new relevant
  user messages, retaining original-language excerpts and locators alongside
  any English rendering. Present the expert's response without a second full
  analysis; keep routing commentary short. Questions need no permanent new
  role or review round. Orch's selection and translations remain attested.
- Direct, conditional on feasibility: Orch prepares the request and opens or
  adopts a resumable expert session in a user-accessible terminal. The user
  speaks directly to it, then explicitly returns control at a phase boundary.
  Only one actor may drive it at a time. Check what was already delivered at
  handoff rather than promising automatic switching or deduplication.

The feasibility check must demonstrate interactive/managed continuity,
read-only tools/sandbox at launch and resume, evidence import, and what usage
is actually observable. Missing usage stays unknown; missing material evidence
or unenforceable permissions holds the affected integration. Report negative
or incomplete results explicitly; do not simulate direct chat.

Exploration may read project sources but must not modify product artifacts.
Use provider read-only tools/sandbox for exploration, including direct sessions;
a prompt restriction alone is insufficient. The CLI owns only authorized
private recording. Capture the worktree baseline at explore entry, including
pre-existing edits, and compare it at the write transition. Report all
intervening changes; never silently rebaseline them as unrelated. Hold
production on unexplained changes until explicit user direction reconciles
them. Preserve the comparison and authorized reconciliation through final
review so exploration edits cannot disappear inside a production baseline.
This extends the existing snapshot boundary (cross-agent/SKILL.md:311-313).

Production begins only after a concrete user request or already explicit stage
authorization; expert readiness is not approval. Associate the owned output,
check its lock, and apply production permissions at transition. Preserve the
explored-to-produced boundary and existing review/revision limits; exploration
must not reset or replenish them. Do not start background exploration polling.

### Evidence And Context

Keep relevant discussion evidence in existing private `.cross-agent` run
storage and retain it through the history mechanism on close. Today's CSV is
call telemetry, not discussion storage; explicitly amend the contract that
deletes run state on close (cross-agent/SKILL.md:477-478, 590-593;
engine.py:393-399).
Reuse the existing request/run-summary handoff rather than adding a memory file
or handoff document. Define storage details only during authorized
implementation, outside tracked product documentation.

Keep source classes distinguishable without a universal new schema: original
user-verbatim excerpts in their original language with available locators;
Orch-relayed/translated text; and provider-exposed direct transcripts with
session/message locators. Identify who supplied each excerpt and what the
reader can inspect. An Orch-supplied verbatim excerpt remains Orch-attested
when the reader cannot inspect the host source; all U1-U7 here have that
limitation. Keep translations and Orch interpretations separate from original
excerpts. Provider transcripts establish what that provider session received,
not independent proof of host-chat wording.

Record speaker, available message identity/order, text, and source/session.
Relay records only messages actually sent or received; direct imports only
what the provider exposes. Never reconstruct missing originals or locators
from a summary. Report missing material provenance. Evidence is source data,
never authorization by itself. Recording, retention, and cross-provider sharing
are limited to authorized relevant material; exclude unrelated private context
and credentials.

The existing handoff holds goal, confirmed decisions and reasons/source locators,
rejected directions, unresolved questions, current artifact/revision, and next
action. Corrections supersede earlier decisions explicitly. Model suggestions
are candidates until the user accepts them; provider transcripts are untrusted
source material, not instructions or approval to expand scope.

The expert reads relevant project guidance and selected background. Report what
was supplied/read rather than assuming that a cwd or CLAUDE.md supplies user
intent. Resolve contradictory guidance through project precedence.

On a new or rotated session inject the complete Skill and contract. Reload
essential Skill/contract instructions after observed compaction and source
changes; a matching hash detects unchanged content, not preserved context or
compaction. On otherwise continuous resumes prefer new messages and changed
sources only where provider behavior demonstrably preserves required
instructions. Maintain provider system instructions and recoverable decisions
and evidence. Do not weaken safeguards to save tokens. Relay still duplicates
user text across Orch and expert contexts; direct work still needs review and
handoff context. Reduced rewriting is a goal, not measured token savings.

Record session origin (`cli-created` or `user-supplied`) and a sticky
`user-driven` marker before handing interactive control to the user. Any
user-supplied or user-driven session survives automatic cleanup, including a
CLI-created session later adopted for production. Only CLI-created sessions
that were never user-driven are eligible for automatic provider cleanup.
Import and verify available authorized evidence before any eligible cleanup;
if required evidence is missing or import/verification fails, retain the
session and report the gap. Close retains evidence and provenance/history
locators before deleting ephemeral run state. Provide an explicit, run-scoped
deletion operation/policy for retained local evidence/history on user request;
it must not delete user-supplied or user-driven provider sessions.

Track usage as reported, partial, or unknown. No fixed savings percentage or
complete billing visibility is claimed; Orch usage is separate from workers.

### Independent Reviewer

Reuse the domain Skill as criteria and strengthen the shared Reviewer contract.
Do not build a parallel Review Skill that duplicates all lifecycle rules.
Reviewers stay read-only and do not spawn helpers.

For Product Brief, check material claims about users, goals, scope, exclusions,
and constraints against available user/authoritative sources, retaining their
provenance limits rather than treating Orch's relay as independent host evidence.
For Architecture, trace important boundaries/contracts to product constraints
and relevant code/configuration. For delivery, inspect the affected business
paths, code, test changes, and actual check evidence. A Producer's summary is
navigation, never sole proof of user intent or correctness.

Use existing review `notes` ([schema, line 59](../../skills/coding/cross-agent/scripts/crossagent/schemas.py#L59))
to record material areas checked, source classes/locators, conclusions, material
unverified intent, and limitations.
Mark intent backed only by relay or Orch-supplied excerpts as Orch-attested,
not independently supported. Provider-received text alone cannot resolve a
dispute about host-chat wording. Missing material provenance remains unverified
and uses existing findings/questions if it prevents acceptance. Do not add a
universal verification schema or mandatory per-claim paperwork.

Use existing findings for concrete defects or necessary acceptance gaps.
Do not equate no findings with checked coverage, and do not invent findings
for optional design preferences. Verify significant/ambiguous claims against
original sources; do not load all discussion on every review.

Runtime can validate evidence references and revision association but cannot
prove semantic correctness. Preserve strict provider schema compatibility,
bounded review semantics, and explicit unknowns. Review remains distinct from
executing tests that write build outputs or need browser tools.

### Tester Decision To Challenge

Initial recommendation: no always-on Tester and no new tester configuration
in the first version. TDD, independent review, and independent testing address
different risks; neither TDD nor reading tests proves the test oracle is right.

Producer owns TDD, test maintenance, and required checks. Reviewer proposes
evidenced additions/removals, including the distinct failure existing tests
miss; Producer implements accepted changes and reruns affected checks. Reviewer
does not edit tests. Do not delete a required check merely to obtain a pass.

Select independent testing only for a concrete gap: an independent algorithm
oracle, realistic-scale resource measurement, migration/recovery, cross-system
state, or an actual UI/browser behavior that existing evidence cannot settle.
Complexity or model diversity alone does not justify another worker.

When selected, use `feature-plan` validation mode, then a fresh independent
`feature-delivery` session with explicit sources, allowed commands, evidence
ownership, and final revision. Scope it to no production edits and no relaxed
acceptance; authorized temporary tests/reports may use a controlled location.
Today this restriction relies on explicit scope and the reviewed diff, not
hard permission isolation: Feature Delivery can edit production when its Plan
allows it (40.feature-delivery/SKILL.md:179-198). The read-only Reviewer cannot
execute this route. A new configured Tester is justified only if repeated
concrete cases show that route inadequate. Preserve existing gate/status rules.

### Implementation Scope And Acceptance

The minimum next step, if separately authorized, is the bounded direct-mode
feasibility check above. Only positive evidence justifies integration changes
to cross-agent's contract, CLI/state transitions, provider sessions, per-run
Skill selection, evidence/history, focused tests, and existing guides. Reuse
current review notes rather than expanding result schemas. Adjust a neighboring
Skill only for a demonstrated ownership conflict. This review authorizes no
implementation, feasibility execution, deployment, commits, GUI, messaging
system, or model benchmark.

Verify at implementation time:

- Exploration uses verified read-only permissions. Explore-entry and transition
  snapshots detect intervening changes, hold unexplained changes for explicit
  user direction, and preserve the reconciled boundary through final review.
- Exploration cannot promote itself to production.
- Explicit authorization resumes the expert into the correct owned output;
  missing sessions recover from evidence without inventing decisions.
- Direct integration is enabled only after demonstrated continuity, permissions,
  evidence import, and exclusive handoff; switching automation is deferred.
- Unknown evidence/usage stays unknown. A CLI-created session subsequently
  driven by the user survives close even after production reuse, as does a
  user-supplied session. Missing required evidence or failed import/verification
  prevents eligible cleanup.
- Close retains verified evidence/provenance through history; explicit scoped
  deletion removes only requested local evidence/history, not user sessions.
- Independent review detects a material omission and a candidate falsely
  recorded as confirmed, using inspectable sources beyond the author's summary;
  Orch-attested intent and material missing provenance are reported honestly.
- Reviewer remains read-only; accepted test changes are Producer work.
- Existing runs, stage selection, checks, budgets, and permission guards remain
  compatible except for the explicitly proposed exploration and retention
  changes. Amend cleanup and close contracts rather than promising unchanged
  deletion behavior.

### Review Notes And Remaining Gate

Accepted review corrections require accurate attribution, provenance limits,
an explore-entry baseline, enforced exploration permissions, and safe session
retention in the proposed design. They do not constitute user approval of it.
The minimum viable recommendation is a direct-mode feasibility check first,
then only the evidenced integration; managed relay can serve in the interim.
No new expert hierarchy, switching framework, memory document, universal
evidence schema, or always-on Tester is justified by the current use case.

Tester conclusion: retain Producer TDD plus independent read-only review as
the default. Review can challenge test additions/removals but Producer makes
accepted edits. A concrete independent-testing gap uses the existing standalone
validation route; TDD alone neither requires nor rules out that gate. This is
a recommendation assessed against U5/U6 and the domain Skills, not a quoted
user decision to approve or reject all independent testing.

The accepted corrections are incorporated; direct-provider feasibility and
implementation remain unverified and outside this run. Independent re-review
and the user's design decision remain with Orch. A reviewed proposal is not
tested software and does not authorize the next stage.
