"""STEPS 3-9: turn an Apify Instagram posts export into a content audit.

Input: a JSON list of posts in the apify/instagram-scraper output shape.
Output: one dict with the performance snapshot, what's working, hashtags, posting pattern, sentiment,
10 content ideas and a 30-day calendar. Every number in the dashboard comes from here.

Engagement = likes + comments (Instagram hides saves, shares and reach from public scrapes).
"""
import datetime as dt
import json
import re
import statistics as st
from collections import Counter, defaultdict

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SLOTS = [("Night", 0, 6), ("Morning", 6, 10), ("Late morning", 10, 13), ("Afternoon", 13, 16),
         ("Evening", 16, 19), ("Prime time", 19, 22), ("Late night", 22, 24)]


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def pct(a, b):
    return (a / b - 1) * 100 if b else 0.0


# ---------------------------------------------------------------- normalise
def post_type(it):
    t, p = it.get("type"), it.get("productType")
    if p == "clips" or (t == "Video" and p in (None, "clips")):
        return "Reel"
    if t == "Video":
        return "Video"
    if t == "Sidecar" or p == "carousel_container":
        return "Carousel"
    return "Image"


def normalise(items):
    posts = []
    for it in items:
        if not it.get("timestamp"):
            continue
        cap = it.get("caption") or ""
        tags = [h.lower().lstrip("#") for h in (it.get("hashtags") or re.findall(r"#(\w+)", cap))]
        likes = it.get("likesCount")
        likes = None if likes is None or likes < 0 else likes
        ts = dt.datetime.fromisoformat(it["timestamp"].replace("Z", "+00:00")).astimezone(IST)
        comments = it.get("commentsCount") or 0
        posts.append(dict(id=it.get("shortCode") or it.get("id"), url=it.get("url") or "", caption=cap, tags=tags,
                          likes=likes, comments=comments, ts=ts, type=post_type(it), pinned=bool(it.get("isPinned")),
                          views=it.get("videoPlayCount") or it.get("videoViewCount"),
                          comment_texts=[c.get("text", "") for c in (it.get("latestComments") or []) if c.get("text")]))
    posts.sort(key=lambda p: p["ts"], reverse=True)
    hidden = all(p["likes"] is None for p in posts)
    for p in posts:
        p["eng"] = (p["likes"] or 0) + p["comments"]
    return posts, hidden


# ---------------------------------------------------------------- classifiers
HOOKS = [  # first match wins
    ("Question", lambda f, w: "?" in f),
    ("Collab reveal", lambda f, w: bool(re.search(r"\s[x×]\s|collab|partner", f, re.I))),
    ("Urgency / scarcity", lambda f, w: bool(re.search(r"limited|last|only|sold out|restock|final|few left|tonight|hours|countdown|\d+\s*(pm|am)", f, re.I))),
    ("Drop announcement", lambda f, w: bool(re.search(r"\bdrop|out now|live now|launch|available|release|arriv|coming|new collection|chapter", f, re.I))),
    ("Store / event invite", lambda f, w: bool(re.search(r"store|pop.?up|event|see you|visit|join us|mumbai|delhi|gurugram|bengaluru", f, re.I))),
    ("Minimal title", lambda f, w: w <= 3),
    ("Emoji-led", lambda f, w: bool(f) and not f[0].isalnum() and f[0] not in "@#\"'"),
    ("Statement / story", lambda f, w: True),
]

CLUSTERS = [
    ("Drops & launches", r"\bdrop|out now|live now|launch|available|release|new collection|chapter|ss\d\d|aw\d\d|fw\d\d|capsule"),
    ("Collaborations", r"\s[x×]\s|collab|partnership|together with|in partnership"),
    ("Campaign & lookbook", r"campaign|lookbook|editorial|shot by|film|styled by|photographed"),
    ("Store & events", r"store|pop.?up|event|flagship|see you|visit us|mumbai|gurugram|delhi|bengaluru|queue"),
    ("Product & craft", r"detail|fabric|gsm|embroider|wash|print|crafted|cotton|quality|stitch|close.?up|texture|made in"),
    ("Culture & community", r"community|fam|tag|fit ?check|repost|culture|artist|music|meme|you guys|spotted|wearing"),
]

