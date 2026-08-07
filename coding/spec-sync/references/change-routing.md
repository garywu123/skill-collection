# Change Routing

Read this reference only for `change-request`. The result is a proposal for the human
controller, not authorization to execute any routed action.

## Invariants

1. **Preserve approved IDs.** A changed approved `PR-###` receives a successor ID; the
   owning requirements workflow records the supersession. Never renumber or reuse IDs.
2. **Preserve delivery validity.** When accepted behavior changes in place,
   reset it to `specified`, remove `verified`, and clear stale checklist results;
   Git preserves the prior version. Use a successor only when the behaviors
   need independent deployment, support, acceptance, migration, or tracking.
3. **Route top-down.** Resolve the highest affected source of truth before downstream
   feature artifacts.
4. **One owner per action.** `spec-sync` identifies the owner, suggested input, and expected
   output, then stops. It never invokes the owner or performs the edit.

## Highest-impact layers

Select the highest layer touched, then include every lower affected layer.

| Layer | Signal | Owning workflow |
|---|---|---|
| Product truth | User capability, business rule, or requirement changes | `product-discovery-roadmap amend` on requirements |
| Feature boundary | Scope, ownership, dependency, horizon, or successor feature changes | `product-discovery-roadmap amend` on roadmap |
| Cross-feature technical decision | Approved constraint or shared boundary must change | `architecture-baseline amend` |
| Navigation or global shell | Product-wide navigation or shared UI structure changes | `ui-wireframe-spec product` |
| Project governance | Build, repository layout, or agent working rule changes | `project-map refresh` |
| Feature internals | Only one non-delivered feature's behavior changes | Human-authorized feature specification workflow |

The list above names possible next workflows; it does not authorize their use.

## Route feature-internal impact by current state

| Current state | Proposed route |
|---|---|
| Planned, not specified | Ask the roadmap owner to amend the entry, then re-enter feature specification |
| Specified, not implemented | Re-authorize specification/clarification; refresh UI, plan, and tasks only where affected |
| In progress | Stop affected implementation; ask the human whether to finish a safe slice or re-specify now |
| Verifying | Propose returning to the earliest affected stage; the stale evidence rows in `checklist.md` must be struck or re-run, not left standing |
| Accepted | Propose one of the two routes below, and say which and why |

For an accepted function, the default route is to edit its spec and checklist in
place, reset `status` to `specified`, delete `verified`, and clear every old
checklist box, Evidence row, Decision, reviewer, and date. Git retains the
previous version. Propose a successor only when the old and new capabilities
need independent deployment, support, acceptance, migration, or long-term
tracking; cross-reference both entries in `notes`. Never leave acceptance
evidence on behavior that has since changed.

Do not infer delivery state from roadmap wording. Use `roadmap.yaml` for the
current status of each function, its `checklist.md` for delivery evidence, and
Git history for what changed when; report conflicting evidence and stop.

## Required proposal

For each change request, record:

- original request and source;
- highest affected layer and rationale;
- affected IDs, artifact paths, current states, and evidence anchors;
- ordered actions, one owner and expected output per action;
- stale downstream artifacts/evidence that will require revalidation;
- exact suggested next prompt or command for the human to choose;
- decision and every action as `Pending`.

Use the bundled CR template when the project keeps change-request records.
`spec-sync` may create or update only that proposed record. It must not edit
requirements, roadmap, ADRs, guidance, feature artifacts, or `roadmap.yaml`.

## Compact example

For a request that changes a product from one workspace to multiple workspaces:

```text
Highest impact: Product truth

1. product-discovery-roadmap amend
   Expected output: one reviewed product amendment covering successor
   requirements, feature boundaries, and dependencies; canonical truth unchanged.
2. product-discovery-roadmap approve-amendment
   Expected output: the explicitly approved proposal applied to canonical product truth.
3. architecture-baseline amend
   Expected output: reviewed architecture amendment and proposed superseding ADR.
4. architecture-baseline approve
   Expected output: the explicitly approved baseline/ADR promotion.
5. project-map refresh (only if working rules changed)
   Expected output: guidance derived from the newly approved sources.

All actions: Pending human authorization. No workflow invoked.
```

## Scale

Large or regulated projects should keep one CR file per request. A small project may return
the same structured proposal in the response when its approved workflow does not require
CR files. The invariants and human decision points do not change with project size.
