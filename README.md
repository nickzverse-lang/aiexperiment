# BLUPRINT — UI/UX Graduation Project (BLUORNG)

**A content intelligence & ideation platform that helps BLUORNG decide what to make for Instagram (organic) and Meta Ads (paid).**

## Documents (Project Proposal → Labeling & Proposed Solution)

| Part | Stages covered |
|---|---|
| [01 — Proposal & Timeline](docs/01-proposal-and-timeline.md) | Project Proposal · Project Timeline |
| [02 — Domain Study & Literature](docs/02-domain-study-and-literature.md) | Domain Study · Competitive/tool analysis · Literature Review |
| [03 — System & Problem Mapping](docs/03-system-and-problem-mapping.md) | Stakeholders Map · System Mapping · Problems Mapping · Problem Area & Target Users |
| [04 — Primary Research](docs/04-primary-research.md) | Research Plan · User Base & Segmentation · Questionnaires · Interviews · Focus Group · Ethnography · Pilot Test · Research Report · Inferences · Redefined Brief · Scope · Environment & Context |
| [05 — Personas, Journey & Goals](docs/05-personas-journey-goals.md) | Personas · Empathy Maps · User Journey Map · Problem Statement · Design Goals |
| [06 — Ideation & Concepts](docs/06-ideation-and-concepts.md) | Brainstorming · Brainwriting · SCAMPER · Space Saturation · Bullseye · Priority Matrix · 3 Concepts · Final Selection |
| [07 — Scenarios, Flows & Tasks](docs/07-scenarios-flows-tasks.md) | User Scenarios · Storyboarding · User Flows · Task Flows · Task Analysis · Feature Mapping |
| [08 — Information Architecture](docs/08-information-architecture.md) | Content Strategy · Organisation · Sitemap · Navigation · Labeling · Proposed Solution |

## BLUPRINT dashboard (final solution)
A content audit and planning dashboard for @bluorng: snapshot, what's working, hashtags, posting pattern, audience sentiment, 10 content ideas and a 30-day calendar, in one self-contained HTML file (light BLUORNG store style, fonts embedded).

- [`docs/bluprint/bluorng-dashboard-demo.html`](docs/bluprint/bluorng-dashboard-demo.html): the dashboard running on **demo data** (made up, labelled on the page). Written audit: [`docs/bluprint/bluorng-dashboard-demo.md`](docs/bluprint/bluorng-dashboard-demo.md).
- Real run, steps 1 and 2 (Apify actor `apify/instagram-scraper`, no login needed):
  - With API access: `APIFY_TOKEN=... python3 tools/bluprint/fetch_apify.py bluorng 150 data/bluorng_posts.json`
  - Or in the Apify Console: run *Instagram Scraper* with the input from `python3 tools/bluprint/fetch_apify.py --print-input bluorng`, then export the dataset as JSON to `data/bluorng_posts.json`.
- Steps 3 to 10: `python3 tools/bluprint/dashboard.py data/bluorng_posts.json --handle bluorng --limit 150` writes `docs/bluprint/bluorng-dashboard.html` and the `.md` audit.
- Code: `tools/bluprint/analyze.py` (all analysis), `tools/bluprint/dashboard.py` (HTML), `tools/bluprint/demo_data.py` (demo set).

## Case study (A4, college grid)
- [`docs/bluorng-casestudy.pdf`](docs/bluorng-casestudy.pdf): 100-page UX case study, A4 landscape, covering every stage from the project proposal to usability evaluation and the test report, ending in the BLUPRINT dashboard. All content sits inside the grid's content box (left margin 33.867 mm, the other margins 23.989 mm).
- [`docs/bluorng-casestudy.html`](docs/bluorng-casestudy.html): the same pages in a browser.
- [`docs/bluorng-casestudy-figma.html`](docs/bluorng-casestudy-figma.html): static, script-free version for Figma. Open it in Chrome and capture it with the html.to.design extension. Rebuild: `node tools/bake_figma.js <url of local build> docs/bluorng-casestudy-figma.html 297mm 210mm`.
- [`docs/research/survey_responses_sample.csv`](docs/research/survey_responses_sample.csv): the 80 sample survey responses behind the charts.
- Content: `tools/cs/pages.py` (months 1–3) and `tools/cs/pages_design.py` (month 4: flows to test report). Dashboard screenshots: `node tools/cs/shoot_dashboard.js docs/bluprint/bluorng-dashboard-demo.html <v1-dark.html> tools/cs/shots`. Sample survey and interviews: `tools/cs/data.py`. Renderer: `tools/build_casestudy.py`.
- PDF: `python3 tools/build_casestudy.py --local <deps> <out>.html`, serve `/` over http, then `node tools/make_pdf.js <url> docs/bluorng-casestudy.pdf 297mm 210mm`.

## Presentation
- [`docs/bluprint-deck.pdf`](docs/bluprint-deck.pdf): the 95-slide 16:9 presentation, Proposal to Proposed Solution.
- [`docs/bluprint-deck.html`](docs/bluprint-deck.html): the same deck in a browser; use the arrow keys to move between slides.
- Rebuild: `python3 tools/build_deck.py` (slide list lives in that file). PDF: `python3 tools/build_deck.py --local <deps> <out>.html`, wrap it in a document, serve over http, then `node tools/make_pdf.js <url> docs/bluprint-deck.pdf 1920 1080`.

- [`docs/bluprint-deck-figma.html`](docs/bluprint-deck-figma.html): static, script-free version for Figma. Open it in Chrome and capture it with the html.to.design extension to get an `.h2d` file. Rebuilt with `tools/bake_figma.js`.

## Project book
- [`docs/bluprint-project-book.html`](docs/bluprint-project-book.html): all 8 parts as one page in BLUORNG's monochrome store style, with the BG mark in 3D, product screens and drawn figures.
- [`docs/bluprint-project-book.pdf`](docs/bluprint-project-book.pdf): the same book as a 40-page PDF.
- Rebuild the page after editing the Markdown: `pip install markdown && python3 tools/build_book.py`.
- Rebuild the PDF: install `three@0.160.0 @fontsource-variable/archivo @fontsource/geist-sans @fontsource/geist-mono` into a folder, run `python3 tools/build_book.py --local <folder> <out>.html`, wrap it in a document, serve `/` over http and run `node tools/make_pdf.js <url> docs/bluprint-project-book.pdf` (needs Playwright).
- Layout: `tools/book/template.html`. Figures: `tools/book/graphics.html`. Traced logos: `tools/book/brand/` (from `tools/trace_logos.py`). 3D renders for the chapter tiles: `tools/book/renders/`.

## Tools
- [`research/chart-builder.html`](research/chart-builder.html): open it in a browser and paste your Google Forms CSV export to get a bar chart per question (for the research report).

## Notes
- Diagrams use Mermaid and render on GitHub.
- Primary research sections contain **instruments and hypotheses with empty slots**. Fill them with your real survey, interview and shadowing data.
- Use internal BLUORNG data only with your industry mentor's approval.
