"""Generate the profile banner in the visual language of hanihashmi.vercel.app.

    python tools/make_banner.py            (run from the repo root)

Gold theme, Poppins + JetBrains Mono, a `hani.ts` editor window and a
VS Code-style status bar: the same identity as the portfolio.

Images in a GitHub README can't load web fonts, so the two fonts are embedded
as base64 subsets that hold only the glyphs this banner uses. Google Fonts
builds those subsets (`&text=`). They are cached in tools/fonts/ after the
first run, so later runs work offline.

The typing animation uses SMIL (<animate>) because it runs inside <img> in
every major browser. Without animation the first line stays visible.
"""
import base64
import hashlib
import re
import urllib.parse
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "banner.svg"
FONT_CACHE = Path(__file__).resolve().parent / "fonts"

# The portfolio's "Gold" theme (hanihashmi.vercel.app, default scheme)
BG, PANEL, LINE, CURRENT = "#121212", "#171717", "#1E1E1F", "#383838"
STATUS_BG, LINENO = "#0E0E0E", "#494C51"
FG, MUTED, COMMENT = "#FFFFFF", "#9CA3AF", "#7A7F88"
GOLD, OK = "#FFDB70", "#22C55E"
KEYWORD, PROP, STRING, BOOL = "#C084FC", "#60A5FA", "#86EFAC", "#F97316"
TL_RED, TL_YELLOW, TL_GREEN = "#FF5F57", "#FEBC2E", "#28C840"
PURPLE = GOLD  # accent slot

W, H = 1280, 440
MONO_ADV = 0.6  # JetBrains Mono advance width, in em

# What the typing line cycles through. Keep each one true.
TYPED = [
    "Product Developer",
    "Python · Django · REST APIs",
    "React Native · EN/AR with RTL",
    "Deep learning → agentic AI",
]
TAGLINE = ("Python at the core. ", ("AI", PURPLE), " at the edge. ", ("Products that ship.", FG))

# hani.ts, as (text, colour) tokens per line
K, S, P, C, N, T = KEYWORD, STRING, PROP, COMMENT, FG, BOOL
CODE = [
    [("const ", K), ("hani", N), (" = {", N)],
    [("  role", P), (": ", N), ("'Product Developer'", S), (",", N)],
    [("  base", P), (": ", N), ("'Riyadh, Saudi Arabia'", S), (",", N)],
    [("  stack", P), (": [", N), ("'Python'", S), (", ", N), ("'Django'", S), (",", N)],
    [("          ", N), ("'React Native'", S), (", ", N), ("'Next.js'", S), ("],", N)],
    [("  ai", P), (": [", N), ("'TensorFlow'", S), (", ", N), ("'LLM agents'", S), ("],", N)],
    [("  i18n", P), (": [", N), ("'en'", S), (", ", N), ("'ar'", S), ("], ", N), ("// RTL ready", C)],
    [("  shipping", P), (": ", N), ("true", T), (",", N)],
    [("};", N)],
    [],
    [("export default ", K), ("hani", N), (";", N)],
]

MONO_TEXTS = (["// Hello World, I'm", "> ", "hani.ts", "haniHashmi();", "~/github",
               "main", "open to work", "Riyadh, Saudi Arabia", "UTF-8", "EN", "TypeScript",
               "$ whoami", "0123456789"] + TYPED
              + ["".join(t for t, _ in line) for line in CODE])
SANS_TEXTS = ["Hani Hashmi"] + [t if isinstance(t, str) else t[0] for t in TAGLINE]


