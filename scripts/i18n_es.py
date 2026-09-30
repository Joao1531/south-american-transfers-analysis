"""
Spanish translation layer for dashboard_template.html.

The template stays the single source of truth (English). `translate_template`
swaps each English string for its Spanish counterpart and fails loudly if a
string is no longer present, so template edits can't silently leave the
Spanish build half-translated.
"""

PAIRS = [
    # --- document / header ---
    ('<html lang="en">', '<html lang="es">'),
    ('<b>__GENERATED_COUNT__ unique transfers</b>', '<b>__GENERATED_COUNT__ traspasos únicos</b>'),

    # --- filters ---
    ('<label>League</label>', '<label>Liga</label>'),
    ('<option value="">All leagues</option>', '<option value="">Todas las ligas</option>'),
    ('<select id="f-club"><option value="">All</option>', '<select id="f-club"><option value="">Todos</option>'),
    ('<label>Season</label>', '<label>Temporada</label>'),
    ('<select id="f-season"><option value="">All</option>', '<select id="f-season"><option value="">Todas</option>'),
    ('<label>Direction</label>', '<label>Dirección</label>'),
    ('<select id="f-dir">\n        <option value="">All</option>', '<select id="f-dir">\n        <option value="">Todas</option>'),
    ('<label>Transfer type</label>', '<label>Tipo de traspaso</label>'),
    ('<select id="f-fee"><option value="">All</option>', '<select id="f-fee"><option value="">Todos</option>'),
    ('<label>Position</label>', '<label>Posición</label>'),
    ('<select id="f-pos"><option value="">All</option>', '<select id="f-pos"><option value="">Todas</option>'),
    ('<label>Nationality</label>', '<label>Nacionalidad</label>'),
    ('<select id="f-nat"><option value="">All</option>', '<select id="f-nat"><option value="">Todas</option>'),
    ('<label>Search player / club</label>', '<label>Buscar jugador / club</label>'),
    ('placeholder="e.g. Palacios, Boca Juniors…"', 'placeholder="ej. Palacios, Boca Juniors…"'),
    ('>Clear filters</button>', '>Limpiar filtros</button>'),

    # --- chart cards ---
    ('<h3>Arrivals vs. departures by season</h3>', '<h3>Llegadas vs. salidas por temporada</h3>'),
    ('</span>Arrivals</span>', '</span>Llegadas</span>'),
    ('</span>Departures</span>', '</span>Salidas</span>'),
    ('<h3>Biggest spenders (purchases)</h3>', '<h3>Mayores compradores (fichajes)</h3>'),
    ('<h3>Transfer type</h3>', '<h3>Tipo de traspaso</h3>'),
    ('<h3>Biggest receivers (sales)</h3>', '<h3>Mayores vendedores (ventas)</h3>'),

    # --- table ---
    ('data-view="all">All</button>', 'data-view="all">Todas</button>'),
    ('data-view="in">Arrivals</button>', 'data-view="in">Llegadas</button>'),
    ('data-view="out">Departures</button>', 'data-view="out">Salidas</button>'),
    ('<th data-key="d">Date</th>', '<th data-key="d">Fecha</th>'),
    ('<th data-key="p">Player</th>', '<th data-key="p">Jugador</th>'),
    ('<th data-key="pos">Position</th>', '<th data-key="pos">Posición</th>'),
    ('<th data-key="nat">Nationality</th>', '<th data-key="nat">Nacionalidad</th>'),
    ('<th data-key="age">Age</th>', '<th data-key="age">Edad</th>'),
    ('<th data-key="from">From</th>', '<th data-key="from">Origen</th>'),
    ('<th data-key="to">To</th>', '<th data-key="to">Destino</th>'),
    ('<th data-key="ft">Type</th>', '<th data-key="ft">Tipo</th>'),
    ('<th data-key="fv">Fee</th>', '<th data-key="fv">Monto</th>'),
    ('<th data-key="mv">Market value</th>', '<th data-key="mv">Valor de mercado</th>'),

    # --- footer ---
    ('<h4>Methodology &amp; limitations</h4>', '<h4>Metodología y limitaciones</h4>'),
    ("<li>Each transfer is a single record; when both clubs involved are inside the universe above, the same deal was cross-matched from both clubs' pages to avoid double counting.</li>",
     "<li>Cada traspaso es un único registro; cuando ambos clubes involucrados están dentro del universo anterior, la misma operación fue cruzada desde las páginas de ambos clubes para evitar el doble conteo.</li>"),
    ('<li>"Market value" is Transfermarkt\'s own market-value estimate at the time of the transfer, where available — it is not the fee actually paid (that\'s the "Fee" column).</li>',
     '<li>El "Valor de mercado" es la propia estimación de Transfermarkt al momento del traspaso, cuando está disponible — no es el monto realmente pagado (eso es la columna "Monto").</li>'),
    ('<li>"What happened to this player next" (visible when a row is expanded) shows the player\'s subsequent moves — including a later sale by the club that signed him, which matters for any sell-on percentage tied to the original deal.</li>',
     '<li>"Qué pasó después con este jugador" (visible al expandir una fila) muestra los movimientos posteriores del jugador — incluyendo una venta posterior por parte del club que lo fichó, lo cual importa para cualquier porcentaje de reventa atado al traspaso original.</li>'),
    ('<li><b>Not included:</b> per-season match/goal/assist statistics — Transfermarkt moved those pages to JS-only components with no stable API, which made reliable scraping at the scale of ~1,340 players impractical.</li>',
     '<li><b>No incluido:</b> estadísticas de partidos/goles/asistencias por temporada — Transfermarkt migró esas páginas a componentes solo-JS sin una API estable, lo que hizo impráctico un scraping confiable a la escala de ~1.340 jugadores.</li>'),
    ('Fee and market-value figures are sourced from Transfermarkt in EUR and converted to USD at a flat rate of €1 = $1.08 for display.',
     'Las cifras de monto y valor de mercado provienen de Transfermarkt en EUR y se convierten a USD a una tasa fija de €1 = $1,08 para su presentación.'),

    # --- JS: formatting ---
    ("const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];",
     "const MONTHS = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];"),
    ("toFixed(usd%1e6===0?0:2) + 'm';", "toFixed(usd%1e6===0?0:2) + 'M';"),
    ('return `${MONTHS[Number(m)-1]} ${Number(d)}, ${y}`;', 'return `${Number(d)} ${MONTHS[Number(m)-1]} ${y}`;'),
    ("const CLAUSE_TYPE_LABEL = {'sell-on':'Sell-on clause','buy-back':'Buy-back clause','option-to-buy':'Purchase option'};",
     "const CLAUSE_TYPE_LABEL = {'sell-on':'Cláusula de reventa','buy-back':'Cláusula de recompra','option-to-buy':'Opción de compra'};\n"
     "const FOOT_LABEL = {'right':'Diestro','left':'Zurdo','both':'Ambidiestro'};\n"
     "function esDur(t){ return t && t.replace(/(\\d+)\\s*Years?/gi, (m,n) => n + (Number(n)===1?' año':' años'))"
     ".replace(/(\\d+)\\s*Months?/gi, (m,n) => n + (Number(n)===1?' mes':' meses'))"
     ".replace(/(\\d+)\\s*Days?/gi, (m,n) => n + (Number(n)===1?' día':' días')); }"),
    ("<div class=\"dval\">${r.agep||'—'}</div>", "<div class=\"dval\">${esDur(r.agep)||'—'}</div>"),
    ("let contractVal = r.cd || '—';", "let contractVal = esDur(r.cd) || '—';"),
    ("'en-US'", "'es-CL'"),

    # --- JS: league / scope ---
    ("""clubSel.innerHTML = '<option value="">All</option>';""", """clubSel.innerHTML = '<option value="">Todos</option>';"""),
    ("if (state.league) return MULTI ? `the ${LG[state.league].adj} ${LG[state.league].label}` : `the ${LG[state.league].label}`;",
     "if (state.league) return MULTI ? `la ${LG[state.league].label} ${LG[state.league].adj}` : `la ${LG[state.league].label}`;"),
    ("return MULTI ? `the ${LEAGUES.length} tracked leagues` : `the ${LEAGUES[0].label}`;",
     "return MULTI ? `las ${LEAGUES.length} ligas seguidas` : `la ${LEAGUES[0].label}`;"),
    ("return MULTI ? 'the tracked leagues' : LEAGUES[0].name;", "return MULTI ? 'las ligas seguidas' : LEAGUES[0].name;"),
    ("`Arrivals to ${scopeLabel()}`", "`Llegadas a ${scopeLabel()}`"),
    ("`Departures from ${scopeLabel()}`", "`Salidas de ${scopeLabel()}`"),
    ("? 'Moves between tracked clubs' : `Domestic moves (${scopeCountry()} ↔ ${scopeCountry()})`",
     "? 'Movimientos entre clubes seguidos' : `Movimientos domésticos (${scopeCountry()} ↔ ${scopeCountry()})`"),
    ("`Where departures from ${scopeCountry()} go (by league)`", "`A dónde van las salidas de ${scopeCountry()} (por liga)`"),

    # --- JS: KPIs ---
    ("{label:'Transfers (current filter)'", "{label:'Traspasos (filtro actual)'"),
    ("{label:'Arrivals'", "{label:'Llegadas'"),
    ("{label:'Departures'", "{label:'Salidas'"),
    ("{label:'Spent on purchases'", "{label:'Gastado en fichajes'"),
    ("{label:'Earned from sales'", "{label:'Ingresado por ventas'"),
    ("{label:'Average fee'", "{label:'Monto promedio'"),
    ("`across ${withFee.length.toLocaleString('es-CL')} transfers with a known fee`", "`sobre ${withFee.length.toLocaleString('es-CL')} traspasos con monto conocido`"),
    ("{label:'Biggest transfer'", "{label:'Mayor traspaso'"),
    ("{label:'With a confirmed sell-on %', value: withClause.toLocaleString('es-CL'), sub: 'via press research, not Transfermarkt'}",
     "{label:'Con % de reventa confirmado', value: withClause.toLocaleString('es-CL'), sub: 'vía investigación de prensa, no Transfermarkt'}"),

    # --- JS: charts ---
    ("${key==='in'?'Arrivals':'Departures'}", "${key==='in'?'Llegadas':'Salidas'}"),
    ("'No fee data for this filter'", "'Sin datos de monto para este filtro'"),
    ("Spent: ${fmtUSD(val)}", "Gastado: ${fmtUSD(val)}"),
    ("Received: ${fmtUSD(val)}", "Recibido: ${fmtUSD(val)}"),
    ("'No club / unknown'", "'Sin club / desconocido'"),
    ("entries.push(['Other', rest])", "entries.push(['Otros', rest])"),
    ("'No departures for this filter'", "'Sin salidas para este filtro'"),
    ("${val} departure${val===1?'':'s'}", "${val} salida${val===1?'':'s'}"),
    ("${val} transfers`", "${val} traspasos`"),

    # --- JS: table ---
    ("`${rows.length.toLocaleString('es-CL')} transfers`", "`${rows.length.toLocaleString('es-CL')} traspasos`"),
    ("`Page ${state.page} of ${totalPages}`", "`Página ${state.page} de ${totalPages}`"),
    ("? 'Arrival' : (fsOf(r) && !tsOf(r) ? 'Departure' : (MULTI && !state.league ? 'Move between tracked clubs' : 'Domestic move'))",
     "? 'Llegada' : (fsOf(r) && !tsOf(r) ? 'Salida' : (MULTI && !state.league ? 'Movimiento entre clubes seguidos' : 'Movimiento doméstico'))"),
    ('title="Documented sell-on/buy-back clause — see detail"', 'title="Cláusula de reventa/recompra documentada — ver detalle"'),
    ('title="Researched in the press — no clause publicly reported"', 'title="Investigado en prensa — no se reportó ninguna cláusula"'),

    # --- JS: detail row ---
    ("· MV ${c.mv}", "· VM ${c.mv}"),
    ("No subsequent transfers recorded to date.", "No hay traspasos posteriores registrados hasta la fecha."),
    ("Sell-on / buy-back clause (source: press)", "Cláusula de reventa / recompra (fuente: prensa)"),
    ("(r.sc.type||'clause')", "(r.sc.type||'cláusula')"),
    (" — held by ${r.sc.ben}", " — en poder de ${r.sc.ben}"),
    ('onclick="event.stopPropagation()">source</a>', 'onclick="event.stopPropagation()">fuente</a>'),
    ("Researched in the Chilean/regional press — no sell-on, buy-back, or purchase-option clause was found reported for this deal.",
     "Investigado en la prensa chilena/regional — no se encontró ninguna cláusula de reventa, recompra u opción de compra reportada para este traspaso."),
    ("`Born ${fmtDate(r.dob)}`", "`Nacido el ${fmtDate(r.dob)}`"),
    ("`${r.foot.charAt(0).toUpperCase()+r.foot.slice(1)}-footed`", "FOOT_LABEL[r.foot] || r.foot"),
    ("' (dual national)'", "' (doble nacionalidad)'"),
    ("— ends ${fmtDate(r.ced)}, ${r.cmr} mo. left at transfer", "— termina el ${fmtDate(r.ced)}, quedaban ${r.cmr} meses al momento del traspaso"),
    ('<div class="dlabel">Player bio</div>', '<div class="dlabel">Datos del jugador</div>'),
    ('<div class="dlabel">Nationality</div>', '<div class="dlabel">Nacionalidad</div>'),
    ('<div class="dlabel">Agent</div>', '<div class="dlabel">Agente</div>'),
    ('<div class="dlabel">Original fee text</div>', '<div class="dlabel">Texto original del monto</div>'),
    ('<div class="dlabel">Precise age at transfer</div>', '<div class="dlabel">Edad exacta al traspaso</div>'),
    ('<div class="dlabel">Remaining contract</div>', '<div class="dlabel">Contrato restante</div>'),
    ('<div class="dlabel">Coach (outgoing → incoming)</div>', '<div class="dlabel">Entrenador (saliente → entrante)</div>'),
    ('<div class="dlabel">What happened to this player next</div>', '<div class="dlabel">Qué pasó después con este jugador</div>'),
]


