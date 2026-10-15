"""Sample research data for the BLUORNG case study.

This is a SAMPLE STUDY: the 80 survey responses are generated from the distributions below (fixed seed),
and the 10 interviews are written examples of what BLUORNG team members are likely to say. Use it to learn
the method and layout, then replace it with real responses.
"""
import csv
import pathlib
import random
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
N = 80
CONTENT = ["Drop teasers", "Lookbooks, campaign films", "Behind the scenes", "Fabric and detail close-ups",
           "Styling videos", "Street style, fit checks", "Memes, culture", "Collab announcements", "Founder stories"]

# question id -> (text, kind, options, weights, max picks)
SURVEY = [
    ("Q1", "Your age group", "single", ["16–18", "19–22", "23–26", "27–30", "31+"], [8, 34, 33, 18, 7], 1),
    ("Q2", "Which city do you live in?", "single", ["Delhi NCR", "Mumbai", "Bengaluru", "Pune", "Other"], [38, 22, 14, 8, 18], 1),
    ("Q3", "Time you spend on Instagram each day", "single", ["Under 1 hour", "1–2 hours", "2–4 hours", "4+ hours"], [10, 34, 40, 16], 1),
    ("Q4", "Do you follow BLUORNG on Instagram?", "single", ["Yes", "No"], [72, 28], 1),
    ("Q5", "Have you bought from BLUORNG?", "single", ["Yes, more than once", "Yes, once", "Not yet, but I want to", "No"], [14, 18, 38, 30], 1),
    ("Q6", "Where do you discover new streetwear brands? (pick up to 3)", "multi",
     ["Instagram Reels", "Instagram Explore", "Friends", "Creators", "Instagram ads", "Stores, pop-ups", "YouTube", "Reddit, Discord"],
     [80, 42, 44, 46, 26, 16, 14, 8], 3),
    ("Q7", "Which brand content do you enjoy watching most? (pick up to 3)", "multi", CONTENT, [44, 30, 52, 40, 46, 42, 58, 24, 12], 3),
    ("Q8", "Which content do you save or share? (pick up to 3)", "multi", CONTENT, [16, 24, 30, 48, 62, 40, 30, 14, 8], 3),
    ("Q9", "Which content has made you want to buy? (pick up to 3)", "multi", CONTENT, [52, 26, 16, 44, 50, 34, 4, 22, 8], 3),
    ("Q10", "Your favourite format from fashion brands", "single", ["Reels", "Carousels", "Single photos", "Stories"], [52, 28, 8, 12], 1),
    ("Q11", "How often do you notice streetwear ads on Instagram?", "single", ["Many times a day", "Daily", "A few times a week", "Rarely"], [34, 36, 22, 8], 1),
    ("Q12", "What makes you stop scrolling on an ad? (pick up to 2)", "multi",
     ["A real person or creator wearing it", "Close-up of fabric and details", "Drop or limited countdown", "Store or queue hype",
      "Studio model shot", "Price or offer"], [66, 50, 34, 22, 14, 14], 2),
    ("Q13", '"Most streetwear ads on Instagram look the same." (1 = disagree, 5 = agree)', "single", ["1", "2", "3", "4", "5"], [4, 8, 18, 38, 32], 1),
    ("Q14", "What makes you trust a premium brand online? (pick up to 3)", "multi",
     ["Close-up quality shots", "Real people wearing it", "Reviews and comments", "Behind the scenes", "Store presence",
      "Creator collabs", "Founder story", "Consistent aesthetic"], [56, 60, 36, 34, 22, 26, 12, 40], 3),
    ("Q15", "Have you bought something after seeing an Instagram ad?", "single", ["Yes, several times", "Yes, once", "No"], [28, 36, 36], 1),
    ("Q16", "What makes a brand ad feel cheap? (open answer, coded)", "single",
     ["Same ad shown again and again", "Too polished, feels fake", "Discount-heavy", "Low-quality or AI look", "Too much text"], [30, 24, 20, 14, 12], 1),
    ("Q17", "One thing you'd like BLUORNG to post more of (open answer, coded)", "single",
     ["Styling ideas", "Behind the scenes, making", "Fabric and quality details", "Drop and restock info", "Community fits", "Store events"],
     [28, 22, 18, 14, 12, 6], 1),
]


