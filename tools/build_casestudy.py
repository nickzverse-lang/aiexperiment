"""Build the BLUORNG UX case study as A4 landscape pages (Project proposal to Storyboarding).

Every page keeps its content inside the content box of the college grid:
A4 landscape, left margin 33.867 mm (binding side), top, right and bottom margins 23.989 mm.

Run:  python3 tools/build_casestudy.py                        -> docs/bluorng-casestudy.html (fonts from Google Fonts)
      python3 tools/build_casestudy.py --local DEPS OUT.html  -> offline copy for PDF export:
      node tools/make_pdf.js <url> docs/bluorng-casestudy.pdf 297mm 210mm
"""
import base64
import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "cs"), str(HERE)]
import build_book as bb  # noqa: E402
from pages import chips, pages  # noqa: E402

BOOK = bb.BOOK
OUT = bb.ROOT / "docs" / "bluorng-casestudy.html"
e = html.escape
PROJECT_TITLE = "Designing a Platform to Help Streetwear Brands Like BLUORNG Decide What Content to Create for Instagram and Meta Ads"


def img(name):
    return "data:image/webp;base64," + base64.b64encode((BOOK / "renders" / name).read_bytes()).decode()


# ---------------------------------------------------------------- storyboards
SK = {
    "desk": '<rect x="30" y="20" width="110" height="72" class="sk-l"/><path d="M20 102h130" class="sk-l"/><rect x="44" y="34" width="50" height="4" class="sk-g"/><rect x="44" y="44" width="70" height="4" class="sk-g"/><rect x="148" y="52" width="30" height="54" rx="5" class="sk-f"/><text x="163" y="84" text-anchor="middle" font-size="9" font-weight="800" fill="#fff">14d</text><text x="86" y="78" text-anchor="middle" font-size="22" font-weight="800" class="sv-heat">?</text>',
    "dash": '<rect x="18" y="12" width="164" height="104" class="sk-l"/><rect x="18" y="12" width="26" height="104" class="sk-g2"/><rect x="54" y="22" width="60" height="6" class="sk-f"/>'
            '<g><rect x="54" y="40" width="110" height="9" class="sk-f"/><rect x="54" y="55" width="78" height="9" class="sk-g"/><rect x="54" y="70" width="56" height="9" class="sk-g"/><rect x="54" y="85" width="30" height="9" class="sk-g"/></g>'
            '<text x="160" y="48" text-anchor="end" font-size="8" font-weight="800" fill="#fff">TRY-ON</text><text x="54" y="108" font-size="8" font-weight="700" class="sv-ink">COST PER SALE BY AD TYPE</text>',
    "ideas": '<rect x="18" y="12" width="164" height="104" class="sk-l"/><g><rect x="28" y="22" width="68" height="40" class="sk-g2"/><rect x="104" y="22" width="68" height="40" class="sk-g2"/><rect x="28" y="68" width="68" height="40" class="sk-g2"/><rect x="104" y="68" width="68" height="40" class="sk-f"/></g>'
             '<g class="sk-f"><rect x="34" y="28" width="34" height="5"/><rect x="110" y="28" width="34" height="5"/><rect x="34" y="74" width="34" height="5"/></g><rect x="110" y="74" width="34" height="5" fill="#fff"/>'
             '<g class="sk-g"><rect x="34" y="38" width="54" height="3"/><rect x="110" y="38" width="54" height="3"/><rect x="34" y="84" width="54" height="3"/></g>'
             '<text x="138" y="100" text-anchor="middle" font-size="7.5" font-weight="800" fill="#fff">AD LIBRARY</text><text x="62" y="56" text-anchor="middle" font-size="8" font-weight="800" class="sv-ink">ANGLE 1</text>',
    "plan": '<rect x="54" y="10" width="92" height="110" class="sk-l"/><rect x="64" y="18" width="50" height="6" class="sk-f"/>'
            + "".join(f'<rect x="64" y="{32 + i * 16}" width="9" height="9" class="{"sk-f" if i < 3 else "sk-l"}" style="stroke-width:1.5"/><rect x="78" y="{34 + i * 16}" width="{48 - (i % 2) * 12}" height="5" class="sk-g"/><text x="138" y="{40 + i * 16}" text-anchor="end" font-size="7" font-weight="700" class="sv-ink">{r}</text>' for i, r in enumerate(["9:16", "4:5", "1:1", "9:16", "4:5"])),
    "set": '<rect x="20" y="44" width="80" height="54" rx="6" class="sk-f"/><circle cx="60" cy="71" r="16" fill="#fff"/><circle cx="60" cy="71" r="9" class="sk-f"/><rect x="40" y="34" width="22" height="12" class="sk-f"/>'
           '<rect x="128" y="16" width="50" height="100" rx="8" class="sk-l"/><rect x="136" y="34" width="8" height="8" class="sk-f"/><rect x="148" y="36" width="22" height="4" class="sk-g"/><rect x="136" y="52" width="8" height="8" class="sk-f"/><rect x="148" y="54" width="22" height="4" class="sk-g"/><rect x="136" y="70" width="8" height="8" class="sk-l" style="stroke-width:1.5"/><rect x="148" y="72" width="22" height="4" class="sk-g"/>',
    "many": "".join(f'<{"circle" if (i * 7) % 3 == 0 else "rect"} {f"cx={41 + (i % 4) * 39} cy={29 + (i // 4) * 36} r=15" if (i * 7) % 3 == 0 else f"x={26 + (i % 4) * 39} y={14 + (i // 4) * 36} width=30 height=30"} class="{["sk-f", "sk-g", "sk-g2"][i % 3]}"/>' for i in range(12))
            + '<text x="186" y="124" text-anchor="end" font-size="10" font-weight="800" class="sv-ink">14 AD CUTS</text>',
    "phone_q": '<rect x="72" y="10" width="56" height="110" rx="8" class="sk-l"/><g class="sk-g"><rect x="80" y="24" width="18" height="18"/><rect x="102" y="24" width="18" height="18"/><rect x="80" y="46" width="18" height="18"/><rect x="102" y="46" width="18" height="18"/><rect x="80" y="68" width="18" height="18"/><rect x="102" y="68" width="18" height="18"/></g><text x="150" y="44" font-size="26" font-weight="800" class="sv-ink">?</text><text x="40" y="70" font-size="20" font-weight="800" class="sv-ink">?</text>',
    "picks": '<rect x="18" y="12" width="164" height="104" class="sk-l"/><rect x="28" y="20" width="70" height="6" class="sk-f"/>'
             + "".join(f'<text x="30" y="{45 + i * 17}" font-size="9" font-weight="800" class="sv-ink">0{i + 1}</text><rect x="46" y="{38 + i * 17}" width="{90 - i * 8}" height="7" class="{"sk-f" if i < 2 else "sk-g"}"/><circle cx="166" cy="{42 + i * 17}" r="5" class="{"sk-f" if i < 2 else "sk-g"}"/>' for i in range(4)),
    "up": '<path d="M30 14v96h150" class="sk-l"/><path d="M38 96 L70 90 L100 80 L130 56 L170 26" class="sk-l" style="stroke-width:3"/><circle cx="170" cy="26" r="5" class="sk-f"/><text x="44" y="22" font-size="10" font-weight="800" class="sv-ink">SAVES</text><rect x="120" y="88" width="50" height="16" class="sk-g2"/><text x="145" y="100" text-anchor="middle" font-size="8" font-weight="800" class="sv-ink">CAROUSEL</text>',
    "alert": '<g class="sk-g"><rect x="22" y="24" width="46" height="70"/><rect x="77" y="24" width="46" height="70"/><rect x="132" y="24" width="46" height="70"/></g><g class="sk-f"><circle cx="45" cy="52" r="10"/><circle cx="100" cy="52" r="10"/><circle cx="155" cy="52" r="10"/></g><text x="100" y="116" text-anchor="middle" font-size="13" font-weight="800" class="sv-heat">FREQ 4.1, CTR FALLING</text>',
    "swap": '<rect x="18" y="20" width="50" height="88" rx="6" class="sk-l"/><rect x="26" y="32" width="34" height="50" class="sk-f"/><text x="43" y="98" text-anchor="middle" font-size="7" font-weight="800" class="sv-ink">REEL</text>'
            '<path d="M76 64h40" class="sk-l" style="stroke-width:3"/><path d="M108 56l10 8-10 8" class="sk-l" style="stroke-width:3"/>'
            '<rect x="126" y="20" width="56" height="88" class="sk-l"/><rect x="134" y="30" width="40" height="50" class="sk-g"/><circle cx="154" cy="55" r="10" class="sk-f"/><rect x="134" y="86" width="40" height="12" class="sk-f"/><text x="154" y="95" text-anchor="middle" font-size="7" font-weight="800" fill="#fff">AD</text>',
    "memory": "".join(f'<rect x="{40 + i * 6}" y="{20 + i * 8}" width="110" height="60" class="{"sk-g2" if i < 3 else "sk-l"}" style="fill:{["#e6e6e6", "#ededed", "#f4f4f4", "#fff"][i]}"/>' for i in range(4))
              + '<rect x="70" y="56" width="70" height="6" class="sk-f"/><rect x="70" y="68" width="50" height="4" class="sk-g"/><rect x="70" y="76" width="60" height="4" class="sk-g"/><text x="100" y="124" text-anchor="middle" font-size="9" font-weight="800" class="sv-ink">SAVED FOR NEXT DROP</text>',
}

