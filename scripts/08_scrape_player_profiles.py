"""
Scrape Transfermarkt player profile pages for bio fields not captured by the
club-transfer-table scrape: height, preferred foot, date of birth, player
agent, and citizenship(s) (a player with more than one flag listed has dual
nationality -- relevant for the foreign-player quota).

Polite scraping: disk cache per page, ~1.3s delay between live requests,
identifying User-Agent, single-threaded. Reuses the same conventions as
01_scrape_club_transfers.py.
"""
import argparse
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup

import league_config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
ROOT = league_config.ROOT
RAW_DIR = os.path.join(ROOT, "data", "raw", "player_profiles")
DELAY = 1.3

os.makedirs(RAW_DIR, exist_ok=True)


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


def parse_height_cm(text):
    # "1,84 m" -> 184
    m = re.search(r"(\d+),(\d+)\s*m", text)
    if not m:
        return None
    return int(m.group(1)) * 100 + int(m.group(2))


def parse_dob(a_tag_text):
    # "24/01/2004 (22)" -> "2004-01-24"
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", a_tag_text)
    if not m:
        return None
    d, mo, y = m.groups()
    return f"{y}-{mo}-{d}"


def parse_profile(html):
    soup = BeautifulSoup(html, "html.parser")
    box = soup.select_one("div.spielerdatenundfakten .info-table")
    result = {
        "height_cm": None,
        "foot": None,
        "date_of_birth": None,
        "agent": None,
        "nationalities": [],
    }
    if not box:
        return result

    spans = box.find_all("span", recursive=False)
    # Labels and values alternate as direct-child spans; pair them up.
    i = 0
    while i < len(spans) - 1:
        label = spans[i].get_text(" ", strip=True).rstrip(":")
        value_el = spans[i + 1]
        if label == "Height":
            result["height_cm"] = parse_height_cm(value_el.get_text(" ", strip=True))
        elif label == "Foot":
            foot = value_el.get_text(" ", strip=True).lower()
            result["foot"] = foot if foot and foot != "-" else None
        elif label == "Date of birth/Age":
            a = value_el.select_one("a")
            result["date_of_birth"] = parse_dob(a.get_text(" ", strip=True) if a else value_el.get_text(" ", strip=True))
        elif label == "Player agent":
            a = value_el.select_one("a")
            if a:
                result["agent"] = a.get_text(" ", strip=True)
        elif label == "Citizenship":
            flags = value_el.select("img.flaggenrahmen")
            result["nationalities"] = [f.get("title") for f in flags if f.get("title")]
        i += 2
    return result


def main():
    parser = argparse.ArgumentParser()
    league_config.add_league_arg(parser)
    args = parser.parse_args()
    config = league_config.get(args.league)
    canon_path = os.path.join(config["processed_dir"], "canonical_transfers.json")
    out_path = os.path.join(config["processed_dir"], "player_profiles.json")

    canon = json.load(open(canon_path, encoding="utf-8"))
    players = {}
    for r in canon:
        players[r["player_id"]] = r["player_url"]
    print(f"{len(players)} unique players to fetch")

    profiles = {}
    if os.path.exists(out_path):
        profiles = json.load(open(out_path, encoding="utf-8"))

    todo = [(pid, url) for pid, url in players.items() if pid not in profiles]
    print(f"{len(todo)} remaining (resuming from {len(profiles)} already done)")

    for n, (pid, url) in enumerate(todo, 1):
        cache_path = os.path.join(RAW_DIR, f"{pid}.html")
        try:
            html = fetch(url, cache_path)
            profiles[pid] = parse_profile(html)
        except Exception as e:
            print(f"  [{n}/{len(todo)}] FAILED player_id={pid} url={url}: {e}")
            profiles[pid] = {"height_cm": None, "foot": None, "date_of_birth": None,
                              "agent": None, "nationalities": [], "error": str(e)}
        if n % 50 == 0 or n == len(todo):
            print(f"  [{n}/{len(todo)}] done, saving checkpoint...")
            json.dump(profiles, open(out_path, "w", encoding="utf-8"), ensure_ascii=False)

    json.dump(profiles, open(out_path, "w", encoding="utf-8"), ensure_ascii=False)
    with_height = sum(1 for p in profiles.values() if p.get("height_cm"))
    with_agent = sum(1 for p in profiles.values() if p.get("agent"))
    dual_nat = sum(1 for p in profiles.values() if len(p.get("nationalities") or []) > 1)
    print(f"Player profiles written -> {out_path}")
    print(f"  total players: {len(profiles)}")
    print(f"  with height: {with_height}")
    print(f"  with agent: {with_agent}")
    print(f"  with dual/multi nationality: {dual_nat}")


if __name__ == "__main__":
    main()
