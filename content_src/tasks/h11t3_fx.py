from kit import table, tables, rng, day

ID = "h11t3"
NAME = "Monthly Shipments in EUR"
LANG = "sql"
MINUTES = 20
TAGS = ["jointure « as-of »", "LATERAL", "nettoyage de codes", "DISTINCT ON", "COUNT(col) vs COUNT(*)"]
DESC = """
<p>The table <b>shipments</b> has the columns <code>shipment_id</code>, <code>shipped_on</code> (date), <code>currency</code> and <code>amount</code>. The table <b>fx_rates</b> has the columns <code>currency</code>, <code>rate_date</code> (date) and <code>rate_to_eur</code>. Rates are not published every day.</p>
<p>Currency codes in <b>shipments</b> were typed by hand: they can be in lower case or padded with spaces (<code>' usd'</code> is <code>USD</code>). Codes in <b>fx_rates</b> are clean.</p>
<p>A shipment is converted to EUR with the <b>latest rate of its currency published on or before</b> its <code>shipped_on</code> date. <code>EUR</code> shipments use the rate 1 (there is no EUR row in <b>fx_rates</b>). A shipment with no rate available is <b>unconverted</b>.</p>
<p>Your task is to return one row per month (the first day of the month of <code>shipped_on</code>, as a date) with the columns <code>month</code>, <code>shipments</code> (number of converted shipments), <code>total_eur</code> and <code>avg_eur</code> (sum and average of the converted amounts, rounded to 2 decimals, <code>NULL</code> when nothing was converted), <code>unconverted</code> and <code>top_currency</code> (the clean currency code with the highest converted total that month; on a tie, the first code in alphabetical order; <code>NULL</code> when nothing was converted), sorted by <code>month</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH s AS (
  SELECT sh.shipment_id, sh.shipped_on, UPPER(TRIM(sh.currency)) AS cur, sh.amount
  FROM shipments sh
), c AS (
  SELECT s.*, date_trunc('month', s.shipped_on)::date AS month,
         s.amount * CASE WHEN s.cur = 'EUR' THEN 1 ELSE r.rate_to_eur END AS eur
  FROM s
  LEFT JOIN LATERAL (
    SELECT f.rate_to_eur FROM fx_rates f
    WHERE f.currency = s.cur AND f.rate_date <= s.shipped_on
    ORDER BY f.rate_date DESC LIMIT 1
  ) r ON true
), top AS (
  SELECT DISTINCT ON (month) month, cur
  FROM (SELECT month, cur, SUM(eur) AS t FROM c WHERE eur IS NOT NULL GROUP BY month, cur) x
  ORDER BY month, t DESC, cur
)
SELECT c.month, COUNT(c.eur) AS shipments, ROUND(SUM(c.eur), 2) AS total_eur, ROUND(AVG(c.eur), 2) AS avg_eur,
       COUNT(*) - COUNT(c.eur) AS unconverted, top.cur AS top_currency
FROM c LEFT JOIN top ON top.month = c.month
GROUP BY c.month, top.cur
ORDER BY c.month;
"""
MUTANTS = [
    SOLUTION.replace("f.rate_date <= s.shipped_on", "f.rate_date < s.shipped_on"),
    SOLUTION.replace("UPPER(TRIM(sh.currency))", "UPPER(sh.currency)"),
    SOLUTION.replace("ORDER BY f.rate_date DESC LIMIT 1", "ORDER BY f.rate_date LIMIT 1"),
    SOLUTION.replace("ORDER BY month, t DESC, cur", "ORDER BY month, t DESC, cur DESC"),
    SOLUTION.replace("CASE WHEN s.cur = 'EUR' THEN 1 ELSE r.rate_to_eur END", "r.rate_to_eur"),
]
S = "shipment_id INT, shipped_on DATE, currency TEXT, amount NUMERIC(12,2)"
F = "currency TEXT, rate_date DATE, rate_to_eur NUMERIC(12,6)"


def tests():
    t = [tables(shipments=table(S, [[1, "2026-01-05", "usd", 100], [2, "2026-01-10", " USD ", 50], [3, "2026-01-11", "EUR", 120],
                                    [4, "2026-01-02", "GBP", 10], [5, "2026-02-03", "gbp", 100], [6, "2026-02-04", "MAD", 1000]]),
                fx_rates=table(F, [["USD", "2026-01-01", 0.9], ["USD", "2026-01-10", 0.8], ["GBP", "2026-01-03", 1.2]])),
         tables(shipments=table(S, [[1, "2026-03-01", "xof", 6559.57], [2, "2026-04-01", "EUR", 10], [3, "2026-04-02", "eur", 10]]),
                fx_rates=table(F, [["XOF", "2026-03-02", 0.001524]])),
         tables(shipments=table(S, [[1, "2026-05-03", "USD", 100], [2, "2026-05-04", "gbp", 50], [3, "2026-05-05", "MAD", 10]]),
                fx_rates=table(F, [["USD", "2026-05-01", 0.5], ["GBP", "2026-05-04", 1.0]]))]
    r = rng(4113)
    curs = ["USD", "GBP", "MAD", "EUR", "XOF"]
    for _ in range(8):
        fx = []
        for c in curs[:-1]:
            if c == "EUR":
                continue
            for d in sorted(r.sample(range(0, 120), r.randint(1, 6))):
                fx.append([c, day(d), round(r.uniform(0.05, 1.3), 6)])
        sh = []
        for i in range(r.randint(5, 25)):
            c = r.choice(curs)
            c = r.choice([c, c.lower(), " " + c, c + " "])
            sh.append([i + 1, day(r.randint(0, 120)), c, r.choice([10, 25.5, 99.99, 250, 1000])])
        t.append(tables(shipments=table(S, sh), fx_rates=table(F, fx)))
    return t
