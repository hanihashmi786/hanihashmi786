"""Print the Tech stack section of the README as shields.io badges.

    python tools/make_badges.py --check   # verify every badge renders its logo
    python tools/make_badges.py           # print the markdown block

Brand-coloured "for-the-badge" badges, grouped and centred. Where shields.io
no longer ships a logo (AWS, VS Code), the logo cached in tools/icons/ is sent
inline as a data URI, so every badge keeps its icon.
"""
import base64
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ICONS = Path(__file__).resolve().parent / "icons"

# (label, logo slug, badge colour, logo colour). A slug starting with "file:"
# uses a cached SVG from tools/icons instead of shields' built-in set.
GROUPS = [
    ("Backend & APIs", [
        ("Python", "python", "3776AB", "FFD43B"), ("Django", "django", "092E20", "white"),
        ("Django REST", "django", "A30000", "white"), ("Flask", "flask", "000000", "white"),
        ("Node.js", "nodedotjs", "339933", "white"), ("Express", "express", "000000", "white"),
        ("tRPC", "trpc", "2596BE", "white")]),
    ("AI & Machine Learning", [
        ("TensorFlow", "tensorflow", "FF6F00", "white"), ("Keras", "keras", "D00000", "white"),
        ("NumPy", "numpy", "013243", "white"), ("Jupyter", "jupyter", "F37626", "white")]),
    ("Databases", [
        ("PostgreSQL", "postgresql", "4169E1", "white"), ("MySQL", "mysql", "4479A1", "white"),
        ("MongoDB", "mongodb", "47A248", "white"), ("Redis", "redis", "DC382D", "white"),
        ("SQLite", "sqlite", "003B57", "white"), ("Firebase", "firebase", "DD2C00", "FFCA28"),
        ("Drizzle", "drizzle", "C5F74F", "black")]),
    ("Frontend", [
        ("TypeScript", "typescript", "3178C6", "white"), ("JavaScript", "javascript", "F7DF1E", "black"),
        ("React", "react", "20232A", "61DAFB"), ("Next.js", "nextdotjs", "000000", "white"),
        ("Angular", "angular", "DD0031", "white"), ("Tailwind CSS", "tailwindcss", "0F172A", "38BDF8"),
        ("Redux", "redux", "764ABC", "white"), ("HTML5", "html5", "E34F26", "white"),
        ("CSS3", "css", "1572B6", "white")]),
    ("Mobile & Desktop", [
        ("React Native", "react", "20232A", "61DAFB"), ("Expo", "expo", "000020", "white"),
        ("Electron", "electron", "47848F", "white")]),
    ("DevOps & Tools", [
        ("Git", "git", "F05032", "white"), ("GitHub", "github", "181717", "white"),
        ("GitHub Actions", "githubactions", "2088FF", "white"), ("Docker", "docker", "2496ED", "white"),
        ("AWS", "file:si-amazonwebservices.svg", "232F3E", "FF9900"), ("Vercel", "vercel", "000000", "white"),
        ("Nginx", "nginx", "009639", "white"), ("Gunicorn", "gunicorn", "499848", "white"),
        ("Linux", "linux", "FCC624", "black"), ("VS Code", "file:vscode-original.svg", "007ACC", "white"),
        ("npm", "npm", "CB3837", "white"), ("Selenium", "selenium", "43B02A", "white")]),
]


def logo_param(slug, colour):
    if not slug.startswith("file:"):
        return f"logo={slug}&logoColor={colour}"
    svg = (ICONS / slug[5:]).read_text(encoding="utf-8")
    m = re.search(r'<path d="([^"]+)"', svg)
    if m and "viewBox=\"0 0 24 24\"" in svg:          # single-path Simple Icon: recolour it
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
               f'<path fill="#{colour}" d="{m.group(1)}"/></svg>')
    data = base64.b64encode(svg.encode()).decode()
    return "logo=" + urllib.parse.quote(f"data:image/svg+xml;base64,{data}", safe="")


def url(label, slug, colour, logo_colour):
    text = label.replace("-", "--").replace("_", "__").replace(" ", "%20")
    return (f"https://img.shields.io/badge/{text}-{colour}?style=for-the-badge&"
            + logo_param(slug, logo_colour))


BADGES = Path(__file__).resolve().parent.parent / "assets" / "badges"


def src(label, slug, colour, logo_colour):
    """Badges with an inline logo make URLs too long for GitHub's image proxy,
    so those are rendered once and committed under assets/badges/."""
    u = url(label, slug, colour, logo_colour)
    if not slug.startswith("file:"):
        return u
    BADGES.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") + ".svg"
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 badge-build"})
    (BADGES / name).write_bytes(urllib.request.urlopen(req, timeout=30).read())
    return f"./assets/badges/{name}"


def markdown():
    out = []
    for title, items in GROUPS:
        badges = "\n".join(f'  <img alt="{l}" src="{src(l, s, c, lc)}">' for l, s, c, lc in items)
        out.append(f'<p align="center">\n  <b>{title.replace("&", "&amp;")}</b><br>\n{badges}\n</p>')
    return "\n\n".join(out)


def check():
    bad = 0
    for _, items in GROUPS:
        for l, s, c, lc in items:
            req = urllib.request.Request(url(l, s, c, lc), headers={"User-Agent": "Mozilla/5.0 badge-check"})
            body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            ok = "<image" in body or "data:image" in body
            bad += not ok
            print(("ok   " if ok else "NO LOGO ") + l)
    total = sum(len(i) for _, i in GROUPS)
    print(f"{total - bad}/{total} badges show a logo")
    return bad == 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    print(markdown())
