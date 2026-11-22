"""Generate the light and dark profile banners from one template.

    python tools/make_banner.py   (run from the repo root)

Writes assets/banner-dark.svg and banner-light.svg.
Edit THEMES or LINES here, never the SVGs by hand, so the two stay in sync.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0B1220", panel="#111A2E", rule="#1E293B", grid="#1A2438",
                 text="#E6EDF7", muted="#8B9BB4", accent="#2DD4BF", warm="#F5B544"),
    "light": dict(bg="#F7F9FC", panel="#FFFFFF", rule="#DCE3EC", grid="#E6ECF3",
                  text="#0F172A", muted="#516079", accent="#0F766E", warm="#B45309"),
}

# Rotating terminal lines. Each one is a real thing in the public repos.
LINES = [
    "django-rest api  ·  jwt auth, boards, cards, attachments",
    "keras transfer learning  ·  4 cnn models on brain mri",
    "react native + expo  ·  bilingual en/ar apps with rtl",
    "node + github actions  ·  tested content pipeline",
]

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

W, H = 1280, 340
CYCLE = 3.5 * len(LINES)  # seconds for a full rotation


def graph(c):
    """A small agent/tool graph on the right: one orchestrator, four tools."""
    hub = (1040, 170)
    nodes = [(930, 92), (1160, 96), (920, 252), (1166, 246)]
    labels = ["api", "db", "model", "tools"]
    parts = []
    for i, (x, y) in enumerate(nodes):
        d = f"M{hub[0]},{hub[1]} L{x},{y}"
        parts.append(f'<path d="{d}" stroke="{c["rule"]}" stroke-width="2" fill="none"/>')
        parts.append(f'<path class="flow f{i}" d="{d}" stroke="{c["accent"]}" stroke-width="2" '
                     f'fill="none" stroke-dasharray="10 220" stroke-linecap="round"/>')
    for (x, y), lab in zip(nodes, labels):
        parts.append(f'<rect x="{x-38}" y="{y-17}" width="76" height="34" rx="8" '
                     f'fill="{c["panel"]}" stroke="{c["rule"]}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="14" fill="{c["muted"]}">{lab}</text>')
    parts.append(f'<circle cx="{hub[0]}" cy="{hub[1]}" r="30" fill="{c["panel"]}" '
                 f'stroke="{c["accent"]}" stroke-width="2"/>')
    parts.append(f'<circle class="pulse" cx="{hub[0]}" cy="{hub[1]}" r="30" fill="none" '
                 f'stroke="{c["accent"]}" stroke-width="2"/>')
    parts.append(f'<text x="{hub[0]}" y="{hub[1]+6}" text-anchor="middle" font-family="{MONO}" '
                 f'font-size="16" font-weight="600" fill="{c["accent"]}">py</text>')
    return "\n    ".join(parts)


def lines(c):
    out = []
    for i, text in enumerate(LINES):
        out.append(f'<text class="ln l{i}" x="106" y="263" font-family="{MONO}" font-size="20" '
                   f'fill="{c["text"]}">{text}</text>')
    return "\n    ".join(out)


def css(c):
    n = len(LINES)
    slot = 100 / n
    rules = [
        # Line i owns its slot: quick fade in, hold, fade out before the slot
        # ends, so two lines are never on screen together. Negative delays
        # start every line mid-cycle; .l0 stays visible if animations never run.
        f"@keyframes rot {{ 0% {{opacity:0}} 1.5% {{opacity:1}} {slot-2.5:.2f}% {{opacity:1}} "
        f"{slot-1:.2f}% {{opacity:0}} 100% {{opacity:0}} }}",
        ".ln { opacity:0; animation: rot %.1fs linear infinite; } .l0 { opacity:1; }" % CYCLE,
    ]
    for i in range(n):
        rules.append(f".l{i} {{ animation-delay: {i * CYCLE / n - (CYCLE if i else 0):.2f}s; }}")
    rules += [
        "@keyframes flow { from { stroke-dashoffset: 230 } to { stroke-dashoffset: 0 } }",
        ".flow { animation: flow 2.8s linear infinite; }",
        ".f1 { animation-delay: .7s } .f2 { animation-delay: 1.4s } .f3 { animation-delay: 2.1s }",
        "@keyframes pulse { 0% { r:30; opacity:.7 } 100% { r:52; opacity:0 } }",
        ".pulse { animation: pulse 2.8s ease-out infinite; }",
        # Motion off: show the first line, keep everything still.
        "@media (prefers-reduced-motion: reduce) {"
        " .ln,.flow,.pulse { animation:none } .l0 { opacity:1 } .flow,.pulse { opacity:0 } }",
    ]
    return "\n      ".join(rules)


def svg(name, c):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Hani Mustafa Hashmi — Software Engineer and Product Developer</title>
  <desc id="d">Software engineer and product developer in Riyadh. Python at the core, AI at the edge, products that ship.</desc>
  <defs>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="{c["grid"]}"/>
    </pattern>
    <linearGradient id="fade" x1="0" x2="1">
      <stop offset="0" stop-color="{c["bg"]}" stop-opacity="1"/>
      <stop offset=".55" stop-color="{c["bg"]}" stop-opacity=".85"/>
      <stop offset="1" stop-color="{c["bg"]}" stop-opacity="0"/>
    </linearGradient>
    <style>
      {css(c)}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="18" fill="{c["bg"]}"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
  <rect width="900" height="{H}" rx="18" fill="url(#fade)"/>
  <rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="17.5" fill="none" stroke="{c["rule"]}" stroke-width="1.5"/>

  <rect x="72" y="66" width="4" height="96" rx="2" fill="{c["accent"]}"/>
  <text x="96" y="96" font-family="{MONO}" font-size="17" letter-spacing="3" fill="{c["muted"]}">SOFTWARE ENGINEER  ·  PRODUCT DEVELOPER  ·  RIYADH</text>
  <text x="94" y="152" font-family="{SANS}" font-size="54" font-weight="700" letter-spacing="-1" fill="{c["text"]}">Hani Mustafa Hashmi</text>
  <text x="96" y="196" font-family="{SANS}" font-size="25" fill="{c["muted"]}">Python at the core. <tspan fill="{c["accent"]}" font-weight="600">AI</tspan> at the edge. <tspan fill="{c["text"]}" font-weight="600">Products that ship.</tspan></text>

  <rect x="72" y="230" width="680" height="48" rx="10" fill="{c["panel"]}" stroke="{c["rule"]}" stroke-width="1.5"/>
  <text x="88" y="263" font-family="{MONO}" font-size="20" fill="{c["warm"]}">›</text>
  <g>
    {lines(c)}
  </g>

  <g>
    {graph(c)}
  </g>
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, c in THEMES.items():
        (OUT / f"banner-{name}.svg").write_text(svg(name, c), encoding="utf-8")
        print("wrote", OUT / f"banner-{name}.svg")
