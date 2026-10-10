"""Build the BLUPRINT presentation (16:9 slides) from the figures in tools/book/.

Run:  python3 tools/build_deck.py                        -> docs/bluprint-deck.html (fonts from Google Fonts)
      python3 tools/build_deck.py --local DEPS OUT.html  -> offline copy for PDF export (see tools/make_pdf.js)
"""
import base64
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_book as bb  # noqa: E402

BOOK = bb.BOOK
OUT = bb.ROOT / "docs" / "bluprint-deck.html"


def img(name):
    return "data:image/webp;base64," + base64.b64encode((BOOK / "renders" / name).read_bytes()).decode()


def tiles(items, cls=""):
    """items: (kicker, title, text, dark?)"""
    out = []
    for k, h, p, dk in items:
        out.append(f'<div class="t{" dk" if dk else ""}"><span class="k">{k}</span><h5>{h}</h5><p>{p}</p></div>')
    return f'<div class="tiles {cls}">' + "".join(out) + "</div>"


def slides(figs, logos):
    S = []
    part = [None]

    def add(title, body, sub="", source="", w=1240, sample=False):
        S.append(dict(kind="content", part=part[0], title=title, sub=sub, body=body, source=source, w=w, sample=sample))

    def divider(i):
        short, title, summary, stages = bb.CHAPTERS[i - 1]
        part[0] = (i, title)
        S.append(dict(kind="divider", i=i, title=title, summary=summary, stages=stages))

    template = (BOOK / "template.html").read_text()
    prods = re.findall(r'<article class="prod[^"]*">.*?</article>', template, flags=re.S)

    # ---------- opening ----------
    S.append(dict(kind="cover"))
    S.append(dict(kind="brand"))
    S.append(dict(kind="agenda"))

    # ---------- part 1 ----------
    divider(1)
    add("BLUPRINT", '<div class="callout" style="font-size:30px;padding:36px 40px"><small>Working title</small>A content intelligence and ideation platform that helps BLUORNG decide what to make for Instagram (organic) and Meta ads (paid).</div>'
        + tiles([("Name", "BLU + PRINT", "BLU from BLUORNG, PRINT from blueprint: a plan for every piece of content before a camera is switched on.", False),
                 ("Partner", "BLUORNG, New Delhi", "Premium streetwear label, founded 2020. GQ India Streetwear Label of the Year 2023.", False),
                 ("My role", "UI/UX designer", "Working inside the content team, so the content workflow can be observed first-hand.", True)]),
        sub="Project proposal")
    add("Background and problem",
        '<div class="grid2"><div class="t"><span class="k">Organic content</span><div class="chips"><span>Drop teasers</span><span>Lookbooks</span><span>Campaign films</span><span>Behind the scenes</span><span>Store launches</span><span>Collabs</span><span>Culture posts</span></div></div>'
        '<div class="t"><span class="k">Paid content, Meta ads</span><div class="chips"><span>Drops</span><span>Retargeting</span><span>Store footfall</span><span>Evergreen products</span></div></div></div>'
        '<div class="callout" style="font-size:26px;padding:32px 36px"><small>Initial brief</small>Drop-led streetwear teams have no structured, evidence-backed way to decide what to make for Instagram and Meta ads. Effort and spend go on guesswork, wins aren\'t repeated, and organic and paid run as separate worlds.</div>'
        '<div class="t dk"><span class="k">Aim</span><p style="font-size:18px">Turn performance data, brand identity and trend signals into on-brand content suggestions and ready-to-shoot briefs, for organic and paid.</p></div>',
        sub="Today, results sit in Insights, Ads Manager and Shopify, and decisions happen on WhatsApp.")
    add("Objectives", figs["objectives"])
    add("Scope and outcome", figs["scope"] + figs["outcome"])
    add("Method and value", figs["method"] + figs["value"], sub="Double Diamond: research, synthesise, ideate, deliver.")
    add("Project timeline", figs["timeline-sec"], sub="20 weeks, three reviews.", w=1400)

    # ---------- part 2 ----------
    divider(2)
    add("The brand", figs["brand"], sub="Domain study", source="Indian Retailer, Business News This Week, Fibre2Fashion, Mediainfoline, HAV Strategy", w=1400)
    add("The market", figs["market"], source="Deep Market Insights; Entrepreneur India; Fibre2Fashion")
    add("Which formats win?", figs["platforms-a"], sub="Fashion data favours Reels. Large accounts favour carousels.",
        source="Dash Social via NetInfluencer; Socialinsider 2026", w=1400)
    add("Paid runs on creative variety", figs["platforms-b"], source="Meta via B&T and AdNews; Jon Loomer; vendor benchmarks")
    add("Content taxonomy: organic series", figs["taxonomy-o"], sub="The shared vocabulary BLUPRINT learns from.", w=1400)
    add("Content taxonomy: paid angles", figs["taxonomy-p"])
    add("Existing tools", figs["tools"], sub="Competitive and analogous analysis.", source="Vendor sites and comparison pages (Atria, Segwise, Foreplay)", w=1300)
    add("Literature review", figs["lit"], sub="12 sources from marketing, psychology and HCI.", w=1500)
    add("What the literature says", figs["synth"])

    # ---------- part 3 ----------
    divider(3)
    add("Stakeholders map", figs["onion"], w=1300)
    add("Power and interest", figs["power"], w=1200)
    add("How content moves today", figs["asis"], sub="System mapping, current state.", w=1300)
    add("How it moves with BLUPRINT", figs["tobe"], sub="System mapping, future state.", w=1300)
    add("Problem tree", figs["tree"], w=1300)
    add("Problem clusters", figs["clusters"], w=1200)
    add("Five whys", figs["whys"], sub="Why did the last drop's ads underperform?")
    add("Problem area and target users",
        '<div class="callout" style="font-size:28px;padding:34px 38px"><small>Problem area</small>The ideation-to-brief stage: the moment the team decides what to make for Instagram and Meta ads. Today it is disconnected from results, brand rules and the drop calendar.</div>'
        + figs["targets"], w=1400)

    # ---------- part 4 ----------
    divider(4)
    add("Research questions", figs["rq"], sub="Primary research plan.", w=1300)
    add("Hypotheses", figs["hyp"], sub="What we expect to find. A rejected hypothesis is a finding too.", w=1400)
    add("Methods and sample", figs["methods"] + '<p class="chart-t">Ethics</p>' + figs["ethics"], w=1300)
    add("User segmentation", figs["segments"], w=1400)
    add("Research instruments", figs["instr"])
    add("The surveys", figs["surveymock"], sub="Survey A: 22 questions for practitioners. Survey B: 14 questions for the audience. Full list in the project files.", w=1100)
    R = dict(sample=True, source="Sample data for layout. Replace with your fieldwork results")
    add("Fieldwork completed", figs["r-overview"], sub="Primary research report.", w=1400, **R)
    add("What the team told us", figs["r-quotes-team"], sub="Interviews with six BLUORNG content and marketing team members.", w=1300, **R)
    add("What the audience told us", figs["r-quotes-aud"], sub="Interviews with four followers and buyers.", w=1300, **R)
    add("Interview themes", figs["r-themes"], sub="How many people raised each theme.", w=1400, **R)
    add("Survey A: how content gets decided", figs["r-sa1"], sub="24 practitioners from fashion and D2C brands.", w=1400, **R)
    add("Survey A: organic, paid and briefs", figs["r-sa2"], w=1400, **R)
    add("Survey A: problems and trust", figs["r-sa3"], w=1400, **R)
    add("Survey B: who answered", figs["r-sb1"], sub="132 streetwear followers aged 18 to 30.", w=1400, **R)
    add("Survey B: watch, save, buy", figs["r-sb2"], w=1500, **R)
    add("Survey B: ads and frequency", figs["r-sb3"], w=1400, **R)
    add("Focus groups", figs["r-focus"], w=1400, **R)
    add("Shadowing a drop week", figs["r-shadow"], w=1400, **R)
    add("Content audit", figs["r-audit"], w=1500, **R)
    add("Hypotheses: what held up", figs["r-hyp"], w=1400, **R)
    add("Key insights", figs["r-insights"], w=1400, **R)
    add("Priority areas", figs["priority"], w=1200)
    add("Redefined brief", figs["rebrief"], w=1300)
    add("Environment and context", figs["context"], w=1300)

    # ---------- part 5 ----------
    divider(5)
    add("Personas", figs["personas"], sub="Built from the team interviews and Survey A.", w=1400)
    add("Empathy maps", figs["empathy"], w=1400)
    add("User journey map", figs["journey"], sub="Planning content for a new drop, as it works today.", w=1400)
    add("Problem statement", figs["statement"], w=1400)
    add("Design goals", figs["goals"], sub="Each goal has a target we test in usability studies.", w=1300)

    # ---------- part 6 ----------
    divider(6)
    add("Brainstorming", figs["brainstorm"], sub="Driven by the six How Might We questions.", w=1400)
    add("Brainwriting", figs["brainwriting"], w=1400)
    add("SCAMPER", figs["scamper"], w=1300)
    add("Space saturation", figs["saturation"], w=1400)
    add("Crazy 8s", figs["crazy8"], sub="Eight home-screen layouts in eight minutes.", w=1300)
    add("Bullseye", figs["bullseye"], w=1200)
    add("Priority matrix", figs["matrix"], w=1100)
    add("Three concepts", figs["concepts"], w=1400)
    add("Concept evaluation", figs["scores2"], w=1500)
    add("Final concept", figs["venn"] + tiles([
        ("Research needs", "Top 3 priorities covered", "Knowing what works, organic ideas, and the organic to paid bridge.", True),
        ("Technology", "APIs exist", "Instagram Graph API and Meta Marketing API give the data. LLMs write ideas and briefs.", False),
        ("Process", "Fits the week", "Works inside weekly planning and the drop cycle. Replaces no one.", False),
        ("Modularity", "Ships in parts", "Pulse, Ideas, Briefs, Plan and Brand DNA can launch one at a time.", False)], "c4"),
        sub="Studio experience, powered by Pulse, organised by drop.", w=1300)

    # ---------- part 7 ----------
    divider(7)
    add("User scenarios", figs["scenarios"], w=1500)
    add("Storyboard 1", figs["sb1"], w=1500)
    add("Storyboard 2", figs["sb2"], w=1500)
    add("Primary user flow", figs["userflow"], w=1300)
    add("Task flows", '<p class="chart-t">Create a brief</p>' + figs["tf-brief"] + '<p class="chart-t">Promote an organic winner</p>' + figs["tf-promote"]
        + '<p class="chart-t">Approve a plan</p>' + figs["tf-approve"], w=1300)
    add("Task analysis", figs["hta"], w=1300)
    add("Time on task", figs["tasks"], w=1200)
    add("Feature mapping", figs["features"], w=1300)

    # ---------- part 8 ----------
    divider(8)
    add("Content strategy", figs["cgoals"] + figs["inventory"], w=1400)
    add("Content types", figs["ctypes"], w=1300)
    add("Voice and tone", figs["voice"])
    add("Organisation", figs["schemes"] + '<p class="chart-t">Card sorting plan</p>' + figs["cardsort"], w=1300)
    add("Sitemap", figs["sitemap"], w=1300)
    add("Navigation", figs["navmock"], w=1300)
    add("Labeling", figs["labels"], w=1300)
    add("How BLUPRINT works", figs["loop"], w=1100)
    add("Core modules", figs["modules"] + figs["devices"], w=1400)
    add("The product: Ideas", prods[0], sub="Concept screen. All numbers are example data.", w=1300)
    add("The product: on the move", '<div class="drop-grid">' + "".join(prods[1:]) + "</div>",
        sub="Concept screens. All numbers are example data.", w=1300)
    add("Value", figs["valuesum"], w=1200)
    add("Next stages", figs["nextsteps"], w=1300)
    S.append(dict(kind="end"))
    return S


