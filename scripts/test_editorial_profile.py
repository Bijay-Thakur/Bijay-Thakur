import unittest
from datetime import date, timedelta, timezone, datetime
from pathlib import Path
import tempfile
import editorial_profile as ep


def example():
    today = date(2026, 11, 27)
    start = today - timedelta(days=364)
    days = [{'date': (start + timedelta(days=i)).isoformat(), 'contributionCount': (1 if i%11 == 0 else 0)} for i in range(365)]
    return {'days': days, 'total': sum(x['contributionCount'] for x in days),
            'repos': [{'stargazers_count': 1, 'forks_count': 2}, {'stargazers_count': 0, 'forks_count': 0}]}


class EditorialActivityTests(unittest.TestCase):
    def test_verified_svg_uses_actual_data(self):
        data = example()
        svg = ep.build_svg(data, datetime(2026, 11, 27, tzinfo=timezone.utc))
        self.assertIn('My year in code', svg)
        self.assertIn('34 contributions', svg)
        self.assertIn('Updated 2026-11-27', svg)
        self.assertNotIn('Your year in code', svg)
        self.assertEqual(svg.count('<rect'), 366)  # 365 contribution days + background

    def test_metric_counts(self):
        text = ep.metrics_markdown(example())
        self.assertIn('34', text)
        self.assertIn('2** public repositories', text)
        self.assertIn('1** stars received', text)
        self.assertIn('2** forks', text)

    def test_bad_totals_fail_closed(self):
        data = example()
        data['total'] = 1000
        with self.assertRaises(ValueError):
            ep.build_svg(data)

    def test_duplicate_day_rejected(self):
        data = example()
        data['days'].append(data['days'][-1])
        with self.assertRaises(ValueError):
            ep.build_svg(data)

    def test_date_range_rejected(self):
        data = example()
        data['days'] = data['days'][:10]
        with self.assertRaises(ValueError):
            ep.build_svg(data)

    def test_readme_changes_only_marked_span(self):
        with tempfile.TemporaryDirectory() as temp:
            original = ep.README
            try:
                ep.README = Path(temp)/'README.md'
                ep.README.write_text('HEADER\n'+ep.START+'\nold\n'+ep.END+'\nFOOTER')
                self.assertTrue(ep.update_readme(example()))
                s = ep.README.read_text()
                self.assertTrue(s.startswith('HEADER\n'))
                self.assertTrue(s.endswith('\nFOOTER'))
                self.assertNotIn('old', s)
                self.assertFalse(ep.update_readme(example()))
            finally:
                ep.README = original


if __name__ == '__main__':
    unittest.main()