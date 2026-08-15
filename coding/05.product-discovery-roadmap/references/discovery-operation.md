# Discovery Operation

Use the [discovery notes template](../assets/discovery-notes-template.md).

1. Establish why the product is needed, what it should mainly do, its primary
   workflow, users, operating context, and the domain facts needed to understand
   the job.
2. Ask only questions that can change scope, behavior, priority, safety, or
   success criteria; at most five independent numbered questions per round.
3. Recommend an answer only when evidence supports it, and state its consequence.
4. Rewrite the notes as a concise current understanding after each conversation.
   Do not append interview rounds, transcripts, decision IDs, rejected options,
   or superseded conclusions; Git already preserves earlier versions.
5. Maintain substantial reusable vocabulary, existing-process detail, and
   confirmed domain facts in focused `doc/domain/<topic>.md` files. Link them
   from the notes and do not duplicate their contents.
6. Keep `Critical Unknowns` only for unresolved answers that could change core
   behavior, the MVP boundary, or feasibility. Delete answered or non-blocking
   questions instead of carrying them forward.
7. Mark `Ready for PRD` only when those unknowns are resolved or explicitly
   bounded.

Stay at product altitude. Technology, storage, APIs, components, and frameworks
belong elsewhere.
