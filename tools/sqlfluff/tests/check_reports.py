"""Verify report formatting in memory; never execute SQL or write report files."""

from collections import Counter
from pathlib import Path
import sys

from sqlfluff.core import FluffConfig, Linter


def tokens(tree):
    """Include comments and literals verbatim while excluding layout/meta tokens."""
    return [(s.get_type(), s.raw) for s in tree.raw_segments
            if not s.is_whitespace and not s.is_meta]


def main():
    """Check supplied SQL paths against the bundled profile and installed plugin."""
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python tests/check_reports.py report.sql [another.sql ...]')
    profile = Path(__file__).resolve().parents[1] / '.sqlfluff'
    linter = Linter(config=FluffConfig.from_string(profile.read_text()))
    rule_codes = {rule.code for rule in linter.get_rulepack().rules}
    if not {'Case_C001', 'Case_L002', 'Case_L003'} <= rule_codes:
        raise SystemExit('Install sqlfluff-personal-layout in this Python environment first.')
    for filename in sys.argv[1:]:
        sql = Path(filename).read_text(encoding='utf-8-sig')
        before = linter.parse_string(sql)
        fixed, _ = linter.lint_string(sql, fix=True).fix_string()
        after = linter.parse_string(fixed)
        if before.violations or after.violations:
            raise SystemExit(f'{filename}: parse errors')
        if tokens(before.tree) != tokens(after.tree):
            raise SystemExit(f'{filename}: non-whitespace tokens changed')
        again, _ = linter.lint_string(fixed, fix=True).fix_string()
        if fixed != again:
            raise SystemExit(f'{filename}: formatting is not idempotent')
        remaining = Counter(v.rule_code() for v in linter.lint_string(fixed).violations)
        if any(code.startswith('Case_') for code in remaining):
            raise SystemExit(f'{filename}: custom-rule violations remain: {dict(remaining)}')
        print(f'{Path(filename).name}: tokens preserved; parses; stable; remaining={dict(remaining)}')


if __name__ == '__main__':
    main()
