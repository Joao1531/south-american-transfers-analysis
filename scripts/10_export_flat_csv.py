"""
Export canonical_transfers.json as a flat, analysis-ready deliverable:

  - transfers_flat.csv   one row per transfer, no nested objects. Club/country
                         fields are un-nested into their own columns
                         (club_origen, pais_origen, club_destino, pais_destino)
                         and the sell-on/buy-back clause is flattened too.
  - transfer_history.json  the per-transfer "subsequent transfers" chain,
                         keyed by transfer_id -- doesn't fit in a flat CSV,
                         so it ships separately.
"""
import argparse
import csv
import json
import os

import league_config

ROOT = league_config.ROOT


def build_fields(season_key, from_scope_key, to_scope_key, both_scope_key):
    return [
        "transfer_id", "player_id", "player_name", "player_url",
        "position", "nationality", "nationality_2", "dual_nationality",
        "date_of_birth", "height_cm", "foot", "agent",
        "age_at_transfer", "age_at_transfer_precise", season_key, "season_transfermarkt", "transfer_date",
        "club_origen", "pais_origen", "liga_origen",
        "club_destino", "pais_destino", "liga_destino",
        from_scope_key, to_scope_key, both_scope_key,
        "fee_text", "fee_type", "fee_value_eur", "market_value_at_transfer_eur",
        "remaining_contract_duration", "contract_end_date", "contract_months_remaining",
        "coach_from", "coach_to", "competition", "league_type",
        "has_subsequent_transfer",
        "clause_found", "clause_type", "clause_percentage", "clause_beneficiary_club", "clause_source_url",
    ]


def flatten(r, season_key, from_scope_key, to_scope_key, both_scope_key):
    fc, tc = r["from_club"] or {}, r["to_club"] or {}
    sc = r.get("sellon_clause") or {}
    return {
        "transfer_id": r["transfer_id"],
        "player_id": r["player_id"],
        "player_name": r["player_name"],
        "player_url": r["player_url"],
        "position": r["position"],
        "nationality": r["nationality"],
        "nationality_2": r.get("nationality_2"),
        "dual_nationality": r.get("dual_nationality", False),
        "date_of_birth": r.get("date_of_birth"),
        "height_cm": r.get("height_cm"),
        "foot": r.get("foot"),
        "agent": r.get("agent"),
        "age_at_transfer": r["age_at_transfer"],
        "age_at_transfer_precise": r["age_at_transfer_precise"],
        season_key: r.get(season_key),
        "season_transfermarkt": r.get("season_transfermarkt"),
        "transfer_date": r["transfer_date"],
        "club_origen": fc.get("club_name"),
        "pais_origen": fc.get("country"),
        "liga_origen": fc.get("league"),
        "club_destino": tc.get("club_name"),
        "pais_destino": tc.get("country"),
        "liga_destino": tc.get("league"),
        from_scope_key: r[from_scope_key],
        to_scope_key: r[to_scope_key],
        both_scope_key: r[both_scope_key],
        "fee_text": r["fee_text"],
        "fee_type": r["fee_type"],
        "fee_value_eur": r["fee_value_eur"],
        "market_value_at_transfer_eur": r["market_value_at_transfer_eur"],
        "remaining_contract_duration": r["remaining_contract_duration"],
        "contract_end_date": r.get("contract_end_date"),
        "contract_months_remaining": r.get("contract_months_remaining"),
        "coach_from": r["coach_from"],
        "coach_to": r["coach_to"],
        "competition": r["competition"],
        "league_type": r["league_type"],
        "has_subsequent_transfer": bool(r.get("subsequent_transfers")),
        "clause_found": sc.get("found", False),
        "clause_type": sc.get("clause_type"),
        "clause_percentage": sc.get("percentage"),
        "clause_beneficiary_club": sc.get("beneficiary_club"),
        "clause_source_url": sc.get("source_url"),
    }


def main():
    parser = argparse.ArgumentParser()
    league_config.add_league_arg(parser)
    args = parser.parse_args()
    config = league_config.get(args.league)
    proc = config["processed_dir"]
    canon_path = os.path.join(proc, "canonical_transfers.json")
    csv_path = os.path.join(proc, "transfers_flat.csv")
    history_path = os.path.join(proc, "transfer_history.json")

    if args.league == "chile":
        season_key, from_scope_key, to_scope_key, both_scope_key = (
            "season_chile", "from_is_chile_pd_scope", "to_is_chile_pd_scope", "both_sides_in_chile_pd_scope")
    else:
        season_key, from_scope_key, to_scope_key, both_scope_key = (
            "season_league", "from_is_league_scope", "to_is_league_scope", "both_sides_in_league_scope")
    fields = build_fields(season_key, from_scope_key, to_scope_key, both_scope_key)

    canon = json.load(open(canon_path, encoding="utf-8"))

    seen_tids = set()
    rows = []
    for r in canon:
        if r["transfer_id"] in seen_tids:
            continue  # defensive: canonical is already one-row-per-transfer_id, but guard against it anyway
        seen_tids.add(r["transfer_id"])
        rows.append(flatten(r, season_key, from_scope_key, to_scope_key, both_scope_key))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    history = {
        r["transfer_id"]: r["subsequent_transfers"]
        for r in canon
        if r["transfer_id"] in seen_tids and r.get("subsequent_transfers")
    }
    json.dump(history, open(history_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"Flat CSV written -> {csv_path} ({len(rows)} rows, {len(fields)} columns)")
    print(f"Transfer history JSON written -> {history_path} ({len(history)} transfers with a known subsequent move)")


if __name__ == "__main__":
    main()