def font_face(family, weight, text):
    """Return a base64 woff2 subset of `family` covering `text`, cached on disk."""
    FONT_CACHE.mkdir(exist_ok=True)
    chars = "".join(sorted(set(text)))
    key = re.sub(r"\W", "", family) + f"-{weight}-" + hashlib.sha1(chars.encode()).hexdigest()[:8]
    cached = FONT_CACHE / f"{key}.woff2"
    if not cached.exists():
        for old in FONT_CACHE.glob(re.sub(r"\W", "", family) + f"-{weight}-*.woff2"):
            old.unlink()
        q = urllib.parse.urlencode({"family": f"{family}:wght@{weight}", "text": chars})
        req = urllib.request.Request(f"https://fonts.googleapis.com/css2?{q}",
                                     headers={"User-Agent": "Mozilla/5.0 Chrome/120"})
        css = urllib.request.urlopen(req, timeout=30).read().decode()
        url = re.search(r"url\((https://[^)]+)\)", css).group(1)
        cached.write_bytes(urllib.request.urlopen(url, timeout=30).read())
    data = base64.b64encode(cached.read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def mono_w(text, size):
    return len(text) * size * MONO_ADV


def typing(x, y, size):
    """Typewriter: each line types, holds, deletes; a block cursor follows."""
    per, type_t, hold_t, del_t = 4.2, 1.3, 2.1, 0.5
    total = per * len(TYPED)
    out, cursor_vals, cursor_times = [], [], []
    for i, text in enumerate(TYPED):
        n = len(text)
        frames = []  # (time, visible chars)
        t0 = i * per
        frames.append((0, 0))
        for k in range(n + 1):
            frames.append((t0 + type_t * k / n, k))
        frames.append((t0 + type_t + hold_t, n))
        for k in range(n - 1, -1, -1):
            frames.append((t0 + type_t + hold_t + del_t * (n - k) / n, k))
        frames = sorted({round(t, 3): c for t, c in frames}.items())
        times = ";".join(f"{t / total:.4f}" for t, _ in frames)
        widths = ";".join(f"{c * size * MONO_ADV:.1f}" for _, c in frames)
        start_w = mono_w(text, size) if i == 0 else 0
        out.append(
            f'<clipPath id="tc{i}"><rect x="{x}" y="{y - size}" width="{start_w:.1f}" height="{size * 1.4}">'
            f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="{times}" values="{widths}"/></rect></clipPath>'
            f'<text clip-path="url(#tc{i})" x="{x}" y="{y}" font-family="JetBrains Mono" font-size="{size}" '
            f'fill="{FG}">{escape(text)}</text>')
        for t, c in frames:
            if t >= t0 or i == 0:
                cursor_times.append(t)
                cursor_vals.append(x + c * size * MONO_ADV + 2)
    pairs = sorted(dict(zip(cursor_times, cursor_vals)).items())
    if pairs[0][0] != 0:
        pairs.insert(0, (0, x + 2))
    ct = ";".join(f"{t / total:.4f}" for t, _ in pairs)
    cv = ";".join(f"{v:.1f}" for _, v in pairs)
    first_x = x + mono_w(TYPED[0], size) + 2
    out.append(
        f'<rect x="{first_x:.1f}" y="{y - size * 0.82:.1f}" width="{size * 0.55:.1f}" height="{size * 1.02:.1f}" fill="{PURPLE}">'
        f'<animate attributeName="x" dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{ct}" values="{cv}"/>'
        f'<animate attributeName="opacity" dur="1.05s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5" values="1;0"/>'
        f'</rect>')
    return "\n  ".join(out)


def tagline(x, y, size):
    spans = []
    for part in TAGLINE:
        if isinstance(part, str):
            spans.append(escape(part))
        else:
            spans.append(f'<tspan fill="{part[1]}" font-weight="600">{escape(part[0])}</tspan>')
    return (f'<text x="{x}" y="{y}" font-family="Poppins" font-size="{size}" fill="{MUTED}">'
            + "".join(spans) + "</text>")


def editor(x, y, w, h):
    size, lh = 16, 24
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{PANEL}" stroke="{CURRENT}" stroke-width="1.2"/>',
        f'<path d="M{x} {y + 14} a14 14 0 0 1 14 -14 h{w - 28} a14 14 0 0 1 14 14 v28 h-{w} z" fill="{BG}"/>',
        f'<line x1="{x}" y1="{y + 42}" x2="{x + w}" y2="{y + 42}" stroke="{CURRENT}"/>',
    ]
    for i, col in enumerate((TL_RED, TL_YELLOW, TL_GREEN)):
        out.append(f'<circle cx="{x + 22 + i * 18}" cy="{y + 21}" r="6" fill="{col}"/>')
    out.append(f'<text x="{x + 88}" y="{y + 26}" font-family="JetBrains Mono" font-size="13" fill="{MUTED}">hani.ts</text>')
    out.append(f'<text x="{x + w - 18}" y="{y + 26}" text-anchor="end" font-family="JetBrains Mono" font-size="12" fill="{COMMENT}">TypeScript</text>')
    ty = y + 42 + 30
    for n, line in enumerate(CODE, start=1):
        out.append(f'<text x="{x + 34}" y="{ty}" text-anchor="end" font-family="JetBrains Mono" font-size="{size - 2}" fill="{LINENO}">{n}</text>')
        if line:
            spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in line)
            out.append(f'<text x="{x + 50}" y="{ty}" font-family="JetBrains Mono" font-size="{size}" xml:space="preserve">{spans}</text>')
        ty += lh
    return "\n  ".join(out)


