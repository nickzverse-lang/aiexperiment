"""DEMO DATA: 150 made-up posts in the apify/instagram-scraper output shape, for testing the pipeline and dashboard
while the real scrape is blocked. These are NOT BLUORNG's numbers. The dashboard shows a DEMO banner when this is used.

Run: python3 tools/bluprint/demo_data.py data/demo_posts.json
"""
import datetime as dt
import json
import math
import random
import sys

R = random.Random(42)
CAPS = {
    "Drops & launches": ["Chapter {n}. Live now on bluorng.com", "New drop. Friday, 8 pm.", "The {p} is out now. Link in bio.",
                         "72 hours to the drop. Set your alarms.", "SS26 capsule. Available now online and in stores.",
                         "Out now: the {p} in three washes. Shop via link in bio.", "Limited run. Only 300 pieces of the {p}."],
    "Collaborations": ["BLUORNG x {c}. Coming this Friday.", "{c} x BLUORNG. The full collection drops tonight at 8 pm.",
                       "Two worlds, one jersey. BLUORNG x {c}.", "In partnership with {c}. Live now."],
    "Campaign & lookbook": ["Campaign: {t}. Shot by {s}.", "The {t} lookbook. Styled by our studio.", "A film about {t}.",
                            "Editorial: {t}, photographed in Old Delhi."],
    "Store & events": ["Mumbai, we're open. See you at the store this weekend.", "The queue at Gurugram this morning.",
                       "Pop-up in Bengaluru, 12-14 Dec. Visit us.", "Flagship store, Delhi. New wall, new pieces."],
    "Product & craft": ["400 GSM. Heavyweight cotton, garment-dyed.", "Detail: hand-placed embroidery on the {p}.",
                        "Close-up. The wash takes 6 hours per piece.", "Crafted in India. Screen print, 5 layers.",
                        "Texture check on the {p}."],
    "Culture & community": ["Spotted: you guys wearing the {p}. Tag us in your fit check.", "Fit check Friday. Tag a friend who'd wear this.",
                            "For the culture.", "Our community, our runway. Repost of the week.", "Meme of the week, you know who you are."],
    "Brand moments": ["BG.", "Thank you for 2025.", "Studio days.", "Back soon.", "Mood."],
}
PRODUCTS = ["Lattice hoodie", "Script tee", "Monogram jacket", "Cargo trousers", "BG varsity", "Washed denim", "Knit polo"]
COLLABS = ["Budweiser", "Jägermeister", "an artist friend", "a football club"]
THEMES = ["Neon Delhi", "After Hours", "Concrete Garden", "Monsoon"]
TAGS = {"Drops & launches": ["newcollection", "limitededition", "streetwear"], "Collaborations": ["collab", "streetwear"],
        "Campaign & lookbook": ["menswear", "fashion"], "Store & events": ["delhi", "mumbai"], "Product & craft": ["oversized", "streetwear"],
        "Culture & community": ["ootd", "streetstyle", "hypebeast"], "Brand moments": ["fashion"]}
BAD_TAGS = ["explorepage", "fyp", "trending", "reels", "viral", "instagood"]
MULT = dict(type={"Reel": 1.35, "Carousel": 1.1, "Image": .8},
            cluster={"Drops & launches": 1.4, "Collaborations": 1.6, "Campaign & lookbook": 1.0, "Store & events": 1.1,
                     "Product & craft": 1.25, "Culture & community": .85, "Brand moments": .7},
            day=[.85, .9, .95, 1.0, 1.2, 1.15, 1.05])
TYPES = {"Drops & launches": [.5, .3, .2], "Collaborations": [.5, .35, .15], "Campaign & lookbook": [.4, .5, .1],
         "Store & events": [.7, .2, .1], "Product & craft": [.6, .3, .1], "Culture & community": [.3, .4, .3], "Brand moments": [.2, .2, .6]}