BOARDS = {
    1: ("Storyboard 1: planning a drop's ads before the shoot", "Naina, Aditya, Karan", [
        ("desk", "Naina", "Drop in 14 days", "Last drop's ads looked alike. The planning board is empty and the shoot is booked for next week."),
        ("dash", "Naina", "Sees what worked", "The dashboard shows creator try-on ads cost less per sale than studio lookbooks over three drops."),
        ("ideas", "Naina, Aditya", "Gets ad ideas with reasons", "Claude AI suggests four ad angles, each with the evidence behind it and competitor ads from the Meta Ad Library."),
        ("plan", "Aditya", "Turns ideas into a shoot plan", "The chosen angles become a shot list with every ratio needed for Reels, feed and ads."),
        ("set", "Karan", "Shoots from the plan", "On set, Karan follows the list on his phone and ticks off each shot. No ad format is asked for after the wrap."),
        ("many", "Team", "More ads from one day", "The shoot gives 14 usable ad cuts instead of four, across four angles."),
    ], "Planning ads before the shoot turns one shoot day into more, and more varied, ads."),
    2: ("Storyboard 2: a week of organic posts and a tired ad", "Riya, Aditya", [
        ("phone_q", "Riya", "Monday, blank page", "Riya has to plan the week's posts and has no new ideas."),
        ("picks", "Riya", "Weekly picks", "The dashboard gives five post ideas based on BLUORNG's most-saved posts and what premium peers post."),
        ("up", "Riya", "Styling carousel lands", "She posts a styling carousel. Saves rise well above the page's average."),
        ("alert", "Aditya", "A running ad gets tired", "Aditya gets an alert: the lookbook ad is shown too often and clicks are falling."),
        ("swap", "Aditya, Riya", "Organic winner becomes an ad", "The dashboard suggests turning Riya's carousel and a close-up Reel into new ads, with hooks to test."),
        ("memory", "Team", "Learning is kept", "What worked this week is saved, so the next planning meeting starts from evidence."),
    ], "Organic and paid stop running apart: winners from the feed feed the ads."),
}