def status_bar():
    y = H - 30
    return "\n  ".join([
        f'<path d="M0 {y} H{W} V{H - 16} a16 16 0 0 1 -16 16 H16 a16 16 0 0 1 -16 -16 z" fill="{STATUS_BG}"/>',
        f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{CURRENT}"/>',
        f'<text x="22" y="{y + 20}" font-family="JetBrains Mono" font-size="13" fill="{PURPLE}">⎇ main</text>',
        f'<circle cx="104" cy="{y + 15}" r="4" fill="{OK}"><animate attributeName="opacity" dur="2.4s" repeatCount="indefinite" values="1;.35;1"/></circle>',
        f'<text x="114" y="{y + 20}" font-family="JetBrains Mono" font-size="13" fill="{MUTED}">open to work</text>',
        f'<text x="{W - 22}" y="{y + 20}" text-anchor="end" font-family="JetBrains Mono" font-size="13" fill="{COMMENT}" xml:space="preserve">Riyadh, Saudi Arabia   UTF-8   EN</text>',
    ])


def svg():
    styles = "".join([
        font_face("Poppins", 400, "".join(SANS_TEXTS)),
        font_face("Poppins", 600, "".join(SANS_TEXTS)),
        font_face("Poppins", 700, "Hani Hashmi"),
        font_face("JetBrains Mono", 400, "".join(MONO_TEXTS) + "⎇"),
        font_face("JetBrains Mono", 700, "haniHashmi();"),
    ])
    lx = 64
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Hani Mustafa Hashmi — Software Engineer and Product Developer</title>
  <desc id="d">Software engineer and product developer in Riyadh. Python at the core, AI at the edge, products that ship.</desc>
  <defs>
    <style>{styles}</style>
    <radialGradient id="glow" cx=".78" cy=".42" r=".55">
      <stop offset="0" stop-color="{GOLD}" stop-opacity=".10"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{LINE}" stroke-width=".6"/>
    </pattern>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#000" flood-opacity=".45"/>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" rx="16" fill="{BG}"/>
  <rect width="{W}" height="{H}" rx="16" fill="url(#grid)" opacity=".55"/>
  <rect width="{W}" height="{H}" rx="16" fill="url(#glow)"/>

  <text x="{lx - 2}" y="44" font-family="JetBrains Mono" font-weight="700" font-size="15" fill="{PURPLE}">haniHashmi();</text>
  <text x="{lx + 128}" y="44" font-family="JetBrains Mono" font-size="13" fill="{COMMENT}">~/github</text>

  <text x="{lx}" y="128" font-family="JetBrains Mono" font-size="18" fill="{PURPLE}">// Hello World, I'm</text>
  <text x="{lx - 4}" y="214" font-family="Poppins" font-weight="700" font-size="88" letter-spacing="-2" fill="{FG}">Hani Hashmi</text>

  <text x="{lx}" y="272" font-family="JetBrains Mono" font-size="26" fill="{PURPLE}">&gt;</text>
  {typing(lx + 30, 272, 26)}

  {tagline(lx, 326, 21)}

  <circle cx="{lx + 7}" cy="{366}" r="6.5" fill="none" stroke="{COMMENT}" stroke-width="1.6"/>
  <circle cx="{lx + 7}" cy="{366}" r="2" fill="{COMMENT}"/>
  <text x="{lx + 22}" y="371" font-family="JetBrains Mono" font-size="15" fill="{MUTED}">Riyadh, Saudi Arabia</text>

  <g filter="url(#shadow)">
  {editor(752, 62, 468, 336)}
  </g>

  {status_bar()}
  <rect x=".6" y=".6" width="{W - 1.2}" height="{H - 1.2}" rx="15.4" fill="none" stroke="{CURRENT}" stroke-width="1.2"/>
</svg>
'''


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg(), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