COMMENTS = {
    "hype": ["🔥🔥🔥", "this is insane", "W drop", "hardest brand in India rn", "unreal 💯", "goated"],
    "desire": ["need this", "take my money", "copping this one", "want the hoodie so bad", "wishlist ✅"],
    "love": ["so clean ❤️", "love the colourway", "aesthetic 🖤", "best one yet"],
    "ask": ["price?", "restock when??", "size guide please", "when is the next drop?", "do you ship to Dubai?", "store in Bangalore when?",
            "how does it fit, true to size?", "link?", "how is the print made?", "more styling videos pls"],
    "frust": ["sold out in 2 mins again 😭", "too expensive bro", "bots got everything", "still waiting for my order"],
    "tag": ["@rahul.s look", "@its.ananya we need this", "@kabir_09 matching?"],
}
CMIX = {"Drops & launches": [3, 3, 1, 4, 2, 1], "Collaborations": [4, 3, 2, 2, 1, 2], "Campaign & lookbook": [2, 1, 4, 1, 0, 1],
        "Store & events": [2, 1, 2, 3, 0, 2], "Product & craft": [2, 3, 3, 3, 0, 1], "Culture & community": [2, 1, 2, 2, 0, 4], "Brand moments": [1, 0, 3, 1, 0, 0]}


def build(n=150, end=dt.datetime(2026, 10, 27, 20, 0, tzinfo=dt.timezone.utc)):
    items, t = [], end
    names = list(MULT["cluster"])
    weights = [22, 9, 14, 12, 16, 18, 9]
    for i in range(n):
        t -= dt.timedelta(hours=R.uniform(20, 70))
        ist_h = R.choices([8, 11, 14, 17, 20, 21, 23], [1, 2, 2, 3, 5, 4, 1])[0]
        ts = (t.astimezone(dt.timezone(dt.timedelta(hours=5, minutes=30))).replace(hour=ist_h, minute=R.randint(0, 59))).astimezone(dt.timezone.utc)
        cl = R.choices(names, weights)[0]
        ty = R.choices(["Reel", "Carousel", "Image"], TYPES[cl])[0]
        cap = R.choice(CAPS[cl]).format(n=R.randint(3, 9), p=R.choice(PRODUCTS), c=R.choice(COLLABS), t=R.choice(THEMES), s="our studio")
        if R.random() < .3:
            cap += "\n\n" + R.choice(["Sizes XS to XXL.", "Available in stores: Delhi, Gurugram, Mumbai.", "Every piece is numbered.",
                                      "Made in small batches. When it's gone, it's gone. Thank you for supporting independent Indian design."]) * R.choice([1, 1, 2])
        tags = ["bluorng"] if R.random() < .55 else []
        tags += R.sample(TAGS[cl], k=R.randint(0, len(TAGS[cl])))
        if R.random() < .2:
            tags += R.sample(BAD_TAGS, k=R.randint(2, 4))
        if tags:
            cap += "\n\n" + " ".join("#" + x for x in tags)
        ist = ts.astimezone(dt.timezone(dt.timedelta(hours=5, minutes=30)))
        m = MULT["type"][ty] * MULT["cluster"][cl] * MULT["day"][ist.weekday()]
        m *= 1.2 if ist.hour in (20, 21) else .85 if ist.hour in (8, 11) else 1.0
        m *= .85 if len(cap) > 250 else 1.08 if 40 < len(cap) <= 120 else 1.0
        m *= .8 if len(tags) >= 5 else 1.0
        m *= .75 if set(tags) & set(BAD_TAGS) else 1.0
        m *= 1 + .18 * (1 - i / n)  # recent posts slightly stronger
        likes = int(7000 * m * math.exp(R.gauss(0, .33)))
        comments = max(3, int(likes * R.uniform(.007, .016) * (1.5 if cl in ("Collaborations", "Drops & launches") else 1)))
        mix = CMIX[cl]
        lc = [dict(text=R.choice(COMMENTS[R.choices(list(COMMENTS), mix)[0]]), ownerUsername=f"user{R.randint(100, 999)}") for _ in range(R.randint(6, 12))]
        code = "".join(R.choice("ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789") for _ in range(11))
        items.append(dict(id=str(3000000000 + i), shortCode=code, url=f"https://www.instagram.com/p/{code}/", caption=cap,
                          hashtags=tags, likesCount=likes, commentsCount=comments, timestamp=ts.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                          type="Video" if ty == "Reel" else "Sidecar" if ty == "Carousel" else "Image",
                          productType="clips" if ty == "Reel" else "carousel_container" if ty == "Carousel" else "feed",
                          videoPlayCount=int(likes * R.uniform(8, 20)) if ty == "Reel" else None, latestComments=lc, ownerUsername="bluorng"))
    return items


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/demo_posts.json"
    json.dump(build(), open(out, "w"), ensure_ascii=False, indent=1)
    print("wrote", out)
