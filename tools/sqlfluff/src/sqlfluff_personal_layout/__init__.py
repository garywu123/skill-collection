"""Register personal SQL layout rules after SQLFluff loads its configuration."""

from sqlfluff.core.plugin import hookimpl


@hookimpl
def get_rules():
    """Load CASE layout and its native indentation compatibility rule."""
    from sqlfluff_personal_layout.rules.case_layout import Rule_Case_C001
    from sqlfluff_personal_layout.rules.indentation import Rule_Case_L002
    from sqlfluff_personal_layout.rules.operators import Rule_Case_L003

    return [Rule_Case_C001, Rule_Case_L002, Rule_Case_L003]
