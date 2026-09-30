"""
Auto-discover which clubs played in a league's top flight each season, by
fetching Transfermarkt's competition "startseite" page per saison_id and
parsing its "Clubs - ..." squad table.

Chile's equivalent file (data/raw/clubs_2020_2025.json) was built by hand;
this script does the same job generically for leagues that use a split
Apertura/Clausura format (Uruguay, Paraguay, Peru) -- the Apertura
competition of a given saison_id is used as a proxy for that season's club
universe, since the same clubs play both halves within a year.

Output shape matches clubs_2020_2025.json: {"by_season": {...}, "all_clubs": {...}}
"""
import argparse
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

import league_config

BASE = "https://www.transfermarkt.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
ROOT = league_config.ROOT
CACHE_DIR = os.path.join(ROOT, "data", "raw", "league_season_pages")
DELAY = 1.3

os.makedirs(CACHE_DIR, exist_ok=True)


def fetch(url, cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return f.read()
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(resp.text)
    time.sleep(DELAY)
    return resp.text


def parse_clubs(html):
    soup = BeautifulSoup(html, "html.parser")
    clubs = {}
    for box in soup.select("div.box"):
        h2 = box.select_one("h2")
        if not h2 or not h2.get_text(strip=True).startswith("Clubs"):
            continue
        table = box.select_one("table.items")
        if not table:
            continue
        for row in table.select("tbody > tr"):
            a = row.select_one("td.hauptlink a[href*='/verein/']")
            if not a:
                continue
            href = a.get("href", "")
            m = re.search(r"/verein/(\d+)", href)
            if not m:
                continue
            club_id = m.group(1)
            slug = href.strip("/").split("/")[0]
            name = (a.get("title") or a.get_text(strip=True)).strip()
            clubs[club_id] = {"slug": slug, "name": name}
        break
    return clubs


def main():
    parser = argparse.ArgumentParser()
    league_config.add_league_arg(parser, default="uruguay")
    args = parser.parse_args()

    config = league_config.get(args.league)
    if not config["competition_code"]:
        print(f"League {args.league!r} has no competition_code configured "
              "(its club list is curated by hand, not auto-fetched).", file=sys.stderr)
        sys.exit(1)

    by_season = {}
    all_clubs = {}
    for season in config["seasons"]:
        url = (f"{BASE}/{config['competition_slug']}/startseite/wettbewerb/"
               f"{config['competition_code']}/saison_id/{season}")
        cache_path = os.path.join(CACHE_DIR, f"{args.league}_{season}.html")
        print(f"Fetching {config['country']} season {season}...")
        html = fetch(url, cache_path)
        clubs = parse_clubs(html)
        print(f"  {len(clubs)} clubs found")
        by_season[str(season)] = clubs
        all_clubs.update(clubs)

    out = {"by_season": by_season, "all_clubs": all_clubs}
    with open(config["clubs_path"], "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Done. {len(all_clubs)} distinct clubs across {len(config['seasons'])} seasons -> {config['clubs_path']}")


if __name__ == "__main__":
    main()
