---
name: document-simplification
description: Review and rewrite one or a few existing Markdown or HTML documents so their intended reader can understand them and act after one read - read as that reader first, propose a new structure when the current one gets in the way, then rewrite whole sections in plain, concrete language. Invoke explicitly, by name, when documents are too long, too abstract, defensive, or written as an analysis record instead of a working reference. Do not use for whitespace-only reflow, repository-wide code and mechanism proportionality reviews (simplification-review), or changing what a document decides or requires.
disable-model-invocation: true
---

# Document Simplification

Work like a capable colleague handed a document to clean up: read it as its
reader, notice where reading stalls, agree on a better shape, and rewrite it
so a person can follow it. Readability comes first; the result does not need
to be perfect, but it must be readable.

## Reader first

Before judging anything, name the reader and the real task they do after
reading, in one sentence: "an engineer who writes the Order query next", "a
reviewer who approves the design". Take it, in this order, from the user's
request, the project's document guidance (for example a document requirements
file routed by `AGENTS.md`), or the Skill that owns the document type. When
none says, infer it from the document's location and content and state the
assumption.

A document owned by another Skill keeps that Skill's required shape and word
budget; simplify within them.

## Procedure

1. Read the whole document once as that reader. Note where you stop: a
   sentence you must reread, a rule you cannot act on, information you have to
   search for, or text addressed to someone else.
2. Load [the anti-patterns](references/anti-patterns.md) and only the
   reference that matches the document type:
   [data analysis](references/data-analysis.md) for report, source-data, and
   investigation pages; [folder README](references/folder-readme.md) for a
   folder's `README.md`. References show common shapes and failures; they are
   not templates. With no matching reference, work from the reader alone.
3. Decide the change:
   - Wording only, structure fine: rewrite directly.
   - Structure changes (sections added, removed, merged, or reordered): show
     the user a short outline first - what each section answers and its rough
     size - with one or two sentences on why the current shape is hard to
     read. Wait for agreement unless the user already approved the structure
     or the change.
4. Rewrite whole sections, not sentence patches. Keep every fact, rule,
   number, and example the reader needs. Use real names (tables, columns,
   values, commands) and small examples instead of abstract description.
   Where a flow is hard to follow, tell it once as the reader's task - who
   starts with what input, what happens, what result they see - rather than
   prefacing every section with a story.
5. Move, do not silently drop, content meant for another reader:
   - a decided rule into the current text of its owner (Brief, Spec,
     Architecture, or Map) when that document is in scope, otherwise report
     where it belongs; no separate decision log or history;
   - agent instructions to `AGENTS.md` or its routed guidance, and environment
     records to wherever the project's guidance routes them;
   - a nonblocking future improvement to a backlog the project already uses
     for it, following that backlog's policy; never read or write a backlog
     its policy reserves for explicit user requests;
   - an unanswered question that blocks a current claim to the owner's open
     questions section when its Skill defines one, and raise it with the user.
   With no owner, keep one short open-items list at the end of the page.
   Check results go in your report, not the page.
6. Reread the result as the reader. Fix anything that still stalls. Check
   changed links and anchors. For HTML, also open the rendered page and check
   legibility, navigation, and diagram labels. That rendered check and the
   read-through are separate, and neither proves a person understood it.

## Flexibility

The reader's need wins over any reference shape. Add a section a scenario
needs, drop one it does not, and say why when you propose the outline.

When a document reveals a failure or a document type the references do not
cover, finish the document, then propose the new example to the user. Edit
this Skill's references only when the user asks. Keep each reference to a few
of the clearest pairs; a new pair should replace a weaker one.

## Boundaries

- Do not change meaning: decisions, requirements, statuses, and numbers stay
  as written. Report a contradiction instead of resolving it.
- Do not invent missing content. Leave a gap visible as an open item.
- Preserve unrelated user changes.

## Report

Per document: the reader, the resulting structure in one line, size before
and after in the unit you measured (say what was not measured, such as HTML
reader text), and where moved content went. Lead with anything the user
must decide.
