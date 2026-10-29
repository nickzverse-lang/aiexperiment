"""STEP 10: render the audit as one self-contained HTML dashboard (no external files, fonts or scripts).

Run:  python3 tools/bluprint/dashboard.py <apify_export.json> --handle bluorng [--limit 150] [--out docs/bluprint/dashboard.html]
                                         [--demo] [--date 2026-10-29]
Also writes <out>.md, the written audit (steps 3 to 9) behind the dashboard.
"""
import argparse
import datetime as dt
import base64
import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import analyze as A  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
e = html.escape


def k(v):
    v = float(v)
    return f"{v / 1e6:.1f}M" if v >= 1e6 else f"{v / 1e3:.1f}k" if v >= 1e4 else f"{v:,.0f}"


def sign(v):
    return f"{v:+.0f}%"


def snip(cap, n=70):
    line = A.first_line(cap) or "(no caption)"
    return line if len(line) <= n else line[: n - 1] + "…"


def tone(lift, band=8):
    return "up" if lift >= band else "down" if lift <= -band else "flat"


def date(p):
    return p["ts"].strftime("%d %b %Y")


def tip(*lines):
    return e(" | ".join(str(x) for x in lines), quote=True)


def logo(name="monogram", cls="logo"):
    svg = (ROOT / f"tools/book/brand/{name}.svg").read_text()
    return svg.replace('<svg xmlns="http://www.w3.org/2000/svg"', f'<svg class="{cls}" aria-hidden="true" focusable="false"')


ICONS = {  # 24 px grid, 1.75 stroke, square caps: the dashboard's whole icon set
    "download": "M12 4v11M7 10l5 5 5-5M5 20h14", "print": "M7 9V4h10v5M7 17H4v-7h16v7h-3M7 14h10v6H7z",
    "external": "M14 4h6v6M20 4l-9 9M18 14v6H4V6h6", "arrow": "M4 12h16M14 6l6 6-6 6", "sort": "M8 9l4-4 4 4M8 15l4 4 4-4",
}


def ico(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICONS[name]}"/></svg>'


def b64(path):
    return base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def font_faces():
    f = pathlib.Path(__file__).resolve().parent / "fonts"
    faces = [("Archivo", "archivo-latin-wdth-normal.woff2", "100 900", "font-stretch: 62% 125%;"),
             ("Geist", "geist-sans-latin-400-normal.woff2", "400", ""), ("Geist", "geist-sans-latin-500-normal.woff2", "500", ""),
             ("Geist", "geist-sans-latin-600-normal.woff2", "600", ""), ("Geist Mono", "geist-mono-latin-500-normal.woff2", "400 600", "")]
    return "".join(f'@font-face {{ font-family: "{n}"; src: url(data:font/woff2;base64,{b64(f / fn)}) format("woff2"); font-weight: {w}; font-display: swap; {x} }}\n'
                   for n, fn, w, x in faces)


def hbar_rows(rows, maxv, cls="", label_w="minmax(160px,1.3fr)"):
    out = []
    for r in rows:
        w = r["v"] / maxv * 100 if maxv else 0
        href = f' href="{e(r["url"])}" target="_blank" rel="noopener"' if r.get("url") else ""
        tag = "a" if href else "div"
        out.append(f'<{tag} class="hb {r.get("tone", cls)}"{href} style="grid-template-columns:{label_w} minmax(0,2fr) 92px" tabindex="0" data-tip="{r["tip"]}">'
                   f'<span class="hb-l">{r["label"]}</span><span class="hb-t"><i style="width:{max(w, .6):.1f}%"></i></span><b>{r["value"]}</b></{tag}>')
    return '<div class="hbs">' + "".join(out) + "</div>"


def kpis(a):
    s = a["snapshot"]
    best = s["top5"][0]
    tr = s["trend"]
    cards = [("Posts analysed", str(s["n"]), f'{dt.date.fromisoformat(s["first"]).strftime("%d %b")} – {dt.date.fromisoformat(s["last"]).strftime("%d %b %Y")}', ""),
             ("Avg likes", "Hidden" if s["likes_hidden"] else k(s["avg_likes"]), "Per post" if not s["likes_hidden"] else "Likes hidden", ""),
             ("Avg comments", k(s["avg_comments"]), f'Median eng. {k(s["median_eng"])}', ""),
             ("Engagement trend", tr["direction"], f'{sign(tr["fit_change"])} over the period', tone(tr["fit_change"], 10)),
             ("Best format", s["best_type"]["name"] + "s", f'{sign(s["best_type"]["lift"])} vs average', "")]
    out = "".join(f'<article class="kp {t}"><div class="kp-shot"><b>{v}</b></div><div class="kp-meta"><h3>{e(l)}</h3><span>{sub}</span></div></article>'
                  for l, v, sub, t in cards)
    out += (f'<a class="kp best" href="{e(best["url"])}" target="_blank" rel="noopener"><div class="kp-shot"><span class="stag">No. 1 post</span><b>{k(best["eng"])}</b>'
            f'<q>{e(snip(best["caption"], 64))}</q></div><div class="kp-meta"><h3>Best post</h3><span>{e(best["type"])} · {best["ts"].strftime("%d %b")}</span></div></a>')
    return f'<div class="kpis">{out}</div>'


def top10(a):
    s = a["snapshot"]
    rows = [dict(label=f'<em>{i + 1:02d}</em><span>{e(p["type"])} · {p["ts"].strftime("%d %b")}</span><small>{e(snip(p["caption"], 46))}</small>',
                 v=p["eng"], value=k(p["eng"]), url=p["url"],
                 tip=tip(f'{p["eng"]:,} engagements', f'{p["likes"] or 0:,} likes, {p["comments"]:,} comments', f'{p["type"]}, {date(p)}', p["cluster"]))
            for i, p in enumerate(s["top10"])]
    return hbar_rows(rows, s["top10"][0]["eng"], "up", "minmax(200px,1.4fr)")


def timeline(a):
    posts = sorted(a["posts"], key=lambda p: p["ts"])
    W, H, L, B, T = 900, 260, 52, 30, 14
    t0, t1 = posts[0]["ts"].timestamp(), posts[-1]["ts"].timestamp()
    ymax = max(p["eng"] for p in posts) * 1.08
    xs = lambda p: L + (p["ts"].timestamp() - t0) / ((t1 - t0) or 1) * (W - L - 10)
    ys = lambda v: T + (1 - v / ymax) * (H - T - B)
    grid = ""
    for i in range(5):
        v = ymax * i / 4
        grid += f'<line x1="{L}" x2="{W - 10}" y1="{ys(v):.1f}" y2="{ys(v):.1f}" class="gl"/><text x="{L - 8}" y="{ys(v) + 4:.1f}" text-anchor="end" class="ax">{k(v)}</text>'
    months, seen = "", set()
    for p in posts:
        m = p["ts"].strftime("%b")
        if m not in seen and p["ts"].day <= 10:
            seen.add(m)
            months += f'<text x="{xs(p):.1f}" y="{H - 8}" class="ax" text-anchor="middle">{m}</text>'
    roll, pts = [], []
    for i, p in enumerate(posts):
        win = posts[max(0, i - 9): i + 1]
        roll.append((xs(p), ys(A.mean(q["eng"] for q in win))))
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in roll)
    base = A.mean(p["eng"] for p in posts)
    for p in posts:
        cls = "up" if p["eng"] >= base * 1.08 else "down" if p["eng"] <= base * .92 else "flat"
        pts.append(f'<g class="dot {cls}" tabindex="0" data-tip="{tip(f"{p["eng"]:,} engagements", p["type"] + ", " + date(p), snip(p["caption"], 50))}">'
                   f'<circle cx="{xs(p):.1f}" cy="{ys(p["eng"]):.1f}" r="10" class="hit"/><circle cx="{xs(p):.1f}" cy="{ys(p["eng"]):.1f}" r="3.6"/></g>')
    avg = f'<line x1="{L}" x2="{W - 10}" y1="{ys(base):.1f}" y2="{ys(base):.1f}" class="avg"/>'
    avg_lab = f'<text x="{L + 6}" y="{ys(base) - 7:.1f}" class="ax halo">account avg {k(base)}</text>'
    return (f'<div class="chart-wrap"><svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Engagement per post over time">{grid}{months}{avg}'
            f'<g>{"".join(pts)}</g><path d="{line}" class="roll"/>{avg_lab}</svg></div>'
            '<div class="legend"><span><i class="lk line"></i>10-post rolling average</span><span><i class="lk dot up"></i>Above average</span>'
            '<span><i class="lk dot down"></i>Below average</span><span><i class="lk dot flat"></i>Near average</span></div>')


