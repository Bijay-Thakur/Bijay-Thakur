#!/usr/bin/env python3
"""Render cozy GitHub profile SVGs from official GitHub API data.

Run in GitHub Actions with GH_TOKEN (the built-in GITHUB_TOKEN works for
public GitHub information). No third-party Python packages are required.

For a fresh profile preview with no network/token, run --placeholders.
Placeholders never contain invented metric values.
"""
from __future__ import annotations

import calendar
from collections import Counter
from datetime import date, datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USER = os.getenv("GITHUB_LOGIN", "Bijay-Thakur")
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

COLORS = dict(
    ink="#553D31", sub="#917665", orange="#C3774E", peach="#F6D7BC",
    cream="#FFF9EE", paper="#FBF2E2", sage="#89AB77", moss="#4D7957",
    pale="#DFE8C7", gold="#E6B16E", blue="#8FAFC3", border="#E6D5BB",
)

PROJECTS = [
    dict(slug="rag-sec-10k", filename="project-sec.svg", name="SEC Insight AI",
         lines=("Cited Q&A over SEC filings", "Hybrid retrieval + evaluation"),
         tags=("RAG", "Financial AI"), theme="#D8AF72", art="sec"),
    dict(slug="RivalScope-AI", filename="project-rivalscope.svg", name="RivalScope AI",
         lines=("Source-grounded research", "LangGraph + live traces"),
         tags=("AI Agents", "Evidence"), theme="#A5BA90", art="rival"),
    dict(slug="GlitchVision---Visual-Anomaly-Detection-for-Game-QA",
         filename="project-glitchvision.svg", name="GlitchVision",
         lines=("Visual anomaly triage", "ResNet-18 + Isolation Forest"),
         tags=("Computer Vision", "Game QA"), theme="#A3B7CF", art="game"),
    dict(slug="Nova-Learn", filename="project-novalearn.svg", name="NovaLearn",
         lines=("AI-powered course workspace", "Assessments + learning evidence"),
         tags=("Education", "AI Product"), theme="#DAB2BC", art="learn"),
    dict(slug="PACT---Protocol-for-Agentic-Commit-Transactions", filename="project-pact.svg", name="PACT",
         lines=("Agent transaction safeguards", "Commit checks + recovery"),
         tags=("Ongoing", "Agent Systems"), theme="#DFC4A4", art="pact"),
]

