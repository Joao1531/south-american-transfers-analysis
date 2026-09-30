"""
Shared per-league configuration for the transfer-pipeline scripts.

`chile` mirrors the project's original, hand-curated setup exactly (same
paths, same output field names) so passing no --league flag (or --league
chile) leaves its behavior byte-for-byte identical to before this module
existed. The other leagues are fetched/consolidated generically.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEAGUES = {
    "chile": {
        "code": "CL",
        "country": "Chile",
        "country_adj": "Chilean",
        "league_label": "Primera División",
        "competition_code": None,
        "competition_slug": None,
        "seasons": list(range(2020, 2026)),
        "clubs_path": os.path.join(ROOT, "data", "raw", "clubs_2020_2025.json"),
        "processed_dir": os.path.join(ROOT, "data", "processed"),
        "dashboard_out": os.path.join(ROOT, "dashboard", "chile", "index.html"),
        "has_cmf": True,
        "has_sellon": True,
    },
    "uruguay": {
        "code": "UY",
        "country": "Uruguay",
        "country_adj": "Uruguayan",
        "league_label": "Primera División",
        "competition_code": "URU1",
        "competition_slug": "primera-division-uruguay",
        "seasons": list(range(2020, 2026)),
        "clubs_path": os.path.join(ROOT, "data", "raw", "clubs_uruguay.json"),
        "processed_dir": os.path.join(ROOT, "data", "processed", "uruguay"),
        "dashboard_out": os.path.join(ROOT, "dashboard", "uruguay", "index.html"),
        "has_cmf": False,
        "has_sellon": False,
    },
    "paraguay": {
        "code": "PY",
        "country": "Paraguay",
        "country_adj": "Paraguayan",
        "league_label": "Primera División",
        "competition_code": "PR1A",
        "competition_slug": "primera-division-apertura",
        "seasons": list(range(2020, 2026)),
        "clubs_path": os.path.join(ROOT, "data", "raw", "clubs_paraguay.json"),
        "processed_dir": os.path.join(ROOT, "data", "processed", "paraguay"),
        "dashboard_out": os.path.join(ROOT, "dashboard", "paraguay", "index.html"),
        "has_cmf": False,
        "has_sellon": False,
    },
    "peru": {
        "code": "PE",
        "country": "Peru",
        "country_adj": "Peruvian",
        "league_label": "Liga 1",
        "competition_code": "TDeA",
        "competition_slug": "liga-1-apertura",
        "seasons": list(range(2020, 2026)),
        "clubs_path": os.path.join(ROOT, "data", "raw", "clubs_peru.json"),
        "processed_dir": os.path.join(ROOT, "data", "processed", "peru"),
        "dashboard_out": os.path.join(ROOT, "dashboard", "peru", "index.html"),
        "has_cmf": False,
        "has_sellon": False,
    },
}


ALL_LEAGUES_DASHBOARD_OUT = os.path.join(ROOT, "dashboard", "index.html")


def get(league):
    if league not in LEAGUES:
        raise ValueError(f"Unknown league {league!r}. Choose one of {sorted(LEAGUES)}.")
    return LEAGUES[league]


def add_league_arg(parser, default="chile"):
    parser.add_argument("--league", default=default, choices=sorted(LEAGUES),
                         help=f"Which league to process (default: {default})")
    return parser
