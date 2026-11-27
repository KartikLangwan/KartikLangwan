#!/usr/bin/env python3
"""Builds the animated SVGs for the profile README.

  python3 scripts/build_assets.py

Fonts in fonts/ (subset woff2) are embedded into each SVG so the typography
renders the same everywhere GitHub shows the README. Standard library only.
"""
import base64
import math
import os
from xml.sax.saxutils import escape as _esc

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
FONTS = os.path.join(HERE, "..", "fonts")

INK = "#0b0b0c"
PAPER = "#f2efe9"
DIM = "#8a8780"
ORANGE = "#ff6b2c"
TEAL, TEAL2, MINT = "#0FB5AE", "#2FD3BC", "#7DE8C8"
AMBER = "#ffb039"

FONT_FILES = {
    "Display": "bricolage-grotesque-latin-800-normal.woff2",
    "Body": "bricolage-grotesque-latin-400-normal.woff2",
    "Serif": "instrument-serif-latin-400-italic.woff2",
    "Mono": "jetbrains-mono-latin-400-normal.woff2",
    "MonoB": "jetbrains-mono-latin-700-normal.woff2",
}
FALLBACK = {
    "Display": "'Segoe UI',system-ui,sans-serif", "Body": "'Segoe UI',system-ui,sans-serif",
    "Serif": "Georgia,'Times New Roman',serif", "Mono": "Consolas,'Courier New',monospace", "MonoB": "Consolas,'Courier New',monospace",
}


_MEASURE = {}


def measure(text, font, size, spacing=0.0):
    """Width of text in px using the real font metrics (needs fonttools; falls back to an estimate)."""
    try:
        if font not in _MEASURE:
            from fontTools.ttLib import TTFont
            f = TTFont(os.path.join(FONTS, FONT_FILES[font]))
            _MEASURE[font] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
        cmap, hmtx, upm = _MEASURE[font]
        w = sum(hmtx[cmap.get(ord(c), cmap[32])][0] for c in text)
        return w * size / upm + spacing * len(text)
    except Exception:
        return len(text) * size * 0.56 + spacing * len(text)


def esc(s):
    return _esc(s, {'"': "&quot;"})


def font_css(*names):
    out = []
    for n in names:
        with open(os.path.join(FONTS, FONT_FILES[n]), "rb") as f:
            b = base64.b64encode(f.read()).decode()
        out.append(f"@font-face{{font-family:'{n}';src:url(data:font/woff2;base64,{b}) format('woff2');}}")
        out.append(f".{n.lower()}{{font-family:'{n}',{FALLBACK[n]};}}")
    return "".join(out)


def write(name, svg):
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"wrote {name}  ({len(svg)//1024} KB)")


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>'
         '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.07 0"/></filter>')

# ------------------------------------------------------------------ Sweeplark bird (from the Sweeplark brand kit)
BIRD_DEFS = """<linearGradient id="sbody" gradientUnits="userSpaceOnUse" x1="60" y1="440" x2="420" y2="130"><stop offset="0" stop-color="#0A9A9C"/><stop offset="1" stop-color="#2FD3BC"/></linearGradient>
<linearGradient id="sw1" gradientUnits="userSpaceOnUse" x1="60" y1="70" x2="320" y2="270"><stop offset="0" stop-color="#7DE8C8"/><stop offset="1" stop-color="#22C4B2"/></linearGradient>
<linearGradient id="sw2" gradientUnits="userSpaceOnUse" x1="60" y1="160" x2="300" y2="290"><stop offset="0" stop-color="#4FD8BE"/><stop offset="1" stop-color="#0A9A9C"/></linearGradient>
<linearGradient id="sw3" gradientUnits="userSpaceOnUse" x1="80" y1="240" x2="290" y2="310"><stop offset="0" stop-color="#22BFB0"/><stop offset="1" stop-color="#087F86"/></linearGradient>"""


def bird(flap="0.5s"):
    return f"""<path fill="url(#sbody)" d="M338 128 C366 110 404 120 418 148 C434 192 418 244 376 282 C328 326 262 332 214 338 C166 346 118 372 70 412 C100 354 140 318 188 296 C238 272 270 240 284 200 C296 166 312 144 338 128 Z"/>
<path fill="url(#sbody)" d="M336 132 C326 108 308 92 282 86 C322 75 368 90 390 123 C372 118 352 122 336 132 Z"/>
<path fill="#FFB039" d="M408 136 L470 134 L420 176 C422 162 418 148 408 136 Z"/>
<circle cx="377" cy="158" r="10" fill="#0B1B33"/>
<g><animateTransform attributeName="transform" type="rotate" values="0 300 230;-16 300 230;6 300 230;0 300 230" dur="{flap}" repeatCount="indefinite"/>
<path fill="url(#sw3)" d="M312 258 C270 306 168 312 94 252 C160 262 214 246 262 214 Z"/>
<path fill="url(#sw2)" d="M306 242 C250 276 134 250 62 164 C138 196 210 192 276 176 Z"/>
<path fill="url(#sw1)" d="M300 228 C214 226 120 164 78 66 C140 122 222 140 296 142 C284 168 286 198 300 228 Z"/></g>"""


def frame_open(W, H, aria, css, extra_defs="", bg=INK):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(aria)}">',
            f"<title>{esc(aria)}</title>",
            f"<defs><style>{css}</style>{GRAIN}{extra_defs}",
            f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="26"/></clipPath></defs>',
            '<g clip-path="url(#frame)">', f'<rect width="{W}" height="{H}" fill="{bg}"/>']


