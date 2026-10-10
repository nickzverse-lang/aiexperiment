"""Generate the primary-research result figures (tools/book/research.html).

ALL NUMBERS AND QUOTES HERE ARE ILLUSTRATIVE SAMPLE DATA. They show the shape of a finished
research chapter. Replace every value with real survey, interview, shadowing and audit results.

Run: python3 tools/book/gen_research.py
"""
import html
import pathlib

OUT = pathlib.Path(__file__).resolve().parent / "research.html"
SHADES = ["#0b0b0b", "#8a8a8a", "#cfcfcf", "#5c5c5c", "#e6e6e6"]
e = html.escape


def hbars(rows, maxv=None, unit="%", hi=None, label_w="minmax(120px,200px)"):
    """rows: [(label, value)]; hi: set of labels drawn in ink, others grey (all ink when None)."""
    maxv = maxv or max(v for _, v in rows)
    out = []
    for lab, v in rows:
        cls = "" if (hi is None or lab in hi) else "g"
        out.append(f'<div class="hb-row" style="grid-template-columns:{label_w} minmax(0,1fr) 64px" title="{e(lab)}: {v}{unit}">'
                   f'<span>{e(lab)}</span><span class="tr"><i class="{cls}" style="width:{v / maxv * 100:.1f}%"></i></span><b>{v}{unit}</b></div>')
    return '<div class="hb">' + "".join(out) + "</div>"


def stacked(segs, unit="%"):
    """segs: [(label, value)] summing to ~100."""
    total = sum(v for _, v in segs)
    bar = "".join(f'<i title="{e(l)}: {v}{unit}" style="width:{v / total * 100:.1f}%;background:{SHADES[i % 5]}"></i>' for i, (l, v) in enumerate(segs))
    leg = "".join(f'<span><i style="background:{SHADES[i % 5]}"></i>{e(l)} <b>{v}{unit}</b></span>' for i, (l, v) in enumerate(segs))
    return f'<div class="stk">{bar}</div><div class="stk-l">{leg}</div>'


def donut(segs, centre, sub):
    r, c = 70, 2 * 3.14159 * 70
    off, arcs = 0, []
    for i, (l, v) in enumerate(segs):
        ln = v / 100 * c
        arcs.append(f'<circle cx="90" cy="90" r="{r}" fill="none" stroke="{SHADES[i % 5]}" stroke-width="26" '
                    f'stroke-dasharray="{ln:.1f} {c - ln:.1f}" stroke-dashoffset="{-off:.1f}"><title>{e(l)}: {v}%</title></circle>')
        off += ln
    leg = "".join(f'<span><i style="background:{SHADES[i % 5]}"></i>{e(l)} <b>{v}%</b></span>' for i, (l, v) in enumerate(segs))
    return (f'<div class="dn"><svg viewBox="0 0 180 180" style="transform:rotate(-90deg)">{"".join(arcs)}</svg>'
            f'<div class="dn-c"><b>{centre}</b><span>{sub}</span></div></div><div class="stk-l" style="flex-direction:column;gap:8px">{leg}</div>')


def grouped(rows, series):
    """rows: [(label, [v1, v2, v3])] as percentages."""
    out = []
    for lab, vals in rows:
        bars = "".join(f'<div class="gl" title="{e(series[j])}: {v}%"><span><i style="width:{v}%;background:{SHADES[j]}"></i></span><b>{v}</b></div>' for j, v in enumerate(vals))
        out.append(f'<div class="gb-row"><span>{e(lab)}</span><div class="gb">{bars}</div></div>')
    leg = "".join(f'<span><i style="background:{SHADES[j]}"></i>{e(s)}</span>' for j, s in enumerate(series))
    return '<div class="gbs">' + "".join(out) + f'</div><div class="stk-l">{leg}</div>'


def panel(title, body, note=""):
    n = f'<p class="chart-s">{e(note)}</p>' if note else ""
    return f'<div class="panel"><p class="chart-t">{e(title)}</p>{body}{n}</div>'


