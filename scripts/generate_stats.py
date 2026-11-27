#!/usr/bin/env python3
"""Generates assets/github-stats.svg (monochrome, animated) from the GitHub GraphQL API.

Usage:
  GH_TOKEN=... python scripts/generate_stats.py KartikLangwan assets/github-stats.svg
  python scripts/generate_stats.py KartikLangwan out.svg --mock          (fake data, for design checks)
  python scripts/generate_stats.py KartikLangwan out.svg --placeholder   (empty state)
Only the Python standard library is used.
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from xml.sax.saxutils import escape

SANS = "'Segoe UI','Inter',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code','Fira Code',Consolas,'SF Mono','DejaVu Sans Mono','Courier New',monospace"
W, H = 830, 424
LEVELS = ["#1c1b19", "#4a2516", "#8f3c1b", "#d4561f", "#ff6b2c"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_assets import font_css, GRAIN, BASE_CSS  # noqa: E402

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 6, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if "errors" in data or not data.get("data", {}).get("user"):
        raise SystemExit(f"GraphQL error: {data.get('errors')}")
    return data["data"]["user"]


def mock():
    rnd = random.Random(3)
    start = dt.date.today() - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    weeks, d = [], start
    while d <= dt.date.today():
        days = []
        for _ in range(7):
            if d <= dt.date.today():
                c = 0 if rnd.random() < 0.45 else rnd.randint(1, 14)
                days.append({"contributionCount": c, "date": d.isoformat(), "weekday": (d.weekday() + 1) % 7})
            d += dt.timedelta(days=1)
        weeks.append({"contributionDays": days})
    total = sum(x["contributionCount"] for w in weeks for x in w["contributionDays"])
    return {
        "contributionsCollection": {
            "totalCommitContributions": int(total * 0.8), "totalIssueContributions": 6,
            "totalPullRequestContributions": 14, "totalPullRequestReviewContributions": 3,
            "contributionCalendar": {"totalContributions": total, "weeks": weeks}},
        "repositories": {"totalCount": 9, "nodes": [
            {"stargazerCount": 4, "languages": {"edges": [{"size": 52000, "node": {"name": "Kotlin"}}, {"size": 9000, "node": {"name": "Java"}}]}},
            {"stargazerCount": 1, "languages": {"edges": [{"size": 31000, "node": {"name": "TypeScript"}}, {"size": 5000, "node": {"name": "CSS"}}]}},
            {"stargazerCount": 0, "languages": {"edges": [{"size": 22000, "node": {"name": "JavaScript"}}, {"size": 3000, "node": {"name": "HTML"}}]}},
            {"stargazerCount": 0, "languages": {"edges": [{"size": 12000, "node": {"name": "Python"}}]}}]}}


def streaks(days):
    cur = best = run = 0
    for x in days:
        if x["contributionCount"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
    # current streak: walk back from the latest day (today may still be empty)
    seq = list(days)
    if seq and seq[-1]["contributionCount"] == 0:
        seq = seq[:-1]
    for x in reversed(seq):
        if x["contributionCount"] > 0:
            cur += 1
        else:
            break
    return cur, best


def fmt(n):
    return f"{n:,}"


def level(c, mx):
    if c <= 0:
        return 0
    q = c / max(mx, 1)
    return 1 if q <= 0.25 else 2 if q <= 0.5 else 3 if q <= 0.75 else 4


def build(login, user, placeholder=False):
    if placeholder:
        weeks = []
        cc = {"totalCommitContributions": 0, "totalIssueContributions": 0, "totalPullRequestContributions": 0,
              "totalPullRequestReviewContributions": 0, "contributionCalendar": {"totalContributions": 0, "weeks": []}}
        repos = {"totalCount": 0, "nodes": []}
    else:
        cc = user["contributionsCollection"]
        weeks = cc["contributionCalendar"]["weeks"]
        repos = user["repositories"]
    days = [d for w in weeks for d in w["contributionDays"]]
    stars = sum(n["stargazerCount"] for n in repos["nodes"])
    langs = {}
    for n in repos["nodes"]:
        for e in n["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    ltotal = sum(v for _, v in top) or 1
    cur, best = streaks(days) if days else (0, 0)
    busiest = max(days, key=lambda d: d["contributionCount"]) if days else None

    dash = "-"
    stats = [
        ("Contributions", fmt(cc["contributionCalendar"]["totalContributions"]) if not placeholder else dash),
        ("Commits", fmt(cc["totalCommitContributions"]) if not placeholder else dash),
        ("Pull requests", fmt(cc["totalPullRequestContributions"]) if not placeholder else dash),
        ("Issues", fmt(cc["totalIssueContributions"]) if not placeholder else dash),
        ("Public repos", fmt(repos["totalCount"]) if not placeholder else dash),
        ("Stars earned", fmt(stars) if not placeholder else dash),
    ]

    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub activity for {escape(login)}">')
    a(f'<title>GitHub activity for {escape(login)}</title><defs>'
      f'<style>{font_css("Display", "Body", "Serif", "Mono", "MonoB")}{BASE_CSS}</style>{GRAIN}'
      f'<clipPath id="pc"><rect width="{W}" height="{H}" rx="26"/></clipPath>'
      '<radialGradient id="og"><stop offset="0" stop-color="#ff6b2c" stop-opacity="0.35"/><stop offset="1" stop-color="#ff6b2c" stop-opacity="0"/></radialGradient>'
      '<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff6b2c" stop-opacity="0"/><stop offset="0.5" stop-color="#ff6b2c" stop-opacity="0.9"/><stop offset="1" stop-color="#ff6b2c" stop-opacity="0"/></linearGradient>'
      '</defs>')
    a(f'<g clip-path="url(#pc)"><rect width="{W}" height="{H}" fill="#0b0b0c"/><circle cx="{W-60}" cy="0" r="300" fill="url(#og)"/><rect width="{W}" height="{H}" filter="url(#grain)"/></g>')
    a(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="25.5" fill="none" stroke="#f2efe9" stroke-opacity="0.1"/>')
    # travelling light on top edge
    a(f'<g clip-path="url(#pc)"><rect x="-220" y="0" width="220" height="2" fill="url(#sh)"><animate attributeName="x" values="-220;{W};{W}" keyTimes="0;0.6;1" dur="7s" repeatCount="indefinite"/></rect></g>')
    # header
    a(f'<text x="44" y="46" class="monob" font-size="10" letter-spacing="2.4" fill="#8a8780">GITHUB ACTIVITY</text>')
    a(f'<text x="44" y="78" class="serif" font-size="30" fill="#ff6b2c">@{escape(login)}</text>')
    a(f'<text x="{W-44}" y="46" text-anchor="end" class="mono" font-size="11" fill="#71717a">last 12 months</text>')
    # stats grid
    for i, (label, val) in enumerate(stats):
        cx = 44 + (i % 3) * 150
        cy = 120 + (i // 3) * 66
        a(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1" keyTimes="0;{0.1 + i * 0.1:.2f};1" dur="{1.0 + i * 0.12:.2f}s" fill="freeze"/>'
          f'<text x="{cx}" y="{cy}" class="display" font-size="34" letter-spacing="-1.2" fill="#f2efe9">{val}</text>'
          f'<text x="{cx}" y="{cy + 20}" class="mono" font-size="10" letter-spacing="1" fill="#71717a">{label.upper()}</text></g>')
    # languages
    lx = 520
    a(f'<text x="{lx}" y="104" class="mono" font-size="10" letter-spacing="1.5" fill="#71717a">TOP LANGUAGES</text>')
    if top:
        for i, (name, size) in enumerate(top):
            y = 128 + i * 24
            pct = size / ltotal
            bw = max(4, 170 * pct / (top[0][1] / ltotal))
            a(f'<text x="{lx}" y="{y + 9}" class="mono" font-size="12" fill="#e4e4e7">{escape(name)}</text>')
            a(f'<rect x="{lx + 96}" y="{y}" width="170" height="10" rx="5" fill="#fff" fill-opacity="0.07"/>')
            a(f'<rect x="{lx + 96}" y="{y}" width="0" height="10" rx="5" fill="#ff6b2c"><animate attributeName="width" from="0" to="{bw:.1f}" dur="1.2s" begin="{0.3 + i * 0.15:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/></rect>')
            a(f'<text x="{lx + 276}" y="{y + 9}" class="mono" font-size="11" fill="#a1a1aa">{pct * 100:.0f}%</text>')
    else:
        a(f'<text x="{lx}" y="132" class="body" font-size="13" fill="#71717a">Fills in after the first workflow run.</text>')
    # heatmap
    cell, gap = 11, 3
    hx, hy = 44, 268
    mx = max((d["contributionCount"] for d in days), default=0)
    a(f'<line x1="44" y1="248" x2="{W-44}" y2="248" stroke="#fff" stroke-opacity="0.08"/>')
    last_month = None
    for wi, w in enumerate(weeks):
        if not w["contributionDays"]:
            continue
        d0 = dt.date.fromisoformat(w["contributionDays"][0]["date"])
        if d0.month != last_month and d0.day <= 7:
            a(f'<text x="{hx + wi * (cell + gap)}" y="{hy - 10}" class="mono" font-size="9.5" fill="#71717a">{d0.strftime("%b").upper()}</text>')
            last_month = d0.month
        col = []
        for d in w["contributionDays"]:
            r = d["weekday"]
            col.append(f'<rect x="{hx + wi * (cell + gap)}" y="{hy + r * (cell + gap)}" width="{cell}" height="{cell}" rx="2.5" fill="{LEVELS[level(d["contributionCount"], mx)]}"/>')
        a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.5s" begin="{0.4 + wi * 0.025:.3f}s" fill="freeze"/>'
          f'<g><animate attributeName="opacity" values="1;0.55;1" dur="7s" begin="{2.2 + wi * 0.1:.2f}s" repeatCount="indefinite"/>{"".join(col)}</g></g>')
    if not weeks:
        for wi in range(53):
            for r in range(7):
                a(f'<rect x="{hx + wi * (cell + gap)}" y="{hy + r * (cell + gap)}" width="{cell}" height="{cell}" rx="2.5" fill="{LEVELS[0]}"/>')
    # footer line
    fy = H - 28
    if days:
        bd = dt.date.fromisoformat(busiest["date"]).strftime("%d %b %Y")
        a(f'<text x="44" y="{fy}" class="mono" font-size="11" fill="#a1a1aa">current streak <tspan fill="#f2efe9" class="monob">{cur}d</tspan>'
          f'    longest streak <tspan fill="#f2efe9" class="monob">{best}d</tspan>'
          f'    busiest day <tspan fill="#f2efe9" class="monob">{busiest["contributionCount"]}</tspan> on {bd}</text>')
    else:
        a(f'<text x="44" y="{fy}" class="mono" font-size="11" fill="#71717a">updates daily through GitHub Actions</text>')
    # legend
    lgx = W - 44 - 5 * 14 - 70
    a(f'<text x="{lgx}" y="{fy}" class="mono" font-size="10" fill="#71717a">less</text>')
    for i, c in enumerate(LEVELS):
        a(f'<rect x="{lgx + 30 + i * 14}" y="{fy - 9}" width="10" height="10" rx="2.5" fill="{c}"/>')
    a(f'<text x="{lgx + 30 + 5 * 14 + 4}" y="{fy}" class="mono" font-size="10" fill="#71717a">more</text>')
    a('</svg>')
    return "\n".join(o)


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = [x for x in sys.argv[1:] if x.startswith("--")]
    login, out = args[0], args[1]
    if "--placeholder" in flags:
        svg = build(login, None, placeholder=True)
    elif "--mock" in flags:
        svg = build(login, mock())
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GH_TOKEN is not set")
        svg = build(login, fetch(login, token))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", out, len(svg) // 1024, "KB")


if __name__ == "__main__":
    main()