CONTRIBUTIONS_QUERY = """
query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def _request(url: str, payload: dict | None = None):
    if not TOKEN:
        raise RuntimeError("GH_TOKEN not set. GitHub Actions supplies secrets.GITHUB_TOKEN.")
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "bijay-cozy-studio-profile",
    }
    body = json.dumps(payload).encode() if payload is not None else None
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, headers=headers, data=body)
    try:
        with urlopen(req, timeout=25) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"GitHub API HTTP {exc.code} for {url}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach GitHub API for {url}: {exc}") from exc


def get_data():
    graph = _request("https://api.github.com/graphql", {
        "query": CONTRIBUTIONS_QUERY, "variables": {"login": USER},
    })
    if graph.get("errors"):
        raise RuntimeError(f"GitHub GraphQL errors: {graph['errors']}")
    profile = (graph.get("data") or {}).get("user")
    if not profile:
        raise RuntimeError(f"GitHub user {USER!r} was not found")
    contribution = profile["contributionsCollection"]["contributionCalendar"]
    days = [day for week in contribution["weeks"] for day in week["contributionDays"]]

    repositories = []
    page = 1
    while True:
        part = _request(f"https://api.github.com/users/{quote(USER)}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(part, list):
            raise RuntimeError("Unexpected repo listing response")
        repositories.extend(r for r in part if not r.get("private", False) and r.get("owner", {}).get("login", "").lower() == USER.lower())
        if len(part) < 100:
            break
        page += 1
        if page > 20:
            raise RuntimeError("Repo pagination limit exceeded")

    chosen = {}
    langs = Counter()
    for project in PROJECTS:
        slug = project["slug"]
        api_repo = _request(f"https://api.github.com/repos/{quote(USER)}/{quote(slug)}")
        if api_repo.get("private") or api_repo.get("full_name", "").lower() != f"{USER}/{slug}".lower():
            raise RuntimeError(f"Cannot verify public repo {slug}")
        chosen[slug] = api_repo
        for language, size in _request(f"https://api.github.com/repos/{quote(USER)}/{quote(slug)}/languages").items():
            langs[language] += int(size)

    return {
        "total": int(contribution["totalContributions"]),
        "days": days,
        "repos": repositories,
        "chosen": chosen,
        "languages": langs,
    }


def svg_start(w, h, body, name):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(name, quote=True)}">
<defs>
 <linearGradient id="cream" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFF9EF"/><stop offset="1" stop-color="#F5E8D6"/></linearGradient>
 <linearGradient id="meadow" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#B7D195"/><stop offset="1" stop-color="#51845B"/></linearGradient>
 <linearGradient id="sun" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F3D88C"/><stop offset="1" stop-color="#D68E5E"/></linearGradient>
 <linearGradient id="land" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#D9E1B7" stop-opacity=".75"/><stop offset="1" stop-color="#6A936A" stop-opacity=".4"/></linearGradient>
</defs>
{body}
</svg>'''


def txt(x, y, value, size=24, color=None, weight=500, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" fill="{color or COLORS["ink"]}" font-size="{size}" font-weight="{weight}" font-family="Trebuchet MS,Segoe UI,Verdana,sans-serif" {extra}>{escape(str(value))}</text>'


def panel(w, h, fill="url(#cream)"):
    return f'<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="25" fill="{fill}" stroke="{COLORS["border"]}" stroke-width="3" />'


def leaf(x, y, scale=1, color="#749C64"):
    return f'<g transform="translate({x} {y}) scale({scale})"><path d="M0 26 C-8 5 -8 -5 0 -20" stroke="#79915C" fill="none" stroke-width="3"/><ellipse cx="-13" cy="-8" rx="14" ry="7" transform="rotate(30 -13 -8)" fill="{color}"/><ellipse cx="12" cy="-18" rx="16" ry="8" transform="rotate(-32 12 -18)" fill="{color}"/></g>'


def pending(w, h, heading):
    body = panel(w, h) + leaf(40, 72, 0.8) + txt(86, 80, heading, 32, weight=800)
    body += txt(w // 2, h // 2 + 12, "GitHub data loads after the first Actions run", 24, COLORS["sub"], 600, text_anchor="middle")
    body += txt(w // 2, h // 2 + 48, "No sample numbers are displayed.", 18, COLORS["sub"], 400, text_anchor="middle")
    return svg_start(w, h, body, heading)


def nice(n):
    return f"{n:,}"


def overview(data):
    w, h = 880, 448
    if data is None:
        return pending(w, h, "The studio at a glance")
    r = data["repos"]
    vals = [
        (nice(data["total"]), "CONTRIBUTIONS", "GitHub's rolling year"),
        (nice(len(r)), "PUBLIC REPOS", "Owned public repositories"),
        (nice(sum(int(x.get("stargazers_count", 0)) for x in r)), "PUBLIC STARS", "Across owned public repos"),
        (nice(len(PROJECTS)), "FEATURED WORK", "Verified public projects"),
    ]
    body = panel(w, h) + txt(32, 47, "The studio at a glance", 31, weight=800)
    for i, (value, title, subtitle) in enumerate(vals):
        x = 28 + (i % 2) * 432
        y = 70 + (i // 2) * 180
        body += f'<rect x="{x}" y="{y}" width="414" height="168" rx="19" fill="{["#FBE6D1", "#EDF1D9", "#F6E6D3", "#E1EBDD"][i]}" opacity=".92" />'
        body += txt(x + 24, y + 68, value, 52, COLORS["ink"], 800)
        body += txt(x + 24, y + 103, title, 21, COLORS["moss"], 800, letter_spacing=".6")
        body += txt(x + 24, y + 136, subtitle, 20, COLORS["sub"])
    return svg_start(w, h, body, "Real GitHub account metrics")


def contribution_graph(data):
    w, h = 755, 352
    if data is None:
        return pending(w, h, "Contribution garden")
    days = data["days"]
    if not days:
        raise RuntimeError("Missing contributions")
    by_date = {d["date"]: int(d["contributionCount"]) for d in days}
    first = date.fromisoformat(days[0]["date"])
    # First contribution week starts on Sunday; GitHub supplies weeks by date.
    # Build grid using GraphQL week ordering: 7 rows per week, Sunday first.
    # GitHub calendar week typically includes partial start and end weeks.
    weeks = []
    column = []
    for index, d in enumerate(days):
        day = date.fromisoformat(d["date"])
        if day.weekday() == 6 and column:
            weeks.append(column)
            column = []
        column.append(((day.weekday() + 1) % 7, int(d["contributionCount"]), d["date"]))
    if column:
        weeks.append(column)
    max_count = max(int(d["contributionCount"]) for d in days) or 1
    body = panel(w, h) + txt(31, 43, "Contribution garden", 27, weight=800)
    body += txt(725, 43, f"{nice(data['total'])} contributions", 17, COLORS["moss"], 800, text_anchor="end")
    body += txt(31, 66, "Actual daily contributions • rolling year", 15, COLORS["sub"])
    grid_x, grid_y = 37, 100
    spacing = min(12.2, 680 / max(len(weeks), 1))
    size = spacing - 2.2
    palette = ["#EEE7D9", "#D5E4BA", "#AFCF91", "#7CAC70", "#478359", "#2E6049"]
    for ix, week in enumerate(weeks):
        for weekday, count, when in week:
            bucket = 0 if count == 0 else min(5, 1 + int((count / max_count) * 4))
            x, y = grid_x + ix * spacing, grid_y + weekday * 17
            body += f'<rect x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="12" rx="3" fill="{palette[bucket]}" />'
    body += f'<path d="M0 291 Q130 274 250 290 Q400 265 560 288 Q670 270 755 286 V352 H0Z" fill="#E5EECF" />'
    for x, s, c in [(45,1.2,"#719C69"),(111,.8,"#A6C189"),(635,1.0,"#719C69"),(712,.8,"#B0C894")]:
        body += leaf(x, 311, s, c)
    body += txt(379, 328, "Each square is one real day from GitHub", 17, COLORS["sub"], 500, text_anchor="middle")
    return svg_start(w, h, body, "GitHub contribution garden")


def month_pairs(today):
    result = []
    for delta in range(11, -1, -1):
        ordinal = today.year * 12 + today.month - 1 - delta
        y, m = divmod(ordinal, 12)
        result.append((y, m + 1))
    return result


def activity_graph(data):
    w, h = 755, 352
    if data is None:
        return pending(w, h, "A year in motion")
    counts = Counter()
    for day in data["days"]:
        y, m = map(int, day["date"][:7].split("-"))
        counts[(y, m)] += int(day["contributionCount"])
    months = month_pairs(datetime.now(timezone.utc).date())
    values = [counts[m] for m in months]
    ymax = max(5, max(values) * 1.16)
    body = panel(w, h) + txt(31, 43, "A year in motion", 27, weight=800)
    body += txt(31, 66, "Monthly contribution counts • GitHub API", 15, COLORS["sub"])
    coords = [(58 + i * (640 / 11), 255 - 145 * n / ymax) for i, n in enumerate(values)]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = f"M{coords[0][0]:.1f} 260 L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in coords) + f" L{coords[-1][0]:.1f} 260 Z"
    body += '<path d="M2 283 Q130 250 263 286 Q400 242 547 280 Q658 246 754 283 V351 H2Z" fill="#DDE7BF" opacity=".6"/>'
    for y in [130, 193, 255]:
        body += f'<path d="M48 {y} H706" stroke="#D7D3BC" stroke-dasharray="3 8" stroke-width="1.6" />'
    body += f'<path d="{area}" fill="url(#land)"/>'
    body += f'<polyline points="{pts}" fill="none" stroke="{COLORS["moss"]}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
    for x, y in coords:
        body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.8" fill="#F7C67A" stroke="#6D8C5A" stroke-width="2"/>'
    for i, (y, m) in enumerate(months):
        body += txt(58 + i * (640 / 11), 300, calendar.month_abbr[m], 14, COLORS["sub"], 500, text_anchor="middle")
    body += txt(370, 334, "Current month is partial", 14, COLORS["sub"], text_anchor="middle")
    return svg_start(w, h, body, "Monthly GitHub contributions")


def language_graph(data):
    w, h = 1500, 250
    if data is None:
        return pending(w, h, "Languages behind the scenes")
    values = data["languages"].most_common(6)
    other = sum(data["languages"].values()) - sum(v for _, v in values)
    if other:
        values.append(("Other", other))
    total = sum(v for _, v in values)
    body = panel(w, h) + txt(40, 54, "Languages behind the scenes", 31, weight=800)
    body += txt(40, 84, "GitHub language bytes across five featured public repositories — not skill ratings", 19, COLORS["sub"])
    palette = ["#C77953", "#7EAC82", "#E2B46F", "#8BA7BC", "#AF95AF", "#D2AA83", "#B0B1AA"]
    if total == 0:
        body += txt(40, 166, "No language data reported for the selected repositories", 22)
    else:
        x, y, barw = 40, 117, 1418
        body += f'<rect x="{x}" y="{y}" width="{barw}" height="34" rx="12" fill="#E5DEC9" />'
        accumulated = 0
        for index, (lang, bytes_) in enumerate(values):
            segment = barw * bytes_ / total
            body += f'<rect x="{x+accumulated:.2f}" y="{y}" width="{segment:.2f}" height="34" fill="{palette[index]}" />'
            accumulated += segment
        start = 42
        for index, (lang, bytes_) in enumerate(values):
            share = bytes_ * 100 / total
            body += f'<circle cx="{start+8}" cy="195" r="7" fill="{palette[index]}"/>'
            body += txt(start + 22, 201, f"{lang}: {share:.1f}%", 19, weight=600)
            start += max(130, min(255, 30 + len(lang) * 10 + 95))
    return svg_start(w, h, body, "GitHub featured repository language breakdown")


def art(kind, theme):
    """Decorative engineering-themed vectors, not photographs or synthetic metrics."""
    g = f'<rect x="0" y="0" width="258" height="282" rx="24" fill="{theme}" opacity=".6" />'
    g += '<circle cx="198" cy="47" r="51" fill="#FFF2D1" opacity=".85"/>'
    g += '<path d="M0 205 Q80 150 152 211 Q213 165 258 211 V285 H0Z" fill="#739B7F" opacity=".5"/>'
    if kind == "sec":
        g += '<path d="M28 97 L130 43 L230 97Z" fill="#F9EBD9" stroke="#916D4A" stroke-width="4"/>'
        g += '<rect x="35" y="99" width="190" height="12" rx="3" fill="#775D53"/>'
        for x in [51, 90, 129, 168, 207]:
            g += f'<rect x="{x}" y="112" width="18" height="96" rx="2" fill="#FCE9CF" stroke="#B09A7A" stroke-width="2"/>'
        g += '<rect x="28" y="207" width="202" height="16" rx="5" fill="#765E51"/>'
        g += '<rect x="87" y="154" width="116" height="90" rx="6" fill="#FFF9E9" stroke="#B99067" stroke-width="3" transform="rotate(-10 87 154)"/>'
        g += txt(125, 192, "10-K", 25, "#8D6449", 800, text_anchor="middle", transform="rotate(-10 125 192)")
    elif kind == "rival":
        g += '<rect x="31" y="85" width="204" height="140" rx="15" fill="#FFF8E8" stroke="#9DAB80" stroke-width="4"/>'
        g += '<polyline points="49,196 90,162 128,174 169,116 215,137" stroke="#C17B51" stroke-width="8" stroke-linejoin="round" fill="none" />'
        g += '<circle cx="116" cy="137" r="41" fill="#E9F4E8" fill-opacity=".65" stroke="#445A53" stroke-width="13"/>'
        g += '<path d="M148 168 L207 226" stroke="#445A53" stroke-width="19" stroke-linecap="round"/>'
    elif kind == "game":
        g += '<rect x="27" y="73" width="207" height="142" rx="18" fill="#4C5770" stroke="#F6E7D5" stroke-width="6" />'
        g += '<rect x="44" y="89" width="174" height="100" rx="6" fill="#C3E1D9"/>'
        g += '<path d="M44 170 L83 129 L116 148 L162 104 L218 154 V190 H44Z" fill="#86AF91"/>'
        g += '<path d="M127 115 L139 151 L159 137" fill="none" stroke="#C86C52" stroke-width="7" stroke-linecap="round"/>'
        g += '<rect x="95" y="199" width="70" height="40" rx="20" fill="#FFF8E8" stroke="#5E7180" stroke-width="5"/>'
        g += '<path d="M111 219 H130 M121 209 V229" stroke="#5E7180" stroke-width="4"/>'
        g += '<circle cx="148" cy="214" r="4" fill="#C67B61"/><circle cx="155" cy="224" r="4" fill="#739E78"/>'
    elif kind == "pact":
        g += '<rect x="28" y="88" width="204" height="148" rx="22" fill="#FFF8E8" stroke="#947457" stroke-width="5"/>'
        for x, t in [(64,"A"),(128,"B"),(192,"C")]:
            g += f'<circle cx="{x}" cy="125" r="23" fill="#DDAE7A" stroke="#8C6A53" stroke-width="3"/>'
            g += txt(x, 133, t, 23, "#513B32", 800, text_anchor="middle")
        g += '<path d="M64 150 V175 H192 V150 M128 150 V194" stroke="#6F8F71" stroke-width="7" fill="none" stroke-linecap="round"/>'
        g += '<path d="M113 198 L124 209 L148 184" stroke="#6A976C" stroke-width="8" fill="none" stroke-linecap="round"/>'
    else:
        g += '<path d="M32 111 Q83 79 129 117 Q175 83 224 108 V228 Q175 206 129 238 Q82 203 32 229Z" fill="#FFF5DC" stroke="#A78982" stroke-width="5" />'
        g += '<path d="M129 117 V238" stroke="#A78982" stroke-width="4"/>'
        g += '<circle cx="129" cy="69" r="30" fill="#FFE4A1" stroke="#D1A57E" stroke-width="4"/>'
        g += '<path d="M122 69 L128 76 L141 59" fill="none" stroke="#698F6A" stroke-width="7" stroke-linecap="round"/>'
        for x in [57, 157]:
            for i in range(3):
                g += f'<path d="M{x} {145+i*20} h48" stroke="#D5C4B0" stroke-width="3"/>'
    return g


def project_card(project, repo):
    w, h = 720, 282
    if repo is None:
        stats = "Real stats appear after the first update"
    else:
        stats = f"{int(repo.get('stargazers_count', 0))} stars  ·  {int(repo.get('forks_count', 0))} forks"
    body = panel(w, h) + art(project["art"], project["theme"])
    body += txt(281, 66, project["name"], 33, COLORS["ink"], 800)
    body += txt(281, 103, project["lines"][0], 22, COLORS["ink"], 500)
    body += txt(281, 133, project["lines"][1], 22, COLORS["sub"], 500)
    for i, tag in enumerate(project["tags"]):
        x = 282 + i * 186
        body += f'<rect x="{x}" y="157" width="176" height="35" rx="17" fill="{COLORS["pale"] if i == 0 else COLORS["peach"]}" />'
        body += txt(x+88, 181, tag, 17, COLORS["ink"], 700, text_anchor="middle")
    body += f'<path d="M282 211 H680" stroke="{COLORS["border"]}" stroke-width="2" />'
    body += txt(282, 244, stats, 19, COLORS["moss"], 700)
    body += txt(282, 264, "Open the real repository", 14, COLORS["sub"], 500)
    return svg_start(w, h, body, f"{project['name']} featured repository")


def save(name, content):
    ASSETS.mkdir(parents=True, exist_ok=True)
    out = ASSETS / name
    out.write_text(content, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)")


def main():
    placeholder = "--placeholders" in sys.argv
    data = None if placeholder else get_data()  # Fail, do not publish fabricated data.
    save("overview.svg", overview(data))
    save("contributions.svg", contribution_graph(data))
    save("activity.svg", activity_graph(data))
    save("languages.svg", language_graph(data))
    for p in PROJECTS:
        save(p["filename"], project_card(p, None if data is None else data["chosen"][p["slug"]]))
    if data:
        print(f"Verified {data['total']} contributions, {len(data['repos'])} public owned repos")
    else:
        print("Placeholders only: no GitHub numbers invented.")


if __name__ == "__main__":
    main()
