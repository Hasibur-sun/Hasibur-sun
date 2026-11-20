#!/usr/bin/env python3
"""Generate pixel-art GitHub stats SVGs from REAL GitHub data.

Writes:
  assets/generated/stats.svg          player statistics card
  assets/generated/contributions.svg  8-bit contribution heatmap

Usage:
  GITHUB_TOKEN=... python scripts/pixel_stats.py [--user NAME] [--out DIR]
  python scripts/pixel_stats.py --placeholder      # "awaiting first sync" cards, no data
  python scripts/pixel_stats.py --mock-test        # layout test with FAKE data (never commit)

Nothing here invents numbers: every figure comes from the GitHub GraphQL API.
If the API call fails, the previously generated files are left untouched.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

BG, BG2, NAVY = "#090D16", "#111827", "#151D2E"
ORANGE, YELLOW, RED, GREEN = "#FF8C42", "#FFD166", "#D95D39", "#7CDBA6"
TEXT, MUTED = "#E8E6DD", "#9299A8"
FONT = "'Courier New',Courier,monospace"

LEVELS = {
    "NONE": NAVY,
    "FIRST_QUARTILE": "#6B3A2E",
    "SECOND_QUARTILE": RED,
    "THIRD_QUARTILE": ORANGE,
    "FOURTH_QUARTILE": YELLOW,
}

QUERY = """
query($login:String!){
  user(login:$login){
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount contributionLevel } }
      }
    }
    repositories(privacy:PUBLIC, ownerAffiliations:OWNER, isFork:false, first:100){
      totalCount
      nodes{ languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "pixel-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        raise RuntimeError(f"GraphQL error: {payload.get('errors')}")
    return payload["data"]["user"]


# ---------------------------------------------------------------- SVG helpers
def head(w: int, h: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{escape(title)}" shape-rendering="crispEdges">'
        f"<title>{escape(title)}</title>"
        '<defs><pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="1" fill="#000" opacity=".22"/></pattern></defs>'
        f'<rect width="{w}" height="{h}" fill="{BG2}"/>'
    )


def frame(w: int, h: int, label: str) -> str:
    s = (
        f'<rect x="0" y="4" width="{w}" height="{h-8}" fill="{ORANGE}"/>'
        f'<rect x="4" y="0" width="{w-8}" height="{h}" fill="{ORANGE}"/>'
        f'<rect x="4" y="8" width="{w-8}" height="{h-16}" fill="{BG}"/>'
        f'<rect x="8" y="4" width="{w-16}" height="{h-8}" fill="{BG}"/>'
        f'<rect x="20" y="0" width="{len(label)*10+24}" height="16" fill="{BG}"/>'
        f'<text x="32" y="12" font-family="{FONT}" font-size="14" font-weight="bold" fill="{YELLOW}">{escape(label)}</text>'
    )
    return s


def tail(w: int, h: int) -> str:
    return f'<rect width="{w}" height="{h}" fill="url(#sl)"/></svg>'


def txt(x, y, s, size=16, fill=TEXT, bold=False, anchor="start") -> str:
    b = ' font-weight="bold"' if bold else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}"{b} '
        f'fill="{fill}" text-anchor="{anchor}">{escape(str(s))}</text>'
    )


# ------------------------------------------------------------------ analysis
def streaks(days: list[dict]) -> tuple[int, int]:
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    cur, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today may not have a contribution yet
        i -= 1
    while i >= 0 and counts[i] > 0:
        cur += 1
        i -= 1
    return cur, longest


def languages(repos: list[dict]) -> list[tuple[str, int]]:
    tot: dict[str, int] = {}
    for r in repos:
        for e in (r.get("languages") or {}).get("edges", []):
            tot[e["node"]["name"]] = tot.get(e["node"]["name"], 0) + e["size"]
    return sorted(tot.items(), key=lambda kv: -kv[1])[:5]


# ------------------------------------------------------------------ renderers
def render_stats(user: dict, today: str) -> str:
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    cur, longest = streaks(days)
    langs = languages(user["repositories"]["nodes"])
    W, H = 800, 250
    s = head(W, H, "Player statistics") + frame(W, H, " PLAYER STATISTICS ")
    s += txt(32, 52, "PLAYER LEVEL: DEVELOPER", 15, GREEN, True)
    items = [
        ("CONTRIBUTIONS · 12 MO", cal["totalContributions"]),
        ("CURRENT STREAK", f"{cur} D"),
        ("LONGEST STREAK · 12 MO", f"{longest} D"),
        ("PUBLIC REPOS", user["repositories"]["totalCount"]),
    ]
    for i, (k, v) in enumerate(items):
        x = 32 + i * 188
        s += f'<rect x="{x}" y="68" width="172" height="62" fill="{NAVY}"/>'
        s += f'<rect x="{x}" y="68" width="172" height="4" fill="{ORANGE}"/>'
        s += txt(x + 10, 94, k, 11, MUTED)
        s += txt(x + 10, 120, v, 24, YELLOW, True)
    s += txt(32, 158, "MOST-USED LANGUAGES · PUBLIC REPOS, BY CODE SIZE", 12, MUTED)
    total = sum(sz for _, sz in langs) or 1
    x, pal = 32, [ORANGE, YELLOW, RED, GREEN, MUTED]
    bw = W - 64
    for i, (n, sz) in enumerate(langs):
        w = max(4, round(bw * sz / total / 4) * 4)
        s += f'<rect x="{x}" y="168" width="{w}" height="14" fill="{pal[i % 5]}"/>'
        x += w
    lx = 32
    for i, (n, sz) in enumerate(langs):
        s += f'<rect x="{lx}" y="194" width="10" height="10" fill="{pal[i % 5]}"/>'
        label = f"{n} {sz*100/total:.0f}%"
        s += txt(lx + 16, 204, label, 13, TEXT)
        lx += 16 + len(label) * 8 + 20
    s += txt(W - 32, 236, f"LAST SYNC {today}", 11, MUTED, anchor="end")
    return s + tail(W, H)