def render(S, logos):
    out = []
    n = len(S)
    for idx, s in enumerate(S, 1):
        pg = f'<span class="pg">{idx:02d} / {n}</span>'
        k = s["kind"]
        if k == "cover":
            out.append(f'''<section class="slide inv cover">
  <div class="cv-word">{logos["{{SVG_wordmark}}"]}</div>
  <img class="cv-mark" src="{img("cover.webp")}" alt="">
  <div class="cv-top"><span class="lockup">{logos["{{SVG_monogram}}"]}<span class="x">×</span><span class="bp">BLUPRINT</span></span><span class="lbl">UI/UX graduation project</span></div>
  <div class="cv-copy"><span class="lbl">Project book / Proposal to proposed solution</span>
  <h1>What should BLUORNG make next?</h1>
  <p>BLUORNG blends global aesthetics with local sensibilities. BLUPRINT helps its team decide what to make next for Instagram and Meta ads, and turns every idea into a brief they can shoot.</p></div>
  <div class="cv-side"><span class="lbl">In collaboration with</span><b>BLUORNG, New Delhi</b></div>
</section>''')
        elif k == "brand":
            out.append(f'''<section class="slide inv brandslide">
  <div class="sc">{logos["{{SVG_script}}"]}</div>
  <p>BLUORNG, pronounced Blue~Orange, blends global aesthetics with local sensibilities, and sits among the top streetwear brands in India. Every drop starts with a feed. This project is about what goes on it.</p>
  <span class="lbl">New Delhi / Mumbai / Online</span>{pg}
</section>''')
        elif k == "agenda":
            tiles_ = "".join(
                f'<div class="ag"><span class="num">Part 0{i}</span><span class="r3d"><img src="{img(f"mark-{i}.webp")}" alt=""></span><div><h3>{html.escape(c[1])}</h3><div class="ct">{len(c[3])} stages</div></div></div>'
                for i, c in enumerate(bb.CHAPTERS, 1))
            out.append(f'''<section class="slide"><div class="s-top"><span>Contents</span>{pg}</div>
  <h2 class="s-title">The collection</h2><div class="agenda">{tiles_}</div></section>''')
        elif k == "divider":
            chips = "".join(f"<span>{html.escape(x)}</span>" for x in s["stages"])
            out.append(f'''<section class="slide divider">
  <div class="dv-copy"><span class="lbl">Part 0{s["i"]} of 08</span><h2>{html.escape(s["title"])}</h2><p>{html.escape(s["summary"])}</p><div class="stage-chips">{chips}</div></div>
  <img class="dv-mark" src="{img(f"mark-{s['i']}.webp")}" alt="">{pg}
</section>''')
        elif k == "end":
            out.append(f'''<section class="slide inv endslide">
  <span class="lockup">{logos["{{SVG_monogram}}"]}<span class="x">×</span><span class="bp">BLUPRINT</span></span>
  <h2>Thank you</h2><p>A UI/UX graduation project with BLUORNG. Not an official BLUORNG publication.</p>
  <div class="ew">{logos["{{SVG_wordmark}}"]}</div>
</section>''')
        else:
            i, ptitle = s["part"]
            src = f'<span>Source: {html.escape(s["source"])}</span>' if s["source"] else "<span></span>"
            sub = f'<p class="s-sub">{html.escape(s["sub"])}</p>' if s["sub"] else ""
            out.append(f'''<section class="slide"><div class="s-top"><span>Part 0{i} / {html.escape(ptitle)}</span><span class="tr">{'<span class="samp">Sample data</span>' if s.get("sample") else ""}{logos["{{SVG_monogram}}"]}{pg}</span></div>
  <h2 class="s-title">{html.escape(s["title"])}</h2>{sub}
  <div class="s-body"><div class="s-fit doc" style="width:{s["w"]}px">{s["body"]}</div></div>
  <div class="s-foot">{src}<span>BLUPRINT × BLUORNG</span></div></section>''')
    return "\n".join(out)


