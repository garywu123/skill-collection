# Spike Result Operation

Use only for an explicitly requested `resolve-spike SPK-###` operation.

1. Verify the approved architecture baseline still contains the exact SPK ID,
   one answerable question, time box, blocked owner/work item, and disposable
   output expectation.
2. Start only `kind: spike`, the named SPK ID, stage `spike_result`. Read the
   spike definition and the smallest repository or external evidence needed;
   do not load unrelated PRD, roadmap, feature, or architecture sections.
3. Stop when the time box expires. Preserve commands/activities, revision,
   results, and evidence paths; mark the outcome `answered` or `inconclusive`.
4. Create `doc/architecture/spikes/<SPK-ID>.md` from the
   [spike result template](../assets/spike-result.template.md). Leave
   `roadmap.yaml` unchanged — a spike closes an investigation, not a decision.
   Report the pending human review and stop.
5. Human approval closes only the investigation. If the answer would change
   an approved baseline, ADR, or Plan Constraint, route a separate CR and wait
   for an explicitly authorized architecture amendment. Never edit canonical
   architecture during this operation.
