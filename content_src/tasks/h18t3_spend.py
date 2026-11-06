from kit import table, tables, rng, day

ID = "h18t3"
NAME = "Supplier Spend Trends"
LANG = "sql"
MINUTES = 25
TAGS = ["mois manquants", "generate_series", "LAG 1 et LAG 12", "moyenne mobile", "noms à normaliser"]
DESC = """
<p>The table <b>purchase_orders</b> has the columns <code>po_id</code>, <code>ordered_on</code> (date), <code>supplier</code>, <code>qty</code> and <code>unit_cost</code>. Supplier names were typed by hand: compare them after trimming spaces and converting to upper case (<code>' acme '</code> is <code>ACME</code>). Orders with <code>qty</code> &lt;= 0 are cancelled and ignored.</p>
<p>The <b>spend</b> of a supplier in a month is the total of <code>qty * unit_cost</code>. Build a report with one row per supplier and per month, for <b>every month</b> from the supplier's first to its last order month (both included, spend 0 for months without orders). For each row compute:</p>
<ul><li><code>spend</code>, rounded to 2 decimals;</li>
<li><code>mom_pct</code>: <code>100 * (spend - previous month spend) / previous month spend</code>, rounded to 1 decimal, <code>NULL</code> for the first month or when the previous spend is 0;</li>
<li><code>ma3</code>: the average spend of this month and the 2 previous months, rounded to 2 decimals, <code>NULL</code> when the supplier does not have 2 previous months in the report yet;</li>
<li><code>yoy_pct</code>: the same as <code>mom_pct</code> but against the same month one year before, <code>NULL</code> when that month is not in the report or its spend is 0.</li></ul>
<p>Your task is to return the columns <code>supplier</code> (clean name), <code>month</code> (first day of the month, as a date), <code>spend</code>, <code>mom_pct</code>, <code>ma3</code> and <code>yoy_pct</code>, sorted by <code>supplier</code>, then <code>month</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH o AS (
  SELECT UPPER(TRIM(supplier)) AS supplier, date_trunc('month', ordered_on)::date AS month, qty * unit_cost AS amt
  FROM purchase_orders WHERE qty > 0
), b AS (
  SELECT supplier, MIN(month) AS a, MAX(month) AS z FROM o GROUP BY supplier
), m AS (
  SELECT supplier, generate_series(a, z, INTERVAL '1 month')::date AS month FROM b
), s AS (
  SELECT m.supplier, m.month, COALESCE(SUM(o.amt), 0) AS spend
  FROM m LEFT JOIN o ON o.supplier = m.supplier AND o.month = m.month
  GROUP BY m.supplier, m.month
)
SELECT supplier, month, ROUND(spend, 2) AS spend,
  ROUND(100 * (spend - LAG(spend) OVER w) / NULLIF(LAG(spend) OVER w, 0), 1) AS mom_pct,
  CASE WHEN COUNT(*) OVER (w ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) = 3
       THEN ROUND(AVG(spend) OVER (w ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) END AS ma3,
  ROUND(100 * (spend - LAG(spend, 12) OVER w) / NULLIF(LAG(spend, 12) OVER w, 0), 1) AS yoy_pct
FROM s
WINDOW w AS (PARTITION BY supplier ORDER BY month)
ORDER BY supplier, month;
"""
MUTANTS = [
    SOLUTION.replace("FROM m LEFT JOIN o", "FROM m JOIN o"),
    SOLUTION.replace("FROM purchase_orders WHERE qty > 0", "FROM purchase_orders"),
    SOLUTION.replace("CASE WHEN COUNT(*) OVER (w ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) = 3\n       THEN ", "CASE WHEN true THEN "),
    SOLUTION.replace("UPPER(TRIM(supplier))", "UPPER(supplier)"),
]
T = "po_id INT, ordered_on DATE, supplier TEXT, qty INT, unit_cost NUMERIC(10,2)"


def tests():
    t = [tables(purchase_orders=table(T, [[1, "2025-01-15", "acme", 10, 5], [2, "2025-01-20", " ACME ", 2, 25], [3, "2025-03-02", "Acme", 4, 25],
                                          [4, "2025-04-30", "ACME", 0, 99], [5, "2025-04-01", "acme", 1, 50], [6, "2026-01-10", "ACME", 5, 30],
                                          [7, "2025-02-11", "Delta", 3, 3.33], [8, "2025-03-11", "delta", -3, 3.33]])),
         tables(purchase_orders=table(T, [[1, "2026-05-05", "zeta", 1, 10], [2, "2026-06-05", "ZETA", 1, 0], [3, "2026-07-05", "zeta", 2, 10]]))]
    r = rng(4183)
    for _ in range(8):
        rows = []
        for i in range(r.randint(5, 40)):
            s = r.choice(["acme", " ACME", "Delta ", "delta", "Omega"])
            rows.append([i + 1, day(r.randint(0, 540), "2025-01-01"), s, r.choice([-1, 0, 1, 2, 5, 10]), r.choice([1.5, 10, 12.25, 40])])
        t.append(tables(purchase_orders=table(T, rows)))
    return t
