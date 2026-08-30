"""
Fetch each unique player's FULL career transfer history from Transfermarkt's
internal JSON endpoint. This lets us detect subsequent transfers -- e.g. a
player who moved to Club X in 2022 and was later sold from X to Y -- which
matters for resale-value / sell-on context.

Endpoint: /ceapi/transferHistory/list/{player_id}  (JSON, no HTML parsing)
"""
import json
import os
import time
import sys
import requests

BASE = "https://www.transfermarkt.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw", "player_history")
OUT_PATH = os.path.join(ROOT, "data", "processed", "player_transfer_history.json")
TRANSFERS_PATH = os.path.join(ROOT, "data", "processed", "transfers_raw.json")
DELAY = 1.1

os.makedirs(RAW_DIR, exist_ok=True)


def fetch(player_id):
    cache_path = os.path.join(RAW_DIR, f"{player_id}.json")
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)
    url = f"{BASE}/ceapi/transferHistory/list/{player_id}"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    time.sleep(DELAY)
    return data


def main():
    transfers = json.load(open(TRANSFERS_PATH, encoding="utf-8"))
    player_ids = sorted({r["player_id"] for r in transfers if r.get("player_id")})

    results = {}
    if os.path.exists(OUT_PATH):
        results = json.load(open(OUT_PATH, encoding="utf-8"))

    print(f"Fetching full transfer history for {len(player_ids)} unique players...")
    for i, pid in enumerate(player_ids, 1):
        if pid in results:
            continue
        try:
            data = fetch(pid)
            results[pid] = data.get("transfers", [])
        except Exception as e:
            print(f"  ERROR player_id={pid}: {e}", file=sys.stderr)
            results[pid] = {"error": str(e)}
        if i % 100 == 0:
            print(f"[{i}/{len(player_ids)}]")
            with open(OUT_PATH, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False)
    print(f"Done. {len(results)} players -> {OUT_PATH}")


if __name__ == "__main__":
    main()
