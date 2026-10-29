"""STEP 1 + 2: scrape an Instagram profile's latest posts with Apify's official Instagram Scraper.

Actor: apify/instagram-scraper (official, maintained by Apify). Works on public profiles without an Instagram login
and returns per post: caption, hashtags, likesCount, commentsCount, timestamp, type (Image / Video / Sidecar),
productType ("clips" for Reels), videoViewCount, latestComments, url.

Run:  APIFY_TOKEN=... python3 tools/bluprint/fetch_apify.py bluorng 150 data/bluorng_posts.json
Needs api.apify.com allowed in the network settings. Without it, run the same actor in the Apify Console with the
input printed by --print-input, export the dataset as JSON, and pass that file to analyze/dashboard instead.
"""
import json
import os
import sys
import time
import urllib.request

ACTOR = "apify~instagram-scraper"
API = "https://api.apify.com/v2"


def actor_input(handle, limit):
    return {"directUrls": [f"https://www.instagram.com/{handle}/"], "resultsType": "posts",
            "resultsLimit": limit, "addParentData": False}


def call(method, path, token, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def scrape(handle, limit, token):
    run = call("POST", f"/acts/{ACTOR}/runs", token, actor_input(handle, limit))["data"]
    print("started run", run["id"])
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(10)
        run = call("GET", f"/actor-runs/{run['id']}", token)["data"]
        print("  status", run["status"])
    if run["status"] != "SUCCEEDED":
        sys.exit(f"run ended with status {run['status']}")
    return call("GET", f"/datasets/{run['defaultDatasetId']}/items?clean=true&format=json", token)


if __name__ == "__main__":
    if "--print-input" in sys.argv:
        print(json.dumps(actor_input(sys.argv[2] if len(sys.argv) > 2 else "bluorng", 150), indent=2))
        sys.exit()
    handle, limit, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    token = os.environ.get("APIFY_TOKEN") or sys.exit("set APIFY_TOKEN")
    items = [i for i in scrape(handle, limit, token) if not i.get("error")]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump(items, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"scraped {len(items)} posts (asked for {limit}) -> {out}")
