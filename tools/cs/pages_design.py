"""Month 4 of the case study: Design, Visual design, Prototype and test.

Every stage leads to the final solution, the BLUPRINT dashboard (docs/bluprint/). Hi-fi images are real screenshots of it
(tools/cs/shoot_dashboard.js). Usability numbers are a SAMPLE study, labelled as such like the earlier research.
"""
import base64
import html as _h
import pathlib

from charts import grouped, hbars, panel, stat

e = _h.escape
SHOTS = pathlib.Path(__file__).resolve().parent / "shots"
SAMPLE_TEST = "Sample usability test, 2 rounds × 6 participants"


def shot(name, cls="", alt=""):
    data = base64.b64encode((SHOTS / f"{name}.jpg").read_bytes()).decode()
    return f'<img class="shot {cls}" src="data:image/jpeg;base64,{data}" alt="{e(alt)}">'


def browser(name, url="bluprint / @bluorng", cls=""):
    return f'<div class="bframe {cls}"><div class="bbar"><i></i><i></i><i></i><span>{e(url)}</span></div>{shot(name)}</div>'


def phone(name, cls=""):
    return f'<div class="pframe {cls}">{shot(name)}</div>'


def T(k, h, p, dk=False, cls=""):
    return f'<div class="t{" dk" if dk else ""} {cls}"><span class="k">{k}</span>{f"<h5>{h}</h5>" if h else ""}<p>{p}</p></div>'


def tiles(items, cls=""):
    return f'<div class="tiles {cls}">' + "".join(items) + "</div>"


def chips(items, filled=()):
    return '<div class="chips">' + "".join(f'<span class="{"f" if i in filled else ""}">{e(i)}</span>' for i in items) + "</div>"


def callout(label, text, size=None):
    st = f' style="font-size:{size}px"' if size else ""
    return f'<div class="callout"{st}><small>{label}</small>{text}</div>'


def table(header, rows, cols=None, cls=""):
    cg = "".join(f'<col style="width:{c}">' for c in cols) if cols else ""
    h = "".join(f"<th>{x}</th>" for x in header)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="dt2 {cls}"><colgroup>{cg}</colgroup><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


# ---------------------------------------------------------------- flow diagrams
def flow(nodes, edges, W, H):
    """nodes: id -> (x, y, w, h, label, kind); kind in start, end, proc, dec, screen, act.
    edges: (a, b, label). Elbow connectors are routed from relative positions."""
    out = []
    for nid, (x, y, w, h, label, kind) in nodes.items():
        lines = label.split("\n")
        cx, cy = x + w / 2, y + h / 2
        if kind == "dec":
            out.append(f'<polygon points="{cx},{y} {x + w},{cy} {cx},{y + h} {x},{cy}" class="fl-dec"/>')
        elif kind in ("start", "end"):
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" class="fl-term"/>')
        elif kind == "screen":
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="fl-screen"/><rect x="{x}" y="{y}" width="{w}" height="5" class="fl-bar"/>')
        elif kind == "act":
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="fl-act"/>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="fl-proc"/>')
        tcls = "fl-tw" if kind in ("start", "end") else "fl-t"
        y0 = cy - (len(lines) - 1) * 7 + 4
        out.append(f'<text x="{cx}" y="{y0}" text-anchor="middle" class="{tcls}">' +
                   "".join(f'<tspan x="{cx}" dy="{0 if i == 0 else 14}">{e(t)}</tspan>' for i, t in enumerate(lines)) + "</text>")
    for a, b, label in edges:
        ax, ay, aw, ah = nodes[a][:4]
        bx, by, bw, bh = nodes[b][:4]
        acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
        anchor = "start"
        if bx >= ax + aw - 2:            # to the right
            s_, t = (ax + aw, acy), (bx, bcy)
            mx = (s_[0] + t[0]) / 2
            d = f"M{s_[0]} {s_[1]} H{mx} V{t[1]} H{t[0] - 2}"
            if abs(s_[1] - t[1]) <= 4:
                lx, ly, anchor = (s_[0] + t[0]) / 2, s_[1] - 5, "middle"
            else:
                lx, ly = mx + 5, t[1] - 5
        elif bx + bw <= ax + 2:          # to the left
            s_, t = (ax, acy), (bx + bw, bcy)
            mx = (s_[0] + t[0]) / 2
            d = f"M{s_[0]} {s_[1]} H{mx} V{t[1]} H{t[0] + 2}"
            lx, ly = mx + 5, (s_[1] + t[1]) / 2
        elif by >= ay + ah - 2:          # below
            s_, t = (acx, ay + ah), (bcx, by)
            my = (s_[1] + t[1]) / 2
            d = f"M{s_[0]} {s_[1]} V{my} H{t[0]} V{t[1] - 2}"
            lx, ly = t[0] + 6, t[1] - 6
        else:                            # above
            s_, t = (acx, ay), (bcx, by + bh)
            my = (s_[1] + t[1]) / 2
            d = f"M{s_[0]} {s_[1]} V{my} H{t[0]} V{t[1] + 2}"
            lx, ly = t[0] + 6, t[1] + 12
        out.insert(0, f'<path d="{d}" class="fl-e" marker-end="url(#fl-arrow)"/>')
        if label:
            out.append(f'<text x="{lx}" y="{ly}" text-anchor="{anchor}" class="fl-l">{e(label)}</text>')
    defs = '<defs><marker id="fl-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="fl-ah"/></marker></defs>'
    return f'<svg class="svg-fluid flow" viewBox="0 0 {W} {H}">{defs}{"".join(out)}</svg>'


# ---------------------------------------------------------------- wireframes
def scrib(x, y, w, n=1, gap=7, lofi=True):
    """Text placeholder lines."""
    out = ""
    for i in range(n):
        ww = w * (0.92 if i < n - 1 else 0.6)
        if lofi:
            pts = " ".join(f"{x + j * ww / 8:.1f},{y + i * gap + (1.4 if j % 2 else -1.4):.1f}" for j in range(9))
            out += f'<polyline points="{pts}" class="wf-s"/>'
        else:
            out += f'<rect x="{x}" y="{y + i * gap - 2}" width="{ww:.1f}" height="4" class="wf-tx"/>'
    return out


def wf_desktop(lofi=True):
    L = lofi
    box = "wf-b" if L else "wf-m"
    dark = "wf-d" if L else "wf-md"
    lab = (lambda x, y, t, c="wf-lab": f'<text x="{x}" y="{y}" class="{c}">{e(t)}</text>') if not L else (lambda *a, **k: "")
    o = [f'<rect x="0" y="0" width="720" height="12" class="{dark}"/>', lab(360, 9, "TICKER · KEY NUMBERS", "wf-lab wf-c wf-w"),
         f'<rect x="0" y="12" width="720" height="34" class="{box}"/>', scrib(30, 29, 90, 1, lofi=L) if L else lab(30, 33, "IDEAS  CALENDAR  HASHTAGS"),
         f'<rect x="320" y="20" width="80" height="18" class="{box}"/>', lab(360, 33, "BG × BLUPRINT", "wf-lab wf-c"),
         f'<rect x="590" y="21" width="56" height="16" class="{dark}"/><rect x="652" y="21" width="44" height="16" class="{box}"/>',
         lab(618, 32, "EXPORT", "wf-lab wf-c wf-w"), lab(674, 32, "PRINT", "wf-lab wf-c"),
         f'<rect x="0" y="46" width="720" height="18" class="{box}"/>']
    o += [scrib(150 + i * 55, 56, 38, 1, lofi=L) for i in range(8)] if L else [lab(360, 58, "OVERVIEW · WHAT'S WORKING · AVOID · HASHTAGS · POSTING · AUDIENCE · IDEAS · CALENDAR", "wf-lab wf-c")]
    o += [f'<rect x="0" y="64" width="720" height="190" class="{dark}"/>', f'<circle cx="560" cy="140" r="62" class="wf-x"/>',
          f'<rect x="40" y="168" width="280" height="40" class="wf-wb"/>', scrib(40, 222, 230, 2, lofi=True if L else False) if L else lab(40, 226, "Lede: posts, period, what this audit answers", "wf-lab wf-w"),
          f'<rect x="40" y="232" width="90" height="14" class="wf-wb"/><rect x="138" y="232" width="90" height="14" class="wf-wo"/>',
          f'<rect x="600" y="206" width="80" height="36" class="wf-wo"/>']
    if not L:
        o += [lab(40, 160, "INSTAGRAM CONTENT AUDIT", "wf-lab wf-w"), lab(180, 193, "@BLUORNG  (H1)", "wf-lab wf-c wf-big"), lab(560, 144, "3D MARK", "wf-lab wf-c wf-w"),
              lab(85, 242, "SEE 10 IDEAS", "wf-lab wf-c"), lab(183, 242, "CALENDAR", "wf-lab wf-c wf-w"), lab(640, 227, "AUDIT META", "wf-lab wf-c wf-w")]
    o += [f'<rect x="40" y="280" width="250" height="34" class="wf-hd"/>', scrib(420, 296, 220, 2, lofi=L)]
    if not L:
        o.append(lab(46, 302, "SECTION TITLE (H2)", "wf-lab wf-big2"))
    for i in range(6):
        x = 40 + i * 108
        o += [f'<rect x="{x}" y="334" width="100" height="112" class="{box if i < 5 else dark}"/>', scrib(x, 458, 70, 2, lofi=L)]
        if not L:
            o.append(lab(x + 50, 394, ["150", "11.0K", "142", "UP", "REELS", "33.8K"][i], f'wf-lab wf-c wf-big{" wf-w" if i == 5 else ""}'))
    o += [f'<rect x="40" y="486" width="410" height="200" class="{box}"/>', f'<rect x="458" y="486" width="222" height="200" class="{box}"/>']
    for i in range(8):
        o += [scrib(54, 512 + i * 20, 90, 1, lofi=L), f'<rect x="160" y="{507 + i * 20}" width="{240 - i * 18}" height="8" class="wf-bar"/>']
    for i in range(3):
        o += [scrib(470, 512 + i * 22, 50, 1, lofi=L), f'<rect x="540" y="{507 + i * 22}" width="{110 - i * 30}" height="8" class="{"wf-bar" if i == 0 else "wf-red"}"/>']
    if not L:
        o += [lab(54, 500, "TOP 10 POSTS (BARS → OPEN POST)"), lab(470, 500, "FORMAT PERFORMANCE")]
    o += [f'<rect x="40" y="696" width="640" height="150" class="{box}"/>',
          '<path d="M60 800 C120 780 160 790 200 770 S300 760 340 740 S440 760 480 735 S600 720 660 715" class="wf-line"/>']
    if not L:
        o.append(lab(54, 712, "ENGAGEMENT OVER TIME · ROLLING AVERAGE + DOTS"))
    return f'<svg class="svg-fluid wf" viewBox="0 0 720 860">{"".join(o)}</svg>'


