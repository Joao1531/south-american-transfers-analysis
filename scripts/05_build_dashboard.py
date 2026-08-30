"""
Build the final self-contained dashboard HTML from canonical_transfers.json.
Run after 04_consolidate.py. Output: dashboard/index.html
"""
import base64
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
CRESTS_DIR = os.path.join(ROOT, "data", "raw", "crests_sq")
AUDAX_HEAD_CREST = os.path.join(ROOT, "data", "raw", "crests", "6363.png")
OUT = os.path.join(ROOT, "dashboard", "index.html")
AUDAX_CLUB_ID = "6363"

FEE_TYPE_META = {
    "transfer_fee":   {"label": "Transfer fee (paid)",   "slot": 1},
    "loan_fee":       {"label": "Loan (with fee)",       "slot": 2},
    "loan_free":      {"label": "Loan (free)",           "slot": 3},
    "end_of_loan":    {"label": "End of loan",           "slot": 4},
    "free_transfer":  {"label": "Free transfer",         "slot": 5},
    "undisclosed":    {"label": "Undisclosed fee",       "slot": 6},
    "unknown":        {"label": "No club / unknown",     "slot": 7},
    "retired":        {"label": "End of career",         "slot": 8},
    "own_youth":      {"label": "Youth academy",         "slot": 8},
}


def slim(rec):
    return {
        "id": rec["transfer_id"],
        "p": rec["player_name"],
        "pu": rec["player_url"],
        "pos": rec["position"] or "—",
        "nat": rec["nationality"],
        "nat2": rec.get("nationality_2"),
        "dn": rec.get("dual_nationality", False),
        "dob": rec.get("date_of_birth"),
        "ht": rec.get("height_cm"),
        "foot": rec.get("foot"),
        "ag": rec.get("agent"),
        "age": rec["age_at_transfer"],
        "agep": rec["age_at_transfer_precise"],
        "s": rec["season"],
        "d": rec["transfer_date"],
        "f": {
            "id": rec["from_club"].get("club_id"),
            "n": rec["from_club"].get("club_name"),
            "c": rec["from_club"].get("country"),
            "l": rec["from_club"].get("league"),
        },
        "t": {
            "id": rec["to_club"].get("club_id"),
            "n": rec["to_club"].get("club_name"),
            "c": rec["to_club"].get("country"),
            "l": rec["to_club"].get("league"),
        },
        "fs": rec["from_is_chile_pd_scope"],
        "ts": rec["to_is_chile_pd_scope"],
        "ft": rec["fee_type"],
        "ftx": rec["fee_text"],
        "fv": rec["fee_value_eur"],
        "mv": rec["market_value_at_transfer_eur"],
        "cd": rec["remaining_contract_duration"],
        "ced": rec.get("contract_end_date"),
        "cmr": rec.get("contract_months_remaining"),
        "cf": rec["coach_from"],
        "ct": rec["coach_to"],
        "chain": [
            {
                "d": c["date_unformatted"],
                "f": c["from_club"],
                "t": c["to_club"],
                "fee": c["fee_text"],
                "mv": c["market_value_text"],
            }
            for c in rec["subsequent_transfers"]
        ],
        "sc": sellon_slim(rec.get("sellon_clause")),
    }


def sellon_slim(sc):
    if not sc:
        return None
    return {
        "found": bool(sc.get("found")),
        "pct": sc.get("percentage"),
        "type": sc.get("clause_type"),
        "ben": sc.get("beneficiary_club"),
        "cond": sc.get("condition"),
        "url": sc.get("source_url"),
        "q": sc.get("source_quote"),
        "note": sc.get("notes"),
    }


def main():
    canonical = json.load(open(os.path.join(PROC, "canonical_transfers.json"), encoding="utf-8"))
    cmf_map = json.load(open(os.path.join(PROC, "cmf_club_mapping.json"), encoding="utf-8"))

    slim_records = [slim(r) for r in canonical]

    clubs = {}
    for r in canonical:
        for side in (r["from_club"], r["to_club"]):
            cid = side.get("club_id")
            if cid and side.get("club_name"):
                clubs.setdefault(cid, side["club_name"])
    club_list = sorted(clubs.items(), key=lambda kv: kv[1])

    seasons = sorted({r["season"] for r in canonical if r["season"]})
    positions_pt = sorted(set(r["position"] for r in canonical if r["position"]))
    nationalities = sorted(set(r["nationality"] for r in canonical if r["nationality"]))

    data_json = json.dumps(slim_records, ensure_ascii=False, separators=(",", ":"))
    clubs_json = json.dumps(club_list, ensure_ascii=False)
    cmf_json = json.dumps(cmf_map, ensure_ascii=False)
    seasons_json = json.dumps(seasons)
    positions_json = json.dumps(positions_pt, ensure_ascii=False)
    nat_json = json.dumps(nationalities, ensure_ascii=False)
    fee_meta_json = json.dumps(FEE_TYPE_META, ensure_ascii=False)

    scope_ids = json.dumps(sorted(clubs.keys()))

    crests = {}
    if os.path.isdir(CRESTS_DIR):
        for fname in os.listdir(CRESTS_DIR):
            if not fname.endswith(".png"):
                continue
            cid = fname[:-4]
            with open(os.path.join(CRESTS_DIR, fname), "rb") as f:
                crests[cid] = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
    crests_json = json.dumps(crests)

    audax_head_uri = ""
    if os.path.exists(AUDAX_HEAD_CREST):
        with open(AUDAX_HEAD_CREST, "rb") as f:
            audax_head_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
    audax_crest_json = json.dumps(audax_head_uri or crests.get(AUDAX_CLUB_ID, ""))

    template_path = os.path.join(ROOT, "scripts", "dashboard_template.html")
    with open(template_path, encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__DATA_JSON__", data_json)
    html = html.replace("__CLUBS_JSON__", clubs_json)
    html = html.replace("__CMF_JSON__", cmf_json)
    html = html.replace("__SEASONS_JSON__", seasons_json)
    html = html.replace("__POSITIONS_JSON__", positions_json)
    html = html.replace("__NAT_JSON__", nat_json)
    html = html.replace("__FEEMETA_JSON__", fee_meta_json)
    html = html.replace("__CRESTS_JSON__", crests_json)
    html = html.replace("__AUDAX_CREST_URI__", audax_crest_json)
    html = html.replace("__GENERATED_COUNT__", str(len(slim_records)))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard written -> {OUT} ({len(slim_records)} transfers, {len(data_json)/1024:.0f} KB data)")


if __name__ == "__main__":
    main()
