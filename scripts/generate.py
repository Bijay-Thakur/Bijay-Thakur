#!/usr/bin/env python3
"""Render refreshed illustrated GitHub profile from authenticated GitHub API data.

Run from a GitHub Actions runner with GH_TOKEN/GITHUB_TOKEN.
No fake numerical defaults: API failure stops the workflow and preserves
the last successful chart images in the repository.
"""
import sys
from github_data import get_data, PROJECTS
from studio_art import render_all

if __name__ == "__main__":
    if "--placeholders" in sys.argv:
        render_all(None, PROJECTS)
        print("Wrote deliberately unpopulated chart placeholders")
    else:
        data = get_data()
        assert len(data["days"]) > 300, "Contribution calendar missing recent days"
        assert len(data["chosen"]) == len(PROJECTS), "Repository metadata mismatch"
        render_all(data, PROJECTS)
        print(f"Rendered {data['total']:,} contributions, {len(data['repos'])} public repos")