def stat(k, n, p, dark=False):
    return f'<div class="t{" dk" if dark else ""}"><span class="k">{e(k)}</span><div class="n">{n}</div><p>{e(p)}</p></div>'


def quote(who, role, text, dark=False):
    return (f'<div class="t q{" dk" if dark else ""}"><p class="qt">"{e(text)}"</p>'
            f'<span class="k">{e(who)} / {e(role)}</span></div>')


F = {}

# ---------- fieldwork overview ----------
F["r-overview"] = '<div class="tiles c5">' + "".join([
    stat("Interviews", "10", "6 BLUORNG team members and 4 audience members, 20 to 45 minutes each.", True),
    stat("Survey A, practitioners", "24", "Content, social and performance roles at fashion and D2C brands."),
    stat("Survey B, audience", "132", "Streetwear followers aged 18 to 30, shared via Instagram stories."),
    stat("Focus groups", "2 x 6", "12 BLUORNG followers and buyers, 60 minutes each."),
    stat("Shadowing and audit", "6 days", "One full drop week shadowed. 90 posts and 30 ads audited."),
]) + "</div>" + '''<div class="panel" style="margin-top:4px"><p class="chart-t">Interview participants</p>
<div class="mx" style="grid-template-columns:70px minmax(170px,1.2fr) minmax(150px,1fr) 110px minmax(200px,1.6fr);min-width:0">
<div class="h">Code</div><div class="h">Role</div><div class="h">Group</div><div class="h">Length</div><div class="h">Focus</div>
<div class="nm">P1</div><div>Marketing Lead</div><div>BLUORNG team</div><div>45 min</div><div>Planning, approvals, what success means</div>
<div class="nm">P2</div><div>Social Media Manager</div><div>BLUORNG team</div><div>40 min</div><div>Ideation, posting, reporting</div>
<div class="nm">P3</div><div>Performance Marketer</div><div>BLUORNG team</div><div>35 min</div><div>Meta ads, testing, fatigue</div>
<div class="nm">P4</div><div>Photographer</div><div>BLUORNG team</div><div>30 min</div><div>Briefs, shoots, formats</div>
<div class="nm">P5</div><div>Video Editor</div><div>BLUORNG team</div><div>30 min</div><div>Edits, versions, changes</div>
<div class="nm">P6</div><div>Graphic Designer</div><div>BLUORNG team</div><div>25 min</div><div>Static posts, stories, approvals</div>
<div class="nm">A1–A4</div><div>Followers and buyers, 20–27</div><div>Audience</div><div>20 min</div><div>Discovery, saving, buying, ads</div>
</div></div>'''

# ---------- interview quotes ----------
F["r-quotes-team"] = '<div class="tiles">' + "".join([
    quote("P1", "Marketing Lead", "We know which drop sold out. We don't know which post made it happen.", True),
    quote("P2", "Social Media Manager", "Every Monday I start from a blank page, even though we've posted hundreds of times."),
    quote("P3", "Performance Marketer", "I end up running the same lookbook clip in five crops and calling it testing."),
    quote("P4", "Photographer", "I find out we needed a vertical version after I've wrapped the shoot."),
    quote("P5", "Video Editor", "The brief is usually a voice note and a Pinterest link."),
    quote("P6", "Graphic Designer", "Feedback comes on WhatsApp at midnight, and then everything changes.", True),
]) + "</div>"

F["r-quotes-aud"] = '<div class="tiles c4">' + "".join([
    quote("A1", "Buyer, 24", "I save the close-up videos. That's how I decide if it's worth the price."),
    quote("A2", "Follower, 21", "If a creator I follow wears it, I'll check it out. A model in a studio, I just scroll."),
    quote("A3", "Buyer, 27", "Show me three ways to wear one piece and I'm sold."),
    quote("A4", "Follower, 20", "The same ad followed me for two weeks. I muted the brand.", True),
]) + "</div>"

