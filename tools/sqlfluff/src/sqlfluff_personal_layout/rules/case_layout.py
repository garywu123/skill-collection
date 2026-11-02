"""Format CASE expressions through whitespace-only parse-tree edits.

Inputs: SQLFluff's parsed T-SQL and configured line width/indent size.
Output: Whitespace fixes; identifiers, literals, comments and SQL order stay intact.
Limits: CASE containing comments or SELECT is left to native layout rules.
"""

import re

from sqlfluff.core.parser import NewlineSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.crawlers import RootOnlyCrawler


def code_leaves(segment):
    """Return non-meta SQL tokens, including comments as preservation barriers."""
    return [s for s in segment.raw_segments if not s.is_meta and not s.is_whitespace]


def supported(case):
    """Avoid guessing layout around comments and multiline subqueries."""
    return not any(s.is_comment for s in case.raw_segments) and not any(
        case.recursive_crawl("select_statement")
    )


def inline_text(segment):
    """Collapse whitespace between tokens without inspecting literal contents."""
    parts = []
    pending = False
    for token in segment.raw_segments:
        if token.is_meta:
            continue
        if token.is_whitespace:
            pending = True
        else:
            if pending and parts:
                parts.append(" ")
            parts.append(token.raw)
            pending = False
    return "".join(parts)


def layout_plan(root, config):
    """Return requested token gaps and lines owned by CASE indentation.

    Example: a long SET x = CASE puts CASE below x, with WHEN one level deeper.
    Only CASE boundaries and existing whitespace are edited.
    """
    raw = root.raw
    width = config.get("max_line_length")
    size = config.get("tab_space_size", section="indentation")
    leaves = [s for s in root.raw_segments if not s.is_meta]
    code = code_leaves(root)
    indexes = {s.uuid: i for i, s in enumerate(code)}
    # Fix passes retain original source markers; derive offsets from the current tree.
    spans = {}
    offset = 0
    for leaf in leaves:
        spans[leaf.uuid] = (offset, offset + len(leaf.raw))
        offset += len(leaf.raw)
    gaps = {}
    protected = set()

    def line_indent(position):
        start = raw.rfind("\n", 0, position) + 1
        return len(re.match(r"[ \t]*", raw[start:]).group().expandtabs(size))

    def before(token, gap):
        gaps[token.uuid] = (token, gap)

    def visit(case, parent_indent=None):
        if not supported(case):
            return
        tokens = code_leaves(case)
        first, last = tokens[0], tokens[-1]
        start = spans[first.uuid][0]
        end = spans[last.uuid][1]
        first_index = indexes[first.uuid]
        previous = code[first_index - 1] if first_index else None
        assignment = (
            parent_indent is None and previous is not None and previous.raw == "="
            and any(step.segment.is_type('set_clause', 'select_clause_element')
                    for step in root.path_to(case))
        )
        indent = line_indent(start) if parent_indent is None else parent_indent
        if assignment:
            indent = line_indent(spans[previous.uuid][0])
            before(previous, " ")
        text = inline_text(case)
        line_start = raw.rfind("\n", 0, start) + 1
        line_end = raw.find("\n", end)
        suffix = raw[end:line_end if line_end >= 0 else len(raw)]
        prefix = raw[line_start:start]
        # A multiline prefix belongs to an already-expanded assignment.
        if assignment:
            operator_end = spans[previous.uuid][1]
            operator_start = raw.rfind("\n", 0, operator_end) + 1
            prefix = raw[operator_start:operator_end] + " "
        if parent_indent is not None:
            prefix = " " * indent
        fits = len(prefix.expandtabs(size)) + len(text) + len(suffix) <= width
        is_nested = parent_indent is not None
        multiline = not fits or ("\n" in case.raw and not is_nested)
        case_indent = indent + size if assignment else indent
        select_inline = (
            not assignment and not is_nested
            and previous is not None and previous.raw_upper in ('SELECT', 'DISTINCT')
            and previous.pos_marker.working_line_no == first.pos_marker.working_line_no
        )
        if multiline and select_inline:
            case_indent += size
        if not multiline:
            for left, right in zip(tokens, tokens[1:]):
                gap = raw[spans[left.uuid][1]:spans[right.uuid][0]]
                if "\n" in gap:
                    before(right, " ")
            if assignment:
                before(first, " ")
        else:
            if assignment:
                before(first, "\n" + " " * case_indent)
            elif is_nested or select_inline:
                before(first, "\n" + " " * case_indent)
            for child in case.segments:
                if child.is_type("when_clause", "else_clause"):
                    clause_tokens = code_leaves(child)
                    before(clause_tokens[0], "\n" + " " * (case_indent + size))
                    nested = list(child.recursive_crawl("case_expression", recurse_into=False))
                    for inner in nested:
                        visit(inner, case_indent + 2 * size)
                    # Collapse native WHEN/THEN breaks when the branch fits.
                    if not nested and len(inline_text(child)) + case_indent + size <= width:
                        for left, right in zip(clause_tokens, clause_tokens[1:]):
                            gap = raw[spans[left.uuid][1]:spans[right.uuid][0]]
                            if "\n" in gap:
                                before(right, " ")
            before(last, "\n" + " " * case_indent)
        first_line = previous.pos_marker.working_line_no if assignment else first.pos_marker.working_line_no
        protected.update(range(first_line, last.pos_marker.working_line_no + 1))

    for case in root.recursive_crawl("case_expression", recurse_into=False):
        visit(case)
    return gaps, protected, leaves


class Rule_Case_C001(BaseRule):
    """Keep short CASE inline and expand long CASE into a readable block."""

    name = "personal.case_layout"
    groups = ("all",)
    crawl_behaviour = RootOnlyCrawler()
    is_fix_compatible = True
    # Run before native LT05 so it evaluates the reformatted line, not stale width.
    lint_phase = "main"

    def _eval(self, context):
        """Apply planned gaps using parsed whitespace anchors only."""
        gaps, _, leaves = layout_plan(context.segment, context.config)
        positions = {s.uuid: i for i, s in enumerate(leaves)}
        results = []
        for token, desired in gaps.values():
            index = positions[token.uuid]
            start = index
            while start > 0 and leaves[start - 1].is_whitespace:
                start -= 1
            existing = leaves[start:index]
            if "".join(s.raw for s in existing) == desired:
                continue
            replacement = []
            if desired.startswith("\n"):
                replacement.append(NewlineSegment())
                if desired[1:]:
                    replacement.append(WhitespaceSegment(raw=desired[1:]))
            elif desired:
                replacement.append(WhitespaceSegment(raw=desired))
            if existing:
                fixes = [LintFix.replace(existing[0], replacement)]
                fixes.extend(LintFix.delete(s) for s in existing[1:])
            else:
                fixes = [LintFix.create_before(token, replacement)]
            results.append(LintResult(anchor=token, fixes=fixes))
        return results
