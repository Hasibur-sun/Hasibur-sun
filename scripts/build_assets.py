#!/usr/bin/env python3
"""Builds the original pixel-art SVG assets in ./assets (no external art, no copyrighted material)."""
from __future__ import annotations

import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
BG, BG2, NAVY = "#090D16", "#111827", "#151D2E"
ORANGE, YELLOW, RED, GREEN = "#FF8C42", "#FFD166", "#D95D39", "#7CDBA6"
TEXT, MUTED = "#E8E6DD", "#9299A8"
FONT = "'Courier New',Courier,monospace"


def svg(w, h, title, body, extra_defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{escape(title)}" shape-rendering="crispEdges">'
        f"<title>{escape(title)}</title><defs>"
        '<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="1" fill="#000" opacity=".22"/></pattern>'
        f"{extra_defs}</defs>{body}"
        f'<rect width="{w}" height="{h}" fill="url(#sl)"/></svg>'
    )


def t(x, y, s, size=16, fill=TEXT, bold=False, anchor="start", extra=""):
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}"{b} fill="{fill}" '
            f'text-anchor="{anchor}" shape-rendering="auto" {extra}>{escape(s)}</text>')


def r(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def frame(w, h, label="", border=ORANGE, bg=BG):
    s = (r(0, 4, w, h - 8, border) + r(4, 0, w - 8, h, border)
         + r(4, 8, w - 8, h - 16, bg) + r(8, 4, w - 16, h - 8, bg))
    if label:
        s += r(20, 0, len(label) * 10 + 24, 16, bg)
        s += t(32, 12, label, 14, YELLOW, True)
    return s


def sprite(rows, palette, x, y, px):
    out = []
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            c = row[i]
            if c == ".":
                i += 1
                continue
            k = i
            while k < len(row) and row[k] == c:
                k += 1
            out.append(r(x + i * px, y + j * px, (k - i) * px, px, palette[c]))
            i = k
    return "".join(out)


COWBOY = [
    "....hhhhhh....",
    "..hhhhhhhhhh..",
    "hhhhbbbbbbhhhh",
    "....ssssss....",
    "....ssdsds....",
    ".....ssss.....",
    "...cccccccc...",
    "..cccccccccc..",
    "..ccccccccccs.",
    "..cccccccccc..",
    "..cccccccccc..",
    "...cccccccc...",
    "...bbbbbbbb...",
    "...tttttttt...",
    "...tt....tt...",
    "...tt....tt...",
    "...tt....tt...",
    "..kkk....kkk..",
    "..kkk....kkk..",
]
COWBOY_PAL = {"h": "#3a4670", "b": ORANGE, "s": TEXT, "d": BG, "c": YELLOW, "t": "#2a3350", "k": "#0b0f1a"}

SHIP = [
    "...........oooo..........",
    "......ooooooooooooo......",
    "...oooooooooooooooooo....",
    "..ooowwwwooooooooooooo...",
    ".oooowwwwoooooooooooooooo",
    "..oooooooooooooooooooooo.",
    "...rrrrrrrrrrrrrrrrrr....",
    ".....rr..........rr......",
]
SHIP_PAL = {"o": ORANGE, "w": YELLOW, "r": RED}

TROPHY = [
    ".yyyyyyyyyy.",
    "yyyyyyyyyyyy",
    "yyyyyyyyyyyy",
    "yyyyyyyyyyyy",
    ".yyyyyyyyyy.",
    "..yyyyyyyy..",
    "....yyyy....",
    "....yyyy....",
    "...oooooo...",
    "..oooooooo..",
]


def stars(w, h, n, seed, ymax=None):
    rnd = random.Random(seed)
    ymax = ymax or h
    s = []
    for i in range(n):
        x, y = rnd.randrange(0, w, 4), rnd.randrange(0, ymax, 4)
        size = rnd.choice([2, 2, 4])
        col = rnd.choice([TEXT, TEXT, YELLOW, MUTED])
        anim = ' class="tw"' if i % 9 == 0 else ""
        s.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{col}"{anim}/>')
    return "".join(s)


TWINKLE = "<style>.tw{animation:tw 3s steps(2) infinite}@keyframes tw{50%{opacity:.15}}</style>"


# ------------------------------------------------------------------ banner
def banner():
    W, H = 1200, 440
    rnd = random.Random(7)
    grad = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG}"/><stop offset=".55" stop-color="{NAVY}"/>'
            f'<stop offset=".82" stop-color="#4a2a36"/><stop offset="1" stop-color="{RED}"/></linearGradient>'
            f'<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{YELLOW}"/>'
            f'<stop offset="1" stop-color="{ORANGE}"/></linearGradient>'
            f'<clipPath id="pl"><circle cx="1030" cy="120" r="84"/></clipPath>'
            f'<clipPath id="sc"><circle cx="930" cy="392" r="118"/></clipPath>'
            f'<filter id="gr"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 .9  0 0 0 0 .8  0 0 0 .5 0"/></filter>')
    b = r(0, 0, W, H, "url(#sky)") + stars(W, H, 130, 11, 300)
    # planet with bands, shadow and ring
    b += '<g clip-path="url(#pl)">' + r(940, 30, 200, 180, RED)
    for i, (y, c) in enumerate([(52, ORANGE), (76, YELLOW), (100, ORANGE), (128, "#a8452a"), (152, ORANGE), (176, YELLOW)]):
        b += r(940, y, 200, 12 if i % 2 else 8, c, 'opacity=".75"')
    b += '<circle cx="1070" cy="150" r="96" fill="#090D16" opacity=".45"/></g>'
    b += (f'<ellipse cx="1030" cy="120" rx="150" ry="22" fill="none" stroke="{YELLOW}" stroke-width="6" '
          f'opacity=".8" transform="rotate(-16 1030 120)" shape-rendering="auto"/>')
    # retro sunset behind skyline
    b += '<g clip-path="url(#sc)">' + f'<circle cx="930" cy="392" r="118" fill="url(#sun)"/>'
    for i, y in enumerate(range(320, 392, 12)):
        b += r(800, y, 260, 2 + i, "#4a2a36")
    b += "</g>"
    # skyline
    x = 0
    while x < W:
        w = rnd.choice([32, 40, 48, 60, 72])
        h = rnd.choice([50, 70, 90, 120, 150])
        b += r(x, 380 - h, w, h + 60, "#0b0f1a")
        if rnd.random() < .3:
            b += r(x + w // 2 - 2, 380 - h - 20, 4, 20, "#0b0f1a")
        for wy in range(380 - h + 10, 372, 16):
            for wx in range(x + 8, x + w - 8, 12):
                if rnd.random() < .22:
                    b += r(wx, wy, 4, 4, YELLOW, 'opacity=".85"')
        x += w + 4
    b += r(0, 392, W, 48, BG)
    b += r(0, 392, W, 4, RED, 'opacity=".6"')
    # cowboy on rock ledge
    b += r(40, 372, 190, 20, "#1b2338") + r(60, 364, 80, 8, "#1b2338")
    b += sprite(COWBOY, COWBOY_PAL, 76, 372 - 19 * 6, 6)
    # drifting ship
    b += sprite(SHIP, SHIP_PAL, 800, 205, 5)
    b += r(740, 238, 50, 4, YELLOW, 'opacity=".6"') + r(700, 238, 30, 4, ORANGE, 'opacity=".4"')
    # title
    b += t(304, 100, "SEE YOU, SPACE CODER.", 50, BG, True, extra='dx="4" dy="4"')
    b += t(300, 96, "SEE YOU, SPACE CODER.", 50, ORANGE, True)
    b += t(300, 134, "BUILDING IN THE DIGITAL FRONTIER.", 22, YELLOW, True)
    b += r(300, 150, 120, 4, GREEN)
    # status panel
    px, py = 300, 190
    b += r(px, py, 400, 168, BG, 'opacity=".88"') + r(px, py, 400, 4, ORANGE) + r(px, py + 164, 400, 4, ORANGE)
    b += r(px, py, 4, 168, ORANGE) + r(px + 396, py, 4, 168, ORANGE)
    lines = [("PLAYER", "HASIBUR-SUN"), ("CLASS", "CSE STUDENT / DEVELOPER"), ("REGION", "BANGLADESH"),
             ("STATUS", "ONLINE"), ("MISSION", "BUILDING & EXPLORING")]
    for i, (k, v) in enumerate(lines):
        y = py + 36 + i * 28
        b += t(px + 20, y, k + ":", 16, MUTED, True)
        col = GREEN if k == "STATUS" else TEXT
        b += t(px + 110, y, ("● " if k == "STATUS" else "") + v, 16, col, True)
    b += f'<rect width="{W}" height="{H}" filter="url(#gr)" opacity=".10"/>'
    return svg(W, H, "Retro space-cowboy banner: SEE YOU, SPACE CODER. Player HASIBUR-SUN, status online", b, grad + TWINKLE)


# ------------------------------------------------------------------ HUD / divider
def hud():
    W, H = 1200, 64
    b = frame(W, H, "", ORANGE, BG2)
    b += r(24, 24, 12, 12, GREEN, 'class="tw"')
    b += t(48, 36, "PLAYER STATUS", 16, YELLOW, True)
    b += t(210, 36, "● ONLINE", 16, GREEN, True)
    b += t(330, 36, "CURRENT MISSION: BUILDING & EXPLORING", 16, TEXT, True)
    b += t(W - 32, 36, "FRONTIER: OPEN", 16, ORANGE, True, "end")
    return svg(W, H, "Player status HUD: online, building and exploring", b, TWINKLE)


def button(label, name, w):
    h = 56
    b = r(4, 4, w - 4, h - 4, BG) + r(0, 0, w - 4, h - 4, ORANGE) + r(4, 4, w - 12, h - 12, BG2)
    b += t(w // 2 - 2, 34, label, 20, YELLOW, True, "middle")
    return svg(w, h, label, b)


def divider():
    W, H = 1200, 24
    b = ""
    for i in range(0, W, 24):
        b += r(i, 10, 12, 4, ORANGE if (i // 24) % 2 else RED)
    b += r(W // 2 - 8, 4, 16, 16, YELLOW) + r(W // 2 - 4, 8, 8, 8, BG)
    return svg(W, H, "pixel divider", b)


def section(title, tag):
    W, H = 1200, 56
    b = r(0, 40, W, 4, ORANGE, 'opacity=".5"') + r(0, 0, 8, 44, YELLOW)
    b += t(24, 30, title, 28, YELLOW, True) + t(W - 8, 30, tag, 14, MUTED, False, "end")
    return svg(W, H, title, b)


# ------------------------------------------------------------------ player profile
def player_profile():
    W, H = 1200, 300
    b = frame(W, H, " PLAYER PROFILE ")
    b += r(40, 40, 200, 220, NAVY) + r(40, 40, 200, 4, ORANGE)
    b += stars(200, 220, 20, 4).replace('x="', 'x="').replace("<rect", '<rect transform="translate(40 40)"')
    b += sprite(COWBOY[:13], COWBOY_PAL, 96, 100, 6)
    b += t(140, 244, "HASIBUR-SUN", 14, YELLOW, True, "middle")
    rows = [("PLAYER", "HASIBUR-SUN"), ("CLASS", "ENGINEERING EXPLORER"), ("REGION", "BANGLADESH"),
            ("SPECIAL INTERESTS", "AI / SOFTWARE / DATABASES / WEB"), ("CURRENT STATUS", "LEARNING & BUILDING")]
    for i, (k, v) in enumerate(rows):
        y = 68 + i * 32
        b += t(280, y, k + ":", 17, MUTED, True) + t(520, y, v, 17, TEXT, True)
    b += r(280, 206, 880, 2, ORANGE, 'opacity=".5"')
    b += t(280, 234, "Somewhere between algorithms, databases, and artificial intelligence,", 16, TEXT)
    b += t(280, 262, "I'm trying to build things worth remembering.", 16, YELLOW, True)
    return svg(W, H, "Player profile card for Hasibur-sun, engineering explorer from Bangladesh", b, TWINKLE)


# ------------------------------------------------------------------ inventory
def inventory():
    W, H = 1200, 360
    cols = [
        ("ACTIVELY BUILDING WITH", GREEN, ["Python", "TypeScript", "React", "FastAPI", "PyTorch", "Gemini API"]),
        ("PROJECT EXPERIENCE", ORANGE, ["Kotlin + Jetpack Compose", "Room (SQLite)", "EfficientNet / transfer learning",
                                        "HTML / CSS / JavaScript", "CSP search algorithms", "Git"]),
        ("EXPLORING / LEARNING", YELLOW, ["C / C++", "Java", "Dart", "SQL & DBMS design", "RAG / ChromaDB",
                                          "Prompt engineering"]),
    ]
    b = frame(W, H, " PLAYER INVENTORY ")
    cw = 360
    for ci, (title, col, items) in enumerate(cols):
        x = 40 + ci * (cw + 20)
        b += r(x, 40, cw, 280, NAVY) + r(x, 40, cw, 4, col)
        b += t(x + 16, 72, title, 16, col, True)
        for i, it in enumerate(items):
            y = 108 + i * 34
            b += r(x + 16, y - 14, 14, 14, col) + r(x + 20, y - 10, 6, 6, NAVY)
            b += t(x + 42, y, it, 16, TEXT)
    b += t(W // 2, H - 18, "exploration, not mastery. categories follow what the public repos actually show.", 12, MUTED,
           False, "middle")
    return svg(W, H, "Player inventory: technologies grouped as actively building, project experience, and exploring", b)


# ------------------------------------------------------------------ missions
MISSIONS = [
    ("01", "CROP GUARDIAN", "AGRICULTURAL AI", "GEMINI / PYTORCH / FASTAPI / REACT", "PUBLIC BETA",
     "AI-ASSISTED CROP HEALTH ASSESSMENT", GREEN, "crop-guardian"),
    ("02", "GARBAGE CLASSIFIER", "COMPUTER VISION", "PYTORCH / EFFICIENTNET-B6 / GRADIO", "EXPERIMENT",
     "SORT WASTE FROM A PHOTO - 94.18% TEST ACC.", ORANGE, "garbage-classification-efficientnet"),
    ("03", "INTELLIGENT SUDOKU SOLVER", "AI ALGORITHMS", "PYTHON / CSP / AC-3 / MRV", "LEARNING PROJECT",
     "SOLVE SUDOKU AS A CONSTRAINT PROBLEM", YELLOW, "Intelligent-Sudoku-Solver-CSP"),
    ("04", "MINIMAL NOTES", "ANDROID APP", "KOTLIN / COMPOSE / ROOM", "PROTOTYPE",
     "NOTES WITH TITLE SEARCH, ON-DEVICE", ORANGE, "minimal-android-noteapk"),
    ("05", "LAZY-PAD", "DESKTOP UTILITY", "PYTHON / PYGAME / PYNPUT", "WORKING TOOL",
     "TURN A GAMEPAD INTO MOUSE + REMOTE", GREEN, "lazy-pad"),
]


def mission(m):
    n, name, typ, tech, status, obj, col, _ = m
    W, H = 580, 210
    b = frame(W, H, f" MISSION {n} ", col)
    b += t(32, 58, name, 22 if len(name) < 20 else 18, YELLOW, True)
    rows = [("TYPE", typ), ("TECH", tech), ("STATUS", status), ("OBJECTIVE", obj)]
    for i, (k, v) in enumerate(rows):
        y = 94 + i * 28
        b += t(32, y, k + ":", 14, MUTED, True)
        fs = 13 if len(v) > 32 else 14
        b += t(126, y, v, fs, col if k == "STATUS" else TEXT, k == "STATUS")
    b += t(W - 32, H - 14, "[ OPEN REPO > ]", 12, col, True, "end")
    return svg(W, H, f"Mission {n}: {name}. Type {typ}. Status {status}. Objective {obj}", b)


# ------------------------------------------------------------------ trophies
def trophies():
    W, H = 1200, 190
    items = [("FIRST COMMIT", "FIRST REPO PUSHED"), ("AI BUILDER", "HYBRID + CV PROJECTS"),
             ("FULL STACK EXPLORER", "FASTAPI + REACT"), ("PROJECT SHIPPER", "CROP GUARDIAN BETA")]
    b = frame(W, H, " ACHIEVEMENT UNLOCKED ")
    cw = 270
    for i, (n, sub) in enumerate(items):
        x = 36 + i * (cw + 20)
        b += r(x, 40, cw, 120, NAVY) + r(x, 40, cw, 4, YELLOW)
        pal = {"y": YELLOW, "o": ORANGE}
        b += sprite(TROPHY, pal, x + 16, 62, 6)
        b += t(x + 100, 86, n, 14 if len(n) > 14 else 17, TEXT, True)
        b += t(x + 100, 112, sub, 12, MUTED)
        b += t(x + 100, 140, "+ UNLOCKED", 12, GREEN, True)
    return svg(W, H, "Achievements: first commit, AI builder, full stack explorer, project shipper", b)


# ------------------------------------------------------------------ terminals
def logbook():
    W, H = 1200, 290
    b = frame(W, H, " THE ENGINEERING LOGBOOK ", GREEN)
    entries = [
        ("ACTIVE", GREEN, "AI & ML", "crop-guardian, garbage-classification (latest signals: Nov 2026)"),
        ("ACTIVE", GREEN, "TOOLING", "lazy-pad: gamepad as laptop remote (Nov 2026)"),
        ("LOGGED", ORANGE, "ALGORITHMS", "CSP sudoku solver with AC-3 + MRV (Sep 2026)"),
        ("LOGGED", ORANGE, "ANDROID", "Kotlin + Compose notes prototype (May 2026)"),
        ("STUDYING", YELLOW, "DATABASES / DSA", "ongoing exploration"),
    ]
    b += t(32, 52, "> mission-journal --recent", 15, MUTED)
    for i, (st, col, k, v) in enumerate(entries):
        y = 90 + i * 34
        b += t(32, y, f"[{st}]", 16, col, True) + t(150, y, k, 16, YELLOW, True) + t(340, y, v, 16, TEXT)
    b += t(32, 268, "_", 18, GREEN, True, extra='class="tw"')
    return svg(W, H, "Engineering logbook: recent mission journal entries", b, TWINKLE)


def destination():
    W, H = 620, 270
    b = frame(W, H, "")
    b += r(8, 56, W - 16, 4, ORANGE)
    b += t(W // 2, 40, "NEXT DESTINATION", 20, YELLOW, True, "middle")
    for i, s in enumerate(["MASTER THE FUNDAMENTALS", "BUILD INTELLIGENT SYSTEMS", "EXPLORE NEW TECHNOLOGIES",
                           "TURN IDEAS INTO REAL PROJECTS"]):
        b += t(60, 102 + i * 30, "> " + s, 18, TEXT, True)
    b += t(60, 238, "MISSION STATUS: ONGOING", 16, GREEN, True)
    return svg(W, H, "Next destination: master the fundamentals, build intelligent systems, explore new technologies, turn ideas into real projects", b)


def soundtrack():
    W, H = 620, 270
    b = frame(W, H, " CURRENT SOUNDTRACK ", YELLOW)
    b += r(40, 50, 220, 130, NAVY) + r(40, 50, 220, 4, ORANGE) + r(56, 66, 188, 34, TEXT)
    b += t(150, 89, "SIDE A / NIGHT SHIFT", 13, BG, True, "middle")
    for cx in (96, 204):
        b += r(cx - 24, 116, 48, 48, BG) + r(cx - 12, 128, 24, 24, ORANGE)
        b += r(cx - 4, 120, 8, 8, YELLOW, 'class="tw"')
    b += r(116, 140, 72, 4, MUTED)
    b += t(290, 96, "Midnight jazz.", 20, TEXT, True) + t(290, 128, "Neon streets.", 20, ORANGE, True)
    b += t(290, 160, "Endless code.", 20, YELLOW, True)
    b += t(40, 226, "(decorative cassette: no audio, no embeds)", 12, MUTED)
    return svg(W, H, "Current soundtrack: Midnight jazz. Neon streets. Endless code.", b, TWINKLE)


def ship_asset():
    return svg(140, 60, "pixel spaceship", sprite(SHIP, SHIP_PAL, 4, 4, 5))


def stars_asset():
    return svg(600, 120, "pixel stars", stars(600, 120, 40, 5), TWINKLE)


def signature():
    W, H = 1200, 150
    b = r(0, 0, W, H, BG) + stars(W, H, 40, 21)
    b += t(W // 2, 56, "Not at the destination yet. Just enjoying the journey through the digital frontier.", 18, TEXT,
           False, "middle")
    b += t(W // 2, 104, "SEE YOU, SPACE CODER.", 34, ORANGE, True, "middle")
    b += r(W // 2 - 60, 120, 120, 4, GREEN)
    return svg(W, H, "SEE YOU, SPACE CODER. Not at the destination yet.", b, TWINKLE)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "space-banner.svg": banner(), "retro-hud.svg": hud(), "pixel-divider.svg": divider(),
        "player-profile.svg": player_profile(), "player-inventory.svg": inventory(),
        "pixel-trophy.svg": trophies(), "pixel-terminal.svg": logbook(),
        "next-destination.svg": destination(), "soundtrack.svg": soundtrack(),
        "pixel-ship.svg": ship_asset(), "pixel-stars.svg": stars_asset(), "signature.svg": signature(),
        "button-portfolio.svg": button("[ OPEN PERSONAL PORTFOLIO ]", "p", 460),
    }
    for title, tag, fname in [("PLAYER PROFILE", "// CHARACTER SCREEN", "h-profile"),
                              ("PLAYER INVENTORY", "// ITEMS", "h-inventory"),
                              ("ACTIVE MISSIONS", "// PROJECT ARCHIVE", "h-missions"),
                              ("PLAYER STATISTICS", "// REAL DATA FROM GITHUB", "h-stats"),
                              ("ACHIEVEMENTS", "// VERIFIED ONLY", "h-achievements")]:
        files[f"{fname}.svg"] = section(title, tag)
    for m in MISSIONS:
        files[f"mission-{m[7]}.svg".lower()] = mission(m)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} assets to {OUT}")


if __name__ == "__main__":
    main()
