"""
Spanish translation layer for report_template.html and the strings generated
by 07_build_report.py. Same approach as i18n_es.py: the English template stays
the single source of truth and translation fails loudly if a string is gone.
"""

PAIRS = [
    ('<html lang="en">', '<html lang="es">'),
    ('<p class="eyebrow">Prepared for Audax Italiano</p>', '<p class="eyebrow">Preparado para Audax Italiano</p>'),
    ('<h1>Chilean Transfer Market Intelligence</h1>', '<h1>Inteligencia del Mercado de Traspasos Chileno</h1>'),
    ('A deep dive into how money, players, and clauses actually move through Chilean football — 2020–2026',
     'Un análisis a fondo de cómo se mueven realmente el dinero, los jugadores y las cláusulas en el fútbol chileno — 2020–2026'),
    ('<h2>TL;DR</h2>', '<h2>En resumen</h2>'),

    # --- TL;DR ---
    ("<li><b>Free transfers can hide real money.</b> Matías Palavecino left Coquimbo Unido for Universidad Católica for €0 despite a €1m market value — his contract had simply expired, so Coquimbo got nothing. That's the single most avoidable mistake in this data: letting a valuable player's contract run out costs the selling club everything.</li>",
     "<li><b>Los traspasos libres pueden esconder dinero real.</b> Matías Palavecino dejó Coquimbo Unido por Universidad Católica por €0 pese a un valor de mercado de €1M — su contrato simplemente había vencido, así que Coquimbo no recibió nada. Es el error más evitable de estos datos: dejar que venza el contrato de un jugador valioso le cuesta todo al club vendedor.</li>"),
    ("<li><b>Sell-on clauses are common in Chile and often pay off later, not immediately.</b> We individually checked __CLAUSE_TOTAL_CHECKED__ transfers against the press and confirmed __CLAUSE_TOTAL_FOUND__ real clauses. Of those, __CLAUSE_MOVED__ (__CLAUSE_MOVED_PCT__%) already involve the player moving to a THIRD club since — meaning the clause may already be owed, or was already paid, without it necessarily making headlines.</li>",
     "<li><b>Las cláusulas de reventa son comunes en Chile y a menudo rinden después, no de inmediato.</b> Revisamos individualmente __CLAUSE_TOTAL_CHECKED__ traspasos contra la prensa y confirmamos __CLAUSE_TOTAL_FOUND__ cláusulas reales. De ellas, __CLAUSE_MOVED__ (__CLAUSE_MOVED_PCT__%) ya involucran al jugador pasando a un TERCER club desde entonces — es decir, la cláusula puede ya deberse, o ya haberse pagado, sin que necesariamente sea noticia.</li>"),
    ('<li><b>Only Universidad Católica runs a clearly profitable transfer model among the "big 3."</b> Colo-Colo is modestly net-positive; Universidad de Chile is net-negative over the period — despite all three being considered the league\'s biggest sellers.</li>',
     '<li><b>Solo Universidad Católica maneja un modelo de traspasos claramente rentable entre los "tres grandes".</b> Colo-Colo es levemente positivo en neto; Universidad de Chile es negativo en el período — pese a que los tres se consideran los mayores vendedores de la liga.</li>'),
    ("<li><b>Argentina is Chile's most valuable market — not because it pays the most, but because it buys the most and acts as a shop window</b> for a second, bigger sale later. Brazil pays the highest average fee per deal but buys rarely and selectively.</li>",
     "<li><b>Argentina es el mercado más valioso de Chile — no porque pague más, sino porque compra más y actúa como vitrina</b> para una segunda venta mayor más adelante. Brasil paga el monto promedio más alto por operación, pero compra poco y de forma selectiva.</li>"),
    ("<li><b>Most loans quietly evaporate — unless a fee was negotiated upfront.</b> 78% of tracked loan-outs end with the player moving on again without the parent club capturing further value. But among loans that DID carry a disclosed fee, __LOANFEE_FOUND__ of __LOANFEE_CHECKED__ turned out to have a real purchase-option, sell-on, or buy-back clause attached — the negotiating discipline at signing is what makes the difference.</li>",
     "<li><b>La mayoría de las cesiones se esfuman en silencio — salvo que se haya negociado un monto de entrada.</b> El 78% de las cesiones rastreadas terminan con el jugador moviéndose otra vez sin que el club de origen capture más valor. Pero entre las cesiones que SÍ tenían un monto revelado, __LOANFEE_FOUND__ de __LOANFEE_CHECKED__ resultaron tener una cláusula real de opción de compra, reventa o recompra — la disciplina de negociación al firmar es lo que marca la diferencia.</li>"),
    ('<li><b>A real structured source for transfer percentages does exist — for two clubs.</b> Colo-Colo\'s and Universidad de Chile\'s audited CMF financial filings contain a per-player table with exact "% federative / % economic rights" splits. Everyone else\'s clauses still have to be found in the press.</li>',
     '<li><b>Sí existe una fuente estructurada real para los porcentajes de traspaso — para dos clubes.</b> Los estados financieros auditados de Colo-Colo y Universidad de Chile ante la CMF contienen una tabla por jugador con las divisiones exactas de "% derechos federativos / % derechos económicos". Las cláusulas de todos los demás todavía hay que encontrarlas en la prensa.</li>'),

    # --- 01 ---
    ('<span class="num">01</span>The Big Three', '<span class="num">01</span>Los Tres Grandes'),
    ("Colo-Colo, Universidad Católica and Universidad de Chile are the league's benchmark sellers. Here's what each has actually done with the transfer market, 2020–2026.",
     'Colo-Colo, Universidad Católica y Universidad de Chile son los vendedores de referencia de la liga. Esto es lo que cada uno ha hecho realmente en el mercado de traspasos, 2020–2026.'),
    ("Reading across the three: Universidad Católica spends the least and earns the second-most, making it the only one of the three with a clearly disciplined, profitable transfer model over this window. Colo-Colo trades the most volume in both directions and finishes modestly ahead. Universidad de Chile — despite producing the single biggest sale in the dataset (Darío Osorio, $5.6m) — has spent slightly more than it has earned overall, meaning its transfer account doesn't fund itself the way the other two do.",
     'Mirando a los tres en conjunto: Universidad Católica gasta lo menos y gana lo segundo más, lo que la convierte en la única de las tres con un modelo de traspasos claramente disciplinado y rentable en esta ventana. Colo-Colo mueve el mayor volumen en ambas direcciones y termina levemente adelante. Universidad de Chile — pese a haber producido la mayor venta del conjunto de datos (Darío Osorio, $5,6M) — ha gastado algo más de lo que ha ganado en total, lo que significa que su cuenta de traspasos no se financia sola como las de las otras dos.'),

    # --- 02 ---
    ('<span class="num">02</span>Case study: the Palavecino free transfer', '<span class="num">02</span>Caso de estudio: el traspaso libre de Palavecino'),
    ('Coquimbo Unido → Universidad Católica, January 2026 — the transfer that cost Coquimbo everything.',
     'Coquimbo Unido → Universidad Católica, enero de 2026 — el traspaso que le costó todo a Coquimbo.'),
    ('<h3>Matías Palavecino, 27, Attacking Midfield (Argentina)</h3>', '<h3>Matías Palavecino, 27, Mediocampista Ofensivo (Argentina)</h3>'),
    ('<span class="date">Jan 2023</span> Joins Coquimbo Unido as a free agent from Gimnasia y Esgrima (Jujuy), Argentina\'s 2nd division. Market value: €300k.',
     '<span class="date">Ene 2023</span> Llega a Coquimbo Unido como agente libre desde Gimnasia y Esgrima (Jujuy), segunda división de Argentina. Valor de mercado: €300k.'),
    ('<span class="date">Aug 2023</span> Loaned to Belgrano (Argentina) for a €73k loan fee. Market value climbs to €500k.',
     '<span class="date">Ago 2023</span> Cedido a Belgrano (Argentina) por una tarifa de cesión de €73k. El valor de mercado sube a €500k.'),
    ('<span class="date">Dec 2024</span> Loan ends, returns to Coquimbo. Market value dips to €150k.',
     '<span class="date">Dic 2024</span> Termina la cesión y vuelve a Coquimbo. El valor de mercado baja a €150k.'),
    ('<span class="date">2025 season</span> Becomes one of the standout figures as Coquimbo wins its first-ever Chilean league title. Market value rockets to €1.00m.',
     '<span class="date">Temporada 2025</span> Se convierte en una de las figuras destacadas mientras Coquimbo gana su primer título de liga chilena. El valor de mercado se dispara a €1,00M.'),
    ('<span class="date">Jan 2026</span> Leaves for Universidad Católica — as a pure free transfer. Both Colo-Colo and Universidad Católica competed for his signature; Católica won.',
     '<span class="date">Ene 2026</span> Se va a Universidad Católica — como traspaso libre puro. Tanto Colo-Colo como Universidad Católica competían por su firma; ganó Católica.'),
    ('<p>Coquimbo did not negotiate a sell-on clause, a fee, or any compensation — because there was nothing left to negotiate. His contract had simply expired, a point confirmed directly by Chilean press coverage of his exit. He was Coquimbo\'s second key departure on a free that same week, after striker Cecilio Waterman.</p>',
     '<p>Coquimbo no negoció una cláusula de reventa, un monto ni ninguna compensación — porque no quedaba nada que negociar. Su contrato simplemente había vencido, punto confirmado directamente por la cobertura de la prensa chilena sobre su salida. Fue la segunda salida clave de Coquimbo sin costo esa misma semana, después del delantero Cecilio Waterman.</p>'),
    ('<div class="case-verdict"><b>The lesson for Audax:</b> a player\'s market value can quadruple while under contract, but none of that value converts to cash unless the club either sells before expiry or extends the contract early enough to negotiate from strength. Once a contract is allowed to run down, the buying club owes nothing at all — not even a nominal fee or a resale percentage. For a club like Audax that develops rather than buys established talent, contract-renewal timing on any player whose value is rising is at least as important as scouting the next signing.</p>',
     '<div class="case-verdict"><b>La lección para Audax:</b> el valor de mercado de un jugador puede cuadruplicarse mientras está bajo contrato, pero nada de ese valor se convierte en efectivo a menos que el club venda antes del vencimiento o extienda el contrato con suficiente anticipación para negociar desde una posición de fuerza. Una vez que se deja agotar un contrato, el club comprador no debe absolutamente nada — ni siquiera una tarifa nominal o un porcentaje de reventa. Para un club como Audax, que forma en vez de comprar talento ya establecido, el momento de la renovación de contrato de cualquier jugador cuyo valor sube es al menos tan importante como ojear al próximo fichaje.</p>'),

    # --- 03 ---
    ('<span class="num">03</span>Sell-on clauses: where the money actually stands today', '<span class="num">03</span>Cláusulas de reventa: dónde está realmente el dinero hoy'),
    ("All __CLAUSE_TOTAL_FOUND__ transfers in our database with a press-confirmed sell-on, buy-back, or purchase-option clause — out of __CLAUSE_TOTAL_CHECKED__ individually checked across every paid transfer, every high-value free transfer, and every disclosed-fee loan since 2020 — cross-checked against each player's full Transfermarkt career history to see whether they've moved again since, which is exactly when these clauses get triggered.",
     'Los __CLAUSE_TOTAL_FOUND__ traspasos de nuestra base con una cláusula de reventa, recompra u opción de compra confirmada por la prensa — de __CLAUSE_TOTAL_CHECKED__ revisados individualmente entre todos los traspasos con monto pagado, todos los traspasos libres de alto valor y todas las cesiones con monto revelado desde 2020 — contrastados con la carrera completa de cada jugador en Transfermarkt para ver si se han movido otra vez, que es exactamente cuando estas cláusulas se activan.'),
    ('<thead><tr><th>Player</th><th>Clause</th><th>Held by</th><th>Sold to (original deal)</th><th>Status today</th></tr></thead>',
     '<thead><tr><th>Jugador</th><th>Cláusula</th><th>En poder de</th><th>Vendido a (operación original)</th><th>Estado hoy</th></tr></thead>'),
    ('"Moved on" doesn\'t guarantee the clause was paid — some are shared economic-rights splits with no automatic trigger, and Transfermarkt doesn\'t confirm settlement. But it does mean the triggering event (a further sale) has already happened, so it\'s worth a direct check with the counterpart club if the amount is meaningful.',
     '"Se movió" no garantiza que la cláusula se haya pagado — algunas son divisiones de derechos económicos compartidos sin disparador automático, y Transfermarkt no confirma la liquidación. Pero sí significa que el evento disparador (una venta posterior) ya ocurrió, por lo que vale la pena consultar directamente al club contraparte si el monto es relevante.'),

    # --- 04 ---
    ('<span class="num">04</span>Do "free transfers" ever hide a clause?', '<span class="num">04</span>¿Los "traspasos libres" esconden alguna vez una cláusula?'),
    ('We tested the Palavecino pattern against every other high-value "free transfer" in the database (market value ≥ €300k) to see how often a club actually negotiated something despite taking no fee: __FREE_CHECKED__ transfers checked, __FREE_FOUND__ confirmed hits. The low hit rate is itself the finding — it confirms Palavecino\'s zero-compensation exit is the norm, not the exception, for a lapsed contract.',
     'Probamos el patrón Palavecino contra cada otro "traspaso libre" de alto valor en la base (valor de mercado ≥ €300k) para ver con qué frecuencia un club negoció realmente algo pese a no cobrar un monto: __FREE_CHECKED__ traspasos revisados, __FREE_FOUND__ aciertos confirmados. La baja tasa de aciertos es en sí el hallazgo — confirma que la salida sin compensación de Palavecino es la norma, no la excepción, para un contrato vencido.'),

    # --- 05 ---
    ('<span class="num">05</span>The loan playbook: what happens when it ends', '<span class="num">05</span>El manual de las cesiones: qué pasa cuando terminan'),
    ('439 loan-out deals from Chilean top-flight clubs since 2020, tracked through to their actual resolution using each player\'s subsequent transfer history.',
     '439 cesiones salientes de clubes chilenos de primera división desde 2020, rastreadas hasta su resolución real usando el historial de traspasos posteriores de cada jugador.'),
    ('<span class="l">total loans out</span>', '<span class="l">cesiones salientes en total</span>'),
    ('<span class="l">returned, then moved on again</span>', '<span class="l">volvieron y luego se movieron otra vez</span>'),
    ('<span class="l">returned and stayed (so far)</span>', '<span class="l">volvieron y se quedaron (hasta ahora)</span>'),
    ('<span class="l">bought outright by the loan host</span>', '<span class="l">comprados definitivamente por el club receptor</span>'),
    ("That's the league-wide pattern. But when we individually researched the __LOANFEE_CHECKED__ loans that had a disclosed loan fee (a proxy for \"the parent club considered this player valuable enough to negotiate terms up front\"), the picture flips completely: __LOANFEE_FOUND__ of __LOANFEE_CHECKED__ had a real, sourced purchase-option, sell-on, or buy-back clause attached at signing.",
     'Ese es el patrón a nivel de liga. Pero cuando investigamos individualmente las __LOANFEE_CHECKED__ cesiones con tarifa de cesión revelada (un indicador de que "el club de origen consideró al jugador lo bastante valioso como para negociar condiciones de entrada"), el panorama se invierte por completo: __LOANFEE_FOUND__ de __LOANFEE_CHECKED__ tenían una cláusula real y documentada de opción de compra, reventa o recompra al firmar.'),
    ('<thead><tr><th>Player</th><th>Move</th><th>Clause type</th><th>Terms</th><th>Status</th></tr></thead>',
     '<thead><tr><th>Jugador</th><th>Movimiento</th><th>Tipo de cláusula</th><th>Términos</th><th>Estado</th></tr></thead>'),
    ("Standouts: Jordhy Thompson's loan to FC Orenburg had a mandatory 60% purchase option triggered at 10 appearances — he played 12, Colo-Colo collected $1.2m and kept the rest for a future sale. Franco Calderón's 2026 loan to Independiente stacks an 80% option, a loan-extension fee, <b>and</b> a buy-back right for Universidad de Chile, all netting against each other. Colo-Colo's loan of Brayan Cortés to Peñarol shows the floor rising in real time during negotiation: the first offer from Peñarol landed under half of the final figure, before the two sides settled on an option worth more than $1.35m against Colo-Colo's $1m minimum.",
     'Casos destacados: la cesión de Jordhy Thompson al FC Orenburg tenía una opción de compra obligatoria del 60% activada a los 10 partidos — jugó 12, Colo-Colo cobró $1,2M y conservó el resto para una venta futura. La cesión de Franco Calderón a Independiente en 2026 apila una opción del 80%, una tarifa por extensión de la cesión <b>y</b> un derecho de recompra para Universidad de Chile, todo compensándose entre sí. La cesión de Brayan Cortés de Colo-Colo a Peñarol muestra cómo el piso subió en tiempo real durante la negociación: la primera oferta de Peñarol quedó por debajo de la mitad de la cifra final, antes de que las partes acordaran una opción por más de $1,35M frente al mínimo de $1M de Colo-Colo.'),

    # --- 06 ---
    ('<span class="num">06</span>Which leagues actually value Chilean talent?', '<span class="num">06</span>¿Qué ligas valoran realmente el talento chileno?'),
    ('Pure departures from a Chilean top-flight club to a club outside our 25-club universe — no domestic moves, no subsequent chain transfers, just the original exit.',
     'Salidas puras de un club chileno de primera división hacia un club fuera de nuestro universo de 25 clubes — sin movimientos domésticos, sin traspasos posteriores de la cadena, solo la salida original.'),
    ('<thead><tr><th>Destination country</th><th>Total departures</th><th>With disclosed fee</th><th>Average fee</th></tr></thead>',
     '<thead><tr><th>País de destino</th><th>Salidas totales</th><th>Con monto revelado</th><th>Monto promedio</th></tr></thead>'),

    # --- 07 ---
    ('<span class="num">07</span>Is there a real source for transfer percentages in Chile?', '<span class="num">07</span>¿Existe una fuente real para los porcentajes de traspaso en Chile?'),
    ("We've been finding sell-on clauses one article at a time. We asked whether a more systematic, official source exists.",
     'Hemos ido encontrando cláusulas de reventa un artículo a la vez. Nos preguntamos si existe una fuente oficial y más sistemática.'),

    # --- 08 ---
    ('<span class="num">08</span>What this means for Audax Italiano', '<span class="num">08</span>Qué significa esto para Audax Italiano'),
    ('<p>Audax sits well below the "big 3" in transfer volume and fees, but every dynamic above still applies at Audax\'s scale — usually with less room for error, since Audax can\'t absorb a Palavecino-style zero as easily as Universidad Católica\'s rivals can.</p>',
     '<p>Audax está muy por debajo de los "tres grandes" en volumen de traspasos y montos, pero todas las dinámicas anteriores siguen aplicando a la escala de Audax — normalmente con menos margen de error, ya que Audax no puede absorber un cero al estilo Palavecino tan fácilmente como los rivales de Universidad Católica.</p>'),
    ("<li><b>Track contract expiry dates like a sales pipeline.</b> Any Audax player whose market value is rising should be renewed, sold, or loaned with an option well before the final year of his contract — the Palavecino case shows exactly how much value evaporates otherwise.</li>",
     "<li><b>Siga las fechas de vencimiento de contrato como un embudo de ventas.</b> Todo jugador de Audax cuyo valor de mercado esté subiendo debe renovarse, venderse o cederse con opción mucho antes del último año de su contrato — el caso Palavecino muestra exactamente cuánto valor se evapora de lo contrario.</li>"),
    ("<li><b>Never loan out a promising player without a purchase option or sell-on clause attached.</b> The data shows 78% of loans return no further value to the parent club specifically because no such clause existed at signing — not because the player failed to develop.</li>",
     "<li><b>Nunca ceda a un jugador prometedor sin una opción de compra o una cláusula de reventa.</b> Los datos muestran que el 78% de las cesiones no devuelven más valor al club de origen precisamente porque no existía tal cláusula al firmar — no porque el jugador no se desarrollara.</li>"),
    ("<li><b>Treat Argentina as the default first stop for a sale, not a last resort.</b> It's the highest-volume, most logistically simple market, and functions as a stepping stone toward a bigger second sale — which matters even more for a smaller seller like Audax that's unlikely to land a direct Brazil-sized fee.</li>",
     "<li><b>Trate a Argentina como la primera parada por defecto para una venta, no como último recurso.</b> Es el mercado de mayor volumen y el más simple logísticamente, y funciona como escalón hacia una segunda venta mayor — lo que importa aún más para un vendedor más pequeño como Audax, que difícilmente conseguirá directamente un monto del tamaño de Brasil.</li>"),
    ("<li><b>Chase the resale, not just the headline fee.</b> A modest sale with a well-drafted 20-30% sell-on clause can end up worth more than a larger sale with none — several clubs smaller than Audax (Deportes Antofagasta, Ñublense, Independiente Rivadavia) have collected real money years later this way.</li>",
     "<li><b>Persiga la reventa, no solo el monto principal.</b> Una venta modesta con una cláusula de reventa del 20-30% bien redactada puede terminar valiendo más que una venta mayor sin ella — varios clubes más pequeños que Audax (Deportes Antofagasta, Ñublense, Independiente Rivadavia) han cobrado dinero real años después de esta manera.</li>"),
    ("<li><b>Keep your own record — don't expect outside help.</b> CMF filings only cover Colo-Colo and Universidad de Chile (see section 07); for everyone else, including Audax's own deals, whatever gets negotiated only stays visible if Audax keeps its own record of it.</li>",
     "<li><b>Lleve su propio registro — no espere ayuda externa.</b> Los informes de la CMF solo cubren a Colo-Colo y Universidad de Chile (ver sección 07); para todos los demás, incluidas las operaciones del propio Audax, lo que se negocie solo queda visible si Audax mantiene su propio registro.</li>"),

    # --- footer ---
    ("<p><b>Methodology:</b> quantitative figures are computed from our own Transfermarkt-derived database of 3,370 transfers involving the 25 clubs that played in the Chilean Primera División between 2020 and 2026. Sell-on/buy-back clause data, the free-transfer clause check, league-reception analysis, loan-practice context, and the CMF/source verdict were gathered via targeted press research (Chile, Argentina, Brazil) — every specific claim is sourced; general patterns are labeled as inference where they are not.</p>",
     "<p><b>Metodología:</b> las cifras cuantitativas se calculan a partir de nuestra propia base derivada de Transfermarkt con 3.370 traspasos que involucran a los 25 clubes que jugaron en la Primera División chilena entre 2020 y 2026. Los datos de cláusulas de reventa/recompra, la revisión de cláusulas en traspasos libres, el análisis de recepción por liga, el contexto de prácticas de cesión y el veredicto de la CMF/fuentes se recopilaron mediante investigación de prensa dirigida (Chile, Argentina, Brasil) — cada afirmación específica tiene fuente; los patrones generales se señalan como inferencia cuando no la tienen.</p>"),
    ('<p>Fee and market-value figures are converted from Transfermarkt\'s EUR at a flat €1 = $1.08 for display. This report is a companion to the full <a href="#">Chilean Transfer Market dashboard</a>.</p>',
     '<p>Las cifras de monto y valor de mercado se convierten desde los EUR de Transfermarkt a una tasa fija de €1 = $1,08 para su presentación. Este informe es complemento del <a href="#">dashboard completo del Mercado de Traspasos</a>.</p>'),
]


