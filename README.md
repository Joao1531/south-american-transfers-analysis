# Chilean Transfers Analysis

A market-intelligence project on the Chilean Primera División transfer market (2020–2026), built around **Audax Italiano**. It scrapes Transfermarkt, consolidates every transfer touching the league's 25-club universe into a canonical dataset, and renders two self-contained HTML deliverables: a league-wide transfer dashboard and a club-focused intelligence report.

## What's inside

| Path | Description |
|---|---|
| `scripts/` | 10 numbered Python scripts forming the full pipeline (run in order) |
| `data/processed/` | Clean outputs: canonical transfers, flat CSV, player histories, sell-on research |
| `data/raw/` | Small cached source assets kept in-repo: club list, CMF/SADP registry, club crests |
| `dashboard/index.html` | "Chilean Transfer Market 2020–2026" — interactive league dashboard (self-contained, crests embedded as base64) |
| `report/index.html` | "Audax Transfer Intelligence" — market report for Audax Italiano with narrative sections |
| `combined/index.html` | Both pages merged into one tabbed artifact (iframe `srcdoc` isolation) |

## Pipeline

1. **`01_scrape_club_transfers.py`** — Scrapes arrivals/departures for every club that played in the Primera División 2020–2025 → `transfers_raw.json`
2. **`02_scrape_transfer_details.py`** — Enriches each transfer from its detail page: market value at transfer, precise age, remaining contract, coaches involved → `transfer_details.json`
3. **`03_scrape_player_transfer_history.py`** — Fetches each player's full career history via Transfermarkt's internal JSON endpoint (`/ceapi/transferHistory/list`) to detect subsequent moves → `player_transfer_history.json`
4. **`04_consolidate.py`** — Deduplicates by `transfer_id` (a real transfer appears on both the selling and buying club pages), normalizes club names, classifies fees, detects sell-on/buy-back clauses → `canonical_transfers.json`
5. **`05_build_dashboard.py`** — Builds the league dashboard with embedded crests → `dashboard/index.html`
6. **`06_fetch_all_crests.py`** — Fetches 30×30 crest PNGs for all 428 clubs appearing anywhere in the data (opponents included) → `data/raw/crests_sq/`
7. **`07_build_report.py`** — Builds the Audax report, combining local analytics (Big-3 profiles, sell-on tracker, loan stats) with narrative agent sections (`report/agent_sections/`) → `report/index.html`
8. **`08_scrape_player_profiles.py`** — Scrapes bio fields not on club pages: height, preferred foot, DOB, player agent, dual citizenship → `player_profiles.json`
9. **`09_build_combined.py`** — Merges dashboard + report into `combined/index.html`
10. **`10_export_flat_csv.py`** — Exports an analysis-ready flat CSV and the per-transfer subsequent-moves chain → `transfers_flat.csv`, `transfer_history.json`

## Dataset stats

- **3,145 canonical transfers** across seasons **2020–2026**
- **1,298 unique players**; **81 Chilean clubs** appear in the network (25 in-scope league clubs)
- **252** transfers carry a market value at the time (2,525 records valued); **120 paid transfer fees** totalling **€119.4M** (max €5.2M)
- Fee breakdown: 1,190 free transfers · 764 end-of-loan returns · 669 free loans · 28 paid loans · 194 undisclosed
- Bio enrichment: 2,158 transfers with agent info · 579 dual-nationality players
- **CMF/SADP mapping**: each league club mapped to its regulatory entity (e.g. Colo-Colo → Blanco y Negro S.A., a bolsa-listed issuer rather than a SADP)

## Key features of the data model

- **Fee classification** into 9 types (`transfer_fee`, `loan_fee`, `loan_free`, `end_of_loan`, `free_transfer`, `undisclosed`, …) with EUR values where available
- **Club-perspective dedup**: arrivals/departures from both sides collapse into one record with clean `from_club`/`to_club`
- **Subsequent-transfers chain** per transfer — resale tracking used for sell-on clause research
- **Foreign-player quota support** via dual-nationality flags and citizenships

## Running it

```bash
pip install requests beautifulsoup4
python scripts/01_scrape_club_transfers.py   # then 02..10 in order
```

Scripts are polite by design: single-threaded, disk-cached per page, ~1.1–1.3s delay between live requests, identifiable User-Agent. Re-runs are cheap — cached pages are never re-fetched.

> Note: the full raw scrape cache (~514MB of HTML/JSON under `data/raw/{club_transfers,transfer_details,player_history,player_profiles,sellon_research}`) is intentionally not committed. Delete the cache folders to re-scrape from scratch, or keep them locally as the cache.

## Deliverables

Open `combined/index.html` in a browser — it contains both the league dashboard and the Audax report as tabs. Fonts load from Google Fonts; everything else (data, crests, styling) is embedded in the file.
