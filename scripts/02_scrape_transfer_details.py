"""
Enrich each transfer record with its Transfermarkt "transfer details" page:
market value at time of transfer, age at time of transfer (precise),
remaining contract duration, coaches/managers involved.

URL pattern: /jumplist/transfers/spieler/{player_id}/transfer_id/{transfer_id}
Static HTML (no JS rendering needed).
"""
import json
import os
import re
import time
import sys
import requests
from bs4 import BeautifulSoup

BASE = "https://www.transfermarkt.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw", "transfer_details")
OUT_PATH = os.path.join(ROOT, "data", "processed", "transfer_details.json")
TRANSFERS_PATH = os.path.join(ROOT, "data", "processed", "transfers_raw.json")
DELAY = 1.1

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


def parse_eur(text):
    m = re.search(r"€\s*([\d.,]+)\s*(k|m)?", text, re.IGNORECASE)
    if not m:
        return None
    num = float(m.group(1).replace(",", "."))
    suffix = (m.group(2) or "").lower()
    if suffix == "m":
        return num * 1_000_000
    if suffix == "k":
        return num * 1_000
    return num


def parse_detail_page(html):
    soup = BeautifulSoup(html, "html.parser")
    box = soup.select_one("div.box")
    if not box:
        return {}
    rows = box.select("div.data-header__details, table tr, div.info-table__content")
    text = box.get_text("\n", strip=True)
    lines = [l for l in text.split("\n") if l]

    out = {
        "market_value_at_transfer_eur": None,
        "age_at_transfer_precise": None,
        "remaining_contract_duration": None,
        "coach_from": None,
        "coach_to": None,
        "manager_from": None,
        "manager_to": None,
        "competition": None,
        "league_type": None,
    }

    def value_after(label):
        for i, l in enumerate(lines):
            if l == label and i + 1 < len(lines):
                return lines[i + 1]
        return None

    mv = value_after("Market value at time of transfer")
    if mv:
        out["market_value_at_transfer_eur"] = parse_eur(mv)

    age = value_after("Age at time of transfer")
    if age:
        out["age_at_transfer_precise"] = age

    contract = value_after("Remaining contract duration at " + lines[1]) if len(lines) > 1 else None
    for i, l in enumerate(lines):
        if l.startswith("Remaining contract duration"):
            if i + 1 < len(lines):
                out["remaining_contract_duration"] = lines[i + 1]
            break

    comp = value_after("Competition")
    if comp:
        out["competition"] = comp
    lt = value_after("League type")
    if lt:
        out["league_type"] = lt

    # Coach (from) / Manager (to) block: two "Coach"/"Manager" labels can appear
    coach_idx = [i for i, l in enumerate(lines) if l == "Coach"]
    manager_idx = [i for i, l in enumerate(lines) if l == "Manager"]
    if coach_idx:
        i = coach_idx[0]
        if i - 1 >= 0:
            out["coach_from"] = lines[i - 1]
        if i + 1 < len(lines):
            out["coach_to"] = lines[i + 1]
    if manager_idx:
        i = manager_idx[0]
        if i - 1 >= 0:
            out["manager_from"] = lines[i - 1]
        if i + 1 < len(lines):
            out["manager_to"] = lines[i + 1]

    return out


def main():
    transfers = json.load(open(TRANSFERS_PATH, encoding="utf-8"))
    seen = {}
    for r in transfers:
        tid = r.get("transfer_id")
        pid = r.get("player_id")
        if tid and pid and tid not in seen:
            seen[tid] = pid

    items = list(seen.items())
    print(f"Fetching {len(items)} unique transfer-detail pages...")
    results = {}
    if os.path.exists(OUT_PATH):
        results = json.load(open(OUT_PATH, encoding="utf-8"))

    for i, (tid, pid) in enumerate(items, 1):
        if tid in results:
            continue
        url = f"{BASE}/jumplist/transfers/spieler/{pid}/transfer_id/{tid}"
        cache_path = os.path.join(RAW_DIR, f"{tid}.html")
        try:
            html = fetch(url, cache_path)
            results[tid] = parse_detail_page(html)
        except Exception as e:
            print(f"  ERROR transfer_id={tid}: {e}", file=sys.stderr)
            results[tid] = {"error": str(e)}
        if i % 50 == 0:
            print(f"[{i}/{len(items)}]")
            with open(OUT_PATH, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Done. {len(results)} transfer details -> {OUT_PATH}")


if __name__ == "__main__":
    main()
