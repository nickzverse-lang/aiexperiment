"""Page content for the BLUORNG UX case study (Project proposal to Storyboarding).

Each page: dict(kind, phase, stage, title, lead, body, take, source, w).
The story stays solution-neutral until the ideation filtration stage, like a real case study.
"""
import html as _h
import re

from charts import donut, grouped, hbars, panel, quote, stacked, stat
import data as D

e = _h.escape


def T(k, h, p, dk=False, cls=""):
    return f'<div class="t{" dk" if dk else ""} {cls}"><span class="k">{k}</span><h5>{h}</h5><p>{p}</p></div>'


def tiles(items, cls=""):
    return f'<div class="tiles {cls}">' + "".join(items) + "</div>"


def callout(label, text, size=None):
    st = f' style="font-size:{size}px"' if size else ""
    return f'<div class="callout"{st}><small>{label}</small>{text}</div>'


def chips(items, filled=()):
    return '<div class="chips">' + "".join(f'<span class="{"f" if i in filled else ""}">{e(i)}</span>' for i in items) + "</div>"


def rail(steps, end_last=True):
    out = []
    for i, (k, t) in enumerate(steps):
        cls = " endc" if end_last and i == len(steps) - 1 else ""
        out.append(f'<div class="node"><div class="card{cls}"><small>{k}</small>{t}</div></div>')
    return '<div class="rail" style="min-width:0">' + "".join(out) + "</div>"


def mx(cols, header, rows, me=None):
    h = "".join(f'<div class="h">{c}</div>' for c in header)
    body = ""
    for r in rows:
        cls = ' class="me"' if me and r[0] == me else ""
        body += "".join(f'<div{cls if i else (" class=me" if cls else " class=nm")}>{c}</div>' for i, c in enumerate(r))
    return f'<div class="mx" style="grid-template-columns:{cols};min-width:0">{h}{body}</div>'


ROWS = D.generate()
S = D.stats(ROWS)


def q(qid):
    return {o: p for o, c, p in S[qid]}


def bars_from(qid, hi=(), sort=True, label_w="minmax(120px,210px)", maxv=100):
    rows = [(o, p) for o, c, p in S[qid]]
    if sort:
        rows.sort(key=lambda r: -r[1])
    return hbars(rows, maxv=maxv, hi=set(hi) if hi else None, label_w=label_w)


