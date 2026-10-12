"""
Build the Audax market-intelligence report (report/index.html).
Combines local data analysis (Big 3 profiles, sell-on tracker, loan stats,
league stats) with narrative text from research agents (saved as plain text
files in report/agent_sections/).
"""
import argparse
import base64
import json
import os
import re

import i18n_report_es

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
REPORT_DIR = os.path.join(ROOT, "report")
AGENT_DIR = os.path.join(REPORT_DIR, "agent_sections")
AUDAX_CREST = os.path.join(ROOT, "data", "raw", "crests", "6363.png")

EN = {
    "pending": "<p><em>Research pending — {name} not yet available.</em></p>",
    "arrivals": "arrivals",
    "departures": "departures",
    "avg_age_arr": "avg. age, arrivals",
    "avg_age_dep": "avg. age, departures",
    "spent": "Spent",
    "earned": "Earned",
    "net": "Net",
    "big3_note": ("{chilean_pct:.0f}% of departures are Chilean nationals; of those, {abroad_pct:.0f}% leave the country entirely "
                  "(rest stay in Chilean football, mostly lower divisions). Top international destinations: {top}."),
    "biggest_sale": "Biggest sale:",
    "biggest_buy": "Biggest buy:",
    "buy_from": "from",
    "moved_on": "moved on → {name}",
    "still_there": "still there",
    "clause": "clause",
    "no_clause": "no clause found",
    "confirmed": "confirmed",
    "clause_labels": {"option-to-buy": "Option to buy", "mandatory-purchase": "Mandatory purchase",
                      "sell-on": "Sell-on", "buy-back": "Buy-back"},
    "unknown_country": "Unknown",
    "million": "m",
}
T = EN
COUNTRY_ES = {}
DECIMAL_COMMA = False

BIG3 = {"2433": "Colo-Colo", "3277": "U. Católica", "1037": "U. de Chile"}


def load(name, default=None):
    path = os.path.join(PROC, name)
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    return default


def age_num(a):
    try:
        return float(a)
    except (TypeError, ValueError):
        return None


def fmt_usd(eur, decimals=2):
    if eur is None:
        return "—"
    usd = eur * 1.08
    if abs(usd) >= 1e6:
        out = f"${usd/1e6:.{decimals}f}{T['million']}"
    elif abs(usd) >= 1e3:
        out = f"${usd/1e3:.0f}k"
    else:
        out = f"${usd:.0f}"
    return out.replace(".", ",") if DECIMAL_COMMA else out


def country(c):
    return COUNTRY_ES.get(c, c)


def read_agent_text(name):
    path = os.path.join(AGENT_DIR, name)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    return T["pending"].format(name=name)


def build_big3_profiles(canonical):
    profile = {cid: {
        "arrivals": 0, "departures": 0, "spend": 0.0, "income": 0.0,
        "arr_ages": [], "dep_ages": [],
        "arr_domestic": 0, "arr_intl": 0,
        "dep_chilean_nat": 0, "dep_foreign_nat": 0,
        "dep_chilean_nat_abroad": 0,
        "dep_countries": {}, "dep_leagues": {},
        "biggest_sale": None, "biggest_buy": None,
    } for cid in BIG3}

    for r in canonical:
        f, t = r["from_club"], r["to_club"]
        fv = r["fee_value_eur"]
        a = age_num(r["age_at_transfer"])
        if t.get("club_id") in BIG3:
            cid = t["club_id"]
            p = profile[cid]
            p["arrivals"] += 1
            if a:
                p["arr_ages"].append(a)
            if f.get("country") == "Chile":
                p["arr_domestic"] += 1
            else:
                p["arr_intl"] += 1
            if fv:
                p["spend"] += fv
                if not p["biggest_buy"] or fv > p["biggest_buy"][1]:
                    p["biggest_buy"] = (r["player_name"], fv, f.get("club_name"))
        if f.get("club_id") in BIG3:
            cid = f["club_id"]
            p = profile[cid]
            p["departures"] += 1
            if a:
                p["dep_ages"].append(a)
            if r["nationality"] == "Chile":
                p["dep_chilean_nat"] += 1
                if t.get("country") and t.get("country") != "Chile":
                    p["dep_chilean_nat_abroad"] += 1
            else:
                p["dep_foreign_nat"] += 1
            if t.get("country") and t.get("country") != "Chile":
                p["dep_countries"][t["country"]] = p["dep_countries"].get(t["country"], 0) + 1
            if fv:
                p["income"] += fv
                if not p["biggest_sale"] or fv > p["biggest_sale"][1]:
                    p["biggest_sale"] = (r["player_name"], fv, t.get("club_name"))
    return profile


