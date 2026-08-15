---
name: feature-implementation-plan
description: Assess one approved roadmap feature and prepare the smallest implementation-ready TDD delivery packet. Use when a user wants to plan, review, or begin one feature; decide whether the target is cohesive enough to implement; create implementation-plan.md and checklist.md for a compact feature; or hand a domain-sized target back to product-discovery-roadmap for reassessment. Do not use to invent product scope, approve roadmap changes, or implement the feature.
---

# Feature Implementation Plan

Prepare one roadmap feature for implementation without repeating the PRD, roadmap, or architecture baseline. Treat compact planning as the normal route. A large project does not by itself require Spec Kit; feature cohesion and unresolved behavior determine the route.

## Operations

- `assess <feature-id>`: read-only. Classify the target and report the next action.
- `plan <feature-id>`: assess first, then create a compact delivery packet only when the feature is cohesive.
- `audit <feature-id>`: check an existing packet for source alignment, actionable slices, verification coverage, and stale assumptions. Report findings before making any requested repair.

If the user omits the operation, use `plan` when they ask to prepare work and `assess` when they only ask whether the feature is ready.

## Required Inputs

Read, in order:

1. the project map and its canonical paths, if present;
2. the approved feature roadmap root and the target feature detail;
3. every owned and additionally bound product requirement;
4. the approved architecture baseline and applicable decisions;
5. repository evidence needed to locate existing components, tests, and conventions;
6. existing target artifacts when auditing or replanning.

Stop if the feature is absent, the roadmap is unapproved, a referenced source is unavailable, or canonical sources materially disagree. Report the smallest corrective action and the owning Skill.

## Assess Cohesion Before Writing

Classify the target using evidence, not project size.

### Compact

Choose `compact` when the target has one independently acceptable outcome, a coherent boundary, testable acceptance criteria, and can be delivered through a short dependency-aware sequence of vertical slices. It may touch several classes or layers.

### Roadmap reassessment required

Choose `reassess` when the target behaves like a domain or program rather than one feature. Strong signals include multiple separately valuable outcomes, independent lifecycle/state models, unrelated acceptance paths, several owning teams, or a dependency graph that would remain meaningful if split.

Do not create or edit feature artifacts. Output a **Roadmap Reassessment Handoff** containing:

- target feature ID, domain, and evidence for the classification;
- candidate feature outcomes using temporary labels, never canonical `F###` IDs;
- requirements and acceptance criteria that appear to belong to each candidate;
- dependencies, shared constraints, and unresolved decisions;
- a recommended amendment scope;
- the exact next prompt: `Use $product-discovery-roadmap amend CR-XXXX to reassess <feature-id> using this handoff.`

Only `product-discovery-roadmap` may propose and, after approval, assign canonical feature IDs or revise the roadmap.

### Detailed exception

Recommend a detailed Spec Kit-style bundle only when the feature remains cohesive but behavior cannot safely be expressed by the roadmap, architecture baseline, implementation plan, and checklist—for example a new public protocol, complex state machine, regulated traceability contract, or unusually large unresolved behavior model. Explain the missing value. Never select detailed merely because the project is large.

For this result, create nothing and invoke nothing. Report the exact missing
behavior-model value and the explicit detailed-workflow prompt the human may
choose. The detailed workflow owns its own files.

## Create the Compact Packet

For `plan`, copy and complete:

- [implementation-plan-template.md](assets/implementation-plan-template.md) as `specs/<feature-id>-<slug>/implementation-plan.md`;
- [delivery-checklist-template.md](assets/delivery-checklist-template.md) as `specs/<feature-id>-<slug>/checklist.md`.

Then update only the target feature entry in `roadmap.yaml` with `domain`, `plan`, and `checklist`. Preserve `status: planned`; planning is not implementation. Do not create `spec.md`, `research.md`, `data-model.md`, or `tasks.md` on the compact route.

The implementation plan must contain only implementation-specific decisions:

- sources and the cohesion result;
- affected classes/types/components, their responsibilities, key functions, dependencies, and likely repository paths;
- ordered vertical delivery slices, explicit dependencies, and safe parallel work;
- verification mapping from acceptance criteria to planned unit or integration evidence;
- risks, blockers, and decisions that must be resolved before a slice starts.

Do not restate product prose or architecture narrative. Link to the canonical source. Do not claim test results before tests run.

The checklist is the delivery gate. It contains exact acceptance items, applicable architecture constraints, quality checks, and an evidence table populated during implementation. Feature implementation tasks belong in plan slices; completion and proof belong in the checklist.

## TDD and Completion Boundary

Shape each delivery slice so an implementing agent can follow red, green, and refactor, but do not duplicate generic TDD instructions. Unit versus integration is chosen by the behavior boundary, not by a fixed quota.

This Skill does not implement code, mark roadmap features complete, or approve artifacts. After planning, use `$spec-sync pre-implement <feature-id> feature`, then the repository's TDD workflow. After implementation, use `$spec-sync post-implement <feature-id> feature` and a fresh-context verification before the roadmap status changes.

## Audit Rules

An audit fails when any of these are true:

- a plan duplicates or contradicts canonical product or architecture content;
- a class/function proposal has no responsibility or behavioral reason;
- a slice is layer-only rather than vertically verifiable;
- dependencies or parallelism are ambiguous;
- an acceptance criterion has no planned evidence;
- the checklist contains implementation design instead of gates and evidence;
- actual results are asserted without a reproducible command, artifact, or test reference;
- the roadmap paths, domain, or feature status disagree with the packet.

Report findings by severity and file location. Repair only when the user asks to update the artifacts.