def storyboard(n):
    title, who, frames, take = BOARDS[n]
    cells = "".join(
        f'<div class="sbf"><svg viewBox="0 0 200 130">{SK[k]}</svg><div class="cap"><span class="sbn">{i + 1:02d}</span><span class="who">{e(p)}</span><b>{e(t)}</b><p>{e(d)}</p></div></div>'
        for i, (k, p, t, d) in enumerate(frames))
    return dict(kind="content", phase="Ideate", stage="Storyboarding", title=title.split(": ")[1].capitalize(),
                lead=f"Storyboard {n}. {who}. Sketches of the team using the chosen direction.",
                body=f'<div class="sbg">{cells}</div>', take=take, source="", w=980)


# ---------------------------------------------------------------- render
def number(P):
    """Add stage list for the contents page."""
    toc, cur = [], None
    for i, p in enumerate(P, 1):
        p["no"] = i
        if p["kind"] == "divider":
            cur = [p, []]
            toc.append(cur)
        elif p["kind"] == "content" and cur:
            st = p["stage"].split(" / ")[0]
            if not any(s == st for s, _ in cur[1]):
                cur[1].append((st, i))
    return toc


def header(p, logos, total):
    return (f'<div class="hd"><span>{e(p.get("phase", ""))}{" / " + e(p["stage"]) if p.get("stage") else ""}</span>'
            f'<span class="hr">{logos["{{SVG_monogram}}"]}<b>{p["no"]:02d}</b></span></div>')


def render(P, logos):
    toc = number(P)
    total = len(P)
    out = []
    for p in P:
        k = p["kind"]
        if k == "cover":
            inner = f'''<div class="cb inv cover">
  <div class="cv-word">{logos["{{SVG_wordmark}}"]}</div>
  <img class="cv-mark" src="{img("cover.webp")}" alt="">
  <div class="cv-top"><span class="lockup">{logos["{{SVG_monogram}}"]}</span><span class="lbl">UI/UX graduation project / UX case study</span></div>
  <div class="cv-copy"><span class="lbl">Project proposal to usability evaluation and test report</span>
    <h1>What should BLUORNG make next?</h1>
    <p>{e(PROJECT_TITLE)}</p></div>
  <div class="cv-meta"><div><span>Industry partner</span><b>BLUORNG, New Delhi</b></div><div><span>Role</span><b>UX designer</b></div><div><span>Duration</span><b>4 months</b></div><div><span>Student</span><b class="fill">Name, enrolment no.</b></div></div>
</div>'''
        elif k == "contents":
            cols = "".join(
                f'<div class="toc-c"><div class="toc-h"><b>{d["n"]}</b><span>{e(d["title"])}</span><i>{d["no"]:02d}</i></div><ul>'
                + "".join(f'<li><span>{e(s)}</span><i>{n:02d}</i></li>' for s, n in stages) + "</ul></div>"
                for d, stages in toc)
            inner = f'''<div class="cb">{header(dict(no=p["no"], phase="Contents"), logos, total)}
  <h2 class="ttl">Contents</h2><p class="lead">The case study follows the design process in order. Each page leads to the next.</p>
  <div class="toc">{cols}</div>
  <div class="dd"><span>Month 1 · Discover</span><span>Month 2 · Research, define</span><span>Month 3 · Ideate</span><span>Month 4 · Design, test</span></div></div>'''
        elif k == "divider":
            inner = f'''<div class="cb divider">
  <div class="dv-copy"><span class="lbl">Phase {p["n"]}</span><div class="dv-n">{p["n"]}</div><h2>{e(p["title"])}</h2><p>{e(p["text"])}</p>{chips(p["stages"])}</div>
  <img class="dv-mark" src="{img(f"mark-{p['mark']}.webp")}" alt="">
  <span class="dv-pg">{logos["{{SVG_monogram}}"]}<b>{p["no"]:02d}</b></span></div>'''
        elif k == "end":
            inner = f'''<div class="cb inv endp">
  <span class="lockup">{logos["{{SVG_monogram}}"]}<span class="x">×</span><span class="bp">BLUPRINT</span></span>
  <div class="end-copy"><span class="lbl">Final solution · UI/UX graduation project 2026</span><h2>Thank you</h2>
  <p>BLUPRINT: a content audit and planning dashboard that tells BLUORNG's team what is working on Instagram, what to avoid, and what to make next, with a 30-day calendar to act on it.</p>
  <div class="next">{"".join(f"<span>{x}</span>" for x in ["Discover", "Research", "Define", "Ideate", "Design", "Visual design", "Prototype", "Test"])}</div></div>
  <p class="disc">A UI/UX graduation project made with BLUORNG. Survey, interview and usability data in this document are a sample study; dashboard numbers are demo data. Not an official BLUORNG publication.</p>
  <div class="ew">{logos["{{SVG_wordmark}}"]}</div></div>'''
        else:
            lead = f'<p class="lead">{e(p["lead"])}</p>' if p.get("lead") else ""
            take = f'<div class="take"><small>Takeaway</small><span>{e(p["take"])}</span></div>' if p.get("take") else ""
            sample = "Sample" in (p.get("source") or "")
            src = f'<div class="src">{"<span class=samp>Sample data</span>" if sample else ""}Source: {e(p["source"])}</div>' if p.get("source") else ""
            inner = f'''<div class="cb">{header(p, logos, total)}
  <h2 class="ttl">{e(p["title"])}</h2>{lead}
  <div class="s-body"><div class="s-fit doc" style="width:{p["w"]}px">{p["body"]}</div></div>
  {take}{src}</div>'''
        out.append(f'<section class="slide">{inner}</section>')
    return "\n".join(out)


