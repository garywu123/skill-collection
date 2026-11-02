"""Keep native operator layout except for assignments directly to managed CASE.

The CASE rule owns the equals sign of those assignments. Other assignments and
comparison/binary operators retain the existing SQLFluff behavior.
"""

from sqlfluff.rules.layout.LT03 import Rule_LT03

from sqlfluff_personal_layout.rules.case_layout import code_leaves, supported


class Rule_Case_L003(Rule_LT03):
    """Apply native operator layout outside direct CASE assignments."""

    name = "personal.operators"
    aliases = ()

    def _eval(self, context):
        """Let CASE layout keep its assignment equals sign on the preceding line."""
        if context.segment.is_type('assignment_operator') and context.parent_stack:
            parent = context.parent_stack[-1]
            tokens = code_leaves(parent)
            index = next(i for i, token in enumerate(tokens)
                         if token.uuid == code_leaves(context.segment)[0].uuid)
            cases = list(parent.recursive_crawl('case_expression', recurse_into=False))
            if cases and supported(cases[0]) and index + 1 < len(tokens):
                if tokens[index + 1].uuid == code_leaves(cases[0])[0].uuid:
                    return None
        return super()._eval(context)