# ---------- affinity themes ----------
F["r-themes"] = '<div class="grid2">' + panel(
    "Themes across 6 team interviews (people who raised it)",
    hbars([("Unsure which content works", 6), ("Fear of looking off-brand", 6), ("Idea pressure before drops", 5),
           ("Briefs over WhatsApp", 5), ("Organic and paid apart", 4), ("Slow, late approvals", 4), ("Trust AI only with reasons", 4)],
          maxv=6, unit="/6", hi={"Unsure which content works", "Fear of looking off-brand"}, label_w="minmax(150px,220px)"),
    "Affinity mapping of interview notes") + panel(
    "Themes across 4 audience interviews",
    hbars([("Want to see how to style it", 4), ("Check detail before paying premium", 3), ("Trust creators over models", 3),
           ("Ads feel repetitive", 3), ("Follow for culture, not product", 2)],
          maxv=4, unit="/4", hi={"Want to see how to style it"}, label_w="minmax(150px,220px)"),
    "Affinity mapping of interview notes") + "</div>"

# ---------- Survey A ----------
F["r-sa1"] = '<div class="grid2">' + panel(
    "How do you mainly decide what content to make? (multi-select)",
    hbars([("Gut and experience", 79), ("Trends and audio", 71), ("Competitors", 58), ("Founder or manager decides", 54),
           ("Past performance data", 33), ("Audience comments, DMs", 29), ("Agency suggests", 13)], maxv=100,
          hi={"Gut and experience", "Trends and audio"}), "Survey A, Q5, n = 24") + \
    '<div style="display:grid;gap:14px;align-content:start">' + panel(
        "Checking data vs using it",
        hbars([("Check data weekly or more", 75), ("Use it to plan next content", 29)], maxv=100, hi={"Check data weekly or more"}),
        "Q6 and Q7. Most look; few act on it") + \
    '<div class="tiles c2" style="margin:0">' + stat("I know what type of content works", "2.4<small> / 5</small>", "Average agreement, Q9.") + \
    stat("Fresh ideas every week are hard", "4.1<small> / 5</small>", "Average agreement, Q10.", True) + "</div></div></div>"

F["r-sa2"] = '<div class="grid2">' + panel(
    "How often are your best organic posts turned into ads?",
    stacked([("Always", 4), ("Often", 13), ("Sometimes", 37), ("Rarely", 33), ("Never", 13)]), "Q11, n = 24") + panel(
    "How often do vague briefs cause re-shoots or re-edits?",
    stacked([("Very often", 17), ("Often", 29), ("Sometimes", 38), ("Rarely", 13), ("Never", 4)]), "Q17, n = 24") + panel(
    "How are briefs shared? (multi-select)",
    hbars([("WhatsApp", 63), ("Verbal", 50), ("Doc or Notion", 33), ("Deck", 17), ("No brief", 13)], maxv=100, hi={"WhatsApp"}), "Q16") + \
    '<div class="tiles c2" style="margin:0;align-content:start">' + \
    stat("I get enough ad variations", "2.1<small> / 5</small>", "Performance marketers only, n = 7. Q14.", True) + \
    stat("New ad creatives tested a month", "3–5", "Most common answer. None test 10+. Q13.") + \
    stat("Drop weeks are stressful", "4.3<small> / 5</small>", "Average agreement, Q18.") + \
    stat("Rarely or never promote winners", "46%", "Organic winners left unused, Q11.") + "</div></div>"

F["r-sa3"] = '<div class="grid2" style="grid-template-columns:minmax(0,1.3fr) minmax(0,1fr)">' + panel(
    "Top problems, weighted rank (3, 2, 1 points)",
    hbars([("Idea block", 41), ("Not knowing what works", 38), ("Too few ad variations", 27), ("Unclear briefs", 24),
           ("Approval delays", 19), ("Staying on-brand", 17), ("Too little time", 15), ("Reporting takes time", 11)],
          unit=" pts", hi={"Idea block", "Not knowing what works"}), "Q19, n = 24") + panel(
    "Would you trust content suggestions from an AI tool?",
    '<div style="display:flex;gap:28px;align-items:center">' + donut([("Only if it explains why", 54), ("Only as inspiration", 25), ("Yes", 13), ("No", 8)], "54%", "need the why") + "</div>",
    "Q20, n = 24") + "</div>"