CSS = r'''
html, body { background: #2a2a2a; margin: 0; }
.pages { display: flex; flex-direction: column; align-items: center; gap: 24px; padding: 24px 0; }
.slide { width: 297mm; height: 210mm; position: relative; overflow: hidden; background: #fff; flex: none; color: var(--ink); }
.slide > .cb { position: absolute; left: 33.867mm; top: 23.989mm; width: 239.183mm; height: 161.925mm; display: flex; flex-direction: column; overflow: hidden; }
html.grid .slide::before { content: ""; position: absolute; left: 33.867mm; top: 23.989mm; width: 239.183mm; height: 161.925mm; background: rgba(1, 219, 144, .25); }
.hd { display: flex; justify-content: space-between; align-items: center; font: 600 8.5px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); padding-bottom: 8px; border-bottom: 1px solid var(--ink); }
.hd .hr { display: flex; align-items: center; gap: 10px; }
.hd .logo { height: 11px; width: auto; color: var(--ink); }
.hd b { font: 500 9px/1 var(--mono); color: var(--ink); letter-spacing: 0; }
.ttl { margin: 12px 0 0; font: 800 27px/0.98 var(--display); text-transform: uppercase; letter-spacing: -0.02em; }
.lead { margin: 6px 0 0; font-size: 12px; line-height: 1.45; color: var(--ink-2); }
.s-body { flex: 1; min-height: 0; margin-top: 12px; position: relative; }
.s-fit { transform-origin: top left; position: absolute; left: 0; top: 0; }
.s-fit > *:first-child { margin-top: 0 !important; }
.s-fit > *:last-child { margin-bottom: 0 !important; }
.take { margin-top: 10px; display: flex; gap: 12px; align-items: baseline; padding: 8px 12px; background: var(--bg-2); border-left: 3px solid var(--ink); font: 600 11.5px/1.4 var(--body); color: var(--ink); }
.take small { flex: none; font: 700 8px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.src { margin-top: 6px; font: 500 8px/1.3 var(--display); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); display: flex; gap: 8px; align-items: center; }
.src .samp { font: 700 7.5px/1 var(--display); padding: 3px 5px; background: var(--ink); color: #fff; letter-spacing: .12em; }
.doc { max-width: none; }
.doc .tiles, .doc .grid2, .doc .grid3, .doc .callout, .doc .personas, .doc .emp-grid { margin: 12px 0; }
.doc .panel { padding: 16px; }
/* survey questionnaire, interviews, brainstorming */
.ql { margin: 0; padding-left: 0; list-style: none; display: grid; gap: 7px; counter-reset: q; }
.doc .ql li { margin: 0; font-size: 12.5px; line-height: 1.4; color: var(--ink-2); max-width: none; }
.ql li b { font: 600 10.5px/1 var(--mono); color: var(--ink); margin-right: 4px; }
ol.ql:not(:has(b)) li { counter-increment: q; } ol.ql:not(:has(b)) li::before { content: counter(q, decimal-leading-zero) "  "; font: 600 10.5px/1 var(--mono); color: var(--ink); }
.iv { background: var(--bg-2); padding: 18px; display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.iv-h { display: flex; gap: 12px; align-items: center; }
.iv-h .mono-av { width: 42px; height: 42px; font-size: 13px; flex: none; }
.iv-h b { display: block; font: 800 13px/1.2 var(--display); text-transform: uppercase; letter-spacing: .03em; }
.iv-h span { font: 500 10.5px/1.2 var(--mono); color: var(--muted); }
.iv-q { margin: 0; font: 600 15px/1.4 var(--body); color: var(--ink); }
.qa { display: grid; grid-template-columns: 30px minmax(0, 1fr); gap: 8px; padding-top: 8px; border-top: 1px solid var(--line); }
.qa span { font: 600 10.5px/1.5 var(--mono); color: var(--muted); }
.qa p { margin: 0; font-size: 12.5px; line-height: 1.45; color: var(--ink-2); }
.mind { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-template-rows: auto auto auto; gap: 12px; }
.mind-c { grid-column: 1 / -1; background: var(--ink); color: #fff; padding: 16px 20px; font: 800 18px/1.2 var(--display); text-transform: uppercase; text-align: center; }
.mind-b { background: var(--bg-2); padding: 14px; display: grid; gap: 10px; align-content: start; border-top: 3px solid var(--ink); }
.mind-b h6 { margin: 0; font: 800 12px/1.2 var(--display); text-transform: uppercase; letter-spacing: .06em; }
.p-bio { margin: 0; font-size: 12.5px; color: var(--ink-2); }
.tiles .t .n { font-size: 34px; }
.slide .gantt { row-gap: 3px; }
.slide .gantt .ph-label { margin-top: 8px; font-size: 10px; }
.slide .gantt .tl { font-size: 12px; line-height: 1.25; }
.slide .gantt .bar { height: 13px; }
.slide .t ul, .slide .p-grid ul { list-style: square; padding-left: 16px; }
.slide .t li::marker { color: var(--muted); } .slide .t.dk li::marker { color: #777; }
.qs { display: grid; gap: 8px; align-content: start; }
.qs .chart-t { margin: 0 0 2px; }
.qc { background: var(--bg-2); padding: 10px 12px; display: grid; gap: 7px; }
.qc-h { display: grid; grid-template-columns: 32px minmax(0, 1fr) auto; gap: 8px; align-items: baseline; }
.qc-h b { font: 600 11px/1 var(--mono); }
.qc-h span { font: 600 12.5px/1.35 var(--body); color: var(--ink); }
.qc-h i { font: 600 8px/1 var(--display); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-style: normal; white-space: nowrap; }
.qc-o { display: flex; flex-wrap: wrap; gap: 4px; padding-left: 40px; }
.qc-o.same { font-size: 10.5px; color: var(--muted); font-style: italic; }
.qs .qs { padding: 0; }
.qc-o span { font-size: 10.5px; line-height: 1.2; padding: 3px 7px; background: #fff; border: 1px solid var(--line); color: var(--ink-2); }
.toc-c { padding: 10px 12px !important; gap: 7px !important; } .toc-h { padding-bottom: 6px !important; } .toc-h b { font-size: 22px !important; }
.toc ul { gap: 3px !important; } .toc li { font-size: 10px !important; line-height: 1.25 !important; }
.endp .lockup .x { color: #8c8c8c; font-size: 11px; margin: 0 8px; } .endp .lockup .bp { font: 900 15px/1 var(--display); letter-spacing: .04em; }
/* month 4 */
.flow .fl-e { fill: none; stroke: var(--ink); stroke-width: 1.4; } .flow .fl-ah { fill: var(--ink); }
.flow .fl-term { fill: var(--ink); } .flow .fl-proc { fill: #fff; stroke: var(--ink); stroke-width: 1.4; }
.flow .fl-screen { fill: var(--bg-2); stroke: var(--ink); stroke-width: 1.4; } .flow .fl-bar { fill: var(--ink); }
.flow .fl-act { fill: #fff; stroke: var(--ink); stroke-width: 1.4; stroke-dasharray: 4 3; } .flow .fl-dec { fill: #fff; stroke: var(--heat); stroke-width: 1.6; }
.flow .fl-t { font: 600 11px/1 var(--body); fill: var(--ink); } .flow .fl-tw { font: 600 11px/1 var(--body); fill: #fff; }
.flow .fl-l { font: 700 9px/1 var(--display); letter-spacing: .1em; text-transform: uppercase; fill: var(--heat); }
.lg-k { display: inline-block; width: 16px; height: 11px; border: 1.4px solid var(--ink); } .lg-k.term { background: var(--ink); border-radius: 6px; }
.lg-k.scr { background: var(--bg-2); border-top-width: 3px; } .lg-k.dec { border-color: var(--heat); transform: rotate(45deg) scale(.8); } .lg-k.act { border-style: dashed; }
.pfs { display: grid; gap: 10px; } .pf { background: var(--bg-2); padding: 14px 16px; display: grid; grid-template-columns: 250px minmax(0, 1fr); gap: 16px; align-items: center; }
.pf-steps { display: flex; align-items: center; gap: 0; } .pf-steps span { flex: 1; background: #fff; padding: 10px 10px; font-size: 12.5px; line-height: 1.3; position: relative; margin-right: 16px; }
.pf-steps span:not(:last-child)::after { content: "→"; position: absolute; right: -13px; top: 50%; transform: translateY(-50%); color: var(--ink); font-size: 12px; }
.pf-steps span:last-child { background: var(--ink); color: #fff; margin-right: 0; }
.fb .col.wont { opacity: .55; } .fb .col.wont .ft { border-style: dashed; }
.dt2 { width: 100%; border-collapse: collapse; font-size: 12.5px; table-layout: fixed; }
.dt2 th { text-align: left; font: 700 9.5px/1.3 var(--display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); padding: 0 10px 8px 0; border-bottom: 1px solid var(--ink); }
.dt2 td { padding: 8px 10px 8px 0; border-bottom: 1px solid var(--line); vertical-align: top; color: var(--ink-2); line-height: 1.4; min-width: 0 !important; }
.dt2 td:first-child { color: var(--ink); font-weight: 600; } .dt2 td small { display: block; color: var(--muted); font-size: 11px; font-weight: 400; }
.st { display: inline-block; font: 700 9px/1 var(--display); letter-spacing: .1em; text-transform: uppercase; padding: 4px 6px; border: 1px solid var(--ink); white-space: nowrap; }
.st.ok { background: var(--ink); color: #fff; } .st.fx { background: #fff; color: var(--ink); } .st.pt { color: var(--heat); border-color: var(--heat); } .st.nx { color: var(--muted); border-color: var(--line); border-style: dashed; }
.sev { display: inline-grid; place-items: center; width: 22px; height: 22px; font: 700 11px/1 var(--mono); border: 1px solid var(--ink); }
.sev.s3 { background: var(--heat); border-color: var(--heat); color: #fff; } .sev.s2 { background: var(--ink); color: #fff; }
.tiles.c1 { --cols: 1; } .tiles.c1 .t { padding: 14px 16px; }
.tokens { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 10px; align-items: center; margin-top: 4px; }
.tokens > div:not(.tk-arr) { background: var(--bg-2); padding: 16px; display: grid; gap: 6px; } .tokens b { font: 800 13px/1.2 var(--display); text-transform: uppercase; letter-spacing: .06em; }
.tokens span { font-size: 12.5px; color: var(--ink-2); } .tk-arr { font-size: 22px; }
.sws { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-bottom: 12px; }
.sw { display: grid; gap: 2px; } .sw i { height: 64px; display: block; margin-bottom: 6px; } .sw b { font: 800 12px/1.2 var(--display); text-transform: uppercase; letter-spacing: .06em; }
.sw code { font: 500 11.5px/1.2 var(--mono); } .sw span { font: 500 11px/1.2 var(--mono); color: var(--muted); } .sw small { font-size: 11.5px; color: var(--ink-2); line-height: 1.35; }
.sw em { font: 600 10px/1.2 var(--display); font-style: normal; letter-spacing: .08em; text-transform: uppercase; color: var(--ink); }
.dm { display: flex; gap: 18px; flex-wrap: wrap; } .dm span { display: inline-flex; gap: 8px; align-items: center; font-size: 13px; } .dm i { width: 36px; height: 12px; display: block; }
.ramp5 { display: flex; gap: 3px; } .ramp5 i { flex: 1; height: 34px; display: block; }
.tyg { display: grid; grid-template-columns: 1.3fr 1fr; gap: 12px; margin-bottom: 14px; } .ty { background: var(--bg-2); padding: 18px; display: flex; flex-direction: column; }
.ty-d { margin: 8px 0 0; font: 800 64px/.9 var(--display); text-transform: uppercase; letter-spacing: -.035em; } .ty-d2 { margin: 8px 0 0; font: 800 30px/1 var(--display); text-transform: uppercase; letter-spacing: -.02em; }
.ty-b { margin: 8px 0 0; font: 400 16px/1.5 var(--body); } .ty-m { margin: 8px 0 0; font: 500 18px/1.3 var(--mono); }
.icns { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }
.icn { background: var(--bg-2); padding: 16px 12px; display: grid; justify-items: center; gap: 6px; text-align: center; }
.icn svg { width: 36px; height: 36px; fill: none; stroke: var(--ink); stroke-width: 1.75; stroke-linecap: square; }
.icn b { font: 700 11px/1 var(--display); text-transform: uppercase; letter-spacing: .1em; } .icn span { font-size: 11.5px; color: var(--muted); line-height: 1.3; }
.icn .glyph { font-size: 26px; line-height: 36px; height: 36px; color: var(--ink); } .kline, .kdot, .ksq { display: inline-block; background: var(--ink); vertical-align: middle; }
.kline { width: 30px; height: 3px; } .kdot { width: 12px; height: 12px; border-radius: 50%; } .ksq { width: 14px; height: 14px; }
.comps { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px 16px; } .comps.c4 { grid-template-columns: repeat(4, minmax(0, 1fr)); align-items: start; }
.cmp { display: grid; gap: 4px; align-content: start; } .cmp-img { background: var(--bg-2); padding: 10px; display: grid; place-items: center; }
.cmp-img .shot { max-width: 100%; height: auto; display: block; } .comps:not(.c4) .cmp-img { min-height: 70px; }
.cmp b { font: 800 11.5px/1.2 var(--display); text-transform: uppercase; letter-spacing: .08em; margin-top: 4px; } .cmp > span { font-size: 11.5px; color: var(--muted); line-height: 1.35; }
.shot { display: block; max-width: 100%; height: auto; }
.bframe { border: 1px solid var(--line); background: #fff; } .bbar { height: 20px; display: flex; align-items: center; gap: 5px; padding: 0 8px; background: var(--bg-2); border-bottom: 1px solid var(--line); }
.bbar i { width: 6px; height: 6px; border-radius: 50%; background: #c8c8c8; } .bbar span { margin-left: 10px; font: 500 9px/1 var(--mono); color: var(--muted); }
.bframe .shot { width: 100%; }
.pframe { border: 6px solid #0b0b0b; border-radius: 22px; overflow: hidden; background: #0b0b0b; } .pframe .shot { width: 100%; }
.wfl { display: flex; align-items: flex-start; gap: 8px; } .wfl-s { flex: 1; min-width: 0; display: grid; gap: 4px; }
.wfl-s b { font: 800 11.5px/1.2 var(--display); text-transform: uppercase; letter-spacing: .08em; margin-top: 6px; } .wfl-s span { font-size: 11.5px; color: var(--muted); }
.wfl-a { font-size: 22px; padding-top: 70px; } .wfl.m .wfl-a { padding-top: 160px; }
.phones-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 12px; padding-inline: 30px; }
.ph-slot { margin-top: 10px; border: 1.5px dashed var(--line); padding: 26px; text-align: center; font: 600 10px/1.3 var(--display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.wf { background: #fff; } .wf .wf-b { fill: #fff; stroke: #0b0b0b; stroke-width: 1.6; stroke-linejoin: round; } .wf .wf-d { fill: #3a3a3a; stroke: #0b0b0b; stroke-width: 1.6; }
.wf .wf-m { fill: #e8e8e8; stroke: #bdbdbd; } .wf .wf-md { fill: #6e6e6e; } .wf .wf-x { fill: none; stroke: #fff; stroke-width: 1.6; stroke-dasharray: 5 4; }
.wf .wf-wb { fill: #fff; } .wf .wf-wo { fill: none; stroke: #fff; stroke-width: 1.4; } .wf .wf-hd { fill: #0b0b0b; } .wf .wf-none { fill: transparent; }
.wf .wf-s { fill: none; stroke: #8a8a8a; stroke-width: 1.4; stroke-linecap: round; } .wf .wf-tx { fill: #c4c4c4; }
.wf .wf-bar { fill: #0b0b0b; } .wf .wf-red { fill: var(--heat); } .wf .wf-line { fill: none; stroke: #0b0b0b; stroke-width: 2; } .wf .wf-rule { stroke: #d0d0d0; }
.wf .wf-lab { font: 700 7.5px/1 var(--display); letter-spacing: .08em; fill: #3b3b3b; } .wf .wf-c { text-anchor: middle; } .wf .wf-r { text-anchor: end; } .wf .wf-w { fill: #fff; }
.wf .wf-big { font-size: 14px; letter-spacing: -.01em; font-weight: 800; } .wf .wf-big2 { font-size: 13px; font-weight: 800; fill: #fff; }
.gcol { fill: color-mix(in srgb, var(--heat) 16%, transparent); } .gframe { fill: none; stroke: var(--ink); stroke-width: 1.2; } .gl-t { font: 700 9px/1 var(--display); letter-spacing: .1em; text-transform: uppercase; fill: var(--ink); }

.panel .hm { width: 100%; table-layout: fixed; min-width: 0; } .panel .hm td.s { width: auto; } .panel .hm th, .panel .hm td { padding: 8px 8px; } .doc .hm th { white-space: normal; } .hm td:first-child, .hm th:first-child { width: 44%; }
svg.wf { width: 100%; height: auto; display: block; }
.comps.rows { grid-template-columns: 1fr; gap: 10px; } .comps.rows .cmp { grid-template-columns: minmax(0, 2.3fr) minmax(0, 1fr); gap: 16px; align-items: center; }
.comps.rows .cmp-img { min-height: 0; padding: 12px; } .comps.rows .cmp b { display: block; margin: 0 0 4px; } .comps.rows .cmp span { font-size: 11.5px; color: var(--muted); }
.bbar span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.wfl .bframe .shot { aspect-ratio: 16 / 10; object-fit: cover; object-position: top; }
.wfl.m .pframe .shot { aspect-ratio: 390 / 760; object-fit: cover; object-position: top; }
.ba2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 14px; } .ba2 .bframe .shot { aspect-ratio: 16 / 9; object-fit: cover; object-position: top; }
.lbl2 { font: 700 10px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; }
/* storyboard */
.sbg { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.sbf { background: var(--bg-2); padding: 10px; display: grid; grid-template-columns: 46% minmax(0, 1fr); gap: 14px; align-items: center; }
.sbf svg { width: 100%; height: auto; display: block; background: #fff; }
.sbf .cap { display: grid; grid-template-columns: auto 1fr; gap: 3px 8px; align-items: baseline; }
.sbf .sbn { font: 800 11px/1 var(--mono); color: var(--ink); }
.sbf .who { font: 600 9px/1 var(--display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.sbf .cap b { grid-column: 1 / -1; font: 800 13px/1.2 var(--display); text-transform: uppercase; }
.sbf .cap p { grid-column: 1 / -1; margin: 0; font-size: 12px; line-height: 1.4; color: var(--ink-2); }
/* cover */
.slide > .cb.cover { background: radial-gradient(ellipse 60% 70% at 72% 40%, #262626 0%, #0a0a0a 70%); padding: 26px 30px; }
.cv-word { position: absolute; left: 50%; top: 46%; transform: translate(-50%, -50%); width: 112%; color: #fff; opacity: .045; }
.cv-mark { position: absolute; right: 6px; top: 50px; width: 42%; height: auto; }
.cv-top { position: relative; display: flex; justify-content: space-between; align-items: center; }
.lockup { display: flex; align-items: center; color: var(--ink); }
.lockup .logo { height: 20px; width: auto; }
.lbl { font: 600 9px/1.2 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.cv-copy { position: absolute; left: 30px; bottom: 96px; width: 62%; }
.cv-copy h1 { margin: 12px 0 0; font: 800 58px/0.9 var(--display); text-transform: uppercase; letter-spacing: -0.03em; }
.cv-copy p { margin: 16px 0 0; max-width: 52ch; font-size: 13px; line-height: 1.5; color: var(--ink-2); }
.cv-meta { position: absolute; left: 30px; right: 30px; bottom: 26px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; padding-top: 14px; border-top: 1px solid #333; }
.cv-meta span { display: block; font: 600 8px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.cv-meta b { font: 600 11px/1.3 var(--display); letter-spacing: .06em; text-transform: uppercase; }
.cv-meta b.fill { color: #777; }
/* contents */
.toc { flex: 1; margin-top: 14px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-template-rows: repeat(2, minmax(0, 1fr)); gap: 8px; min-height: 0; }
.toc-c { background: var(--bg-2); padding: 14px; display: flex; flex-direction: column; gap: 12px; }
.toc-h { display: grid; grid-template-columns: 1fr auto; gap: 4px; padding-bottom: 10px; border-bottom: 1px solid var(--ink); }
.toc-h b { grid-column: 1 / -1; font: 800 34px/1 var(--display); letter-spacing: -0.02em; }
.toc-h span { font: 800 13px/1.1 var(--display); text-transform: uppercase; }
.toc-h i, .toc li i { font: 500 10px/1.3 var(--mono); font-style: normal; color: var(--muted); }
.toc ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 7px; }
.toc li { display: flex; justify-content: space-between; gap: 8px; font-size: 11.5px; line-height: 1.3; color: var(--ink-2); }
.dd { margin-top: 12px; display: flex; gap: 2px; }
.dd span { flex: 1; padding: 7px 10px; background: var(--ink); color: #fff; font: 700 8.5px/1 var(--display); letter-spacing: .12em; text-transform: uppercase; }
.dd span.nx { background: transparent; color: var(--muted); border: 1px dashed var(--line); }
/* divider */
.slide > .cb.divider { background: var(--bg-2); flex-direction: row; align-items: center; gap: 20px; padding: 30px 34px; }
.dv-copy { flex: 1; min-width: 0; }
.dv-n { margin-top: 10px; font: 800 96px/0.85 var(--display); letter-spacing: -0.04em; color: #d6d6d6; }
.dv-copy h2 { margin: 6px 0 0; font: 800 54px/0.9 var(--display); text-transform: uppercase; letter-spacing: -0.03em; }
.dv-copy p { margin: 16px 0 18px; font-size: 13.5px; line-height: 1.5; color: var(--ink-2); max-width: 44ch; }
.dv-copy .chips span { background: #fff; }
.dv-mark { width: 38%; max-height: 90%; object-fit: contain; height: auto; filter: drop-shadow(0 26px 22px rgba(0,0,0,.16)); }
.dv-pg { position: absolute; right: 34px; top: 30px; display: flex; gap: 10px; align-items: center; }
.dv-pg .logo { height: 11px; width: auto; } .dv-pg b { font: 500 9px/1 var(--mono); }
/* end */
.slide > .cb.endp { padding: 30px 34px; justify-content: space-between; }
.endp .lockup { color: #f4f4f4; }
.end-copy h2 { margin: 10px 0 0; font: 800 60px/0.9 var(--display); text-transform: uppercase; letter-spacing: -0.03em; }
.end-copy p { margin: 16px 0 0; max-width: 60ch; font-size: 13px; line-height: 1.5; color: var(--ink-2); }
.next { margin-top: 18px; display: flex; flex-wrap: wrap; gap: 6px; }
.next span { font: 600 9px/1 var(--display); letter-spacing: .1em; text-transform: uppercase; padding: 7px 9px; border: 1px solid #3a3a3a; color: #f4f4f4; }
.endp .disc { margin: 0; font-size: 10px; color: var(--muted); position: relative; }
.endp .ew { position: absolute; left: 34px; right: 34px; bottom: 50px; color: #f4f4f4; opacity: .07; }
@page { margin: 0; }
@media print { html, body { background: none; } .pages { padding: 0; gap: 0; display: block; } .slide { break-after: page; break-inside: avoid; }
  .slide * { break-inside: auto !important; break-before: auto !important; break-after: auto !important; } }
'''

