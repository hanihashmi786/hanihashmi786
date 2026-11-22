"""Generate the GitHub activity cards in the banner's Gold theme and fonts.

    python tools/make_stats.py           (run from the repo root; needs `gh` logged in)

Writes assets/stats.svg (contributions + streaks) and assets/heatmap.svg
(the last 53 weeks). The data comes from GitHub's GraphQL contribution
calendar for USER. These cards are a snapshot: re-run the script, or let a
scheduled workflow run it, to refresh them.
"""
import datetime as dt
import json
import subprocess
from html import escape
from pathlib import Path

from make_banner import (BG, PANEL, CURRENT, STATUS_BG, FG, MUTED, COMMENT, GOLD, OK,
                         TL_RED, TL_YELLOW, TL_GREEN, font_face)

USER = "hanihashmi786"
ROOT = Path(__file__).resolve().parent.parent
W = 1280
LEVELS = ["#1E1E1F", "#4A3F22", "#8A7233", "#C9A64A", GOLD]  # empty → full gold


def gql(query):
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]


def calendar():
    """Every day since the account was created: [(date, count)], oldest first."""
    u = gql(f'query{{user(login:"{USER}"){{createdAt}}}}')["user"]
    start = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).date()
    today = dt.date.today()
    days, cur = {}, start
    while cur <= today:
        end = min(cur + dt.timedelta(days=364), today)
        q = (f'query{{user(login:"{USER}"){{contributionsCollection(from:"{cur}T00:00:00Z",to:"{end}T23:59:59Z")'
             '{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}')
        weeks = gql(q)["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        for w in weeks:
            for d in w["contributionDays"]:
                day = dt.date.fromisoformat(d["date"])
                if start <= day <= today:
                    days[day] = d["contributionCount"]
        cur = end + dt.timedelta(days=1)
    return sorted(days.items()), start, today


def streaks(days):
    longest, best_end, run = 0, None, 0
    for day, n in days:
        run = run + 1 if n else 0
        if run > longest:
            longest, best_end = run, day
    # current streak may end yesterday if nothing is logged yet today
    cur, i = 0, len(days) - 1
    if days and days[i][1] == 0:
        i -= 1
    end = days[i][0] if i >= 0 else None
    while i >= 0 and days[i][1]:
        cur, i = cur + 1, i - 1
    cur_start = end - dt.timedelta(days=cur - 1) if cur else None
    best_start = best_end - dt.timedelta(days=longest - 1) if longest else None
    return (cur, cur_start, end if cur else None), (longest, best_start, best_end)


def fmt(d):
    return d.strftime("%b %-d, %Y") if hasattr(d, "strftime") and not _win() else d.strftime("%b %d, %Y").replace(" 0", " ")


def _win():
    import os
    return os.name == "nt"


def frame(h, title, body, fonts):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="t">
  <title id="t">{escape(title)}</title>
  <defs><style>{fonts}</style></defs>
  <rect width="{W}" height="{h}" rx="16" fill="{BG}"/>
  <path d="M0 16 a16 16 0 0 1 16 -16 H{W - 16} a16 16 0 0 1 16 16 V44 H0 z" fill="{PANEL}"/>
  <line x1="0" y1="44" x2="{W}" y2="44" stroke="{CURRENT}"/>
  <circle cx="24" cy="22" r="6" fill="{TL_RED}"/><circle cx="42" cy="22" r="6" fill="{TL_YELLOW}"/><circle cx="60" cy="22" r="6" fill="{TL_GREEN}"/>
  <text x="84" y="27" font-family="JetBrains Mono" font-size="14" fill="{MUTED}">{escape(title)}</text>
  {body}
  <rect x=".6" y=".6" width="{W - 1.2}" height="{h - 1.2}" rx="15.4" fill="none" stroke="{CURRENT}" stroke-width="1.2"/>
</svg>
'''


def heat_start(today):
    """First Sunday of the 53-week window GitHub calls "the last year"."""
    start = today - dt.timedelta(days=today.weekday() + 1 + 52 * 7)
    while start.weekday() != 6:
        start -= dt.timedelta(days=1)
    return start


def stats_svg(days, start, today):
    total = sum(n for _, n in days)
    year = sum(n for d, n in days if d >= heat_start(today))
    (cur, cs, ce), (best, bs, be) = streaks(days)
    H = 300
    col = W / 3

    def block(i, value, label, sub, highlight=False):
        cx = col * i + col / 2
        parts = []
        if highlight:
            parts.append(f'<circle cx="{cx}" cy="142" r="56" fill="none" stroke="{CURRENT}" stroke-width="6"/>')
            parts.append(f'<circle cx="{cx}" cy="142" r="56" fill="none" stroke="{GOLD}" stroke-width="6" '
                         f'stroke-linecap="round" stroke-dasharray="300 352" transform="rotate(-90 {cx} 142)"/>')
            parts.append(f'<path d="M{cx} 72 c-9 10 -11 16 -6 22 c-8 -2 -11 -9 -9 -16 c-7 8 -7 19 2 25 '
                         f'c9 6 22 2 24 -9 c2 -9 -3 -15 -11 -22 z" fill="{GOLD}" transform="translate(0 -6) scale(1)"/>')
            vy = 160
        else:
            vy = 158
        parts.append(f'<text x="{cx}" y="{vy}" text-anchor="middle" font-family="Poppins" font-weight="700" '
                     f'font-size="{46 if highlight else 54}" fill="{FG}">{escape(value)}</text>')
        parts.append(f'<text x="{cx}" y="236" text-anchor="middle" font-family="Poppins" font-weight="600" '
                     f'font-size="20" fill="{GOLD if highlight else FG}">{escape(label)}</text>')
        parts.append(f'<text x="{cx}" y="264" text-anchor="middle" font-family="JetBrains Mono" font-size="14" '
                     f'fill="{COMMENT}">{escape(sub)}</text>')
        return "\n  ".join(parts)

    def rng(a, b):
        return f"{fmt(a)} – {fmt(b)}" if a else "—"

    body = "\n  ".join([
        f'<line x1="{col}" y1="90" x2="{col}" y2="260" stroke="{CURRENT}"/>',
        f'<line x1="{col * 2}" y1="90" x2="{col * 2}" y2="260" stroke="{CURRENT}"/>',
        block(0, f"{total:,}", "Total Contributions", f"{fmt(start)} – Present"),
        block(1, str(cur), "Current Streak", rng(cs, ce), highlight=True),
        block(2, str(best), "Longest Streak", rng(bs, be)),
        f'<text x="{W - 20}" y="27" text-anchor="end" font-family="JetBrains Mono" font-size="12" '
        f'fill="{COMMENT}">{year:,} in the last year · updated {today.isoformat()}</text>',
    ])
    return body, H


def heatmap_svg(days, today):
    by_day = dict(days)
    end = today
    start = heat_start(end)
    x0, y0, cell, gap = 84, 96, 18, 4
    step = cell + gap
    peak = max([n for d, n in days if d >= start] + [1])
    rects, months, last_month = [], [], None
    d, col = start, 0
    while d <= end:
        row = (d.weekday() + 1) % 7
        n = by_day.get(d, 0)
        lvl = 0 if n == 0 else min(4, 1 + int(3 * (n - 1) / max(peak - 1, 1) + 0.5) if peak > 1 else 4)
        lvl = max(1, lvl) if n else 0
        rects.append(f'<rect x="{x0 + col * step}" y="{y0 + row * step}" width="{cell}" height="{cell}" rx="4" '
                     f'fill="{LEVELS[lvl]}"><title>{n} contributions on {d.isoformat()}</title></rect>')
        if row == 0 and d.month != last_month and d.day <= 7:
            months.append(f'<text x="{x0 + col * step}" y="{y0 - 14}" font-family="JetBrains Mono" font-size="13" '
                          f'fill="{MUTED}">{d.strftime("%b")}</text>')
            last_month = d.month
        if row == 6:
            col += 1
        d += dt.timedelta(days=1)
    labels = [f'<text x="{x0 - 14}" y="{y0 + r * step + 14}" text-anchor="end" font-family="JetBrains Mono" '
              f'font-size="12" fill="{COMMENT}">{lab}</text>' for r, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri"))]
    H = y0 + 7 * step + 64
    lx = W - 40 - 5 * step - 60
    legend = [f'<text x="{lx - 10}" y="{H - 30}" text-anchor="end" font-family="JetBrains Mono" font-size="12" fill="{COMMENT}">Less</text>']
    legend += [f'<rect x="{lx + i * step}" y="{H - 44}" width="{cell}" height="{cell}" rx="4" fill="{c}"/>' for i, c in enumerate(LEVELS)]
    legend.append(f'<text x="{lx + 5 * step + 6}" y="{H - 30}" font-family="JetBrains Mono" font-size="12" fill="{COMMENT}">More</text>')
    year = sum(n for dd, n in days if dd >= start)
    caption = (f'<text x="{x0}" y="{H - 30}" font-family="JetBrains Mono" font-size="13" fill="{MUTED}">'
               f'<tspan fill="{OK}">$</tspan> git log --since="1 year ago" <tspan fill="{GOLD}">→ {year:,} contributions</tspan></text>')
    body = "\n  ".join(months + labels + rects + legend + [caption])
    return body, H


def main():
    days, start, today = calendar()
    text = ("0123456789,– Total Contributions Current Streak Longest Streak Present "
            "JanFebMarAprMayJunJulAugSepOctNovDec")
    mono = ("0123456789,.–-·→$\"= ~/github/activity.log contributions.svg in the last year updated "
            "Less More Mon Wed Fri git log since 1 year ago contributions JanFebMarAprMayJunJulAugSepOctNovDec Present")
    fonts = "".join([font_face("Poppins", 600, text), font_face("Poppins", 700, text),
                     font_face("JetBrains Mono", 400, mono)])
    body, h = stats_svg(days, start, today)
    (ROOT / "assets" / "stats.svg").write_text(frame(h, "~/github/stats", body, fonts), encoding="utf-8")
    body, h = heatmap_svg(days, today)
    (ROOT / "assets" / "heatmap.svg").write_text(frame(h, "~/github/activity.log", body, fonts), encoding="utf-8")
    print("wrote assets/stats.svg and assets/heatmap.svg")


if __name__ == "__main__":
    main()