DECK_CSS = r'''
html, body { background: #1a1a1a; }
body { margin: 0; }
.deck { display: flex; flex-direction: column; align-items: center; gap: 24px; padding: 24px 0; }
.slide { width: 1920px; height: 1080px; position: relative; overflow: hidden; background: var(--bg); color: var(--ink); padding: 64px 96px 56px; display: flex; flex-direction: column; flex: none; }
.s-top { display: flex; justify-content: space-between; align-items: center; font: 600 14px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.s-top .tr { display: flex; align-items: center; gap: 18px; }
.s-top .logo { height: 20px; width: auto; color: var(--ink); }
.pg { font: 500 14px/1 var(--mono); letter-spacing: 0; color: var(--muted); }
.s-title { margin: 30px 0 0; font: 800 68px/0.95 var(--display); text-transform: uppercase; letter-spacing: -0.025em; }
.s-sub { margin: 14px 0 0; font-size: 21px; line-height: 1.45; color: var(--ink-2); max-width: 80ch; }
.s-body { flex: 1; min-height: 0; margin-top: 30px; position: relative; }
.s-fit { transform-origin: top left; position: absolute; left: 0; top: 0; }
.s-fit > *:first-child { margin-top: 0 !important; }
.s-fit > *:last-child { margin-bottom: 0 !important; }
.s-foot { display: flex; justify-content: space-between; gap: 24px; padding-top: 18px; font: 500 12px/1.4 var(--display); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
.slide .fig-core { overflow: visible; }
.slide .fig { margin: 0 0 20px; }
.slide .doc { max-width: none; }
.slide .lit { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.slide .prod.wide .shot-area { padding-block: 40px; }
.slide .drop-grid { gap: 18px; }
.slide .shot-area { min-height: 0; }
.slide .phone { max-width: 250px; }
/* cover */
.cover { padding: 0; background: radial-gradient(ellipse 60% 60% at 68% 42%, #222 0%, #0a0a0a 70%); }
.cv-word { position: absolute; left: 50%; top: 44%; transform: translate(-50%, -50%); width: 118%; color: #fff; opacity: .04; }
.cv-mark { position: absolute; right: 110px; top: 110px; width: 640px; height: auto; }
.cv-top { position: absolute; left: 96px; right: 96px; top: 64px; display: flex; justify-content: space-between; align-items: center; }
.lockup { display: flex; align-items: center; gap: 16px; color: var(--ink); }
.lockup .logo { height: 30px; width: auto; }
.lockup .x { font: 400 16px/1 var(--display); color: var(--muted); }
.lockup .bp { font: 900 26px/1 var(--display); font-stretch: 112%; letter-spacing: .02em; }
.cv-copy { position: absolute; left: 96px; bottom: 90px; width: 980px; }
.cv-copy h1 { margin: 18px 0 0; font: 800 128px/0.9 var(--display); text-transform: uppercase; letter-spacing: -0.03em; }
.cv-copy p { margin: 30px 0 0; max-width: 46ch; font-size: 22px; line-height: 1.55; color: var(--ink-2); }
.cv-side { position: absolute; right: 96px; bottom: 96px; text-align: right; display: grid; gap: 8px; }
.cv-side b { font: 600 16px/1.3 var(--display); letter-spacing: .1em; text-transform: uppercase; }
.cover .lbl, .brandslide .lbl { font-size: 14px; }
/* brand */
.brandslide { justify-content: center; align-items: center; text-align: center; }
.brandslide .sc { width: 900px; color: #f4f4f4; }
.brandslide p { margin: 48px auto 0; max-width: 54ch; font-size: 24px; line-height: 1.55; color: var(--ink-2); }
.brandslide .lbl { margin-top: 24px; }
.brandslide .pg, .divider .pg { position: absolute; right: 96px; top: 64px; }
/* agenda */
.agenda { flex: 1; margin-top: 36px; display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(2, 1fr); gap: 16px; }
.ag { position: relative; background: var(--bg-2); padding: 22px; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; }
.ag .num { font: 600 13px/1 var(--display); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.ag .r3d { position: absolute; inset: 14% 10% 34% 10%; display: grid; place-items: center; }
.ag .r3d img { max-width: 80%; max-height: 100%; filter: drop-shadow(0 26px 22px rgba(0,0,0,.16)); }
.ag h3 { margin: 0; font: 800 30px/1 var(--display); text-transform: uppercase; position: relative; }
.ag .ct { margin-top: 10px; font: 500 13px/1 var(--display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
/* divider */
.divider { background: var(--bg-2); flex-direction: row; align-items: center; gap: 60px; }
.dv-copy { flex: 1; }
.dv-copy .lbl { font-size: 15px; }
.dv-copy h2 { margin: 22px 0 0; font: 800 120px/0.9 var(--display); text-transform: uppercase; letter-spacing: -0.03em; }
.dv-copy p { margin: 28px 0 0; font-size: 24px; line-height: 1.5; color: var(--ink-2); max-width: 40ch; }
.dv-copy .stage-chips { margin-top: 30px; }
.dv-copy .stage-chips span { font-size: 13px; padding: 11px 14px; background: var(--bg); }
.dv-mark { width: 660px; height: auto; filter: drop-shadow(0 40px 34px rgba(0,0,0,.18)); }
/* end */
.endslide { justify-content: center; }
.endslide h2 { margin: 40px 0 0; font: 800 180px/0.9 var(--display); text-transform: uppercase; letter-spacing: -0.03em; }
.endslide p { margin: 24px 0 0; font-size: 22px; color: var(--ink-2); }
.endslide .ew { position: absolute; left: 96px; right: 96px; bottom: 56px; color: #f4f4f4; opacity: .1; }
.endslide .lockup { color: #f4f4f4; }
@media print { html, body { background: none; } .deck { padding: 0; gap: 0; display: block; } .slide { break-after: page; break-inside: avoid; } .slide * { break-inside: auto !important; break-before: auto !important; break-after: auto !important; } }
'''

