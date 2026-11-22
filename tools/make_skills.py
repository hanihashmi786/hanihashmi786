"""Generate the Skills & Technologies card, modelled on the portfolio's About page.

    python tools/make_skills.py   (run from the repo root)

Same lists as hanihashmi.vercel.app/about (Tech Stack and Tools tabs), drawn as
tiles in the banner's Gold theme. Logos are Devicon (MIT), fetched once and
cached in tools/icons/, then embedded as data URIs because README images can't
load anything external.
"""
import base64
import urllib.request
from html import escape
from pathlib import Path

from make_banner import (BG, PANEL, CURRENT, FG, MUTED, COMMENT, GOLD,
                         TL_RED, TL_YELLOW, TL_GREEN, font_face)

ROOT = Path(__file__).resolve().parent.parent
ICONS = Path(__file__).resolve().parent / "icons"
DEVICON = "2.16.0"
TILE_BG, TILE_EDGE = "#1A1A1B", "#2D2D2D"

# (name, category, devicon path, fix): fix=True turns a dark logo white,
# fix="invert" flips a black-and-white logo so it reads on the dark tile.
STACK = [
    ("Python", "Language", "python/python-original", False),
    ("JavaScript", "Language", "javascript/javascript-original", False),
    ("TypeScript", "Language", "typescript/typescript-original", False),
    ("React", "Frontend", "react/react-original", False),
    ("React Native", "Mobile", "react/react-original", False),
    ("Next.js", "Framework", "nextjs/nextjs-original", "invert"),
    ("HTML", "Markup", "html5/html5-original", False),
    ("CSS", "Styling", "css3/css3-original", False),
    ("Tailwind CSS", "Styling", "tailwindcss/tailwindcss-original", False),
    ("Angular", "Framework", "angular/angular-original", False),
    ("Flask", "Backend", "flask/flask-original", True),
    ("Django", "Backend", "django/django-plain", True),
    ("Node.js", "Runtime", "nodejs/nodejs-original", False),
    ("Express", "Backend", "express/express-original", True),
    ("PostgreSQL", "Database", "postgresql/postgresql-original", False),
    ("MySQL", "Database", "mysql/mysql-original", False),
    ("MongoDB", "Database", "mongodb/mongodb-original", False),
    ("Firebase", "Backend", "firebase/firebase-original", False),
]
TOOLS = [
    ("Git", "Version Control", "git/git-original", False),
    ("GitHub", "Git Hosting", "github/github-original", True),
    ("AWS", "Cloud", "amazonwebservices/amazonwebservices-original-wordmark", True),
    ("Docker", "Containers", "docker/docker-original", False),
    ("VS Code", "IDE", "vscode/vscode-original", False),
    ("NPM", "Package Manager", "npm/npm-original-wordmark", False),
    ("Selenium", "Automation", "selenium/selenium-original", False),
    ("TensorFlow", "AI / ML", "tensorflow/tensorflow-original", False),
]

W, COLS, PAD, GAP = 1280, 5, 36, 14
TW = (W - 2 * PAD - (COLS - 1) * GAP) / COLS
TH = 70


def icon(path):
    ICONS.mkdir(exist_ok=True)
    cached = ICONS / (path.split("/")[-1].replace("amazonwebservices", "aws") + ".svg")
    if not cached.exists():
        urls = [f"https://cdn.jsdelivr.net/npm/devicon@{DEVICON}/icons/{path}.svg",
                f"https://unpkg.com/devicon@{DEVICON}/icons/{path}.svg",
                f"https://raw.githubusercontent.com/devicons/devicon/v{DEVICON}/icons/{path}.svg"]
        last = None
        for u in urls:
            try:
                data = urllib.request.urlopen(u, timeout=40).read()
                if b"<svg" in data:
                    cached.write_bytes(data)
                    break
            except Exception as e:  # try the next mirror
                last = e
        else:
            raise SystemExit(f"could not fetch {path}: {last}")
    return "data:image/svg+xml;base64," + base64.b64encode(cached.read_bytes()).decode()


def tiles(items, y0):
    out = []
    for i, (name, cat, path, white) in enumerate(items):
        r, c = divmod(i, COLS)
        x, y = PAD + c * (TW + GAP), y0 + r * (TH + GAP)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{TW:.1f}" height="{TH}" rx="14" fill="{TILE_BG}" '
                   f'stroke="{TILE_EDGE}" stroke-width="1.2" filter="url(#soft)"/>')
        f = {True: ' filter="url(#white)"', "invert": ' filter="url(#invert)"'}.get(white, "")
        out.append(f'<image x="{x + 18:.1f}" y="{y + 19}" width="32" height="32" href="{icon(path)}"{f}/>')
        out.append(f'<text x="{x + 64:.1f}" y="{y + 32}" font-family="Poppins" font-weight="600" '
                   f'font-size="17" fill="{FG}">{escape(name)}</text>')
        out.append(f'<text x="{x + 64:.1f}" y="{y + 52}" font-family="JetBrains Mono" font-size="12.5" '
                   f'fill="{COMMENT}">{escape(cat)}</text>')
    rows = -(-len(items) // COLS)
    return "\n  ".join(out), y0 + rows * (TH + GAP) - GAP


def section(label, count, y):
    return (f'<text x="{PAD}" y="{y}" font-family="JetBrains Mono" font-size="15" fill="{GOLD}">{escape(label)}'
            f'<tspan fill="{COMMENT}">  // {count} items</tspan></text>')


def main():
    y = 44 + 52
    parts = [section("tech_stack", len(STACK), y)]
    body, y = tiles(STACK, y + 20)
    parts.append(body)
    y += 52
    parts.append(section("tools", len(TOOLS), y))
    body, y = tiles(TOOLS, y + 20)
    parts.append(body)
    H = int(y + 34)

    names = "".join(n for n, *_ in STACK + TOOLS)
    mono = "".join(c for _, c, *_ in STACK + TOOLS) + "tech_stacktools// items 0123456789~/skills"
    fonts = "".join([font_face("Poppins", 600, names), font_face("JetBrains Mono", 400, mono)])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Skills and technologies</title>
  <desc id="d">Tech stack: {escape(", ".join(n for n, *_ in STACK))}. Tools: {escape(", ".join(n for n, *_ in TOOLS))}.</desc>
  <defs>
    <style>{fonts}</style>
    <filter id="soft" x="-10%" y="-20%" width="120%" height="160%">
      <feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#000" flood-opacity=".55"/>
    </filter>
    <filter id="invert"><feColorMatrix type="matrix" values="-1 0 0 0 1  0 -1 0 0 1  0 0 -1 0 1  0 0 0 1 0"/></filter>
    <filter id="white"><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BG}"/>
  <path d="M0 16 a16 16 0 0 1 16 -16 H{W - 16} a16 16 0 0 1 16 16 V44 H0 z" fill="{PANEL}"/>
  <line x1="0" y1="44" x2="{W}" y2="44" stroke="{CURRENT}"/>
  <circle cx="24" cy="22" r="6" fill="{TL_RED}"/><circle cx="42" cy="22" r="6" fill="{TL_YELLOW}"/><circle cx="60" cy="22" r="6" fill="{TL_GREEN}"/>
  <text x="84" y="27" font-family="JetBrains Mono" font-size="14" fill="{MUTED}">~/skills</text>
  {"".join(parts)}
  <rect x=".6" y=".6" width="{W - 1.2}" height="{H - 1.2}" rx="15.4" fill="none" stroke="{CURRENT}" stroke-width="1.2"/>
</svg>
'''
    out = ROOT / "assets" / "skills.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
