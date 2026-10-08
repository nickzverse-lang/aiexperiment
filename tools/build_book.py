"""Build docs/bluprint-project-book.html from docs/0*.md plus the drawn figures in tools/book/.

Run: python3 tools/build_book.py   (needs: pip install markdown)
"""
import html
import pathlib
import re

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "tools" / "book"
OUT = ROOT / "docs" / "bluprint-project-book.html"

CHAPTERS = [
    ("Brief", "The brief", "What we're building, who it's for, and the 20-week plan to get there.",
     ["Project proposal", "Project timeline"]),
    ("Research", "Secondary research", "The brand, the market, the platforms, the existing tools, and twelve sources that shape the design.",
     ["Domain study", "Tool review", "Literature review"]),
    ("Systems", "Systems and problems", "Who is involved, how content moves today, and exactly where it breaks.",
     ["Stakeholders map", "System mapping", "Problem mapping", "Target users"]),
    ("Fieldwork", "Primary research", "How we learn from the team and the audience, the instruments, and what we expect to find.",
     ["Research plan", "Segmentation", "Questionnaires", "Interviews", "Focus group", "Ethnography", "Report", "Inferences"]),
    ("Synthesis", "People and problem", "Who we design for, how their week feels today, and the problem in one sentence.",
     ["Personas", "Empathy maps", "Journey map", "Problem statement", "Design goals"]),
    ("Ideation", "Ideas to direction", "From forty-plus raw ideas to three concepts, then one direction with a reason.",
     ["Brainstorming", "Brainwriting", "SCAMPER", "Space saturation", "Bullseye", "Priority matrix", "3 concepts", "Final selection"]),
    ("Flows", "Scenarios and flows", "How each person moves through BLUPRINT, step by step.",
     ["User scenarios", "Storyboards", "User flows", "Task flows", "Task analysis", "Feature mapping"]),
    ("IA", "Information architecture", "How the product is organised, named and navigated, and the final proposal.",
     ["Content strategy", "Organisation", "Sitemap", "Navigation", "Labeling", "Proposed solution"]),
]

# mermaid block order across all docs -> figure key ("" drops the block; a section override draws it instead)
MERMAID = ["timeline", "", "asis", "tobe", "", "", "", "userflow", "tf-brief", "tf-promote", "tf-approve", "sitemap", "loop"]

# heading text prefix -> (mode, figure key, end heading prefix or None)
# replace: keep the heading, swap its body for the figure until the next heading of the same or higher level (or `end`)
# prepend: keep the heading and body, put the figure right after the heading
SECTIONS = {
    "5.1": ("replace", "onion", None),
    "5.2": ("replace", "power", None),
    "7.1": ("replace", "tree", None),
    "14. Personas": ("replace", "personas", None),
    "15. Empathy Maps": ("replace", "empathy", None),
    "16. User Journey Map": ("replace", "journey", None),
    "20.1": ("replace", "bullseye", None),
    "20.2": ("replace", "matrix", None),
    "21. Three Concepts": ("replace", "concepts", "21.1"),
    "21.1": ("prepend", "scores", None),
    "22. Final Concept": ("prepend", "venn", None),
    "31. Navigation": ("prepend", "navmock", None),
}


def load_figures():
    text = (BOOK / "graphics.html").read_text()
    parts = re.split(r"<!-- @@([\w-]+) -->\n", text)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def clean(md):
    md = md.replace("✅", "Yes").replace("❌", "No")
    md = re.sub(r"[\U0001F300-\U0001FAFF☀-➿️]\s?", "", md)
    md = md.replace(" — ", ": ").replace(" · ", ", ")
    return md


def apply_sections(h, figs):
    heads = [(m.start(), m.end(), int(m.group(1)), re.sub("<[^>]+>", "", m.group(2)).strip())
             for m in re.finditer(r"<h([23])>(.*?)</h\1>", h)]
    out, pos = [], 0
    skip_until = None
    for i, (s, e, lvl, text) in enumerate(heads):
        if skip_until is not None and s < skip_until:
            continue
        rule = next((v for k, v in SECTIONS.items() if text.startswith(k)), None)
        if not rule:
            continue
        mode, key, end = rule
        if mode == "prepend":
            out.append(h[pos:e] + figs[key])
            pos = e
            continue
        stop = len(h)
        for s2, _, lvl2, text2 in heads[i + 1:]:
            if (end and text2.startswith(end)) or (not end and lvl2 <= lvl):
                stop = s2
                break
        out.append(h[pos:e] + figs[key])
        pos = skip_until = stop
    out.append(h[pos:])
    return "".join(out)


def main():
    figs = load_figures()
    files = sorted((ROOT / "docs").glob("0*.md"))
    mermaid = iter(MERMAID)
    nav, chapters = [], []
    for i, (f, (short, title, summary, stages)) in enumerate(zip(files, CHAPTERS), 1):
        md = clean(re.sub(r"^# .+\n", "", f.read_text(), count=1))
        h = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
        h = re.sub(r'<pre><code class="language-mermaid">.*?</code></pre>',
                   lambda m: figs.get(next(mermaid), ""), h, flags=re.S)
        h = apply_sections(h, figs)
        h = re.sub(r"<table>", '<div class="table-wrap"><table>', h).replace("</table>", "</table></div>")
        h = h.replace("<hr />", "")
        h = h.replace("<td>Yes", '<td><span class="ok">Yes</span>').replace("<td>No</td>", '<td><span class="no">No</span></td>')
        sid = f"part{i}"
        nav.append(f'      <a href="#{sid}">{short}</a>')
        chips = "".join(f"<span>{html.escape(s)}</span>" for s in stages)
        chapters.append(
            f'<section class="band chapter" id="{sid}"><div class="wrap">'
            f'<div class="band-head"><div><p class="eyebrow">Part {i} of 8</p><h2>{html.escape(title)}</h2></div>'
            f'<div><p>{html.escape(summary)}</p><div class="stage-chips">{chips}</div></div></div>'
            f'<div class="doc">{h}</div></div></section>')
    page = (BOOK / "template.html").read_text()
    page = page.replace("{{NAV}}", "\n".join(nav)).replace("{{CHAPTERS}}", "\n".join(chapters))
    OUT.write_text(page)
    print(OUT, len(page))


if __name__ == "__main__":
    main()
