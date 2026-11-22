"""Generate the tech-stack badge wall (assets/stack.svg).

    python tools/make_stack.py   (run from the repo root)

Brand-coloured pills with white logos, grouped by area, inside the same Gold
window as the banner and stats. Logos are Simple Icons (CC0), with Devicon
(MIT) as a fallback; both are fetched once, cached in tools/icons/, and
embedded, so the image needs nothing from the network.
"""
import base64
import re
import time
import urllib.request
from html import escape
from pathlib import Path

from make_banner import (BG, PANEL, CURRENT, MUTED, COMMENT, GOLD,
                         TL_RED, TL_YELLOW, TL_GREEN, font_face)

ROOT = Path(__file__).resolve().parent.parent
ICONS = Path(__file__).resolve().parent / "icons"
SIMPLE_ICONS = "13.21.0"
DEVICON = "2.16.0"
DARK_TEXT = "#121212"

# group -> [(label, simple-icons slug or "devicon:<path>", pill colour, text colour)]
GROUPS = [
    ("backend", [
        ("Python", "python", "#3776AB", None), ("Django", "django", "#0C4B33", None),
        ("Django REST", "django", "#A30000", None), ("Flask", "flask", "#2B2B2B", None),
        ("Node.js", "nodedotjs", "#339933", None), ("Express", "express", "#2B2B2B", None),
        ("tRPC", "trpc", "#2596BE", None)]),
    ("ai_ml", [
        ("TensorFlow", "tensorflow", "#FF6F00", None), ("Keras", "keras", "#D00000", None),
        ("NumPy", "numpy", "#013243", None), ("Jupyter", "jupyter", "#F37626", None)]),
    ("databases", [
        ("PostgreSQL", "postgresql", "#4169E1", None), ("MySQL", "mysql", "#4479A1", None),
        ("MongoDB", "mongodb", "#47A248", None), ("Redis", "redis", "#DC382D", None),
        ("SQLite", "sqlite", "#003B57", None), ("Firebase", "firebase", "#DD2C00", None),
        ("Drizzle", "drizzle", "#C5F74F", DARK_TEXT)]),
    ("frontend", [
        ("TypeScript", "typescript", "#3178C6", None), ("JavaScript", "javascript", "#F7DF1E", DARK_TEXT),
        ("React", "react", "#1F2A37", "#61DAFB"), ("Next.js", "nextdotjs", "#2B2B2B", None),
        ("Angular", "angular", "#DD0031", None), ("Tailwind CSS", "tailwindcss", "#0F766E", None),
        ("Redux", "redux", "#764ABC", None), ("HTML", "html5", "#E34F26", None),
        ("CSS", "css3", "#1572B6", None)]),
    ("mobile_desktop", [
        ("React Native", "react", "#1F2A37", "#61DAFB"), ("Expo", "expo", "#2B2B2B", None),
        ("Electron", "electron", "#47848F", None)]),
    ("devops_tools", [
        ("Git", "git", "#F05032", None), ("GitHub", "github", "#2B2B2B", None),
        ("GitHub Actions", "githubactions", "#2088FF", None), ("Docker", "docker", "#2496ED", None),
        ("AWS", "amazonwebservices", "#FF9900", DARK_TEXT), ("Vercel", "vercel", "#2B2B2B", None),
        ("Nginx", "nginx", "#009639", None), ("Gunicorn", "gunicorn", "#499848", None),
        ("Linux", "linux", "#FCC624", DARK_TEXT), ("VS Code", "devicon:vscode/vscode-original", "#007ACC", None),
        ("NPM", "npm", "#CB3837", None), ("Selenium", "selenium", "#43B02A", None)]),
]

W, PAD, LABEL_W = 1280, 36, 200
PH, PGAP, RGAP, FS = 42, 10, 12, 15


def fetch(urls):
    last = None
    for attempt in range(3):
        for u in urls:
            try:
                data = urllib.request.urlopen(u, timeout=40).read()
                if b"<svg" in data:
                    return data
            except Exception as e:
                last = e
        time.sleep(2)
    raise SystemExit(f"could not fetch {urls[0]}: {last}")


def logo(slug):
    """Return (href, needs_whitening). Simple Icons are single-path, so they're
    recoloured directly; Devicon files are multi-colour and get a white filter."""
    ICONS.mkdir(exist_ok=True)
    if slug.startswith("devicon:"):
        path = slug.split(":", 1)[1]
        cached = ICONS / (path.split("/")[-1] + ".svg")
        if not cached.exists():
            cached.write_bytes(fetch([f"https://cdn.jsdelivr.net/npm/devicon@{DEVICON}/icons/{path}.svg",
                                      f"https://unpkg.com/devicon@{DEVICON}/icons/{path}.svg"]))
        return "data:image/svg+xml;base64," + base64.b64encode(cached.read_bytes()).decode(), True
    cached = ICONS / f"si-{slug}.svg"
    if not cached.exists():
        cached.write_bytes(fetch([f"https://cdn.jsdelivr.net/npm/simple-icons@{SIMPLE_ICONS}/icons/{slug}.svg",
                                  f"https://unpkg.com/simple-icons@{SIMPLE_ICONS}/icons/{slug}.svg"]))
    path = re.search(rb'<path d="([^"]+)"', cached.read_bytes()).group(1).decode()
    return path, False


