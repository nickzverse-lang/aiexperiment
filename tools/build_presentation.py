"""Build the 16:9 final jury presentation from the case study pages, regrouped into the five parts the jury asked for.

Run:  python3 tools/build_presentation.py                        -> docs/bluorng-jury-presentation.html
      python3 tools/build_presentation.py --local DEPS OUT.html  -> offline copy for PDF and Figma:
      node tools/make_pdf.js <file url> docs/bluorng-jury-presentation.pdf 1280 720
"""
import copy
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "cs"), str(HERE)]
import build_book as bb  # noqa: E402
import build_casestudy as cs  # noqa: E402
from pages import pages  # noqa: E402

OUT = bb.ROOT / "docs" / "bluorng-jury-presentation.html"

# (part number, title, intro, topic chips, mark render, [page numbers in the full case study, or "conclusion"])
PARTS = [
    ("01", "Domain and problem", "The brand, the content-creation domain, the problem I saw from inside the team, and what existing knowledge says.",
     ["Domain", "Initial problem statement", "Information gathering"], 1,
     [7, 9, 10, 17, 18, 11, 12, 13, 15]),
    ("02", "Research and users", "How the problem was tested with BLUORNG's audience and team, what we learned, and who we design for.",
     ["Research methods", "Research insights", "User segments and personas", "User journeys, user flows, task flows"], 2,
     [22, 30, 31, 27, 28, 37, 38, 39, 23, 41, 42, 43, 44, 45, 60, 62]),
    ("03", "Concepts and first prototype", "From needs and features to ideas, the chosen direction, the experience narrative, and the first test with users.",
     ["Need and feature mapping", "Concept sketches and ideation", "Experience narrative", "Initial prototyping and testing"], 4,
     [46, 64, 48, 50, 51, 53, 54, 55, 57, 63, 70, 71, 75, 92, 94, 95]),
    ("04", "Final solution and testing", "Validating the direction and building BLUPRINT: the final UI, design system and working prototype, tested again with users.",
     ["Validation and solution building", "Final UI and digital prototype", "Final testing and insights"], 6,
     [67, 74, 77, 78, 81, 82, 86, 89, 90, 91, 96, 97, 98]),
    ("05", "Conclusion", "What BLUPRINT achieves, what we learned, and where it goes next.",
     ["Conclusion", "Future scope"], 8,
     [99, "conclusion"]),
]


def conclusion():
    def T(k, h, p, dk=False):
        return f'<div class="t{" dk" if dk else ""}"><span class="k">{k}</span><h5>{h}</h5><p>{p}</p></div>'
    body = ('<div class="grid3" style="align-items:stretch">'
            '<div class="t dk"><span class="k">Conclusion</span><h5>From instinct to evidence</h5><ul>'
            '<li>BLUORNG decided what to make by instinct; results sat in separate tools and never reached the next plan.</li>'
            '<li>BLUPRINT turns the latest 150 posts into what works, what to avoid, 10 ideas and a 30-day calendar.</li>'
            '<li>Built in BLUORNG\'s own visual language, so the team and founders trust it and share it.</li>'
            '<li>Usability: task success 72% → 97%, SUS 64 → 82 across two rounds (sample study).</li></ul></div>'
            '<div class="t"><span class="k">What I learned</span><h5>Three lessons</h5><ul>'
            '<li><b>Brand fit is a usability issue.</b> The first, generic version was understood but not trusted.</li>'
            '<li><b>Every idea needs its reason.</b> People chose faster when the data behind an idea was visible.</li>'
            '<li><b>Test the real build.</b> A working prototype gave findings about the product, not the mock-up.</li></ul></div>'
            '<div class="t"><span class="k">Limitations</span><h5>What this does not cover yet</h5><ul>'
            '<li>Survey, interviews and usability numbers are a sample study; the dashboard runs on demo data.</li>'
            '<li>Public data only: no saves, shares, reach or ad spend.</li>'
            '<li>Topics and hooks are found with keyword rules, not yet with AI.</li></ul></div></div>'
            '<p class="chart-t">Future scope</p><div class="rail" style="min-width:0">' +
            "".join(f'<div class="node"><div class="card{" endc" if i == 4 else ""}"><small>{k}</small>{t}</div></div>' for i, (k, t) in enumerate([
                ("NEXT", "Run the real Apify scrape of @bluorng and re-test with real data"),
                ("V2 · G2 G5", "Meta ads results and the Meta Ad Library next to organic data"),
                ("V2 · G3 G4", "Claude AI write-ups per idea and a shoot planner with shot lists"),
                ("V3", "Monthly auto-refresh, Slack or WhatsApp digest, approvals for founders"),
                ("LATER", "Open it to other drop-led streetwear brands")])) + "</div>")
    return dict(kind="content", phase="", stage="Conclusion and future scope", title="Conclusion and future scope",
                lead="Where the project landed, and where BLUPRINT goes next.", body=body,
                take="BLUPRINT gives BLUORNG's team a clear answer to one question: what should we make next, and why?", source="", w=1080)


