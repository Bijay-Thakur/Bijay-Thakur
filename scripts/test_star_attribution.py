"""Local offline tests for public-star provenance. No GitHub network needed."""
import unittest
from star_attribution import replace_star_block, star_sources_markdown, START, END


def repo(name, stars):
    return {"name": name, "owner": {"login": "Bijay-Thakur"},
            "html_url": "https://github.com/Bijay-Thakur/" + name,
            "stargazers_count": stars}


class PublicStarSourcesTest(unittest.TestCase):
    def test_verified_one_star_and_zero_star_repositories(self):
        data = {"repos": [repo("SEC-Insight", 0), repo("StoreSense", 1)]}
        result = star_sources_markdown(data)
        self.assertIn("StoreSense — 1 star", result)
        self.assertNotIn("SEC-Insight —", result)
        self.assertIn("stars received", result)

    def test_multiple_stars_sorted_by_count(self):
        data = {"repos": [repo("Project-B", 2), repo("Project-A", 5)]}
        result = star_sources_markdown(data)
        self.assertLess(result.index("Project-A — 5 stars"), result.index("Project-B — 2 stars"))

    def test_zero_star_case_has_no_fabricated_link(self):
        result = star_sources_markdown({"repos": [repo("Project-A", 0)]})
        self.assertIn("Public stars received: 0", result)
        self.assertNotIn('href=', result)

    def test_atomic_block_replacement_leaves_rest_unchanged(self):
        before = "Intro\n" + START + "\nold\n" + END + "\nFooter"
        after = replace_star_block(before, {"repos": [repo("StoreSense", 1)]})
        self.assertTrue(after.startswith("Intro\n"))
        self.assertTrue(after.endswith("\nFooter"))
        self.assertNotIn("\nold\n", after)

    def test_missing_markers_raise(self):
        with self.assertRaises(ValueError):
            replace_star_block("No markers", {"repos": []})


if __name__ == "__main__":
    unittest.main()