def lift_bars(rows, label_w="minmax(190px,1.3fr)"):
    mx = max(r["avg"] for r in rows) or 1
    return hbar_rows([dict(label=f'<span>{e(r["name"])}</span><small>{r["n"]} posts</small>', v=r["avg"], value=f'{k(r["avg"])} <small>{sign(r["lift"])}</small>',
                           tone=tone(r["lift"]), tip=tip(f'{r["avg"]:,.0f} avg engagements', f'{sign(r["lift"])} vs account average', f'{r["n"]} posts, median {r["median"]:,.0f}'))
                      for r in rows], mx, label_w=label_w)


def hooks(a):
    w = a["working"]
    rows = "".join(f'<tr><td>{e(h["name"])}</td><td class="num">{h["n"]}</td><td class="num">{h["share_all"]:.0f}%</td>'
                   f'<td class="num"><b>{h["share_top"]:.0f}%</b></td><td class="num {tone(h["lift"])}">{sign(h["lift"])}</td></tr>' for h in w["hooks"])
    return (f'<div class="tbl-wrap"><table class="tbl hooks"><thead><tr><th>Hook style (first line)</th><th class="num">Posts</th><th class="num">Share of all</th>'
            f'<th class="num">Share of top {w["top_k"]}</th><th class="num">Avg vs account</th></tr></thead><tbody>{rows}</tbody></table></div>'
            '<p class="note">Share of top 10% higher than share of all = the hook shows up more among winners.</p>')


def cta_block(a):
    c = a["working"]["cta"]
    mx = max(c["yes_avg"], c["no_avg"]) or 1
    rows = [dict(label=f'<span>With a CTA</span><small>{c["yes_n"]} posts</small>', v=c["yes_avg"], value=k(c["yes_avg"]), tone=tone(c["lift"]),
                 tip=tip(f'{c["yes_avg"]:,.0f} avg engagements', f'{c["yes_n"]} posts with a call to action')),
            dict(label=f'<span>No CTA</span><small>{c["no_n"]} posts</small>', v=c["no_avg"], value=k(c["no_avg"]), tone="flat",
                 tip=tip(f'{c["no_avg"]:,.0f} avg engagements', f'{c["no_n"]} posts without a call to action'))]
    return hbar_rows(rows, mx) + f'<p class="note">CTA posts perform <b>{sign(c["lift"])}</b> vs posts without one. CTA = link in bio, shop, comment, tag, visit, DM, save, pre-order.</p>'


def formulas(a):
    s, w, h, ps = a["snapshot"], a["working"], a["hashtags"], a["posting"]
    cl = w["all_clusters"]
    pool = [x for x in w["hooks"] if x["n"] >= 3 and x["share_top"] >= x["share_all"]] or [x for x in w["hooks"] if x["n"] >= 3]
    best_hook = max(pool, key=lambda x: x["lift"])
    items = [
        ("Format", f'{s["best_type"]["name"]}s lead', f'{s["best_type"]["name"]}s average {k(s["best_type"]["avg"])} engagements, {sign(s["best_type"]["lift"])} vs the account.'),
        ("Topic", f'{cl[0]["name"]} and {cl[1]["name"].lower()}', f'The two strongest topics: {sign(cl[0]["lift"])} and {sign(cl[1]["lift"])} vs average.'),
        ("Hook", best_hook["name"], f'Opens {best_hook["n"]} posts and averages {sign(best_hook["lift"])}; it is {best_hook["share_top"]:.0f}% of the top {w["top_k"]}.'),
        ("Caption", w["best_length"]["name"], f'Best caption length, {sign(w["best_length"]["lift"])} vs average across {w["best_length"]["n"]} posts.'),
        ("Timing", " and ".join(d["name"] for d in ps["best_days"][:2]) + (f', {ps["best_slots"][0]["name"].lower()}' if ps["best_slots"] else ""),
         f'Best days by average engagement: ' + ", ".join(f'{d["name"]} {sign(d["lift"])}' for d in ps["best_days"]) + "."),
        ("Hashtags", "Few and specific", f'Posts use {h["per_post"]:.1f} tags on average. {len(h["keep"])} tags beat the average; {len(h["stop"])} drag it down.'),
    ]
    return '<div class="cards c3">' + "".join(f'<div class="card win"><span class="kk">{e(a_)}</span><h4>{e(b)}</h4><p>{e(c)}</p></div>' for a_, b, c in items) + "</div>"


def avoid(a):
    w, h = a["working"], a["hashtags"]
    items = []
    for x in w["avoid"][:4]:
        items.append((x["feature"].capitalize(), x["value"], f'{x["bottom_share"]:.0f}% of the bottom {w["top_k"]} posts vs {x["all_share"]:.0f}% of all posts.'))
    worst = w["all_clusters"][-1]
    items.append(("Topic", worst["name"], f'Weakest topic: {k(worst["avg"])} avg, {sign(worst["lift"])} vs account, {worst["n"]} posts.'))
    wh = min((x for x in w["hooks"] if x["n"] >= 3), key=lambda x: x["lift"])
    items.append(("Hook", wh["name"], f'Averages {sign(wh["lift"])} and is {wh["share_top"]:.0f}% of top posts.'))
    wl = min((x for x in w["lengths"] if x["n"] >= 2), key=lambda x: x["lift"])
    items.append(("Caption", wl["name"], f'{sign(wl["lift"])} vs average across {wl["n"]} posts.'))
    if h["stop"]:
        items.append(("Hashtags", "Generic reach tags", "Posts with " + ", ".join("#" + t["tag"] for t in h["stop"][:4]) + " sit below average."))
    seen, out = set(), []
    for it in items:
        if it[1] not in seen:
            seen.add(it[1]); out.append(it)
    return '<div class="cards c3">' + "".join(f'<div class="card bad"><span class="kk">{e(a_)}</span><h4>{e(b)}</h4><p>{e(c)}</p></div>' for a_, b, c in out[:6]) + "</div>"


def bottom_list(a):
    rows = "".join(f'<li><a href="{e(p["url"])}" target="_blank" rel="noopener"><b>{k(p["eng"])}</b><span>{e(p["type"])} · {date(p)} · {e(p["cluster"])}</span>'
                   f'<small>{e(snip(p["caption"], 60))}</small></a></li>' for p in a["working"]["bottom"][::-1])
    return f'<ul class="plist">{rows}</ul>'


def cloud(a):
    tags = a["hashtags"]["all"][:60]
    if not tags:
        return '<p class="note">No hashtags used in this sample.</p>'
    mx = max(t["n"] for t in tags)
    out = []
    for t in sorted(tags, key=lambda t: t["tag"]):
        size = 12 + (t["n"] / mx) ** .5 * 26
        cls = "one" if t["n"] < 2 else "up" if t["index"] >= 1.08 else "down" if t["index"] <= .92 else "flat"
        out.append(f'<span class="tag {cls}" style="font-size:{size:.0f}px" tabindex="0" data-tip="{tip(f"{t["n"]} posts", f"{t["avg"]:,.0f} avg engagements ({(t["index"] - 1) * 100:+.0f}%)", f"in top quarter {t["in_top"]}x, bottom quarter {t["in_bottom"]}x")}">#{e(t["tag"])}</span>')
    return ('<div class="cloud">' + "".join(out) + '</div><div class="legend"><span><i class="lk sq up"></i>Above average</span>'
            '<span><i class="lk sq flat"></i>Near average</span><span><i class="lk sq down"></i>Below average</span><span><i class="lk sq one"></i>Used once</span><span>Size = how often it is used</span></div>')


def tag_lists(a):
    h = a["hashtags"]
    keep = "".join(f'<li><b>#{e(t["tag"])}</b><span>{t["n"]} posts · {(t["index"] - 1) * 100:+.0f}%</span></li>' for t in h["keep"][:10]) or "<li>No tag clears the average yet.</li>"
    try_ = "".join(f'<li><b>#{e(t["tag"])}</b><span>{e(t["theme"])}</span></li>' for t in h["try_"])
    stop = "".join(f'<li><b>#{e(t["tag"])}</b><span>{t["n"]} posts · {(t["index"] - 1) * 100:+.0f}%</span></li>' for t in h["stop"][:10]) or "<li>Nothing to drop.</li>"
    return (f'<div class="cards c3"><div class="card"><span class="kk">Keep using</span><ul class="tl up">{keep}</ul></div>'
            f'<div class="card"><span class="kk">Try these</span><ul class="tl new">{try_}</ul></div>'
            f'<div class="card"><span class="kk">Stop using</span><ul class="tl down">{stop}</ul></div></div>'
            f'<p class="note">Posts without hashtags: {h["no_tag_n"]}, averaging {k(h["no_tag_avg"])}. Posts with hashtags average {k(h["tag_avg"])}. '
            f'Keep = used 2+ times and at or above average. Stop = used 2+ times and 20% below average, or only seen in the bottom quarter.</p>')