def translate_template(html):
    for en, es in PAIRS:
        if en not in html:
            raise RuntimeError(f"dashboard_template.html changed; no longer contains: {en!r}")
        html = html.replace(en, es)
    return html


POSITION_ES = {
    "Goalkeeper": "Portero",
    "Centre-Back": "Defensa Central",
    "Left-Back": "Lateral Izquierdo",
    "Right-Back": "Lateral Derecho",
    "Defender": "Defensa",
    "Defensive Midfield": "Mediocampista Defensivo",
    "Central Midfield": "Mediocampista Central",
    "Attacking Midfield": "Mediocampista Ofensivo",
    "Midfielder": "Mediocampista",
    "Left Midfield": "Volante Izquierdo",
    "Right Midfield": "Volante Derecho",
    "Left Winger": "Extremo Izquierdo",
    "Right Winger": "Extremo Derecho",
    "Second Striker": "Segundo Delantero",
    "Striker": "Delantero",
    "Centre-Forward": "Delantero Centro",
    "Attack": "Delantero",
}

FEE_TYPE_META_ES = {
    "transfer_fee":   {"label": "Traspaso con monto",     "slot": 1},
    "loan_fee":       {"label": "Cesión con monto",       "slot": 2},
    "loan_free":      {"label": "Cesión sin costo",       "slot": 3},
    "end_of_loan":    {"label": "Fin de cesión",          "slot": 4},
    "free_transfer":  {"label": "Traspaso libre",         "slot": 5},
    "unknown":        {"label": "Sin club / desconocido", "slot": 7},
    "retired":        {"label": "Fin de carrera",         "slot": 8},
    "own_youth":      {"label": "Cantera propia",         "slot": 8},
}

