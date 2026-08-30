"""
Fetch small crest images for every club that appears anywhere in
canonical_transfers.json (not just the 25 in-scope Chilean clubs), so the
dashboard table/charts can show a logo for opponents too (Boca Juniors,
River Plate, Belgrano, etc.) without bloating the file -- uses the
"smallquad" (30x30, ~2KB) Transfermarkt crest variant.
"""
import json
import os
import time
import requests

BASE = "https://img.a.transfermarkt.technology/wappen/smallquad"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "raw", "crests_sq")
CANONICAL = os.path.join(ROOT, "data", "processed", "canonical_transfers.json")
DELAY = 0.3
SKIP_IDS = {"515"}  # Transfermarkt's "Without Club" pseudo-entity


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    canonical = json.load(open(CANONICAL, encoding="utf-8"))
    club_ids = set()
    for r in canonical:
        for side in (r["from_club"], r["to_club"]):
            cid = side.get("club_id")
            if cid and cid not in SKIP_IDS:
                club_ids.add(cid)

    print(f"Fetching smallquad crests for {len(club_ids)} distinct clubs...")
    ok = fail = cached = 0
    for i, cid in enumerate(sorted(club_ids), 1):
        path = os.path.join(OUT_DIR, f"{cid}.png")
        if os.path.exists(path):
            cached += 1
            continue
        try:
            resp = requests.get(f"{BASE}/{cid}.png", headers=HEADERS, timeout=15)
            resp.raise_for_status()
            with open(path, "wb") as f:
                f.write(resp.content)
            ok += 1
        except Exception as e:
            print(f"  FAIL {cid}: {e}")
            fail += 1
        if i % 50 == 0:
            print(f"[{i}/{len(club_ids)}]")
        time.sleep(DELAY)

    print(f"Done. ok={ok} cached={cached} fail={fail} -> {OUT_DIR}")


if __name__ == "__main__":
    main()