def heatmap(a):
    ps = a["posting"]
    vals = [c["avg"] for row in ps["heat"] for c in row if c["n"]]
    lo, hi = min(vals), max(vals)
    head = '<span></span>' + "".join(f'<span class="hh"><span class="hn">{e(n)}</span><small>{s_:02d}-{e_:02d}</small></span>' for n, s_, e_ in A.SLOTS)
    body = ""
    for d, row in enumerate(ps["heat"]):
        body += f'<span class="hd">{A.DAYS[d]}</span>'
        for si, c in enumerate(row):
            if not c["n"]:
                body += '<span class="hc empty" aria-label="no posts">·</span>'
                continue
            t = (c["avg"] - lo) / ((hi - lo) or 1)
            body += (f'<span class="hc{" dk" if t > .5 else ""}" tabindex="0" style="--p:{8 + t * 92:.0f}%" data-tip="{tip(f"{c["avg"]:,.0f} avg engagements", f"{A.DAYS[d]}, {A.SLOTS[si][0]} (IST)", f"{c["n"]} posts")}">'
                     f'<b>{k(c["avg"])}</b><small>{c["n"]}</small></span>')
    return (f'<div class="heat">{head}{body}</div><div class="legend"><span class="ramp"><i style="--p:8%"></i><i style="--p:38%"></i><i style="--p:69%"></i><i style="--p:100%"></i></span>'
            f'<span>Avg engagement, low to high ({k(lo)} to {k(hi)})</span><span>Small number = posts in that slot</span><span>Times in IST</span></div>')


def frequency(a):
    ps = a["posting"]
    fr = "".join(f'<li><b>{e(name)}/week</b><span>{v["n"]} weeks · {k(v["avg"])} avg</span></li>' for name, v in sorted(ps["freq"].items()))
    gp = "".join(f'<li><b>{e(name)}</b><span>{v["n"]} posts · {k(v["avg"])} avg</span></li>' for name, v in ps["gaps"].items())
    r = ps["weekly_r"]
    verdict = "more posts in a week go with higher engagement per post" if r > .2 else "more posts in a week go with lower engagement per post" if r < -.2 else "posting frequency has little effect on engagement per post"
    return (f'<div class="cards c2"><div class="card"><span class="kk">Posts per week</span><ul class="tl">{fr}</ul></div>'
            f'<div class="card"><span class="kk">Gap since previous post</span><ul class="tl">{gp}</ul></div></div>'
            f'<p class="note">Currently {ps["per_week"]:.1f} posts a week. Weekly correlation r = {r:+.2f}: {verdict}.</p>')


def schedule(a):
    ps = a["posting"]
    return ('<div class="sched">' + "".join(f'<div><b>{e(s["day"])}</b><span>{e(s["slot"])}</span><small>{e(s["hours"])} IST</small></div>' for s in ps["schedule"]) + "</div>"
            f'<p class="note">{ps["rec_per_week"]} feed posts a week on the strongest days, plus daily Stories. Days with too few posts in the sample are not ranked.</p>')


def sentiment(a):
    se = a["sentiment"]
    names = [n for n, _ in A.EMOTIONS]
    mx = max(max(se["top"].values()), max(se["all"].values()), 1)
    rows = ""
    for n in names:
        t, al = se["top"][n], se["all"][n]
        rows += (f'<div class="gb"><span class="gb-l">{e(n)}</span><div class="gb-b">'
                 f'<div class="hb-t up" tabindex="0" data-tip="{tip(f"{t:.0f}% of comments", "Top 10% posts", n)}"><i style="width:{t / mx * 100:.1f}%"></i></div>'
                 f'<div class="hb-t flat" tabindex="0" data-tip="{tip(f"{al:.0f}% of comments", "All posts", n)}"><i style="width:{al / mx * 100:.1f}%"></i></div></div>'
                 f'<b>{t:.0f}%<small>{al:.0f}%</small></b></div>')
    leg = '<div class="legend"><span><i class="lk sq up"></i>Top 10% posts</span><span><i class="lk sq flat"></i>All posts</span><span>Share of comments showing each reaction</span></div>'
    asks = se["asks"][:8]
    amx = max((c for _, c in asks), default=1)
    ask_rows = hbar_rows([dict(label=f"<span>{e(n)}</span>", v=c, value=str(c), tone="up", tip=tip(f"{c} comments", n)) for n, c in asks], amx) if asks else '<p class="note">No comment text in this export.</p>'
    quotes = "".join(f"<li>“{e(q)}”</li>" for q in se["samples"])
    return (f'<div class="grid g2"><div class="panel"><h3>What top posts make people feel</h3>{rows and "<div class=gbs>" + rows + "</div>"}{leg}</div>'
            f'<div class="panel"><h3>What the audience asks for</h3>{ask_rows}<p class="note">From {se["n_comments"]:,} recent comments on the analysed posts.</p>'
            f'<ul class="quotes">{quotes}</ul></div></div>')


def idea_cards(a):
    out = []
    for i, x in enumerate(a["ideas"], 1):
        c = x["confidence"].lower()
        out.append(f'<article class="idea" data-format="{e(x["format"])}"><div class="idea-shot"><span class="stag {c}">{x["confidence"]} confidence</span>'
                   f'<span class="no">{i:02d}</span><p class="hook">{e(x["hook"])}</p></div>'
                   f'<div class="idea-meta"><h3>{e(x["title"])}</h3><span>{e(x["format"])}</span></div>'
                   f'<dl><dt>Why it will work</dt><dd>{e(x["why"])}</dd><dt>Formula</dt><dd>{e(x["formula"])}</dd>'
                   f'<dt>Caption opener</dt><dd>“{e(x["opener"])}”</dd></dl></article>')
    return '<div class="ideas">' + "".join(out) + "</div>"


def calendar(a):
    cal = a["calendar"]
    rows = ""
    for r in cal["rows"]:
        d = dt.date.fromisoformat(r["date"])
        badge = f' <span class="badge {r["confidence"].lower()} sm">{r["confidence"]}</span>' if r["confidence"] else ""
        rows += (f'<tr class="k-{r["kind"]}" data-format="{e(r["format"])}"><td class="num">{d.strftime("%d %b")}<small>{r["day"]}</small></td>'
                 f'<td>{e(r["type"])}{badge}</td><td>{e(r["hook"])}</td><td><span class="fmt">{e(r["format"])}</span></td>'
                 f'<td>{e(r["time"]) or "–"}</td><td>{e(r["group"])}</td></tr>')
    groups = "".join(f'<li><b>{g}</b><span>{e(v)}</span></li>' for g, v in cal["groups"].items())
    filt = "".join(f'<button type="button" data-f="{f}" class="{"on" if f == "All" else ""}">{f}</button>' for f in ["All", "Reel", "Carousel", "Static", "Story"])
    return (f'<div class="filters" role="group" aria-label="Filter by format">{filt}</div>'
            f'<div class="tbl-wrap"><table class="tbl cal"><thead><tr><th>Date</th><th>Content type</th><th>Hook</th><th>Format</th><th>Time (IST)</th><th>Hashtag group</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div><ul class="groups">{groups}</ul>')


def all_posts(a):
    rows = "".join(f'<tr><td class="num" data-v="{p["ts"].timestamp():.0f}">{p["ts"].strftime("%d %b %y")}</td><td>{e(p["type"])}</td><td>{e(p["cluster"])}</td><td>{e(p["hook"])}</td>'
                   f'<td class="num" data-v="{p["likes"] or 0}">{p["likes"] or 0:,}</td><td class="num" data-v="{p["comments"]}">{p["comments"]:,}</td>'
                   f'<td class="num" data-v="{p["eng"]}"><b>{p["eng"]:,}</b></td><td><a href="{e(p["url"])}" target="_blank" rel="noopener">{e(snip(p["caption"], 50))}</a></td></tr>'
                   for p in a["posts"])
    return (f'<details class="all"><summary>All {len(a["posts"])} posts as a table</summary><div class="tbl-wrap"><table class="tbl sortable"><thead><tr>'
            '<th>Date</th><th>Format</th><th>Topic</th><th>Hook</th><th class="num">Likes</th><th class="num">Comments</th><th class="num">Engagement</th><th>Caption</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div></details>')


