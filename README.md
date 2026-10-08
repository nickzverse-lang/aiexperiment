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