CTA = r"link in bio|shop |shop now|available (now|at|on)|\bdm\b|comment|tag (a|your)|visit|register|sign ?up|save (this|it)|share|bluorng\.com|website|\bcop\b|pre-?order|order now|swipe"

LEN_BUCKETS = [("Minimal (0-40)", 0, 40), ("Short (41-120)", 41, 120), ("Medium (121-250)", 121, 250), ("Long (251+)", 251, 10 ** 6)]

EMOTIONS = [
    ("Hype", r"🔥|fire|insane|crazy|hard|heat|goat|dope|sick|unreal|💯|🙌|lit|w drop|banger"),
    ("Desire to buy", r"need|want|cop|buy|take my money|wishlist|must have|🛒|grail|saving up"),
    ("Love & admiration", r"❤|♥|🖤|😍|love|beautiful|clean|aesthetic|best|stunning|elite"),
    ("Questions", r"\?|price|size|when|restock|ship|how much|where|link"),
    ("Frustration", r"sold out|didn.?t get|couldn.?t|expensive|overpriced|delay|refund|worst|scam|bot|never got"),
    ("Tags a friend", r"@\w+"),
]

ASKS = [("Restocks", r"restock|again|back in stock|sold out"), ("Size and fit info", r"size|fit|xl|xs|oversized|true to size"),
        ("Price and availability", r"price|how much|cost|available|where to buy|link"),
        ("Next drop dates", r"when|next drop|release date|coming"), ("Stores in more cities", r"bangalore|bengaluru|pune|hyderabad|kolkata|chennai|store in|come to"),
        ("International shipping", r"ship|international|dubai|usa|uk|canada"), ("More styling / fits", r"styl|fit check|how to wear|outfit|lookbook"),
        ("Behind the scenes", r"bts|behind|process|how .{0,25}made|making")]

TRY_TAGS = {  # candidate new tags per theme; filtered against tags already used
    "Drops & launches": ["streetweardrop", "limiteddrop", "newdrop"],
    "Collaborations": ["streetwearcollab", "collabdrop"],
    "Campaign & lookbook": ["streetwearlookbook", "fashionfilm"],
    "Store & events": ["delhistreetwear", "mumbaistreetwear", "popupstore"],
    "Product & craft": ["madeinindia", "garmentdetails", "heavyweightcotton"],
    "Culture & community": ["indianstreetwear", "streetwearindia", "fitcheck", "streetstyleindia", "ootdindia"],
}


def first_line(cap):
    for line in cap.splitlines():
        if line.strip():
            return line.strip()
    return ""


def hook_of(cap):
    f = first_line(cap)
    w = len(re.findall(r"\w+", f))
    return next(name for name, test in HOOKS if test(f, w))


def cluster_of(p):
    text = p["caption"] + " " + " ".join(p["tags"])
    hits = [(len(re.findall(rx, text, re.I)), -i, name) for i, (name, rx) in enumerate(CLUSTERS)]
    best = max(hits)
    return best[2] if best[0] else "Brand moments"


def len_bucket(cap):
    n = len(cap)
    return next(name for name, a, b in LEN_BUCKETS if a <= n <= b)


def slot_of(h):
    return next(i for i, (_, a, b) in enumerate(SLOTS) if a <= h < b)


# ---------------------------------------------------------------- analysis
def group(posts, key):
    g = defaultdict(list)
    for p in posts:
        g[key(p)].append(p)
    return g


def summarise(groups, base):
    rows = []
    for k, ps in groups.items():
        a = mean(p["eng"] for p in ps)
        rows.append(dict(name=k, n=len(ps), avg=a, lift=pct(a, base), median=st.median(p["eng"] for p in ps)))
    return sorted(rows, key=lambda r: -r["avg"])


def trend(chron):
    n = len(chron)
    xs, ys = range(n), [p["eng"] for p in chron]
    mx, my = (n - 1) / 2, mean(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sum((x - mx) ** 2 for x in xs) or 1)
    change = slope * (n - 1) / my * 100 if my else 0
    half = n // 2
    halves = pct(mean(ys[half:]), mean(ys[:half]))
    direction = "Up" if change > 10 else "Down" if change < -10 else "Flat"
    months = defaultdict(list)
    for p in chron:
        months[p["ts"].strftime("%Y-%m")].append(p["eng"])
    return dict(direction=direction, fit_change=change, halves_change=halves,
                monthly=[dict(month=m, avg=mean(v), n=len(v)) for m, v in sorted(months.items())])


