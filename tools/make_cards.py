"""Generate the project cards (light + dark) shown in the profile README.

    python tools/make_cards.py   (run from the repo root)

Every number on a card comes from the project's own repository: test files,
routers, migrations, notebook logs. Update PROJECTS here and re-run; never edit
the SVGs by hand.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "cards"

THEMES = {
    "dark": dict(bg="#0B1220", panel="#111A2E", rule="#22304A", text="#E6EDF7",
                 muted="#8B9BB4", accent="#2DD4BF", warm="#F5B544", chip="#16223A"),
    "light": dict(bg="#FFFFFF", panel="#F4F7FB", rule="#DCE3EC", text="#0F172A",
                  muted="#516079", accent="#0F766E", warm="#B45309", chip="#EEF2F7"),
}

PROJECTS = [
    dict(slug="motorek", kicker="BACKEND · DJANGO", status="PRIVATE · PRODUCTION",
         title="Motorek",
         desc="Backend for an on-demand oil-change service: bookings and scheduling, payments, rider dispatch, inventory and notifications.",
         metrics=[("10", "Django apps"), ("75", "test modules"), ("JWT+OTP", "auth")],
         chips=["Django", "DRF", "Redis", "SimpleJWT", "django-otp"]),
    dict(slug="awn-care", kicker="FULL-STACK · TYPESCRIPT", status="PRIVATE · PRODUCTION",
         title="Awn Care",
         desc="Hospital companion booking: an Expo mobile app and admin panel on a typed tRPC API over PostgreSQL, with an outbox for reliable events.",
         metrics=[("22", "API routers"), ("32", "DB migrations"), ("E2E", "tested")],
         chips=["Expo Router", "tRPC", "Drizzle", "PostgreSQL", "Zod"]),
    dict(slug="zatca", kicker="DESKTOP · COMPLIANCE", status="PRIVATE · PRODUCTION",
         title="ZATCA E-Invoicing",
         desc="Saudi ZATCA Phase 2 e-invoicing on one Windows PC with no server. Onboarding runs against the live sandbox: CSR, then a compliance CSID, then a production CSID.",
         metrics=[("Phase 2", "compliant"), ("0", "servers"), ("Unit+E2E", "tests")],
         chips=["Electron", "React", "TypeScript", "SQLite", "Vitest"]),
    dict(slug="perfect-house", kicker="MOBILE · EXPO", status="LIVE",
         title="The Perfect House",
         desc="Bilingual app for a Riyadh architecture and interior design firm: portfolio galleries, services and furniture supply, with full Arabic RTL.",
         metrics=[("EN/AR", "with RTL"), ("iOS+Android", "and web"), ("2", "themes")],
         chips=["Expo", "React Native", "TypeScript"]),
    dict(slug="taskio", kicker="FULL-STACK · PYTHON", status="OPEN SOURCE",
         title="Taskio",
         desc="Kanban workspace on a Django REST API: boards, cards, checklists, attachments, member roles and notifications, with a React 19 client.",
         metrics=[("10", "data models"), ("22", "API endpoints"), ("JWT", "auth")],
         chips=["Django", "DRF", "React 19", "PostgreSQL"]),
    dict(slug="brain-tumor", kicker="AI · DEEP LEARNING", status="OPEN SOURCE",
         title="Brain Tumor Detection",
         desc="Final-year project: a custom CNN, VGG16, InceptionV3 and ResNet trained to classify brain MRI scans into four classes, served by Flask.",
         metrics=[("99.1%", "val accuracy"), ("4", "models"), ("4", "tumor classes")],
         chips=["TensorFlow", "Keras", "Flask", "Transfer learning"]),
    dict(slug="mutmainnah", kicker="AUTOMATION · CI/CD", status="OPEN SOURCE",
         title="Mutma'innah Feed",
         desc="Arabic and Urdu text files go through a tested parser into a JSON feed. CI blocks bad content before it deploys to GitHub Pages.",
         metrics=[("466", "line parser"), ("217", "lines of tests"), ("Auto", "deploy")],
         chips=["Node.js", "GitHub Actions", "GitHub Pages"]),
    dict(slug="voicedrop", kicker="BACKEND · FLASK", status="OPEN SOURCE",
         title="VoiceDrop",
         desc="Call-center QA app: agents upload call recordings, QA reviews them, and admins manage teams and users through role-based access.",
         metrics=[("3", "user roles"), ("18", "routes"), ("Audio", "uploads")],
         chips=["Flask", "PostgreSQL", "Jinja"]),
]

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
W, H = 620, 300


def wrap(text, width_px, size):
    """Greedy wrap using an average glyph width; good enough for system sans."""
    per_line = int(width_px / (size * 0.45))
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > per_line and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    lines.append(cur)
    return lines


def chip_w(label, size=13):
    return int(len(label) * size * 0.62) + 22


def card(p, c):
    e = escape
    parts = []
    status_w = chip_w(p["status"], 11) + 6
    live = p["status"] in ("LIVE",) or "PRODUCTION" in p["status"]
    status_col = c["warm"] if live else c["accent"]
    parts.append(f'<rect x="{W-28-status_w}" y="26" width="{status_w}" height="24" rx="12" fill="none" '
                 f'stroke="{status_col}" stroke-width="1.3"/>')
    parts.append(f'<circle cx="{W-28-status_w+14}" cy="38" r="3.5" fill="{status_col}"/>')
    parts.append(f'<text x="{W-28-status_w+24}" y="42.5" font-family="{MONO}" font-size="11" '
                 f'letter-spacing=".5" fill="{status_col}">{e(p["status"])}</text>')
    parts.append(f'<text x="28" y="43" font-family="{MONO}" font-size="12.5" letter-spacing="1.5" '
                 f'fill="{c["accent"]}">{e(p["kicker"])}</text>')
    parts.append(f'<text x="28" y="84" font-family="{SANS}" font-size="32" font-weight="700" '
                 f'letter-spacing="-.5" fill="{c["text"]}">{e(p["title"])}</text>')
    y = 113
    for line in wrap(p["desc"], W - 56, 17)[:3]:
        parts.append(f'<text x="28" y="{y}" font-family="{SANS}" font-size="17" fill="{c["muted"]}">{e(line)}</text>')
        y += 22
    # metrics strip
    my = 186
    parts.append(f'<rect x="28" y="{my}" width="{W-56}" height="56" rx="10" fill="{c["panel"]}" '
                 f'stroke="{c["rule"]}" stroke-width="1"/>')
    colw = (W - 56) / len(p["metrics"])
    for i, (num, lab) in enumerate(p["metrics"]):
        x = 28 + colw * i + 16
        if i:
            parts.append(f'<line x1="{28+colw*i}" y1="{my+12}" x2="{28+colw*i}" y2="{my+44}" stroke="{c["rule"]}"/>')
        parts.append(f'<text x="{x}" y="{my+26}" font-family="{SANS}" font-size="21" font-weight="700" '
                     f'fill="{c["text"]}">{e(num)}</text>')
        parts.append(f'<text x="{x}" y="{my+45}" font-family="{MONO}" font-size="12.5" fill="{c["muted"]}">{e(lab)}</text>')
    # chips
    x, cy = 28, 256
    for ch in p["chips"]:
        w = chip_w(ch)
        if x + w > W - 28:
            break
        parts.append(f'<rect x="{x}" y="{cy}" width="{w}" height="26" rx="6" fill="{c["chip"]}" '
                     f'stroke="{c["rule"]}" stroke-width="1"/>')
        parts.append(f'<text x="{x + w/2}" y="{cy+17.5}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="13" fill="{c["text"]}">{e(ch)}</text>')
        x += w + 8
    body = "\n  ".join(parts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">{e(p["title"])}</title>
  <desc id="d">{e(p["kicker"].title())}. {e(p["desc"])} {e(", ".join(n + " " + l for n, l in p["metrics"]))}.</desc>
  <rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="16" fill="{c["bg"]}" stroke="{c["rule"]}" stroke-width="1.5"/>
  <rect x="28" y="0.75" width="56" height="3" rx="1.5" fill="{c["accent"]}"/>
  {body}
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for p in PROJECTS:
        for name, c in THEMES.items():
            (OUT / f'{p["slug"]}-{name}.svg').write_text(card(p, c), encoding="utf-8")
    print(f"wrote {len(PROJECTS) * len(THEMES)} cards to {OUT}")
