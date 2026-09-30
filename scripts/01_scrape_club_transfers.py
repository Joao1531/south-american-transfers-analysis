"""
Scrape Transfermarkt club transfer pages (arrivals + departures) for every
club that played in the Chilean Primera Division between 2020 and 2025.

Polite scraping: disk cache per page, ~1.3s delay between live requests,
identifying User-Agent, single-threaded.
"""
import argparse
import json
import os
import re
import time
import sys
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
RAW_DIR = os.path.join(ROOT, "data", "raw", "club_transfers")
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


def parse_fee(cell):
    text = cell.get_text(" ", strip=True)
    a = cell.select_one("a")
    transfer_id = None
    if a and "transfer_id" in a.get("href", ""):
        m = re.search(r"transfer_id/(\d+)", a["href"])
        if m:
            transfer_id = m.group(1)

    low = text.lower()
    fee_type = "unknown"
    fee_value_eur = None

    if "loan fee" in low:
        fee_type = "loan_fee"
    elif "loan" in low and "end of loan" not in low:
        fee_type = "loan_free"
    elif "end of loan" in low:
        fee_type = "end_of_loan"
    elif "free transfer" in low:
        fee_type = "free_transfer"
    elif "free" in low:
        fee_type = "free_transfer"
    elif "-" == text.strip():
        fee_type = "unknown"
    elif "?" in text:
        fee_type = "undisclosed"
    elif "retired" in low:
        fee_type = "retired"
    elif "youth" in low or "own youth" in low:
        fee_type = "own_youth"
    elif "€" in text:
        fee_type = "transfer_fee"

    m = re.search(r"€\s*([\d.,]+)\s*(k|m)?", text, re.IGNORECASE)
    if m:
        num = float(m.group(1).replace(",", "."))
        suffix = (m.group(2) or "").lower()
        if suffix == "m":
            fee_value_eur = num * 1_000_000
        elif suffix == "k":
            fee_value_eur = num * 1_000
        else:
            fee_value_eur = num

    return {
        "fee_text": text,
        "fee_type": fee_type,
        "fee_value_eur": fee_value_eur,
        "transfer_id": transfer_id,
    }


def parse_club_cell(cell):
    a_tags = cell.select("table.inline-table a")
    club_name, club_url, club_id, league_name, league_url, country = (None,) * 6
    if a_tags:
        first = a_tags[0]
        img = first.select_one("img")
        # Prefer the crest's alt text: Transfermarkt's "Without Club" pseudo-club
        # renders its <a title="..."> doubled ("Without ClubWithout Club"), but
        # the <img alt="..."> on the same link is clean.
        club_name = (img.get("alt") if img else None) or first.get("title") or first.get_text(strip=True)
        club_url = first.get("href")
        m = re.search(r"/verein/(\d+)", club_url or "")
        club_id = m.group(1) if m else None
        # Row 0 = club (image + name, both linking to /verein/), row 1 = league (flag + link).
        rows = cell.select("table.inline-table tr")
        if len(rows) > 1:
            league_a = rows[1].select_one("a")
            if league_a:
                league_name = league_a.get_text(strip=True)
                league_url = league_a.get("href")
    flag = cell.select_one("img.flaggenrahmen")
    if flag:
        country = flag.get("title")
    # "Without Club" case
    if not club_name:
        txt = cell.get_text(strip=True)
        club_name = txt or None
    return {
        "club_id": club_id,
        "club_name": club_name,
        "club_url": club_url,
        "league_name": league_name,
        "country": country,
    }


def parse_transfer_table(table, direction):
    records = []
    for row in table.select("tbody > tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 6:
            continue
        pos_td = cells[0]
        pos_class = " ".join(pos_td.get("class", []))

        player_cell = cells[1]
        player_a = player_cell.select_one("a[href*='/profil/spieler/']")
        if not player_a:
            continue
        player_name = player_a.get_text(strip=True)
        player_url = player_a.get("href")
        m = re.search(r"/spieler/(\d+)", player_url)
        player_id = m.group(1) if m else None
        pos_rows = player_cell.select("table.inline-table tr")
        position = pos_rows[1].get_text(strip=True) if len(pos_rows) > 1 else None

        age = cells[2].get_text(strip=True)
        nat_img = cells[3].select_one("img")
        nationality = nat_img.get("title") if nat_img else None

        counterpart = parse_club_cell(cells[4])
        fee = parse_fee(cells[5])

        records.append({
            "direction": direction,
            "player_id": player_id,
            "player_name": player_name,
            "player_url": BASE + player_url if player_url else None,
            "position": position,
            "position_class": pos_class,
            "age_at_transfer": age,
            "nationality": nationality,
            "counterpart_club_id": counterpart["club_id"],
            "counterpart_club_name": counterpart["club_name"],
            "counterpart_league": counterpart["league_name"],
            "counterpart_country": counterpart["country"],
            **fee,
        })
    return records


def scrape_club_season(club_id, slug, season, club_name):
    url = f"{BASE}/{slug}/transfers/verein/{club_id}/saison_id/{season}"
    cache_path = os.path.join(RAW_DIR, f"{club_id}_{season}.html")
    try:
        html = fetch(url, cache_path)
    except Exception as e:
        print(f"  ERROR {club_name} {season}: {e}", file=sys.stderr)
        return []
    soup = BeautifulSoup(html, "html.parser")
    boxes = soup.select("div.box")
    out = []
    for box in boxes:
        header = box.select_one("h2.content-box-headline")
        if not header:
            continue
        htext = header.get_text(strip=True)
        table = box.select_one("table")
        if not table:
            continue
        if htext == "Arrivals":
            recs = parse_transfer_table(table, "in")
        elif htext == "Departures":
            recs = parse_transfer_table(table, "out")
        else:
            continue
        for r in recs:
            r["club_id"] = club_id
            r["club_name"] = club_name
            r["season"] = season
        out.extend(recs)
    return out


def main():
    parser = argparse.ArgumentParser()
    league_config.add_league_arg(parser)
    args = parser.parse_args()
    config = league_config.get(args.league)
    out_path = os.path.join(config["processed_dir"], "transfers_raw.json")
    os.makedirs(config["processed_dir"], exist_ok=True)

    clubs = json.load(open(config["clubs_path"], encoding="utf-8"))
    all_records = []
    pairs = []
    for season, season_clubs in clubs["by_season"].items():
        for cid, info in season_clubs.items():
            pairs.append((cid, info["slug"], int(season), info["name"]))
    pairs.sort(key=lambda x: (x[3], x[2]))

    print(f"Scraping {len(pairs)} club-season transfer pages...")
    for i, (cid, slug, season, name) in enumerate(pairs, 1):
        print(f"[{i}/{len(pairs)}] {name} {season}")
        recs = scrape_club_season(cid, slug, season, name)
        all_records.extend(recs)
        if i % 10 == 0:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(all_records, f, ensure_ascii=False, indent=2)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Done. {len(all_records)} transfer records -> {out_path}")


if __name__ == "__main__":
    main()