def big3_cards_html(profile):
    cards = []
    order = ["2433", "3277", "1037"]  # Colo-Colo, U. Católica, U. de Chile
    for cid in order:
        p = profile[cid]
        name = BIG3[cid]
        avg_arr_age = sum(p["arr_ages"]) / len(p["arr_ages"]) if p["arr_ages"] else 0
        avg_dep_age = sum(p["dep_ages"]) / len(p["dep_ages"]) if p["dep_ages"] else 0
        net = p["income"] - p["spend"]
        net_class = "pos" if net >= 0 else "neg"
        chilean_pct = p["dep_chilean_nat"] / p["departures"] * 100 if p["departures"] else 0
        abroad_pct = p["dep_chilean_nat_abroad"] / p["dep_chilean_nat"] * 100 if p["dep_chilean_nat"] else 0
        top_countries = sorted(p["dep_countries"].items(), key=lambda x: -x[1])[:3]
        top_countries_s = ", ".join(f"{country(c)} ({n})" for c, n in top_countries) or "—"
        sale = p["biggest_sale"]
        buy = p["biggest_buy"]
        cards.append(f"""
        <div class="big3-card">
          <div class="big3-card-head">
            <img class="big3-crest" src="__CREST_{cid}__" alt="">
            <h3>{name}</h3>
          </div>
          <div class="big3-stat-row">
            <div><span class="n">{p['arrivals']}</span><span class="l">{T['arrivals']}</span></div>
            <div><span class="n">{p['departures']}</span><span class="l">{T['departures']}</span></div>
          </div>
          <div class="big3-stat-row">
            <div><span class="n">{avg_arr_age:.1f}</span><span class="l">{T['avg_age_arr']}</span></div>
            <div><span class="n">{avg_dep_age:.1f}</span><span class="l">{T['avg_age_dep']}</span></div>
          </div>
          <div class="big3-money">
            <div><span class="l">{T['spent']}</span><span class="n">{fmt_usd(p['spend'])}</span></div>
            <div><span class="l">{T['earned']}</span><span class="n">{fmt_usd(p['income'])}</span></div>
            <div><span class="l">{T['net']}</span><span class="n {net_class}">{'+' if net>=0 else ''}{fmt_usd(net)}</span></div>
          </div>
          <p class="big3-note">{T['big3_note'].format(chilean_pct=chilean_pct, abroad_pct=abroad_pct, top=top_countries_s)}</p>
          <p class="big3-note"><b>{T['biggest_sale']}</b> {sale[0] if sale else '—'} → {sale[2] if sale else ''} ({fmt_usd(sale[1]) if sale else ''})<br>
          <b>{T['biggest_buy']}</b> {buy[0] if buy else '—'} {T['buy_from']} {buy[2] if buy else ''} ({fmt_usd(buy[1]) if buy else ''})</p>
        </div>""")
    return "\n".join(cards)


def current_club_id_name(history, pid):
    h = history.get(pid)
    if not h or isinstance(h, dict) or not h:
        return None, None
    latest = h[0]
    to = latest.get("to", {})
    href = to.get("href") or ""
    m = re.search(r"/verein/(\d+)", href)
    return (m.group(1) if m else None), to.get("clubName")


def sellon_tracker_html(canonical, history):
    with_clause = [r for r in canonical if r["sellon_clause"] and r["sellon_clause"].get("found")]
    with_clause.sort(key=lambda r: r["transfer_date"] or "", reverse=True)
    rows = []
    for r in with_clause:
        sc = r["sellon_clause"]
        cur_id, cur_name = current_club_id_name(history, r["player_id"])
        sold_to_id = r["to_club"].get("club_id")
        moved = not (cur_id and sold_to_id and cur_id == sold_to_id)
        status = f'<span class="tag tag-moved">{T["moved_on"].format(name=cur_name)}</span>' if moved else f'<span class="tag tag-stable">{T["still_there"]}</span>'
        pct = sc.get("percentage") or (sc.get("clause_type") or T["clause"])
        rows.append(f"""<tr>
          <td>{r['player_name']}</td>
          <td class="num">{pct}</td>
          <td>{sc.get('beneficiary_club') or '—'}</td>
          <td>{r['to_club']['club_name']}</td>
          <td>{status}</td>
        </tr>""")
    return "\n".join(rows)