# Display name (country, as shown in selectors) and feminine adjective (after "la Primera División ...").
LEAGUE_NAMES_ES = {
    "CL": {"name": "Chile", "adj": "chilena", "adj_m": "chileno"},
    "UY": {"name": "Uruguay", "adj": "uruguaya", "adj_m": "uruguayo"},
    "PY": {"name": "Paraguay", "adj": "paraguaya", "adj_m": "paraguayo"},
    "PE": {"name": "Perú", "adj": "peruana", "adj_m": "peruano"},
}

CHILE_UNIVERSE_EXTRA_ES = " (incluye clubes descendidos después, ej. Melipilla, Curicó Unido, Santiago Wanderers, Magallanes)"

SELLON_LI_ES = ('<li><b>Cláusulas de reventa / recompra / opción de compra</b>{scope} (expande una fila para verlas; '
                'se marcan con <span class="clause-badge" style="margin-left:0">%</span> junto al monto cuando están '
                'confirmadas, o <span class="clause-badge unknown" style="margin-left:0">?</span> cuando se investigó '
                'pero no se encontró nada): Transfermarkt no publica este dato en absoluto, así que se recopiló mediante '
                'investigación de prensa dirigida (Chile, Argentina, Brasil, Europa) para los 117 traspasos que tuvieron '
                'un monto realmente pagado — los únicos donde este tipo de cláusula suele reportarse. Solo se registraron '
                'porcentajes/términos explícitamente declarados por una fuente, nunca estimados; se confirmó una cláusula '
                'en 57 de los 117 casos (49%). Cada cláusula confirmada lleva un enlace a la fuente y una cita verificable. '
                'Donde dos fuentes no coincidían en la cifra exacta, queda señalado en las notas del propio registro.</li>')

