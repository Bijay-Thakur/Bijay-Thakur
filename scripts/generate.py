#!/usr/bin/env python3
"""Render refreshed illustrated GitHub profile from authenticated GitHub API data.

Run from a GitHub Actions runner with GH_TOKEN/GITHUB_TOKEN.
No fake numerical defaults: API failure stops the workflow and preserves
the last successful chart images in the repository.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path
from github_data import get_data, PROJECTS
from studio_art import render_all
from render_painted_cards import draw_all
from star_attribution import update_readme_star_sources
from render_concept2 import render_garden

if __name__ == "__main__":
    if "--placeholders" in sys.argv:
        render_all(None, PROJECTS)
        render_garden(None)
        draw_all(PROJECTS, None)
        print("Wrote deliberately unpopulated chart placeholders")
    else:
        data = get_data()
        assert len(data["days"]) > 300, "Contribution calendar missing recent days"
        assert len(data["chosen"]) == len(PROJECTS), "Repository metadata mismatch"
        render_all(data, PROJECTS)
        render_garden(data, refreshed_at=datetime.now(timezone.utc))
        draw_all(PROJECTS, data)
        update_readme_star_sources(data)
        # Timestamp the last successful data retrieval, not an assumed update cadence.
        garden = Path(__file__).resolve().parents[1] / "assets" / "contributions.svg"
        chart = garden.read_text(encoding="utf-8")
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        chart = chart.replace("updated every 30 min", f"last refreshed {stamp}")
        garden.write_text(chart, encoding="utf-8")
        print(f"Rendered {data['total']:,} contributions, {len(data['repos'])} public repos")
