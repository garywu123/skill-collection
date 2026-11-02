"""Check CASE layout, token preservation and formatting stability without a database."""

from pathlib import Path
import subprocess
import sys
import unittest

from sqlfluff.core import FluffConfig, Linter


ROOT = Path(__file__).resolve().parents[1]


class CaseLayoutTests(unittest.TestCase):
    """Exercise the complete configured rule set, including native rules."""

    def setUp(self):
        self.linter = Linter(
            config=FluffConfig.from_string((ROOT / '.sqlfluff').read_text()),
        )

    def format_sql(self, sql):
        """Require unchanged SQL tokens, no parse errors and a stable second fix."""
        before = self.linter.parse_string(sql)
        self.assertFalse(before.violations)
        fixed, _ = self.linter.lint_string(sql, fix=True).fix_string()
        after = self.linter.parse_string(fixed)
        self.assertFalse(after.violations)
        tokens = lambda tree: [
            (s.get_type(), s.raw) for s in tree.raw_segments
            if not s.is_whitespace and not s.is_meta
        ]
        self.assertEqual(tokens(before.tree), tokens(after.tree))
        again, _ = self.linter.lint_string(fixed, fix=True).fix_string()
        self.assertEqual(fixed, again)
        return fixed

    def test_long_update_places_case_under_equals(self):
        fixed = self.format_sql(
            'UPDATE #example\nSET\n'
            '    pick_completed_time_utc = CASE WHEN pick_completed_time_utc < '
            'pick_active_time_utc THEN NULL ELSE pick_completed_time_utc END;\n'
        )
        self.assertIn('pick_completed_time_utc =\n        CASE\n', fixed)
        self.assertIn('\n            ELSE pick_completed_time_utc\n        END;', fixed)
        self.assertFalse(self.linter.lint_string(fixed).violations)

    def test_select_equals_uses_the_same_continuation(self):
        fixed = self.format_sql(
            'SELECT\n    pick_completed_time_utc = CASE WHEN pick_completed_time_utc '
            '< pick_active_time_utc THEN NULL ELSE pick_completed_time_utc END\n'
            'FROM #example;\n'
        )
        self.assertIn('pick_completed_time_utc =\n        CASE\n', fixed)

    def test_short_cases_remain_inline(self):
        for case in ('CASE WHEN flag = 1 THEN value END',
                     'CASE WHEN flag = 1 THEN NULL ELSE value END'):
            with self.subTest(case=case):
                self.assertIn(case, self.format_sql(f'SELECT {case} AS result FROM #example;\n'))

    def test_short_nested_case_stays_on_one_line(self):
        sql = '''SELECT
    result =
        CASE
            WHEN use_actual = 1 THEN
                CASE WHEN completed_time_utc < active_time_utc THEN NULL ELSE completed_time_utc END
            ELSE estimated_time_utc
        END
FROM #example;
'''
        self.assertEqual(sql, self.format_sql(sql))

    def test_as_alias_is_preserved(self):
        fixed = self.format_sql(
            "SELECT CASE WHEN destination.milestone_role = 'drop' AND "
            'destination.location_resolved = 1 THEN destination.part_completed_utc '
            'END AS drop_completed_time_utc FROM #example AS destination;\n'
        )
        self.assertIn('END AS drop_completed_time_utc', fixed)
        self.assertIn('\n        WHEN', fixed)

    def test_ir_aggregate_and_function_cases_keep_tokens(self):
        self.format_sql('''SELECT
    MIN(CASE WHEN is_promotion_observation = 1 THEN recorded_time_utc END) AS promoted_time_utc,
    MIN(CASE WHEN is_cancellation_observation = 1 THEN recorded_time_utc END) AS canceled_time_utc,
    CONVERT(bit, CASE WHEN order_id IS NOT NULL THEN 1 ELSE 0 END) AS found_in_order_evidence
FROM #request_detail;
''')

    def test_literals_and_comments_remain_exact(self):
        self.format_sql("""SELECT
    CASE -- preserve this comment
        WHEN flag = 1 THEN N'CASE  WHEN  ELSE END'
        ELSE N'quoted '' value'
    END AS result,
    CASE WHEN flag = 1 THEN N'a  b' ELSE N'c' END AS label
FROM #example;
""")

    def test_subquery_case_is_preserved(self):
        self.format_sql('SELECT CASE WHEN EXISTS (SELECT 1 FROM #e) THEN 1 ELSE 0 END AS found;\n')

    def test_native_indent_still_fixes_non_case_lines(self):
        fixed = self.format_sql('SELECT\n  a,\n  b\nFROM #example;\n')
        self.assertIn('\n    a,\n    b\n', fixed)

    def test_leading_equals_is_moved_back_only_for_case(self):
        fixed = self.format_sql('''UPDATE #example
SET
    pick_completed_time_utc
    = CASE WHEN pick_completed_time_utc < pick_active_time_utc THEN NULL ELSE pick_completed_time_utc END;
''')
        self.assertIn('pick_completed_time_utc =\n        CASE', fixed)

    def test_native_operators_remain_enabled_for_other_assignments(self):
        fixed = self.format_sql('UPDATE #example\nSET\n    result =\n        other_value;\n')
        self.assertIn('= other_value', fixed)

    def test_exact_width_boundary_includes_indent_and_semicolon(self):
        for length in (100, 101):
            with self.subTest(length=length):
                head = '    result = CASE WHEN flag = 1 THEN '
                tail = ' END;'
                value = "'" + 'x' * (length - len(head) - len(tail) - 2) + "'"
                fixed = self.format_sql('UPDATE #example\nSET\n' + head + value + tail + '\n')
                self.assertEqual('result =\n' in fixed, length > 100)

    def test_vscode_stdin_returns_formatted_sql_and_success(self):
        result = subprocess.run(
            [sys.executable, '-m', 'sqlfluff', 'fix', '--config', str(ROOT / '.sqlfluff'),
             '--stdin-filename', 'example.sql', '-'],
            input=(ROOT / 'examples/case.before.sql').read_text(),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (ROOT / 'examples/case.after.sql').read_text())


if __name__ == '__main__':
    unittest.main()