def csv_data(a):
    rows = [dict(date=p["ts"].isoformat(), type=p["type"], topic=p["cluster"], hook=p["hook"], likes=p["likes"] or 0, comments=p["comments"],
                 engagement=p["eng"], cta=p["cta"], hashtags=" ".join("#" + t for t in p["tags"]), url=p["url"], caption=p["caption"][:300]) for p in a["posts"]]
    return json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")


# ---------------------------------------------------------------- page
def section(n, title, sub, body, sid, crumb=None):
    return (f'<section id="{sid}" class="band"><div class="wrap"><p class="crumbs">Audit / <b>{n} {e(crumb or title)}</b></p>'
            f'<div class="sec-head"><h2>{e(title)}</h2><p>{e(sub)}</p></div>{body}</div></section>')


def ticker(a):
    s, w, ps, se = a["snapshot"], a["working"], a["posting"], a["sentiment"]
    items = [f'{s["n"]} posts analysed', f'{s["best_type"]["name"]}s {sign(s["best_type"]["lift"])} vs average',
             f'Top topic: {w["all_clusters"][0]["name"]}', f'Engagement trend: {s["trend"]["direction"]} {sign(s["trend"]["fit_change"])}']
    if ps["best_days"]:
        items.append(f'Best day: {ps["best_days"][0]["name"]}')
    if se["asks"]:
        items.append(f'Most asked: {se["asks"][0][0].lower()}')
    items.append("10 ideas ready")
    run = "".join(f"<span>{e(x)}</span>" for x in items)
    return f'<div class="announce" aria-label="Key numbers"><div class="mq"><div class="mq-run">{run}</div><div class="mq-run" aria-hidden="true">{run}</div></div></div>'


def render(a):
    s, w = a["snapshot"], a["working"]
    handle = a["handle"]
    audit = dt.date.fromisoformat(a["audit_date"]).strftime("%d %b %Y")
    period = f'{dt.date.fromisoformat(s["first"]).strftime("%d %b %Y")} to {dt.date.fromisoformat(s["last"]).strftime("%d %b %Y")}'
    demo = ('<div class="demo" role="note"><span>Demo data</span>These numbers are generated to test the dashboard. They are not BLUORNG\'s real results. '
            'Run the Apify step to replace them with the real scrape.</div>') if a["demo"] else ""
    nav = [("overview", "Overview"), ("working", "What's working"), ("avoid", "Avoid"), ("hashtags", "Hashtags"), ("posting", "Posting"),
           ("audience", "Audience"), ("ideas", "Ideas"), ("calendar", "Calendar")]
    cats = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in nav)
    tr = s["trend"]
    body = [
        section("01", "Performance", f'{s["n"]} posts from {period}. Engagement = likes + comments.',
                kpis(a) + f'<div class="grid g2w"><div class="panel"><h3>Top 10 posts by engagement</h3>{top10(a)}<p class="note">{ico("external")} Select a bar to open the post on Instagram.</p></div>'
                f'<div class="panel"><h3>Format performance</h3>{lift_bars(s["types"], "minmax(130px,1fr)")}<p class="note">Average engagement per post; % vs the account average of {k(s["avg_eng"])}.</p></div></div>'
                f'<div class="panel"><h3>Engagement over time <span class="pill {tone(tr["fit_change"], 10)}">{tr["direction"]} {sign(tr["fit_change"])}</span></h3>{timeline(a)}'
                f'<p class="note">Trend line change {sign(tr["fit_change"])}; second half vs first half {sign(tr["halves_change"])}. Up or down means more than 10% either way.</p></div>',
                "overview", "Performance snapshot"),
        section("02", "What's working", f'What the top {w["top_k"]} posts (top 10%) have in common, compared with the whole account.',
                formulas(a) + f'<div class="grid g2"><div class="panel"><h3>Content clusters</h3>{lift_bars(w["clusters"])}<p class="note">Topics found from captions and hashtags. Black = above account average, red = below.</p></div>'
                f'<div class="panel"><h3>Hook styles</h3>{hooks(a)}</div></div>'
                f'<div class="grid g2"><div class="panel"><h3>Caption length</h3>{lift_bars(w["lengths"])}<p class="note">Characters in the caption, hashtags included.</p></div>'
                f'<div class="panel"><h3>Call to action vs none</h3>{cta_block(a)}</div></div>', "working"),
        section("03", "What to avoid", f'Patterns that show up more often in the bottom {w["top_k"]} posts.',
                avoid(a) + f'<div class="panel"><h3>Bottom {w["top_k"]} posts</h3>{bottom_list(a)}</div>', "avoid"),
        section("04", "Hashtags", f'{len(a["hashtags"]["all"])} unique hashtags across {s["n"]} posts, ranked by how the posts using them perform.',
                f'<div class="panel"><h3>Hashtag cloud</h3>{cloud(a)}</div>' + tag_lists(a), "hashtags", "Hashtag intelligence"),
        section("05", "Posting pattern", "When the account posts, when it performs, and how often it should post.",
                f'<div class="panel"><h3>Day × time heatmap</h3>{heatmap(a)}</div><div class="grid g2"><div class="panel"><h3>Best days</h3>{lift_bars(a["posting"]["by_day"], "minmax(90px,.6fr)")}</div>'
                f'<div class="panel"><h3>Recommended schedule</h3>{schedule(a)}</div></div>{frequency(a)}', "posting"),
        section("06", "Audience", "Reactions in the comments, and what people keep asking for.", sentiment(a), "audience", "Audience sentiment"),
        section("07", "10 content ideas", "Each idea cites the data behind it. Confidence reflects how big the effect is and how many posts support it.", idea_cards(a), "ideas", "Content ideas"),
        section("08", "30-day calendar", "Ideas placed on the recommended posting days, with lighter formats in between. Starts the day after the audit.",
                calendar(a) + all_posts(a), "calendar", "Content calendar"),
    ]
    src = e(a["source"] or "apify/instagram-scraper")
    hero = (f'<section class="hero inv" id="top"><div class="hero-word">{logo("wordmark", "logo")}</div>'
            f'<img class="hero-mark" src="data:image/webp;base64,{b64(ROOT / "tools/book/renders/cover.webp")}" alt="">'
            f'<div class="wrap hero-copy"><div><span class="lbl">Instagram content audit</span><h1>@{e(handle)}</h1>'
            f'<p class="lede">{s["n"]} posts, {period}. What works, what to drop, and what to make next for the feed and for Meta ads.</p>'
            f'<div class="ctas"><a class="btn btn-solid" href="#ideas">See 10 ideas {ico("arrow")}</a><a class="btn btn-line" href="#calendar">30-day calendar</a></div></div>'
            f'<dl class="hero-side"><dt>Audit date</dt><dd>{audit}</dd><dt>Data</dt><dd>{src}</dd><dt>Posts</dt><dd>{s["n"]}</dd></dl></div></section>')
    foot_links = "".join(f'<li><a href="#{i}">{e(t)}</a></li>' for i, t in nav)
    footer = (f'<footer class="foot"><div class="wrap foot-top"><div><a class="lockup" href="#top">{logo()}<span class="x">×</span><span class="bp">BLUPRINT</span></a>'
              f'<p>Engagement = likes + comments, the two counts a public scrape returns. Saves, shares and reach need the account\'s own Insights. '
              f'Topics, hooks, CTAs and comment reactions are found with keyword rules on captions and comments. Times are IST.</p></div>'
              f'<div><h4>Sections</h4><ul>{foot_links}</ul></div>'
              f'<div><h4>Data</h4><ul><li>{src}</li><li>{s["n"]} posts</li><li>{period}</li><li>Audit {audit}</li></ul></div>'
              f'<div><h4>Project</h4><ul><li>BLUPRINT, a UI/UX graduation project with BLUORNG</li><li>Not an official BLUORNG publication</li></ul></div></div>'
              f'<div class="wrap foot-word">{logo("wordmark", "logo")}</div></footer>')
    page = TEMPLATE.replace("{{CSS}}", font_faces() + CSS).replace("{{JS}}", JS)
    page = page.replace("{{TITLE}}", f"@{e(handle)} content audit · BLUPRINT").replace("{{LOGO}}", logo()).replace("{{TICKER}}", ticker(a))
    page = page.replace("{{AUDIT}}", audit).replace("{{DEMO}}", demo).replace("{{CATS}}", cats).replace("{{IC_DL}}", ico("download")).replace("{{IC_PR}}", ico("print")).replace("{{HERO}}", hero)
    page = page.replace("{{BODY}}", "\n".join(body)).replace("{{FOOT}}", footer).replace("{{DATA}}", csv_data(a))
    return page


