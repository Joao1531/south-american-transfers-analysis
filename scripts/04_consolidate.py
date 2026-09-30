"""
Merge the raw scrape outputs into one canonical transfers table:
  - transfers_raw.json          (club-perspective arrivals/departures, 2020-2025)
  - transfer_details.json       (market value at transfer, contract, coaches)
  - player_transfer_history.json (full career -> used to find subsequent moves)
  - cmf_club_mapping.json       (CMF/SADP registry info per club)

A single real-world transfer usually appears twice in transfers_raw.json (once
as a "departure" row on the selling club's page, once as an "arrival" row on
the buying club's page) whenever both clubs are in our 25-club universe. This
script groups by transfer_id so each transfer appears exactly once, with a
clear from_club / to_club, then attaches enrichment.
"""
import argparse
import json
import os
import re
from collections import defaultdict

import league_config

ROOT = league_config.ROOT

SQUAD_SUFFIX_RE = re.compile(
    r"\s+(U1[5-9]|U2[0-3]|Sub[- ]?1[5-9]|Sub[- ]?2[0-3]|II|B|Reserves?|Res\.|Youth|Juvenil[es]*|Cadetes?)\s*$",
    re.IGNORECASE,
)


def squad_base_name(name):
    """Strip trailing youth/reserve-squad markers (' U21', ' Sub-20', ' II', ...)."""
    if not name:
        return name
    prev = None
    while prev != name:
        prev = name
        name = SQUAD_SUFFIX_RE.sub("", name).strip()
    return name


def is_internal_squad_move(from_club, to_club):
    """True when a transfer is really a youth/reserve-to-first-team promotion within
    the same club, not a real transfer (e.g. 'Colo-Colo U21' -> 'Colo-Colo')."""
    fname = (from_club or {}).get("club_name")
    tname = (to_club or {}).get("club_name")
    if not fname or not tname:
        return False
    fbase, tbase = squad_base_name(fname), squad_base_name(tname)
    return fbase == tbase and (fname != fbase or tname != tbase)


def load(proc, name, default):
    path = os.path.join(proc, name)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def club_side(rec, country):
    return {
        "club_id": rec["club_id"],
        "club_name": rec["club_name"],
        "country": country,
    }


def counterpart_side(rec):
    return {
        "club_id": rec.get("counterpart_club_id"),
        "club_name": rec.get("counterpart_club_name"),
        "league": rec.get("counterpart_league"),
        "country": rec.get("counterpart_country"),
    }


def find_chain(player_history, transfer_id, this_date):
    """Later moves for this player, in chronological order, after this transfer.

    Youth/reserve <-> first-team promotions within the same club are dropped:
    they're a registration-category change, not a real transfer.
    """
    if not player_history or not isinstance(player_history, list):
        return []
    later = []
    for t in player_history:
        d = t.get("dateUnformatted")
        if not d or not this_date:
            continue
        if d > this_date:
            from_name = (t.get("from") or {}).get("clubName")
            to_name = (t.get("to") or {}).get("clubName")
            if is_internal_squad_move({"club_name": from_name}, {"club_name": to_name}):
                continue
            later.append({
                "date": t.get("date"),
                "date_unformatted": d,
                "season": t.get("season"),
                "from_club": from_name,
                "to_club": to_name,
                "fee_text": t.get("fee"),
                "market_value_text": t.get("marketValue"),
            })
    later.sort(key=lambda x: x["date_unformatted"])
    return later


def this_transfer_date(player_history, transfer_id):
    for t in player_history or []:
        url = t.get("url", "")
        if f"transfer_id/{transfer_id}" in url:
            return t.get("dateUnformatted")
    return None


CONTRACT_RE = re.compile(
    r"(?:(\d+)\s*Years?\s*)?(?:(\d+)\s*Months?\s*)?(?:(\d+)\s*Days?\s*)?"
    r"\(\s*(\d{2})/(\d{2})/(\d{4})\s*\)"
)


def parse_contract(text, transfer_date):
    """'02 Years 03 Months 21 Days (31/12/2022)' -> (end_date iso, months_remaining int).

    months_remaining is computed from the gap between the transfer date and the
    contract end date (both known exactly), rather than re-summing the fuzzy
    Y/M/D text, so it's internally consistent with transfer_date.
    """
    if not text:
        return None, None
    m = CONTRACT_RE.search(text)
    if not m:
        return None, None
    _, _, _, d, mo, y = m.groups()
    end_date = f"{y}-{mo}-{d}"
    months_remaining = None
    if transfer_date:
        try:
            from datetime import date
            ty, tm, td = (int(x) for x in transfer_date.split("-"))
            ey, em, ed = int(y), int(mo), int(d)
            days = (date(ey, em, ed) - date(ty, tm, td)).days
            months_remaining = round(days / 30.44, 1)
        except (ValueError, TypeError):
            months_remaining = None
    return end_date, months_remaining


