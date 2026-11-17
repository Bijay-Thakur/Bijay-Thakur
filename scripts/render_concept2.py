#!/usr/bin/env python3
"""Paint Cozy Studio's contribution garden using the GitHub GraphQL calendar.

The background is decorative only. All counts, dates, month positions, and
heatmap colors are computed from the verified GitHub API payload. This module
never copies any numerical values from the illustrated mockup.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
SOURCE = ASSETS / 'garden-scene.jpg'
DESTINATION = ASSETS / 'contributions-painted.png'
INK = '#453020'
BROWN = '#82583B'
GREEN = '#276D3D'
FILL = '#FFF8E9'
OUTLINE = '#E2B677'
SHADES = ['#E7ECDC', '#CBE9A1', '#A8DB6B', '#76BC50', '#348D3E', '#145C33']


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    p = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    return ImageFont.truetype(p, size)


def _calendar_columns(days: list[dict]) -> list[tuple[date, dict[int, int]]]:
    if not days:
        raise ValueError('GitHub did not provide any contribution days')
    groups: dict[date, dict[int, int]] = defaultdict(dict)
    for item in days:
        d = date.fromisoformat(item['date'])
        count = int(item['contributionCount'])
        if count < 0:
            raise ValueError('GitHub contribution count cannot be negative')
        dow = (d.weekday() + 1) % 7  # Sunday=0, matching GitHub's calendar
        first = d - timedelta(days=dow)
        groups[first][dow] = count
    return [(k, groups[k]) for k in sorted(groups)][-54:]


def render_garden(data: dict | None, target: Path | None = None, refreshed_at: datetime | None = None) -> Path:
    if not SOURCE.is_file():
        raise FileNotFoundError(f'Illustration missing: {SOURCE}')
    image = Image.open(SOURCE).convert('RGB')
    width, height = image.size
    if width != 1500 or height != 354:
        raise ValueError(f'Unexpected garden illustration dimensions: {image.size}')
    draw = ImageDraw.Draw(image)

    # A fresh opaque parchment overlays *all* of the illustrative fake sample
    # grid, month labels and "206" count baked into the reference image.
    # This leaves the garden sign, flowers, trees and watering can untouched.
    draw.rounded_rectangle((391, 45, 1278, 329), radius=25,
                           fill=FILL, outline=OUTLINE, width=5)
    if data is None:
        draw.text((427, 81), 'Awaiting GitHub contribution data', font=font(30, True), fill=BROWN)
        draw.text((427, 145), 'The next successful GitHub Actions run draws the real calendar.',
                  font=font(19), fill=INK)
        draw.text((427, 210), 'No sample contributions are shown.', font=font(20, True), fill=GREEN)
    else:
        if not isinstance(data.get('days'), list) or 'total' not in data:
            raise ValueError('Missing verified GitHub contribution calendar')
        cols = _calendar_columns(data['days'])
        count = int(data['total'])
        if count < 0:
            raise ValueError('Invalid GitHub rolling-year count')

        draw.text((410, 69), 'My year in code', font=font(30, True), fill=INK)
        count_str = f'{count:,} contributions'
        right = draw.textbbox((0, 0), count_str, font=font(25, True))[2]
        draw.text((1251 - right, 76), count_str, font=font(25, True), fill=GREEN)

        n = len(cols)
        start_x, grid_w = 416, 837
        step = grid_w / max(n, 1)
        sq = max(7, min(13, int(step) - 3))
        grid_top = 142
        max_day = max(int(d['contributionCount']) for d in data['days']) or 1
        last_month = None
        last_month_x = -100
        for ix, (first, vals) in enumerate(cols):
            mid = first + timedelta(days=3)
            month_key = (mid.year, mid.month)
            pos = int(start_x + ix*step)
            if month_key != last_month and pos - last_month_x > 43:
                draw.text((pos, 113), mid.strftime('%b'), font=font(17, True), fill=BROWN)
                last_month = month_key
                last_month_x = pos
            for dow, daily in vals.items():
                lvl = 0 if daily == 0 else min(5, 1 + int(4 * math.sqrt(daily/max_day)))
                x, y = pos, grid_top + dow*18
                draw.rounded_rectangle((x, y, x+sq, y+13), radius=3, fill=SHADES[lvl])

        draw.text((413, 287), 'Less', font=font(19, True), fill=BROWN)
        for k, color in enumerate(SHADES):
            x = 468 + k*28
            draw.rounded_rectangle((x, 288, x+21, 305), radius=4, fill=color)
        draw.text((646, 287), 'More', font=font(19, True), fill=BROWN)
        refreshed_at = refreshed_at or datetime.now(timezone.utc)
        if refreshed_at.tzinfo is None:
            raise ValueError('Refresh timestamp must include a timezone')
        timestamp = refreshed_at.astimezone(timezone.utc).strftime('Updated %Y-%m-%d %H:%M UTC')
        draw.text((866, 288), timestamp, font=font(15), fill=BROWN)
    output = target or DESTINATION
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True, compress_level=8)
    print(f'Generated verified contribution garden: {output} ({output.stat().st_size:,} bytes)')
    return output