def frame_close(W, H, stroke=PAPER, op=0.1):
    return [f'<rect width="{W}" height="{H}" filter="url(#grain)"/>', "</g>",
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="25.5" fill="none" stroke="{stroke}" stroke-opacity="{op}"/>', "</svg>\n"]


BASE_CSS = """
.fade{opacity:0;animation:fade .9s ease forwards;}
@keyframes fade{to{opacity:1}}
.up{opacity:0;transform:translateY(16px);animation:up 1s cubic-bezier(.2,.8,.2,1) forwards;}
@keyframes up{to{opacity:1;transform:none}}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 26s linear infinite;}
.spinr{transform-box:fill-box;transform-origin:center;animation:spin 9s linear infinite reverse;}
@keyframes spin{to{transform:rotate(360deg)}}
.blink{animation:blink 1.1s steps(1) infinite;}
@keyframes blink{50%{opacity:0}}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-out infinite;}
@keyframes pulse{0%{transform:scale(1);opacity:.6}100%{transform:scale(3.2);opacity:0}}
.float{animation:float 3.2s ease-in-out infinite alternate;}
@keyframes float{to{transform:translateY(-5px)}}
"""


# ================================================================== HERO
def hero():
    W, H = 830, 400
    ticker = ["WEBSITES", "ANDROID APPS", "DISCORD BOTS", "DEV TOOLS", "AUTOMATION", "AI WORKFLOWS", "PC UTILITIES"]
    ring_text = "INDEPENDENT DEV · BUILT IN DELHI · "
    css = font_css("Display", "Serif", "Mono", "MonoB") + BASE_CSS + f"""
.draw{{fill:{PAPER};fill-opacity:0;stroke:{PAPER};stroke-width:1.4;stroke-dasharray:420;stroke-dashoffset:420;
  animation:draw 2.4s cubic-bezier(.6,.05,.3,1) .3s forwards, fillin 1s ease 2.1s forwards;}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes fillin{{to{{fill-opacity:1;stroke-opacity:0}}}}
.rise{{transform:translateY(130px);animation:rise 1.3s cubic-bezier(.2,.8,.2,1) 1.5s forwards;}}
@keyframes rise{{to{{transform:translateY(0)}}}}
.tick{{animation:tick 34s linear infinite;}}
@keyframes tick{{to{{transform:translateX(-50%)}}}}
.shine{{animation:shine 6s ease-in-out 3.4s infinite;transform:translateX(-500px);}}
@keyframes shine{{0%{{transform:translateX(-500px)}}35%,100%{{transform:translateX(900px)}}}}
.orb{{animation:orb 12s ease-in-out infinite alternate;}}
@keyframes orb{{0%{{transform:translate(0,0)}}100%{{transform:translate(-120px,40px)}}}}
"""
    defs = (f'<radialGradient id="orbg"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0.55"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            '<clipPath id="nameclip"><text x="38" y="208" class="display" font-size="132" letter-spacing="-5">Kartik</text></clipPath>'
            '<clipPath id="riseclip"><rect x="0" y="150" width="830" height="135"/></clipPath>'
            '<path id="ring" d="M 0,-64 a 64,64 0 1,1 0,128 a 64,64 0 1,1 0,-128"/>')
    o = frame_open(W, H, "Kartik Langwan, independent developer from Delhi", css, defs)
    o.append(f'<g class="orb"><circle cx="720" cy="80" r="260" fill="url(#orbg)" opacity="0.55"/></g>')
    o.append(f'<circle cx="60" cy="420" r="200" fill="url(#orbg)" opacity="0.18"/>')
    for y in (56, 322):
        o.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{PAPER}" stroke-opacity="0.08"/>')
    o.append(f'<text x="38" y="36" class="mono fade" font-size="11" letter-spacing="2" fill="{DIM}" style="animation-delay:.1s">KL—PORTFOLIO / 2026</text>')
    o.append(f'<g class="fade" style="animation-delay:.3s"><circle cx="{W-236}" cy="32" r="4" fill="{ORANGE}"/><circle cx="{W-236}" cy="32" r="4" fill="{ORANGE}" class="pulse"/>'
             f'<text x="{W-224}" y="36" class="mono" font-size="11" letter-spacing="2" fill="{PAPER}">TAKING ON NEW PROJECTS</text></g>')
    o.append(f'<text x="42" y="96" class="mono fade" font-size="14" fill="{DIM}" style="animation-delay:.2s">hello, world — i’m<tspan fill="{ORANGE}" class="blink">_</tspan></text>')
    o.append('<text x="38" y="208" class="display draw" font-size="132" letter-spacing="-5">Kartik</text>')
    o.append('<g clip-path="url(#nameclip)"><rect class="shine" x="0" y="80" width="160" height="160" fill="url(#sh)" opacity="0.35" transform="skewX(-20)"/></g>')
    o.append(f'<g clip-path="url(#riseclip)"><text x="236" y="270" class="serif rise" font-size="104" fill="{ORANGE}" letter-spacing="-1">Langwan</text></g>')
    o.append(f'<text x="42" y="300" class="mono fade" font-size="13" fill="{PAPER}" style="animation-delay:2.4s">Independent developer — Delhi</text>')
    cx, cy = 728, 190
    o.append(f'<g class="fade" style="animation-delay:1.1s" transform="translate({cx} {cy})">'
             f'<circle r="86" fill="none" stroke="{PAPER}" stroke-opacity="0.12"/>'
             f'<circle r="44" fill="{ORANGE}"/>'
             f'<g class="spin"><circle r="78" fill="none"/><text class="monob" font-size="10.4" letter-spacing="2.2" fill="{PAPER}"><textPath xlink:href="#ring" href="#ring" textLength="398" lengthAdjust="spacing">{esc(ring_text)}</textPath></text></g>'
             f'<g class="spinr"><circle r="44" fill="none"/><path d="M-13 13 L13 -13 M-6 -13 H13 V6" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></g>'
             f'</g>')
    items, x = [], 0
    for _ in range(2):
        for i, t in enumerate(ticker):
            style = f'fill="none" stroke="{PAPER}" stroke-width="1"' if i % 2 else f'fill="{PAPER}"'
            items.append(f'<text x="{x}" y="0" class="display" font-size="34" letter-spacing="-0.5" {style}>{esc(t)}</text>')
            x += measure(t, 'Display', 34, -0.5) + 26
            items.append(f'<path transform="translate({x - 15} -12)" d="M0 -9 L2.6 -2.6 L9 0 L2.6 2.6 L0 9 L-2.6 2.6 L-9 0 L-2.6 -2.6Z" fill="{ORANGE}"/>')
            x += 18
    o.append(f'<g class="fade" style="animation-delay:2.6s"><g transform="translate(0 374)"><g class="tick">{"".join(items)}</g></g></g>')
    o += frame_close(W, H)
    return "\n".join(o)


# ================================================================== SWEEPLARK SCENE
def sweeplark():
    W, H, D = 830, 360, 10.0
    gx, gy, gr = 612, 178, 70
    N = 360
    RX, RY = 142, 116
    a0, span = 0.93 * math.pi, 2.57 * math.pi
    sx, sy0 = gx + RX * math.cos(a0), gy + RY * math.sin(a0)
    ex, ey = gx + RX * math.cos(a0 + span), gy + RY * math.sin(a0 + span)
    raw = []
    for i in range(N + 1):
        t = i / N
        if t < 0.14:
            u = t / 0.14
            x = 400 + u * (sx - 400)
            y = 360 + u * (sy0 - 360)
        elif t < 0.88:
            u = (t - 0.14) / 0.74
            a = a0 + u * span
            x = gx + RX * math.cos(a)
            y = gy + RY * math.sin(a)
        else:
            u = (t - 0.88) / 0.12
            x = ex + u * 300
            y = ey - u * u * 160
        raw.append((x, y))
    pts = raw
    for _ in range(8):
        pts = [pts[0]] + [((pts[i - 1][0] + pts[i][0] + pts[i + 1][0]) / 3, (pts[i - 1][1] + pts[i][1] + pts[i + 1][1]) / 3) for i in range(1, len(pts) - 1)] + [pts[-1]]
    route = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    cum = [0.0]
    for i in range(len(pts) - 1):
        cum.append(cum[-1] + math.dist(pts[i], pts[i + 1]))
    L = cum[-1]
    fly0, fly1 = 0.08, 0.68

    def t_of(idx):
        return fly0 + (cum[idx] / L) * (fly1 - fly0)

    junk = [("temp", "1.24 GB"), ("crash.dmp", "380 MB"), ("chrome cache", "864 MB"), ("shader cache", "412 MB"),
            ("npm-cache", "590 MB"), ("update junk", "1.12 GB")]
    idxs = [int(N * (0.14 + 0.74 * (2 / 2.57) * f)) for f in (0.06, 0.22, 0.38, 0.54, 0.70, 0.86)]
    times = [t_of(i) for i in idxs]

    css = font_css("Display", "Body", "Serif", "Mono", "MonoB") + BASE_CSS + """
.ring{transform-box:fill-box;transform-origin:center;animation:spin 18s linear infinite;}
"""
    defs = (BIRD_DEFS +
            f'<radialGradient id="tg"><stop offset="0" stop-color="{TEAL}" stop-opacity="0.5"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="trail" gradientUnits="userSpaceOnUse" x1="430" y1="330" x2="830" y2="0"><stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset="0.4" stop-color="{TEAL}" stop-opacity="0.6"/><stop offset="1" stop-color="{MINT}"/></linearGradient>'
            f'<linearGradient id="tt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PAPER}"/><stop offset="1" stop-color="{MINT}"/></linearGradient>'
            f'<path id="route" d="{route}"/>')
    o = frame_open(W, H, "Sweeplark: a small bird sweeps junk files off your Windows PC", css, defs, bg="#06100f")
    o.append(f'<circle cx="{gx}" cy="{gy}" r="300" fill="url(#tg)" opacity="0.5"/>')
    o.append(f'<circle cx="40" cy="0" r="220" fill="url(#tg)" opacity="0.22"/>')

    # ---- copy
    o.append(f'<text x="40" y="52" class="monob up" font-size="11" letter-spacing="2.4" fill="{MINT}" style="animation-delay:.1s">NOW BUILDING — V1.4 FOR WINDOWS</text>')
    o.append(f'<text x="35" y="130" class="display up" font-size="78" letter-spacing="-3.5" fill="url(#tt)" style="animation-delay:.25s">Sweeplark</text>')
    o.append(f'<text x="40" y="170" class="serif up" font-size="34" fill="{PAPER}" style="animation-delay:.45s">Small bird. <tspan fill="{MINT}">Clean PC.</tspan></text>')
    o.append(f'<g class="up" style="animation-delay:.65s"><text x="40" y="206" class="body" font-size="14.5" fill="#a9b8b5">A lightweight cleaner, optimizer and health monitor</text>'
             f'<text x="40" y="226" class="body" font-size="14.5" fill="#a9b8b5">with an offline AI that explains your PC.</text></g>')
    feats = [("PREVIEW", "before every action"), ("LEDGER", "every change logged"), ("OFFLINE", "AI, zero telemetry")]
    for i, (k, v) in enumerate(feats):
        x = 40 + i * 124
        o.append(f'<g class="up" style="animation-delay:{0.85 + i*0.12:.2f}s"><line x1="{x}" y1="256" x2="{x+110}" y2="256" stroke="{MINT}" stroke-opacity="0.35"/>'
                 f'<text x="{x}" y="276" class="monob" font-size="10.5" letter-spacing="1.6" fill="{MINT}">{k}</text>'
                 f'<text x="{x}" y="294" class="body" font-size="12" fill="#7f8f8c">{esc(v)}</text></g>')
    o.append(f'<text x="40" y="330" class="mono up" font-size="11" fill="#5f6f6c" style="animation-delay:1.3s">rust core · tauri 2 + svelte 5 · llama.cpp · ~8 MB · GPL-3.0</text>')

    # ---- gauge
    full0, full1 = 91, 58
    per = (full0 - full1) / len(junk)
    o.append(f'<g transform="translate({gx} {gy})"><circle r="{gr+22}" fill="none" stroke="{MINT}" stroke-opacity="0.16" stroke-dasharray="2 7" class="ring"/>'
             f'<circle r="{gr}" fill="#081816" stroke="#ffffff" stroke-opacity="0.06" stroke-width="12"/></g>')
    kts, vals, lvl = [0.0], [full0], full0
    for t in times:
        kts += [t, t + 0.03]
        vals += [lvl, lvl - per]
        lvl -= per
    kts += [0.9, 0.97, 1.0]
    vals += [full1, full0, full0]
    o.append(f'<g transform="translate({gx} {gy}) rotate(-90)"><circle r="{gr}" fill="none" stroke="{AMBER}" stroke-width="12" stroke-linecap="round" pathLength="100" stroke-dasharray="{full0} 100">'
             f'<animate attributeName="stroke-dasharray" dur="{D}s" repeatCount="indefinite" keyTimes="{";".join(f"{k:.4f}" for k in kts)}" values="{";".join(f"{v:.1f} 100" for v in vals)}"/>'
             f'<animate attributeName="stroke" dur="{D}s" repeatCount="indefinite" keyTimes="0;{times[0]:.3f};{times[-1]:.3f};0.9;0.97;1" values="{AMBER};{AMBER};{TEAL2};{TEAL2};{AMBER};{AMBER}"/></circle></g>')
    nums = [full0] + [round(full0 - per * (i + 1)) for i in range(len(junk))]
    bounds = [0.0] + [t + 0.015 for t in times] + [0.95]
    for i, n in enumerate(nums):
        a, b = bounds[i], bounds[i + 1]
        col = PAPER if i < len(nums) - 1 else MINT
        if a == 0:
            kt, vv, init = f"0;{b:.4f};0.95;1", "1;0;1;1", 1  # first number also shows again after reset
            kt, vv = f"0;{b:.4f};0.95", "1;0;1"
        else:
            kt, vv, init = f"0;{a:.4f};{b:.4f}", "0;1;0", 0
        o.append(f'<text x="{gx}" y="{gy+10}" text-anchor="middle" class="display" font-size="42" letter-spacing="-2" fill="{col}" opacity="{1 if a == 0 else 0}">{n}<tspan font-size="19" dx="1">%</tspan>'
                 f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{vv}"/></text>')
    o.append(f'<text x="{gx}" y="{gy+32}" text-anchor="middle" class="mono" font-size="9.5" letter-spacing="1.8" fill="#6f8481">DISK C:</text>')

    # ---- trail (paced motion => reveal linear in time)
    o.append(f'<path d="{route}" fill="none" stroke="url(#trail)" stroke-width="2.2" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000 1000" stroke-dashoffset="1000">'
             f'<animate attributeName="stroke-dashoffset" dur="{D}s" repeatCount="indefinite" keyTimes="0;{fly0};{fly1};1" values="1000;1000;0;0"/>'
             f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;{fly1};0.88;1" values="1;1;0;0"/></path>')

    # ---- junk chips
    for k, ((name, size), idx, t) in enumerate(zip(junk, idxs, times)):
        px, py = pts[idx]
        w = len(name) * 6.3 + 38
        o.append(f'<g transform="translate({px:.1f} {py:.1f})">')
        o.append(f'<g class="float" style="animation-delay:-{k*0.55:.2f}s"><g>'
                 f'<animateTransform attributeName="transform" type="scale" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t-0.004:.4f};{t+0.03:.4f};0.9;0.97;1" values="1;1;0.05;0.05;1;1"/>'
                 f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t-0.004:.4f};{t+0.025:.4f};0.9;0.97;1" values="1;1;0;0;1;1"/>'
                 f'<rect x="{-w/2:.1f}" y="-14" width="{w:.1f}" height="28" rx="8" fill="#1d150e" stroke="{AMBER}" stroke-opacity="0.5"/>'
                 f'<path transform="translate({-w/2+11:.1f} -7)" d="M0 0 h6 l4 4 v10 h-10z" fill="none" stroke="{AMBER}" stroke-width="1.3" stroke-linejoin="round"/>'
                 f'<text x="{-w/2+27:.1f}" y="4.2" class="mono" font-size="10.2" fill="#f4d9b5">{esc(name)}</text></g></g>')
        o.append(f'<text x="0" y="-20" text-anchor="middle" class="monob" font-size="12" fill="{MINT}" opacity="0">−{size}'
                 f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t:.4f};{t+0.015:.4f};{t+0.11:.4f};1" values="0;0;1;0;0"/>'
                 f'<animateTransform attributeName="transform" type="translate" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t:.4f};{t+0.11:.4f};1" values="0 0;0 0;0 -24;0 -24"/></text>')
        for j in range(10):
            ang = j / 10 * 2 * math.pi + k
            dist = 22 + (j % 3) * 11
            dx, dy = math.cos(ang) * dist, math.sin(ang) * dist
            col = MINT if j % 2 else AMBER
            o.append(f'<circle r="{1.5 + (j%3)*0.6:.1f}" fill="{col}" opacity="0">'
                     f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t:.4f};{t+0.008:.4f};{t+0.075:.4f};1" values="0;0;1;0;0"/>'
                     f'<animateTransform attributeName="transform" type="translate" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t:.4f};{t+0.075:.4f};1" values="0 0;0 0;{dx:.1f} {dy:.1f};{dx:.1f} {dy:.1f}" calcMode="spline" keySplines="0 0 1 1;0.1 0.8 0.3 1;0 0 1 1"/></circle>')
        o.append("</g>")

    # ---- the bird (flies the route, faces direction of travel)
    o.append(f'<g opacity="0"><animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;{fly0};{fly0+0.01};{fly1-0.01};{fly1};1" values="0;0;1;1;0;0"/>'
             f'<animateMotion dur="{D}s" repeatCount="indefinite" rotate="auto" keyPoints="0;0;1;1" keyTimes="0;{fly0};{fly1};1" calcMode="linear"><mpath xlink:href="#route" href="#route"/></animateMotion>'
             f'<g transform="scale(0.12) rotate(12) translate(-300 -240)">{bird("0.3s")}</g></g>')

    # ---- status
    sy = 336
    done_t = times[-1] + 0.04
    o.append(f'<text x="{gx}" y="{sy}" text-anchor="middle" class="mono" font-size="11.5" fill="#7f8f8c">scanning 40+ rules…'
             f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{fly0+0.02:.3f};0.95" values="1;0;1"/></text>')
    o.append(f'<text x="{gx}" y="{sy}" text-anchor="middle" class="mono" font-size="11.5" fill="#a9b8b5" opacity="0">sweeping the safe part…'
             f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{fly0+0.02:.3f};{done_t:.3f}" values="0;1;0"/></text>')
    o.append(f'<text x="{gx}" y="{sy}" text-anchor="middle" class="monob" font-size="11.5" fill="{MINT}" opacity="0">4.61 GB freed · logged · undo ready'
             f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{done_t:.3f};0.95" values="0;1;0"/></text>')
    o += frame_close(W, H, MINT, 0.18)
    return "\n".join(o)



# ================================================================== PROJECT CARDS
def card(fname, aria, accent, label, title, desc, tech, visual_fn, extra_css="", extra_defs="", bg="#0d0d0e"):
    W, H = 405, 260
    css = font_css("Display", "Body", "Mono", "MonoB") + BASE_CSS + extra_css + f"""
.lift{{opacity:0;transform:translateY(14px);animation:up .9s cubic-bezier(.2,.8,.2,1) .15s forwards;}}
.arrow{{animation:arrow 2.4s ease-in-out infinite;}}
@keyframes arrow{{0%,60%,100%{{transform:translate(0,0)}}30%{{transform:translate(3px,-3px)}}}}
"""
    defs = (f'<radialGradient id="cg" cx="0.85" cy="0" r="0.9"><stop offset="0" stop-color="{accent}" stop-opacity="0.28"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="vis"><rect x="12" y="12" width="{W-24}" height="132" rx="16"/></clipPath>' + extra_defs)
    o = frame_open(W, H, aria, css, defs, bg=bg)
    o.append(f'<rect width="{W}" height="{H}" fill="url(#cg)"/>')
    o.append(f'<rect x="12" y="12" width="{W-24}" height="132" rx="16" fill="#000" fill-opacity="0.35" stroke="#fff" stroke-opacity="0.06"/>')
    o.append(f'<g clip-path="url(#vis)">{visual_fn(W)}</g>')
    o.append('<g class="lift">')
    o.append(f'<text x="24" y="172" class="monob" font-size="10" letter-spacing="2" fill="{accent}">{esc(label)}</text>')
    o.append(f'<text x="22" y="206" class="display" font-size="30" letter-spacing="-1.2" fill="{PAPER}">{esc(title)}</text>')
    o.append(f'<text x="24" y="228" class="body" font-size="13" fill="#9c9a94">{esc(desc)}</text>')
    o.append(f'<text x="24" y="248" class="mono" font-size="10.5" fill="#6b6964">{esc(tech)}</text>')
    o.append(f'<g class="arrow"><circle cx="{W-38}" cy="196" r="16" fill="{accent}"/>'
             f'<path transform="translate({W-38} 196)" d="M-5 5 L5 -5 M-2 -5 H5 V2" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g>')
    o.append("</g>")
    o += frame_close(W, H, accent, 0.22)
    write(fname, "\n".join(o))


def vis_sweeplark(W):
    D = 5.0
    o = [BIRD_DEFS.replace("id=\"s", "id=\"cs").replace("url(#s", "url(#cs")]
    route = "M-40 110 C 80 120, 120 30, 210 60 S 340 120, 440 40"
    o.append(f'<path id="cr" d="{route}" fill="none"/>')
    o.append(f'<path d="{route}" fill="none" stroke="{MINT}" stroke-width="2" stroke-linecap="round" pathLength="100" stroke-dasharray="100 100" stroke-dashoffset="100" opacity="0.7">'
             f'<animate attributeName="stroke-dashoffset" dur="{D}s" repeatCount="indefinite" keyTimes="0;0.7;1" values="100;0;0"/>'
             f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;0.7;0.95;1" values="0.7;0.7;0;0"/></path>')
    files = [(70, 104, 0.16), (150, 52, 0.30), (232, 66, 0.44), (300, 100, 0.56), (360, 70, 0.64)]
    for x, y, t in files:
        o.append(f'<g transform="translate({x} {y})"><g><animateTransform attributeName="transform" type="scale" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t:.2f};{t+0.05:.2f};0.92;1" values="1;1;0;0;1"/>'
                 f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t:.2f};{t+0.05:.2f};0.92;1" values="1;1;0;0;1"/>'
                 f'<path d="M-8 -10 h10 l6 6 v14 h-16z" fill="#1d150e" stroke="{AMBER}" stroke-width="1.4" stroke-linejoin="round"/></g>')
        for j in range(6):
            a = j / 6 * 6.28 + x
            o.append(f'<circle r="1.6" fill="{MINT if j%2 else AMBER}" opacity="0"><animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t:.3f};{t+0.01:.3f};{t+0.1:.3f};1" values="0;0;1;0;0"/>'
                     f'<animateTransform attributeName="transform" type="translate" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t:.3f};{t+0.1:.3f};1" values="0 0;0 0;{math.cos(a)*20:.1f} {math.sin(a)*20:.1f};{math.cos(a)*20:.1f} {math.sin(a)*20:.1f}"/></circle>')
        o.append("</g>")
    b = bird("0.28s").replace("url(#s", "url(#cs")
    o.append(f'<g><animateMotion dur="{D}s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" keyTimes="0;0.7;1" calcMode="linear"><mpath xlink:href="#cr" href="#cr"/></animateMotion>'
             f'<g transform="scale(0.1) rotate(12) translate(-300 -240)">{b}</g></g>')
    return "".join(o)


def vis_k4(W):
    o = []
    # spinning record
    o.append(f'<g transform="translate(86 78)"><g class="spin" style="animation-duration:4s">'
             f'<circle r="54" fill="#111"/>' + "".join(f'<circle r="{r}" fill="none" stroke="#fff" stroke-opacity="0.07"/>' for r in (48, 42, 36, 30)) +
             f'<circle r="18" fill="{ORANGE}"/><circle r="3" fill="#111"/><rect x="-1" y="-54" width="2" height="16" fill="#fff" fill-opacity="0.25"/></g></g>')
    # equalizer
    import random
    rnd = random.Random(7)
    for i in range(22):
        x = 170 + i * 9.5
        hs = [rnd.randint(8, 70) for _ in range(5)]
        vals = ";".join(str(h) for h in hs + [hs[0]])
        ys = ";".join(str(112 - h) for h in hs + [hs[0]])
        d = 1.2 + (i % 5) * 0.17
        o.append(f'<rect x="{x:.1f}" y="{112-hs[0]}" width="5" height="{hs[0]}" rx="2.5" fill="{ORANGE}" fill-opacity="{0.45 + (i%3)*0.2:.2f}">'
                 f'<animate attributeName="height" dur="{d:.2f}s" repeatCount="indefinite" values="{vals}"/><animate attributeName="y" dur="{d:.2f}s" repeatCount="indefinite" values="{ys}"/></rect>')
    o.append(f'<text x="170" y="36" class="monob" font-size="9.5" letter-spacing="1.6" fill="{ORANGE}">NOW PLAYING · 320 KBPS</text>')
    o.append(f'<rect x="170" y="124" width="206" height="3" rx="1.5" fill="#fff" fill-opacity="0.1"/>'
             f'<rect x="170" y="124" width="0" height="3" rx="1.5" fill="{ORANGE}"><animate attributeName="width" dur="8s" repeatCount="indefinite" values="0;206"/></rect>')
    return "".join(o)


def vis_lab(W):
    import random
    rnd = random.Random(3)
    D = 6.0
    plain = "meet me at 9, bring the keys"
    chars = "abcdef0123456789+/=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cipher = "".join(rnd.choice(chars) for _ in range(len(plain)))
    frames = []
    n = 10
    for f in range(n + 1):  # plain -> cipher scramble
        k = int(len(plain) * f / n)
        frames.append("".join(cipher[i] if i < k else plain[i] for i in range(len(plain))))
    o = []
    o.append(f'<text x="28" y="40" class="monob" font-size="9.5" letter-spacing="1.6" fill="#a78bfa">AES-256-GCM · IN YOUR BROWSER</text>')
    slot = 0.5 / (n + 1)
    for f, txt in enumerate(frames):
        a = 0.15 + f * slot
        b = a + slot if f < n else 0.85
        o.append(f'<text x="28" y="84" class="mono" font-size="15" fill="{"#e9e4ff" if f == 0 else "#a78bfa"}" opacity="{1 if f == 0 else 0}">{esc(txt)}'
                 f'<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{a if f else b:.3f}{";" + f"{b:.3f}" if f else ""};1" values="{"0;1;0;0" if f else "1;0;1"}"/></text>')
    # lock
    o.append(f'<g transform="translate(352 70)"><rect x="-18" y="-6" width="36" height="28" rx="6" fill="#a78bfa"/>'
             f'<path d="M-10 -6 v-8 a10 10 0 0 1 20 0 v8" fill="none" stroke="#a78bfa" stroke-width="4">'
             f'<animateTransform attributeName="transform" type="translate" dur="{D}s" repeatCount="indefinite" keyTimes="0;0.6;0.66;0.9;0.95;1" values="0 -6;0 -6;0 0;0 0;0 -6;0 -6"/></path>'
             f'<circle cy="6" r="3.5" fill="{INK}"/></g>')
    o.append(f'<text x="28" y="118" class="mono" font-size="10.5" fill="#6b6964">no sign-ups · no servers · stays in your tab</text>')
    return "".join(o)


def vis_ai(W):
    D = 7.0
    blue = "#60a5fa"
    o = []
    # user bubble
    o.append(f'<g opacity="0"><animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;0.06;0.1;0.92;1" values="0;0;1;1;0"/>'
             f'<rect x="150" y="24" width="220" height="30" rx="12" fill="#1e293b"/><text x="162" y="43" class="body" font-size="12" fill="#e2e8f0">make a #clips channel, mods only</text></g>')
    # typing dots
    o.append(f'<g opacity="0"><animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.2;0.42" values="0;1;0"/>'
             f'<rect x="32" y="66" width="52" height="26" rx="12" fill="{blue}" fill-opacity="0.18"/>'
             + "".join(f'<circle cx="{46+i*12}" cy="79" r="3" fill="{blue}"><animate attributeName="opacity" values="0.3;1;0.3" dur="0.9s" begin="{i*0.15}s" repeatCount="indefinite"/></circle>' for i in range(3)) + '</g>')
    # bot reply
    o.append(f'<g opacity="0"><animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;0.42;0.46;0.92;1" values="0;0;1;1;0"/>'
             f'<rect x="32" y="66" width="252" height="50" rx="12" fill="{blue}" fill-opacity="0.16" stroke="{blue}" stroke-opacity="0.35"/>'
             f'<text x="44" y="86" class="monob" font-size="10" fill="{blue}">AI MANAGER · LLAMA</text>'
             f'<text x="44" y="104" class="body" font-size="12" fill="#e2e8f0">done — #clips created, 2 roles set ✓</text></g>')
    for i, (t, txt) in enumerate([(0.55, "+ channel #clips"), (0.62, "~ perms @mods"), (0.69, "~ perms @everyone")]):
        o.append(f'<text x="300" y="{80+i*15}" class="mono" font-size="9.5" fill="#64748b" opacity="0">{txt}<animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" keyTimes="0;{t};{t+0.03};0.92;1" values="0;0;1;1;0"/></text>')
    return "".join(o)


def vis_gb(W):
    green = "#4ade80"
    lines = [("automod", "blocked a scam link in #general"), ("/warn", "@spammer — rule 3"), ("welcome", "@newbie joined, role given"),
             ("/purge", "50 messages in #memes"), ("lfg", "Valorant 5-stack ready"), ("/mute", "@toxic for 10m"), ("backup", "settings saved to SQLite")]
    rows = lines + lines
    o = [f'<g><animateTransform attributeName="transform" type="translate" dur="14s" repeatCount="indefinite" values="0 0;0 -{len(lines)*22}"/>']
    for i, (cmd, msg) in enumerate(rows):
        y = 34 + i * 22
        o.append(f'<circle cx="32" cy="{y-4}" r="3" fill="{green}" fill-opacity="{0.9 if i%3==0 else 0.4}"/>'
                 f'<text x="44" y="{y}" class="monob" font-size="11" fill="{green}">{esc(cmd)}</text>'
                 f'<text x="{44 + len(cmd)*7 + 10}" y="{y}" class="mono" font-size="11" fill="#a3a3a3">{esc(msg)}</text>')
    o.append("</g>")
    o.append(f'<rect x="12" y="12" width="{W-24}" height="26" fill="url(#topfade)"/><rect x="12" y="118" width="{W-24}" height="26" fill="url(#botfade)"/>')
    return "".join(o)


def vis_jay(W):
    pink = "#f472b6"
    o = []
    cols = 6
    for i in range(12):
        c, r = i % cols, i // cols
        x, y = 26 + c * 60, 22 + r * 62
        d = 3 + (i % 4) * 0.7
        o.append(f'<g><rect x="{x}" y="{y}" width="52" height="54" rx="8" fill="{pink}" fill-opacity="0.08" stroke="{pink}" stroke-opacity="0.25">'
                 f'<animate attributeName="fill-opacity" dur="{d:.1f}s" begin="-{i*0.37:.2f}s" repeatCount="indefinite" values="0.06;0.32;0.06"/></rect>'
                 f'<path transform="translate({x+26} {y+27})" d="M-5 -7 L8 0 L-5 7Z" fill="{pink}" fill-opacity="0.8"/></g>')
    o.append(f'<rect x="26" y="22" width="52" height="54" rx="8" fill="none" stroke="{pink}" stroke-width="2.4">'
             f'<animate attributeName="x" dur="6s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.25;0.5;0.75;1" values="26;206;326;86;26" keySplines="0.6 0 0.2 1;0.6 0 0.2 1;0.6 0 0.2 1;0.6 0 0.2 1"/>'
             f'<animate attributeName="y" dur="6s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.25;0.5;0.75;1" values="22;84;22;84;22" keySplines="0.6 0 0.2 1;0.6 0 0.2 1;0.6 0 0.2 1;0.6 0 0.2 1"/></rect>')
    return "".join(o)


def cards():
    card("card-sweeplark.svg", "Sweeplark project card", TEAL2, "NEW · WINDOWS PC CLEANER", "Sweeplark",
         "Cleaner + health monitor with an offline AI.", "rust · tauri 2 · svelte 5 · llama.cpp", vis_sweeplark, bg="#07100f")
    card("card-k4-audio.svg", "K4 Audio project card", ORANGE, "MUSIC APP · ANDROID + WINDOWS", "K4 Audio",
         "YT Music + JioSaavn. No ads, 320 kbps offline.", "kotlin · android · windows", vis_k4)
    card("card-anonymous-lab.svg", "Anonymous Lab project card", "#a78bfa", "PRIVACY TOOLKIT · WEB", "Anonymous Lab",
         "Encryption, dev utils and file tools in-browser.", "react 18 · typescript · tailwind · zustand", vis_lab)
    card("card-ai-server-manager.svg", "AI Server Manager project card", "#60a5fa", "DISCORD · AI AGENT", "AI Server Manager",
         "Runs a Discord server from plain English.", "node.js · discord.js · groq · ollama", vis_ai)
    card("card-gaming-bros-bot.svg", "Gaming Bros Bot project card", "#4ade80", "DISCORD · COMMUNITY BOT", "Gaming Bros Bot",
         "Moderation, utilities and saved settings.", "node.js · discord.js · sqlite · pterodactyl", vis_gb,
         extra_defs='<linearGradient id="topfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0d0e"/><stop offset="1" stop-color="#0d0d0e" stop-opacity="0"/></linearGradient>'
                    '<linearGradient id="botfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0d0e" stop-opacity="0"/><stop offset="1" stop-color="#0d0d0e"/></linearGradient>')
    card("card-jay-sharma.svg", "Jay Sharma portfolio project card", "#f472b6", "CLIENT SITE · VIDEO EDITOR", "Jay Sharma",
         "Reels grid, clients wall, filters, modals.", "html · css · javascript · vercel", vis_jay)



# ================================================================== STACK
STACK = [
    ["React", "TypeScript", "Svelte", "Tailwind CSS", "Framer Motion", "JavaScript", "HTML / CSS", "Zustand", "Vercel"],
    ["Rust", "Tauri", "Kotlin", "Node.js", "discord.js", "Python", "SQLite", "llama.cpp", "Groq", "Ollama", "Pterodactyl"],
]
STACK_HOT = {"Rust", "Tauri", "Svelte", "llama.cpp"}


def stack():
    W, H = 830, 168
    css = font_css("Display", "Mono", "MonoB") + BASE_CSS + """
.m0{animation:m0 40s linear infinite;} .m1{animation:m1 46s linear infinite;}
@keyframes m0{to{transform:translateX(-33.3333%)}} @keyframes m1{from{transform:translateX(-33.3333%)}to{transform:translateX(0)}}
"""
    defs = ('<linearGradient id="ef" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset="0.14" stop-color="#fff"/><stop offset="0.92" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
            f'<mask id="em"><rect width="{W}" height="{H}" fill="url(#ef)"/></mask>')
    o = frame_open(W, H, "Tech stack: " + ", ".join(sum(STACK, [])), css, defs)
    o.append(f'<text x="28" y="34" class="monob" font-size="10" letter-spacing="2.4" fill="{ORANGE}">TOOLBOX</text>')
    o.append(f'<text x="{W-28}" y="34" text-anchor="end" class="mono" font-size="10" letter-spacing="1.5" fill="{DIM}"><tspan fill="{TEAL2}">●</tspan> new this year</text>')
    o.append('<g mask="url(#em)">')
    for r, items in enumerate(STACK):
        y = 82 + r * 52
        parts, x = [], 0.0
        for name in items:
            hot = name in STACK_HOT
            fs = 30
            wch = measure(name, "Display", fs, -0.8)
            col = TEAL2 if hot else (PAPER if r == 0 else "#6f6c66")
            parts.append(f'<text x="{x:.1f}" y="0" class="display" font-size="{fs}" letter-spacing="-0.8" fill="{col}">{esc(name)}</text>')
            x += wch + 20
            parts.append(f'<circle cx="{x:.1f}" cy="-10" r="3" fill="{ORANGE}"/>')
            x += 20
        span = x
        one = "".join(parts)
        o.append(f'<g transform="translate(0 {y})"><g class="m{r}"><g>{one}</g><g transform="translate({span:.1f} 0)">{one}</g><g transform="translate({2*span:.1f} 0)">{one}</g></g></g>')
    o.append("</g>")
    o += frame_close(W, H)
    return "\n".join(o)


# ================================================================== NOW (terminal)
NOW_LINES = [
    ("building", "Sweeplark — offline-AI PC cleaner for Windows", True),
    ("shipping", "K4 Audio updates for Android + Windows", False),
    ("keeping", "Anonymous Lab and the community bots alive", False),
    ("exploring", "AI-assisted server workflows", False),
]


def now():
    W = 830
    n = len(NOW_LINES)
    H = 104 + n * 34 + 44
    cw, fs = 8.4, 14
    x_verb, x_text = 78, 78 + 11 * cw
    per_char, gap, start, hold = 0.035, 0.45, 1.0, 4.5
    t, spans = start, []
    for verb, txt, _ in NOW_LINES:
        spans.append((t, len(txt)))
        t += len(txt) * per_char + gap
    D = round(t + hold, 2)
    css = font_css("Mono", "MonoB", "Serif") + BASE_CSS
    defs = []
    for i, (s0, L) in enumerate(spans):
        kt = [0.0, s0 / D] + [(s0 + c * per_char) / D for c in range(1, L + 1)] + [(D - 0.3) / D, 1.0]
        vals = [0, 0] + [round(c * cw, 1) for c in range(1, L + 1)] + [0, 0]
        kt[-2] = max(kt[-2], kt[-3] + 1e-4)
        defs.append(f'<clipPath id="n{i}"><rect x="{x_text}" y="0" width="0" height="999"><animate attributeName="width" dur="{D}s" repeatCount="indefinite" calcMode="discrete" '
                    f'keyTimes="{";".join(f"{k:.5f}" for k in kt)}" values="{";".join(str(v) for v in vals)}"/></rect></clipPath>')
        defs.append(f'<clipPath id="v{i}"><rect x="0" y="0" width="0" height="999"><animate attributeName="width" dur="{D}s" repeatCount="indefinite" calcMode="discrete" '
                    f'keyTimes="0;{max(s0-0.15,0)/D:.5f};{(D-0.3)/D:.5f}" values="0;{W};0"/></rect></clipPath>')
    o = frame_open(W, H, "What Kartik is working on right now", css, "".join(defs))
    o.append(f'<rect width="{W}" height="46" fill="#fff" fill-opacity="0.035"/><line x1="0" y1="46" x2="{W}" y2="46" stroke="#fff" stroke-opacity="0.07"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        o.append(f'<circle cx="{30 + i*20}" cy="23" r="6" fill="{c}" fill-opacity="0.85"/>')
    o.append(f'<text x="{W/2}" y="27" text-anchor="middle" class="mono" font-size="11.5" fill="{DIM}">kartik@delhi — ~/right-now</text>')
    o.append(f'<text x="{W-30}" y="28" text-anchor="end" class="serif" font-size="17" fill="{ORANGE}">right now</text>')
    o.append(f'<text x="34" y="84" class="monob" font-size="{fs}" fill="{PAPER}"><tspan fill="{ORANGE}">➜</tspan>  <tspan fill="{TEAL2}">~</tspan> now --status</text>')
    for i, (verb, txt, hl) in enumerate(NOW_LINES):
        y = 120 + i * 34
        col = MINT if hl else PAPER
        o.append(f'<g clip-path="url(#v{i})"><text x="34" y="{y}" class="mono" font-size="{fs}" fill="#55534e">{i+1:02d}</text>'
                 f'<text x="{x_verb}" y="{y}" class="monob" font-size="{fs}" fill="{TEAL2 if hl else ORANGE}">{verb}</text></g>')
        o.append(f'<g clip-path="url(#n{i})"><text x="{x_text}" y="{y}" class="mono" font-size="{fs}" fill="{col}" textLength="{len(txt)*cw:.1f}" lengthAdjust="spacingAndGlyphs">{esc(txt)}</text></g>')
        if hl:
            s0, L = spans[i]
            ta = (s0 + L * per_char) / D
            o.append(f'<g opacity="0"><animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{ta:.4f};{(D-0.3)/D:.4f}" values="0;1;0"/><rect x="{x_text + len(txt)*cw + 12:.1f}" y="{y-14}" width="44" height="19" rx="9.5" fill="{TEAL2}" fill-opacity="0.15" stroke="{TEAL2}" stroke-opacity="0.5"/>'
                     f'<text x="{x_text + len(txt)*cw + 34:.1f}" y="{y-0.5}" text-anchor="middle" class="monob" font-size="10" fill="{TEAL2}">NEW</text></g>')
    # cursor
    ckt, cx, cy = [0.0], [x_text], [120 - 13]
    for i, (s0, L) in enumerate(spans):
        for c in range(L + 1):
            ckt.append((s0 + c * per_char) / D)
            cx.append(x_text + c * cw)
            cy.append(120 + i * 34 - 13)
    ckt += [(D - 0.3) / D, 1.0]
    cx += [x_text, x_text]
    cy += [107, 107]
    o.append(f'<rect width="8" height="17" fill="{ORANGE}">'
             f'<animate attributeName="x" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(f"{k:.5f}" for k in ckt)}" values="{";".join(f"{v:.1f}" for v in cx)}"/>'
             f'<animate attributeName="y" dur="{D}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(f"{k:.5f}" for k in ckt)}" values="{";".join(str(v) for v in cy)}"/>'
             '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    o.append(f'<text x="34" y="{H-22}" class="mono" font-size="11" fill="#55534e">open for a few projects at a time · replies within 24h · kartiklangwan@gmail.com</text>')
    o += frame_close(W, H)
    return "\n".join(o)


if __name__ == "__main__":
    write("banner.svg", hero())
    write("sweeplark.svg", sweeplark())
    cards()
    write("stack.svg", stack())
    write("now.svg", now())