def wf_mobile(lofi=True):
    L = lofi
    box = "wf-b" if L else "wf-m"
    dark = "wf-d" if L else "wf-md"
    o = [f'<rect x="0" y="0" width="200" height="8" class="{dark}"/>', f'<rect x="0" y="8" width="200" height="26" class="{box}"/>',
         f'<rect x="12" y="15" width="70" height="12" class="{box}"/>', f'<rect x="150" y="14" width="38" height="14" class="{dark}"/>',
         f'<rect x="0" y="34" width="200" height="16" class="{box}"/>', scrib(12, 42, 170, 1, lofi=L),
         f'<rect x="0" y="50" width="200" height="200" class="{dark}"/>', f'<circle cx="130" cy="100" r="38" class="wf-x"/>',
         f'<rect x="12" y="160" width="150" height="22" class="wf-wb"/>', f'<rect x="12" y="214" width="84" height="16" class="wf-wb"/><rect x="104" y="214" width="84" height="16" class="wf-wo"/>',
         f'<rect x="12" y="266" width="120" height="20" class="wf-hd"/>']
    for i in range(4):
        x, y = 12 + (i % 2) * 92, 300 + (i // 2) * 80
        o += [f'<rect x="{x}" y="{y}" width="84" height="56" class="{box}"/>', scrib(x, y + 66, 60, 1, lofi=L)]
    return f'<svg class="svg-fluid wf" viewBox="0 0 200 460">{"".join(o)}</svg>'


def wf_ideas(lofi=False):
    box = "wf-b" if lofi else "wf-m"
    lab = (lambda x, y, t, c="wf-lab": f'<text x="{x}" y="{y}" class="{c}">{e(t)}</text>')
    o = [f'<rect x="20" y="16" width="230" height="30" class="wf-hd"/>', lab(26, 37, "10 CONTENT IDEAS", "wf-lab wf-big2"), scrib(420, 28, 260, 2, lofi=lofi)]
    hooks = ["PRICE, SIZES, TIME.", "WHAT SIZE SHOULD I GET?", "IT'S BACK. FOR 48 HOURS.", "72 HOURS. ONE PIECE."]
    for i in range(4):
        x = 20 + i * 172
        o += [f'<rect x="{x}" y="66" width="164" height="164" class="{"wf-md" if i == 0 else box}"/>', f'<rect x="{x + 8}" y="74" width="66" height="12" class="{"wf-wb" if i == 0 else "wf-md"}"/>',
              lab(x + 41, 83, "HIGH", f'wf-lab wf-c{"" if i == 0 else " wf-w"}'), lab(x + 82, 152, hooks[i], f'wf-lab wf-c{" wf-w" if i == 0 else ""}'),
              lab(x, 248, "IDEA TITLE"), lab(x + 164, 248, "FORMAT", "wf-lab wf-r"), scrib(x, 264, 150, 3, lofi=lofi)]
    o += [f'<rect x="20" y="310" width="230" height="30" class="wf-hd"/>', lab(26, 331, "30-DAY CALENDAR", "wf-lab wf-big2")]
    for i, t in enumerate(["ALL", "REEL", "CAROUSEL", "STATIC", "STORY"]):
        o += [f'<rect x="{20 + i * 62}" y="354" width="56" height="18" class="{"wf-md" if i == 0 else box}"/>', lab(48 + i * 62, 366, t, f'wf-lab wf-c{" wf-w" if i == 0 else ""}')]
    o += [lab(20, 392, "DATE"), lab(90, 392, "CONTENT TYPE"), lab(300, 392, "HOOK"), lab(520, 392, "FORMAT"), lab(590, 392, "TIME"), lab(650, 392, "TAGS")]
    for i in range(6):
        y = 400 + i * 24
        o += [f'<line x1="20" x2="700" y1="{y}" y2="{y}" class="wf-rule"/>', f'<rect x="20" y="{y + 1}" width="2" height="22" class="{"wf-md" if i % 2 == 0 else "wf-none"}"/>',
              scrib(28, y + 13, 40, 1, lofi=lofi), scrib(90, y + 13, 170, 1, lofi=lofi), scrib(300, y + 13, 190, 1, lofi=lofi),
              f'<rect x="520" y="{y + 7}" width="40" height="11" class="{box}"/>', scrib(590, y + 13, 40, 1, lofi=lofi), scrib(650, y + 13, 30, 1, lofi=lofi)]
    return f'<svg class="svg-fluid wf" viewBox="0 0 720 550">{"".join(o)}</svg>'


def layout_option(kind):
    o = []
    if kind == "A":   # SaaS sidebar
        o += ['<rect x="0" y="0" width="200" height="14" class="wf-d"/>', '<rect x="0" y="14" width="44" height="126" class="wf-d"/>']
        o += [f'<rect x="54" y="{22 + i * 0}" width="{36}" height="22" class="wf-b"/>'.replace('x="54"', f'x="{54 + i * 24}"').replace('width="36"', 'width="20"') for i in range(6)]
        o += ['<rect x="54" y="52" width="80" height="40" class="wf-b"/><rect x="140" y="52" width="52" height="40" class="wf-b"/><rect x="54" y="98" width="138" height="36" class="wf-b"/>']
    elif kind == "B":  # store single page
        o += ['<rect x="0" y="0" width="200" height="6" class="wf-d"/>', '<rect x="0" y="6" width="200" height="12" class="wf-b"/><rect x="80" y="8" width="40" height="8" class="wf-b"/>',
              '<rect x="0" y="18" width="200" height="8" class="wf-b"/>', '<rect x="0" y="26" width="200" height="50" class="wf-d"/><circle cx="150" cy="48" r="16" class="wf-x"/>',
              '<rect x="8" y="58" width="70" height="10" class="wf-wb"/>']
        o += [f'<rect x="{8 + i * 31.5}" y="84" width="28" height="34" class="wf-b"/>' for i in range(6)]
        o += ['<rect x="8" y="124" width="184" height="12" class="wf-b"/>']
    else:             # card feed
        o += ['<rect x="0" y="0" width="200" height="16" class="wf-b"/>']
        o += [f'<rect x="{8 + (i % 3) * 63}" y="{24 + (i // 3) * 58}" width="58" height="52" class="wf-b"/>' for i in range(6)]
    return f'<svg class="svg-fluid wf" viewBox="0 0 200 140">{"".join(o)}</svg>'


# ---------------------------------------------------------------- colour maths
def lum(h):
    h = h.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def cr(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------- pages
def design_pages():
    P = []

    def page(phase, stage, title, body, lead="", take="", source="", w=900):
        P.append(dict(kind="content", phase=phase, stage=stage, title=title, lead=lead, body=body, take=take, source=source, w=w))

    def divider(n, title, text, stages, mark):
        P.append(dict(kind="divider", n=n, title=title, text=text, stages=stages, mark=mark))

    # ============================================================ 05 DESIGN
    divider("05", "Design", "Turning the chosen direction into flows, structure and screens: from how the team moves through BLUPRINT to the first wireframes.",
            ["User flows", "Task flows", "Task analysis", "Feature mapping", "Information architecture", "Wireframes", "Paper prototype"], 6)

    D = "Design"
    nodes = {
        "s": (10, 150, 110, 34, "Weekly audit link\n(WhatsApp, Slack)", "start"),
        "land": (150, 140, 120, 54, "Land: hero +\nticker numbers", "screen"),
        "q": (300, 132, 110, 70, "What do I\nneed today?", "dec"),
        "perf": (490, 20, 130, 44, "Performance:\nKPIs, top 10", "screen"),
        "post": (660, 20, 120, 44, "Open post on\nInstagram", "act"),
        "learn": (490, 100, 130, 44, "What's working\n+ what to avoid", "screen"),
        "fix": (490, 180, 130, 44, "Hashtags +\nposting schedule", "screen"),
        "ideas": (490, 260, 130, 44, "10 content ideas\n(read the why)", "screen"),
        "cal": (660, 260, 120, 44, "30-day calendar\n(filter format)", "screen"),
        "exp": (820, 260, 110, 44, "Export CSV\nor print", "act"),
        "end": (820, 150, 110, 34, "Plan shared in\nthe meeting", "end"),
    }
    edges = [("s", "land", ""), ("land", "q", ""), ("q", "perf", "check"), ("q", "learn", "learn"), ("q", "fix", "fix"), ("q", "ideas", "plan"),
             ("perf", "post", ""), ("learn", "ideas", ""), ("ideas", "cal", ""), ("cal", "exp", ""), ("exp", "end", ""), ("fix", "cal", "")]
    page(D, "User flows", "The main user flow",
         flow(nodes, edges, 940, 320) + '<div class="legend-row" style="margin-top:8px"><span><i class="lg-k term"></i>Start or end</span><span><i class="lg-k scr"></i>Screen or section</span>'
         '<span><i class="lg-k dec"></i>Decision</span><span><i class="lg-k act"></i>User action</span></div>',
         lead="One link, one page, four reasons to open it. Every path ends in a plan the team can act on.",
         take="The flow is built around the planning meeting: diagnose, learn, then decide what to make.", w=980)

    per = [("NK", "Naina, Marketing Lead", "Monthly review", ["Open audit", "Read KPIs + trend", "What's working", "Avoid list", "Share in meeting"]),
           ("AV", "Aditya, Performance Marketer", "Pick ad angles", ["Top 10 posts", "Open best post", "Content clusters", "Ideas: High confidence", "Brief the editor"]),
           ("RS", "Riya, Social Media Manager", "Weekly plan", ["Ideas", "Calendar", "Filter: Reel", "Hashtag groups", "Export CSV"]),
           ("KM", "Karan, Photographer", "Before the shoot", ["Calendar", "Idea card: hook + format", "Formula", "Shot list from ideas", "Shoot"])]
    rows = "".join(f'<div class="pf"><div class="iv-h"><div class="mono-av">{a}</div><div><b>{e(n)}</b><span>{e(g)}</span></div></div>'
                   f'<div class="pf-steps">' + "".join(f'<span>{e(s)}</span>' for s in steps) + "</div></div>" for a, n, g, steps in per)
    page(D, "User flows / Per persona", "Four people, four routes", f'<div class="pfs">{rows}</div>',
         lead="The same page serves each persona from the Define phase through a different route.",
         take="Nobody needs every section every time. The section tabs let each role jump straight to its part.", w=980)

    t1 = {"a": (10, 40, 100, 40, "Open audit", "start"), "b": (135, 40, 105, 40, "Tap 'Ideas'\ntab", "act"), "c": (265, 30, 120, 60, "Enough High\nconfidence?", "dec"),
          "d": (430, 40, 110, 40, "Read hook +\nwhy", "screen"), "e": (570, 40, 110, 40, "Calendar:\nfilter Reel", "screen"), "f": (710, 40, 100, 40, "Export CSV", "end"),
          "g": (270, 120, 110, 40, "Check What's\nworking", "screen")}
    t2 = {"a": (10, 30, 100, 40, "Open audit", "start"), "b": (135, 30, 105, 40, "Tap 'Hashtags'", "act"), "c": (265, 30, 110, 40, "Read 'Stop\nusing' list", "screen"),
          "d": (400, 20, 120, 60, "Unsure about\na tag?", "dec"), "e": (570, 30, 110, 40, "Hover tag in\nthe cloud", "act"), "f": (710, 30, 100, 40, "Copy Keep +\nTry lists", "end")}
    t3 = {"a": (10, 30, 100, 40, "Open audit", "start"), "b": (140, 30, 110, 40, "Tap 'Posting'", "act"), "c": (280, 30, 110, 40, "Read heatmap\n(day × time)", "screen"),
          "d": (420, 30, 110, 40, "Recommended\nschedule", "screen"), "e": (560, 30, 110, 40, "Set time in\nscheduler", "end")}
    page(D, "Task flows", "Three core tasks, step by step",
         '<p class="chart-t">T1 · Plan next week\'s posts</p>' + flow(t1, [("a", "b", ""), ("b", "c", ""), ("c", "d", "yes"), ("c", "g", "no"), ("g", "d", ""), ("d", "e", ""), ("e", "f", "")], 820, 170) +
         '<p class="chart-t">T2 · Drop hashtags that hurt reach</p>' + flow(t2, [("a", "b", ""), ("b", "c", ""), ("c", "d", ""), ("d", "e", "yes"), ("e", "f", "")], 820, 90) +
         '<p class="chart-t">T3 · Choose when to post</p>' + flow(t3, [("a", "b", ""), ("b", "c", ""), ("c", "d", ""), ("d", "e", "")], 820, 90),
         lead="The three tasks the team does every week, mapped screen by screen. These become the usability test tasks.",
         take="Each core task takes four to six steps, all on one page, with no logins or menus in the way.", w=940)

    hta = [("1", "Review performance", ["1.1 Read KPI tiles", "1.2 Scan top 10 posts", "1.3 Check the trend"]),
           ("2", "Learn the patterns", ["2.1 Read winning formulas", "2.2 Compare clusters, hooks", "2.3 Check what to avoid"]),
           ("3", "Choose ideas", ["3.1 Scan confidence tags", "3.2 Read the why", "3.3 Pick three ideas"]),
           ("4", "Schedule and share", ["4.1 Open the calendar", "4.2 Filter by format", "4.3 Export CSV or print"])]
    cols = "".join(f'<div class="sm-col"><div class="sm-h">{n}. {e(t)}</div><ul>' + "".join(f"<li>{e(x)}</li>" for x in subs) + "</ul></div>" for n, t, subs in hta)
    page(D, "Task analysis", "Hierarchical task analysis",
         f'<div class="sitemap" style="min-width:0"><div class="sm-root" style="width:360px">0. Plan a week of content with BLUPRINT</div><div class="sm-stem"></div>'
         f'<div class="sm-cols" style="grid-template-columns:repeat(4,minmax(0,1fr))">{cols}</div></div>' +
         '<div class="grid2" style="grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);align-items:stretch">' +
         callout("Plan 0", "Do 1, then 3 and 4. Do 2 when the plan needs a reason, or in the monthly review. Repeat users skip 1.1.") +
         panel("Minutes per weekly planning task: today vs target with BLUPRINT",
               hbars([("Find what worked last week", 40), ("  with BLUPRINT", 2), ("Come up with 5 post ideas", 75), ("  with BLUPRINT", 10),
                      ("Pick posting times", 15), ("  with BLUPRINT", 2)], maxv=80, unit=" min", hi={"  with BLUPRINT"}, label_w="minmax(170px,220px)"),
               "Today = interview estimates (sample interviews). Target = design goal measures G1 and G3.") + "</div>",
         lead="Breaking 'plan a week of content' into the goals and sub-tasks the interface has to support.",
         take="Sub-tasks map one to one onto page sections, so the structure follows the work.", source="Sample interviews", w=960)

    feats = {"Must": [("KPI snapshot", "G1", "All"), ("Top 10 posts → open post", "G1", "NK AV"), ("Winning formulas", "G1 G3", "NK RS"),
                      ("10 ideas with the why", "G3 G6", "All"), ("30-day calendar", "G4 G7", "RS KM"), ("Keep / Try / Stop hashtags", "G1", "RS")],
             "Should": [("Day × time heatmap", "G1", "RS"), ("Recommended schedule", "G4", "RS"), ("Audience asks", "G3", "NK RS"), ("Export CSV", "G7", "NK RS")],
             "Could": [("Ticker of key numbers", "G1", "All"), ("All-posts table", "G1", "AV"), ("Print view", "G7", "NK")],
             "Won't (v1)": [("Meta Ad Library scan", "G2", "AV"), ("Ad spend and ROAS", "G5", "AV NK"), ("Shoot planner", "G4", "KM"), ("Claude AI write-ups", "G3", "All")]}
    fb = "".join(f'<div class="col{" wont" if k.startswith("Won") else ""}"><h6>{e(k)}</h6>' + "".join(f'<div class="ft">{e(n)}<small>{g} · {p}</small></div>' for n, g, p in v) + "</div>"
                 for k, v in feats.items())
    page(D, "Feature mapping", "Features, goals and priority",
         f'<div class="fb" style="grid-template-columns:repeat(4,minmax(0,1fr))">{fb}</div>' +
         callout("Scope decision", "Version 1 is built on public Instagram data, which can be collected for any account today. Meta ads data, the Ad Library and the shoot planner need BLUORNG's ad account access, so they move to version 2.", 15),
         lead="Every feature traced to a design goal (G1 to G7) and the personas it serves, then prioritised with MoSCoW.",
         take="Version 1 covers goals G1, G3, G4 (partly) and G7. G2 and G5 need ad-account data and come next.", w=980)

    # ---------- information architecture
    inv = [["Post", "Caption, format, date, likes, comments, link", "Apify scrape", "Every audit"],
           ["Metric", "Averages, trend, lift vs account", "Computed", "Every audit"],
           ["Pattern", "Topic cluster, hook style, caption length, CTA", "Computed from captions", "Every audit"],
           ["Hashtag", "Uses, lift, top or bottom quarter", "Computed", "Every audit"],
           ["Time slot", "Day × time, posts, average", "Computed", "Every audit"],
           ["Comment signal", "Reaction, ask (restock, size, price…)", "Computed from comments", "Every audit"],
           ["Idea", "Hook, format, formula, why, confidence, opener", "Generated from signals", "Every audit"],
           ["Calendar entry", "Date, time, idea or filler, hashtag group", "Generated", "Every audit"]]
    page(D, "Information architecture / Content strategy", "Content strategy and analysis",
         tiles([T("Goal 1", "Answer one question", "What should we make next, and why?", True), T("Goal 2", "Evidence on every claim", "Each idea cites the number behind it."),
                T("Goal 3", "Brand voice, not analytics speak", "Short uppercase labels, plain sentences, no jargon.")]) +
         table(["Content object", "Attributes", "Source", "Refresh"], inv, ["18%", "44%", "22%", "16%"]),
         lead="A content inventory of everything the dashboard shows, where it comes from and how often it changes.",
         take="Eight content objects, all produced by one audit run. Nothing on the page is typed in by hand.", w=940)

    sort = [("What's working", [6, 0, 0, 0]), ("What to avoid", [5, 1, 0, 0]), ("Hashtags", [1, 4, 1, 0]), ("Posting times", [0, 5, 1, 0]),
            ("Audience asks", [1, 1, 4, 0]), ("Content ideas", [0, 0, 1, 5]), ("Calendar", [0, 0, 0, 6]), ("Top posts", [5, 0, 1, 0])]
    groups = ["Learn", "Optimise", "Listen", "Plan"]
    hm = "<tr><th>Card</th>" + "".join(f'<th style="text-align:center">{g}</th>' for g in groups) + "</tr>" + "".join(
        f"<tr><td>{e(c)}</td>" + "".join(f'<td class="s s{min(5, v)}">{v}</td>' for v in vals) + "</tr>" for c, vals in sort)
    page(D, "Information architecture / Organisation", "Organisation: ordered by the job",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.1fr) minmax(0,1fr)">' +
         f'<div class="panel"><p class="chart-t">Open card sort, 6 team members: where each card was placed</p><table class="hm">{hm}</table></div>' +
         '<div>' + tiles([T("Scheme", "Task-based, top to bottom", "Diagnose → learn → optimise → listen → plan. The page reads in the order of the planning meeting.", True),
                          T("Structure", "One page, eight sections", "Interviews showed the team shares one link in a meeting. A single scrolling page beats a multi-page app."),
                          T("Result", "Four groups became eight sections", "Learn: performance, working, avoid. Optimise: hashtags, posting. Listen: audience. Plan: ideas, calendar.")], "c1") + "</div></div>",
         lead="How the content is grouped and ordered, checked with an open card sort.",
         take="The team grouped the cards the way they plan: look back, fix the basics, then plan forward.", source="Sample card sort, n = 6", w=980)

    sm = [("Header", ["Quick links", "BG × BLUPRINT", "Export CSV", "Print", "Section tabs"]),
          ("Hero", ["@handle, period", "See 10 ideas", "30-day calendar", "Audit meta"]),
          ("01 Performance", ["KPI tiles", "Top 10 posts", "Format performance", "Engagement over time"]),
          ("02 What's working", ["Winning formulas", "Clusters", "Hook styles", "Caption length", "CTA"]),
          ("03 Avoid", ["Avoid patterns", "Bottom 15 posts"]),
          ("04 Hashtags", ["Cloud", "Keep / Try / Stop"]),
          ("05 Posting", ["Heatmap", "Best days", "Schedule", "Frequency"]),
          ("06 Audience", ["Reactions", "Asks", "Comment samples"]),
          ("07 Ideas", ["10 idea cards"]),
          ("08 Calendar", ["Format filter", "30 days", "Hashtag groups", "All posts table"])]
    cols = "".join(f'<div class="sm-col"><div class="sm-h">{e(t)}</div><ul>' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul></div>" for t, xs in sm)
    page(D, "Information architecture / Sitemap", "Sitemap",
         f'<div class="sitemap" style="min-width:0"><div class="sm-root" style="width:320px">BLUPRINT · @bluorng audit (one page)</div><div class="sm-stem"></div>'
         f'<div class="sm-cols" style="grid-template-columns:repeat(5,minmax(0,1fr));row-gap:18px">{cols}</div></div><p class="chart-s">Footer: method, section links, data source, project note.</p>',
         lead="The structure of the single-page dashboard, from header to calendar.",
         take="Ten blocks, at most two levels deep. Everything is one tap from the sticky section tabs.", w=980)

    labels = [["Engagement rate analysis", "Performance", "Plain word; 'rate' needs follower data we don't have"],
              ["Negative patterns", "What to avoid", "Card sort: 5 of 6 used 'avoid'"],
              ["Content taxonomy", "Content clusters", "Kept: the team already says 'clusters'"],
              ["Sentiment analysis", "Audience", "Shorter tab; the section covers reactions and asks"],
              ["Recommendations", "Content ideas", "Matches how the team talks: 'ideas'"],
              ["Publishing schedule", "Calendar", "One word, fits the tab bar"],
              ["Confidence 0.82", "High confidence", "Words over decimals; tested in round 2"],
              ["Download data", "Export CSV", "Says the format"]]
    page(D, "Information architecture / Navigation and labels", "Navigation and labelling",
         '<div class="grid2" style="grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr)">' +
         tiles([T("Global", "Sticky section tabs", "Eight tabs under the header; the active one is underlined and a progress line shows how far you are.", True),
                T("Utility", "Export CSV, Print", "Top right, always visible."),
                T("Contextual", "Hero buttons, bars, tags", "'See 10 ideas', bar → open post, hover → tooltip."),
                T("Quick links", "Ideas, Calendar, Hashtags", "The three most used sections, top left on desktop.")], "c1") +
         table(["Working label", "Final label", "Why"], labels, ["30%", "24%", "46%"]) + "</div>",
         lead="How people move around the page, and the words on the signposts.",
         take="Labels were renamed in the team's own words, so nothing needs explaining in the meeting.", w=1000)

    page(D, "Information architecture / Proposed solution", "Proposed solution: BLUPRINT v1",
         '<div class="grid2" style="grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);align-items:center">' +
         '<div>' + callout("Proposed solution", "A one-page content audit dashboard for @bluorng. It scrapes the latest 150 posts, finds what works and what doesn't, and turns it into 10 ideas and a 30-day calendar the team can export.", 16) +
         '<div class="tobe" style="min-width:0;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr)"><div class="cols">' +
         "".join(f'<div class="src-chip"><i></i>{x}</div>' for x in ["150 public posts", "Captions + hashtags", "Likes, comments", "Latest comments"]) +
         '</div><div class="arrow-r">→</div><div class="cols">' +
         "".join(f'<div class="box acc"><h5>{a}</h5><ul><li>{b}</li></ul></div>' for a, b in [("Learn", "Performance, working, avoid"), ("Optimise", "Hashtags, posting"), ("Plan", "Ideas, calendar, export")]) +
         '</div></div></div>' + browser("d-top") + "</div>",
         lead="Everything so far, combined into one proposal.",
         take="The structure is settled. Next: sketch it, test it on paper, then design it.", w=1040)

    # ---------- wireframes
    page(D, "Wireframes / Layout options", "Three layouts, sketched",
         '<div class="grid3">' + "".join(f'<div class="panel"><p class="chart-t">{t}</p>{layout_option(k)}<p class="chart-s">{d}</p></div>' for k, t, d in [
             ("A", "A · SaaS dashboard", "Sidebar, dark theme, dense panels. Familiar from analytics tools."),
             ("B", "B · Store page", "Announcement bar, store header, campaign hero, product-style tiles. BLUORNG's own language."),
             ("C", "C · Card feed", "Instagram-like grid of insight cards. Fast to scan, weak for comparing numbers.")]) + "</div>" +
         tiles([T("Round 1 pick", "A, the SaaS dashboard", "Chosen first because it felt like a 'real tool' to the team."), T("Round 2 pick", "B, the store page", "After usability round 1: the team wanted it to feel like BLUORNG, not like software.", True),
                T("Dropped", "C, the card feed", "Hard to compare numbers side by side; tables and bars won.")]),
         lead="Crazy-8-style layout sketches before any detail. Two of them were built and tested.",
         take="Layout A was tested first; testing pushed the design to B. The usability section shows why.", w=980)

    page(D, "Wireframes / Low fidelity", "Low-fidelity wireframes",
         '<div class="grid2" style="grid-template-columns:minmax(0,2.2fr) minmax(0,1fr);align-items:start">' +
         f'<div class="panel"><p class="chart-t">Desktop · 1440</p>{wf_desktop(True)}</div><div class="panel"><p class="chart-t">Mobile · 390</p>{wf_mobile(True)}</div></div>',
         lead="Boxes and squiggles: where things go, in what order, and how big.",
         take="The low-fi frames fix the order: header, tabs, hero, KPIs, then evidence. Content comes later.", w=960)

    page(D, "Wireframes / Mid fidelity", "Mid-fidelity wireframes: overview",
         '<div class="grid2" style="grid-template-columns:minmax(0,2.2fr) minmax(0,1fr);align-items:start">' +
         f'<div class="panel"><p class="chart-t">Desktop · real labels, grey boxes</p>{wf_desktop(False)}</div><div class="panel"><p class="chart-t">Mobile</p>{wf_mobile(False)}</div></div>',
         lead="Real labels and hierarchy, still in greyscale, so the test is about structure, not colour.",
         take="Mid-fi adds the label system and the KPI order: posts, likes, comments, trend, format, best post.", w=960)

    page(D, "Wireframes / Mid fidelity", "Mid-fidelity wireframes: ideas and calendar",
         f'<div class="panel">{wf_ideas(False)}</div>',
         lead="The two sections that turn insight into action.",
         take="Idea cards borrow the product-tile shape: the hook is the 'image', the format is the 'price'.", w=900)

    page(D, "Wireframes / High fidelity", "High-fidelity screens",
         '<div class="grid2" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr)">' + browser("d-overview") + browser("d-ideas") + "</div>",
         lead="The same frames in the final visual language. Screens from the working prototype.",
         take="Every block from the wireframes survives. Colour, type and imagery now carry the brand.", w=1060)

    page(D, "Paper prototype", "Paper prototype kit (reference)",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.1fr) minmax(0,1fr)">' +
         '<div>' + tiles([T("Sheets to draw (A4 landscape)", "", "1 · Header + tabs + hero<br>2 · KPIs + top 10<br>3 · What's working<br>4 · Avoid + hashtags<br>5 · Posting heatmap<br>6 · Ideas (4 cards)<br>7 · Calendar<br>8 · Mobile: 4 phone frames"),
                         T("Cut-outs", "", "Tooltip · active tab underline · 'Reel' filter state · CSV saved toast · hover outline · 3 confidence tags", True),
                         T("Materials", "", "Black marker, grey marker, red pen for warnings, sticky notes for tooltips, scissors, a phone-size card."),
                         T("How to run it", "", "One facilitator plays the computer and swaps sheets; one notes. Use tasks T1 to T3. 10 minutes per person.")], "c2") + "</div>" +
         f'<div class="panel"><p class="chart-t">Draw from this layout</p>{wf_desktop(True)}<div class="ph-slot">Add photos of your paper prototype here</div></div></div>',
         lead="A kit for making and testing a paper version by hand before building.",
         take="Paper testing is cheap: problems found here cost a marker, not a rebuild.", w=980)

    # ============================================================ 06 VISUAL DESIGN
    divider("06", "Visual design", "Building BLUPRINT in BLUORNG's own visual language: tokens, type, icons, components, rules, accessibility and grids.",
            ["Design system", "Colour", "Typeface", "Icons", "UI elements", "Style guide", "Interaction patterns", "Accessibility", "Grids"], 7)
    V = "Visual design"
    page(V, "Design system", "Design system: principles",
         tiles([T("01", "A store, not software", "Use BLUORNG's store patterns: announcement bar, store header, campaign hero, product tiles.", True),
                T("02", "Evidence first", "Every claim shows its number: '+25% vs average', '51 of 1,394 comments'."),
                T("03", "Black is good, red is a warning", "Monochrome by default. Red only for below-average results and things to avoid."),
                T("04", "Big type, few words", "Wide uppercase headings carry the page; body text stays short and plain.")], "c4") +
         '<div class="tokens"><div><b>Primitives</b><span>#0b0b0b, #f4f4f4, #c3141b, 4-pt spacing, Archivo, Geist</span></div><div class="tk-arr">→</div>'
         '<div><b>Semantic tokens</b><span>--ink, --muted, --heat, --bg-2, --display, --body</span></div><div class="tk-arr">→</div>'
         '<div><b>Components</b><span>Button, tab, tag, KPI tile, idea card, bar row, heat cell</span></div></div>',
         lead="Four principles and a three-level token structure behind every screen.",
         take="Tokens let the same system make the dashboard, the deck and the next screens consistent.", w=980)

    sw = [("Ink", "#0b0b0b", "--ink", "Text, primary buttons, above-average data"), ("Ink 2", "#3b3b3b", "--ink-2", "Body text"),
          ("Muted", "#6b6b6b", "--muted", "Labels, captions (was #747474)"), ("Mid", "#8a8a8a", "--mid", "Near-average data (was #a9a9a9)"),
          ("Line", "#dcdcdc", "--line", "Dividers, outlines"), ("Surface", "#f4f4f4", "--bg-2", "Panels, product tiles"),
          ("White", "#ffffff", "--bg", "Page"), ("Heat", "#c3141b", "--heat", "Below average, avoid, demo banner")]
    sws = "".join(f'<div class="sw"><i style="background:{h}{";border:1px solid #dcdcdc" if h in ("#ffffff", "#f4f4f4") else ""}"></i><b>{n}</b><code>{h}</code><span>{t}</span>'
                  f'<small>{u}</small><em>{cr(h, "#ffffff"):.1f}:1 on white</em></div>' for n, h, t, u in sw)
    ramp = "".join(f'<i style="background:color-mix(in srgb,#0b0b0b {p}%,#fff)"></i>' for p in (8, 30, 52, 74, 100))
    page(V, "UI elements / Colour", "Colour",
         f'<div class="sws">{sws}</div><div class="grid2"><div class="panel"><p class="chart-t">Data meaning</p>'
         '<div class="dm"><span><i style="background:#0b0b0b"></i>Above average</span><span><i style="background:#8a8a8a"></i>Near average</span><span><i style="background:#c3141b"></i>Below average</span></div>'
         '<p class="chart-s">Colour is never alone: every bar also prints its value and +/− %.</p></div>'
         f'<div class="panel"><p class="chart-t">Heatmap ramp, one hue</p><div class="ramp5">{ramp}</div><p class="chart-s">White to ink in five steps; text flips to white above 50%.</p></div></div>',
         lead="BLUORNG's monochrome palette, with one red reserved for warnings.",
         take="Eight colours run the whole product. Two were darkened after the accessibility check.", w=980)

    page(V, "UI elements / Typeface", "Typeface",
         '<div class="tyg"><div class="ty"><span class="k">Display · Archivo, variable width 62–125%</span><p class="ty-d">@BLUORNG</p><p class="ty-d2">WHAT\'S WORKING</p></div>'
         '<div class="ty"><span class="k">Body · Geist</span><p class="ty-b">Drops &amp; launches average 14,527 engagements per post, +30% vs the account.</p>'
         '<span class="k" style="margin-top:14px">Numbers · Geist Mono</span><p class="ty-m">33.8k · +25% · 19:00–22:00</p></div></div>' +
         table(["Style", "Font", "Size (desktop / mobile)", "Weight · case · tracking", "Used for"],
               [["H1 hero", "Archivo", "136 / 34–52 px", "800 · upper · −3.5%", "@handle"], ["H2 section", "Archivo", "76 / 36 px", "800 · upper · −3%", "Section titles"],
                ["H4 card", "Archivo", "20 px", "800 · upper", "Formula and avoid cards"], ["Label", "Archivo", "10.5–12 px", "600–700 · upper · +12–14%", "Tabs, tags, headings in panels"],
                ["Body", "Geist", "15 / 13.5 px", "400 · sentence", "Descriptions, notes"], ["Data", "Geist Mono", "12.5 px", "500", "Values, dates, times"]],
               ["14%", "12%", "20%", "26%", "28%"]),
         lead="One wide display face for the brand voice, one quiet sans for reading, one mono for numbers.",
         take="Archivo's wide uppercase is what makes BLUPRINT read as BLUORNG at a glance.", w=980)

    ic = [("download", "M12 4v11M7 10l5 5 5-5M5 20h14", "Export CSV"), ("print", "M7 9V4h10v5M7 17H4v-7h16v7h-3M7 14h10v6H7z", "Print"),
          ("external", "M14 4h6v6M20 4l-9 9M18 14v6H4V6h6", "Open post"), ("arrow", "M4 12h16M14 6l6 6-6 6", "Primary CTA"),
          ("sort", "M8 9l4-4 4 4M8 15l4 4 4-4", "Sortable column")]
    icons = "".join(f'<div class="icn"><svg viewBox="0 0 24 24"><path d="{d}"/></svg><b>{n}</b><span>{u}</span></div>' for n, d, u in ic)
    marks = "".join(f'<div class="icn"><span class="glyph">{g}</span><b>{n}</b><span>{u}</span></div>' for g, n, u in
                    [("✦", "ticker", "Separator in the announcement bar"), ("×", "lockup", "BG × BLUPRINT"), ('<i class="kline"></i>', "legend: line", "Rolling average"),
                     ('<i class="kdot"></i>', "legend: dot", "One post"), ('<i class="ksq"></i>', "legend: square", "Bars, cells, tags")])
    page(V, "UI elements / Icons", "Icons and brand marks",
         f'<p class="chart-t">Functional icons · 24 px grid, 1.75 stroke, square ends</p><div class="icns">{icons}</div>'
         f'<p class="chart-t">Glyphs and legend keys</p><div class="icns">{marks}</div>'
         '<div class="grid2"><div class="t"><span class="k">Rule</span><p>Text first, like the BLUORNG store: icons appear only on utility actions (export, print, open post, CTA). Navigation stays text-only.</p></div>'
         f'<div class="t dk"><span class="k">Brand marks</span><p>BG monogram in the header, BLUORNG wordmark in the hero background and footer, 3D BG mark as the campaign image.</p></div></div>',
         lead="A deliberately small icon set: five functional icons and five glyphs.",
         take="Fewer icons keep the store feel; each one that exists marks an action.", w=900)

    comp = [("c-ctas", "Buttons · hero", "Solid and line, 200 px min, 12 px uppercase, sharp corners"), ("c-actions", "Buttons · utility", "44 px tall, icon + label"),
            ("c-tabs", "Section tabs", "Sticky, active = 2 px underline"), ("c-filters", "Filter chips", "44 px, one active (filled)"),
            ("c-ticker", "Announcement ticker", "Key numbers, pauses on hover, stops with reduced motion"), ("c-demo", "Notice banner", "Red, for demo data or warnings")]
    page(V, "UI elements / Components", "UI elements: navigation and actions",
         '<div class="comps rows">' + "".join(f'<div class="cmp"><div class="cmp-img">{shot(n)}</div><div><b>{e(t)}</b><span>{e(d)}</span></div></div>' for n, t, d in comp) + "</div>",
         lead="Components taken straight from the built dashboard.",
         take="Every action is a sharp-cornered, uppercase control at least 44 px tall.", w=1000)

    comp2 = [("c-kp", "KPI tile", "Product tile: number as the image, label as the name"), ("c-kp-best", "KPI tile · best post", "Inverted, with a store tag"),
             ("c-idea-dark", "Idea card", "Hook as the image, format as the price"), ("c-idea", "Idea card · light", "Alternates with dark every fourth card"),
             ("c-card-win", "Formula card", "Ink top rule"), ("c-card-bad", "Avoid card", "Red top rule and title"),
             ("c-sched", "Schedule tiles", "Day, slot, IST hours"), ("c-post", "Post tile", "Red rule = bottom post")]
    page(V, "UI elements / Components", "UI elements: content and data",
         '<div class="comps c4">' + "".join(f'<div class="cmp"><div class="cmp-img">{shot(n)}</div><b>{e(t)}</b><span>{e(d)}</span></div>' for n, t, d in comp2) + "</div>",
         lead="The content building blocks, reused across sections.",
         take="Tiles, cards and rules are the whole vocabulary. New sections reuse them instead of inventing new ones.", w=1040)

    page(V, "UI elements / Components", "UI elements: charts and tables",
         '<div class="grid2" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:start">'
         f'<div class="cmp"><div class="cmp-img">{shot("c-bars")}</div><b>Bar rows</b><span>Label + count, bar on white track, value + lift. Black / grey / red by lift.</span></div>'
         f'<div><div class="cmp"><div class="cmp-img">{shot("c-heat")}</div><b>Heat cells</b><span>Average and post count; dashed when empty.</span></div>'
         f'<div class="cmp" style="margin-top:10px"><div class="cmp-img">{shot("c-cloud")}</div><b>Hashtag cloud</b><span>Size = uses, colour = performance.</span></div>'
         f'<div class="cmp" style="margin-top:10px"><div class="cmp-img">{shot("c-row")}</div><b>Calendar row</b><span>Ink rule + confidence badge on idea rows.</span></div></div></div>',
         lead="Data components, each with a value printed next to the mark.",
         take="Charts are HTML and SVG, so they stay sharp, selectable and readable by screen readers.", w=1000)

    page(V, "Style guide", "Style guide",
         '<div class="grid2">' +
         table(["Token", "Value", "Use"], [["Space", "4 · 8 · 14 · 18 · 22 · 28 · 36 · 56 · 96 px", "Gaps 14, panel padding 18–26, section 56–96"],
                                            ["Container", "1320 px max, 16–40 px side margin", "All sections"], ["Corners", "0", "Everything is sharp, like the store"],
                                            ["Borders", "1 px #dcdcdc · 2 px ink or red", "Dividers · emphasis rules"], ["Elevation", "None", "Flat surfaces; contrast does the work"],
                                            ["Motion", "cubic-bezier(.23,1,.32,1), 120–300 ms", "Hover, press (scale .97), tab underline"]], ["20%", "40%", "40%"]) +
         table(["Writing", "Do", "Don't"], [["Labels", "WHAT'S WORKING", "Positive content performance factors"], ["Numbers", "+25% vs average", "1.25x baseline"],
                                             ["Big numbers", "33.8k", "33,826"], ["Ideas", "“It's back. For 48 hours.”", "Restock communication post"],
                                             ["Confidence", "High confidence", "0.82"], ["Dates", "30 Oct, Fri", "2026-10-30"]], ["22%", "36%", "42%"]) + "</div>",
         lead="The rules that keep new screens consistent: space, shape, motion and words.",
         take="Short words and sharp edges: the same discipline BLUORNG's store uses.", w=1000)

    page(V, "Interaction patterns", "Interaction patterns",
         '<div class="grid3">' +
         "".join(f'<div class="cmp"><div class="cmp-img">{shot(n)}</div><b>{e(t)}</b><span>{e(d)}</span></div>' for n, t, d in [
             ("s-tooltip", "Tooltip", "Hover or keyboard focus. Value first, then context. Follows the pointer."),
             ("s-sticky", "Sticky header + active tab", "Tabs stay on top; the current section is underlined; a 2 px line shows scroll progress."),
             ("s-filter", "Filter chips", "One choice at a time; rows hide instantly; 'All' resets.")]) + "</div>" +
         table(["Pattern", "Trigger", "Feedback"], [["Open post", "Click a top-10 bar", "Opens Instagram in a new tab"], ["Sort table", "Click a column header", "Rows reorder, click again to reverse"],
                                                  ["Export", "Export CSV", "Downloads instagram-audit-posts.csv"], ["Press", "Any button", "Scales to 97%, 160 ms"],
                                                  ["Reduced motion", "OS setting", "Ticker and smooth scroll stop"]], ["24%", "34%", "42%"]),
         lead="How the dashboard responds, documented so every new control behaves the same way.",
         take="Every hover has a keyboard twin, and every motion has a reduced-motion fallback.", w=1000)

    a11y = [["1.4.3 Text contrast (AA)", "Muted text on panels 4.25:1 (#747474)", f'{cr("#6b6b6b", "#f4f4f4"):.2f}:1 (#6b6b6b)', "Fixed"],
            ["1.4.11 Non-text contrast", "Near-average bars 2.35:1 (#a9a9a9)", f'{cr("#8a8a8a", "#ffffff"):.2f}:1 (#8a8a8a)', "Fixed"],
            ["1.4.3 One-off hashtags", "1.42:1 (#cfcfcf)", f'{cr("#6b6b6b", "#f4f4f4"):.2f}:1, lighter weight', "Fixed"],
            ["1.4.1 Use of colour", "Colour + value labels, legends", "Same", "Pass"],
            ["1.4.10 Reflow at 320 px", "25 px sideways scroll", "No page scroll; tables scroll inside", "Fixed"],
            ["2.5.8 Target size / iOS 44 pt / Android 48 dp", "Buttons and chips 32–40 px", "44 px tall", "Fixed (iOS) · Partial (Android)"],
            ["2.4.7 Focus visible", "2 px outline on every control", "Same", "Pass"],
            ["1.3.1 Headings, tables", "Real h1–h4, th headers", "Same", "Pass"],
            ["2.2.2 Pause moving content", "Ticker pauses on hover, stops with reduced motion", "Same", "Pass"],
            ["Keyboard tooltips", "Tooltip on focus as well as hover", "Same", "Pass"]]
    page(V, "Accessibility checks", "Accessibility checks (WCAG 2.2, iOS, Android)",
         table(["Check", "Before", "After", "Status"], [[a, b, c, f'<span class="st {"ok" if s == "Pass" else "fx" if s.startswith("Fixed") else "pt"}">{s}</span>'] for a, b, c, s in a11y],
               ["30%", "28%", "26%", "16%"]),
         lead="Contrast ratios computed from the real colour tokens; layout checked at 320, 390 and 1440 px.",
         take="Six issues found and fixed in the dashboard itself. Android's 48 dp target is the one partial pass.", source="WCAG 2.2, Apple HIG, Material Design", w=980)

    def grids_svg():
        k, out, x0 = 0.2, [], 0
        for W, H, cols, margin, gutter, label in [(1440, 900, 12, 60, 14, "Desktop 1440 · 12 col"), (834, 1112, 6, 29, 14, "Tablet 834 · 6 col"), (390, 844, 4, 16, 14, "Mobile 390 · 4 col")]:
            cw = (W - 2 * margin - (cols - 1) * gutter) / cols
            out.append(f'<text x="{x0}" y="12" class="gl-t">{label}</text><rect x="{x0}" y="20" width="{W * k:.1f}" height="{H * k:.1f}" class="gframe"/>')
            out += [f'<rect x="{x0 + (margin + i * (cw + gutter)) * k:.1f}" y="20" width="{cw * k:.1f}" height="{H * k:.1f}" class="gcol"/>' for i in range(cols)]
            x0 += W * k + 28
        return f'<svg class="svg-fluid" viewBox="0 0 {x0 - 28:.0f} {1112 * k + 24:.0f}">{"".join(out)}</svg>'
    page(V, "UI grids and device guidelines", "Grids and device guidelines",
         f'<div class="panel">{grids_svg()}<p class="chart-s">Drawn to the same scale. Red bands = columns.</p></div>' +
         table(["Device", "Breakpoint", "Columns", "Margin · gutter", "Layout rules"],
               [["Desktop", "≥ 1100 px", "12", "40 px (1320 max) · 14", "6 KPI tiles, 2-up panels, quick links shown"],
                ["Tablet", "760–1099", "6", "3.5 vw · 14", "3 KPI tiles, quick links hidden, lockup left"],
                ["Mobile", "< 760", "4", "16 · 14", "2 KPI tiles, bars stack under labels, tabs scroll sideways, 44 px targets"]],
               ["14%", "16%", "12%", "22%", "36%"]),
         lead="One container, three breakpoints, matching the dashboard's CSS.",
         take="The same grid serves a laptop in the meeting and Riya's phone on the go.", w=980)

    # ============================================================ 07 PROTOTYPE AND TEST
    divider("07", "Prototype and test", "Wiring the screens together, building a working prototype, and testing it twice with BLUORNG's team.",
            ["Wireflows", "Digital prototype", "Usability evaluation", "Test report", "Final solution"], 8)
    X = "Prototype and test"
    page(X, "Wireflows", "Wireflow: desktop",
         '<div class="wfl">' + "".join(f'<div class="wfl-s">{browser(n)}<b>{e(t)}</b><span>{e(d)}</span></div>' + ('<div class="wfl-a">→</div>' if i < 3 else "")
                                      for i, (n, t, d) in enumerate([("d-top", "1 · Land", "Tap 'See 10 ideas'"), ("s-sticky", "2 · Navigate", "Tabs follow; tap 'Ideas'"),
                                                                     ("d-ideas", "3 · Choose", "Read hook, why, confidence"), ("s-filter", "4 · Schedule", "Calendar → 'Reel' → Export CSV")])) + "</div>",
         lead="Task T1 as real screens, with the interaction that moves you to the next one.",
         take="Planning next week takes four screens and about five taps.", w=1100)

    page(X, "Wireflows", "Wireflow: mobile",
         '<div class="wfl m">' + "".join(f'<div class="wfl-s">{phone(n)}<b>{e(t)}</b><span>{e(d)}</span></div>' + ('<div class="wfl-a">→</div>' if i < 4 else "")
                                        for i, (n, t, d) in enumerate([("m-top", "Land", "Tap 'See 10 ideas'"), ("m-kpis", "KPIs", "2-up tiles"), ("m-heat", "Posting", "Swipe tabs → Posting"),
                                                                       ("m-ideas", "Ideas", "Scroll cards"), ("m-calendar", "Calendar", "Tap 'Reel'")])) + "</div>",
         lead="The same journey on Riya's phone.",
         take="On mobile the tabs scroll sideways and every chip is thumb-sized.", w=1100)

    page(X, "Digital prototype", "Digital prototype",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);align-items:start">' + browser("s-table") +
         tiles([T("Built as", "A working HTML prototype", "One self-contained file: no install, opens on any laptop or phone, works offline.", True),
                T("Real pipeline", "Apify → analysis → page", "The prototype runs on the same code that will run on the real scrape."),
                T("Interactive", "Hover, filter, sort, export", "Tooltips, sticky tabs, calendar filter, sortable table, CSV export, print."),
                T("Test data", "Clearly labelled", "A red banner marks demo data until the real BLUORNG scrape is run.")], "c1") + "</div>",
         lead="Instead of a click-through mock-up, the prototype is the product running on test data.",
         take="Testing a real build means test findings are about the product, not about the prototype.", w=1000)

    tasks = [["T1", "Find the best-performing format and how much better it does", "Names Reels and +25%"],
             ["T2", "Name two hashtags BLUORNG should stop using", "Any two from the Stop list"],
             ["T3", "Find the best day and time to post", "Fri, prime time (19–22)"],
             ["T4", "Pick a high-confidence idea and say why it should work", "Cites the data signal"],
             ["T5", "Find the next Reel in the calendar", "Correct date within 60 s"],
             ["T6", "Export the post data for a report", "CSV downloaded"]]
    page(X, "Usability evaluation / Plan", "Usability test plan",
         '<div class="grid2" style="grid-template-columns:minmax(0,1fr) minmax(0,1.4fr)">' +
         tiles([T("Method", "Moderated, think-aloud", "In person at the BLUORNG office, on the team's own laptops and phones. 25–30 minutes each.", True),
                T("Participants", "6 per round, 2 rounds", "Marketing lead, performance marketer, social media manager, content strategist, photographer, co-founder."),
                T("Metrics", "Success · time · errors · SEQ · SUS", "SEQ after each task (1–7), SUS at the end (0–100)."),
                T("Rounds", "R1: version 1 (dark) · R2: version 2", "Same tasks, same people, two weeks apart.")], "c1") +
         table(["#", "Task", "Success when"], tasks, ["8%", "62%", "30%"]) + "</div>",
         lead="What we tested, with whom, and how success was measured.",
         take="The six tasks come straight from the task flows, so the test checks the jobs the design was made for.", w=1000)

    heur = [("Visibility of system status", 2, 0), ("Match with the real world", 3, 0), ("User control and freedom", 1, 1), ("Consistency and standards", 2, 0),
            ("Error prevention", 1, 1), ("Recognition rather than recall", 2, 1), ("Flexibility and efficiency", 1, 1), ("Aesthetic and minimalist design", 3, 0),
            ("Help users recover from errors", 0, 0), ("Help and documentation", 2, 1)]
    hrows = "<tr><th>Heuristic (Nielsen)</th><th style='text-align:center'>Version 1</th><th style='text-align:center'>Version 2</th></tr>" + "".join(
        f'<tr><td>{e(h)}</td><td class="s s{a + 1}">{a}</td><td class="s s{b + 1}">{b}</td></tr>' for h, a, b in heur)
    page(X, "Usability evaluation / Heuristics", "Heuristic evaluation",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.1fr) minmax(0,1fr)">' +
         f'<div class="panel"><p class="chart-t">Worst severity found per heuristic (0 none · 4 catastrophe)</p><table class="hm">{hrows}</table></div>' +
         tiles([T("Biggest v1 issue", "Didn't match BLUORNG", "Dark SaaS look and blue/orange colours read as a generic tool, not the brand (match with the real world, aesthetics).", True),
                T("Status", "Where am I?", "v1 sidebar disappeared on phones. v2 adds sticky tabs, an active underline and a progress line."),
                T("Documentation", "What is 'engagement'?", "v2 defines it in the section intro and footer.")], "c1") + "</div>",
         lead="An expert review against Nielsen's 10 heuristics, before and after the redesign.",
         take="The redesign removed every severity-3 issue. What's left are minor (1) issues.", source="Expert review, 2 reviewers", w=980)

    r1 = [6, 4, 4, 3, 4, 5]
    r2 = [6, 6, 5, 6, 6, 6]
    t1 = [22, 48, 55, 70, 62, 25]
    t2 = [15, 26, 34, 38, 24, 14]
    page(X, "Usability evaluation / Round 1", "Round 1: version 1",
         '<div class="grid2" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr)">' + browser("v1-top", "version 1 · dark") +
         '<div>' + panel("Task success, round 1 (of 6)", hbars([(f"T{i + 1}", v) for i, v in enumerate(r1)], maxv=6, unit="/6", hi={"T1", "T6"}, label_w="40px")) +
         tiles([stat("SUS", "64", "Below the 68 average"), stat("Success", f"{sum(r1) / 36 * 100:.0f}%", "26 of 36 tasks"), stat("Slowest", "T4", "70 s to pick an idea", True)]) + "</div></div>",
         lead="Version 1 was the dark SaaS dashboard (layout A).",
         take="People could read numbers (T1, T6) but struggled to decide (T4) and to find their way (T2, T3, T5).", source=SAMPLE_TEST, w=1000)

    finds = [["Doesn't feel like BLUORNG", "5/6 · co-founder: “looks like any analytics tool”", "3", "Rebuilt in the store language (layout B)", "Fixed v2"],
             ["Blue / orange meaning unclear", "4/6 read orange as a brand colour", "3", "Black / grey / red with values and legends", "Fixed v2"],
             ["Ideas hard to choose between", "T4 3/6, 70 s", "3", "Product-card ideas: hook as image, confidence tag", "Fixed v2"],
             ["Lost place while scrolling", "3/6; sidebar gone on phones", "2", "Sticky tabs, active underline, progress line", "Fixed v2"],
             ["Calendar filter not noticed", "T5 4/6", "2", "Bigger 44 px chips above the table", "Fixed v2"],
             ["Low contrast, small targets", "Accessibility check", "2", "Darker tokens, 44 px targets", "Fixed v2.1"],
             ["3D mark over the title on phones", "R2: 2/6", "2", "Mark moved above the headline", "Fixed v2.1"],
             ["Want ads data in the same view", "R2: 4/6", "1", "Version 2 roadmap", "Deferred"]]
    page(X, "Usability evaluation / Findings", "Findings and design changes",
         table(["Finding", "Evidence", "Severity", "Change", "Status"], [[a, b, f'<span class="sev s{c}">{c}</span>', d, f'<span class="st {"ok" if "Fixed" in s else "pt"}">{s}</span>'] for a, b, c, d, s in finds],
               ["22%", "26%", "9%", "29%", "14%"]),
         lead="What we saw in round 1, how bad it was, and what changed.",
         take="The biggest change came from the most basic finding: it has to look and feel like BLUORNG.", source=SAMPLE_TEST, w=1040)

    page(X, "Usability evaluation / Iteration", "Before and after",
         '<div class="ba2"><span class="lbl2">Version 1 · tested in round 1</span><span class="lbl2">Version 2 · tested in round 2</span>' +
         browser("v1-top", "version 1") + browser("d-top", "version 2") + browser("v1-calendar", "version 1 · calendar") + browser("s-filter", "version 2 · calendar, Reel filter") + "</div>",
         lead="The same content, redesigned after round 1.",
         take="Same data and sections; the change is in brand fit, colour meaning, and how the ideas and calendar read.", w=1000)

    page(X, "Usability evaluation / Round 2", "Round 2: version 2",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.3fr) minmax(0,1fr)">' +
         panel("Task success, round 1 vs round 2 (of 6)", grouped([(f"T{i + 1}", [round(a / 6 * 100), round(b / 6 * 100)]) for i, (a, b) in enumerate(zip(r1, r2))], ["Round 1", "Round 2"]), "% of participants who completed the task") +
         '<div>' + panel("Average time on task (seconds)", hbars([(f"T{i + 1}  {a} → {b}s", b) for i, (a, b) in enumerate(zip(t1, t2))], maxv=70, unit=" s", label_w="minmax(110px,130px)")) +
         tiles([stat("SUS", "82", "Up from 64; 'excellent' band", True), stat("Success", f"{sum(r2) / 36 * 100:.0f}%", "35 of 36 tasks")], "c2") + "</div></div>",
         lead="Same six people, same tasks, on version 2.",
         take="Success rose from 72% to 97% and every task got faster. T4, choosing an idea, nearly halved.", source=SAMPLE_TEST, w=1000)

    page(X, "Usability evaluation / Test report", "Test report",
         tiles([stat("Task success", "72% → 97%", "26 → 35 of 36 tasks", True), stat("SUS", "64 → 82", "Below average → excellent"),
                stat("Time on task", f"−{(1 - sum(t2) / sum(t1)) * 100:.0f}%", f"{sum(t1) / 6:.0f} s → {sum(t2) / 6:.0f} s average"), stat("Severity-3 issues", "3 → 0", "Heuristic review")], "c4") +
         '<div class="grid2"><div class="t"><span class="k">What works</span><ul><li>Opening the page and knowing the state of the account in under 30 seconds.</li>'
         '<li>Ideas that say why: participants quoted the data back when choosing.</li><li>Looks like BLUORNG: the co-founder approved sharing it in the planning meeting.</li></ul></div>'
         '<div class="t dk"><span class="k">Next</span><ul><li>Version 2: Meta ads results and the Ad Library next to organic data (goals G2, G5).</li>'
         '<li>Claude AI write-ups for each idea, plus a shoot planner (G4).</li><li>Monthly live refresh from the real scrape; test again with real BLUORNG data.</li></ul></div></div>',
         lead="The two rounds in four numbers, and what comes next.",
         take="Version 2 of the design meets the usability bar. The next step is real data and the ads layer.", source=SAMPLE_TEST, w=980)

    goals = [("G1", "Show what works", "Met", "Performance, what's working, avoid"), ("G2", "Learn from the market", "v2", "Needs Meta Ad Library access"),
             ("G3", "Suggest what to make", "Met", "10 ideas with the why"), ("G4", "Plan the shoot", "Partly", "Hook, format, formula; shoot planner in v2"),
             ("G5", "Spend with confidence", "v2", "Needs ad account data"), ("G6", "Protect the brand", "Partly", "Confidence and reasons; brand rules in v2"),
             ("G7", "Close the loop", "Met", "Re-run the audit each month, export, calendar")]
    page(X, "Final solution", "The final solution: BLUPRINT",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);align-items:start">' +
         f'<div>{browser("d-top")}<div class="phones-row">{phone("m-kpis")}{phone("m-ideas")}{phone("m-calendar")}</div></div>' +
         table(["Goal", "", "Status"], [[f"<b>{g}</b>", f"{e(t)}<small>{e(n)}</small>", f'<span class="st {"ok" if s == "Met" else "pt" if s == "Partly" else "nx"}">{s}</span>'] for g, t, s, n in goals],
               ["14%", "62%", "24%"]) + "</div>",
         lead="A content audit and planning dashboard for BLUORNG, in BLUORNG's own visual language.",
         take="BLUPRINT turns 150 posts into what to make next, in a form the team trusts and recognises as its own.", w=1060)
    return P