FIT_JS = r'''
<script>
(function () {
  function fit() {
    var report = [];
    document.querySelectorAll('.s-body').forEach(function (body) {
      var el = body.querySelector('.s-fit');
      el.style.transform = 'none';
      var bw = body.clientWidth, bh = body.clientHeight;
      var base = parseInt(el.dataset.w || el.style.width, 10);
      el.dataset.w = base;
      var best = null;
      [1.2, 1.12, 1.05, 1, 0.94, 0.88, 0.82, 0.76, 0.7].forEach(function (f) {
        var w = Math.round(base * f);
        el.style.width = w + 'px';
        var rw = Math.max(el.offsetWidth, el.scrollWidth), rh = el.scrollHeight;
        var s = Math.min(bw / rw, bh / rh, 1.15);
        if (!best || s > best.s + 0.01) best = { w: w, s: s, rw: rw, rh: rh };
      });
      el.style.width = best.w + 'px';
      el.style.transform = 'scale(' + best.s + ')';
      el.style.top = Math.max(0, (bh - best.rh * best.s) / 2) + 'px';
      el.style.left = Math.max(0, (bw - best.rw * best.s) / 2) + 'px';
      report.push(best.s.toFixed(2));
    });
    return report;
  }
  function scale() {
    if (document.documentElement.classList.contains('pdf')) return;
    var k = Math.min(1.4, (window.innerWidth - 32) / 1123);
    document.querySelectorAll('.slide').forEach(function (s) { s.style.zoom = k; });
  }
  window.fitSlides = fit;
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(function () { fit(); scale(); });
  addEventListener('resize', scale);
})();
</script>'''


