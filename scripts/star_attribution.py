"""Update public-star source links using verified repository API metadata.

This module never estimates stars: it reads `data["repos"]`, which is obtained
from the official GitHub REST API by github_data.get_data().
"""
from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import quote

README = Path(__file__).resolve().parents[1] / "README.md"
START = "<!-- STAR_PROVENANCE_START -->"
END = "<!-- STAR_PROVENANCE_END -->"


def star_sources_markdown(data: dict) -> str:
    if not isinstance(data.get("repos"), list):
        raise ValueError("Missing GitHub repository list; refusing to invent public stars")
    starred = []
    for repo in data["repos"]:
        count = int(repo.get("stargazers_count", 0))
        if count <= 0:
            continue
        name = repo.get("name", "")
        owner = (repo.get("owner") or {}).get("login", "")
        url = repo.get("html_url") or ""
        if not (name and owner and url.startswith(f"https://github.com/{owner}/")):
            raise ValueError("Starred repository lacks a trustworthy GitHub URL")
        starred.append((count, str(name), str(url)))
    starred.sort(key=lambda x: (-x[0], x[1].casefold()))
    total = sum(int(r.get("stargazers_count", 0)) for r in data["repos"])
    if total != sum(row[0] for row in starred):
        raise ValueError("Star source total does not match repository total")
    if not starred:
        detail = "<p align=\"center\"><strong>⭐ Public stars received: 0</strong> — no public repositories currently have a star.</p>"
    else:
        labels = []
        for count, name, url in starred:
            plural = "star" if count == 1 else "stars"
            labels.append(
                f'<a href="{escape(url, quote=True)}">{escape(name)} — {count} {plural}</a>'
            )
        detail = (
            '<p align="center"><strong>⭐ Where do the public stars come from?</strong> '
            + " · ".join(labels)
            + "<br /><sub>Verified GitHub public repositories. This is stars received, not repositories starred by me.</sub></p>"
        )
    return f"{START}\n{detail}\n{END}"


def replace_star_block(readme_text: str, data: dict) -> str:
    if readme_text.count(START) != 1 or readme_text.count(END) != 1:
        raise ValueError("Expected exactly one pair of star provenance markers")
    a = readme_text.index(START)
    b = readme_text.index(END)
    if b <= a:
        raise ValueError("Malformed star provenance block")
    return readme_text[:a] + star_sources_markdown(data) + readme_text[b+len(END):]


def update_readme_star_sources(data: dict) -> None:
    current = README.read_text(encoding="utf-8")
    updated = replace_star_block(current, data)
    if current != updated:
        README.write_text(updated, encoding="utf-8")
        print("Updated README with verified source links for received public stars")