def analyse(items, handle, limit=150, source="", demo=False, audit_date=None):
    posts, hidden = normalise(items)
    posts = posts[:limit]
    n = len(posts)
    if not n:
        raise SystemExit("no posts in the input")
    audit_date = audit_date or dt.date.today()
    chron = sorted(posts, key=lambda p: p["ts"])
    for p in posts:
        p["hook"], p["cluster"], p["len"] = hook_of(p["caption"]), cluster_of(p), len_bucket(p["caption"])
        p["cta"] = bool(re.search(CTA, p["caption"], re.I))
        p["day"], p["slot"] = p["ts"].weekday(), slot_of(p["ts"].hour)
    base = mean(p["eng"] for p in posts)
    ranked = sorted(posts, key=lambda p: -p["eng"])
    k = max(1, round(n * 0.1))
    top, bottom = ranked[:k], ranked[-k:]
    q = max(1, n // 4)
    topq, botq = {p["id"] for p in ranked[:q]}, {p["id"] for p in ranked[-q:]}

    # STEP 3 snapshot
    snapshot = dict(n=n, avg_likes=None if hidden else mean(p["likes"] or 0 for p in posts), avg_comments=mean(p["comments"] for p in posts),
                    avg_eng=base, median_eng=st.median(p["eng"] for p in posts), likes_hidden=hidden,
                    first=chron[0]["ts"].date().isoformat(), last=chron[-1]["ts"].date().isoformat(),
                    top5=ranked[:5], top10=ranked[:10], trend=trend(chron), types=summarise(group(posts, lambda p: p["type"]), base))
    snapshot["best_type"] = max((t for t in snapshot["types"] if t["n"] >= max(3, n * 0.05)), key=lambda t: t["avg"], default=snapshot["types"][0])

    # STEP 4 what's working
    hooks_all = Counter(p["hook"] for p in posts)
    hooks_top = Counter(p["hook"] for p in top)
    hook_rows = summarise(group(posts, lambda p: p["hook"]), base)
    for r in hook_rows:
        r["share_top"], r["share_all"] = hooks_top[r["name"]] / k * 100, hooks_all[r["name"]] / n * 100
    clusters = summarise(group(posts, lambda p: p["cluster"]), base)
    for c in clusters:
        c["top_post"] = max((p for p in posts if p["cluster"] == c["name"]), key=lambda p: p["eng"])
    lengths = summarise(group(posts, lambda p: p["len"]), base)
    lengths.sort(key=lambda r: [b[0] for b in LEN_BUCKETS].index(r["name"]))
    cta_yes = [p for p in posts if p["cta"]]
    cta_no = [p for p in posts if not p["cta"]]
    cta = dict(yes_n=len(cta_yes), no_n=len(cta_no), yes_avg=mean(p["eng"] for p in cta_yes), no_avg=mean(p["eng"] for p in cta_no))
    cta["lift"] = pct(cta["yes_avg"], cta["no_avg"]) if cta_yes and cta_no else 0

    def share(ps, f):
        return Counter(f(p) for p in ps)
    avoid = []
    feats = [("format", lambda p: p["type"]), ("topic", lambda p: p["cluster"]), ("hook", lambda p: p["hook"]),
             ("caption length", lambda p: p["len"]), ("CTA", lambda p: "with a CTA" if p["cta"] else "without a CTA"),
             ("hashtags", lambda p: "5+ hashtags" if len(p["tags"]) >= 5 else "0-4 hashtags"), ("day", lambda p: DAYS[p["day"]])]
    for label, f in feats:
        sb, sa = share(bottom, f), share(posts, f)
        for v, c in sb.items():
            b_sh, a_sh = c / len(bottom) * 100, sa[v] / n * 100
            if c >= 2 and b_sh - a_sh >= 15:
                avoid.append(dict(feature=label, value=v, bottom_share=b_sh, all_share=a_sh))
    avoid.sort(key=lambda a: -(a["bottom_share"] - a["all_share"]))
    working = dict(top_k=k, hooks=hook_rows, clusters=clusters[:6], all_clusters=clusters, lengths=lengths,
                   best_length=max((r for r in lengths if r["n"] >= 3), key=lambda r: r["avg"], default=lengths[0]),
                   cta=cta, avoid=avoid, bottom=bottom)

    # STEP 5 hashtags
    tagc = Counter(t for p in posts for t in set(p["tags"]))
    tags = []
    for t, c in tagc.most_common():
        ps = [p for p in posts if t in p["tags"]]
        a = mean(p["eng"] for p in ps)
        tags.append(dict(tag=t, n=c, avg=a, index=a / base if base else 1, in_top=sum(p["id"] in topq for p in ps), in_bottom=sum(p["id"] in botq for p in ps)))
    keep = [t for t in tags if t["n"] >= 2 and t["index"] >= 1.0]
    stop = [t for t in tags if t["n"] >= 2 and (t["index"] < 0.8 or (t["in_bottom"] and not t["in_top"]))]
    used = set(tagc)
    themes = [c["name"] for c in clusters if c["name"] in TRY_TAGS]
    try_tags = []
    for th in themes + list(TRY_TAGS):
        for t in TRY_TAGS.get(th, []):
            if t not in used and t not in [x["tag"] for x in try_tags]:
                try_tags.append(dict(tag=t, theme=th))
    hashtags = dict(all=tags, keep=keep[:15], stop=stop, try_=try_tags[:10], per_post=mean(len(p["tags"]) for p in posts),
                    no_tag_avg=mean(p["eng"] for p in posts if not p["tags"]), tag_avg=mean(p["eng"] for p in posts if p["tags"]),
                    no_tag_n=sum(not p["tags"] for p in posts))

    # STEP 6 posting pattern
    cells = defaultdict(list)
    for p in posts:
        cells[(p["day"], p["slot"])].append(p["eng"])
    heat = [[dict(n=len(cells[(d, s)]), avg=mean(cells[(d, s)])) for s in range(len(SLOTS))] for d in range(7)]
    min_n = max(2, round(n * 0.03))
    by_day = summarise(group(posts, lambda p: DAYS[p["day"]]), base)
    by_slot = summarise(group(posts, lambda p: SLOTS[p["slot"]][0]), base)
    best_days = [r for r in by_day if r["n"] >= min_n][:3]
    best_slots = [r for r in by_slot if r["n"] >= min_n][:2]
    weeks = defaultdict(list)
    for p in posts:
        weeks[p["ts"].isocalendar()[:2]].append(p["eng"])
    wk = [(len(v), mean(v)) for v in weeks.values()]
    r = 0.0
    if len(wk) > 2:
        mx, my = mean(a for a, _ in wk), mean(b for _, b in wk)
        sx = sum((a - mx) ** 2 for a, _ in wk) ** .5
        sy = sum((b - my) ** 2 for _, b in wk) ** .5
        r = sum((a - mx) * (b - my) for a, b in wk) / (sx * sy) if sx and sy else 0.0
    freq = defaultdict(list)
    for a, b in wk:
        freq["1-2 posts" if a <= 2 else "3-4 posts" if a <= 4 else "5+ posts"].append(b)
    gaps = defaultdict(list)
    for prev, cur in zip(chron, chron[1:]):
        h = (cur["ts"] - prev["ts"]).total_seconds() / 3600
        gaps["Under 24 h" if h < 24 else "1-3 days" if h < 72 else "3+ days"].append(cur["eng"])
    span_weeks = max(1, (chron[-1]["ts"] - chron[0]["ts"]).days / 7)
    per_week = n / span_weeks
    rec_per_week = max(3, min(5, round(max(per_week, 3))))
    best_freq = max(freq.items(), key=lambda kv: mean(kv[1]))[0] if freq else ""
    sched_days = [r_["name"] for r_ in sorted(by_day, key=lambda r_: -r_["avg"]) if r_["n"] >= min_n][:rec_per_week]
    schedule = []
    for d in sorted(sched_days, key=DAYS.index):
        di = DAYS.index(d)
        row = max(range(len(SLOTS)), key=lambda s: (heat[di][s]["n"] >= 3, heat[di][s]["avg"]))
        if heat[di][row]["n"] < 3:
            row = [s[0] for s in SLOTS].index(best_slots[0]["name"]) if best_slots else 5
        schedule.append(dict(day=d, slot=SLOTS[row][0], hours=f"{SLOTS[row][1]:02d}:00-{SLOTS[row][2]:02d}:00"))
    posting = dict(heat=heat, by_day=by_day, by_slot=by_slot, best_days=best_days, best_slots=best_slots, per_week=per_week,
                   weekly_r=r, freq={k_: dict(n=len(v), avg=mean(v)) for k_, v in freq.items()}, best_freq=best_freq,
                   gaps={k_: dict(n=len(v), avg=mean(v)) for k_, v in gaps.items()}, schedule=schedule, rec_per_week=rec_per_week)

    # STEP 7 sentiment
    def emo(ps):
        texts = [t for p in ps for t in p["comment_texts"]]
        c = Counter(name for t in texts for name, rx in EMOTIONS if re.search(rx, t, re.I))
        return len(texts), {name: c[name] / len(texts) * 100 if texts else 0 for name, _ in EMOTIONS}
    n_all, emo_all = emo(posts)
    n_top, emo_top = emo(top)
    texts = [t for p in posts for t in p["comment_texts"]]
    asks = sorted(((name, sum(bool(re.search(rx, t, re.I)) for t in texts)) for name, rx in ASKS), key=lambda a: -a[1])
    sentiment = dict(n_comments=n_all, n_top_comments=n_top, all=emo_all, top=emo_top, asks=[a for a in asks if a[1]],
                     samples=[t for p in top for t in p["comment_texts"]][:6])

    out = dict(handle=handle, audit_date=audit_date.isoformat(), source=source, demo=demo, limit=limit,
               snapshot=snapshot, working=working, hashtags=hashtags, posting=posting, sentiment=sentiment, posts=posts)
    out["ideas"] = ideas(out)
    out["calendar"] = calendar(out, audit_date)
    return out


# ---------------------------------------------------------------- STEP 8 ideas
def confidence(lift, n):
    if lift >= 25 and n >= 8:
        return "High"
    if lift >= 10 and n >= 4:
        return "Medium"
    return "Low"


def ideas(a):
    s, w, h, ps, se = a["snapshot"], a["working"], a["hashtags"], a["posting"], a["sentiment"]
    cl = {c["name"]: c for c in w["all_clusters"]}
    ty = {t["name"]: t for t in s["types"]}
    hk = {r["name"]: r for r in w["hooks"]}
    best_t, best_len, cta = s["best_type"], w["best_length"], w["cta"]
    ask = dict(se["asks"])
    nc = max(1, se["n_comments"])

    def ask_ev(name):  # share of comments with this ask, scaled so 2.5% of comments counts like a +25% lift
        return ask.get(name, 0) / nc * 1000
    best_day = ps["best_days"][0]["name"] if ps["best_days"] else "Fri"
    fmt = "Reel" if best_t["name"] in ("Reel", "Video") else best_t["name"]

    def c(name):
        return cl.get(name, dict(name=name, n=0, avg=0, lift=0))

    def signal_cluster(name):
        x = c(name)
        return f"{name} average {x['avg']:,.0f} engagements per post ({x['lift']:+.0f}% vs account average, {x['n']} posts)" if x["n"] else f"No {name.lower()} posts in the sample yet: an untested gap"

    reel = ty.get("Reel", dict(avg=0, lift=0, n=0))
    car = ty.get("Carousel", dict(avg=0, lift=0, n=0))
    cands = [
        dict(title="ASMR fabric close-ups", hook="Listen to 400 GSM.", format="Reel", formula="Sensory hook → slow detail → product reveal",
             cluster="Product & craft", why=signal_cluster("Product & craft") + f"; Reels average {reel['lift']:+.0f}% vs account.",
             opener="No music. Just the fabric.", ev=(c("Product & craft")["lift"] + reel["lift"]) / 2, n=c("Product & craft")["n"]),
        dict(title="Drop countdown series", hook="72 hours. One piece. No restock.", format="Reel", formula="Countdown → tease → date and time",
             cluster="Drops & launches", why=signal_cluster("Drops & launches") + f"; urgency hooks average {hk.get('Urgency / scarcity', dict(lift=0))['lift']:+.0f}%; 'next drop dates' asked in {ask.get('Next drop dates', 0)} comments.",
             opener="Three days left before it's gone.", ev=c("Drops & launches")["lift"], n=c("Drops & launches")["n"]),
        dict(title="Collab reveal in three frames", hook="Two names. One drop. Guess who.", format="Carousel", formula="Teaser → reveal → details",
             cluster="Collaborations", why=signal_cluster("Collaborations") + ".", opener="You asked. They answered.",
             ev=c("Collaborations")["lift"], n=c("Collaborations")["n"]),
        dict(title="Styling one piece three ways", hook="One hoodie. Three cities.", format="Carousel" if car["lift"] >= reel["lift"] else "Reel",
             formula="One product → three looks → save prompt", cluster="Culture & community",
             why=f"'More styling / fits' asked in {ask.get('More styling / fits', 0)} of {nc} comments; {'carousels' if car['lift'] >= reel['lift'] else 'Reels'} average {max(car['lift'], reel['lift']):+.0f}% vs account.",
             opener="Save this for your next fit.", ev=ask_ev("More styling / fits"), n=ask.get("More styling / fits", 0)),
        dict(title="Size guide from the comments", hook="What size should I get? Answered.", format="Carousel", formula="Real question → answer → proof (fit on 3 bodies)",
             cluster="Product & craft", why=f"Size and fit questions in {ask.get('Size and fit info', 0)} of {nc} comments.",
             opener="Your most asked question, answered once.", ev=ask_ev("Size and fit info"), n=ask.get("Size and fit info", 0)),
        dict(title="Store-day story experience", hook="This was the queue at 9 am.", format="Reel", formula="Scene → crowd → product moment → invite",
             cluster="Store & events", why=signal_cluster("Store & events") + f"; 'Stores in more cities' asked in {ask.get('Stores in more cities', 0)} comments.",
             opener="Mumbai showed up. Who's next?", ev=c("Store & events")["lift"], n=c("Store & events")["n"]),
        dict(title="Restock alert done right", hook="It's back. For 48 hours.", format="Reel" if fmt == "Reel" else fmt, formula="Proof of demand → return → deadline",
             cluster="Drops & launches", why=f"Restock requests in {ask.get('Restocks', 0)} of {nc} comments; {se['all'].get('Frustration', 0):.0f}% of comments show frustration (sell-outs, bots, price).",
             opener="You kept asking. It's back, briefly.", ev=ask_ev("Restocks"), n=ask.get("Restocks", 0)),
        dict(title="Behind the print", hook="From sketch to screen print in 30 seconds.", format="Reel", formula="Process timelapse → maker → final piece",
             cluster="Product & craft", why=f"Behind-the-scenes or process asked in {ask.get('Behind the scenes', 0)} of {nc} comments; {signal_cluster('Product & craft')}.",
             opener="Every piece starts on paper.", ev=(c("Product & craft")["lift"] + ask_ev("Behind the scenes")) / 2, n=c("Product & craft")["n"]),
        dict(title="Community fit check", hook="You wore it better. Here's proof.", format="Carousel", formula="UGC repost → tag → invite to share",
             cluster="Culture & community", why=signal_cluster("Culture & community") + f"; {se['all'].get('Tags a friend', 0):.0f}% of comments tag a friend.",
             opener="Our favourite fits from you this month.", ev=c("Culture & community")["lift"], n=c("Culture & community")["n"]),
        dict(title="Campaign film cut-downs", hook="The 7 seconds everyone replayed.", format="Reel", formula="Best moment first → context → full film link",
             cluster="Campaign & lookbook", why=signal_cluster("Campaign & lookbook") + f"; {w['best_length']['name'].split(' (')[0].lower()} captions perform best.",
             opener="A moment from the new campaign.", ev=c("Campaign & lookbook")["lift"], n=c("Campaign & lookbook")["n"]),
        dict(title="Price and drop-time FAQ story", hook="Price, sizes, time. Everything before Friday.", format="Static", formula="FAQ → clear facts → reminder CTA",
             cluster="Drops & launches", why=f"Price and availability asked in {ask.get('Price and availability', 0)} of {nc} comments; CTA posts average {cta['lift']:+.0f}% vs no-CTA posts.",
             opener="Everything you need before the drop.", ev=ask_ev("Price and availability"), n=ask.get("Price and availability", 0)),
        dict(title="Prime-time anchor post", hook="The one post to see this week.", format=fmt, formula=f"Best format ({fmt}) at the best slot",
             cluster=w["all_clusters"][0]["name"], why=f"One planned hero post a week in the best slot: {best_day} is the best day by average engagement; {best_t['name']}s are the best format ({best_t['lift']:+.0f}%).", day=best_day,
             opener="This week's main moment.", ev=best_t["lift"], n=best_t["n"]),
    ]
    for x in cands:
        x["confidence"] = confidence(x["ev"], x["n"])
    order = {"High": 0, "Medium": 1, "Low": 2}
    cands.sort(key=lambda x: (order[x["confidence"]], -x["ev"]))
    return cands[:10]


# ---------------------------------------------------------------- STEP 9 calendar
FILLERS = [("Behind the scenes", "Story set from the studio", "Story"), ("Product detail", "Close-up of this week's hero piece", "Carousel"),
           ("Community repost", "Fit of the week from the community", "Story"), ("Poll / question sticker", "Which colourway next?", "Story")]


def calendar(a, audit_date):
    sched = {s["day"]: s for s in a["posting"]["schedule"]}
    ideas_ = list(a["ideas"])
    keep = [t["tag"] for t in a["hashtags"]["keep"][:3]] or ["bluorng"]
    used = {t["tag"] for t in a["hashtags"]["all"]}

    def fresh(theme):
        return " ".join("#" + x for x in [x for x in TRY_TAGS[theme] if x not in used][:3])
    groups = {"A": "Core: " + " ".join("#" + t for t in keep[:3]), "B": "Drop: " + fresh("Drops & launches"),
              "C": "Culture: " + fresh("Culture & community"), "D": "Craft: " + fresh("Product & craft")}
    grp_of = {"Drops & launches": "A + B", "Collaborations": "A + B", "Product & craft": "A + D", "Culture & community": "A + C",
              "Store & events": "A + C", "Campaign & lookbook": "A"}
    rows, fi, ii = [], 0, 0
    start = audit_date + dt.timedelta(days=1)
    slots = [i for i in range(30) if DAYS[(start + dt.timedelta(days=i)).weekday()] in sched]
    spare = max(0, len(slots) - len(ideas_))
    step = len(slots) / spare if spare else 0
    filler_slots = {slots[int(step * j + step / 2)] for j in range(spare)} if spare else set()
    for i in range(30):
        d = start + dt.timedelta(days=i)
        day = DAYS[d.weekday()]
        if day in sched:
            if ii < len(ideas_) and ideas_[ii].get("day") not in (None, day):  # an idea tied to another day waits for it
                j = next((j for j in range(ii + 1, len(ideas_)) if ideas_[j].get("day") in (None, day)), None)
                if j is not None:
                    ideas_[ii], ideas_[j] = ideas_[j], ideas_[ii]
            tied = ii < len(ideas_) and ideas_[ii].get("day") == day
            if ii < len(ideas_) and (i not in filler_slots or tied) and ideas_[ii].get("day") in (None, day):
                x = ideas_[ii]; ii += 1
                rows.append(dict(date=d.isoformat(), day=day, time=sched[day]["hours"], type=x["title"], hook=x["hook"], format=x["format"],
                                 group=grp_of.get(x["cluster"], "A"), kind="idea", confidence=x["confidence"]))
            else:
                f = FILLERS[fi % len(FILLERS)]; fi += 1
                rows.append(dict(date=d.isoformat(), day=day, time=sched[day]["hours"], type=f[0], hook=f[1], format=f[2], group="A", kind="filler", confidence=""))
        else:
            f = FILLERS[(i + 2) % len(FILLERS)]
            rows.append(dict(date=d.isoformat(), day=day, time="", type="Stories only: " + f[0].lower(), hook=f[1], format="Story", group="-", kind="rest", confidence=""))
    return dict(rows=rows, groups=groups)


def load(path):
    data = json.load(open(path))
    return data["items"] if isinstance(data, dict) and "items" in data else data