# ---------- Survey B ----------
F["r-sb1"] = '<div class="grid3">' + panel(
    "Age", hbars([("18–21", 38), ("22–25", 44), ("26–30", 18)], maxv=50, hi={"22–25"}, label_w="70px"), "n = 132") + panel(
    "City", hbars([("Delhi NCR", 41), ("Mumbai", 23), ("Bengaluru", 12), ("Other", 24)], maxv=50, hi={"Delhi NCR"}, label_w="100px"), "n = 132") + panel(
    "Relationship with BLUORNG",
    stacked([("Bought", 27), ("Planning to buy", 31), ("Not yet", 42)]) + '<p class="chart-s">68% follow the brand on Instagram</p>', "Q3, Q4") + \
    "</div>" + panel(
    "Where do you discover new streetwear brands? (multi-select)",
    hbars([("Instagram Reels", 72), ("Friends", 48), ("Creators", 45), ("Instagram Explore", 39), ("Ads", 22), ("Stores", 18), ("Reddit, Discord", 9)],
          maxv=100, hi={"Instagram Reels"}), "Q5, n = 132")

F["r-sb2"] = '<div class="grid2" style="grid-template-columns:minmax(0,1.6fr) minmax(0,1fr)">' + panel(
    "Content from fashion brands people watch fully, save, and buy from (% of respondents)",
    grouped([("Styling guides", [47, 49, 31]), ("ASMR, fabric close-ups", [52, 41, 26]), ("Fit checks, street style", [55, 37, 24]),
             ("Behind the scenes", [58, 33, 12]), ("Lookbooks", [44, 29, 21]), ("Collabs", [49, 22, 19]), ("Drop teasers", [61, 18, 34]),
             ("Memes, culture", [64, 14, 4]), ("Founder stories", [23, 11, 6]), ("Interactive stories", [31, 5, 7])],
            ["Watch fully", "Save", "Made me buy"]), "Q6, Q7, Q8. Sorted by saves") + \
    '<div style="display:grid;gap:14px;align-content:start">' + \
    '<div class="callout" style="margin:0"><small>Reading it</small>Memes get watched but not saved. Styling and ASMR detail get saved. Drop teasers turn into purchases.</div>' + \
    '<div class="tiles c2" style="margin:0">' + stat("Saved most", "49%", "Styling guides.", True) + stat("Bought from most", "34%", "Drop teasers.") + "</div></div></div>"

F["r-sb3"] = '<div class="grid2">' + panel(
    "Which ads make you stop scrolling? (multi-select)",
    hbars([("Creator wearing it", 57), ("Close-up details", 46), ("Drop countdown", 38), ("Store or queue hype", 31),
           ("Model lookbook", 24), ("Price or offer", 12)], maxv=100, hi={"Creator wearing it", "Close-up details"}), "Q10, n = 132") + \
    '<div style="display:grid;gap:14px;align-content:start">' + panel(
        "How often should a streetwear brand post?", stacked([("Daily", 21), ("3–5 a week", 58), ("1–2 a week", 21)]), "Q11") + panel(
        "Do you answer polls and quizzes in brand stories?", stacked([("Often", 18), ("Sometimes", 49), ("Never", 33)]), "Q12") + \
    '<div class="tiles c2" style="margin:0">' + stat("Brand ads on Instagram annoy me", "3.6<small> / 5</small>", "Average agreement, Q9.", True) + \
    stat("Most wanted: how to wear it", "38", "Open-ended mentions, Q13.") + "</div></div></div>"

# ---------- focus group card sort ----------
rows = [("Styling guide", [8, 10, 7, 7, 2]), ("ASMR detail", [9, 8, 5, 6, 3]), ("Fit check", [9, 6, 6, 5, 3]),
        ("Behind the scenes", [10, 5, 6, 2, 2]), ("Drop teaser", [9, 2, 4, 6, 3]), ("Lookbook", [7, 4, 2, 4, 5]),
        ("Meme, culture", [11, 1, 9, 1, 1]), ("Plain product post", [4, 2, 1, 3, 8])]