def pages():
    P = []

    def page(phase, stage, title, body, lead="", take="", source="", w=900):
        P.append(dict(kind="content", phase=phase, stage=stage, title=title, lead=lead, body=body, take=take, source=source, w=w))

    def divider(n, title, text, stages, mark):
        P.append(dict(kind="divider", n=n, title=title, text=text, stages=stages, mark=mark))

    P.append(dict(kind="cover"))
    P.append(dict(kind="contents"))

    # ------------------------------------------------------------------ 00 OVERVIEW
    divider("00", "Overview", "What this project is about, who it is with, and how the four months were planned.",
            ["Project proposal", "Project timeline"], 1)
    page("Overview", "Project proposal", "Project overview",
         tiles([T("Industry partner", "BLUORNG, New Delhi", "Premium Indian streetwear label, founded 2020. Drop-led, Instagram-first, runs Meta ads for every drop."),
                T("My role", "UX designer, embedded", "I work alongside BLUORNG's content and marketing team, so I could observe the content process first-hand."),
                T("Duration", "4 months", "Research, synthesis, ideation and design, ending in a tested prototype.", True)]) +
         '<div class="grid2">' +
         '<div class="t"><span class="k">Background</span><p>BLUORNG builds hype for every drop through Instagram content and Meta ads. Each drop needs fresh posts, a shoot, ad creatives and ad budget. The team decides what to make mostly on experience and instinct, and results are spread across different tools.</p></div>' +
         '<div class="t"><span class="k">Project aim</span><p>Understand how BLUORNG\'s marketing and content team decides what to create for organic social media and Meta ads, find where time and money are lost, and design a solution that helps the team make better content decisions.</p></div></div>' +
         chips(["Domain study", "Literature review", "Stakeholders", "System mapping", "Problem mapping", "Survey, 80 people", "10 team interviews", "Personas", "Journey map", "Ideation", "Filtration", "Scenarios", "Storyboards"]),
         lead="A UX case study, from understanding the problem to choosing a solution direction.",
         take="The project starts with a question, not a solution: how does BLUORNG decide what content to make?")

    weeks = [("Month 1: Discover", [("Proposal and timeline", 1, 1), ("Domain study", 1, 2), ("Literature review", 2, 3), ("Stakeholders and system mapping", 3, 4), ("Problem identification", 4, 4)]),
             ("Month 2: Research and define", [("Research plan and segmentation", 5, 5), ("Survey, 80 responses", 5, 7), ("10 team interviews", 6, 7), ("Research report", 8, 8), ("Personas, journey, problem statement", 8, 9)]),
             ("Month 3: Ideate", [("Design goals", 9, 9), ("Ideation", 10, 10), ("Filtration and final direction", 11, 11), ("Scenarios and storyboards", 12, 12)]),
             ("Month 4: Design and test", [("Flows, IA, wireframes", 13, 14), ("UI design system and prototype", 14, 15), ("Usability testing and report", 16, 16)])]
    g = '<div class="gantt" style="grid-template-columns:250px repeat(16,minmax(0,1fr));min-width:0"><span></span>' + "".join(f'<span class="wk">W{i}</span>' for i in range(1, 17))
    shade = ["", "p2", "p3", "p4"]
    for mi, (m, rows) in enumerate(weeks):
        g += f'<span class="ph-label">{m}</span>'
        for t, a, b in rows:
            g += f'<span class="tl">{t}</span><span class="bar {shade[mi]}" style="grid-column:{a + 1}/{b + 2}"></span>'
    g += '<span class="ph-label">Reviews</span><span class="tl">Research review</span><span class="ms" style="grid-column:9/10"></span><span class="tl">Concept review</span><span class="ms" style="grid-column:13/14"></span><span class="tl">Final jury</span><span class="ms" style="grid-column:17/18"></span></div>'
    page("Overview", "Project timeline", "Four months, sixteen weeks",
         f'<div class="panel">{g}</div>', lead="Month by month: discover, research and define, ideate, then design and test.",
         take="This document covers months 1 to 3, up to scenarios and storyboards. Month 4 builds and tests the design.", w=920)

    # ------------------------------------------------------------------ 01 DISCOVER
    divider("01", "Discover", "Understanding the brand, the content-creation domain, what others have written, and who is involved.",
            ["Domain study", "Literature review", "Stakeholders map", "System mapping", "Problem identification", "Problem area and users"], 2)
    page("Discover", "Domain study / The brand", "BLUORNG at a glance",
         rail([("2020", "Founded in New Delhi by Siddhant Sabharwal and Mokam Singh. Appointment-only studio."), ("NEXT", "Flagship store in Gurugram."),
               ("2023", "GQ India Streetwear Label of the Year."), ("2024", "Jägermeister collaboration."), ("COLLAB", "Budweiser jersey collection."),
               ("2026", "Larger Mumbai store reopens.")]) +
         tiles([T("Positioning", "Premium streetwear", "Design-led, bold visuals, global aesthetic with local sensibility."),
                T("Business model", "Drop-led", "Limited releases, sell-outs and collaborations create urgency."),
                T("Growth engine", "Instagram first", "Discovery and hype on Instagram, conversion through Meta ads."),
                T("Price band", "Premium", "Tees in the few-thousand-rupee range, outerwear far higher.", True)], "c4"),
         lead="A young, fast-growing label whose growth depends on how good its content is.",
         take="For BLUORNG, content is not marketing on the side. It is how the brand is discovered and sold.",
         source="Indian Retailer, Business News This Week, Fibre2Fashion, Mediainfoline", w=940)

    page("Discover", "Domain study / The brand", "How BLUORNG uses content today",
         '<div class="grid2"><div class="t"><span class="k">Organic Instagram</span><h5>Hype and community</h5><p>Drop teasers, lookbooks and campaign films, behind the scenes, store launches, collabs and culture posts. Builds desire and recall.</p>' +
         chips(["Reels", "Carousels", "Stories", "Collab posts"]) + '</div>'
         '<div class="t dk"><span class="k">Meta ads</span><h5>Conversion and footfall</h5><p>Ads for every drop, retargeting of site visitors, store footfall and evergreen products. Every ad needs creative from a shoot, plus spend.</p>' +
         chips(["Drop ads", "Retargeting", "Store footfall", "Evergreen"]) + '</div></div>' +
         '<p class="chart-t">One drop, as a content cycle</p>' +
         rail([("1", "Collection ready"), ("2", "Content planning meeting"), ("3", "Shoot day"), ("4", "Edits and versions"), ("5", "Posts go live"), ("6", "Meta ads run"), ("7", "Results checked")]),
         lead="Every drop runs the same cycle, and every step costs time or money.",
         take="The shoot day and the Meta ad budget are the two biggest costs in each cycle.")

    page("Discover", "Domain study / Content creation", "The content-creation domain",
         tiles([T("Organic content", "Earned reach", "Free to post, reach decided by the algorithm: watch time, saves and shares. The first 3 to 4 seconds decide if people stay."),
                T("Paid content", "Bought reach", "Meta ads place content in front of chosen audiences. Meta's own guidance says the creative is now the main lever, because targeting is automated."),
                T("Production", "The hidden cost", "Concept, shoot, edit and resize for 9:16, 4:5 and 1:1. A shoot day is planned once and must feed both organic and ads.", True)]) +
         '<div class="grid2">' + panel("Engagement by format, fashion brands", hbars([("Reels", 1.9), ("Carousels", 0.8), ("Single images", 0.8)], maxv=2, unit="%", hi={"Reels"}, label_w="110px"), "Dash Social via NetInfluencer") +
         panel("What makes paid content work", hbars([("Diversified creative, CPA", 32), ("Diversified creative, reach", 9)], maxv=40, unit="%", label_w="190px"), "Best-case improvement vs similar ads. Meta via B&T") + "</div>",
         lead="Two kinds of content, one production pipeline.",
         take="Paid results depend on creative variety, and variety has to be planned before the shoot.",
         source="Dash Social, Meta via B&T, Socialinsider", w=920)

    page("Discover", "Domain study / Market", "A market growing on Instagram",
         '<div class="grid2">' + panel("India streetwear market, USD bn",
                                      '<div class="vb" style="height:150px"><div class="c"><b>23.1</b><i style="height:51%"></i></div><div class="c"><b>~43</b><i class="g" style="height:95%"></i></div></div><div class="vb-l"><span>2025</span><span>2034, projected</span></div>',
                                      "About 7.1% a year. Deep Market Insights estimate") +
         panel("Online fashion in India, USD bn",
               '<div class="vb" style="height:150px"><div class="c"><b>~11</b><i style="height:30%"></i></div><div class="c"><b>35</b><i class="g" style="height:95%"></i></div></div><div class="vb-l"><span>Today</span><span>2028, projected</span></div>',
               "Entrepreneur India") + "</div>" +
         callout("What this means", "More Indian streetwear labels compete for the same Instagram feed, so content quality and ad efficiency decide who wins.") +
         '<p class="chart-t">Premium streetwear peers</p>' + chips(["Jaywalking", "Almost Gods", "Huemn", "Capsul", "Urban Monkey", "Bonkers Corner", "Fear of God Essentials", "Corteiz", "Represent", "Aimé Leon Dore"], filled=("Jaywalking", "Almost Gods", "Huemn", "Capsul", "Urban Monkey", "Bonkers Corner")),
         lead="The space is crowded and growing, and the competition happens in the feed.",
         take="Competitors' content is public in the Meta Ad Library and on Instagram, but studying it is manual today.",
         source="Deep Market Insights, Entrepreneur India, Fibre2Fashion")

    lit = [("1984", "Cialdini, Influence", "Scarcity raises perceived value.", "Drop content works, but loses power if overused."),
           ("1989", "Davis, TAM", "People adopt tools that are useful and easy.", "Any new way of working must save the team time."),
           ("2010", "Kaplan & Haenlein", "Brands must take part in social media, not broadcast.", "Participation beats announcements."),
           ("2012", "Berger & Milkman", "High-arousal emotions drive sharing.", "Emotion matters as much as format."),
           ("2012", "de Vries et al.", "Vivid and interactive posts get different responses.", "Format and interactivity change results."),
           ("2012", "Kim & Ko", "Entertainment and interaction build luxury brand equity.", "Premium brands need more than conversion content."),
           ("2015", "Ashley & Tuten", "Brands use functional, emotional and experiential strategies.", "Ads can be grouped by creative angle."),
           ("2016", "Godey et al.", "Social builds awareness and image, then loyalty.", "Measure recall, not only sales."),
           ("2016", "Lemon & Verhoef", "Experience spans the whole customer journey.", "Content serves discover, desire, buy and share."),
           ("2019", "Amershi et al.", "Guidelines for human-AI interaction: explain, allow correction.", "Any automated help must explain itself."),
           ("2023–25", "Meta, creative is targeting", "Diverse creative improves cost and reach.", "Ad variety is a planning problem.")]
    page("Discover", "Literature review", "What existing knowledge says",
         '<div class="lit" style="grid-template-columns:repeat(4,minmax(0,1fr))">' + "".join(
             f'<div class="t"><span class="k">{y}</span><h5>{e(a)}</h5><p>{e(k)}</p><p><b>So:</b> {e(s)}</p></div>' for y, a, k, s in lit) +
         '<div class="t dk"><span class="k">Gap</span><h5>Not yet studied</h5><p>How a small, drop-led Indian streetwear team decides what to make, day to day.</p></div></div>',
         lead="Twelve sources from marketing, psychology and design research.",
         take="Research explains what makes content work in general. It doesn't tell BLUORNG's team what to make next.", w=1000)

    page("Discover", "Literature review / Existing practice", "How teams decide today",
         mx("minmax(160px,1.3fr) repeat(3,minmax(70px,.7fr)) minmax(170px,1.5fr)",
            ["Practice", "Organic", "Paid", "Says what to make", "Limitation"],
            [["Instagram Insights", '<i class="dt f"></i>', '<i class="dt o"></i>', '<i class="dt o"></i>', "Numbers without meaning"],
             ["Meta Ads Manager", '<i class="dt o"></i>', '<i class="dt f"></i>', '<i class="dt o"></i>', "Shows cost, not why"],
             ["Meta Ad Library", '<i class="dt o"></i>', '<i class="dt f"></i>', '<i class="dt o"></i>', "Competitor ads, studied by hand"],
             ["Scheduling tools", '<i class="dt f"></i>', '<i class="dt h"></i>', '<i class="dt h"></i>', "Plans posts, not ideas"],
             ["Creative analytics tools", '<i class="dt o"></i>', '<i class="dt f"></i>', '<i class="dt h"></i>', "Paid only, costly, generic"],
             ["Agencies", '<i class="dt h"></i>', '<i class="dt f"></i>', '<i class="dt h"></i>', "Expensive, slow, less brand feel"],
             ["Generic AI chat", '<i class="dt f"></i>', '<i class="dt f"></i>', '<i class="dt h"></i>', "No brand data or memory"],
             ["WhatsApp, Sheets, instinct", '<i class="dt h"></i>', '<i class="dt h"></i>', '<i class="dt o"></i>', "Where decisions happen now"]]) +
         '<div class="legend-row"><span><i class="dt f" style="width:12px;height:12px;border-radius:50%"></i>Yes</span><span><i class="dt h" style="width:12px;height:12px;border-radius:50%"></i>Partly</span><span><i class="dt o" style="width:12px;height:12px;border-radius:50%"></i>No</span></div>',
         lead="Tools and practices the team, or brands like it, use now.",
         take="Each tool covers one piece. None connects results, competitors and planning for a brand like BLUORNG.", w=920)

    page("Discover", "Stakeholders map", "Who is involved",
         '<div class="split"><svg class="svg-fluid" viewBox="0 0 520 520"><circle cx="260" cy="260" r="250" style="fill:color-mix(in srgb,var(--ink) 5%,transparent)" class="sv-line"/>'
         '<circle cx="260" cy="260" r="190" style="fill:color-mix(in srgb,var(--ink) 10%,transparent)" class="sv-line"/><circle cx="260" cy="260" r="130" style="fill:color-mix(in srgb,var(--ink) 18%,transparent)" class="sv-line"/>'
         '<circle cx="260" cy="260" r="72" class="sv-acc"/><text x="260" y="254" text-anchor="middle" font-size="15" font-weight="700" fill="#fff">Marketing and</text><text x="260" y="274" text-anchor="middle" font-size="15" font-weight="700" fill="#fff">content team</text>'
         '<text x="260" y="160" text-anchor="middle" font-size="11" class="sv-ink sv-mono">FOUNDERS, E-COM, RETAIL</text><text x="260" y="100" text-anchor="middle" font-size="11" class="sv-ink2 sv-mono">CREATORS, AGENCIES, CREW</text><text x="260" y="40" text-anchor="middle" font-size="11" class="sv-mute sv-mono">AUDIENCE, META, COMPETITORS</text></svg>'
         '<div class="legend-list">'
         '<div class="lg-row"><i style="background:var(--ink)"></i><div><b>Core: decide and make content</b><span>Marketing lead, performance marketer (Meta ads), social media manager, content strategist, photographer, video editor, graphic designer.</span></div></div>'
         '<div class="lg-row"><i style="background:#9a9a9a"></i><div><b>Internal: approve or are affected</b><span>Co-founders, e-commerce manager, retail store managers, design and product team.</span></div></div>'
         '<div class="lg-row"><i style="background:#cfcfcf"></i><div><b>External partners</b><span>Creators and models, agencies and freelancers, production crew, collab brands.</span></div></div>'
         '<div class="lg-row"><i style="background:#ececec;border:1px solid var(--line)"></i><div><b>Wider ecosystem</b><span>The audience, Instagram and Meta (algorithm, ad policies, Ad Library), competitor brands.</span></div></div></div></div>',
         lead="Mapped from closest to the content decision to furthest away.",
         take="The marketing and content team sits at the centre: they decide, make and pay for content.", w=960)

    page("Discover", "Stakeholders map", "Power and interest",
         '<svg class="svg-fluid" viewBox="0 0 640 400"><rect x="320" y="20" width="260" height="170" style="fill:color-mix(in srgb,var(--ink) 8%,transparent)"/><rect x="60" y="20" width="520" height="340" class="sv-line"/>'
         '<line x1="320" y1="20" x2="320" y2="360" class="sv-line" stroke-dasharray="4 4"/><line x1="60" y1="190" x2="580" y2="190" class="sv-line" stroke-dasharray="4 4"/>'
         '<text x="72" y="40" font-size="11" class="sv-mute sv-mono">KEEP SATISFIED</text><text x="568" y="40" font-size="11" text-anchor="end" class="sv-ink sv-mono">MANAGE CLOSELY</text>'
         '<text x="72" y="350" font-size="11" class="sv-mute sv-mono">MONITOR</text><text x="568" y="350" font-size="11" text-anchor="end" class="sv-mute sv-mono">KEEP INFORMED, INVOLVE</text>'
         '<text x="320" y="390" text-anchor="middle" font-size="12" class="sv-mute">Interest in content decisions →</text><text transform="translate(30 190) rotate(-90)" text-anchor="middle" font-size="12" class="sv-mute">Power over content →</text>'
         '<g font-size="12.5"><circle cx="520" cy="66" r="7" class="sv-ink"/><text x="508" y="70" text-anchor="end" font-weight="600" class="sv-ink">Co-founders</text>'
         '<circle cx="470" cy="92" r="7" class="sv-ink"/><text x="458" y="96" text-anchor="end" font-weight="600" class="sv-ink">Marketing lead</text>'
         '<circle cx="430" cy="140" r="7" class="sv-ink"/><text x="418" y="144" text-anchor="end" font-weight="600" class="sv-ink">Performance marketer</text>'
         '<circle cx="190" cy="70" r="6" class="sv-mute"/><text x="200" y="74" class="sv-ink2">Meta platform</text>'
         '<circle cx="530" cy="230" r="7" class="sv-ink"/><text x="518" y="234" text-anchor="end" font-weight="600" class="sv-ink">Social media manager</text>'
         '<circle cx="480" cy="270" r="7" class="sv-ink"/><text x="468" y="274" text-anchor="end" font-weight="600" class="sv-ink">Photographer, editor, designer</text>'
         '<circle cx="400" cy="320" r="6" class="sv-mute"/><text x="410" y="324" class="sv-ink2">Audience</text>'
         '<circle cx="250" cy="250" r="6" class="sv-mute"/><text x="260" y="254" class="sv-ink2">E-com, store managers</text>'
         '<circle cx="130" cy="130" r="6" class="sv-mute"/><text x="140" y="134" class="sv-ink2">Agencies, creators</text>'
         '<circle cx="140" cy="300" r="6" class="sv-mute"/><text x="150" y="304" class="sv-ink2">Competitors</text></g></svg>',
         lead="Who can shape the outcome, and who cares most about it.",
         take="Founders and the marketing lead approve. The content makers feel the problem daily. Both must be part of the research.", w=820)

    page("Discover", "System mapping", "How content moves today",
         '<div class="flow5" style="min-width:0">' + "".join(
             f'<div class="stage"><div class="st"><b>{i + 1}</b>{s}</div><div class="box"><ul>{"".join(f"<li>{x}</li>" for x in items)}</ul></div></div>'
             for i, (s, items) in enumerate([("Inputs", ["Drop calendar", "Trends, audio", "Competitor pages", "Founder taste"]),
                                             ("Decide", ["Planning meeting", "Moodboards", "WhatsApp threads", "Founder approval"]),
                                             ("Produce", ["Voice-note brief", "One shoot day", "Edits, resizing"]),
                                             ("Publish", ["Instagram posts", "Meta ads from leftover cuts"]),
                                             ("Measure", ["IG Insights", "Ads Manager", "Shopify sales"])])) + "</div>"
         '<div class="broken" style="min-width:0"><svg class="i"><use href="#i-break"/></svg><span><b>The loop is broken.</b> Results stay in Insights and Ads Manager. They rarely reach the next planning meeting, and competitor learning is never saved.</span></div>',
         lead="Mapped from observation inside the team: inputs, decisions, production, publishing and measurement.",
         take="The system has no feedback loop. What is learned after a drop does not shape the next one.", w=940)

    page("Discover", "System mapping", "Where the money and effort go",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.2fr) minmax(0,1fr)">' +
         '<div class="panel"><p class="chart-t">Effort and spend in one drop cycle</p>' +
         rail([("SPEND", "Shoot day: crew, models, location"), ("SPEND", "Edits in many ratios"), ("SPEND", "Meta ad budget"), ("RESULT", "Sales, reach, saves")], end_last=True) +
         '<p class="chart-s" style="margin-top:16px">Most spend happens before anyone knows which content will work</p></div>' +
         tiles([T("Leak 1", "Under-used shoots", "Shoots are planned around the lookbook. Few cuts suit ads.", True),
                T("Leak 2", "Habit-led ad spend", "Budget goes to familiar ad formats, not proven ones."),
                T("Leak 3", "Late re-work", "Missing formats and late feedback cause re-edits and re-shoots."),
                T("Leak 4", "Lost learning", "Winning posts and ads aren't recorded or repeated.")], "c2") + "</div>",
         lead="Following the money shows the problem is bigger than reporting.",
         take="The costliest decisions, what to shoot and which ads to run, are made with the least information.", w=920)

    page("Discover", "Problem identification", "How I spotted the problem",
         '<div class="grid2"><div class="t dk"><span class="k">My vantage point</span><h5>Working inside the team</h5><p>As part of BLUORNG\'s content process, I sat in planning meetings, shoots and edit reviews, and saw how ad and post decisions get made.</p></div>'
         '<div class="t"><span class="k">What I kept seeing</span><ul><li>Planning starts from moodboards and instinct, not results.</li><li>Ads are cut from whatever the lookbook shoot produced.</li><li>The marketing team can see an ad is failing, but not why.</li><li>Competitor ads are checked by hand, then forgotten.</li><li>Money spent on making and running ads is hard to justify.</li></ul></div></div>' +
         callout("Initial problem", "BLUORNG's marketing team spends heavily on making and running Meta ads, but has no reliable way to know which ideas work. A system is needed that tells the team what kind of content to make for Instagram and Meta ads.", 18),
         lead="The problem came from first-hand observation, then had to be tested with research.",
         take="An observation is not yet a finding. The next steps break the problem down and test it.")

    page("Discover", "Problem analysis", "Problem tree",
         '<div class="tree" style="min-width:0"><div class="tier-l">Effects</div><div class="effects">' + "".join(f'<div class="eff">{x}</div>' for x in
         ["Ad budget spent on formats that don't perform", "Shoot days give too few usable ads", "Repetitive ads and fatigue", "Wins are not repeated", "Team burnout before drops"]) +
         '</div><div class="trunk"></div><div class="core"><small>Core problem</small><b>BLUORNG decides what content and ads to make without knowing what works</b></div><div class="trunk"></div><div class="tier-l">Root causes</div><div class="roots">' +
         "".join(f'<div class="root"><b>{k}</b>{v}</div>' for k, v in
                 [("DATA", "Results spread across Insights, Ads Manager and Shopify"), ("PLANNING", "Ads are not planned before the shoot"),
                  ("SILOS", "Organic and paid planned separately"), ("MEMORY", "No record of what worked last drop"),
                  ("MARKET", "Competitor study is manual"), ("PRESSURE", "Drop deadlines push instinct-led choices")]) + "</div></div>",
         lead="Breaking the core problem into causes and effects.",
         take="The effects are costs. The causes are missing information and missing planning.", w=960)

    page("Discover", "Problem analysis", "Why does it happen? Five whys",
         '<div class="ladder">' + "".join(
             f'<div{" class=root" if i == 4 else ""} style="margin-left:{i * 4}%"><b>{k}</b><span>{t}</span></div>'
             for i, (k, t) in enumerate([("Why 1", "Why did last drop's ads underperform? They all looked alike."),
                                         ("Why 2", "They were all cut from the same lookbook footage."),
                                         ("Why 3", "The shoot was planned only for the lookbook."),
                                         ("Why 4", "Nobody knew which ad angles worked, so none were planned."),
                                         ("Root", "The team has no evidence of what works to plan shoots and ads around.")])) + "</div>",
         lead="Asking why, five times, from a real situation in the last drop.",
         take="Fixing ads means fixing planning, and fixing planning needs evidence.")

    page("Discover", "Problem area and target users", "Where to focus, and for whom",
         callout("Problem area", "The planning stage of content: deciding what to shoot, post and advertise for each drop. This is where costs are committed and where evidence is missing.", 19) +
         tiles([T("Primary users", "Marketing and content team", "Marketing lead, performance marketer, social media manager, content strategist.", True),
                T("Secondary users", "Makers", "Photographer, video editor, graphic designer who turn plans into content."),
                T("Approvers", "Co-founders", "Protect the brand and approve campaigns and spend."),
                T("Beneficiaries", "Audience", "Get content that is more relevant and less repetitive.")], "c4"),
         lead="Narrowing the scope so research has a clear target.",
         take="Next: test this with the people involved. Primary research covers the team and the audience.")

    # ------------------------------------------------------------------ 02 RESEARCH
    divider("02", "Research", "Testing the problem with BLUORNG's audience and team: a survey of 80 people and 10 interviews.",
            ["Research plan", "User base and segmentation", "Questionnaire", "Interviews", "Research report"], 3)
    page("Research", "Primary research plan", "Research plan",
         '<div class="grid2"><div class="t"><span class="k">Objectives</span><ul><li>Learn how the team decides what to make, and what data it uses.</li><li>Find where time and money are lost in a drop cycle.</li><li>Learn what content BLUORNG\'s audience watches, saves, trusts and buys from.</li><li>Understand what would help the team plan better.</li></ul></div>' +
         '<div class="t dk"><span class="k">Methods</span><ul><li>Online survey of BLUORNG\'s audience, 80 responses.</li><li>10 semi-structured interviews with BLUORNG\'s team, 20 to 45 minutes.</li><li>Observation during a drop cycle, from inside the team.</li></ul></div></div>' +
         mx("minmax(230px,2fr) repeat(3,minmax(80px,.7fr))", ["Research question", "Survey", "Interviews", "Observation"],
            [["How does the team decide what to make?", "", '<i class="dt f"></i>', '<i class="dt f"></i>'],
             ["How do they know what worked?", "", '<i class="dt f"></i>', '<i class="dt f"></i>'],
             ["Where are time and money lost?", "", '<i class="dt f"></i>', '<i class="dt f"></i>'],
             ["What content does the audience value and trust?", '<i class="dt f"></i>', "", ""],
             ["What makes ads work or feel cheap?", '<i class="dt f"></i>', '<i class="dt f"></i>', ""]]),
         lead="Two groups, two methods: a survey for the audience, interviews for the team.",
         take="Every research question is covered by at least one method.", w=920)

    page("Research", "User base and segmentation", "Who we researched",
         '<div class="grid2"><div><p class="chart-t">Team segments (interviews)</p>' +
         tiles([T("Deciders", "Plan and approve", "Co-founder, marketing lead, content strategist.", True),
                T("Optimisers", "Run and measure", "Performance marketer, social media manager, e-commerce."),
                T("Makers", "Create content", "Photographer, video editor, graphic designer."),
                T("Front line", "Hear customers", "Retail store manager.")], "c2") + '</div>'
         '<div><p class="chart-t">Audience segments (survey)</p>' +
         tiles([T("Hype hunters", "Follow drops", "Act on teasers and countdowns."),
                T("Culture seekers", "Love the world", "Watch BTS, collabs and culture posts."),
                T("Style learners", "Want to dress well", "Save styling and fit content."),
                T("Quality checkers", "Judge value", "Need close-ups before paying premium.", True)], "c2") + "</div></div>",
         lead="The team who make content, and the audience who receive it.",
         take="Interviews target all four team segments. The survey reaches 18 to 30 year-old streetwear followers.", w=920)

    qs = D.SURVEY

    def qcard(qid, t, kind, opts, k):
        how = "Pick one" if kind == "single" else f"Pick up to {k}"
        if qid == "Q13":
            how = "Scale 1 to 5"
        if qid in ("Q16", "Q17"):
            how = "Open, coded"
        t = re.sub(r" \((pick up to \d|open answer, coded)\)", "", t)
        o = (f'<div class="qc-o same">Same nine content types as Q7</div>' if qid in ("Q8", "Q9")
             else f'<div class="qc-o">{"".join(f"<span>{e(x)}</span>" for x in opts)}</div>')
        return f'<div class="qc"><div class="qc-h"><b>{qid}</b><span>{e(t)}</span><i>{how}</i></div>{o}</div>'

    def qsec(title, items):
        head = f'<p class="chart-t">{title}</p>' if title else ""
        return f'<div class="qs">{head}' + "".join(qcard(qid, t, kind, opts, k) for qid, t, kind, opts, _, k in items) + "</div>"

    page("Research", "Questionnaire", "Audience survey, part 1",
         '<div class="grid2" style="align-items:start">' + qsec("A. About you", qs[0:5]) + qsec("B. Discovery and content", qs[5:10]) + "</div>",
         lead="17 questions on a Google Form, shared through BLUORNG's Instagram stories and streetwear communities. 5 to 7 minutes.",
         take="Section A checks the sample knows the brand. Section B finds which content the audience watches, saves and buys from.", w=980)
    page("Research", "Questionnaire", "Audience survey, part 2",
         '<div class="grid2" style="align-items:start">' + qsec("C. Ads and trust", qs[10:14]) +
         '<div class="qs">' + qsec("C. Ads and trust, continued", qs[14:16]) + qsec("D. Your voice", qs[16:]) + "</div></div>",
         lead="Questions about ads, trust and what people want more of. Open answers were coded into the groups shown.",
         take="Responses were collected from 80 people. The next pages show what they said.", w=980)

    page("Research", "Survey results / Who answered", "80 respondents",
         '<div class="grid3">' + panel("Age", bars_from("Q1", hi=("19–22", "23–26"), sort=False, label_w="60px", maxv=50), "n = 80") +
         panel("City", bars_from("Q2", hi=("Delhi NCR",), label_w="90px", maxv=50), "n = 80") +
         panel("Daily time on Instagram", bars_from("Q3", hi=("2–4 hours",), sort=False, label_w="100px", maxv=60), "n = 80") + "</div>" +
         '<div class="grid2">' + panel("Follow BLUORNG on Instagram", stacked([(o, p) for o, c, p in S["Q4"]]), "Q4") +
         panel("Bought from BLUORNG", stacked([(o, p) for o, c, p in S["Q5"]]), "Q5") + "</div>",
         lead="Mostly 19 to 26, mostly Delhi NCR and Mumbai, heavy Instagram users.",
         take=f"{q('Q4')['Yes']}% follow BLUORNG and {q('Q5')['Yes, more than once'] + q('Q5')['Yes, once']}% have bought, so the sample knows the brand.",
         source="Sample survey, n = 80", w=960)

    page("Research", "Survey results / Discovery and content", "What the audience watches, saves and buys from",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.5fr) minmax(0,1fr)">' +
         panel("Brand content: enjoy watching, save or share, made me want to buy (% of 80)",
               grouped(sorted([(o, [q("Q7")[o], q("Q8")[o], q("Q9")[o]]) for o in D.CONTENT], key=lambda r: -r[1][1]), ["Enjoy watching", "Save or share", "Want to buy"]),
               "Q7, Q8, Q9. Sorted by saves") +
         '<div style="display:grid;gap:12px;align-content:start">' + panel("Where they discover brands", bars_from("Q6", hi=("Instagram Reels",), label_w="120px")) +
         panel("Favourite format", stacked([(o, p) for o, c, p in S["Q10"]]), "Q10") + "</div></div>",
         lead="Watching, saving and buying are driven by different content.",
         take=f"Memes get watched ({q('Q7')['Memes, culture']}%) but rarely drive purchase ({q('Q9')['Memes, culture']}%). Drop teasers ({q('Q9')['Drop teasers']}%) and styling ({q('Q9')['Styling videos']}%) do.",
         source="Sample survey, n = 80", w=1060)

    page("Research", "Survey results / Ads", "What makes an ad work",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)">' + panel("What makes you stop scrolling on an ad?", bars_from("Q12", hi=("A real person or creator wearing it", "Close-up of fabric and details"), label_w="minmax(150px,230px)"), "Q12, pick up to 2") +
         '<div style="display:grid;gap:12px;align-content:start">' + panel('"Most streetwear ads on Instagram look the same"', stacked([(o, p) for o, c, p in S["Q13"]]), f"Q13. 1 = disagree, 5 = agree. Mean {D.likert_mean(ROWS, 'Q13'):.1f}") +
         panel("How often they notice streetwear ads", stacked([(o, p) for o, c, p in S["Q11"]]), "Q11") + "</div></div>",
         lead="Ads work when they feel real and show the product up close.",
         take=f"Real people ({q('Q12')['A real person or creator wearing it']}%) and close-ups ({q('Q12')['Close-up of fabric and details']}%) stop the scroll. Studio model shots stop only {q('Q12')['Studio model shot']}%.",
         source="Sample survey, n = 80", w=980)

    page("Research", "Survey results / Trust", "What builds trust, and what feels cheap",
         '<div class="grid2">' + panel("What makes you trust a premium brand online?", bars_from("Q14", hi=("Close-up quality shots", "Consistent aesthetic", "Real people wearing it"), label_w="minmax(140px,190px)"), "Q14, pick up to 3") +
         '<div style="display:grid;gap:12px;align-content:start">' + panel("What makes a brand ad feel cheap?", bars_from("Q16", hi=("Too polished, feels fake", "Same ad shown again and again"), label_w="minmax(150px,200px)"), "Q16, open answer, coded") +
         panel("Bought after seeing an Instagram ad", stacked([(o, p) for o, c, p in S["Q15"]]), "Q15") + "</div></div>",
         lead="Premium trust comes from quality you can see. Repetition and over-polish break it.",
         take=f"Repeating the same ad ({q('Q16')['Same ad shown again and again']}%) and over-polished ads ({q('Q16')['Too polished, feels fake']}%) feel cheap. BLUORNG needs more ad variety, not more spend on one ad.",
         source="Sample survey, n = 80", w=960)

    agree = q("Q13")["4"] + q("Q13")["5"]
    page("Research", "Survey results / Summary", "What 80 people told us",
         tiles([stat("Discover through Reels", f"{q('Q6')['Instagram Reels']}%", "Reels are the main door to new brands.", True),
                stat("Ads look the same", f"{agree}%", "Agree or strongly agree that streetwear ads look alike."),
                stat("Stop for real people", f"{q('Q12')['A real person or creator wearing it']}%", "Versus 10% for studio model shots."),
                stat("Trust close-ups", f"{q('Q14')['Close-up quality shots']}%", "Close-up quality shots build trust in premium."),
                stat("Want styling ideas", f"{q('Q17')['Styling ideas']}%", "Top request for what BLUORNG should post more."),
                stat("Bought after an ad", f"{q('Q15')['Yes, several times'] + q('Q15')['Yes, once']}%", "Ads do convert, when they land.")]),
         lead="The audience's side of the story, in six numbers.",
         take="The audience rewards real, detailed, varied content. BLUORNG's ads need more variety than one lookbook shoot gives.",
         source="Sample survey, n = 80")

    page("Research", "Interviews", "Interview plan",
         '<div class="grid2" style="grid-template-columns:minmax(0,1fr) minmax(0,1.1fr)"><div class="panel"><p class="chart-t">Interview guide</p><ol class="ql">' +
         "".join(f"<li>{e(x)}</li>" for x in D.INTERVIEW_GUIDE) + "</ol></div>" +
         '<div class="panel"><p class="chart-t">Participants, BLUORNG team</p>' +
         mx("50px minmax(170px,1.6fr) 70px", ["Code", "Role", "Min"], [[c, e(r), str(m)] for c, r, m, *_ in D.INTERVIEWS]) + "</div></div>",
         lead="10 semi-structured interviews, 20 to 45 minutes each, recorded with consent.",
         take="Each interview followed the same guide, so answers can be compared across roles.", w=980)

    def interview_card(iv):
        code, role, mins, ans, quote_t, tags = iv
        qa = "".join(f'<div class="qa"><span>Q{n}</span><p>{e(a)}</p></div>' for n, a in ans)
        return (f'<div class="iv"><div class="iv-h"><div class="mono-av">{code}</div><div><b>{e(role)}</b><span>{mins} min</span></div></div>'
                f'<p class="iv-q">"{e(quote_t)}"</p>{qa}{chips(tags)}</div>')

    for i in range(0, 10, 2):
        page("Research", "Interviews / Responses", f"Interviews {i + 1} and {i + 2}",
             f'<div class="grid2">{interview_card(D.INTERVIEWS[i])}{interview_card(D.INTERVIEWS[i + 1])}</div>',
             lead="Key answers, numbered by interview question.",
             take={0: "Leadership feels the cost but can't trace it to content.", 2: "Ads are measured, but competitor and organic learning never reaches them.",
                   4: "Shoots are planned for the lookbook, and ad formats come too late.", 6: "Briefs and goals live in chats, so work is redone.",
                   8: "Sales and store signals exist but never reach the content team."}[i],
             source="Sample interviews", w=980)

    page("Research", "Research report / Affinity mapping", "Themes across 10 interviews",
         '<div class="grid2" style="grid-template-columns:minmax(0,1.4fr) minmax(0,1fr)">' +
         panel("How many of the 10 people raised each theme", hbars(D.THEMES, maxv=10, unit="/10", hi={"No clear view of what works", "Fear of looking off-brand", "Shoot day under-planned for ads", "Briefs and feedback over WhatsApp"}, label_w="minmax(170px,240px)"), "Affinity mapping of interview notes") +
         '<div class="t"><span class="k">How</span><p>Every answer was written on a sticky note, grouped by similarity, named, then counted by how many people mentioned it.</p>' +
         chips(["120 notes", "10 themes", "4 raised by 7+ people"]) + "</div></div>",
         lead="Grouping 120 interview notes into themes.",
         take="The strongest themes: no view of what works, brand fears, and under-planned shoots.", source="Sample interviews", w=980)

    ins = [("Data without direction", "The team sees numbers in three tools but can't tell which content earned results.", "9 of 10 interviews"),
           ("Money follows habit", "Ad budget goes to familiar formats like studio lookbooks, which the audience rarely stops for.", f"{q('Q12')['Studio model shot']}% stop for studio shots"),
           ("One shoot, few ads", "Shoots are planned for the lookbook, so ad variety is limited before editing starts.", "7 of 10 interviews"),
           ("Real and detailed wins", "The audience stops for real people and close-ups and trusts quality shots.", f"{q('Q12')['A real person or creator wearing it']}% and {q('Q12')['Close-up of fabric and details']}%"),
           ("Sameness hurts", "Most people feel streetwear ads look alike, and repeated ads feel cheap.", f"{agree}% agree"),
           ("Learning gets lost", "Competitor ads, store feedback and past wins are never collected in one place.", "5 of 10 interviews"),
           ("Brand comes first", "Any help must keep BLUORNG premium and explain its reasoning to be trusted.", "8 of 10 interviews")]
    page("Research", "Primary research report", "Key insights",
         '<div class="tiles c4">' + "".join(
             f'<div class="t{" dk" if i in (0, 1) else ""}"><span class="k">Insight {i + 1}</span><h5>{e(t)}</h5><p>{e(p)}</p><div class="n" style="font-size:18px;margin-top:auto">{e(n)}</div></div>'
             for i, (t, p, n) in enumerate(ins)) + '<div class="t dash"><span class="k">Next</span><h5>Who feels this most</h5><p>Insights become personas, pain points and a journey map.</p></div></div>',
         lead="Combining the survey and the interviews into seven insights.",
         take="The problem is confirmed: BLUORNG commits shoot and ad money before it knows what works.", source="Sample survey and interviews", w=980)

    page("Research", "Primary research report", "Pain points and gain points",
         '<div class="grid2"><div class="t"><span class="k">Pain points</span><ul>' + "".join(f"<li>{x}</li>" for x in [
             "No single view of which posts and ads work, and why",
             "Ad spend and formats chosen by habit",
             "Shoot days planned for the lookbook, too few ad cuts",
             "Competitor ads studied by hand, then forgotten",
             "Organic winners not reused as ads",
             "Briefs and feedback scattered across WhatsApp",
             "Idea fatigue every Monday and before every drop"]) + "</ul></div>"
         '<div class="t dk"><span class="k">Gain points, what they hope for</span><ul>' + "".join(f"<li>{x}</li>" for x in [
             "Know which ad types and post types to make next",
             "Plan ad angles before the shoot, get more from each shoot day",
             "Learn from BLUORNG's past content and premium competitors",
             "Spend ad budget with confidence",
             "Suggestions that keep the brand premium",
             "Reasons behind every suggestion, for quick approval",
             "One shared memory of what worked"]) + "</ul></div></div>" +
         tiles([stat("Team", "9/10", "can't say which content earned results"), stat("Audience", f"{agree}%", "say streetwear ads look the same"),
                stat("Shoot day", "3–4", "ads run from a full lookbook shoot", True)]),
         lead="What hurts today, and what the team wishes for.",
         take="The gains point to one need: guidance on what to make and how to make it, before money is spent.")

    # ------------------------------------------------------------------ 03 DEFINE
    divider("03", "Define", "Turning research into people, a journey, a problem statement and design goals.",
            ["Personas", "Empathy maps", "User journey map", "Problem statement", "Design goals"], 4)

    def persona(av, name, role, bio, quote_t, goals, pains, behaviours, tools, dk=False):
        return (f'<div class="persona-in"><div class="p-top"><div class="mono-av{" alt" if dk else ""}">{av}</div><div><h4>{e(name)}</h4><p>{e(role)}</p></div></div>'
                f'<p class="p-quote">"{e(quote_t)}"</p><p class="p-bio">{e(bio)}</p>'
                f'<div class="p-grid" style="grid-template-columns:repeat(3,minmax(0,1fr))"><div class="go"><h6>Goals</h6><ul>{"".join(f"<li>{x}</li>" for x in goals)}</ul></div>'
                f'<div class="fr"><h6>Pain points</h6><ul>{"".join(f"<li>{x}</li>" for x in pains)}</ul></div>'
                f'<div><h6>Behaviours</h6><ul>{"".join(f"<li>{x}</li>" for x in behaviours)}</ul></div></div>'
                f'<div class="p-foot"><div class="tools">{"".join(f"<span>{t}</span>" for t in tools)}</div></div></div>')

    page("Define", "Personas", "Persona 1 and 2",
         '<div class="personas" style="margin:0">' +
         persona("NK", "Naina Kapoor, 31", "Marketing Lead", "Owns drop campaigns and the ad budget. Reports to the founders.",
                 "Half of our ad budget goes to formats we picked out of habit.",
                 ["Make every drop sell through", "Justify ad spend", "Keep the brand premium"],
                 ["Can't trace results to content", "Shoot gives too few ad cuts", "Approvals by taste"],
                 ["Runs planning meetings", "Checks ROAS daily during drops"], ["Ads Manager", "IG Insights", "Sheets"]) +
         persona("AV", "Aditya Verma, 28", "Performance Marketer, Meta Ads", "Runs and optimises every Meta campaign for drops and retargeting.",
                 "I can see an ad is dying, not why.",
                 ["Lower cost per sale", "Test more creative angles", "Spot fatigue early"],
                 ["Same footage in five crops", "Competitor research by hand", "Learns of organic winners late"],
                 ["Lives in Ads Manager", "Browses the Ad Library weekly"], ["Ads Manager", "Ad Library", "Shopify"]) + "</div>",
         lead="Built from the interviews with the deciders and optimisers.",
         take="Both carry the cost of wrong content decisions: one owns the budget, one spends it.", w=1040)

    page("Define", "Personas", "Persona 3 and 4",
         '<div class="personas" style="margin:0">' +
         persona("RS", "Riya Sharma, 26", "Social Media Manager", "Plans and posts BLUORNG's Instagram every week.",
                 "I don't need more numbers. I need to know what they mean for next week.",
                 ["A fresh, on-brand feed", "Grow saves and reach", "Plan ahead of drops"],
                 ["Blank page every Monday", "Manual monthly reports", "Trends feel off-brand"],
                 ["Screenshots competitors", "Keeps ideas in Notes"], ["IG Insights", "Notion", "WhatsApp"]) +
         persona("KM", "Karan Malhotra, 27", "Photographer", "Shoots lookbooks, campaigns and product content for each drop.",
                 "If I knew the ad angles before the shoot, I could get three times the content.",
                 ["Get everything in one day", "Avoid re-shoots", "Do creative work"],
                 ["Shot list arrives late", "Ad formats asked after wrap", "Briefs as voice notes"],
                 ["Shoots extra just in case", "Plans from moodboards"], ["Camera", "Drive", "WhatsApp"], dk=True) + "</div>",
         lead="Built from the interviews with the optimisers and makers.",
         take="Riya needs direction for organic. Karan needs a plan before the shoot.", w=1040)

    def emp(av, name, says, thinks, does, feels, dk=False):
        return (f'<article class="emp"><div class="emp-h"><div class="mono-av{" alt" if dk else ""}">{av}</div><div><b>{name}</b></div></div><div class="quad">'
                f'<div><h6>SAYS</h6>{says}</div><div><h6>THINKS</h6>{thinks}</div><div><h6>DOES</h6>{does}</div><div><h6>FEELS</h6>{feels}</div></div></article>')
    page("Define", "Empathy maps", "Empathy maps",
         '<div class="emp-grid" style="grid-template-columns:repeat(2,minmax(0,1fr));margin:0">' +
         emp("NK", "Naina", '"Which post sold this drop?"', "Am I wasting budget?", "Approves plans, checks ROAS", "Pressure to justify spend") +
         emp("AV", "Aditya", '"Frequency is 4.2, it\'s burning."', "The organic team had a great Reel. Why didn't I know?", "Duplicates ad sets, studies Ad Library", "Stuck waiting on creative") +
         emp("RS", "Riya", '"What should we post this week?"', "Am I just guessing?", "Scrolls competitors, builds decks", "Creative burnout") +
         emp("KM", "Karan", '"Do you need a vertical version?"', "This would make a great ad, nobody asked.", "Shoots extra coverage", "Frustrated by re-shoots", dk=True) + "</div>",
         lead="What each persona says, thinks, does and feels during a drop.",
         take="Across all four: they act without evidence and feel the cost later.", w=1000)

    stages = ["Drop brief", "Ideate", "Plan shoot", "Shoot day", "Edit and approve", "Launch posts and ads", "Monitor", "Next drop"]
    emo = [3, 2, 2, 3, 1.5, 3.5, 1, 2]
    xs = [50 + 100 * i for i in range(8)]
    ys = [135 - (v - 1) * 37 for v in emo]
    path = f"M{xs[0]} {ys[0]} " + " ".join(f"C{xs[i - 1] + 50} {ys[i - 1]} {xs[i] - 50} {ys[i]} {xs[i]} {ys[i]}" for i in range(1, 8))
    dots = "".join(f'<span class="jd{" low" if v <= 1.5 else (" high" if v >= 3.5 else "")}" style="left:{(x / 800) * 100:.2f}%;top:{y / 150 * 100:.1f}%"></span>' for x, y, v in zip(xs, ys, emo))
    rows = [("Doing", ["Gets products and drop date", "Moodboards, competitor scrolling", "Shot list for the lookbook", "One shoot, models, crew", "Edits, ratios, founder review", "Posts and 3 to 4 ads go live", "Watches ROAS, sees fatigue", "Starts again from scratch"]),
            ("Thinking", ['"What worked last time?"', '"Is this on-brand?"', '"Ads can come from this"', '"Shoot extra just in case"', '"Can we get a vertical?"', '"Hope this one works"', '"Why is it dying?"', '"What did we learn?"']),
            ("Pain", ["No past results at hand", "Instinct and trends", "Ad angles not planned", "Too few ad cuts", "Re-edits, late feedback", "Spend on habit formats", "No reason why", "Nothing recorded"]),
            ("Opportunity", ["Show what worked", "Suggest proven ideas", "Plan ad angles early", "Shot list for ads too", "Formats known up front", "Back proven angles", "Explain results", "Save the learning"])]
    j = '<div class="journey" style="grid-template-columns:96px repeat(8,minmax(0,1fr));min-width:0"><div class="rl sh"></div>' + "".join(f'<div class="sh"><small>{i + 1:02d}</small>{s}</div>' for i, s in enumerate(stages))
    j += f'<div class="rl">Emotion</div><div class="curve" style="position:relative;grid-column:2/-1"><svg viewBox="0 0 800 150" preserveAspectRatio="none"><line x1="0" y1="61" x2="800" y2="61" class="sv-line" stroke-dasharray="3 5" vector-effect="non-scaling-stroke"/><path d="{path} L750 150 L50 150 Z" style="fill:color-mix(in srgb,var(--ink) 9%,transparent)"/><path d="{path}" fill="none" style="stroke:var(--ink)" stroke-width="2.5" vector-effect="non-scaling-stroke"/></svg>{dots}</div>'
    for lab, cells in rows:
        cls = {"Thinking": "think", "Pain": "pain", "Opportunity": "opp"}.get(lab, "")
        j += f'<div class="rl">{lab}</div>' + "".join(f'<div class="{cls}">{c}</div>' for c in cells)
    j += "</div>"
    page("Define", "User journey map", "A drop, through Naina's and Aditya's eyes", j,
         lead="The current experience of planning, making and running content for one drop.",
         take="The lowest points are where money is committed: editing, running ads and monitoring without answers.", w=1120)

    page("Define", "Problem statement", "Problem statement",
         callout("Problem statement", "BLUORNG's marketing and content team lacks a structured way to pre-plan ads and organic content, and has no reliable feedback on which content works. As a result, shoot days produce fewer usable ads than they could, Meta ad spend follows habit instead of evidence, and Instagram posting relies on instinct rather than on what has worked for BLUORNG and comparable premium streetwear brands.", 18) +
         '<p class="chart-t">How might we...</p>' +
         tiles([T("HMW 1", "", "Show the team which of its ads and posts work, and why?"),
                T("HMW 2", "", "Learn from what works for comparable premium streetwear brands?"),
                T("HMW 3", "", "Plan ad angles before the shoot, so one shoot day gives the most ads?"),
                T("HMW 4", "", "Suggest what to post on Instagram, based on BLUORNG's own history?"),
                T("HMW 5", "", "Help the team spend Meta budget with confidence?"),
                T("HMW 6", "", "Keep every suggestion premium and on-brand?", True)]),
         lead="Everything learned so far, in one statement.",
         take="Six questions to ideate on. None of them assumes a solution yet.", w=980)

    goals = [("G1", "Show what works", "Reveal which BLUORNG posts and ads perform, by type, with reasons.", "Name top ad type in under 1 min"),
             ("G2", "Learn from the market", "Bring in what works for premium streetwear competitors.", "Competitor patterns weekly"),
             ("G3", "Suggest what to make", "Recommend ad ideas and organic posts for the next drop.", "Ideas ready before planning"),
             ("G4", "Plan the shoot", "Turn ideas into a shoot plan that serves posts and ads.", "Ad cuts per shoot from ~4 to 10+"),
             ("G5", "Spend with confidence", "Back proven angles with ad budget.", "Lower cost per sale"),
             ("G6", "Protect the brand", "Keep every suggestion premium and explain it.", "Founders approve most ideas"),
             ("G7", "Close the loop", "Record what each drop teaches for the next one.", "Every drop adds learning")]
    page("Define", "Defined design goals", "Design goals",
         callout("Overall goal", "Give BLUORNG a system that suggests what to make and how to make it, for Instagram and Meta ads.", 20) +
         '<div class="tiles c4">' + "".join(f'<div class="t{" dk" if i in (2, 3) else ""}"><span class="k">{g}</span><h5>{e(t)}</h5><p>{e(p)}</p><span class="k" style="margin-top:auto">Measure: {e(m)}</span></div>' for i, (g, t, p, m) in enumerate(goals)) + "</div>",
         lead="What any solution must achieve, and how we'll measure it.",
         take="With goals set, ideation can begin. Every idea will be checked against these seven goals.", w=1000)

    # ------------------------------------------------------------------ 04 IDEATE
    divider("04", "Ideate", "Generating many ideas, filtering them to one direction, then imagining it in use.",
            ["Brainstorming", "Brainwriting", "SCAMPER", "Bullseye", "Priority matrix", "Final direction", "User scenarios", "Storyboards"], 5)

    mind = [("Know what works", ["Weekly results digest", "Tag every post by type", "Compare to own average", "Hire a content analyst"]),
            ("Learn from market", ["Agency competitor reports", "Ad Library tracker", "AI scan of competitor ads", "Trend newsletters"]),
            ("Suggest what to make", ["AI idea generator", "Ideas from past winners", "Creative testing playbook", "Agency concepts"]),
            ("Plan the shoot", ["Shared shot-list template", "Ad angles in the brief", "Shoot-day app", "Pre-shoot checklist"]),
            ("Spend better", ["Test small, then scale", "Promote organic winners", "Fatigue alerts", "Monthly spend review"]),
            ("Protect brand", ["Written brand rules", "Founder review queue", "Brand-fit check", "Reference library"])]
    page("Ideate", "Ideation / Brainstorming", "Brainstorming",
         '<div class="mind"><div class="mind-c">How might we help BLUORNG decide what to make?</div>' + "".join(
             f'<div class="mind-b"><h6>{e(h)}</h6>{chips(ideas)}</div>' for h, ideas in mind) + "</div>",
         lead="A mind map around the HMW questions. 24 ideas, no judging yet.",
         take="Ideas range from hiring people to processes to software. All are kept for now.", w=1000)

    page("Ideate", "Ideation / Brainwriting 6-3-5", "Brainwriting",
         tiles([stat("Session", "6-3-5", "6 people, 3 ideas each, 5 rounds of building on each other's ideas.", True),
                stat("Ideas produced", "54", "After removing duplicates."),
                stat("Participants", "6", "2 marketing, 2 content, 1 designer, me.")], "") +
         rail([("ROUND 1", "Track which ads worked"), ("ROUND 2", "Group them by ad type"), ("ROUND 3", "Compare with competitor ads"), ("ROUND 4", "Let AI read both and spot patterns"), ("ROUND 5", "Suggest next ads from the patterns")]) +
         '<div style="height:10px"></div>' +
         rail([("ROUND 1", "Better shoot briefs"), ("ROUND 2", "Add ad angles to the brief"), ("ROUND 3", "Suggest angles from results"), ("ROUND 4", "Shot list per angle"), ("ROUND 5", "Checklist on the photographer's phone")]),
         lead="Building on each other's ideas in rounds. Two of the strongest chains:",
         take="Both chains ended at the same place: use evidence to suggest what to make and plan the shoot around it.", w=980)

    sc = [("S", "Substitute", "Replace instinct-led planning with evidence-led suggestions."),
          ("C", "Combine", "Combine BLUORNG's results with competitor ads from the Ad Library."),
          ("A", "Adapt", "Adapt Spotify's weekly picks into weekly content picks."),
          ("M", "Modify", "Turn the shoot brief into an ad-angle plan."),
          ("P", "Put to other use", "Reuse winning organic Reels as ads."),
          ("E", "Eliminate", "Remove manual reporting and screenshot decks."),
          ("R", "Reverse", "Plan the ads first, then the shoot.")]
    page("Ideate", "Ideation / SCAMPER", "SCAMPER",
         '<div class="tiles c4">' + "".join(f'<div class="t{" dk" if l == "R" else ""}"><div class="n">{l}</div><span class="k">{w}</span><p>{e(t)}</p></div>' for l, w, t in sc) +
         '<div class="t dash"><span class="k">Result</span><div class="n">7</div><p>New angles on the current process.</p></div></div>',
         lead="Questioning the current process one letter at a time.",
         take="SCAMPER reframed the process: plan ads first, combine own and competitor data, remove manual reports.")

    concepts = [("C1", "Content analyst hire", "A full-time analyst studies results and competitors and advises the team."),
                ("C2", "Creative agency", "Outsource ad strategy, competitor research and ad creative."),
                ("C3", "Tracking template", "A shared Notion or Sheets tracker and a weekly review meeting."),
                ("C4", "Testing playbook", "A written process for testing ad angles and planning shoots."),
                ("C5", "AI insights dashboard", "Software that analyses BLUORNG's page and ads plus the Meta Ad Library, then suggests what to make."),
                ("C6", "WhatsApp digest bot", "A weekly message summarising top posts and ads."),
                ("C7", "Social listening tool", "An off-the-shelf subscription for trends and competitor tracking."),
                ("C8", "Creator network", "A roster of creators for regular UGC ads.")]
    page("Ideate", "Ideation / Idea pool", "Eight ideas worth testing",
         '<div class="tiles c4">' + "".join(f'<div class="t"><span class="k">{c}</span><h5>{e(t)}</h5><p>{e(p)}</p></div>' for c, t, p in concepts) + "</div>",
         lead="Clustering the session outputs into eight distinct directions.",
         take="Eight different directions: people, process, partners and products. Now they need filtering.", w=980)

    # ---------- filtration
    page("Ideate", "Ideation filtration / Bullseye", "Bullseye: how close each idea is to the goals",
         '<div class="split"><svg class="svg-fluid" viewBox="0 0 440 440"><circle cx="220" cy="220" r="205" style="fill:color-mix(in srgb,var(--ink) 5%,transparent)" class="sv-line"/>'
         '<circle cx="220" cy="220" r="138" style="fill:color-mix(in srgb,var(--ink) 14%,transparent)" class="sv-line"/><circle cx="220" cy="220" r="72" class="sv-acc"/>'
         '<text x="220" y="214" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">Meets most goals</text><text x="220" y="234" text-anchor="middle" font-size="12" fill="#fff" opacity=".75">C5, C4</text>'
         '<text x="220" y="112" text-anchor="middle" font-size="11" class="sv-ink sv-mono">MEETS SOME: C2, C3, C8</text><text x="220" y="44" text-anchor="middle" font-size="11" class="sv-ink2 sv-mono">MEETS FEW: C1, C6, C7</text></svg>'
         '<div class="legend-list">'
         '<div class="lg-row"><i style="background:var(--ink)"></i><div><b>Centre: G1 to G7 mostly met</b><span>C5 AI insights dashboard, C4 testing playbook.</span></div></div>'
         '<div class="lg-row"><i style="background:#9a9a9a"></i><div><b>Middle ring: some goals</b><span>C2 agency (costly, slow), C3 template (manual), C8 creators (one angle only).</span></div></div>'
         '<div class="lg-row"><i style="background:#e0e0e0"></i><div><b>Outer ring: few goals</b><span>C1 analyst (one person, costly), C6 digest (reports only), C7 listening tool (generic).</span></div></div></div></div>',
         lead="Placing each idea by how many design goals it meets.",
         take="Two ideas sit at the centre. A process alone (C4) relies on discipline. A system (C5) can carry the process.", w=920)

    pts = [("C1", .78, .52), ("C2", .86, .70), ("C3", .22, .46), ("C4", .30, .64), ("C5", .58, .90), ("C6", .18, .30), ("C7", .46, .36), ("C8", .44, .55)]
    dots = "".join(f'<circle cx="{60 + x * 520:.0f}" cy="{380 - y * 360:.0f}" r="{9 if c == "C5" else 7}" class="{"sv-ink" if c in ("C5", "C4") else "sv-mute"}"/><text x="{72 + x * 520:.0f}" y="{384 - y * 360:.0f}" font-size="13" font-weight="{700 if c in ("C5", "C4") else 500}" class="sv-ink">{c} {dict((a, b) for a, b, _ in concepts)[c]}</text>' for c, x, y in pts)
    page("Ideate", "Ideation filtration / Priority matrix", "Priority matrix: impact vs effort",
         f'<svg class="svg-fluid" viewBox="0 0 700 420"><rect x="60" y="20" width="260" height="180" style="fill:color-mix(in srgb,var(--ink) 8%,transparent)"/><rect x="60" y="20" width="520" height="360" class="sv-line"/>'
         f'<line x1="320" y1="20" x2="320" y2="380" class="sv-line" stroke-dasharray="4 4"/><line x1="60" y1="200" x2="580" y2="200" class="sv-line" stroke-dasharray="4 4"/>'
         f'<text x="72" y="40" font-size="11" class="sv-ink sv-mono">QUICK WINS</text><text x="568" y="40" text-anchor="end" font-size="11" class="sv-ink sv-mono">BIG BETS</text>'
         f'<text x="72" y="370" font-size="11" class="sv-mute sv-mono">FILL-INS</text><text x="568" y="370" text-anchor="end" font-size="11" class="sv-heat sv-mono">MONEY PITS</text>'
         f'<text x="320" y="410" text-anchor="middle" font-size="12" class="sv-mute">Effort and cost →</text><text transform="translate(30 200) rotate(-90)" text-anchor="middle" font-size="12" class="sv-mute">Impact on the problem →</text>{dots}</svg>',
         lead="Impact on the problem against effort and cost for BLUORNG.",
         take="C5 is a big bet with the highest impact. C4 is a quick win that fits inside it. Agency and analyst cost more for less.", w=860)

    crit = [("Tells the team what to make", 25, [2, 4, 5, 3]), ("Learns from own and competitor data", 20, [3, 4, 5, 1]),
            ("Plans shoots for more ads", 15, [3, 3, 4, 5]), ("Keeps the brand in-house", 10, [2, 4, 4, 5]),
            ("Running cost", 10, [1, 2, 4, 5]), ("Speed of insight", 10, [2, 2, 5, 3]), ("Scales with more drops", 10, [3, 2, 5, 3])]
    names = ["C2 Agency", "C1 Analyst", "C5 AI dashboard", "C4 Playbook"]
    tot = [sum(w * s[i] for _, w, s in crit) / 100 for i in range(4)]
    shade = lambda v: f"s{v}"
    tbl = "<tr><th>Criterion</th><th>Weight</th>" + "".join(f'<th style="text-align:center">{n}</th>' for n in names) + "</tr>" + "".join(
        f"<tr><td>{c}</td><td>{w}%</td>" + "".join(f'<td class="s {shade(v)}">{v}</td>' for v in s) + "</tr>" for c, w, s in crit) + \
        '<tr class="tot"><td>Weighted total</td><td>100%</td>' + "".join(f'<td class="s">{t:.2f}</td>' for t in tot) + "</tr>"
    page("Ideate", "Ideation filtration / Evaluation", "Scoring the shortlist",
         f'<div class="panel"><table class="hm">{tbl}</table></div>',
         lead="The four strongest ideas, scored 1 to 5 against weighted criteria from the design goals.",
         take=f"The AI insights dashboard scores highest ({tot[2]:.2f}). The playbook ({tot[3]:.2f}) becomes part of it rather than a separate idea.", w=900)

    page("Ideate", "Final direction", "The direction: BLUPRINT",
         callout("Final idea", "An AI-assisted insights dashboard, powered by Claude AI, that constantly analyses BLUORNG's Instagram page, its Meta ad results and the Meta Ad Library, then tells the team what type of ads and posts to make, how to make them, and how to plan the shoot to get the most out of it.", 17) +
         '<div class="tobe" style="min-width:0;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr) auto minmax(0,1fr)"><div class="cols">' +
         "".join(f'<div class="src-chip"><i></i>{x}</div>' for x in ["BLUORNG Instagram page", "Meta ads results", "Meta Ad Library, competitors", "Drop calendar", "Brand rules"]) +
         '</div><div class="arrow-r">→</div><div class="engine" style="width:170px"><div><b>Claude AI</b><span>Finds patterns, explains why, suggests next</span></div></div><div class="arrow-r">→</div><div class="cols">' +
         '<div class="box acc"><h5>For Meta ads</h5><ul><li>Which ad types work</li><li>New ad ideas and variations</li></ul></div>'
         '<div class="box acc"><h5>For Instagram</h5><ul><li>What to post next</li><li>How to grow organic reach</li></ul></div>'
         '<div class="box acc"><h5>For the shoot</h5><ul><li>Shot list covering posts and ads</li></ul></div></div></div>',
         lead="Chosen because it meets the most design goals at a cost that fits BLUORNG.",
         take="The name BLUPRINT: a plan for every piece of content before the camera is switched on.", w=980)

    sc_ = [("NK", "Naina, Marketing Lead", "Drop planning, Monday", "Opens BLUPRINT before the planning meeting. It shows creator try-on ads cost 28% less per sale than studio lookbooks over the last three drops, and suggests four ad angles for the new drop. She takes it straight into the meeting."),
           ("AV", "Aditya, Performance Marketer", "Mid-campaign", "Gets an alert: the lookbook ad's frequency is 4.1 and clicks are falling. BLUPRINT shows a competitor's close-up ad pattern doing well in the Ad Library and suggests two replacement hooks from footage already shot."),
           ("RS", "Riya, Social Media Manager", "Weekly planning", "Instead of a blank page, she gets five post ideas based on BLUORNG's best-saved posts: styling carousels and fabric close-ups, with reasons and the best times to post."),
           ("KM", "Karan, Photographer", "Shoot day", "Opens the shot list on his phone. It covers the lookbook, four ad angles in 9:16 and 4:5, and close-ups for ASMR posts. He finishes with 14 usable ad cuts instead of four.")]
    page("Ideate", "User scenarios", "BLUPRINT in use",
         '<div class="tiles c2">' + "".join(f'<div class="t"><div class="iv-h"><div class="mono-av">{a}</div><div><b>{e(n)}</b><span>{e(w)}</span></div></div><p>{e(t)}</p></div>' for a, n, w, t in sc_) + "</div>",
         lead="How each persona's day changes with the chosen direction. Figures are illustrative.",
         take="Every scenario moves a decision from instinct to evidence, before money is spent.", w=980)

    P.append(dict(kind="storyboard", n=1))
    P.append(dict(kind="storyboard", n=2))
    P.append(dict(kind="end"))
    return P
