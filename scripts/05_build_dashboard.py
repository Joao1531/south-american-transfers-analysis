"""
Build the self-contained dashboard HTML from canonical_transfers.json.
Run after 04_consolidate.py.

  python 05_build_dashboard.py                 -> dashboard/index.html, all four leagues merged
  python 05_build_dashboard.py --league peru   -> dashboard/peru/index.html, single league
  python 05_build_dashboard.py --lang es       -> same pages in Spanish (index_es.html)

A transfer that touches two tracked leagues (e.g. Uruguay -> Chile) appears in
both leagues' canonical files under the same transfer_id; in the merged
dashboard it is kept once, carrying the league of each side (`fl` / `tl`).
"""
import argparse
import base64
import json
import os

import i18n_es
import league_config

ROOT = league_config.ROOT
CRESTS_DIR = os.path.join(ROOT, "data", "raw", "crests_sq")
AUDAX_HEAD_CREST = os.path.join(ROOT, "data", "raw", "crests", "6363.png")
AUDAX_CLUB_ID = "6363"
FLAGS_DIR = os.path.join(ROOT, "data", "raw", "flags")

FEE_TYPE_META = {
    "transfer_fee":   {"label": "Transfer fee (paid)",   "slot": 1},
    "loan_fee":       {"label": "Loan (with fee)",       "slot": 2},
    "loan_free":      {"label": "Loan (free)",           "slot": 3},
    "end_of_loan":    {"label": "End of loan",           "slot": 4},
    "free_transfer":  {"label": "Free transfer",         "slot": 5},
    "unknown":        {"label": "No club / unknown",     "slot": 7},
    "retired":        {"label": "End of career",         "slot": 8},
    "own_youth":      {"label": "Youth academy",         "slot": 8},
}


def dashboard_fee_type(rec):
    # Transfermarkt's "?" fee (undisclosed) is treated as a free transfer.
    return "free_transfer" if rec["fee_type"] == "undisclosed" else rec["fee_type"]


def scope_keys(league):
    if league == "chile":
        return "season_chile", "from_is_chile_pd_scope", "to_is_chile_pd_scope"
    return "season_league", "from_is_league_scope", "to_is_league_scope"


def load_league(league):
    """Load one league's canonical transfers, normalising its scope/season keys."""
    config = league_config.get(league)
    season_key, from_key, to_key = scope_keys(league)
    path = os.path.join(config["processed_dir"], "canonical_transfers.json")
    with open(path, encoding="utf-8") as f:
        recs = json.load(f)
    for r in recs:
        r["_s"] = r[season_key]
        r["_fl"] = config["code"] if r[from_key] else None
        r["_tl"] = config["code"] if r[to_key] else None
    return recs


def _empty(v):
    return v is None or v == "" or v == []


def merge_leagues(datasets):
    """One record per transfer_id. Earlier datasets win; later ones only fill gaps
    (e.g. a sell-on clause, or a club's league name) and add their scope flags."""
    by_id = {}
    for recs in datasets:
        for r in recs:
            cur = by_id.get(r["transfer_id"])
            if cur is None:
                by_id[r["transfer_id"]] = r
                continue
            for k, v in r.items():
                if k in ("from_club", "to_club"):
                    for kk, vv in (v or {}).items():
                        if _empty(cur[k].get(kk)) and not _empty(vv):
                            cur[k][kk] = vv
                elif k in ("_fl", "_tl"):
                    if cur[k] is None:
                        cur[k] = v
                elif _empty(cur.get(k)) and not _empty(v):
                    cur[k] = v
    merged = list(by_id.values())
    merged.sort(key=lambda r: (r["transfer_date"] or "", r["player_name"]))
    return merged


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
        "s": rec["_s"],
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
        "fl": rec["_fl"],
        "tl": rec["_tl"],
        "ft": dashboard_fee_type(rec),
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


CHILE_UNIVERSE_EXTRA = " (includes clubs later relegated, e.g. Melipilla, Curicó Unido, Santiago Wanderers, Magallanes)"

SELLON_LI = ('<li><b>Sell-on / buy-back / purchase-option clauses</b>{scope} (expand a row to see; '
             'flagged with <span class="clause-badge" style="margin-left:0">%</span> next to the '
             'fee when confirmed, or <span class="clause-badge unknown" style="margin-left:0">?</span> '
             'when researched but nothing was found): Transfermarkt does not publish this data at all, '
             'so it was gathered through targeted press research (Chile, Argentina, Brazil, Europe) for '
             'the 117 transfers that had an actual fee paid — the only ones where this kind of clause '
             'tends to get reported. Only percentages/terms explicitly stated by a source were recorded, '
             'never estimated; we confirmed a clause in 57 of the 117 cases (49%). Every confirmed clause '
             'carries a source link and a verifiable quote. Where two sources disagreed on the exact '
             "figure, that's flagged in the record's own notes.</li>")

