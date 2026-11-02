"""Delegate ordinary indentation to LT02, leaving supported CASE lines to C001.

SQLFluff's T-SQL parser has no continuation indent after an assignment operator.
Native LT02 would therefore undo the agreed CASE-under-equals indentation.
"""

from sqlfluff.rules.layout.LT02 import Rule_LT02

from sqlfluff_personal_layout.rules.case_layout import layout_plan


class Rule_Case_L002(Rule_LT02):
    """Apply native indentation outside lines managed by personal CASE layout."""

    name = "personal.indent"
    aliases = ()

    def _eval(self, context):
        """Keep native results unless their edits touch a managed CASE line."""
        _, protected, _ = layout_plan(context.segment, context.config)
        results = super()._eval(context)
        return [
            result for result in results
            if not any(
                line in protected
                for fix in result.fixes
                if fix.anchor.pos_marker
                for line in range(
                    fix.anchor.pos_marker.working_line_no,
                    fix.anchor.pos_marker.working_line_no + fix.anchor.raw.count("\n") + 1,
                )
            )
        ]