TEMPLATE = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title><style>{{CSS}}</style></head>
<body>
{{TICKER}}
{{DEMO}}
<header class="store"><div class="wrap store-top">
<nav class="l" aria-label="Quick links"><a href="#ideas">Ideas</a><a href="#calendar">Calendar</a><a href="#hashtags">Hashtags</a></nav>
<a class="lockup" href="#top" aria-label="BLUPRINT, back to top">{{LOGO}}<span class="x">×</span><span class="bp">BLUPRINT</span></a>
<div class="r"><span class="lbl">Audit {{AUDIT}}</span><button type="button" class="btn-s solid" id="csv" aria-label="Export CSV">{{IC_DL}}Export CSV</button><button type="button" class="btn-s" onclick="print()">{{IC_PR}}Print</button></div>
</div><nav class="cats" aria-label="Sections">{{CATS}}</nav><div class="progress"></div></header>
<main>
{{HERO}}
{{BODY}}
</main>
{{FOOT}}
<div id="tip" role="tooltip" hidden></div>
<script type="application/json" id="data">{{DATA}}</script>
<script>{{JS}}</script>
</body></html>
'''

CSS = r'''
:root { --bg:#ffffff; --bg-2:#f4f4f4; --bg-3:#ebebeb; --line:#dcdcdc; --line-soft:#e9e9e9; --ink:#0b0b0b; --ink-2:#3b3b3b; --muted:#6b6b6b;
  --heat:#c3141b; --mid:#8a8a8a; --one:#cfcfcf;
  --display:"Archivo", "Helvetica Neue", Arial, sans-serif; --body:"Geist", "Helvetica Neue", Arial, sans-serif; --mono:"Geist Mono", ui-monospace, Menlo, monospace;
  --ease:cubic-bezier(0.23, 1, 0.32, 1); color-scheme: light; }
