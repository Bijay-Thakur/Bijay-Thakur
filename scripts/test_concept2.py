"""Offline assertions for the GitHub-data-driven painted contribution garden."""
from __future__ import annotations
import hashlib
import tempfile
import unittest
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
from unittest.mock import patch
from PIL import Image

from render_concept2 import render_garden, _calendar_columns


class ConceptTwoGardenTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'garden.png'
        # In workflow, repository includes the committed illustrative background.
        self.assertTrue((Path(__file__).resolve().parents[1] / 'assets' / 'garden-scene.jpg').is_file())

    def tearDown(self):
        self.temp.cleanup()

    def test_pending_output_is_valid_image(self):
        render_garden(None, target=self.path)
        with Image.open(self.path) as img:
            self.assertEqual(img.size, (1500, 354))
            self.assertEqual(img.format, 'PNG')

    def test_calendar_day_positions(self):
        start = date(2026, 11, 15)  # Sunday
        data = [{'date': (start + timedelta(days=i)).isoformat(), 'contributionCount': i}
                for i in range(7)]
        cols = _calendar_columns(data)
        self.assertEqual(len(cols), 1)
        self.assertEqual(cols[0][1][0], 0)
        self.assertEqual(cols[0][1][6], 6)

    def test_calendar_rejects_negative_values(self):
        with self.assertRaises(ValueError):
            _calendar_columns([{'date': '2026-11-16', 'contributionCount': -2}])

    def test_actual_values_change_rendered_output(self):
        start = date(2025, 11, 16)
        days = [{'date': (start + timedelta(days=i)).isoformat(), 'contributionCount': 0}
                for i in range(366)]
        now = datetime(2026, 11, 16, 21, 0, tzinfo=timezone.utc)
        render_garden({'days': days, 'total': 0}, target=self.path, refreshed_at=now)
        zero_digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        days[-1]['contributionCount'] = 3
        render_garden({'days': days, 'total': 3}, target=self.path, refreshed_at=now)
        one_digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.assertNotEqual(zero_digest, one_digest)

    def test_missing_verified_data_fails(self):
        with self.assertRaises(ValueError):
            render_garden({'days': []}, target=self.path)


if __name__ == '__main__':
    unittest.main()