def build(local_deps=None):
    logos = bb.load_logos()
    template = (BOOK / "template.html").read_text()
    css = re.search(r"<style>(.*?)</style>", template, flags=re.S).group(1)
    symbols = re.search(r'<svg width="0" height="0".*?</svg>', template, flags=re.S).group(0)
    P = pages()
    sb = [i for i, p in enumerate(P) if p["kind"] == "storyboard"]
    for i in sb:
        P[i] = storyboard(P[i]["n"])
    body = render(P, logos)
    head = '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<title>What should BLUORNG make next?</title>\n'
    if local_deps:
        head += bb.font_faces(local_deps)
    else:
        head += re.search(r'(<link rel="preconnect".*?display=swap">)', template, flags=re.S).group(1)
    page = f'<!doctype html><html lang="en"><head>{head}\n<style>{css}{CSS}</style></head><body>\n{symbols}\n<main class="pages">\n{body}\n</main>\n{FIT_JS}\n</body></html>\n'
    for k, v in logos.items():
        page = page.replace(k, v)
    assert "{{" not in page, re.findall(r"\{\{[\w:-]+\}\}", page)
    return page, len(P)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--local":
        out, (page, n) = pathlib.Path(sys.argv[3]), build(sys.argv[2])
    else:
        out, (page, n) = OUT, build()
    out.write_text(page)
    print(out, len(page), "pages:", n)