.inv { --bg:#0a0a0a; --bg-2:#141414; --ink:#f4f4f4; --ink-2:#c8c8c8; --muted:#8c8c8c; --line:#2d2d2d; background: var(--bg); color: var(--ink); }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } *, *::before, *::after { animation: none !important; transition: none !important; } }
body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.6 var(--body); -webkit-font-smoothing: antialiased; }
a { color: inherit; text-decoration: none; } button { font: inherit; cursor: pointer; }
:focus-visible { outline: 2px solid var(--ink); outline-offset: 3px; }
.wrap { max-width: 1320px; margin: 0 auto; padding-inline: clamp(16px, 3.5vw, 40px); }
.lbl { font: 500 11px/1.3 var(--display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.logo { display: block; width: 100%; height: auto; } .logo path { fill: currentColor; }
/* store chrome */
.announce { background: #0b0b0b; color: #f4f4f4; overflow: hidden; font: 500 11px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; }
.mq { display: flex; width: max-content; animation: mq 38s linear infinite; }
.mq-run { display: flex; } .mq-run span { padding: 11px 28px; white-space: nowrap; } .mq-run span::after { content: "✦"; margin-left: 56px; font-size: 8px; vertical-align: 2px; color: #8c8c8c; }
@keyframes mq { to { transform: translateX(-50%); } }
.announce:hover .mq { animation-play-state: paused; }
.demo { background: var(--heat); color: #fff; text-align: center; padding: 10px 16px; font-size: 13px; }
.demo span { font: 700 10.5px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; border: 1px solid #fff; padding: 4px 7px; margin-right: 10px; }
.store { position: sticky; top: 0; z-index: 30; background: color-mix(in srgb, #fff 92%, transparent); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border-bottom: 1px solid var(--line-soft); }
.store-top { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; height: 64px; gap: 16px; }
.store-top nav.l { display: flex; gap: 22px; }
.store-top nav a, .cats a { font: 600 11.5px/1 var(--display); letter-spacing: .12em; text-transform: uppercase; white-space: nowrap; transition: opacity .2s; }
.store-top .r { display: flex; gap: 8px; justify-content: flex-end; align-items: center; } .store-top .r .lbl { margin-right: 8px; }
.lockup { display: flex; align-items: center; gap: 14px; color: var(--ink); }
.lockup .logo { height: 22px; width: auto; } .lockup .x { font: 400 13px/1 var(--display); color: var(--muted); }
.lockup .bp { font: 900 19px/1 var(--display); font-stretch: 112%; letter-spacing: .02em; }
.btn-s { min-height: 44px; border: 1px solid var(--ink); background: transparent; color: var(--ink); padding: 10px 16px; font: 700 10.5px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; transition: background-color .2s, color .2s, transform .16s var(--ease); }
.btn-s.solid { background: var(--ink); color: #fff; } .btn-s:active, .btn:active { transform: scale(.97); }
.cats { display: flex; justify-content: center; gap: 28px; height: 44px; align-items: center; border-top: 1px solid var(--line-soft); overflow-x: auto; scrollbar-width: none; padding-inline: 16px; }
.cats::-webkit-scrollbar { display: none; }
.cats a { color: var(--muted); font-weight: 500; padding-block: 16px; }
.cats a.on { color: var(--ink); box-shadow: inset 0 -2px 0 var(--ink); }
@media (hover: hover) and (pointer: fine) { .cats a:hover, .store-top nav a:hover { opacity: .55; } .btn-s:hover { background: var(--ink); color: #fff; } .btn-s.solid:hover { background: #fff; color: var(--ink); } }
.progress { position: absolute; left: 0; bottom: -1px; height: 2px; width: 100%; background: var(--ink); transform-origin: 0 50%; transform: scaleX(0); }
@supports (animation-timeline: scroll()) { .progress { animation: grow linear both; animation-timeline: scroll(root); } @keyframes grow { to { transform: scaleX(1); } } }
.ic { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 1.75; stroke-linecap: square; stroke-linejoin: miter; flex: none; vertical-align: -3px; }
.btn-s { display: inline-flex; align-items: center; gap: 8px; } .btn .ic { margin-left: 10px; transition: transform .2s var(--ease); } .note .ic { width: 14px; height: 14px; margin-right: 4px; }
@media (hover: hover) and (pointer: fine) { .btn:hover .ic { transform: translateX(3px); } }
/* campaign hero */
.hero { position: relative; overflow: hidden; min-height: clamp(520px, 78vh, 760px); display: flex; align-items: flex-end; background: radial-gradient(ellipse 55% 60% at 68% 42%, #222 0%, #0a0a0a 70%); }
.hero-word { position: absolute; left: 50%; top: 42%; transform: translate(-50%, -50%); width: 116%; color: #fff; opacity: .045; pointer-events: none; }
.hero-mark { position: absolute; right: max(3vw, calc(50% - 620px)); top: 44%; transform: translateY(-60%); width: min(34vw, 440px); height: auto; filter: drop-shadow(0 40px 50px rgba(0,0,0,.5)); }
.hero-copy { position: relative; z-index: 2; width: 100%; padding-block: 64px clamp(40px, 6vw, 72px); display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 32px; align-items: end; }
.hero h1 { margin: 14px 0 0; font: 800 clamp(52px, 9vw, 136px)/.88 var(--display); text-transform: uppercase; letter-spacing: -.035em; font-stretch: 105%; }
.lede { margin: 22px 0 30px; max-width: 46ch; color: var(--ink-2); font-size: 16px; }
.ctas { display: flex; flex-wrap: wrap; gap: 10px; }
.btn { display: inline-flex; align-items: center; justify-content: center; min-width: 200px; padding: 16px 22px; font: 700 12px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; border: 1px solid var(--ink); transition: background-color .2s, color .2s, transform .16s var(--ease); }
.btn-solid { background: var(--ink); color: var(--bg); } .btn-line { color: var(--ink); }
@media (hover: hover) and (pointer: fine) { .btn-solid:hover { background: transparent; color: var(--ink); } .btn-line:hover { background: var(--ink); color: var(--bg); } }
.hero-side { position: relative; z-index: 2; margin: 0; text-align: right; display: grid; gap: 4px; justify-items: end; }
.hero-side dt { font: 500 10.5px/1.3 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-top: 10px; }
.hero-side dd { margin: 0; font: 600 13px/1.3 var(--display); letter-spacing: .1em; text-transform: uppercase; }
/* sections */
.band { padding-block: clamp(56px, 7vw, 96px) 24px; border-bottom: 1px solid var(--line-soft); scroll-margin-top: 104px; }
.crumbs { margin: 0 0 20px; font: 500 11px/1 var(--display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); } .crumbs b { color: var(--ink); font-weight: 600; }
.sec-head { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, .75fr); gap: 16px 64px; align-items: end; margin-bottom: clamp(28px, 4vw, 44px); }
.sec-head h2 { margin: 0; font: 800 clamp(36px, 5.4vw, 76px)/.9 var(--display); text-transform: uppercase; letter-spacing: -.03em; text-wrap: balance; }
.sec-head p { margin: 0; color: var(--ink-2); max-width: 46ch; }
.grid { display: grid; gap: 14px; margin-bottom: 14px; } .g2 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .g2w { grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); }
.panel { background: var(--bg-2); padding: clamp(18px, 2vw, 26px); min-width: 0; margin-bottom: 14px; } .grid > .panel { margin-bottom: 0; }
.panel h3 { margin: 0 0 18px; font: 700 12px/1.3 var(--display); letter-spacing: .12em; text-transform: uppercase; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.note { margin: 16px 0 0; font-size: 12.5px; color: var(--muted); } .note b { color: var(--ink); }
.pill { font: 700 10px/1 var(--display); letter-spacing: .12em; padding: 5px 8px; border: 1px solid currentColor; }
.pill.up, .pill.flat { color: var(--ink); } .pill.down { color: var(--heat); }
/* KPI product tiles */
.kpis { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 28px 14px; margin-bottom: 36px; }
.kp { display: flex; flex-direction: column; min-width: 0; }
.kp-shot { background: var(--bg-2); aspect-ratio: 4 / 5; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 10px; padding: 16px; position: relative; text-align: center; transition: background-color .3s var(--ease); }
.kp-shot b { font: 800 clamp(30px, 3.2vw, 46px)/1 var(--display); letter-spacing: -.03em; text-transform: uppercase; }
.kp.down .kp-shot b { color: var(--heat); }
.kp-meta { padding-top: 12px; display: grid; gap: 3px; }
.kp-meta h3 { margin: 0; font: 700 12px/1.3 var(--display); letter-spacing: .1em; text-transform: uppercase; }
.kp-meta span { font: 500 11.5px/1.3 var(--display); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.kp.best .kp-shot { background: #0b0b0b; color: #f4f4f4; } .kp.best q { font-size: 12px; color: #c8c8c8; line-height: 1.4; quotes: "“" "”"; }
@media (hover: hover) and (pointer: fine) { .kp:hover .kp-shot { background: var(--bg-3); } .kp.best:hover .kp-shot { background: #222; } }
.stag { position: absolute; left: 12px; top: 12px; font: 700 9.5px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; padding: 6px 8px; background: #0b0b0b; color: #fff; }
.kp.best .stag { background: #fff; color: #0b0b0b; }
/* bars */
.hbs { display: grid; gap: 4px; }
.hb { display: grid; gap: 14px; align-items: center; padding: 6px 8px; margin: 0 -8px; transition: background-color .15s; }
.hb:hover, .hb:focus-visible { background: #fff; }
.hb-l { display: flex; gap: 8px; align-items: baseline; min-width: 0; font-size: 13.5px; }
.hb-l em { font: 500 11px/1 var(--mono); font-style: normal; color: var(--muted); } .hb-l span { white-space: nowrap; }
.hb-l small { color: var(--muted); font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hb-t { height: 12px; position: relative; background: #fff; }
.hb-t i { position: absolute; inset: 0 auto 0 0; background: var(--mid); border-radius: 0 4px 4px 0; }
.hb.up .hb-t i, .hb-t.up i { background: var(--ink); } .hb.down .hb-t i { background: var(--heat); } .hb-t.flat i { background: var(--mid); }
.hb > b { font: 500 12.5px/1 var(--mono); text-align: right; white-space: nowrap; } .hb > b small { color: var(--muted); font-size: 11px; }
.hb.down > b small { color: var(--heat); }
/* timeline */
.chart { width: 100%; height: auto; display: block; }
.chart .gl { stroke: var(--line); stroke-width: 1; } .chart .ax { fill: var(--muted); font: 10.5px var(--mono); }
.chart .avg { stroke: var(--muted); stroke-dasharray: 3 5; }
.chart .halo { paint-order: stroke; stroke: var(--bg-2); stroke-width: 5px; stroke-linejoin: round; font-weight: 500; fill: var(--ink-2); }
.chart .roll { fill: none; stroke: var(--ink); stroke-width: 2.5; pointer-events: none; paint-order: stroke; }
.dot circle:not(.hit) { fill: var(--mid); stroke: var(--bg-2); stroke-width: 2; transition: r .12s; }
.dot.up circle:not(.hit) { fill: var(--ink); } .dot.down circle:not(.hit) { fill: var(--heat); }
.dot .hit { fill: transparent; } .dot { outline: none; cursor: pointer; } .dot:hover circle:not(.hit), .dot:focus circle:not(.hit) { r: 6; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 14px; font-size: 12px; color: var(--muted); align-items: center; }
.legend span { display: inline-flex; gap: 7px; align-items: center; }
.lk { display: inline-block; flex: none; } .lk.line { width: 18px; height: 2.5px; background: var(--ink); }
.lk.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--mid); } .lk.sq { width: 11px; height: 11px; background: var(--mid); }
.lk.up { background: var(--ink); } .lk.down { background: var(--heat); } .lk.one { background: transparent; border: 1px solid var(--muted); }
/* tables */
.tbl-wrap { overflow-x: auto; }
.tbl { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.tbl th { text-align: left; font: 600 10.5px/1.3 var(--display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); padding: 0 12px 10px 0; border-bottom: 1px solid var(--ink); white-space: nowrap; }
.tbl.hooks th { white-space: normal; }
.tbl td { padding: 11px 12px 11px 0; border-bottom: 1px solid var(--line); vertical-align: top; color: var(--ink-2); }
.tbl td:first-child { color: var(--ink); font-weight: 500; }
.tbl .num { text-align: right; font-family: var(--mono); font-size: 12.5px; white-space: nowrap; }
.tbl td.up { color: var(--ink); font-weight: 600; } .tbl td.down { color: var(--heat); }
.tbl td small { display: block; color: var(--muted); font-size: 11px; font-weight: 400; }
/* cards */
.cards { display: grid; gap: 14px; margin-bottom: 14px; } .cards.c3 { grid-template-columns: repeat(3, minmax(0, 1fr)); } .cards.c2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.card { background: var(--bg-2); padding: 22px; min-width: 0; border-top: 2px solid transparent; }
.card .kk { font: 600 10.5px/1.2 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.card h4 { margin: 10px 0 8px; font: 800 20px/1.05 var(--display); text-transform: uppercase; letter-spacing: -.01em; }
.card p { margin: 0; color: var(--ink-2); font-size: 13.5px; }
.card.win { border-top-color: var(--ink); } .card.bad { border-top-color: var(--heat); } .card.bad h4 { color: var(--heat); }
.plist { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; }
.plist a { display: grid; gap: 3px; padding: 14px; background: #fff; border-left: 2px solid var(--heat); transition: background-color .15s; height: 100%; }
.plist a:hover { background: var(--bg-3); } .plist b { font: 800 20px/1.1 var(--display); } .plist span { font-size: 12px; color: var(--muted); } .plist small { font-size: 12.5px; color: var(--ink-2); }
/* hashtags */
.cloud { display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: baseline; line-height: 1.2; }
.tag { font-family: var(--display); font-weight: 800; letter-spacing: -.01em; text-transform: lowercase; outline: none; transition: opacity .15s; color: var(--mid); cursor: default; }
.tag.up { color: var(--ink); } .tag.down { color: var(--heat); } .tag.one { color: var(--muted); font-weight: 500; }
.cloud:hover .tag { opacity: .35; } .cloud .tag:hover, .tag:focus-visible { opacity: 1; }
.tl { list-style: none; margin: 14px 0 0; padding: 0; display: grid; }
.tl li { display: flex; justify-content: space-between; gap: 10px; font-size: 13.5px; padding: 9px 0; border-bottom: 1px solid var(--line); }
.tl li span { color: var(--muted); font-size: 12px; text-align: right; } .tl b { font-weight: 600; }
.tl.down b { color: var(--heat); }
/* heatmap */
.heat { display: grid; grid-template-columns: 52px repeat(7, minmax(0, 1fr)); gap: 3px; }
.heat .hh { font: 600 9.5px/1.2 var(--display); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); padding: 0 0 8px; text-align: center; }
.heat .hh small { display: block; font: 400 10px/1.3 var(--mono); letter-spacing: 0; }
.heat .hd { font: 700 11px/1 var(--display); letter-spacing: .12em; text-transform: uppercase; display: flex; align-items: center; }
.hc { min-height: 52px; background: color-mix(in srgb, #0b0b0b var(--p), #ffffff); color: var(--ink); display: flex; flex-direction: column; justify-content: center; align-items: center; outline: none; transition: box-shadow .12s; }
.hc.dk { color: #fff; } .hc b { font: 500 12px/1 var(--mono); } .hc small { font: 10px/1.2 var(--mono); opacity: .65; margin-top: 3px; }
.hc:hover, .hc:focus-visible { box-shadow: inset 0 0 0 2px var(--heat); }
.hc.empty { background: transparent; border: 1px dashed var(--line); color: var(--one); }
.ramp { display: inline-flex !important; gap: 2px !important; } .ramp i { width: 18px; height: 10px; display: block; background: color-mix(in srgb, #0b0b0b var(--p), #fff); }
.sched { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; }
.sched div { background: #fff; padding: 16px; border-top: 2px solid var(--ink); display: grid; gap: 4px; }
.sched b { font: 800 26px/1 var(--display); text-transform: uppercase; } .sched span { font-size: 13px; } .sched small { font: 11px var(--mono); color: var(--muted); }
/* sentiment */
.gbs { display: grid; gap: 12px; }
.gb { display: grid; grid-template-columns: minmax(110px, .8fr) minmax(0, 2fr) 64px; gap: 12px; align-items: center; }
.gb-l { font-size: 13.5px; } .gb-b { display: grid; gap: 3px; } .gb-b .hb-t { height: 9px; outline: none; }
.gb > b { font: 500 12.5px/1.2 var(--mono); text-align: right; } .gb > b small { display: block; color: var(--muted); font-size: 11px; }
.quotes { list-style: none; margin: 16px 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px; }
.quotes li { font-size: 12.5px; padding: 7px 11px; background: #fff; color: var(--ink-2); }
/* ideas as product cards */
.ideas { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 36px 14px; }
.idea { display: flex; flex-direction: column; min-width: 0; }
.idea-shot { position: relative; background: var(--bg-2); aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; padding: 48px 28px 28px; transition: background-color .3s var(--ease); }
.idea:nth-child(4n+1) .idea-shot { background: #0b0b0b; color: #f4f4f4; }
.idea-shot .hook { margin: 0; font: 800 clamp(22px, 2.2vw, 28px)/1.05 var(--display); text-transform: uppercase; letter-spacing: -.02em; text-align: center; text-wrap: balance; }
.idea-shot .no { position: absolute; right: 12px; top: 12px; font: 500 11px/1 var(--mono); color: var(--muted); }
.stag.high { background: #0b0b0b; color: #fff; } .stag.medium { background: #fff; color: #0b0b0b; border: 1px solid #0b0b0b; } .stag.low { background: transparent; color: var(--muted); border: 1px solid var(--line); }
.idea:nth-child(4n+1) .stag.high { background: #fff; color: #0b0b0b; } .idea:nth-child(4n+1) .stag.medium { background: transparent; color: #fff; border-color: #fff; }
.idea-meta { display: flex; justify-content: space-between; gap: 12px; padding-top: 14px; }
.idea-meta h3 { margin: 0; font: 700 13px/1.3 var(--display); letter-spacing: .1em; text-transform: uppercase; }
.idea-meta span { font: 500 12px/1.3 var(--display); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); white-space: nowrap; }
.idea dl { margin: 10px 0 0; } .idea dt { font: 600 10px/1.3 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-top: 10px; }
.idea dd { margin: 3px 0 0; font-size: 13.5px; color: var(--ink-2); }
@media (hover: hover) and (pointer: fine) { .idea:hover .idea-shot { background: var(--bg-3); } .idea:nth-child(4n+1):hover .idea-shot { background: #222; } }
/* calendar */
.filters { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.filters button { min-height: 44px; border: 1px solid var(--line); background: #fff; color: var(--ink); padding: 10px 16px; font: 600 10.5px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; transition: border-color .15s; }
.filters button:hover { border-color: var(--ink); } .filters button.on { background: var(--ink); color: #fff; border-color: var(--ink); }
.cal tr.k-idea td:first-child { box-shadow: inset 2px 0 0 var(--ink); padding-left: 10px; } .cal tr.k-filler td:first-child, .cal tr.k-rest td:first-child { padding-left: 10px; }
.cal tr.k-rest td { color: var(--muted); font-weight: 400; } .cal td:first-child { white-space: nowrap; }
.badge { font: 700 9px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; padding: 4px 6px; margin-left: 6px; vertical-align: 1px; border: 1px solid var(--ink); white-space: nowrap; }
.badge.high { background: var(--ink); color: #fff; } .badge.medium { color: var(--ink); } .badge.low { color: var(--muted); border-color: var(--line); }
.fmt { font: 600 10px/1 var(--display); letter-spacing: .12em; text-transform: uppercase; padding: 5px 7px; border: 1px solid var(--line); }
.groups { list-style: none; margin: 14px 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 22px; font-size: 12.5px; color: var(--muted); }
.groups b { color: var(--ink); margin-right: 6px; }
details.all { margin-top: 22px; border-top: 1px solid var(--line); }
details.all summary { cursor: pointer; font: 700 11px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; padding: 18px 0; }
.sortable th { cursor: pointer; } .sortable th:hover { color: var(--ink); } .sortable a { text-decoration: underline; text-decoration-color: var(--line); text-underline-offset: 3px; }
/* footer */
.foot { margin-top: 0; }
.foot-top { display: grid; grid-template-columns: minmax(0, 1.4fr) repeat(3, minmax(0, 1fr)); gap: 32px; padding-block: 64px 40px; border-bottom: 1px solid var(--line); }
.foot-top p { color: var(--muted); font-size: 13px; margin: 18px 0 0; max-width: 44ch; }
.foot-top h4 { margin: 0 0 14px; font: 700 11px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; }
.foot-top ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; } .foot-top li { color: var(--muted); font-size: 13px; }
.foot-top a:hover { color: var(--ink); }
.foot-word { padding-block: 28px 24px; color: var(--ink); }
/* tooltip */
#tip { position: fixed; z-index: 60; pointer-events: none; background: #0b0b0b; color: #f4f4f4; padding: 9px 11px; font-size: 12px; line-height: 1.45; max-width: 280px; }
#tip b { display: block; font: 600 14px/1.3 var(--body); }
@media (max-width: 1100px) { .kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); } .cards.c3 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .store-top nav.l { display: none; } .store-top { grid-template-columns: auto 1fr; } .store-top .lockup { order: -1; } }
@media (max-width: 760px) {
  .store-top { height: 56px; } .store-top .r .lbl { display: none; } .store-top .r .btn-s:not(.solid) { display: none; } .cats { justify-content: flex-start; gap: 22px; }
  .hero { min-height: 0; } .hero-mark { width: 52vw; top: 28px; right: 16px; transform: none; } .hero-copy { grid-template-columns: 1fr; padding-top: calc(52vw + 24px); } .hero-side { justify-items: start; text-align: left; }
  .sec-head, .g2, .g2w, .cards.c2, .cards.c3, .foot-top { grid-template-columns: 1fr; } .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hb { grid-template-columns: minmax(0, 1fr) 84px !important; } .hb .hb-t { grid-column: 1 / -1; grid-row: 2; }
  .heat { grid-template-columns: 34px repeat(7, minmax(0, 1fr)); gap: 2px; } .heat .hn { display: none; } .heat .hh small { font-size: 9px; } .hc { min-height: 44px; } .hc b { font-size: 9.5px; } .hc small { display: none; }
  .kp-shot { aspect-ratio: 4 / 3; } .kp.best .kp-shot { padding-top: 44px; aspect-ratio: auto; min-height: 100%; } .chart-wrap { overflow-x: auto; margin-inline: -8px; } .chart-wrap .chart { min-width: 620px; } .btn { min-width: 0; flex: 1; }
}
@media (max-width: 420px) {
  .store-top .r .btn-s.solid { font-size: 0; gap: 0; padding: 10px 13px; } .store-top .r .btn-s.solid .ic { width: 18px; height: 18px; }
  .lockup { gap: 10px; } .lockup .bp { font-size: 16px; } .hero h1 { font-size: clamp(34px, 12.5vw, 52px); }
  .hero-side dd { overflow-wrap: anywhere; } .tbl.hooks { font-size: 12.5px; }
}
@media print { .store, .announce, .filters, .ctas { display: none; } .band { break-inside: avoid-page; } }
'''

JS = r'''
(function () {
  var tipEl = document.getElementById('tip');
  function show(el, x, y) {
    var parts = (el.getAttribute('data-tip') || '').split(' | ');
    tipEl.textContent = '';
    var b = document.createElement('b'); b.textContent = parts[0]; tipEl.appendChild(b);
    for (var i = 1; i < parts.length; i++) { var s = document.createElement('div'); s.textContent = parts[i]; tipEl.appendChild(s); }
    tipEl.hidden = false;
    var r = tipEl.getBoundingClientRect();
    tipEl.style.left = Math.min(window.innerWidth - r.width - 8, x + 14) + 'px';
    tipEl.style.top = Math.max(8, y - r.height - 12) + 'px';
  }
  document.addEventListener('pointermove', function (ev) {
    var el = ev.target.closest && ev.target.closest('[data-tip]');
    if (el) show(el, ev.clientX, ev.clientY); else tipEl.hidden = true;
  });
  document.addEventListener('focusin', function (ev) {
    var el = ev.target.closest && ev.target.closest('[data-tip]');
    if (!el) { tipEl.hidden = true; return; }
    var r = el.getBoundingClientRect(); show(el, r.left + r.width / 2, r.top);
  });
  document.addEventListener('focusout', function () { tipEl.hidden = true; });
  // calendar filter
  document.querySelectorAll('.filters button').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.filters button').forEach(function (x) { x.classList.toggle('on', x === b); });
      var f = b.getAttribute('data-f');
      document.querySelectorAll('.cal tbody tr').forEach(function (tr) {
        tr.hidden = !(f === 'All' || tr.getAttribute('data-format') === f);
      });
    });
  });
  // sortable table
  document.querySelectorAll('.sortable th').forEach(function (th, i) {
    th.addEventListener('click', function () {
      var tb = th.closest('table').tBodies[0], rows = [].slice.call(tb.rows), dir = th.dataset.dir === 'desc' ? 1 : -1;
      th.dataset.dir = dir === 1 ? 'asc' : 'desc';
      rows.sort(function (a, b) {
        var x = a.cells[i], y = b.cells[i];
        var vx = x.dataset.v !== undefined ? +x.dataset.v : x.textContent, vy = y.dataset.v !== undefined ? +y.dataset.v : y.textContent;
        return (vx > vy ? 1 : vx < vy ? -1 : 0) * dir;
      });
      rows.forEach(function (r) { tb.appendChild(r); });
    });
  });
  // section highlight
  var links = [].slice.call(document.querySelectorAll('.cats a'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) links.forEach(function (l) { var on = l.getAttribute('href') === '#' + en.target.id; l.classList.toggle('on', on); if (on && l.scrollIntoView && innerWidth < 760) l.parentNode.scrollLeft = l.offsetLeft - 16; }); });
    }, { rootMargin: '-30% 0px -60% 0px' });
    document.querySelectorAll('.band').forEach(function (s) { io.observe(s); });
  }
  // CSV export
  document.getElementById('csv').addEventListener('click', function () {
    var rows = JSON.parse(document.getElementById('data').textContent);
    var cols = Object.keys(rows[0] || {});
    var esc = function (v) { v = String(v == null ? '' : v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    var csv = [cols.join(',')].concat(rows.map(function (r) { return cols.map(function (c) { return esc(r[c]); }).join(','); })).join('\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'instagram-audit-posts.csv'; a.click();
  });
})();
'''


def report_md(a):
    s, w, h, ps, se = a["snapshot"], a["working"], a["hashtags"], a["posting"], a["sentiment"]
    likes_txt = "hidden" if s["likes_hidden"] else f"{s['avg_likes']:,.0f}"
    L = [f"# @{a['handle']} Instagram audit, {a['audit_date']}", ""]
    if a["demo"]:
        L += ["> **Demo data.** Generated to test the pipeline, not BLUORNG's real numbers.", ""]
    L += [f"Source: {a['source']}. Posts analysed: {s['n']} ({s['first']} to {s['last']}). Engagement = likes + comments.", "",
          "## Step 3: Performance snapshot", f"- Average likes: {likes_txt}",
          f"- Average comments: {s['avg_comments']:,.0f}", f"- Trend: {s['trend']['direction']} ({s['trend']['fit_change']:+.0f}% trend line, {s['trend']['halves_change']:+.0f}% second half vs first)",
          f"- Best format: {s['best_type']['name']} ({s['best_type']['lift']:+.0f}% vs average)", "", "Top 5 posts:"]
    L += [f"{i}. {p['eng']:,} — {p['type']}, {date(p)} — {snip(p['caption'], 80)} ({p['url']})" for i, p in enumerate(s["top5"], 1)]
    L += ["", "| Format | Posts | Avg engagement | vs average |", "|---|---|---|---|"] + [f"| {t['name']} | {t['n']} | {t['avg']:,.0f} | {t['lift']:+.0f}% |" for t in s["types"]]
    L += ["", "## Step 4: What's working", "", "| Hook style | Posts | Share of top 10% | vs average |", "|---|---|---|---|"]
    L += [f"| {x['name']} | {x['n']} | {x['share_top']:.0f}% | {x['lift']:+.0f}% |" for x in w["hooks"]]
    L += ["", "| Topic cluster | Posts | Avg engagement | vs average |", "|---|---|---|---|"] + [f"| {c['name']} | {c['n']} | {c['avg']:,.0f} | {c['lift']:+.0f}% |" for c in w["all_clusters"]]
    L += ["", f"Best caption length: {w['best_length']['name']} ({w['best_length']['lift']:+.0f}%).",
          f"CTA: {w['cta']['yes_n']} posts average {w['cta']['yes_avg']:,.0f}; {w['cta']['no_n']} without average {w['cta']['no_avg']:,.0f} ({w['cta']['lift']:+.0f}%).", "", "Bottom 10% patterns:"]
    L += [f"- {x['feature']}: {x['value']} is {x['bottom_share']:.0f}% of the bottom posts vs {x['all_share']:.0f}% overall" for x in w["avoid"]] or ["- No strong pattern."]
    L += ["", "## Step 5: Hashtags", "", "| Hashtag | Posts | vs average |", "|---|---|---|"] + [f"| #{t['tag']} | {t['n']} | {(t['index'] - 1) * 100:+.0f}% |" for t in h["all"]]
    L += ["", "Keep using: " + ", ".join("#" + t["tag"] for t in h["keep"]), "", "Stop using: " + ", ".join("#" + t["tag"] for t in h["stop"]),
          "", "Try these: " + ", ".join(f"#{t['tag']} ({t['theme']})" for t in h["try_"])]
    L += ["", "## Step 6: Posting pattern", "Best days: " + ", ".join(f"{d['name']} ({d['lift']:+.0f}%)" for d in ps["best_days"]),
          "Best times: " + ", ".join(f"{d['name']} ({d['lift']:+.0f}%)" for d in ps["best_slots"]),
          f"Posts per week: {ps['per_week']:.1f}; weekly frequency vs engagement r = {ps['weekly_r']:+.2f}.",
          "Recommended schedule: " + ", ".join(f"{x['day']} {x['hours']} IST" for x in ps["schedule"])]
    L += ["", "## Step 7: Audience sentiment", f"{se['n_comments']} comments read.", "Top 10% posts: " + ", ".join(f"{k_} {v:.0f}%" for k_, v in se["top"].items()),
          "Asks: " + ", ".join(f"{n} ({c})" for n, c in se["asks"])]
    L += ["", "## Step 8: 10 content ideas"]
    for i, x in enumerate(a["ideas"], 1):
        L += [f"{i}. **{x['title']}** ({x['confidence']}) — Hook: “{x['hook']}” — {x['format']} — {x['formula']}", f"   Why: {x['why']}", f"   Caption opener: {x['opener']}"]
    L += ["", "## Step 9: 30-day calendar", "", "| Date | Content type | Hook | Format | Hashtag group |", "|---|---|---|---|---|"]
    L += [f"| {r['date']} {r['day']} | {r['type']} | {r['hook']} | {r['format']} | {r['group']} |" for r in a["calendar"]["rows"]]
    L += ["", "Hashtag groups: " + "; ".join(f"{g} = {v}" for g, v in a["calendar"]["groups"].items()), ""]
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--handle", default="bluorng")
    ap.add_argument("--limit", type=int, default=150)
    ap.add_argument("--out", default=str(ROOT / "docs/bluprint/bluorng-dashboard.html"))
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--source", default="Apify · apify/instagram-scraper")
    o = ap.parse_args()
    items = A.load(o.data)
    a = A.analyse(items, o.handle, o.limit, source=o.source + (" (demo data)" if o.demo else ""), demo=o.demo,
                  audit_date=dt.date.fromisoformat(o.date) if o.date else None)
    print(f"posts in file {len(items)}, analysed {a['snapshot']['n']} (limit {o.limit})")
    out = pathlib.Path(o.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(a))
    out.with_suffix(".md").write_text(report_md(a))
    print("wrote", out, "and", out.with_suffix(".md"))