def slides():
    P = pages()
    for i, p in enumerate(P):
        if p["kind"] == "storyboard":
            P[i] = cs.storyboard(p["n"])
    S = [copy.deepcopy(P[0]), copy.deepcopy(P[1])]   # cover, contents
    for n, title, text, chips, mark, nums in PARTS:
        S.append(dict(kind="divider", n=n, title=title, text=text, stages=chips, mark=mark, label=f"Part {int(n)}"))
        for x in nums:
            p = conclusion() if x == "conclusion" else copy.deepcopy(P[x - 1])
            p["phase"] = f"Part {int(n)} · {title}"
            S.append(p)
    S.append(copy.deepcopy(P[-1]))                   # thank you
    return S


DECK_CSS = r'''
html.deck .slide { width: 1280px; height: 720px; }
html.deck .slide > .cb { left: 64px; top: 44px; width: 1152px; height: 632px; }
html.deck .ttl { font-size: 36px; margin-top: 14px; }
html.deck .lead { font-size: 15px; margin-top: 8px; }
html.deck .hd { font-size: 10px; } html.deck .hd .logo { height: 13px; } html.deck .hd b { font-size: 10.5px; }
html.deck .take { font-size: 14px; padding: 10px 14px; } html.deck .take small { font-size: 9px; }
html.deck .src { font-size: 9px; }
html.deck .dd { display: none; }
html.deck .toc { grid-template-columns: repeat(5, minmax(0, 1fr)) !important; grid-template-rows: auto !important; }
html.deck .toc li { font-size: 11.5px !important; } html.deck .toc-h span { font-size: 15px; }
html.deck .cv-copy h1 { font-size: 76px; } html.deck .cv-copy p { font-size: 15px; } html.deck .cv-copy { bottom: 110px; }
html.deck .cv-mark { width: 40%; top: 40px; }
html.deck .dv-copy h2 { font-size: 72px; } html.deck .dv-n { font-size: 120px; } html.deck .dv-copy p { font-size: 17px; max-width: 46ch; }
html.deck .dv-copy .chips span { font-size: 11.5px; padding: 9px 12px; } html.deck .dv-mark { width: 34%; }
html.deck .end-copy h2 { font-size: 96px; } html.deck .end-copy p { font-size: 16px; }
@page { size: 1280px 720px; margin: 0; }
'''


def build(local_deps=None):
    logos = bb.load_logos()
    template = (bb.BOOK / "template.html").read_text()
    css = re.search(r"<style>(.*?)</style>", template, flags=re.S).group(1)
    symbols = re.search(r'<svg width="0" height="0".*?</svg>', template, flags=re.S).group(0)
    cs.COVER_LABEL[0] = "Final jury presentation · design, prototype and testing"
    S = slides()
    body = cs.render(S, logos)
    body = body.replace('<span class="lbl">Phase ', '<span class="lbl">Part ')
    fit = cs.FIT_JS.replace("1.15);", "1.35);").replace("/ 1123)", "/ 1280)")
    head = '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<title>BLUPRINT · Final jury presentation</title>\n'
    head += bb.font_faces(local_deps) if local_deps else re.search(r'(<link rel="preconnect".*?display=swap">)', template, flags=re.S).group(1)
    keys = r'''<script>addEventListener('keydown', function (e) {
  var s = [].slice.call(document.querySelectorAll('.slide')), c = s.findIndex(function (x) { return x.getBoundingClientRect().top > -10; });
  if (['ArrowRight', 'PageDown', ' '].indexOf(e.key) > -1) { e.preventDefault(); (s[Math.min(s.length - 1, c + 1)] || s[0]).scrollIntoView(); }
  if (['ArrowLeft', 'PageUp'].indexOf(e.key) > -1) { e.preventDefault(); (s[Math.max(0, c - 1)] || s[0]).scrollIntoView(); }
});</script>'''
    page = (f'<!doctype html><html lang="en" class="deck"><head>{head}\n<style>{css}{cs.CSS}{DECK_CSS}</style></head><body>\n{symbols}\n'
            f'<main class="pages">\n{body}\n</main>\n{fit}\n{keys}\n</body></html>\n')
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