cols = ["Watch", "Save", "Share", "Want to buy", "Skip"]
def shade(v):
    return "s5" if v >= 10 else "s4" if v >= 8 else "s3" if v >= 5 else "s2" if v >= 3 else "s1"
tbl = "<tr><th>Content type</th>" + "".join(f'<th style="text-align:center">{c}</th>' for c in cols) + "</tr>" + "".join(
    f"<tr><td>{e(r)}</td>" + "".join(f'<td class="s {shade(v)}">{v}</td>' for v in vals) + "</tr>" for r, vals in rows)
F["r-focus"] = '<div class="grid2" style="grid-template-columns:minmax(0,1.6fr) minmax(0,1fr)">' + \
    f'<div class="panel"><p class="chart-t">Card sort: what 12 people would do with each post</p><table class="hm">{tbl}</table><p class="chart-s">2 groups of 6. Darker means more people</p></div>' + \
    panel("Reactions to three ad styles (liked it, out of 12)",
          hbars([("Creator UGC try-on", 9), ("ASMR detail ad", 8), ("Studio lookbook ad", 3)], maxv=12, unit="/12", hi={"Creator UGC try-on"}, label_w="minmax(120px,170px)"),
          "Shown as three short ads") + "</div>"

# ---------- shadowing ----------
F["r-shadow"] = '<div class="grid2" style="grid-template-columns:minmax(0,1.3fr) minmax(0,1fr)">' + panel(
    "Team hours in one drop week, by activity",
    hbars([("Editing and resizing", 14), ("Shoot", 11), ("Ideation meetings", 9), ("Blocked on approvals", 7),
           ("Re-edits after late changes", 6), ("Briefing over calls and chats", 5), ("Manual reporting", 3)],
          unit=" h", hi={"Blocked on approvals", "Re-edits after late changes"}, label_w="minmax(160px,230px)"),
    "55 team hours logged over 6 days. 13 h (24%) went to waiting and redoing") + \
    '<div class="tiles c2" style="margin:0;align-content:start">' + \
    stat("WhatsApp threads for one drop", "14", "Ideas, briefs and feedback spread across them.", True) + \
    stat("Times past results came up", "0", "In the drop planning meeting.") + \
    stat("Brief changes after the shoot", "3", "Including a new vertical cut.") + \
    stat("Ad creatives from the shoot", "3", "All cut from the same lookbook footage.") + "</div></div>" + \
    '<div class="rail" style="min-width:0;margin-top:6px">' + "".join(
        f'<div class="node"><div class="card{" endc" if i == 5 else ""}"><small>DAY {i + 1}</small>{t}</div></div>'
        for i, t in enumerate(["Planning meeting from instinct", "Brief sent as a voice note", "Shoot day, lookbook focus",
                               "Edits, approvals wait", "Late changes, re-edits", "Posts and ads go live"])) + "</div>"

# ---------- content audit ----------
F["r-audit"] = '<div class="grid2">' + panel(
    "Saves by series, indexed (median post = 100)",
    hbars([("ASMR", 260), ("One piece, 3 ways", 190), ("Studio diaries", 170), ("Fit check", 140), ("Collab", 120),
           ("Lookbook", 100), ("Drop countdown", 90), ("Memes", 60)], unit="", hi={"ASMR", "One piece, 3 ways", "Studio diaries"}),
    "90 organic posts, last 6 months. Indexed to keep real numbers private") + panel(
    "Meta ads: cost per sale by angle vs share of spend",
    '<div class="mx" style="grid-template-columns:minmax(120px,1fr) minmax(140px,1.4fr) minmax(140px,1.4fr);min-width:0">'
    '<div class="h">Angle</div><div class="h">Cost per sale (avg = 100, lower is better)</div><div class="h">Share of spend</div>' + "".join(
        f'<div class="nm">{a}</div><div><span class="hb-row" style="grid-template-columns:1fr 40px;width:100%"><span class="tr"><i class="{"" if c < 90 else "g"}" style="width:{c / 120 * 100:.0f}%"></i></span><b>{c}</b></span></div>'
        f'<div><span class="hb-row" style="grid-template-columns:1fr 40px;width:100%"><span class="tr"><i class="g" style="width:{s / 50 * 100:.0f}%"></i></span><b>{s}%</b></span></div>'
        for a, c, s in [("Retargeting", 65, 11), ("Creator / UGC", 72, 8), ("Craft detail", 84, 4), ("Scarcity", 97, 31), ("Lookbook", 118, 46)]) +
    "</div>", "30 ads. 77% of spend went to the two angles with average or worse cost") + "</div>"