CMF_LI_ES = ("<li><b>CMF Chile:</b> la mayoría de los clubes chilenos están constituidos como S.A.D.P. (sociedades "
             "anónimas deportivas profesionales) y reportan a la Comisión para el Mercado Financiero de Chile; Colo-Colo "
             "y Universidad de Chile son administrados por sociedades anónimas abiertas (Blanco y Negro S.A. y Azul Azul "
             "S.A.) reguladas como emisores de valores. Estos informes contienen estados financieros anuales agregados, "
             "no datos por traspaso — útiles como verificación financiera a nivel de club, no como base de datos de "
             "traspasos.</li>")

SELLON_FILTER_ES = ('<div class="field">\n      <label>Cláusulas</label>\n      '
                    '<label class="checkbox-field"><input type="checkbox" id="f-clause"> '
                    'Solo con cláusula de reventa / recompra confirmada{scope}</label>\n    </div>')


def build_copy_es(configs, scope_counts):
    multi = len(configs) > 1
    any_sellon = any(c["has_sellon"] for c in configs)
    any_cmf = any(c["has_cmf"] for c in configs)
    sellon_scope = " (solo Chile)" if multi and any_sellon else ""
    names = LEAGUE_NAMES_ES

    if not multi:
        c = configs[0]
        n, label = scope_counts[c["code"]], c["league_label"]
        nm = names[c["code"]]
        title = f"Mercado de Traspasos {nm['adj_m'].capitalize()} 2020–2026"
        h1 = f"Mercado de Traspasos {label}"
        subtitle = (f"Todo traspaso doméstico e internacional que involucra a un club {nm['adj_m']} de primera división, "
                    "2020–2026 (hasta ago. 2026)")
        scope = f"{n} clubes que jugaron en la {label} entre 2020 y 2026"
        if c["country"] == "Chile":
            universe = ("<li>Universo: los 25 clubes que jugaron en la Primera División chilena en al menos una temporada "
                        f"entre 2020 y 2026{CHILE_UNIVERSE_EXTRA_ES}.</li>")
        else:
            universe = (f"<li>Universo: los {n} clubes que jugaron en la {label} {nm['adj']} en al menos una temporada "
                        "entre 2020 y 2026 (incluye clubes ascendidos o descendidos durante el período).</li>")
    else:
        display = [names[c["code"]]["name"] for c in configs]
        listed = ", ".join(display[:-1]) + f" y {display[-1]}"
        title = "Mercado de Traspasos Sudamericano 2020–2026"
        h1 = "Mercado de Traspasos Sudamericano"
        subtitle = (f"Todo traspaso doméstico e internacional que involucra a un club de primera división de {listed}, "
                    "2020–2026 (hasta ago. 2026)")
        scope = f"{sum(scope_counts.values())} clubes que jugaron en primera división de {listed} entre 2020 y 2026"
        items = []
        for c in configs:
            nm = names[c["code"]]
            extra = CHILE_UNIVERSE_EXTRA_ES if c["country"] == "Chile" else ""
            items.append(f"{nm['name']}: los {scope_counts[c['code']]} clubes que jugaron en la "
                         f"{c['league_label']} {nm['adj']}{extra}")
        universe = ("<li>Universo: todos los clubes que jugaron en primera división de cada liga en al menos una temporada "
                    "entre 2020 y 2026 (se incluyen clubes ascendidos o descendidos durante el período) — "
                    + "; ".join(items) + ".</li>"
                    "<li>Un traspaso entre clubes de dos ligas seguidas (ej. Uruguay → Chile) es un solo registro, contado "
                    "en la vista de ambas ligas. Usa el filtro Liga para ver el mercado de una sola liga; con \"Todas las "
                    "ligas\", ese movimiento cuenta como movimiento entre clubes seguidos, no como llegada ni salida.</li>")

    return {
        "__PAGE_TITLE__": title,
        "__BRAND_ALT__": "Audax Italiano",
        "__LEAGUE_H1__": h1,
        "__SUBTITLE__": subtitle,
        "__TOPMETA_SCOPE__": scope,
        "__TOPMETA_SOURCE_LINE__": ("Fuente principal: Transfermarkt · referencia corporativa: CMF Chile"
                                     if any_cmf else "Fuente principal: Transfermarkt"),
        "__UNIVERSE_LI__": universe,
        "__SELLON_LI__": SELLON_LI_ES.format(scope=sellon_scope) if any_sellon else "",
        "__CMF_LI__": CMF_LI_ES if any_cmf else "",
        "__SELLON_FEE_NOTE__": (" Los montos dentro de citas de cláusulas de reventa/recompra se mantienen exactamente "
                                 "como fueron reportados originalmente (mayormente ya en USD en la prensa "
                                 "chilena/argentina).") if any_sellon else "",
        "__SELLON_FILTER_FIELD__": SELLON_FILTER_ES.format(scope=sellon_scope) if any_sellon else "",
    }