def text_w(s):
    # Poppins 600 average advance is about 0.6 em; narrow glyphs bring it down
    narrow = sum(1 for ch in s if ch in "iljtfrI.() ")
    return FS * (0.62 * (len(s) - narrow) + 0.32 * narrow)


def pill(x, y, label, slug, bg, fg):
    fg = fg or "#FFFFFF"
    icon_fill = fg
    w = 14 + 20 + 9 + text_w(label) + 16
    href, is_image = logo(slug)
    if is_image:
        mark = f'<image x="{x + 14}" y="{y + 11}" width="20" height="20" href="{href}" filter="url(#white)"/>'
    else:
        mark = (f'<svg x="{x + 14}" y="{y + 11}" width="20" height="20" viewBox="0 0 24 24">'
                f'<path d="{href}" fill="{icon_fill}"/></svg>')
    edge = ' stroke="#3A3A3A" stroke-width="1.2"' if bg in ("#2B2B2B", "#1F2A37", "#013243", "#003B57") else ""
    return (f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{PH}" rx="10" fill="{bg}"{edge}/>'
            f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{PH / 2}" rx="10" fill="#FFFFFF" opacity=".07"/>'
            + mark +
            f'<text x="{x + 43}" y="{y + 26.5}" font-family="Poppins" font-weight="600" font-size="{FS}" '
            f'fill="{fg}">{escape(label)}</text>'), w


def main():
    parts, y = [], 44 + 30
    x_start, x_end = PAD + LABEL_W, W - PAD
    for gi, (group, items) in enumerate(GROUPS):
        if gi:
            parts.append(f'<line x1="{PAD}" y1="{y - RGAP - 4}" x2="{W - PAD}" y2="{y - RGAP - 4}" '
                         f'stroke="{CURRENT}" stroke-dasharray="2 6"/>')
        parts.append(f'<text x="{PAD}" y="{y + 27}" font-family="JetBrains Mono" font-size="15" fill="{GOLD}">'
                     f'{escape(group)}<tspan fill="{COMMENT}">:</tspan></text>')
        parts.append(f'<text x="{PAD}" y="{y + 46}" font-family="JetBrains Mono" font-size="12" fill="{COMMENT}">'
                     f'// {len(items)}</text>')
        x = x_start
        for label, slug, bg, fg in items:
            _, w = pill(0, 0, label, slug, bg, fg)
            if x + w > x_end:
                x, y = x_start, y + PH + PGAP
            svg, w = pill(x, y, label, slug, bg, fg)
            parts.append(svg)
            x += w + PGAP
        y += PH + RGAP * 2 + 8
    H = int(y + 6)
    total = sum(len(i) for _, i in GROUPS)

    names = "".join(l for _, items in GROUPS for l, *_ in items)
    mono = "".join(g for g, _ in GROUPS) + ":// 0123456789~/stack technologies"
    fonts = "".join([font_face("Poppins", 600, names), font_face("JetBrains Mono", 400, mono)])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Tech stack</title>
  <desc id="d">{escape("; ".join(g + ": " + ", ".join(l for l, *_ in items) for g, items in GROUPS))}.</desc>
  <defs>
    <style>{fonts}</style>
    <filter id="white"><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BG}"/>
  <path d="M0 16 a16 16 0 0 1 16 -16 H{W - 16} a16 16 0 0 1 16 16 V44 H0 z" fill="{PANEL}"/>
  <line x1="0" y1="44" x2="{W}" y2="44" stroke="{CURRENT}"/>
  <circle cx="24" cy="22" r="6" fill="{TL_RED}"/><circle cx="42" cy="22" r="6" fill="{TL_YELLOW}"/><circle cx="60" cy="22" r="6" fill="{TL_GREEN}"/>
  <text x="84" y="27" font-family="JetBrains Mono" font-size="14" fill="{MUTED}">~/stack</text>
  <text x="{W - 20}" y="27" text-anchor="end" font-family="JetBrains Mono" font-size="12" fill="{COMMENT}">{total} technologies</text>
  {"".join(parts)}
  <rect x=".6" y=".6" width="{W - 1.2}" height="{H - 1.2}" rx="15.4" fill="none" stroke="{CURRENT}" stroke-width="1.2"/>
</svg>
'''
    out = ROOT / "assets" / "stack.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB, {total} technologies, height {H})")


if __name__ == "__main__":
    main()