def clause_research_stats(canonical, history):
    by_type = {}
    for r in canonical:
        sc = r["sellon_clause"]
        if sc is None:
            continue
        ft = r["fee_type"]
        by_type.setdefault(ft, {"checked": 0, "found": 0})
        by_type[ft]["checked"] += 1
        if sc.get("found"):
            by_type[ft]["found"] += 1

    with_clause = [r for r in canonical if r["sellon_clause"] and r["sellon_clause"].get("found")]
    moved = 0
    for r in with_clause:
        cur_id, _ = current_club_id_name(history, r["player_id"])
        if cur_id != r["to_club"].get("club_id"):
            moved += 1

    return {
        "total_checked": sum(v["checked"] for v in by_type.values()),
        "total_found": sum(v["found"] for v in by_type.values()),
        "by_type": by_type,
        "moved": moved,
        "moved_pct": round(moved / len(with_clause) * 100) if with_clause else 0,
    }


def loan_clause_tracker_html(canonical):
    """The 16 disclosed-fee loans we specifically researched for purchase-option / sell-on terms."""
    sellon = load("sellon_research_merged.json", {})
    rows_data = [r for r in canonical if r["fee_type"] == "loan_fee" and r["transfer_id"] in sellon
                 and "exit_reason" not in sellon[r["transfer_id"]]]
    rows_data.sort(key=lambda r: r["transfer_date"] or "", reverse=True)
    CLAUSE_LABEL = T["clause_labels"]
    rows = []
    for r in rows_data:
        sc = sellon[r["transfer_id"]]
        if not sc.get("found"):
            status = f'<span class="tag tag-stable">{T["no_clause"]}</span>'
            pct, clause = "—", "—"
        else:
            status = f'<span class="tag tag-moved">{T["confirmed"]}</span>'
            pct = sc.get("percentage") or "—"
            clause = CLAUSE_LABEL.get(sc.get("clause_type"), sc.get("clause_type") or "—")
        rows.append(f"""<tr>
          <td>{r['player_name']}</td>
          <td>{r['from_club']['club_name']} → {r['to_club']['club_name']}</td>
          <td>{clause}</td>
          <td class="num">{pct}</td>
          <td>{status}</td>
        </tr>""")
    return "\n".join(rows)


def loan_stats(canonical):
    loans = [r for r in canonical if r["fee_type"] in ("loan_fee", "loan_free") and r["from_is_chile_pd_scope"]]
    total = len(loans)
    returned_moved = returned_stayed = converted = unresolved = 0
    for r in loans:
        chain = r["subsequent_transfers"]
        if not chain:
            unresolved += 1
            continue
        first = chain[0]
        if first["fee_text"] and "end of loan" in first["fee_text"].lower():
            if len(chain) > 1:
                returned_moved += 1
            else:
                returned_stayed += 1
        else:
            converted += 1
    return {
        "total": total, "returned_moved": returned_moved, "returned_stayed": returned_stayed,
        "converted": converted, "unresolved": unresolved,
    }


def league_reception_stats(canonical):
    from collections import defaultdict
    by_country = defaultdict(lambda: {"count": 0, "fee_sum": 0.0, "fee_n": 0})
    for r in canonical:
        if r["from_is_chile_pd_scope"] and not r["to_is_chile_pd_scope"]:
            c = r["to_club"].get("country") or "Unknown"
            by_country[c]["count"] += 1
            if r["fee_value_eur"]:
                by_country[c]["fee_sum"] += r["fee_value_eur"]
                by_country[c]["fee_n"] += 1
    rows = []
    for c, v in by_country.items():
        if c in ("Chile", "Unknown"):
            continue
        avg = v["fee_sum"] / v["fee_n"] if v["fee_n"] else None
        rows.append((c, v["count"], v["fee_n"], avg))
    rows.sort(key=lambda x: -x[1])
    return rows[:10]


def league_table_html(rows):
    out = []
    for c, count, feen, avg in rows:
        avg_s = fmt_usd(avg) if avg else "—"
        out.append(f"<tr><td>{country(c)}</td><td class='num'>{count}</td><td class='num'>{feen}</td><td class='num'>{avg_s}</td></tr>")
    return "\n".join(out)