def render_contrib(user: dict, today: str) -> str:
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    cell, gap = 12, 3
    step = cell + gap
    left, top = 40, 84
    W = left + len(weeks) * step + 32
    H = 84 + 7 * step + 78
    s = head(W, H, "Pixelated contribution graph") + frame(W, H, " XP LOG · LAST 12 MONTHS ")
    s += txt(32, 52, f"XP EARNED: {cal['totalContributions']}", 14, GREEN, True)
    for d, lbl in ((1, "MON"), (3, "WED"), (5, "FRI")):
        s += txt(10, top + d * step + 10, lbl[0], 10, MUTED)
    last_month = None
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            dt = datetime.strptime(d["date"], "%Y-%m-%d").date()
            dow = (dt.weekday() + 1) % 7  # Sunday = 0
            x, y = left + wi * step, top + dow * step
            col = LEVELS.get(d["contributionLevel"], NAVY)
            s += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{col}"/>'
            if d["date"] == today:
                s += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="none" stroke="{GREEN}" stroke-width="2"/>'
            if dow == 0 and dt.month != last_month and dt.day <= 7:
                s += txt(x, top - 8, dt.strftime("%b").upper(), 10, MUTED)
                last_month = dt.month
    ly = top + 7 * step + 22
    s += txt(left, ly + 10, "LESS", 11, MUTED)
    for i, c in enumerate(LEVELS.values()):
        s += f'<rect x="{left + 40 + i*(cell+4)}" y="{ly}" width="{cell}" height="{cell}" fill="{c}"/>'
    s += txt(left + 40 + 5 * (cell + 4) + 6, ly + 10, "MORE XP", 11, MUTED)
    s += txt(W - 32, H - 14, f"LAST SYNC {today}", 11, MUTED, anchor="end")
    return s + tail(W, H)


def render_placeholder(kind: str) -> str:
    W, H = (800, 250) if kind == "stats" else (800, 210)
    label = " PLAYER STATISTICS " if kind == "stats" else " XP LOG · LAST 12 MONTHS "
    s = head(W, H, f"{kind} awaiting first sync") + frame(W, H, label)
    s += txt(W // 2, H // 2 - 6, "SCANNING THE FRONTIER...", 20, YELLOW, True, "middle")
    s += txt(W // 2, H // 2 + 22, "REAL DATA ARRIVES AFTER THE FIRST WORKFLOW RUN", 12, MUTED, False, "middle")
    return s + tail(W, H)


def mock_user() -> dict:
    import random
    random.seed(3)
    weeks, d0 = [], date(2026, 11, 20)
    from datetime import timedelta
    start = d0 - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    cur = start
    while cur <= d0:
        days = []
        for _ in range(7):
            if cur <= d0:
                n = random.choice([0, 0, 0, 1, 2, 4, 7, 12])
                lv = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"][
                    0 if n == 0 else 1 if n < 2 else 2 if n < 4 else 3 if n < 8 else 4]
                days.append({"date": cur.isoformat(), "contributionCount": n, "contributionLevel": lv})
            cur += timedelta(days=1)
        weeks.append({"contributionDays": days})
    return {
        "contributionsCollection": {"contributionCalendar": {"totalContributions": 123, "weeks": weeks}},
        "repositories": {"totalCount": 9, "nodes": [{"languages": {"edges": [
            {"size": 500, "node": {"name": "Python"}}, {"size": 300, "node": {"name": "TypeScript"}},
            {"size": 100, "node": {"name": "Kotlin"}}]}}]},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "Hasibur-sun"))
    ap.add_argument("--out", default="assets/generated")
    ap.add_argument("--placeholder", action="store_true")
    ap.add_argument("--mock-test", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    if a.placeholder:
        (out / "stats.svg").write_text(render_placeholder("stats"), encoding="utf-8")
        (out / "contributions.svg").write_text(render_placeholder("contributions"), encoding="utf-8")
        return 0
    if a.mock_test:
        user, today = mock_user(), "2026-11-20"
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print("GITHUB_TOKEN is required", file=sys.stderr)
            return 1
        try:
            user = fetch(a.user, token)
        except Exception as e:  # keep the old files: graceful fallback
            print(f"fetch failed, keeping existing files: {e}", file=sys.stderr)
            return 0
    (out / "stats.svg").write_text(render_stats(user, today), encoding="utf-8")
    (out / "contributions.svg").write_text(render_contrib(user, today), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