# ---------- hypotheses ----------
hyp = [("H1", "Decisions come from intuition and trends", "79% gut, 71% trends vs 33% data", "Supported"),
       ("H2", "Data is checked but not used to plan", "75% check weekly, 29% use it to plan", "Supported"),
       ("H3", "Organic winners rarely become ads", "46% rarely or never, 37% sometimes", "Partly"),
       ("H4", "Not enough ad variations", "2.1 / 5 agreement, none test 10+ a month", "Supported"),
       ("H5", "Vague briefs cause re-shoots", "84% at least sometimes, 3 changes in shadowing", "Supported"),
       ("H6", "Drop weeks create pressure", "4.3 / 5 agreement, 5 of 6 interviews", "Supported"),
       ("H7", "Audience prefers BTS, ASMR, styling", "Styling 49% and ASMR 41% saved vs lookbook 29%", "Supported"),
       ("H8", "Audience prefers creator-style ads", "57% vs 24% stop for creator vs model; cost 72 vs 118", "Supported"),
       ("H9", "AI trusted only if it explains", "54% only if it explains why", "Supported"),
       ("H10", "Brand consistency is a top concern", "6 of 6 team interviews", "Supported")]
F["r-hyp"] = '<div class="panel"><div class="mx" style="grid-template-columns:60px minmax(220px,1.4fr) minmax(260px,1.8fr) 130px;min-width:0">' + \
    '<div class="h">ID</div><div class="h">Hypothesis</div><div class="h">Evidence</div><div class="h">Result</div>' + "".join(
        f'<div class="nm">{i}</div><div>{e(h)}</div><div>{e(ev)}</div><div><span class="chip {"chip-acc" if r == "Supported" else "chip-mute"}">{r}</span></div>'
        for i, h, ev, r in hyp) + "</div></div>"

# ---------- insights ----------
ins = [("Data without direction", "The team checks numbers weekly but rarely turns them into what to make next.", "75% check, 29% act"),
       ("The idea treadmill", "Drops demand constant novelty, and idea block is the top-ranked problem.", "41 pts, rank 1"),
       ("Two teams, one feed", "Organic winners rarely reach ads, and ads are cut from one shoot.", "46% rarely or never"),
       ("Spend follows habit", "Most ad money goes to lookbook and scarcity angles that cost more per sale.", "77% of spend"),
       ("Brief is a voice note", "Informal briefs lead to late changes, re-edits and missing formats.", "13 h lost in one week"),
       ("Save-worthy beats scroll-worthy", "Followers save styling and ASMR detail, and stop for creators.", "49% / 41% / 57%"),
       ("Show me why", "AI help is welcome only when it explains itself and stays on-brand.", "54%, 6 of 6")]
F["r-insights"] = '<div class="tiles c4">' + "".join(
    f'<div class="t{" dk" if i in (0, 3) else ""}"><span class="k">Insight {i + 1}</span><h5>{e(t)}</h5><p>{e(p)}</p><div class="n" style="font-size:22px;margin-top:auto">{e(n)}</div></div>'
    for i, (t, p, n) in enumerate(ins)) + \
    '<div class="t dash"><span class="k">Next</span><h5>From insight to design</h5><p>These seven insights set the priority areas, the redefined brief and the design goals that follow.</p></div></div>'

CSS_NOTE = ""
OUT.write_text("".join(f"<!-- @@{k} -->\n{v}\n\n" for k, v in F.items()))
print(OUT, len(F), "figures")