def generate(seed=7):
    rnd = random.Random(seed)
    rows = []
    for i in range(N):
        r = {"respondent": f"R{i + 1:02d}"}
        for qid, _, kind, opts, w, k in SURVEY:
            if kind == "single":
                r[qid] = rnd.choices(opts, weights=w)[0]
            else:
                n = rnd.choices([1, 2, 3][:k], weights=[2, 4, 5][:k])[0]
                pool, ww, picks = list(opts), list(w), []
                for _ in range(n):
                    c = rnd.choices(range(len(pool)), weights=ww)[0]
                    picks.append(pool.pop(c)); ww.pop(c)
                r[qid] = "; ".join(picks)
        rows.append(r)
    return rows


def stats(rows):
    """qid -> list of (option, count, percent of respondents) in option order."""
    out = {}
    for qid, _, kind, opts, _, _ in SURVEY:
        c = Counter()
        for r in rows:
            for v in r[qid].split("; "):
                c[v] += 1
        out[qid] = [(o, c[o], round(c[o] / N * 100)) for o in opts]
    return out


def likert_mean(rows, qid):
    return sum(int(r[qid]) for r in rows) / N


def write_csv(rows, path=ROOT / "docs" / "research" / "survey_responses_sample.csv"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    return path


INTERVIEW_GUIDE = [
    "Walk me through your role during a typical drop.",
    "How does the team decide what content or ad to make?",
    "How do you know whether a post or an ad worked?",
    "Tell me about one ad that did well and one that didn't. Why?",
    "How is a shoot day planned, and what usually gets missed?",
    "How do organic posts and Meta ads connect today?",
    "Where does the most time or money get wasted?",
    "How do you make sure content stays on-brand?",
    "Which tools or data do you use, and what's missing?",
    "If one thing could change tomorrow, what would it be?",
]

# code, role, minutes, [(question no, answer)], quote, tags
INTERVIEWS = [
    ("P1", "Co-founder, Brand Head", 35,
     [(2, "Mostly instinct and the mood of the collection. I approve what feels like BLUORNG."),
      (3, "Sell-through tells me if a drop worked. It doesn't tell me which content did the work."),
      (8, "I reject anything that looks mass-market or discount-led, even if it might convert."),
      (10, "I want to see why the team is proposing something, not just the idea.")],
     "We spend serious money on every drop campaign, and I still can't tell you which piece of content earned it back.",
     ["No proof of what works", "Brand protection", "Approvals by taste"]),
    ("P2", "Marketing Lead", 45,
     [(2, "A planning meeting before each drop. We look at moodboards, competitor pages and last month's top Reels."),
      (3, "Reach and saves for organic, ROAS for ads, but they sit in different places and nobody joins them."),
      (7, "Ad production. We book a full shoot, then only three or four cuts actually run as ads."),
      (10, "Know before the shoot which ad types to make, so the shoot day pays for itself.")],
     "Half of our ad budget goes to formats we picked out of habit.",
     ["No proof of what works", "Spend by habit", "Shoot under-planned"]),
    ("P3", "Performance Marketer, Meta Ads", 40,
     [(3, "Ads Manager shows CTR, CPA and frequency. I can see an ad is dying, not why."),
      (4, "A creator try-on beat our studio lookbook on cost per sale. We had only one creator clip, so we couldn't scale it."),
      (6, "I find out about a great organic Reel days later, by accident."),
      (9, "I check the Meta Ad Library for competitors by hand. It takes hours and I never save what I learn.")],
     "I end up running the same lookbook footage in five crops and calling it testing.",
     ["Too few ad variations", "Organic and paid apart", "Manual competitor study"]),
    ("P4", "Social Media Manager", 40,
     [(2, "Trends, audio, what competitors posted, and what the founders liked last week."),
      (3, "I screenshot Insights into a deck every month. It's a report, not a plan."),
      (7, "Monday mornings. I start the content plan from a blank page every week."),
      (10, "Something that tells me which of our post types to repeat and which to drop.")],
     "I don't need more numbers. I need to know what the numbers mean for next week's posts.",
     ["No proof of what works", "Idea fatigue", "Manual reporting"]),
    ("P5", "Content Strategist, Creative Lead", 35,
     [(2, "I write concepts for each drop, mostly from references and gut feel."),
      (5, "We plan the hero lookbook in detail. Ad versions and extra angles are an afterthought."),
      (8, "We keep a moodboard, but rules about what we never do live in people's heads."),
      (10, "A shared memory of what worked in past drops.")],
     "Every drop we reinvent the wheel because nothing from the last one is written down.",
     ["Shoot under-planned", "No shared memory", "Brand rules unwritten"]),
    ("P6", "Photographer", 30,
     [(5, "I get a shot list the night before, sometimes as a voice note."),
      (6, "Vertical versions for ads are usually requested after we wrap."),
      (7, "Re-shoots for one missing angle. A whole half-day for two images."),
      (10, "Know every format and ad angle before I set up the first light.")],
     "If I knew the ad angles before the shoot, I could get three times the usable content from the same day.",
     ["Shoot under-planned", "Briefs over chat", "Re-shoots"]),
    ("P7", "Video Editor", 30,
     [(5, "Briefs come as a voice note and a Pinterest link."),
      (6, "I cut the organic Reel first. Ads get whatever is left over."),
      (7, "Re-edits when feedback arrives late at night on WhatsApp."),
      (9, "Drive folders and WhatsApp. No single place for briefs or versions.")],
     "I make the same edit in four ratios at the end because nobody asked for them at the start.",
     ["Briefs over chat", "Late feedback", "Organic and paid apart"]),
    ("P8", "Graphic Designer", 25,
     [(2, "I get asked for story and post graphics once the shoot is done."),
      (8, "Brand rules are a feeling. I learn them when something gets rejected."),
      (7, "Rounds of changes because the goal of a post wasn't clear."),
      (10, "A clear goal and reference for each piece before I start.")],
     "Half my revisions happen because nobody wrote down what the post was supposed to do.",
     ["Brand rules unwritten", "Late feedback", "Unclear goals"]),
    ("P9", "E-commerce Manager", 25,
     [(3, "I see which products sell after a post, but that data never reaches the content team."),
      (6, "Ads point to the site; organic posts mostly don't."),
      (7, "Paid traffic that bounces because the ad promised a different product feel."),
      (10, "Connect what sells on the site with what we post.")],
     "The website knows what people buy. The content team never sees it.",
     ["Signals not shared", "Organic and paid apart"]),
    ("P10", "Retail Store Manager, Mumbai", 20,
     [(3, "Customers walk in showing me a Reel on their phone. That's how I know it worked."),
      (6, "Store events get posted, but rarely promoted as ads."),
      (8, "In-store, people trust what they can touch. Online they need close-ups to feel it."),
      (10, "Tell the content team what customers ask about in store.")],
     "People come in holding their phone with our Reel open. That feedback never goes back to the team.",
     ["Signals not shared", "Proof of quality"]),
]

THEMES = [  # theme, number of the 10 team interviews that raised it
    ("No clear view of what works", 9), ("Fear of looking off-brand", 8), ("Shoot day under-planned for ads", 7),
    ("Briefs and feedback over WhatsApp", 7), ("Ad spend follows habit", 6), ("Organic and paid planned apart", 6),
    ("Idea fatigue before drops", 6), ("Competitor study is manual", 5), ("Slow, taste-based approvals", 5),
    ("Store and site signals not shared", 3),
]


if __name__ == "__main__":
    rows = generate()
    print(write_csv(rows))
    for q, v in stats(rows).items():
        print(q, v)
    print("Q13 mean", likert_mean(rows, "Q13"))