def main():
    parser = argparse.ArgumentParser()
    league_config.add_league_arg(parser)
    args = parser.parse_args()
    config = league_config.get(args.league)
    proc = config["processed_dir"]
    country = config["country"]

    if args.league == "chile":
        season_key = "season_chile"
        from_scope_key = "from_is_chile_pd_scope"
        to_scope_key = "to_is_chile_pd_scope"
        both_scope_key = "both_sides_in_chile_pd_scope"
    else:
        season_key = "season_league"
        from_scope_key = "from_is_league_scope"
        to_scope_key = "to_is_league_scope"
        both_scope_key = "both_sides_in_league_scope"

    raw = load(proc, "transfers_raw.json", [])
    details = load(proc, "transfer_details.json", {})
    histories = load(proc, "player_transfer_history.json", {})
    cmf_map = load(proc, "cmf_club_mapping.json", {})
    sellon = load(proc, "sellon_research_merged.json", {})
    profiles = load(proc, "player_profiles.json", {})

    by_tid = defaultdict(list)
    for r in raw:
        by_tid[r["transfer_id"]].append(r)

    canonical = []
    excluded_internal = 0
    for tid, recs in by_tid.items():
        out_rec = next((r for r in recs if r["direction"] == "out"), None)
        in_rec = next((r for r in recs if r["direction"] == "in"), None)
        base = in_rec or out_rec

        if out_rec:
            from_club = club_side(out_rec, country)
        elif in_rec:
            from_club = counterpart_side(in_rec)
        else:
            from_club = {}

        if in_rec:
            to_club = club_side(in_rec, country)
        elif out_rec:
            to_club = counterpart_side(out_rec)
        else:
            to_club = {}

        if is_internal_squad_move(from_club, to_club):
            excluded_internal += 1
            continue  # youth/reserve -> first-team promotion within the same club, not a real transfer

        both_in_scope = bool(out_rec and in_rec)
        from_is_scope = bool(out_rec)
        to_is_scope = bool(in_rec)

        detail = details.get(tid, {}) or {}
        player_id = base["player_id"]
        history = histories.get(player_id, [])
        t_date = this_transfer_date(history, tid) or None
        if not t_date and base.get("season"):
            t_date = f"{base['season']}-01-01"

        contract_end_date, months_remaining = parse_contract(detail.get("remaining_contract_duration"), t_date)
        # Transfermarkt's `season` (saison_id) follows the European July-June convention.
        # South American leagues run by calendar year (Feb-Nov), so "season 2020"
        # on Transfermarkt is mostly actual 2021 activity here. season_key is the
        # correct calendar-year bucket, derived directly from the transfer date.
        season_bucket = int(t_date[:4]) if t_date else None
        profile = profiles.get(player_id, {}) or {}
        nationalities = profile.get("nationalities") or []

        record = {
            "transfer_id": tid,
            "player_id": player_id,
            "player_name": base["player_name"],
            "player_url": base["player_url"],
            "position": base["position"],
            "nationality": base["nationality"],
            "age_at_transfer": base["age_at_transfer"],
            "season": (out_rec or in_rec)["season"],
            "season_transfermarkt": (out_rec or in_rec)["season"],
            season_key: season_bucket,
            "seasons_seen": sorted({r["season"] for r in recs}),
            "from_club": from_club,
            "to_club": to_club,
            both_scope_key: both_in_scope,
            from_scope_key: from_is_scope,
            to_scope_key: to_is_scope,
            "fee_text": base["fee_text"],
            "fee_type": base["fee_type"],
            "fee_value_eur": base["fee_value_eur"],
            "market_value_at_transfer_eur": detail.get("market_value_at_transfer_eur"),
            "age_at_transfer_precise": detail.get("age_at_transfer_precise"),
            "remaining_contract_duration": detail.get("remaining_contract_duration"),
            "contract_end_date": contract_end_date,
            "contract_months_remaining": months_remaining,
            "height_cm": profile.get("height_cm"),
            "foot": profile.get("foot"),
            "date_of_birth": profile.get("date_of_birth"),
            "agent": profile.get("agent"),
            "nationality_2": nationalities[1] if len(nationalities) > 1 else None,
            "dual_nationality": len(nationalities) > 1,
            "coach_from": detail.get("coach_from"),
            "coach_to": detail.get("coach_to"),
            "competition": detail.get("competition"),
            "league_type": detail.get("league_type"),
            "transfer_date": t_date,
            "subsequent_transfers": find_chain(history, tid, t_date),
            "sellon_clause": sellon.get(tid),
        }
        canonical.append(record)

    canonical.sort(key=lambda r: (r["transfer_date"] or "", r["player_name"]))

    out_path = os.path.join(proc, "canonical_transfers.json")
    os.makedirs(proc, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(canonical, f, ensure_ascii=False)

    enrichment_details = sum(1 for r in canonical if r["market_value_at_transfer_eur"] is not None)
    with_chain = sum(1 for r in canonical if r["subsequent_transfers"])
    print(f"{len(canonical)} canonical transfers -> {out_path}")
    print(f"  excluded (youth/reserve -> first-team promotion, same club): {excluded_internal}")
    print(f"  with transfer-detail enrichment: {enrichment_details}")
    print(f"  with a known subsequent move:    {with_chain}")
    print(f"  both sides in league scope:      {sum(1 for r in canonical if r[both_scope_key])}")
    print(f"  with a documented sell-on/buy-back clause: {sum(1 for r in canonical if r['sellon_clause'] and r['sellon_clause'].get('found'))}")
    print(f"  researched but not found:                  {sum(1 for r in canonical if r['sellon_clause'] and not r['sellon_clause'].get('found'))}")
    print(f"  with height:                     {sum(1 for r in canonical if r['height_cm'])}")
    print(f"  with agent:                      {sum(1 for r in canonical if r['agent'])}")
    print(f"  with dual/multi nationality:      {sum(1 for r in canonical if r['dual_nationality'])}")
    print(f"  with contract_end_date parsed:    {sum(1 for r in canonical if r['contract_end_date'])}")
    from collections import Counter
    print(f"  {season_key} distribution: {dict(sorted(Counter(r[season_key] for r in canonical if r[season_key]).items()))}")


if __name__ == "__main__":
    main()