def translate_template(html):
    for en, es in PAIRS:
        if en not in html:
            raise RuntimeError(f"report_template.html changed; no longer contains: {en[:90]!r}")
        html = html.replace(en, es)
    return html


# Strings generated by 07_build_report.py (keys mirror the English literals).
PY = {
    "pending": "<p><em>Investigación pendiente — {name} aún no está disponible.</em></p>",
    "arrivals": "llegadas",
    "departures": "salidas",
    "avg_age_arr": "edad prom., llegadas",
    "avg_age_dep": "edad prom., salidas",
    "spent": "Gastado",
    "earned": "Ingresado",
    "net": "Neto",
    "big3_note": ("{chilean_pct:.0f}% de las salidas son jugadores chilenos; de ellos, {abroad_pct:.0f}% deja el país por completo "
                  "(el resto se queda en el fútbol chileno, sobre todo en divisiones inferiores). "
                  "Principales destinos internacionales: {top}."),
    "biggest_sale": "Mayor venta:",
    "biggest_buy": "Mayor compra:",
    "buy_from": "desde",
    "moved_on": "se movió → {name}",
    "still_there": "sigue allí",
    "clause": "cláusula",
    "no_clause": "sin cláusula",
    "confirmed": "confirmada",
    "clause_labels": {"option-to-buy": "Opción de compra", "mandatory-purchase": "Compra obligatoria",
                      "sell-on": "Reventa", "buy-back": "Recompra"},
    "unknown_country": "Desconocido",
    "million": "M",
}

COUNTRY_ES = {
    "Brazil": "Brasil", "Mexico": "México", "United States": "Estados Unidos", "Peru": "Perú",
    "Spain": "España", "Italy": "Italia", "Germany": "Alemania", "France": "Francia", "England": "Inglaterra",
    "Saudi Arabia": "Arabia Saudita", "Japan": "Japón", "Netherlands": "Países Bajos", "Belgium": "Bélgica",
    "Switzerland": "Suiza", "Greece": "Grecia", "Turkey": "Turquía", "Russia": "Rusia", "Denmark": "Dinamarca",
    "Sweden": "Suecia", "Norway": "Noruega", "Scotland": "Escocia", "Poland": "Polonia", "Canada": "Canadá",
    "China": "China", "Korea, South": "Corea del Sur", "Qatar": "Catar", "United Arab Emirates": "Emiratos Árabes Unidos",
    "Costa Rica": "Costa Rica", "Panama": "Panamá", "Romania": "Rumania", "Croatia": "Croacia", "Cyprus": "Chipre",
    "Czech Republic": "República Checa", "Austria": "Austria", "Israel": "Israel", "Australia": "Australia",
    "Honduras": "Honduras", "Guatemala": "Guatemala", "El Salvador": "El Salvador",
}