FIT_JS = r'''
<script>
(function () {
  function fit() {
    document.querySelectorAll('.s-body').forEach(function (body) {
      var el = body.querySelector('.s-fit');
      el.style.transform = 'none';
      var bw = body.clientWidth, bh = body.clientHeight;
      var base = parseInt(el.dataset.w || el.style.width, 10);
      el.dataset.w = base;
      var best = null;
      [1.25, 1.15, 1.05, 1, 0.92, 0.84, 0.76, 0.68, 0.6].forEach(function (f) {
        var w = Math.round(base * f);
        el.style.width = w + 'px';
        var rw = Math.max(el.offsetWidth, el.scrollWidth), rh = el.scrollHeight;
        var s = Math.min(bw / rw, bh / rh, 1.9);
        if (!best || s > best.s + 0.01) best = { w: w, s: s, rw: rw, rh: rh };
      });
      el.style.width = best.w + 'px';
      el.style.transform = 'scale(' + best.s + ')';
      el.style.top = Math.max(0, (bh - best.rh * best.s) / 2) + 'px';
      el.style.left = Math.max(0, (bw - best.rw * best.s) / 2) + 'px';
    });
  }
  function scaleDeck() {
    if (document.documentElement.classList.contains('pdf')) return;
    var k = Math.min(1, (window.innerWidth - 32) / 1920);
    document.querySelectorAll('.slide').forEach(function (s) {
      s.style.zoom = k;
    });
  }
  window.fitSlides = fit;
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(function () { fit(); scaleDeck(); });
  addEventListener('resize', scaleDeck);
  addEventListener('keydown', function (e) {
    var slides = [].slice.call(document.querySelectorAll('.slide'));
    var cur = slides.findIndex(function (s) { return s.getBoundingClientRect().top > -10; });
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { e.preventDefault(); (slides[Math.min(slides.length - 1, cur + 1)] || slides[0]).scrollIntoView(); }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); (slides[Math.max(0, cur - 1)] || slides[0]).scrollIntoView(); }
  });
})();
</script>'''


def build(local_deps=None):
    figs = bb.load_figures()
    logos = bb.load_logos()
    template = (BOOK / "template.html").read_text()
    css = re.search(r"<style>(.*?)</style>", template, flags=re.S).group(1)
    symbols = re.search(r'<svg width="0" height="0".*?</svg>', template, flags=re.S).group(0)
    S = slides(figs, logos)
    body = render(S, logos)
    head = '<title>BLUPRINT Deck</title>\n'
    if local_deps:
        head += bb.font_faces(local_deps)
    else:
        head += re.search(r'(<link rel="preconnect".*?display=swap">)', template, flags=re.S).group(1)
    page = f'{head}\n<style>{css}{DECK_CSS}</style>\n{symbols}\n<main class="deck">\n{body}\n</main>\n{FIT_JS}\n'
    for k, v in logos.items():
        page = page.replace(k, v)
    assert "{{" not in page, re.findall(r"\{\{[\w:-]+\}\}", page)
    return page, len(S)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--local":
        out, (page, n) = pathlib.Path(sys.argv[3]), build(sys.argv[2])
    else:
        out, (page, n) = OUT, build()
    out.write_text(page)
    print(out, len(page), "slides:", n)