CMF_LI = ("<li><b>CMF Chile:</b> most Chilean clubs are incorporated as S.A.D.P. (professional sports "
          "corporations) and report to Chile's Comisión para el Mercado Financiero; Colo-Colo and "
          "Universidad de Chile are run by publicly listed companies (Blanco y Negro S.A. and Azul Azul "
          "S.A.) regulated as securities issuers instead. These filings contain aggregate annual "
          "financial statements, not per-transfer data — useful as a club-level financial cross-check, "
          "not as a transfer database.</li>")

SELLON_FILTER = ('<div class="field">\n      <label>Clauses</label>\n      '
                 '<label class="checkbox-field"><input type="checkbox" id="f-clause"> '
                 'Only confirmed sell-on / buy-back clauses{scope}</label>\n    </div>')


def build_copy(configs, scope_counts):
    """Page copy. A single-league build keeps the original per-league wording;
    a multi-league build names every league."""
    multi = len(configs) > 1
    any_sellon = any(c["has_sellon"] for c in configs)
    any_cmf = any(c["has_cmf"] for c in configs)
    sellon_scope = " (Chile only)" if multi and any_sellon else ""

    if not multi:
        c = configs[0]
        adj, label, n = c["country_adj"], c["league_label"], scope_counts[c["code"]]
        title = f"{adj} Transfer Market 2020–2026"
        h1 = f"{label} Transfer Market"
        subtitle = f"Every domestic and international transfer involving a {adj} top-flight club, 2020–2026 (through Aug 2026)"
        scope = f"{n} clubs that played in the {label} between 2020 and 2026"
        if c["country"] == "Chile":
            universe = ("<li>Universe: the 25 clubs that played in the Chilean Primera División in at least "
                        f"one season between 2020 and 2026{CHILE_UNIVERSE_EXTRA}.</li>")
        else:
            universe = (f"<li>Universe: the {n} clubs that played in the {adj} {label} in at least one season "
                        "between 2020 and 2026 (includes clubs promoted or relegated during the period).</li>")
    else:
        names = [c["country"] for c in configs]
        listed = ", ".join(names[:-1]) + f" and {names[-1]}"
        title = "South American Transfer Market 2020–2026"
        h1 = "South American Transfer Market"
        subtitle = (f"Every domestic and international transfer involving a top-flight club in {listed}, "
                    "2020–2026 (through Aug 2026)")
        scope = f"{sum(scope_counts.values())} clubs that played in the top flight of {listed} between 2020 and 2026"
        items = []
        for c in configs:
            extra = CHILE_UNIVERSE_EXTRA if c["country"] == "Chile" else ""
            items.append(f"{c['country']}: the {scope_counts[c['code']]} clubs that played in the "
                         f"{c['country_adj']} {c['league_label']}{extra}")
        universe = ("<li>Universe: every club that played in the top flight of each league in at least one season "
                    "between 2020 and 2026 (clubs promoted or relegated during the period are included) — "
                    + "; ".join(items) + ".</li>"
                    "<li>A transfer between two clubs of different tracked leagues (e.g. Uruguay → Chile) is one "
                    "record, counted in both leagues' views. Use the League filter to see a single league's market; "
                    "with \"All leagues\", such a move counts as a move between tracked clubs, not as an arrival or departure.</li>")

    return {
        "__PAGE_TITLE__": title,
        "__BRAND_ALT__": ("Audax Italiano" if multi or configs[0]["country"] == "Chile"
                          else f"Flag of {configs[0]['country']}"),
        "__LEAGUE_H1__": h1,
        "__SUBTITLE__": subtitle,
        "__TOPMETA_SCOPE__": scope,
        "__TOPMETA_SOURCE_LINE__": ("Primary source: Transfermarkt · corporate cross-reference: CMF Chile"
                                     if any_cmf else "Primary source: Transfermarkt"),
        "__UNIVERSE_LI__": universe,
        "__SELLON_LI__": SELLON_LI.format(scope=sellon_scope) if any_sellon else "",
        "__CMF_LI__": CMF_LI if any_cmf else "",
        "__SELLON_FEE_NOTE__": (" Amounts inside sell-on/buy-back quotes are kept exactly as originally reported "
                                 "(mostly already in USD in Chilean/Argentine press).") if any_sellon else "",
        "__SELLON_FILTER_FIELD__": SELLON_FILTER.format(scope=sellon_scope) if any_sellon else "",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", default="all", choices=["all"] + sorted(league_config.LEAGUES))
    parser.add_argument("--lang", default="en", choices=["en", "es"])
    args = parser.parse_args()
    es = args.lang == "es"

    if args.league == "all":
        league_keys = ["chile", "uruguay", "paraguay", "peru"]
        out = league_config.ALL_LEAGUES_DASHBOARD_OUT
    else:
        league_keys = [args.league]
        out = league_config.get(args.league)["dashboard_out"]
    if es:
        out = out.replace("index.html", "index_es.html")
    configs = [league_config.get(k) for k in league_keys]

    datasets = [load_league(k) for k in league_keys]
    scope_counts = {}
    for cfg, recs in zip(configs, datasets):
        ids = set()
        for r in recs:
            if r["_fl"] and r["from_club"].get("club_id"):
                ids.add(r["from_club"]["club_id"])
            if r["_tl"] and r["to_club"].get("club_id"):
                ids.add(r["to_club"]["club_id"])
        scope_counts[cfg["code"]] = len(ids)
    canonical = merge_leagues(datasets)
    print(f"{len(canonical)} unique transfers from {sum(len(d) for d in datasets)} league records")

    cmf_map = {}
    if any(c["has_cmf"] for c in configs):
        cmf_path = os.path.join(league_config.get("chile")["processed_dir"], "cmf_club_mapping.json")
        if os.path.exists(cmf_path):
            cmf_map = json.load(open(cmf_path, encoding="utf-8"))

    slim_records = [slim(r) for r in canonical]
    if es:
        for r in slim_records:
            r["pos"] = i18n_es.POSITION_ES.get(r["pos"], r["pos"])

    clubs = {}
    for r in canonical:
        for side in (r["from_club"], r["to_club"]):
            cid = side.get("club_id")
            if cid and side.get("club_name"):
                clubs.setdefault(cid, side["club_name"])
    club_list = sorted(clubs.items(), key=lambda kv: kv[1])

    seasons = sorted({r["_s"] for r in canonical if r["_s"]})
    positions_pt = sorted(set(i18n_es.POSITION_ES.get(r["position"], r["position"]) if es else r["position"]
                              for r in canonical if r["position"]))
    nationalities = sorted(set(r["nationality"] for r in canonical if r["nationality"]))

    crests = {}
    for cid in clubs:
        path = os.path.join(CRESTS_DIR, f"{cid}.png")
        if os.path.exists(path):
            with open(path, "rb") as f:
                crests[cid] = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

    brand_crest_uri = ""  # no club logo in the header (the template hides the brand mark when empty)

    if len(league_keys) == 1 and league_keys[0] != "chile":
        flag_path = os.path.join(FLAGS_DIR, f"{configs[0]['code'].lower()}.png")
        if os.path.exists(flag_path):
            with open(flag_path, "rb") as f:
                brand_crest_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

    leagues_meta = [{"code": c["code"], "country": c["country"], "label": c["league_label"],
                     "name": i18n_es.LEAGUE_NAMES_ES[c["code"]]["name"] if es else c["country"],
                     "adj": i18n_es.LEAGUE_NAMES_ES[c["code"]]["adj"] if es else c["country_adj"]}
                    for c in configs]

    template_path = os.path.join(ROOT, "scripts", "dashboard_template.html")
    with open(template_path, encoding="utf-8") as f:
        html = f.read()
    if es:
        html = i18n_es.translate_template(html)
    replacements = {
        "__DATA_JSON__": json.dumps(slim_records, ensure_ascii=False, separators=(",", ":")),
        "__CLUBS_JSON__": json.dumps(club_list, ensure_ascii=False),
        "__CMF_JSON__": json.dumps(cmf_map, ensure_ascii=False),
        "__SEASONS_JSON__": json.dumps(seasons),
        "__POSITIONS_JSON__": json.dumps(positions_pt, ensure_ascii=False),
        "__NAT_JSON__": json.dumps(nationalities, ensure_ascii=False),
        "__FEEMETA_JSON__": json.dumps(i18n_es.FEE_TYPE_META_ES if es else FEE_TYPE_META, ensure_ascii=False),
        "__CRESTS_JSON__": json.dumps(crests),
        "__LEAGUES_JSON__": json.dumps(leagues_meta, ensure_ascii=False),
        "__HAS_SELLON__": json.dumps(any(c["has_sellon"] for c in configs)),
        "__BRAND_CREST_URI__": json.dumps(brand_crest_uri),
        "__GENERATED_COUNT__": str(len(slim_records)),
    }
    for placeholder, text in replacements.items():
        html = html.replace(placeholder, text)
    copy = i18n_es.build_copy_es(configs, scope_counts) if es else build_copy(configs, scope_counts)
    for placeholder, text in copy.items():
        html = html.replace(placeholder, text)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard written -> {out} ({len(slim_records)} transfers, "
          f"{len(replacements['__DATA_JSON__'])/1024:.0f} KB data, {len(crests)} crests)")


if __name__ == "__main__":
    main()
