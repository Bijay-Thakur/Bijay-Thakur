#!/usr/bin/env python3
"""Generate a restrained, data-accurate profile activity panel and README metrics.

Uses the authenticated GitHub API loader in github_data.py. If the request fails,
this script fails rather than silently writing synthetic counts.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / 'assets/editorial-activity.svg'
README = ROOT / 'README.md'
START = '<!-- LIVE_METRICS_START -->'
END = '<!-- LIVE_METRICS_END -->'


def _week_columns(days: list[dict]):
    if not days or not isinstance(days, list):
        raise ValueError('Missing verified contribution days')
    groups = defaultdict(dict)
    unique_dates = set()
    for day in days:
        when = date.fromisoformat(day['date'])
        count = int(day['contributionCount'])
        if count < 0 or when in unique_dates:
            raise ValueError('Invalid or repeated GitHub contribution day')
        unique_dates.add(when)
        weekday = (when.weekday() + 1) % 7  # Sunday = 0
        week = when - timedelta(days=weekday)
        groups[week][weekday] = count
    return [(start, groups[start]) for start in sorted(groups)][-54:]


def metrics_markdown(data: dict) -> str:
    repos = data['repos']
    if not isinstance(repos, list):
        raise ValueError('Missing public repository list')
    contributions = int(data['total'])
    if contributions < 0:
        raise ValueError('Negative contribution count')
    stars = sum(int(x['stargazers_count']) for x in repos)
    forks = sum(int(x['forks_count']) for x in repos)
    if min(stars, forks) < 0:
        raise ValueError('Invalid public repository statistics')
    return (f'**{contributions:,}** contributions in the rolling year · '
            f'**{len(repos):,}** public repositories · '
            f'**{stars:,}** stars received · '
            f'**{forks:,}** forks  \n'
            '<sub>Source: GitHub GraphQL contribution calendar and REST repository metadata.</sub>')


def update_readme(data: dict) -> bool:
    source = README.read_text(encoding='utf-8')
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError('Expected exactly one live-metrics marker pair')
    a, b = source.index(START), source.index(END)
    if b <= a:
        raise ValueError('Incorrect marker order')
    updated = source[:a] + START + '\n' + metrics_markdown(data) + '\n' + source[b:]
    if source != updated:
        README.write_text(updated, encoding='utf-8')
        return True
    return False


def build_svg(data: dict, now: datetime | None = None) -> str:
    columns = _week_columns(data['days'])
    if not 52 <= len(columns) <= 54:
        raise ValueError('GitHub GraphQL calendar should contain 52–54 weeks')
    if not 300 <= len(data['days']) <= 372:
        raise ValueError('GitHub GraphQL calendar is incomplete')
    if sum(int(d['contributionCount']) for d in data['days']) != int(data['total']):
        raise ValueError('Calendar total does not match returned contribution days')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('Timestamp needs timezone')
    timestamp = now.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    width, height = 1040, 221
    x0, y0, step, side = 57, 58, 17, 12
    colors = ['#e5eaf0','#c5d8e9','#89b3d6','#4687bb','#1f5c91']
    body = [f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="12" fill="#f8fafc" stroke="#d9e2ec"/>',
            '<text x="26" y="34" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#132336">My year in code</text>',
            f'<text x="1014" y="32" font-family="Arial,Helvetica,sans-serif" font-size="15" text-anchor="end" fill="#3a5873">{int(data["total"]):,} contributions</text>']
    # 52/53/54 week columns: adjust step so the heatmap never overflows the fixed canvas.
    step = min(17, 946 / max(len(columns), 1))
    side = min(12, step - 4)
    for i, (week_start, entries) in enumerate(columns):
        xx = x0 + i * step
        if i == 0 or week_start.day <= 7:
            label = escape((week_start + timedelta(days=3)).strftime('%b'))
            if i == 0 or (columns[i-1][0] + timedelta(days=3)).month != (week_start + timedelta(days=3)).month:
                body.append(f'<text x="{xx:.1f}" y="53" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#486278">{label}</text>')
        for weekday, count in entries.items():
            level = 0 if count == 0 else (1 if count == 1 else 2 if count <= 3 else 3 if count <= 6 else 4)
            yy = y0 + weekday * 17
            body.append(f'<rect x="{xx:.1f}" y="{yy}" width="{side:.1f}" height="12" rx="2" fill="{colors[level]}"/>')
    body += [
        '<text x="26" y="195" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#4f6277">Every square is one day · darker blue = more contributions</text>',
        f'<text x="1014" y="195" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#4f6277">Updated {escape(timestamp)}</text>'
    ]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Verified GitHub daily contribution heatmap">'
            + ''.join(body) + '</svg>')


def render(data: dict) -> None:
    svg = build_svg(data)
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    ASSET.write_text(svg, encoding='utf-8')
    update_readme(data)
    print('Updated editorial profile activity from GitHub API data')


if __name__ == '__main__':
    if '--placeholder' in sys.argv:
        # A failure must not write fabricated numbers or previous data.
        raise SystemExit('Run in GitHub Actions with GH_TOKEN to create verified charts')
    from github_data import get_data
    render(get_data())