def main():
    global T, COUNTRY_ES, DECIMAL_COMMA, AGENT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="en", choices=["en", "es"])
    es = parser.parse_args().lang == "es"
    if es:
        T = i18n_report_es.PY
        COUNTRY_ES = i18n_report_es.COUNTRY_ES
        DECIMAL_COMMA = True
        AGENT_DIR = os.path.join(REPORT_DIR, "agent_sections_es")

    canonical = load("canonical_transfers.json", [])
    history = load("player_transfer_history.json", {})

    profile = build_big3_profiles(canonical)
    big3_html = big3_cards_html(profile)
    sellon_rows_html = sellon_tracker_html(canonical, history)
    loans = loan_stats(canonical)
    league_rows = league_reception_stats(canonical)
    league_html = league_table_html(league_rows)
    clause_stats = clause_research_stats(canonical, history)
    loan_clause_rows_html = loan_clause_tracker_html(canonical)

    audax_uri = ""  # header logo removed

    # crests_sq for big3 mini logos
    crests_sq_dir = os.path.join(ROOT, "data", "raw", "crests_sq")
    crest_uris = {}
    for cid in BIG3:
        path = os.path.join(crests_sq_dir, f"{cid}.png")
        if os.path.exists(path):
            with open(path, "rb") as f:
                crest_uris[cid] = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

    template_path = os.path.join(ROOT, "scripts", "report_template.html")
    with open(template_path, encoding="utf-8") as f:
        html = f.read()
    if es:
        html = i18n_report_es.translate_template(html)

    for cid, uri in crest_uris.items():
        big3_html = big3_html.replace(f"__CREST_{cid}__", uri)

    html = html.replace("__AUDAX_LOGO__", audax_uri)
    html = html.replace("__BIG3_CARDS__", big3_html)
    html = html.replace("__SELLON_ROWS__", sellon_rows_html)
    html = html.replace("__LEAGUE_ROWS__", league_html)
    html = html.replace("__LOAN_TOTAL__", str(loans["total"]))
    html = html.replace("__LOAN_RETURNED_MOVED__", str(loans["returned_moved"]))
    html = html.replace("__LOAN_RETURNED_STAYED__", str(loans["returned_stayed"]))
    html = html.replace("__LOAN_CONVERTED__", str(loans["converted"]))
    html = html.replace("__LOAN_UNRESOLVED__", str(loans["unresolved"]))
    html = html.replace("__LOAN_CLAUSE_ROWS__", loan_clause_rows_html)

    bt = clause_stats["by_type"]
    html = html.replace("__CLAUSE_TOTAL_CHECKED__", str(clause_stats["total_checked"]))
    html = html.replace("__CLAUSE_TOTAL_FOUND__", str(clause_stats["total_found"]))
    html = html.replace("__CLAUSE_MOVED__", str(clause_stats["moved"]))
    html = html.replace("__CLAUSE_MOVED_PCT__", str(clause_stats["moved_pct"]))
    html = html.replace("__PAID_CHECKED__", str(bt.get("transfer_fee", {}).get("checked", 0)))
    html = html.replace("__PAID_FOUND__", str(bt.get("transfer_fee", {}).get("found", 0)))
    html = html.replace("__FREE_CHECKED__", str(bt.get("free_transfer", {}).get("checked", 0)))
    html = html.replace("__FREE_FOUND__", str(bt.get("free_transfer", {}).get("found", 0)))
    html = html.replace("__LOANFEE_CHECKED__", str(bt.get("loan_fee", {}).get("checked", 0)))
    html = html.replace("__LOANFEE_FOUND__", str(bt.get("loan_fee", {}).get("found", 0)))

    html = html.replace("__AGENT_FREE_CLAUSES__", read_agent_text("free_clauses.html"))
    html = html.replace("__AGENT_LEAGUE_RECEPTION__", read_agent_text("league_reception.html"))
    html = html.replace("__AGENT_LOAN_PRACTICES__", read_agent_text("loan_practices.html"))
    html = html.replace("__AGENT_SOURCE_VERDICT__", read_agent_text("source_verdict.html"))

    out_path = os.path.join(REPORT_DIR, "index_es.html" if es else "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report written -> {out_path} ({len(html)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
